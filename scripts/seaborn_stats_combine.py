import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from seaborn import objects as so
import seaborn as sns
import math

# ACL require font 11
sns.set_palette("colorblind")
plt.rcParams.update({
    'axes.titlesize': 11,
    'axes.labelsize': 11,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11
})

def scrape(age, col):
    input_folder = f"stats/{age}"
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()
        if col in df.columns:
            df = df[[col]].copy()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            dfs.append(df)
        else:
            print(f"skipping {file}")
    if not dfs:
        raise ValueError(f"No CSVs with a '{col}' column found in {input_folder}.")
    all_stats = pd.concat(dfs, ignore_index=True)
    all_stats = all_stats.replace([np.inf, -np.inf], np.nan).dropna(subset=[col])
    if all_stats.empty:
        raise ValueError(f"No valid {col} data to plot.")
    return all_stats

# cols = data cols, caps = axis labels
cols = ["views", "diggs", "comments"]
caps = ["Views", "Likes", "Comments"]

nplots = len(cols)
ncols = 3
nrows = math.ceil(nplots / ncols)

# >>> CHANGED: make figure a bit shorter. 4, 6 6,4
fig, axs = plt.subplots(nrows, ncols, figsize=(12, 4), sharey=True)
axs = axs.flatten()

for i, (col, cap) in enumerate(zip(cols, caps)):
    a_stats = scrape("adults", col)
    a_stats["Age"] = "Adults"
    c_stats = scrape("children", col)
    c_stats["Age"] = "Youth"

    df = pd.concat([a_stats, c_stats], ignore_index=True)
    df = df.dropna(subset=[col])
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[np.isfinite(df[col])]
    df[col] = df[col].astype("float64")
    df[col] += np.random.normal(0, 1e-6, size=len(df))

    # >>> CHANGED: only show "Density" at the start of each row
    y_label = "Density" if (i % ncols == 0) else ""

    (
        so.Plot(df, x=col, color="Age")
        .add(so.Line(), so.KDE(common_norm=False))
        .label(x=cap, y=y_label)
        .scale(x="log")
        .on(axs[i])
        .plot()
    )

# >>> CHANGED: hide any unused axes (the 6th slot)
for j in range(nplots, len(axs)):
    fig.delaxes(axs[j])  # removes the extra axis entirely

fig.suptitle("KDE of Video Stats by Age Group", fontsize=11)
# >>> CHANGED: layout tweaks to reduce gaps
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.subplots_adjust(hspace=0.35, wspace=0.25)

output_path = os.path.join("stats", "all_stats_kde_less.png")
fig.savefig(output_path, dpi=200, bbox_inches="tight")
print(f"\nSaved to {output_path}")
