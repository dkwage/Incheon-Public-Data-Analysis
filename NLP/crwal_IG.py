import os
import re
import time
import random
import polars as pl
from langdetect import detect, LangDetectException
from instagrapi import Client


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
INSTA_USERNAME = os.getenv("INSTA_USERNAME")
INSTA_PASSWORD = os.getenv("INSTA_PASSWORD")
if not INSTA_USERNAME or not INSTA_PASSWORD:
    raise RuntimeError("INSTA_USERNAME, INSTA_PASSWORD 환경 변수가 필요합니다.")
INPUT_FILE = "IG.csv"
LEGACY_INPUT_FILE = "target_links.csv"
OUTPUT_CSV = "insta_results.csv"
SESSION_FILE = "insta_session.json"
MAX_INSTA_COMMENTS = 30
SAVE_EVERY = 3 # 인스타는 더 자주 저장하는 것이 안전

cl = Client()

def insta_login():
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.get_timeline_feed()
            print("기존 세션 로그인 성공")
            return
        except: print("세션 만료됨")
    cl.login(INSTA_USERNAME, INSTA_PASSWORD)
    cl.dump_settings(SESSION_FILE)
    print("새 로그인 성공")

def safe_detect_language(text):
    try: return detect(text)
    except: return "unknown"

def extract_instagram_shortcode(url):
    match = re.search(r"/(?:p|reels|reel)/([^/?#&]+)", url)
    return match.group(1) if match else None

def get_instagram_comments(url, title):
    results = []
    try:
        shortcode = extract_instagram_shortcode(url)
        if not shortcode: return results
        
        media_pk = cl.media_pk_from_code(shortcode)
        comments = cl.media_comments(media_pk, amount=MAX_INSTA_COMMENTS)
        
        for c in comments:
            results.append({
                "platform": "Instagram", "title": title, "url": url, "shortcode": shortcode,
                "author": c.user.username, "comment": c.text,
                "language": safe_detect_language(c.text), "likes": c.like_count,
                "published_at": str(c.created_at), "type": "comment"
            })
        print(f"   ㄴ {len(results)}개 수집 완료")
        time.sleep(random.uniform(15, 30)) # 인스타 보안
    except Exception as e: print(f"Instagram Error ({title}): {e}")
    return results

def save_results(results):
    if not results: return
    df = pl.DataFrame(results).unique().filter(pl.col("comment").str.len_chars() > 0)
    df.to_pandas().to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Instagram 저장 완료: {len(df)} rows")

def main():
    insta_login()
    input_file = INPUT_FILE if os.path.exists(INPUT_FILE) else LEGACY_INPUT_FILE
    if not os.path.exists(input_file): return
    df = pl.read_csv(input_file)
    
    # 인스타그램 링크만 필터링
    insta_df = df.filter(pl.col("url").str.contains("instagram"))
    all_results = []

    for idx, row in enumerate(insta_df.iter_rows(named=True)):
        print(f"[{idx+1}/{len(insta_df)}] 📸 Instagram: {row['title']}")
        all_results.extend(get_instagram_comments(row["url"], row["title"]))
        if (idx + 1) % SAVE_EVERY == 0: save_results(all_results)
        
    save_results(all_results)

if __name__ == "__main__":
    main()