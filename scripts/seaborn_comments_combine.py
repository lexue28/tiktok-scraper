import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns
import seaborn.objects as so
from scipy.stats import gaussian_kde

# detoxify categories
target_cols = [
    "toxicity",
    "severe_toxicity",
    "obscene",
    "identity_attack",
    "insult",
    "threat",
    "sexual_explicit"
]

def scrape(age, col):
    input_folder = f"comments/detoxify/{age}"
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    dfs = []

    for file in csv_files:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()
        if col in df.columns:
            dfs.append(df[col])

    all_stats = pd.DataFrame({col: pd.concat(dfs, ignore_index=True)})
    all_stats[col] = pd.to_numeric(all_stats[col], errors="coerce")
    all_stats = all_stats.replace([np.inf, -np.inf], np.nan).dropna(subset=[col])
    return all_stats

def scrape_max(age):
    input_folder = f"comments/detoxify/{age}"
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    dfs = []

    for file in csv_files:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()
        if any(col in df.columns for col in target_cols):
            dfs.append(df)
        else:
            print("skipping")

    all_data = pd.concat(dfs, ignore_index=True)
    all_data = all_data[[col for col in target_cols if col in all_data.columns]]
    all_data = all_data.apply(pd.to_numeric, errors="coerce")
    all_data = all_data.replace([np.inf, -np.inf], np.nan).dropna(how="all", subset=target_cols)

    all_data["max"] = all_data.max(axis=1)
    return all_data

a_stats = scrape("adults", "toxicity")
a_stats["Age"] = "Adults"
c_stats = scrape("children", "toxicity")
c_stats["Age"] = "Youth"
tox_df = pd.concat([a_stats, c_stats], ignore_index=True)
a_stats = scrape_max("adults")
a_stats["Age"] = "Adults"
c_stats = scrape_max("children")
c_stats["Age"] = "Youth"
max_df = pd.concat([a_stats, c_stats], ignore_index=True)

sns.set_palette("colorblind")
plt.rcParams.update({
    'axes.titlesize': 11,
    'axes.labelsize': 11,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11
})


fig = plt.figure(figsize=(6, 8))
gs = GridSpec(3, 1, figure=fig)


ax1 = fig.add_subplot(gs[0])
(
    so.Plot(tox_df, x="toxicity", color="Age")
    .add(so.Line(), so.KDE(common_norm=False))
    .label(title="General Toxicity", x="Toxicity Score", y="Density")
    .scale(x="log")
    .on(ax1)
    .plot()
)

ax2 = fig.add_subplot(gs[1])
(
    so.Plot(max_df, x="max", color="Age")
    .add(so.Line(), so.KDE(common_norm=False))
    .label(title="Maximum Toxicity", x="Toxicity Score", y="Density")
    .scale(x="log")
    .on(ax2)
    .plot()
)

plt.tight_layout()
output_path = os.path.join("comments/detoxify", "comment_toxicity_all.png")
plt.savefig(output_path, dpi=200, bbox_inches="tight")

def print_stats(df, value_col):
    print(f"\nStats for {value_col}:")
    for group in df["Age"].unique():
        sub = df[df["Age"] == group][value_col]
        median = np.median(sub)
        p95 = np.percentile(sub, 95)
        print(f"{group}: Median = {median:.4f}, 95th percentile = {p95:.4f}")

# print_stats(tox_df, "toxicity")
# print_stats(avg_df, "avg")
# print_stats(max_df, "max")

def find_kde_peak(values):
    values = values.dropna().values
    if len(values) < 2:
        return np.nan, np.nan
    kde = gaussian_kde(values)
    x_grid = np.linspace(values.min(), values.max(), 1000)
    y_vals = kde(x_grid)
    max_idx = np.argmax(y_vals)
    return x_grid[max_idx], y_vals[max_idx]

def print_kde_peaks(df, colname):
    print(f"\nKDE Peak for: {colname}")
    peaks = {}
    for age in ["Adults", "Youth"]:
        subset = df[df["Age"] == age][colname]
        x_peak, y_peak = find_kde_peak(subset)
        peaks[age] = y_peak
        if np.isnan(y_peak):
            print(f"{age}: Not enough data")
        else:
            print(f"{age}: x = {x_peak:.4f}, y = {y_peak:.4f}")
    if not any(np.isnan(v) for v in peaks.values()):
        print(f"Youth - Adults Peak Y diff: {peaks['Youth'] - peaks['Adults']:.4f}")

# print_kde_peaks(tox_df, "toxicity")
# print_kde_peaks(avg_df, "avg")
# print_kde_peaks(max_df, "max")

'''
Stats for toxicity:
Adults: Median = 0.0035, 95th percentile = 0.2894
Youth: Median = 0.0028, 95th percentile = 0.2671

Stats for avg:
Adults: Median = 0.0027, 95th percentile = 0.0650
Youth: Median = 0.0025, 95th percentile = 0.0561

Stats for max:
Adults: Median = 0.0089, 95th percentile = 0.2924
Youth: Median = 0.0083, 95th percentile = 0.2671

KDE Peak for: toxicity
Adults: x = 0.0041, y = 17.2817
Youth: x = 0.0041, y = 18.7349
Youth - Adults Peak Y diff: 1.4532

KDE Peak for: avg
Adults: x = 0.0022, y = 64.3754
Youth: x = 0.0022, y = 67.8415
Youth - Adults Peak Y diff: 3.4661

KDE Peak for: max
Adults: x = 0.0082, y = 16.2684
Youth: x = 0.0072, y = 17.4265
Youth - Adults Peak Y diff: 1.1581
'''