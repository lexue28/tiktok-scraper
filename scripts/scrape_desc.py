import pandas as pd
import glob
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def extract_harmful_all_days(age):
    days = ["search"]
    existing_a = "classify/adults_harmful_only.csv"
    existing_c = "classify/children_harmful_only.csv"
    existing_ids = set()

    for existing_file in [existing_a, existing_c]:
        if os.path.exists(existing_file):
            try:
                df_existing = pd.read_csv(existing_file)
                if "video_id" in df_existing.columns:
                    existing_ids.update(df_existing["video_id"].dropna().astype(str))
            except Exception as e:
                print(f"Failed to read")

    mega_rows = []
    for day in days:
        input_folder = f"classify/{day}"
        csv_files = glob.glob(os.path.join(input_folder, f"*classified_results_{age[0]}*.csv"))

        for file in csv_files:
            df = pd.read_csv(file)
            print("file", file)
            df.columns = df.columns.str.strip().str.lower()

            if "harmful" not in df.columns:
                print(f"skipping {file}")
                continue

            filtered = df[df["harmful"] == "harmful"][["video_id", "harmful", "reasoning"]].copy()
            filtered["video_id"] = filtered["video_id"].astype(str)
            filtered = filtered[~filtered["video_id"].isin(existing_ids)]

            if not filtered.empty:
                filtered.insert(0, "link", filtered["video_id"].apply(lambda x: f"https://www.tiktok.com/@temp/video/{x}"))
                mega_rows.append(filtered)

    if mega_rows:
        result = pd.concat(mega_rows, ignore_index=True)
        result.drop_duplicates(subset="video_id", inplace=True)
        output_path = f"classify/{age}_harmful_search.csv"
        result.to_csv(output_path, index=False)
        return len(result)
    else:
        return 0

# count_adults = extract_harmful_all_days("adults")
# count_children = extract_harmful_all_days("children")

# plot_df = pd.DataFrame([
#     {"Source": "adults", "HarmfulCount": count_adults},
#     {"Source": "children", "HarmfulCount": count_children}
# ])

# plt.figure(figsize=(8, 6))
# p = sns.barplot(data=plot_df, x="Source", y="HarmfulCount", palette="Set2")
# plt.ylabel("Number of Harmful Descriptions")
# plt.xlabel("Group")
# plt.title("Total Harmful Descriptions by Age Group")
# plt.tight_layout()

# output_path = os.path.join("classify", "desc_bar_days.png")
# p.figure.savefig(output_path, dpi=200, bbox_inches="tight")

def clean():
    # filter out duplicates
    adults_path = "classify/adults_harmful_search.csv"
    children_path = "classify/children_harmful_search.csv"
    cleaned_path = "classify/adult_search_cleaned.csv"

    df_adults = pd.read_csv(adults_path)
    df_children = pd.read_csv(children_path)

    df_adults["video_id"] = df_adults["video_id"].astype(str)
    df_children["video_id"] = df_children["video_id"].astype(str)

    children_ids = set(df_children["video_id"])
    filtered_adults = df_adults[~df_adults["video_id"].isin(children_ids)].copy()

    filtered_adults.to_csv(cleaned_path, index=False)
    print(f"Saved non-overlapping entries")

clean()
