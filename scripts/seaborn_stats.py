import os
import glob
import numpy as np
import pandas as pd
import seaborn.objects as so

def scrape(age, col):
    input_folder = f"stats/{age}"
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

    return all_stats

# Set stat to plot
col = "views"
cap = "Plays"

# Scrape both groups and tag them
a_stats = scrape("adults", col)
a_stats["Age"] = "Adults"

c_stats = scrape("children", col)
c_stats["Age"] = "Children"

# Combine
df = pd.concat([a_stats, c_stats], ignore_index=True)

# Optional: add tiny jitter to help KDE math
df[col] += np.random.normal(0, 1e-6, size=len(df))

# Plot
p = (
    so.Plot(df, x=col, color="Age")
    .add(so.Area(), so.KDE(common_norm=False))
    .label(title=f"KDE of Video {cap}", x=cap, y="Density")
    .scale(x="log")
)

# Save
output_path = os.path.join("stats", f"{col}_kde.png")
p.save(output_path, dpi=200, bbox_inches="tight")
print(f"Saved KDE plot to {output_path}")
