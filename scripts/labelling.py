import os
import csv
import pandas as pd
from collections import defaultdict, Counter
import numpy as np
from statsmodels.stats.inter_rater import fleiss_kappa

def extract_labels():
    input_folder = os.path.join("labelling", "manual")
    output_path = os.path.join("labelling", "label_output.csv")
    video_labels = defaultdict(lambda: [None, None, None])

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

    francesco_c_path = os.path.join(input_folder, "francesco_c.csv")
    df_fc = pd.read_csv(francesco_c_path, dtype={"video_id": str}, encoding="ISO-8859-1")
    for _, row in df_fc.iterrows():
        vid = str(row["video_id"]).strip()
        label = row.get("label")
        if pd.notna(label):
            video_labels[vid][1] = int(label)

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

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["video_id", "nicolo", "francesco_c", "francesco_p", "final"])
        for vid, labels in video_labels.items():
            final = majority_vote(labels)
            writer.writerow([vid] + labels + [final])

def extract_final():
    input_folder = os.path.join("labelling")
    path = os.path.join(input_folder, "label_output.csv")
    df = pd.read_csv(path, dtype={"video_id": str})
    df = df[["video_id", "final"]]
    sort_order = {"0": 0, "1": 1, "2": 2, "unclear": 3}
    df["sort_key"] = df["final"].astype(str).map(sort_order)
    df_sorted = df.sort_values(by="sort_key").drop(columns=["sort_key"])
    df_sorted.to_csv("label_output_final_only.csv", index=False)

# extract_final()

def video():
    label_df = pd.read_csv("labelling/label_output.csv", dtype={"video_id": str})
    videollama_df = pd.read_csv("labelling/videollama.csv", dtype={"filename": str})
    videollama_df["video_id"] = videollama_df["filename"].str.replace(".mp4", "", regex=False)
    videollama_df["videollama"] = videollama_df["response"].str.lower().str.contains("not harmful").apply(lambda x: int(0) if x else int(1))
    merged_df = label_df[["video_id", "final"]].merge(
        videollama_df[["video_id", "videollama"]],
        on="video_id",
        how="left"
    )
    merged_df.to_csv("label_output_with_videollama.csv", index=False)

# video()

def calc_accuracy():
    df = pd.read_csv("labelling/label_output_with_videollama.csv")

    correct = 0

    for _, row in df.iterrows():
        final = str(row["final"]).strip()
        llama = row["videollama"]

        if (llama == 0.0 and final == "0") or (llama == 1.0 and final in ["1", "2"]):
            correct += 1

    print(f"correct matches: {correct}")

def annotate_accur():
    df = pd.read_csv("labelling/label_output.csv", dtype={"video_id": str})
    annot_cols = ["nicolo", "francesco_c", "francesco_p"]

    ratings = df[annot_cols].applymap(lambda x: str(x).strip().lower())
    ratings = ratings.apply(pd.to_numeric, errors="coerce")

    # change 2 → 1 (both are harmful)
    ratings = ratings.replace({2: 1})

    cats = [0, 1]
    mat = np.array([[(row == c).sum() for c in cats] for _, row in ratings.iterrows()], dtype=int)
    mat = mat[mat.sum(axis=1) > 0]
    n_per_item = mat.sum(axis=1)
    assert np.all(n_per_item == n_per_item[0]), "Fleiss' kappa assumes constant raters/item"
    n = n_per_item[0]
    N = mat.shape[0]
    kappa = fleiss_kappa(mat, method="fleiss")
    agreements = (mat.max(axis=1) / mat.sum(axis=1)).mean()
    print(f"Fleiss' Kappa: {kappa:.3f}")
    print(f"Mean percent agreement: {agreements*100:.1f}%")

annotate_accur()
# calc_accuracy()
'''
Fleiss' Kappa (1+2 collapsed): 0.260
Mean percent agreement: 81.7%'''