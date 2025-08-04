import glob
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn.objects as so

# Set seaborn theme
sns.set_theme(style="whitegrid", context="talk")

# Paths to both folders
folders = ["classify/adults", "classify/children"]

# Collect harmful counts from both folders
data = []
for folder_path in folders:
    for file in os.listdir(folder_path):
        if file.endswith("_classified_results.csv"):
            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path)

            # Clean column names
            df.columns = df.columns.str.strip().str.lower()

            if "harmful" in df.columns:
                harmful_count = (df["harmful"] == "harmful").sum()
                label = file.replace("logs_", "").replace("_classified_results.csv", "")
                data.append((label, harmful_count))

# Convert to DataFrame
plot_df = pd.DataFrame(data, columns=["Source", "HarmfulCount"])
plot_df = plot_df.sort_values("Source")

# Plot
plt.figure(figsize=(10, 6))
p = sns.barplot(data=plot_df, x="Source", y="HarmfulCount", palette="rocket")
plt.ylabel("Number of Harmful Descriptions")
plt.xlabel("Account")
plt.title("Harmful Descriptions per CSV")
plt.xticks(rotation=45)
plt.tight_layout()

# Save to file
output_path = os.path.join("classify", "desc_bar_days.png")
p.figure.savefig(output_path, dpi=200, bbox_inches="tight")
print(f"Saved bar plot to {output_path}")

# def scrape(age):
#     input_folder = f"classify/{age}"
#     csv_files = glob.glob(os.path.join(input_folder, "*_classified_results.csv"))
#     counts = []

#     for file in csv_files:
#         df = pd.read_csv(file)
#         df.columns = df.columns.str.strip().str.lower()
#         if "harmful" not in df.columns:
#             print(f"Skipping {file}: no 'harmful' column.")
#             continue
#         count = (df["harmful"] == "harmful").sum()
#         counts.append(count)

#     return pd.DataFrame({
#         "Harmful Videos": counts,
#         "Age": age.capitalize()
#     })

# # Scrape both groups
# a_stats = scrape("adults")
# c_stats = scrape("children")

# # Combine for KDE
# df = pd.concat([a_stats, c_stats], ignore_index=True)

# # KDE Plot
# cap = "Number of Harmful Descriptions"
# p = (
#     so.Plot(df, x="Harmful Videos", color="Age")
#     .add(so.Area(), so.KDE(common_norm=False))
#     .label(title=f"KDE of Video {cap}", x=cap, y="Density")
#     .scale(x="log")
# )

# # Save
# output_path = os.path.join("classify", "harmful_kde.png")
# p.save(output_path, dpi=200, bbox_inches="tight")
# print(f"Saved KDE plot to {output_path}")