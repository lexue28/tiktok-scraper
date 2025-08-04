import json
import csv
import os
import openai

client = openai.OpenAI(api_key="")

framework_prompt = """
Classify the following tiktok video descriptions as 'harmful' or 'not harmful' under this harmful content framework:
- Disordered Eating and Body Image
- Suicide and Self-Harm
- Dangerous Activity and Challenges
- Nudity and Body Exposure
- Sexually Suggestive Content
- Shocking and Graphic Content
- Hate Speech or Behavior
- Sexual and physical abuse
- Human Trafficking and Smuggling
- Gambling
- Alcohol, Tobacco, and Drugs
- Integrity and Authencity
- Harassment and Bullying

Reply in the format:
harmful/not harmful based on if the tiktok falls under one of these groups. Reasoning: <your brief reasoning>. The goal of this is to prevent minors from seeing harmful content.
"""

def classify_gpt(video_id, description, account):
    messages = [
        {"role": "system", "content": framework_prompt},
        {"role": "user", "content": description}
    ]
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=200,
        temperature=0
    )
    raw = resp.choices[0].message.content
    if raw.strip().lower().startswith("harmful"):
        harmful = "harmful"
        reasoning = raw.split("Reasoning:", 1)[-1].strip()
    elif raw.strip().lower().startswith("not harmful"):
        harmful = "not harmful"
        reasoning = raw.split("Reasoning:", 1)[-1].strip()
    else:
        harmful = "unclear"
        reasoning = raw.strip()
    return {
        "video_id": video_id,
        "link": f"https://www.tiktok.com/@temp/video/{video_id}",
        "account": account,
        "desc": description,
        "harmful": harmful,
        "reasoning": reasoning,
        "day": "Sunday"
    }

for i in ["a", "c"]:
    print("got in here")
    input = f"logs_{i}"
    with open(f"desc/sun/{input}_desc.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    output_folder = os.path.join("classify/sun")
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"classified_results_{i}.csv")

    # Load already classified video IDs
    existing_ids = set()
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_ids.add(row["video_id"])

    # Open CSV in append mode
    csvfile = open(output_path, "a", encoding="utf-8", newline="")
    writer = csv.DictWriter(csvfile, fieldnames=["video_id", "link", "account", "desc", "harmful", "reasoning", "day"])

    # Write header only if file is empty
    if os.stat(output_path).st_size == 0:
        writer.writeheader()

    for entry in data:
        dat = entry["data"]
        if dat and len(dat) > 0:
            video_id = dat[0]
        else:
            print("Warning: empty or malformed entry", dat)
            continue

        if video_id in existing_ids:
            continue  # skip already processed

        description = " ".join([part.strip() for part in dat[1:] if part.strip()])
        account = entry["folder"]
        result = classify_gpt(video_id, description, account)
        writer.writerow(result)

    csvfile.close()
