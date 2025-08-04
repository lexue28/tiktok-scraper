import os
import glob
import numpy as np
import pandas as pd
import seaborn.objects as so

def scrape(age, col):
    input_folder = f"comments/detoxify/{age}"
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    dfs = []

    for file in csv_files:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()
        if col in df.columns:
            dfs.append(df[col])
        else:
            print(f"Skipping {file}: no '{col}' column.")

    if not dfs:
        raise ValueError(f"No CSVs with a '{col}' column found in {input_folder}.")

    all_stats = pd.DataFrame({col: pd.concat(dfs, ignore_index=True)})
    all_stats[col] = pd.to_numeric(all_stats[col], errors="coerce")
    all_stats = all_stats.replace([np.inf, -np.inf], np.nan).dropna(subset=[col])

    if all_stats.empty:
        raise ValueError(f"No valid {col} data to plot.")

    # all_stats[col] *= 100
    return all_stats

# # Set stat to plot
# col = "toxicity"
# cap = "Average Toxicity Percentage"

# # Scrape both groups and tag them
# a_stats = scrape("adults", col)
# a_stats["Age"] = "Adults"

# c_stats = scrape("children", col)
# c_stats["Age"] = "Children"

# # Combine
# df = pd.concat([a_stats, c_stats], ignore_index=True)

# # Optional: add tiny jitter to help KDE math
# # df[col] += np.random.normal(0, 1e-6, size=len(df))

# # Plot
# p = (
#     so.Plot(df, x=col, color="Age")
#     .add(so.Area(), so.KDE(common_norm=False))
#     .label(title=f"KDE of Video {cap}", x=cap, y="Density")
#     .scale(x="log")
# )

# # Save
# output_path = os.path.join("comments/detoxify", f"{col}_percentage_kde.png")
# p.save(output_path, dpi=200, bbox_inches="tight")
# print(f"Saved KDE plot to {output_path}")

def scrape_max(age):
    input_folder = f"comments/detoxify/{age}"
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    dfs = []

    target_cols = [
        "toxicity",
        "severe_toxicity",
        "obscene",
        "identity_attack",
        "insult",
        "threat",
        "sexual_explicit"
    ]

    for file in csv_files:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()
        if any(col in df.columns for col in target_cols):
            dfs.append(df)
        else:
            print(f"Skipping {file}: none of the target columns found.")

    if not dfs:
        raise ValueError(f"No CSVs with target columns found in {input_folder}.")

    # Concatenate and filter to just target columns
    all_data = pd.concat(dfs, ignore_index=True)
    all_data = all_data[[col for col in target_cols if col in all_data.columns]]

    # Convert all to numeric and drop rows with all-NaN
    all_data = all_data.apply(pd.to_numeric, errors="coerce")
    all_data = all_data.replace([np.inf, -np.inf], np.nan).dropna(how="all", subset=target_cols)

    if all_data.empty:
        raise ValueError(f"No valid data to plot in columns: {target_cols}")

    # Multiply by 100 for percentage
    # all_data *= 100

    # Add max column
    all_data["max"] = all_data.max(axis=1)

    return all_data

# Set stat to plot
cap = "Max Toxicity"

# Scrape both groups and tag them
a_stats = scrape_max("adults")
a_stats["Age"] = "Adults"

c_stats = scrape_max("children")
c_stats["Age"] = "Children"

# Combine
df = pd.concat([a_stats, c_stats], ignore_index=True)

# Optional: add tiny jitter to help KDE math
# df[col] += np.random.normal(0, 1e-6, size=len(df))

# Plot
p = (
    so.Plot(df, x="max", color="Age")
    .add(so.Area(), so.KDE(common_norm=False))
    .label(title=f"KDE of Video {cap}", x=cap, y="Density")
    .scale(x="log")
)

# Save
output_path = os.path.join("comments/detoxify", f"max_tox_kde.png")
p.save(output_path, dpi=200, bbox_inches="tight")
print(f"Saved KDE plot to {output_path}")