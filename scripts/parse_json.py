import csv
import json
import os
import random

def extract_hashtags(json_obj):
    all_cycles = []
    for cycle in json_obj.get("cycles", []):
        texts = []
        for api in cycle.get("api_responses", []):
            if api.get("endpoint") == "get_trending":
                if not api.get("response_data"):
                    continue
                for item in api.get("response_data", {}).get("item_list", []):
                    for content in item.get("contents", []):
                        for text_extra in content.get("text_extra", []):
                            if "hashtag_name" in text_extra:
                                texts.append(text_extra["hashtag_name"])

        texts = [x for x in texts if x]
        all_cycles.append(texts)
    return all_cycles

def extract_desc(json_obj):
    all_cycles = []

    for cycle in json_obj.get("cycles", []):
        texts = []
        
        # 1. Append first video ID if available
        video_ids = cycle.get("videos_collected", [])
        if video_ids:
            texts.append(video_ids[0])

        # 2. Loop through api_responses
        for api in cycle.get("api_responses", []):
            if not api:
                continue
            response_data = api.get("response_data")
            if not response_data:
                continue

            item_list = response_data.get("item_list", [])
            if not item_list:
                continue

            first_item = item_list[0]  # only first item
            contents = first_item.get("contents", [])
            for content in contents:
                desc = content.get("desc", "")
                if desc.strip():  # skip empty descriptions
                    texts.append(desc.strip())

            break  # only take from first valid api_response

        if texts:
            all_cycles.append(texts)

    return all_cycles

def extract_desc_search(json_obj, folder_name):
    per_video_entries = []

    for cycle in json_obj.get("cycles", []):
        for api in cycle.get("api_responses", []):
            if not api:
                continue
            response_data = api.get("response_data")
            if not response_data:
                continue

            for entry in response_data.get("data", []):
                item = entry.get("item", {})
                video_id = item.get("id")
                if not video_id:
                    continue

                # Collect unique descriptions from contents only
                seen = set()
                descs = []

                for content in item.get("contents", []):
                    desc = content.get("desc", "").strip()
                    if desc and desc not in seen:
                        descs.append(desc)
                        seen.add(desc)

                if descs:
                    per_video_entries.append({
                        "folder": "adult",
                        "data": [video_id, *descs]
                    })

    return per_video_entries




def extract_stats(json_obj):
    pairs = []
    for cycle in json_obj.get("cycles", []):
        for api in cycle.get("api_responses", []):
            if api is None:
                continue
            if api.get("response_data") is None:
                continue
            if api.get("endpoint") == "get_trending":
                for item in api.get("response_data", {}).get("item_list", []):
                    video_id = item.get("id") or item.get("aweme_id")
                    play_count = item.get("stats", {}).get("play_count")
                    collect_count = item.get("stats", {}).get("collect_count")
                    digg_count = item.get("stats", {}).get("digg_count")
                    comment_count = item.get("stats", {}).get("comment_count")
                    share_count = item.get("stats", {}).get("share_count")

                    if video_id is not None and play_count is not None:
                        pairs.append([video_id, play_count, collect_count, digg_count, comment_count, share_count])
    return pairs

def extract_comments(json_obj):
    all_cycles = []
    for cycle in json_obj.get("cycles", []):
        texts = []
        for id in cycle.get("videos_collected", []):
            texts.append(id)
        for api in cycle.get("api_responses", []):
            if api is None:
                continue
            if api.get("response_data") is None:
                continue
            if api.get("endpoint") == "list_comments":
                for comment in api.get("response_data", {}).get("comments", []):
                    desc = comment.get("share_info", {}).get("desc", "")
                    if "comment:" in desc:
                        # clean up comments
                        comment_text = desc.split("comment:", 1)[1].strip()
                        if comment_text:
                            texts.append(comment_text)
                    else:
                        if desc:
                            texts.append(desc)
        # remove empty
        texts = [x for x in texts if x]
        all_cycles.append(texts)
    return all_cycles


def extract_all(json_obj):
    all_cycles = []
    for cycle in json_obj.get("cycles", []):
        texts = []
        for id in cycle.get("videos_collected", []):
            texts.append(id)
        for api in cycle.get("api_responses", []):
            if api is None:
                continue
            if api.get("response_data") is None:
                continue
            if api.get("endpoint") == "get_trending":
                for item in api.get("response_data", {}).get("item_list", []):
                    author = item.get("author", {})
                    texts.append(author.get("nickname", ""))
                    texts.append(author.get("unique_id", ""))

                    for content in item.get("contents", []):
                        desc = content.get("desc", "")
                        if desc:
                            texts.append(desc)
                        for text_extra in content.get("text_extra", []):
                            if "hashtag_name" in text_extra:
                                texts.append(text_extra["hashtag_name"])

                    music = item.get("music", {})
                    texts.append(music.get("title", ""))

            # comments 
            if api.get("endpoint") == "list_comments":
                for comment in api.get("response_data", {}).get("comments", []):
                    desc = comment.get("share_info", {}).get("desc", "")
                    if "comment:" in desc:
                        # clean up comments
                        comment_text = desc.split("comment:", 1)[1].strip()
                        if comment_text:
                            texts.append(comment_text)
                    else:
                        if desc:
                            texts.append(desc)
        # remove empty
        texts = [x for x in texts if x]
        all_cycles.append(texts)
    return all_cycles

def json_output_desc(dates, day, age):
    parent_folder = ".."
    output_folder = f"desc/{day}"
    os.makedirs(output_folder, exist_ok=True)
    all_cycles = []

    for folder in os.listdir(parent_folder):
        folder_path = os.path.join(parent_folder, folder)
        if os.path.isdir(folder_path) and folder.startswith(f"logs_{age}"):
            for filename in os.listdir(folder_path):
                if filename.endswith(".json") and any(date in filename for date in dates):
                    input_path = os.path.join(folder_path, filename)
                    with open(input_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        extracted_cycles = extract_desc(data)
                        for item in extracted_cycles:
                            all_cycles.append({
                                "folder": folder,
                                "data": item
                            })

    output_file = os.path.join(output_folder, f"logs_{age}_desc.json")
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(all_cycles, out, ensure_ascii=False, indent=2)

# Define which dates to use per day
day_to_dates = {
    # "thur": ["0717", "0724", "0731"],
    # "fri": ["0718", "0725", "0801"],
    # "sat": ["0705","0712","0719","0726","0802"],
    "sun": ["0706","0713","0720", "0727", "0803"]
}

# Run for each day and age group
# for day, dates in day_to_dates.items():
#     for age in ["a", "c"]:
#         json_output_desc(dates=dates, day=day, age=age)

def json_output_random():
    for group in ["a", "c"]:
        all_entries = []
        for day in ["thur", "fri", "sat", "sun"]:
            parent_folder = os.path.join("desc", day)
            if not os.path.exists(parent_folder):
                continue
            filename = f"logs_{group}_desc.json"
            input_path = os.path.join(parent_folder, filename)
            if not os.path.exists(input_path):
                continue
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_entries.extend(data)

        sampled = random.sample(all_entries, 5) 

        os.makedirs("desc", exist_ok=True)
        output_path = os.path.join("desc", f"sampled_{group}_extra.json")
        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(sampled, out, ensure_ascii=False, indent=2)

# json_output_random()

def json_output_random_search():
    import os, json, random, csv

    def load_excluded_ids():
        s = set()
        for folder in ["classify/sampled", "classify"]:
            if not os.path.exists(folder):
                continue
            for fn in os.listdir(folder):
                if not fn.endswith(".csv"):
                    continue
                p = os.path.join(folder, fn)
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        r = csv.DictReader(f)
                        if not r.fieldnames or "video_id" not in r.fieldnames:
                            continue
                        for row in r:
                            vid = str(row.get("video_id", "")).strip()
                            if vid:
                                s.add(vid)
                except Exception:
                    continue
        return s

    excluded = load_excluded_ids()
    used = set()

    for group in ["adult", "children"]:
        filename = f"logs_{group}_desc.json"
        input_path = os.path.join("search", filename)
        if not os.path.exists(input_path):
            continue
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        unique_entries = []
        seen_local = set()
        for entry in data:
            dat = entry.get("data", [])
            vid = str(dat[0]).strip() if dat else ""
            if not vid or vid in excluded or vid in used or vid in seen_local:
                continue
            seen_local.add(vid)
            unique_entries.append(entry)

        take = min(25, len(unique_entries))
        sampled = random.sample(unique_entries, take) if take else []
        for e in sampled:
            d = e.get("data", [])
            if d:
                used.add(str(d[0]).strip())

        os.makedirs("desc", exist_ok=True)
        output_path = os.path.join("desc", f"sampled_search_{group}_extra.json")
        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(sampled, out, ensure_ascii=False, indent=2)
json_output_random_search()

def json_output_desc_search(age):
    parent_folder = f"search/{age}"
    output_file = f"search/logs_{age}_desc.json"
    os.makedirs("search", exist_ok=True)

    all_entries = []

    for filename in os.listdir(parent_folder):
        if filename.endswith(".json"):
            input_path = os.path.join(parent_folder, filename)
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                folder_name = filename.replace(".json", "")
                per_video = extract_desc_search(data, folder_name)
                all_entries.extend(per_video)

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(all_entries, out, ensure_ascii=False, indent=2)

# json_output_desc_search("children")
# File paths

def json_output_comments():
    folder = "logs_c5"
    input_folder = f"../{folder}"
    output_folder = "comments"
    output_file = os.path.join(output_folder, f"{folder}_comments.json")  

    os.makedirs(output_folder, exist_ok=True)

    all_cycles = []
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        if os.path.isdir(input_path):
            print(f"Skipping directory: {filename}")
            continue
        # print("fi", filename)
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            extracted_cycles = extract_comments(data)  # assume returns a list
            all_cycles.extend(extracted_cycles)

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(all_cycles, out, ensure_ascii=False, indent=2)

# json_output_comments()

def json_output_stats(id):
    folder = f"logs_{id}"
    input_folder = f"../{folder}"
    output_folder = "stats/children"
    output_file = os.path.join(output_folder, f"{folder}_stats.csv")  

    os.makedirs(output_folder, exist_ok=True)

    all_pairs = []
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        if os.path.isdir(input_path):
            continue
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            extracted_pairs = extract_stats(data)
            all_pairs.extend(extracted_pairs)

    # Write as CSV
    with open(output_file, "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["video_id", "views", "collects", "diggs", "comments", "shares"])
        writer.writerows(all_pairs)

# for letter in ["a", "c"]:
#     for i in range(1, 11):
#         print("hey", f"{letter}{i}")
#         json_output_stats(f"{letter}{i}")

def hashtag_output():
    input_folder = "../logs_c2"
    output_folder = "texts"
    output_file = os.path.join(output_folder, f"{input_folder}.txt")

    os.makedirs(output_folder, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as out:
        for filename in os.listdir(input_folder):
            input_path = os.path.join(input_folder, filename)
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Use your real extraction function here!
                extracted_cycles = extract_hashtags(data)
                for item_list in extracted_cycles:
                    line = " ".join(str(x) for x in item_list if x)  # skip empty values
                    out.write(line + "\n")


