import json
import os

def extract_fields_per_cycle(json_obj):
    all_cycles = []
    for cycle in json_obj.get("cycles", []):
        texts = []
        for id in cycle.get("videos_collected", []):
            texts.append(id)
        for api in cycle.get("api_responses", []):
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

# File paths
js_file = "bot_activity_20250714_092319"
input = f"../logs_c2/{js_file}.json"
output_folder = "texts"
output_file = os.path.join(output_folder, f"{js_file}_cycles.json")

os.makedirs(output_folder, exist_ok=True)

with open(input, "r", encoding="utf-8") as f:
    data = json.load(f)
    extracted_cycles = extract_fields_per_cycle(data)
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(extracted_cycles, out, ensure_ascii=False, indent=2)
