import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Set seaborn theme
sns.set_theme(style="whitegrid", context="talk")

# do this for search as well
# days = ["Thur", "Fri", "Sat", "Sun"]
days = ["search"]

# Initialize counters
group_stats = {
    "Adults": {"harmful": 0, "total": 0},
    "Children": {"harmful": 0, "total": 0},
}

for day in days:
    folder_path = os.path.join("classify", day)
    if not os.path.exists(folder_path):
        continue
    print("foldername", folder_path)
    for file in os.listdir(folder_path):
        print("file", file)
        if file.endswith(".csv") and "classified_results" in file:
            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip().str.lower()

            if "harmful" not in df.columns:
                continue

            group = "Adults" if "_a" in file else "Children" if "_c" in file else None
            if group is None:
                continue

            harmful_count = (df["harmful"] == "harmful").sum()
            total_count = len(df)

            group_stats[group]["harmful"] += harmful_count
            group_stats[group]["total"] += total_count

# Compute proportions and print
proportions = []
for group in ["Adults", "Children"]:
    harmful = group_stats[group]["harmful"]
    total = group_stats[group]["total"]
    proportion = harmful / total if total > 0 else 0
    proportions.append({"Group": group, "ProportionHarmful": proportion})
    print(f"{group.title()}: {harmful} harmful / {total} total = {proportion:.2%}")

# Create DataFrame for bar plot
plot_df = pd.DataFrame(proportions)

# Plot
plt.figure(figsize=(6, 4))
p = sns.barplot(data=plot_df, x="Group", y="ProportionHarmful", palette="rocket")
plt.ylabel("Proportion Harmful")
plt.xlabel("Group")
plt.title("Proportion of Harmful Descriptions")
plt.ylim(0, plot_df["ProportionHarmful"].max() * 1.2)
plt.tight_layout()

# Save
output_path = os.path.join("classify", "desc_harmful_prop_search.png")
p.figure.savefig(output_path, dpi=200, bbox_inches="tight")
print(f"Saved plot to {output_path}")
