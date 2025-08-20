import glob
import os
import csv
import re
import pandas as pd
from collections import defaultdict, Counter
import numpy as np
from statsmodels.stats.inter_rater import fleiss_kappa

def extract_labels():
    input_folder = os.path.join("labelling", "manual", "take2")
    output_path = os.path.join("labelling/manual/take2", "label_output_2.csv")
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
        everyone = str(row.get("harmful for adults", "")).lower()
        children = str(row.get("harmful for children", "")).lower()
        if everyone == "harmful" or children == "harmful":
            label = 1
        # elif children == "harmful":
        #     label = 2
        else:
            label = 0
        video_labels[vid][i] = label

    # francesco_c_path = os.path.join(input_folder, "francesco_c.csv")
    # df_fc = pd.read_csv(francesco_c_path, dtype={"video_id": str}, encoding="ISO-8859-1")
    # for _, row in df_fc.iterrows():
    #     vid = str(row["video_id"]).strip()
    #     label = row.get("label")
    #     if pd.notna(label):
    #         video_labels[vid][1] = int(label)

    # francesco_p_path = os.path.join(input_folder, "francesco_p.csv")
    # df_fp = pd.read_csv(francesco_p_path, dtype={"video_id": str})
    # for _, row in df_fp.iterrows():
    #     vid = str(row["video_id"]).strip()
    #     everyone = str(row.get("everyone-harmful", "")).lower()
    #     children = str(row.get("children-harmful", "")).lower()
    #     if everyone == "yes":
    #         label = 1
    #     elif children == "yes":
    #         label = 2
    #     else:
    #         label = 0
    #     video_labels[vid][2] = label

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["video_id", "nicolo", "francesco_c", "francesco_p", "final"])
        for vid, labels in video_labels.items():
            final = majority_vote(labels)
            writer.writerow([vid] + labels + [final])

def extract_labels_take2():
    input_folder = os.path.join("labelling/manual/take2")
    output_path = os.path.join("labelling/manual/take2/label_output_2.csv")

    csv_files = sorted(glob.glob(os.path.join(input_folder, "*.csv")))[:3]
    rater_names = [os.path.splitext(os.path.basename(p))[0] for p in csv_files]
    video_labels = defaultdict(lambda: [None] * len(csv_files))

    def majority_vote(labels):
        vals = [x for x in labels if x is not None]
        counts = Counter(vals)
        top_label, top_count = counts.most_common(1)[0]
        if list(counts.values()).count(top_count) > 1:
            return "unclear"
        return "yes" if top_label == 1 else "no"

    for i, path in enumerate(csv_files):
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.reader(fh)
            for row in reader:
                if not row or len(row) < 4:
                    continue
                vid = str(row[0]).strip()
                if not vid:
                    continue
                # last two col important
                a = str(row[-2]).strip().lower()
                c = str(row[-1]).strip().lower()
                # if harmful to either children or adult
                label = 1 if (a == "yes" or c == "yes") else 0
                video_labels[vid][i] = label

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["video_id"] + rater_names + ["final"])
        for vid, labels in video_labels.items():
            final = majority_vote(labels)
            writer.writerow([vid] + labels + [final])

# extract_labels_take2()

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

def video_vl():
    label_df = pd.read_csv("labelling/take2/label_output_2.csv", dtype={"video_id": str})
    videollama_df = pd.read_csv("labelling/take2/videollama_2.csv", dtype={"filename": str})
    videollama_df["video_id"] = videollama_df["filename"].str.replace(".mp4", "", regex=False)
    videollama_df["videollama"] = videollama_df["response"].str.lower().str.contains("not harmful").apply(lambda x: "no" if x else "yes")
    merged_df = label_df[["video_id", "final"]].merge(
        videollama_df[["video_id", "videollama"]],
        on="video_id",
        how="left"
    )
    merged_df.to_csv("labelling/take2/label_output_with_videollama.csv", index=False)

    
def video_gpt():
    label_df = pd.read_csv("labelling/take2/label_output_2.csv",
                           dtype={"video_id": str}, encoding="utf-8-sig")

    rows = []
    with open("labelling/take2/gpt.csv", "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if header:
            header = [h.strip().lower() for h in header]
        for raw in reader:
            if not raw:
                continue
            if header and len(raw) == 5:
                vid = str(raw[0]).strip()
                lab = str(raw[3]).strip().lower()
            else:
                line = ",".join(raw)
                vid = re.search(r"(\d{15,22})", line)
                vid = vid.group(1) if vid else ""
                m = re.search(r"(not harmful|harmful)", line, flags=re.I)
                lab = m.group(1).lower() if m else ""
            if not vid:
                continue
            if lab not in {"harmful", "not harmful"}:
                continue
            rows.append({"video_id": vid, "gpt": "no" if lab == "not harmful" else "yes"})

    gpt_df = pd.DataFrame(rows).drop_duplicates("video_id", keep="first")

    out = label_df[["video_id", "final"]].merge(gpt_df, on="video_id", how="left")
    out.to_csv("labelling/take2/label_output_with_gpt.csv", index=False, encoding="utf-8")

# video_gpt()

def calc_accuracy():
    df = pd.read_csv("labelling/take2/label_output_with_videollama.csv")

    correct = 0

    for _, row in df.iterrows():
        final = str(row["final"]).strip()
        llama = row["videollama"]

        if (llama == "no" and final == "no") or (llama == "yes" and final == "yes"):
            correct += 1

    print(f"correct matches: {correct}")

def annotate_accur():
    df = pd.read_csv("labelling/take2/label_output_2.csv", dtype={"video_id": str})
    annot_cols = ["nicolo", "francesco_c", "placeholder"]

    ratings = df[annot_cols].applymap(lambda x: str(x).strip().lower())
    ratings = ratings.apply(pd.to_numeric, errors="coerce")

    # change 2 → 1 (both are harmful)
    # ratings = ratings.replace({2: 1})

    cats = [0, 1]
    mat = np.array([[(row == c).sum() for c in cats] for _, row in ratings.iterrows()], dtype=int)
    mat = mat[mat.sum(axis=1) > 0]
    n_per_item = mat.sum(axis=1)
    assert np.all(n_per_item == n_per_item[0])
    n = n_per_item[0]
    N = mat.shape[0]
    kappa = fleiss_kappa(mat, method="fleiss")
    agreements = (mat.max(axis=1) / mat.sum(axis=1)).mean()
    print(f"Fleiss' Kappa: {kappa:.3f}")
    print(f"Mean percent agreement: {agreements*100:.1f}%")

annotate_accur()
calc_accuracy()

'''
gpt:
Fleiss' Kappa: 0.452
Mean percent agreement: 87.3%
correct matches: 59
'''

'''
videollama:
Fleiss' Kappa: 0.452
Mean percent agreement: 87.3%
correct matches: 58
'''