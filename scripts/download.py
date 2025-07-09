import yt_dlp
import os

def download_tiktok(post_id: str, video_url: str, output_dir: str = "downloads"):
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
        ydl.download([video_url])

post_meta = {
    "id": "7516123586508197142",
    "link": "https://www.tiktok.com/@zanno_tw/video/7516123586508197142"
}

download_tiktok(post_id=post_meta["id"], video_url=post_meta["link"])
