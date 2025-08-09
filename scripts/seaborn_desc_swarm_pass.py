import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="whitegrid", context="talk")
sns.set_palette("colorblind")
plt.rcParams.update({
    'axes.titlesize': 11,
    'axes.labelsize': 11,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11
})

day_folders = ["Thur", "Fri", "Sat", "Sun"]
# only passive boxplot
def get_account_proportions(folders):
    proportions = []
    for day in folders:
        folder_path = os.path.join("classify", day)
        if not os.path.exists(folder_path):
            continue
        for file in os.listdir(folder_path):
            if file.endswith(".csv") and "classified_results" in file:
                file_path = os.path.join(folder_path, file)
                df = pd.read_csv(file_path)
                df.columns = df.columns.str.strip().str.lower()

                if "harmful" not in df.columns:
                    continue

                if "account" not in df.columns:
                    print("wrong")
                    continue
                for account, group_df in df.groupby("account"):
                    group = "Adults" if "_a" in account else "Youth" if "_c" in account else None
                    if group is None:
                        continue

                    harmful_count = (group_df["harmful"] == "harmful").sum()
                    total_count = len(group_df)
                    proportion = harmful_count / total_count if total_count > 0 else 0

                    proportions.append({
                        "Group": group,
                        "ProportionHarmful": proportion,
                        "Account": account
                    })
    return proportions

day_data = get_account_proportions(day_folders)
plot_df = pd.DataFrame(day_data)

youth_outliers = plot_df[plot_df["Group"] == "Youth"].sort_values("ProportionHarmful", ascending=False)
print(youth_outliers.head(2))
outlier_values = youth_outliers["ProportionHarmful"].head(2).tolist()
print(outlier_values)


green_color = "#029e73"
blue_color = "#0173b2"
orange_color = "#de8f05"


plt.figure(figsize=(6, 5))

sns.boxplot(data=plot_df[plot_df["Group"] == "Adults"],
            x="Group", y="ProportionHarmful",
            showcaps=True,
            boxprops={'facecolor': 'None', 'edgecolor': blue_color},
            whiskerprops={'linewidth': 1, 'color': blue_color},
            medianprops={'color': blue_color})

sns.boxplot(data=plot_df[plot_df["Group"] == "Youth"],
            x="Group", y="ProportionHarmful",
            showcaps=True,
            boxprops={'facecolor': 'None', 'edgecolor': orange_color},
            whiskerprops={'linewidth': 1, 'color': orange_color},
            medianprops={'color': orange_color})

sns.swarmplot(data=plot_df, x="Group", y="ProportionHarmful",
              size=5, linewidth=0.5, edgecolor="black",
              palette={"Adults": blue_color, "Youth": orange_color})

plt.title("Distribution of Harmful Descriptions")
plt.ylim(0, plot_df["ProportionHarmful"].max() * 1.1)
plt.xlabel("")

plt.ylabel("")
plt.tight_layout()

out_path = os.path.join("classify", "desc_box_fyf_only.png")
plt.savefig(out_path, dpi=200, bbox_inches="tight")
print(f"Saved to: {out_path}")

# # Calculate and print medians
# adult_median = plot_df[plot_df["Group"] == "Adults"]["ProportionHarmful"].median()
# child_median = plot_df[plot_df["Group"] == "Youth"]["ProportionHarmful"].median()

# print(f"Adults median proportion harmful: {adult_median:.3f}")
# print(f"Youth median proportion harmful: {child_median:.3f}")

# '''
# Adults median proportion harmful: 0.034
# Children median proportion harmful: 0.023

# 57  Youth           0.250000  logs_c7
# 59  Youth           0.142857  logs_c9
# '''