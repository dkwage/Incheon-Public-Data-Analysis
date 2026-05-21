import os
import re
import time
import json
import torch
import pandas as pd
from tqdm.auto import tqdm
from google import genai
from transformers import pipeline as hf_pipeline
from huggingface_hub import login


# ──────────────────────────────────────────────
# 0. 환경 설정
# ──────────────────────────────────────────────

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

# HuggingFace 로그인 (필요 시)
hf_token = os.getenv("HUGGINGFACE_TOKEN")
if hf_token:
    login(token=hf_token)

# Apple Silicon MPS 가속
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"[장치] {device} — MPS {'✓' if torch.backends.mps.is_available() else '✗'}")

# Gemini 클라이언트
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise RuntimeError("GEMINI_API_KEY 환경 변수가 필요합니다.")
client = genai.Client(api_key=gemini_api_key)

# ── 모델 선택 ──────────────────────────────────
GEMINI_MODEL   = "gemini-3.1-flash-lite"
GEMINI_RPM     = 15          # 분당 최대 요청 수
GEMINI_SLEEP   = 60 / GEMINI_RPM + 0.5   # ≈ 4.5초 — 안전 여유 포함
MAX_RETRY      = 3           # 429/503 발생 시 최대 재시도 횟수
# ──────────────────────────────────────────────

# KoELECTRA 감성 분석 모델 로드
print("[모델 로딩] KoELECTRA 감성 분석 모델 초기화 중...")
sentiment_pipe = hf_pipeline(
    "sentiment-analysis",
    model="Copycats/koelectra-base-v3-generalized-sentiment-analysis",
    device=device,
)
print("[모델 로딩] 완료\n")


# ──────────────────────────────────────────────
# 1. 데이터 로드
# ──────────────────────────────────────────────

def load_and_clean(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df = df.drop_duplicates(subset=["comment"]).dropna(subset=["comment"])
    df["comment"] = df["comment"].str.replace(r"\s+", " ", regex=True).str.strip()
    return df.reset_index(drop=True)


# ──────────────────────────────────────────────
# 2. Gemini 호출 (Rate Limit 자동 재시도 포함)
# ──────────────────────────────────────────────

def call_gemini_with_retry(comment: str) -> dict:
    """
    부정 댓글 1건을 Gemini에 전송해 민원 여부와 요지를 반환.
    429(Rate Limit) / 503(서버 과부하) 발생 시 에러 메시지의
    retryDelay 값을 파싱해 대기 후 자동 재시도.

    반환: {"is_complaint": bool, "summary": str | None, "error": str | None}
    """
    prompt = f"""
너는 지자체 SNS 민원 판별 전문가야. 다음 '부정적' 감정이 담긴 유튜브 댓글을 분석해줘.

판별 기준:
- is_complaint = true  → 구청의 조치·답변·개선이 필요한 민원/건의 (예: 시설 불편, 정책 반대, 행정 요청, 경품 미수령 문의 등)
- is_complaint = false → 단순 불평·욕설·감상·의문, 구청 액션이 필요 없는 것

출력 규칙:
- summary: 민원이면 "주제: 한 문장 요지" 형태로 작성, 아니면 null
- 반드시 아래 JSON 형식으로만 응답 (다른 텍스트 금지)

댓글: "{comment}"

{{"is_complaint": bool, "summary": "string or null"}}
"""
    for attempt in range(1, MAX_RETRY + 1):
        try:
            resp = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            data = json.loads(resp.text)
            return {
                "is_complaint": bool(data.get("is_complaint", False)),
                "summary": data.get("summary"),
                "error": None,
            }

        except Exception as e:
            err_str = str(e)
            # 429 또는 503 → retryDelay 파싱 후 대기
            if "429" in err_str or "503" in err_str:
                match = re.search(r"retryDelay['\"]?\s*:\s*['\"]?(\d+)", err_str)
                wait = int(match.group(1)) + 3 if match else 60
                print(f"  ⚠ [{attempt}/{MAX_RETRY}] Rate Limit / 서버 과부하 → {wait}초 대기 후 재시도...")
                time.sleep(wait)
            else:
                # 그 외 에러는 재시도 없이 반환
                return {"is_complaint": False, "summary": None, "error": err_str}

    return {"is_complaint": False, "summary": None, "error": "최대 재시도 초과"}


# ──────────────────────────────────────────────
# 3. 메인 파이프라인
# ──────────────────────────────────────────────

def run_pipeline(input_csv: str = "youtube_results.csv"):
    df = load_and_clean(input_csv)
    print(f"총 {len(df)}건 로드 완료\n")

    results = []
    gemini_call_count = 0   # Gemini 실제 호출 횟수 추적

    for _, row in tqdm(df.iterrows(), total=len(df), desc="댓글 분석"):
        comment = row["comment"]
        entry = {
            **row.to_dict(),
            "type":           "일반",
            "is_complaint":   False,
            "is_event":       False,
            "final_analysis": "N/A",
            "sentiment_label":"",
        }

        # ── Step 1: 이벤트 필터 ──────────────────
        EVENT_KEYWORDS = {"정답", "참여", "이벤트", "응모", "답"}
        if any(kw in comment for kw in EVENT_KEYWORDS):
            entry.update(
                is_event=True,
                type="이벤트 참여",
                sentiment_label="기능적 텍스트",
                final_analysis="이벤트 응모 댓글",
            )
            results.append(entry)
            continue

        # ── Step 2: KoELECTRA 감성 분석 ─────────
        is_negative = False
        try:
            local_res = sentiment_pipe(comment[:512])[0]
            is_negative = str(local_res["label"]) == "0"
            entry["sentiment_label"] = "부정" if is_negative else "긍정/중립"
        except Exception as e:
            entry["sentiment_label"] = "에러"
            entry["final_analysis"] = f"감성 분석 실패: {e}"
            results.append(entry)
            continue

        # ── Step 3: 부정 댓글만 Gemini 민원 판별 ─
        if is_negative:
            gemini_call_count += 1
            result = call_gemini_with_retry(comment)

            if result["error"]:
                entry["final_analysis"] = f"Gemini 분석 실패: {result['error']}"
            elif result["is_complaint"]:
                entry.update(
                    is_complaint=True,
                    type="민원",
                    final_analysis=result["summary"] or "(요지 미반환)",
                )
            else:
                entry.update(
                    type="일반(부정)",
                    final_analysis="단순 부정 의견",
                )

            # Rate Limit 방지 sleep (마지막 건 제외)
            time.sleep(GEMINI_SLEEP)

        else:
            entry["final_analysis"] = "일반 응원 및 의견"

        results.append(entry)

    # ── Step 4: 결과 집계 ────────────────────────
    final_df = pd.DataFrame(results)
    negative_df = final_df[final_df["sentiment_label"] == "부정"].copy()

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

    # ── Step 5: 저장 ─────────────────────────────
    final_df.to_csv("michuhol_analysis_raw.csv",        index=False, encoding="utf-8-sig")
    negative_df.to_csv("michuhol_negative_comments.csv", index=False, encoding="utf-8-sig")
    performance.to_csv("michuhol_performance_report.csv",              encoding="utf-8-sig")

    # ── 요약 출력 ────────────────────────────────
    complaint_df = final_df[final_df["is_complaint"]].copy()

    print(f"\n{'='*55}")
    print("  분석 완료 요약")
    print(f"{'='*55}")
    print(f"  총 데이터        : {len(final_df):>5}건")
    print(f"  이벤트 참여      : {int(final_df['is_event'].sum()):>5}건  (건너뜀)")
    print(f"  부정 댓글        : {len(negative_df):>5}건")
    print(f"  Gemini 호출      : {gemini_call_count:>5}건")
    print(f"  확정 민원        : {len(complaint_df):>5}건")
    print(f"{'='*55}")

    if len(complaint_df) > 0:
        print("\n[ 민원 목록 ]")
        for i, row in complaint_df.reset_index(drop=True).iterrows():
            print(f"  #{i+1:02d} [{row.get('title','')[:25]}]")
            print(f"       댓글  : {row['comment'][:80]}")
            print(f"       요지  : {row['final_analysis']}")
            print()
    else:
        print("\n  ※ 확정 민원 없음")

    print("저장 완료:")
    print("  - michuhol_analysis_raw.csv")
    print("  - michuhol_negative_comments.csv")
    print("  - michuhol_performance_report.csv")

    return final_df, negative_df, performance


# ──────────────────────────────────────────────
# 실행
# ──────────────────────────────────────────────
if __name__ == "__main__":
    run_pipeline("youtube_results.csv")