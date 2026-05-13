import torch
import pandas as pd
import json
import os
from google import genai
from transformers import pipeline
from tqdm.auto import tqdm
from huggingface_hub import login


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

hf_token = os.getenv("HUGGINGFACE_TOKEN")
if hf_token:
    login(token=hf_token)

# 1. 환경 설정 및 apple silicon 가속(MPS) 확인
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"사용 장치: {device} - MPS 가속 {'사용 가능' if torch.backends.mps.is_available() else '사용 불가'}")

# Gemini SDK 설정
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise RuntimeError("GEMINI_API_KEY 환경 변수가 필요합니다.")
client = genai.Client(api_key=gemini_api_key)

# 로컬 감성 분석 모델 (Copycats KoELECTRA)
# 레이블 정보: 0 -> 부정, 1 -> 긍정
sentiment_model = "Copycats/koelectra-base-v3-generalized-sentiment-analysis"
sentiment_pipe = pipeline("sentiment-analysis", model=sentiment_model, device=device)

# 2. 데이터 로드 및 전처리 (Preprocessing)
def load_and_clean(file_path):
    df = pd.read_csv(file_path)
    # 중복 제거 및 결측치 처리
    df = df.drop_duplicates(subset=['comment']).dropna(subset=['comment'])
    # 공백 정규화 및 양끝 공백 제거 (Pandas Accessor 주의)
    df['comment'] = df['comment'].str.replace(r'\s+', ' ', regex=True).str.strip()
    return df

# 3. 메인 파이프라인 실행
df = load_and_clean('youtube_results.csv')
results = []

print(f"총 {len(df)}건의 데이터 분석")

for _, row in tqdm(df.iterrows(), total=len(df)):
    comment = row['comment']
    # 기본 구조 설정
    res_entry = {
        **row.to_dict(), 
        'type': '일반', 
        'is_complaint': False, 
        'is_event': False, 
        'final_analysis': 'N/A'
    }
    
    # [Step 1] 이벤트 필터링 
    # "정답" 혹은 "참여" 키워드 포함 시 이벤트로 분류
    if "정답" in comment or "참여" in comment:
        res_entry['is_event'] = True
        res_entry['type'] = '이벤트 참여'
        res_entry['sentiment_label'] = '기능적 텍스트'
        res_entry['final_analysis'] = '이벤트 응모 댓글'
        is_negative = False
        
    else:
        # [Step 2] 로컬 BERT 감성 분석 (이벤트가 아닐 때만)
        try:
            # 512자 초과 시 절단 처리
            local_res = sentiment_pipe(comment[:512])[0]
            is_negative = str(local_res['label']) == '0'
            res_entry['sentiment_label'] = '부정' if is_negative else '긍정/중립'
        except:
            is_negative = False
            res_entry['sentiment_label'] = '에러'

    # [Step 3] 부정 댓글만 Gemini에게 전송 (민원 여부 최종 확정)
    if is_negative:
        try:
            prompt = f"""
            너는 지자체 민원 판별 전문가야. 다음 '부정적'인 감정이 담긴 댓글을 분석해줘.
            1. is_complaint: 구청의 조치나 답변이 필요한 '민원/건의'라면 true, 단순 욕설이나 불평이면 false
            2. summary: 민원일 경우 핵심 내용을 1문장으로 요약 (아니면 null)
            
            댓글: "{comment}"
            
            응답은 반드시 다음 JSON 형식으로만 해:
            {{"is_complaint": bool, "summary": "string"}}
            """
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            analysis = json.loads(response.text)
            
            res_entry['is_complaint'] = analysis.get('is_complaint', False)
            if res_entry['is_complaint']:
                res_entry['type'] = '민원'
                res_entry['final_analysis'] = analysis.get('summary')
            else:
                res_entry['type'] = '일반(부정)'
                res_entry['final_analysis'] = "단순 부정 의견"
        except:
            res_entry['final_analysis'] = "Gemini 분석 실패"
            
    elif not res_entry['is_event']:
        res_entry['final_analysis'] = "일반 응원 및 의견"

    results.append(res_entry)

# 4. 결과 정리 및 성과 분석 (Performance Analysis)
final_df = pd.DataFrame(results)

# 영상 제목별 성과 리포트 생성
performance = final_df.groupby('title').agg({
    'comment': 'count',
    'is_event': 'sum',
    'is_complaint': 'sum',
    'sentiment_label': lambda x: (x == '긍정/중립').sum()
}).rename(columns={
    'comment': '총 댓글 수',
    'is_event': '이벤트 참여 수',
    'is_complaint': '확정 민원 수',
    'sentiment_label': '긍정적 반응 수'
})

# 성과 지표 계산
performance['민원 발생률(%)'] = (performance['확정 민원 수'] / performance['총 댓글 수'] * 100).round(2)
performance['순수 긍정률(%)'] = (performance['긍정적 반응 수'] / (performance['총 댓글 수'] - performance['이벤트 참여 수']) * 100).round(2)

# 5. 저장 및 종료
final_df.to_csv('michuhol_analysis_raw.csv', index=False, encoding='utf-8-sig')
performance.to_csv('michuhol_performance_report.csv', encoding='utf-8-sig')

print(f"\n분석 완료")
print(f"- 총 데이터: {len(final_df)}건")
print(f"- 이벤트 참여: {final_df['is_event'].sum()}건")
print(f"- 확정 민원: {final_df['is_complaint'].sum()}건")
print(f"- 'michuhol_performance_report.csv' 저장")