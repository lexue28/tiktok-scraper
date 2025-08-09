import os
import re
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Paths
adult_folder = "stats/adults"
child_folder = "stats/children"

adult_files = sorted([f for f in os.listdir(adult_folder) if f.endswith(".csv")])
child_files = sorted([f for f in os.listdir(child_folder) if f.endswith(".csv")])

account_to_vids = {}

def clean_label(filename):
    m = re.search(r'(a|c)(\d+)', filename)
    if m:
        return f"{m.group(1)}{int(m.group(2))}"
    return filename

def load_videos_from_folder(folder, files):
    for f in files:
        path = os.path.join(folder, f)
        df = pd.read_csv(path)
        if "video_id" not in df.columns:
            continue
        vids = set(df["video_id"].dropna().astype(str))
        account_name = clean_label(f)
        account_to_vids[account_name] = vids

load_videos_from_folder(adult_folder, adult_files)
load_videos_from_folder(child_folder, child_files)

def sort_key(name):
    return (0 if name.startswith("a") else 1, int(name[1:]))

accounts = sorted(account_to_vids.keys(), key=sort_key)
n = len(accounts)
M = np.zeros((n, n), dtype=float)
row_sizes = {acc: len(account_to_vids[acc]) for acc in accounts}

for i, ai in enumerate(accounts):
    size_i = row_sizes[ai] or 1 
    for j, aj in enumerate(accounts):
        if i == j:
            M[i, j] = 0.0  
        else:
            inter = len(account_to_vids[ai] & account_to_vids[aj])
            M[i, j] = 100.0 * inter / size_i  

M_df = pd.DataFrame(M, index=accounts, columns=accounts)
# no lower
mask = np.tril(np.ones_like(M_df, dtype=bool))

sns.set_theme(style="white", context="talk")
plt.figure(figsize=(10, 8))
ax = sns.heatmap(
    M_df,
    mask=mask,
    cmap="cividis",              
    annot=True,
    fmt=".0f",                  
    annot_kws={"size": 10},
    linewidths=0.5,
    linecolor="white",
    vmin=0, vmax=100,              
    cbar_kws={"label": "Overlap (%)"}
)
ax.set_title("FYF Overlap (%)")
ax.set_xlabel("Account")
ax.set_ylabel("Account")
plt.tight_layout()

out_path = "stats/account_overlap_heatmap_new.png"
plt.savefig(out_path, dpi=200, bbox_inches="tight")
