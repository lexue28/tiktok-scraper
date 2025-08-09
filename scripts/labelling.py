import os
import csv
import pandas as pd
from collections import defaultdict, Counter
import numpy as np
from statsmodels.stats.inter_rater import fleiss_kappa

def extract_labels():
    input_folder = os.path.join("labelling", "manual")

    # Output CSV path
    output_path = os.path.join("labelling", "label_output.csv")

    # Video ID mapping: {video_id: [nicolo_label, francesco_c_label, francesco_p_label]}
    video_labels = defaultdict(lambda: [None, None, None])

    # Helper for majority vote
    def majority_vote(labels):
        counts = Counter([x for x in labels if x is not None])
        if len(counts) == 0:
            return "unclear"
        if len(counts) == 3:
            return "unclear"
        most_common = counts.most_common(1)[0]
        if list(counts.values()).count(most_common[1]) > 1:
            return "unclear"
        return most_common[0]

    # --- 1. Parse nicolo.csv ---
    nicolo_path = os.path.join(input_folder, "nicolo.csv")
    df_nicolo = pd.read_csv(nicolo_path, dtype={"video_id": str})

    for _, row in df_nicolo.iterrows():
        vid = str(row["video_id"]).strip()
        everyone = str(row.get("everyone-harmful", "")).lower()
        children = str(row.get("children-harmful", "")).lower()
        if everyone == "harmful":
            label = 1
        elif children == "harmful":
            label = 2
        else:
            label = 0
        video_labels[vid][0] = label

    # --- 2. Parse francesco_c.csv ---
    francesco_c_path = os.path.join(input_folder, "francesco_c.csv")
    df_fc = pd.read_csv(francesco_c_path, dtype={"video_id": str}, encoding="ISO-8859-1")
    for _, row in df_fc.iterrows():
        vid = str(row["video_id"]).strip()
        label = row.get("label")
        if pd.notna(label):
            video_labels[vid][1] = int(label)

    # --- 3. Parse francesco_p.csv ---
    francesco_p_path = os.path.join(input_folder, "francesco_p.csv")
    df_fp = pd.read_csv(francesco_p_path, dtype={"video_id": str})
    for _, row in df_fp.iterrows():
        vid = str(row["video_id"]).strip()
        everyone = str(row.get("everyone-harmful", "")).lower()
        children = str(row.get("children-harmful", "")).lower()
        if everyone == "yes":
            label = 1
        elif children == "yes":
            label = 2
        else:
            label = 0
        video_labels[vid][2] = label

    # --- Write output ---
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["video_id", "nicolo", "francesco_c", "francesco_p", "final"])
        for vid, labels in video_labels.items():
            final = majority_vote(labels)
            writer.writerow([vid] + labels + [final])

    print(f"Saved output to {output_path}")

def extract_final():
    input_folder = os.path.join("labelling")
    # Load the CSV and ensure video_id is treated as a string
    path = os.path.join(input_folder, "label_output.csv")

    df = pd.read_csv(path, dtype={"video_id": str})

    # Keep only the columns we care about
    df = df[["video_id", "final"]]

    # Define sort order for final column
    sort_order = {"0": 0, "1": 1, "2": 2, "unclear": 3}
    df["sort_key"] = df["final"].astype(str).map(sort_order)

    # Sort and drop helper column
    df_sorted = df.sort_values(by="sort_key").drop(columns=["sort_key"])

    # Save to new file
    df_sorted.to_csv("label_output_final_only.csv", index=False)

# extract_final()

def video():
    # Load label_output.csv
    label_df = pd.read_csv("labelling/label_output.csv", dtype={"video_id": str})

    # Load videollama.csv
    videollama_df = pd.read_csv("labelling/videollama.csv", dtype={"filename": str})

    # Extract video_id from filename by stripping '.mp4'
    videollama_df["video_id"] = videollama_df["filename"].str.replace(".mp4", "", regex=False)

    # Create videollama label: 0 if "not harmful" in response, else 1
    videollama_df["videollama"] = videollama_df["response"].str.lower().str.contains("not harmful").apply(lambda x: int(0) if x else int(1))

    # Merge on video_id
    merged_df = label_df[["video_id", "final"]].merge(
        videollama_df[["video_id", "videollama"]],
        on="video_id",
        how="left"
    )

    # Save output
    merged_df.to_csv("label_output_with_videollama.csv", index=False)

    print("Saved merged results to label_output_with_videollama.csv")

# video()

def calc_accuracy():
    df = pd.read_csv("labelling/label_output_with_videollama.csv")

    correct = 0

    for _, row in df.iterrows():
        final = str(row["final"]).strip()
        llama = row["videollama"]

        if (llama == 0.0 and final == "0") or (llama == 1.0 and final in ["1", "2"]):
            correct += 1

    print(f"Correct matches: {correct} out of {len(df)}")

def annotate_accur():

    # --- Load CSV ---
    df = pd.read_csv("labelling/label_output.csv", dtype={"video_id": str})

    # Only keep the three annotator columns
    annot_cols = ["nicolo", "francesco_c", "francesco_p"]

    ratings = df[annot_cols].applymap(lambda x: str(x).strip().lower())

    # Replace "unclear" with NaN and coerce to numeric
    ratings = ratings.replace({"unclear": "something wrong"})
    ratings = ratings.apply(pd.to_numeric, errors="coerce")

    # Collapse 2 → 1 (both are harmful)
    ratings = ratings.replace({2: 1})

    # Drop rows with fewer than 2 valid ratings
    valid_mask = ratings.notna().sum(axis=1) >= 2
    ratings = ratings[valid_mask]

    # Build Fleiss’ Kappa matrix: each row is counts for [not harmful (0), harmful (1)]
    cats = [0, 1]
    mat = np.array([[(row == c).sum() for c in cats] for _, row in ratings.iterrows()], dtype=int)

    # Remove rows where there are no ratings at all (shouldn’t happen now)
    mat = mat[mat.sum(axis=1) > 0]

    # mat: N_items x N_categories (here 2: [0,1]), entries are counts per item
    n_per_item = mat.sum(axis=1)
    assert np.all(n_per_item == n_per_item[0]), "Fleiss' kappa assumes constant raters/item"
    n = n_per_item[0]
    N = mat.shape[0]

    # Observed agreement per item: P_i
    P_i = ( (mat * (mat - 1)).sum(axis=1) ) / (n * (n - 1))
    P_bar = P_i.mean()

    # Category proportions across all ratings: p_j
    p_j = mat.sum(axis=0) / (N * n)
    P_e_bar = (p_j ** 2).sum()

    kappa_manual = (P_bar - P_e_bar) / (1 - P_e_bar)

    print(f"P̄ (observed) = {P_bar:.3f}")
    print(f"P̄_e (expected by chance) = {P_e_bar:.3f}")
    print(f"Fleiss κ (manual) = {kappa_manual:.3f}")
    print(f"Category proportions p_j = {p_j}")
    # Compute Fleiss’ Kappa
    kappa = fleiss_kappa(mat, method="fleiss")

    # Percent agreement (how often majority agreed)
    agreements = (mat.max(axis=1) / mat.sum(axis=1)).mean()

    print(f"Items used: {mat.shape[0]}")
    print(f"Fleiss' Kappa (1+2 collapsed): {kappa:.3f}")
    print(f"Mean percent agreement: {agreements*100:.1f}%")

annotate_accur()
calc_accuracy()
'''
Items used: 100
Fleiss' Kappa (1+2 collapsed): 0.260
Mean percent agreement: 81.7%'''