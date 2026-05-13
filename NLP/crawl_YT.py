import os
import time
import random
import polars as pl
from urllib.parse import urlparse, parse_qs
from langdetect import detect, LangDetectException
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def load_local_env(env_path=".env"):
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_local_env()

# --- 설정 ---
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY 환경 변수가 필요합니다.")
INPUT_FILE = "YT.csv"
OUTPUT_CSV = "youtube_results1.csv"
MAX_YT_COMMENTS = 500  # 영상 하나당 최대 수집 댓글 수
SAVE_EVERY = 5

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def random_sleep(min_sec=0.2, max_sec=0.5):
    time.sleep(random.uniform(min_sec, max_sec))

def safe_detect_language(text):
    try: return detect(text)
    except: return "unknown"

def extract_youtube_id(url):
    try:
        if "shorts/" in url: return url.split("shorts/")[1].split("?")[0]
        elif "youtu.be" in url: return urlparse(url).path[1:]
        elif "youtube.com" in url: return parse_qs(urlparse(url).query).get("v", [None])[0]
    except: return None

def get_youtube_comments(video_id, title, url):
    results = []
    try:
        next_page_token = None
        while True:
            request = youtube.commentThreads().list(
                part="snippet,replies", videoId=video_id, maxResults=100,
                pageToken=next_page_token, textFormat="plainText"
            )
            response = request.execute()
            for item in response["items"]:
                top = item["snippet"]["topLevelComment"]["snippet"]
                txt = top.get("textDisplay", "")
                results.append({
                    "platform": "YouTube", "title": title, "url": url, "video_id": video_id,
                    "author": top.get("authorDisplayName"), "comment": txt,
                    "language": safe_detect_language(txt), "likes": top.get("likeCount"),
                    "published_at": top.get("publishedAt"), "type": "top_comment"
                })
                if "replies" in item:
                    for reply in item["replies"]["comments"]:
                        r = reply["snippet"]
                        r_txt = r.get("textDisplay", "")
                        results.append({
                            "platform": "YouTube", "title": title, "url": url, "video_id": video_id,
                            "author": r.get("authorDisplayName"), "comment": r_txt,
                            "language": safe_detect_language(r_txt), "likes": r.get("likeCount"),
                            "published_at": r.get("publishedAt"), "type": "reply"
                        })
            if len(results) >= MAX_YT_COMMENTS: break
            next_page_token = response.get("nextPageToken")
            if not next_page_token: break
            random_sleep()
    except Exception as e: print(f"⚠️ YouTube Error ({title}): {e}")
    return results

def save_results(results):
    if not results: return
    df = pl.DataFrame(results).unique().filter(pl.col("comment").str.len_chars() > 0)
    df.to_pandas().to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"💾 YouTube 저장 완료: {len(df)} rows")

def main():
    if not os.path.exists(INPUT_FILE): return
    df = pl.read_csv(INPUT_FILE)
    all_results = []
    
    # 유튜브 링크만 필터링
    yt_df = df.filter(pl.col("url").str.contains("youtube|youtu.be"))
    
    for idx, row in enumerate(yt_df.iter_rows(named=True)):
        v_id = extract_youtube_id(row["url"])
        if not v_id: continue
        print(f"[{idx+1}/{len(yt_df)}] 📺 YouTube: {row['title']}")
        all_results.extend(get_youtube_comments(v_id, row["title"], row["url"]))
        if (idx + 1) % SAVE_EVERY == 0: save_results(all_results)
        
    save_results(all_results)

if __name__ == "__main__":
    main()