import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from seaborn import objects as so
import seaborn as sns

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

def print_stats(df, col):
    print(f"\nStats for {col}:")
    for group in df["Age"].unique():
        sub = df[df["Age"] == group][col]
        median = np.median(sub)
        p95 = np.percentile(sub, 95)
        print(f"  {group}: Median = {median:.2f}, 95th percentile = {p95:.2f}")

# caps is for names of axis labels
cols = ["views", "diggs", "comments", "shares", "collects"]
caps = ["Plays", "Diggs", "Comments", "Shares", "Collects"]

fig, axs = plt.subplots(5, 1, figsize=(6, 20), sharey=True)
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
    (
        so.Plot(df, x=col, color="Age")
        .add(so.Line(), so.KDE(common_norm=False))
        .label(x=cap, y="Density")
        .scale(x="log")
        .on(axs[i])
        .plot()
    )

fig.suptitle("KDE of Video Stats by Age Group", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.97])  # reduce gap
fig.subplots_adjust(hspace=0.3)  # vert spacing
output_path = os.path.join("stats", "all_stats_kde_form.png")
fig.savefig(output_path, dpi=200, bbox_inches="tight")
print(f"\nSaved to {output_path}")

'''

Stats for Views:
  Adults: Median = 1500000.00, 95th percentile = 30200000.00        
  Children: Median = 1500000.00, 95th percentile = 28835000.00      

Stats for Diggs:
  Adults: Median = 104600.00, 95th percentile = 2200000.00
  Children: Median = 104050.00, 95th percentile = 2000000.00        

Stats for Comments:
  Adults: Median = 704.00, 95th percentile = 9984.80
  Children: Median = 648.50, 95th percentile = 12000.00

Stats for Shares:
  Adults: Median = 3740.00, 95th percentile = 201500.00
  Children: Median = 3382.50, 95th percentile = 185250.00

Stats for Collects:
  Adults: Median = 4617.00, 95th percentile = 114300.00
  Children: Median = 4458.00, 95th percentile = 106315.00'''