import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

sns.set_theme(style="whitegrid", context="talk")
sns.set_palette("colorblind")
plt.rcParams.update({
    'axes.titlesize': 11,
    'axes.labelsize': 11,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11
})

def compute_search():
    folder_path = os.path.join("classify", "search")
    group_stats = {"Adults": {"harmful": 0, "total": 0},
                   "Children": {"harmful": 0, "total": 0}}
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith(".csv") and "classified_results" in file:
                df = pd.read_csv(os.path.join(folder_path, file))
                df.columns = df.columns.str.strip().str.lower()
                if "harmful" not in df.columns:
                    continue
                group = "Adults" if "_a" in file else "Children" if "_c" in file else None
                if group is None:
                    continue
                group_stats[group]["harmful"] += (df["harmful"] == "harmful").sum()
                group_stats[group]["total"] += len(df)
    rows = []
    for group in ["Adults", "Children"]:
        harmful = group_stats[group]["harmful"]
        total = group_stats[group]["total"]
        proportion = harmful / total if total > 0 else 0.0
        label = "Adults" if group == "Adults" else "Youth"
        rows.append({"Group": label, "ProportionHarmful": proportion})
    return pd.DataFrame(rows)

def compute_passive(day_folders):
    proportions = []
    for day in day_folders:
        folder_path = os.path.join("classify", day)
        if not os.path.exists(folder_path):
            continue
        for file in os.listdir(folder_path):
            if file.endswith(".csv") and "classified_results" in file:
                df = pd.read_csv(os.path.join(folder_path, file))
                df.columns = df.columns.str.strip().str.lower()
                if "harmful" not in df.columns or "account" not in df.columns:
                    continue
                for account, g in df.groupby("account"):
                    group = "Adults" if "_a" in account else "Youth" if "_c" in account else None
                    if group is None:
                        continue
                    harmful = (g["harmful"] == "harmful").sum()
                    total = len(g)
                    prop = harmful / total if total > 0 else 0.0
                    proportions.append({"Group": group, "ProportionHarmful": prop, "Account": account})
    return pd.DataFrame(proportions)

search_df = compute_search()
passive_df = compute_passive(["Thur", "Fri", "Sat", "Sun"])
palette = {"Adults": "#0173b2", "Youth": "#de8f05"}
max_prop = 0.0
if not search_df.empty:
    max_prop = max(max_prop, search_df["ProportionHarmful"].max())
if not passive_df.empty:
    max_prop = max(max_prop, passive_df["ProportionHarmful"].max())
# ylim_top = min(1.0, (max_prop * 1.2) if max_prop > 0 else 0.5)

fig, axes = plt.subplots(1, 2, figsize=(8, 4), sharey=True)

ax1 = axes[0]
if not passive_df.empty:
    sns.boxplot(
        data=passive_df[passive_df["Group"] == "Adults"],
        x="Group", y="ProportionHarmful",
        showcaps=True,
        boxprops={'facecolor': 'None', 'edgecolor': palette["Adults"]},
        whiskerprops={'linewidth': 1, 'color': palette["Adults"]},
        medianprops={'color': palette["Adults"]},
        ax=ax1
    )
    sns.boxplot(
        data=passive_df[passive_df["Group"] == "Youth"],
        x="Group", y="ProportionHarmful",
        showcaps=True,
        boxprops={'facecolor': 'None', 'edgecolor': palette["Youth"]},
        whiskerprops={'linewidth': 1, 'color': palette["Youth"]},
        medianprops={'color': palette["Youth"]},
        ax=ax1
    )
    sns.swarmplot(
        data=passive_df, x="Group", y="ProportionHarmful",
        size=5, linewidth=0.5, edgecolor="black",
        palette=palette, ax=ax1
    )
ax1.set_title("")
ax1.set_xlabel("")
ax1.set_ylabel("% of harmful videos")
# ax1.set_ylim(0, ylim_top)
ax1.yaxis.set_major_formatter(PercentFormatter(1.0))

ax2 = axes[1]
sns.barplot(data=search_df, x="Group", y="ProportionHarmful", palette=palette, ax=ax2)
ax2.set_title("")
ax2.set_xlabel("")
ax2.set_ylabel("")
# ax2.set_ylim(0, ylim_top)
ax2.yaxis.set_major_formatter(PercentFormatter(1.0))

fig.tight_layout(rect=[0, 0, 1, 0.95])
out_path = os.path.join("classify", "desc_combined_swarm_left_bar_right.png")
fig.savefig(out_path, dpi=200, bbox_inches="tight")
print(f"Saved combined figure to {out_path}")
