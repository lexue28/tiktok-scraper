import yt_dlp
import os
from datetime import datetime

LOG_FILE = "download_log.txt"

def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def download_tiktok(post_id: str, video_url: str, output_dir: str = "download/downloads"):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{post_id}.mp4")

    ydl_opts = {
        'outtmpl': output_path,
        'quiet': False,
        'noplaylist': True,
        'format': 'mp4',
        'cookiefile': "C:\\Users\\lexue\\OneDrive\\ComputerProjects\\MIT\\tiktok-scraper-master-3\\scripts\\cookies.txt",
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',  
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
            log(f"downloaded: {post_id}")
        except Exception as e:
            log(f"failed: {post_id}, {str(e)}")

def download_from_file(filepath="download/download_ids.txt"):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        url = line.strip()
        if not url:
            continue
        post_id = url.split("/video/")[1].split("?")[0]
        download_tiktok(post_id=post_id, video_url=url)

if __name__ == "__main__":
    download_from_file()
