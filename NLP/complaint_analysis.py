import os
import re
import time
import json
import torch
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
from kiwipiepy import Kiwi
from tqdm.auto import tqdm
from google import genai
from transformers import pipeline as hf_pipeline
from huggingface_hub import login

matplotlib.use("Agg")
plt.rcParams['font.family'] = 'Apple SD Gothic Neo'


# ══════════════════════════════════════════════
# 0. 환경 설정
# ══════════════════════════════════════════════

def load_local_env(env_path=".env"):
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_local_env()

hf_token = os.getenv("HUGGINGFACE_TOKEN")
if hf_token:
    login(token=hf_token)

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"[장치] {device} — MPS {'✓' if torch.backends.mps.is_available() else '✗'}")

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise RuntimeError("GEMINI_API_KEY 환경 변수가 필요합니다.")
client = genai.Client(api_key=gemini_api_key)

GEMINI_MODEL = "gemini-3.1-flash-lite"  # RPM 15, TPM 250K, RPD 500
GEMINI_RPM   = 15
GEMINI_SLEEP = 60 / GEMINI_RPM + 0.5   # ≈ 4.5초
MAX_RETRY    = 3

print("[모델 로딩] KoELECTRA 초기화 중...")
sentiment_pipe = hf_pipeline(
    "sentiment-analysis",
    model="Copycats/koelectra-base-v3-generalized-sentiment-analysis",
    device=device,
)
print("[모델 로딩] 완료\n")

kiwi = Kiwi()


# ══════════════════════════════════════════════
# 1. 데이터 로드
# ══════════════════════════════════════════════

def load_and_clean(file_path: str, yt_path: str = "YT.csv") -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df = df.drop_duplicates(subset=["comment"]).dropna(subset=["comment"])
    df["comment"] = df["comment"].str.replace(r"\s+", " ", regex=True).str.strip()
    
    if os.path.exists(yt_path):
        yt_df = pd.read_csv(yt_path)
        if 'title' in yt_df.columns and 'topic' in yt_df.columns and 'content' in yt_df.columns:
            df = pd.merge(df, yt_df[['title', 'topic', 'content']], on='title', how='left')
            
    return df.reset_index(drop=True)


# ══════════════════════════════════════════════
# 2. 이벤트 필터 (키워드)
# ══════════════════════════════════════════════

EVENT_KEYWORDS = {"정답", "응모", "참여합니다", "신청합니다", "이벤트", "행사", "답", "1번", "2번", "3번", "4번", "5번"}

def check_event(comment: str) -> bool:
    return any(kw in comment for kw in EVENT_KEYWORDS)


# ══════════════════════════════════════════════
# 3. Gemini 공통 호출 래퍼
# ══════════════════════════════════════════════

def call_gemini(prompt: str) -> dict | None:
    for attempt in range(1, MAX_RETRY + 1):
        try:
            resp = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            return json.loads(resp.text)
        except Exception as e:
            err = str(e)
            if "429" in err or "503" in err:
                match = re.search(r"retryDelay['\"]?\s*:\s*['\"]?(\d+)", err)
                wait = int(match.group(1)) + 3 if match else 60
                print(f"  ⚠ [{attempt}/{MAX_RETRY}] Rate Limit → {wait}초 대기...")
                time.sleep(wait)
            else:
                print(f"  ✗ Gemini 에러: {err[:80]}")
                return None
    return None


# ══════════════════════════════════════════════
# 4-A. 부정 댓글 → 민원 판별 (1건씩)
# ══════════════════════════════════════════════

def analyze_negative(comment: str) -> dict:
    prompt = f"""
너는 지자체 SNS 민원 판별 전문가야. 아래 '부정적' 감정의 유튜브 댓글을 분석해줘.

[민원 판별]
- is_complaint = true  → 구청의 조치·답변·개선이 필요한 민원/건의
- is_complaint = false → 단순 욕설·불평·감상으로 구청 액션 불필요

[민원 유형] (is_complaint=true일 때만)
complaint_type 값: "시설·환경", "교통·도로", "행정·서비스", "정책·사업", "이벤트·행사", "기타"

[출력 규칙]
- summary: 민원이면 "주제: 한 문장 요지", 아니면 null
- 반드시 아래 JSON 형식으로만 응답

댓글: "{comment}"

{{"is_complaint": bool, "complaint_type": "string or null", "summary": "string or null"}}
"""
    result = call_gemini(prompt)
    time.sleep(GEMINI_SLEEP)
    if result is None:
        return {"is_complaint": False, "complaint_type": None, "summary": None, "error": "Gemini 호출 실패"}
    return {
        "is_complaint":   bool(result.get("is_complaint", False)),
        "complaint_type": result.get("complaint_type"),
        "summary":        result.get("summary"),
        "error":          None,
    }


# ══════════════════════════════════════════════
# 4-B. 긍정 댓글 → 키워드 추출 → Gemini 1회 유형 분류
# ══════════════════════════════════════════════

STOPWORDS = {
    "이", "가", "을", "를", "은", "는", "의", "에", "에서", "도", "로", "으로",
    "와", "과", "이나", "나", "하다", "있다", "없다", "하고", "그리고", "하지만",
    "그", "저", "것", "수", "더", "이런", "저런", "좀", "진짜", "정말", "너무",
    "제", "게", "거", "다", "네", "요", "해", "할", "한", "합", "했", "히",
    "ㅋ", "ㅎ", "ㅠ", "ㅜ", "ㄷ", "ㄱ", "ㅇ", "ㅅ", "미추홀구", "미추홀", "구청",
}

# 긍정 유형 우선순위 (앞쪽이 높음 — 댓글 분배 시 먼저 매칭된 유형으로 확정)
POSITIVE_TYPE_PRIORITY = [
    "정보요청",
    "제안·아이디어",
    "칭찬·감사",
    "공감·감동",
    "응원·격려",
    "일상·감상",
]

def extract_top_keywords(texts: list[str], top_n: int = 80) -> list[str]:
    """Kiwi로 명사·형용사 추출 후 상위 N개 반환."""
    counter: Counter = Counter()
    for text in texts:
        for tok in kiwi.tokenize(text):
            word = tok.form
            if tok.tag in ("NNG", "NNP", "VA") and len(word) >= 2:
                if word not in STOPWORDS:
                    counter[word] += 1
    return [word for word, _ in counter.most_common(top_n)]


def classify_positive_keywords(keywords: list[str]) -> dict[str, list[str]]:
    """
    키워드 목록을 Gemini에 한 번 보내서 유형별로 분류.
    반환: {"정보요청": ["언제", "어디서", ...], "응원·격려": [...], ...}
    """
    kw_str = ", ".join(keywords)
    type_desc = "\n".join([
        '- "정보요청": 장소·시간·방법 등 정보를 요구하는 맥락의 키워드',
        '- "제안·아이디어": 개선·추가·건의 맥락의 키워드',
        '- "칭찬·감사": 좋다·감사·최고 등 칭찬 맥락의 키워드',
        '- "공감·감동": 감동·공감·추억 등 정서적 반응 키워드',
        '- "응원·격려": 화이팅·응원·기대 등 응원 맥락의 키워드',
        '- "일상·감상": 특정 유형에 속하지 않는 일반 감상 키워드',
    ])
    prompt = f"""
아래 키워드들을 유튜브 댓글 맥락에서 아래 6가지 유형으로 분류해줘.
하나의 키워드는 가장 적합한 유형 1개에만 배정해.
모든 키워드를 빠짐없이 배정해야 해.

[유형 설명]
{type_desc}

[키워드 목록]
{kw_str}

반드시 아래 JSON 형식으로만 응답해. 각 유형의 값은 해당 키워드 배열이야:
{{
  "정보요청": [],
  "제안·아이디어": [],
  "칭찬·감사": [],
  "공감·감동": [],
  "응원·격려": [],
  "일상·감상": []
}}
"""
    result = call_gemini(prompt)
    time.sleep(GEMINI_SLEEP)
    if result is None:
        # 실패 시 모두 일상·감상으로
        return {"일상·감상": keywords, **{t: [] for t in POSITIVE_TYPE_PRIORITY if t != "일상·감상"}}
    # 반환값 정제: 모든 유형 키 보장
    classified = {t: result.get(t, []) for t in POSITIVE_TYPE_PRIORITY}
    return classified


def assign_positive_type(comment: str, type_keywords: dict[str, list[str]]) -> str:
    """
    우선순위 순서대로 댓글에 키워드가 포함되어 있는지 확인,
    첫 번째 매칭 유형을 반환. 없으면 '일상·감상'.
    """
    for ptype in POSITIVE_TYPE_PRIORITY:
        for kw in type_keywords.get(ptype, []):
            if kw in comment:
                return ptype
    return "일상·감상"


# ══════════════════════════════════════════════
# 5. 워드클라우드
# ══════════════════════════════════════════════

def extract_keyword_freq(texts: list[str]) -> dict[str, int]:
    counter: Counter = Counter()
    for text in texts:
        for tok in kiwi.tokenize(text):
            word = tok.form
            if tok.tag in ("NNG", "NNP", "VV", "VA") and len(word) >= 2:
                if word not in STOPWORDS:
                    counter[word] += 1
    return dict(counter)


def save_wordcloud(freq: dict, title: str, save_path: str, colormap: str):
    if not freq:
        print(f"  → 키워드 없음, 워드클라우드 생략: {save_path}")
        return
    wc = WordCloud(
        font_path="/System/Library/Fonts/Supplemental/AppleSDGothicNeo.ttc",
        width=1600,
        height=800,
        background_color="white",
        colormap=colormap,
        max_words=100,
        prefer_horizontal=0.85,
    ).generate_from_frequencies(freq)
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(title, fontsize=18, pad=14)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  → 워드클라우드 저장: {save_path}")


# ══════════════════════════════════════════════
# 6. 메인 파이프라인
# ══════════════════════════════════════════════

def run_pipeline(input_csv: str = "youtube_results.csv"):
    df = load_and_clean(input_csv)
    print(f"총 {len(df)}건 로드 완료\n")

    results       = []
    gemini_call_count = 0

    # ── Step 1·2: 이벤트 필터 + 감성 분석 ────────
    # 부정/긍정을 먼저 나눠두고 Gemini는 후처리
    neg_indices = []   # 부정 댓글 인덱스 (results 기준)
    pos_indices = []   # 긍정 댓글 인덱스

    for _, row in tqdm(df.iterrows(), total=len(df), desc="[Step 1·2] 감성 분석"):
        comment = str(row.get("comment", ""))
        entry = {
            **row.to_dict(),
            "type":            "일반",
            "is_complaint":    False,
            "is_event":        False,
            "sentiment_label": "",
            "positive_type":   None,
            "complaint_type":  None,
            "final_analysis":  "N/A",
        }

        # 이벤트 필터
        if check_event(comment):
            entry.update(
                is_event=True,
                type="이벤트 참여",
                sentiment_label="기능적 텍스트",
                final_analysis="이벤트 응모 댓글",
            )
            results.append(entry)
            continue

        # KoELECTRA 감성 분석
        try:
            local_res = sentiment_pipe(comment[:512])[0]
            is_negative = str(local_res["label"]) == "0"
            entry["sentiment_label"] = "부정" if is_negative else "긍정/중립"
        except Exception as e:
            entry["sentiment_label"] = "에러"
            entry["final_analysis"]  = f"감성 분석 실패: {e}"
            results.append(entry)
            continue

        idx = len(results)
        results.append(entry)

        if is_negative:
            neg_indices.append(idx)
        else:
            pos_indices.append(idx)

    print(f"\n  부정 댓글: {len(neg_indices)}건 / 긍정 댓글: {len(pos_indices)}건\n")

    # ── Step 3-A: 부정 → Gemini 민원 판별 ────────
    for idx in tqdm(neg_indices, desc="[Step 3-A] 부정 민원 판별"):
        comment = results[idx]["comment"]
        gemini_call_count += 1
        neg = analyze_negative(comment)
        results[idx]["complaint_type"] = neg["complaint_type"]
        if neg["error"]:
            results[idx]["final_analysis"] = f"Gemini 분석 실패: {neg['error']}"
        elif neg["is_complaint"]:
            results[idx].update(
                is_complaint=True,
                type="민원",
                final_analysis=neg["summary"] or "(요지 미반환)",
            )
        else:
            results[idx].update(type="일반(부정)", final_analysis="단순 부정 의견")

    # ── Step 3-B: 긍정 → 키워드 추출 → Gemini 1회 → 댓글 분배 ──
    if pos_indices:
        pos_comments = [results[i]["comment"] for i in pos_indices]

        print("\n[Step 3-B] 긍정 키워드 추출 중...")
        top_keywords = extract_top_keywords(pos_comments, top_n=80)
        print(f"  상위 키워드 {len(top_keywords)}개 추출 완료")

        print("[Step 3-B] Gemini 유형 분류 (1회 호출)...")
        gemini_call_count += 1
        type_keywords = classify_positive_keywords(top_keywords)
        print("  유형별 키워드 분류 완료:")
        for ptype, kws in type_keywords.items():
            print(f"    {ptype:<14}: {', '.join(kws[:5])}{'...' if len(kws) > 5 else ''}")

        print("\n[Step 3-B] 댓글 → 유형 매칭 중...")
        for idx in pos_indices:
            comment = results[idx]["comment"]
            ptype   = assign_positive_type(comment, type_keywords)
            results[idx]["positive_type"]  = ptype
            results[idx]["type"]           = ptype
            results[idx]["final_analysis"] = ptype

    # ── Step 4: 결과 집계 ─────────────────────────
    final_df    = pd.DataFrame(results)
    negative_df = final_df[final_df["sentiment_label"] == "부정"].copy()
    positive_df = final_df[final_df["sentiment_label"] == "긍정/중립"].copy()

    # 교차 집계: topic x content x positive_type
    cross_tab = pd.DataFrame()
    if "topic" in positive_df.columns and "content" in positive_df.columns and "positive_type" in positive_df.columns:
        cross_tab = pd.crosstab(
            [positive_df["topic"], positive_df["content"]],
            positive_df["positive_type"],
            margins=True, margins_name="총계"
        )
        cross_tab.to_csv("michuhol_positive_crosstab.csv", encoding="utf-8-sig")

    performance = (
        final_df.groupby("title")
        .agg(
            총댓글수=("comment", "count"),
            이벤트참여수=("is_event", "sum"),
            확정민원수=("is_complaint", "sum"),
            긍정반응수=("sentiment_label", lambda x: (x == "긍정/중립").sum()),
        )
    )
    denom = (performance["총댓글수"] - performance["이벤트참여수"]).replace(0, float("nan"))
    performance["민원발생률(%)"] = (performance["확정민원수"] / performance["총댓글수"] * 100).round(2)
    performance["순수긍정률(%)"] = (performance["긍정반응수"] / denom * 100).fillna(0).round(2)

    # ── Step 5: 워드클라우드 ──────────────────────
    print("\n[Step 5] 워드클라우드 생성 중...")
    pos_freq = extract_keyword_freq(positive_df["comment"].tolist())
    neg_freq = extract_keyword_freq(negative_df["comment"].tolist())
    save_wordcloud(pos_freq, "긍정 댓글 키워드", "michuhol_wordcloud_positive.png", colormap="Blues")
    save_wordcloud(neg_freq, "부정 댓글 키워드", "michuhol_wordcloud_negative.png", colormap="Reds")

    # ── Step 6: 저장 ──────────────────────────────
    final_df.to_csv("michuhol_analysis_raw.csv",         index=False, encoding="utf-8-sig")
    negative_df.to_csv("michuhol_negative_comments.csv", index=False, encoding="utf-8-sig")
    positive_df.to_csv("michuhol_positive_comments.csv", index=False, encoding="utf-8-sig")
    performance.to_csv("michuhol_performance_report.csv",               encoding="utf-8-sig")

    # ── 요약 출력 ─────────────────────────────────
    complaint_df    = final_df[final_df["is_complaint"]].copy()
    pos_type_counts = positive_df["positive_type"].value_counts()

    print(f"\n{'='*60}")
    print("  분석 완료 요약")
    print(f"{'='*60}")
    print(f"  총 데이터        : {len(final_df):>6}건")
    print(f"  이벤트 참여      : {int(final_df['is_event'].sum()):>6}건  (건너뜀)")
    print(f"  부정 댓글        : {len(negative_df):>6}건")
    print(f"  긍정/중립 댓글   : {len(positive_df):>6}건")
    print(f"  Gemini 총 호출   : {gemini_call_count:>6}건  (부정 {len(neg_indices)}회 + 긍정 1회)")
    print(f"  확정 민원        : {len(complaint_df):>6}건")
    print(f"{'='*60}")

    if not pos_type_counts.empty:
        print("\n[ 긍정 댓글 유형 분포 ]")
        for ptype, cnt in pos_type_counts.items():
            bar = "█" * int(cnt / max(pos_type_counts) * 20)
            print(f"  {ptype:<14} {cnt:>4}건  {bar}")

    if not cross_tab.empty:
        print("\n[ 긍정 댓글 교차 집계 (Topic x Content x Positive_Type) ]")
        print(cross_tab)

    if len(complaint_df) > 0:
        print("\n[ 민원 목록 ]")
        for i, r in complaint_df.reset_index(drop=True).iterrows():
            print(f"  #{i+1:02d} [{r.get('title','')[:30]}]")
            print(f"       유형  : {r.get('complaint_type', '–')}")
            print(f"       댓글  : {r['comment'][:80]}")
            print(f"       요지  : {r['final_analysis']}")
            print()
    else:
        print("\n  ※ 확정 민원 없음")

    print("\n저장 완료:")
    for f in [
        "michuhol_analysis_raw.csv",
        "michuhol_negative_comments.csv",
        "michuhol_positive_comments.csv",
        "michuhol_positive_crosstab.csv",
        "michuhol_performance_report.csv",
        "michuhol_wordcloud_positive.png",
        "michuhol_wordcloud_negative.png",
    ]:
        print(f"  - {f}")

    return final_df, negative_df, positive_df, performance


# ══════════════════════════════════════════════
# 실행
# ══════════════════════════════════════════════
if __name__ == "__main__":
    run_pipeline("youtube_results.csv")