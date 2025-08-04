import pandas as pd
import glob
import os

def extract_harmful_csv(age):
    input_folder = f"classify/thur"
    output_path = f"classify/thur/{age}_harmful_only.csv"
    csv_files = glob.glob(os.path.join(input_folder, f"*classified_results_{age[0]}*.csv"))

    harmful_rows = []

    for file in csv_files:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()

        if "harmful" not in df.columns:
            print(f"Skipping {file}: no 'harmful' column.")
            continue

        filtered = df[df["harmful"] == "harmful"][["video_id", "harmful", "reasoning"]].copy()
        filtered.insert(0, "link", filtered["video_id"].apply(lambda x: f"https://www.tiktok.com/@temp/video/{x}"))
        harmful_rows.append(filtered)

    if harmful_rows:
        result = pd.concat(harmful_rows, ignore_index=True)
        result.to_csv(output_path, index=False)
        print(f"Saved harmful videos to {output_path}")
    else:
        print(f"No harmful videos found for {age}.")

# Generate harmful-only CSVs
extract_harmful_csv("adults")
extract_harmful_csv("children")

