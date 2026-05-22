# NLP 댓글 분석 파이프라인

YouTube와 Instagram 댓글을 수집한 뒤, 로컬 감성 분석과 Gemini 기반 민원 판별을 수행하는 파이썬 프로젝트입니다. 현재 메인 분석 파이프라인은 `complaint_analysis.py`입니다.

## 주요 기능

- 댓글을 불러와 중복과 공백을 정리
- 이벤트 응모성 댓글을 먼저 필터링
- 로컬 KoELECTRA 모델로 댓글을 긍정/부정으로 분류
- 부정 댓글은 Google Gemini로 민원 여부(`is_complaint`), 민원 유형(`complaint_type`), 한 줄 요약(`summary`)을 판별
- 긍정/중립 댓글은 Kiwi 기반 키워드 추출 후 Gemini로 6개 유형으로 묶어 분류
- 댓글 전체 결과, 부정 댓글, 긍정 댓글, 영상별 성과 리포트, 워드클라우드를 저장

## 파일 구성

- `complaint_analysis.py` — 감성 분석, 민원 판별, 긍정 유형 분류, 워드클라우드 생성
- `crawl_YT.py` — YouTube 댓글 수집
- `crwal_IG.py` — Instagram 댓글 수집
- `requirements.txt` — 의존성 목록
- `YT.csv`, `IG.csv` — 수집 대상 목록
- `youtube_results.csv` — 분석 입력 파일 예시
- `michuhol_analysis_raw.csv` — 전체 분석 결과
- `michuhol_negative_comments.csv` — 부정 댓글만 모은 결과
- `michuhol_positive_comments.csv` — 긍정/중립 댓글만 모은 결과
- `michuhol_performance_report.csv` — 영상별 성과 리포트
- `michuhol_wordcloud_positive.png` — 긍정 댓글 워드클라우드
- `michuhol_wordcloud_negative.png` — 부정 댓글 워드클라우드

## 동작 흐름

1. `youtube_results.csv`를 입력으로 읽습니다.
2. 이벤트 키워드가 포함된 댓글은 별도로 표시하고 분석에서 제외합니다.
3. 나머지 댓글은 KoELECTRA 감성 분석으로 긍정/부정을 나눕니다.
4. 부정 댓글은 Gemini로 민원 여부와 민원 유형을 판별합니다.
5. 긍정/중립 댓글은 Kiwi로 키워드를 추출한 뒤 Gemini로 유형을 분류하고, 댓글 단위로 유형을 배정합니다.
6. 결과를 CSV와 PNG 파일로 저장합니다.

## 설치

```bash
python -m pip install -r requirements.txt
```

필요한 주요 패키지는 `pandas`, `torch`, `transformers`, `huggingface_hub`, `google-genai`, `kiwipiepy`, `wordcloud`, `matplotlib`, `tqdm`입니다.

## 환경 변수

`complaint_analysis.py`는 `GEMINI_API_KEY`가 필요합니다. `HUGGINGFACE_TOKEN`이 있으면 Hugging Face 로그인도 수행합니다.

예시:

```bash
export HUGGINGFACE_TOKEN="your-huggingface-token"
export GEMINI_API_KEY="your-gemini-api-key"
```

또는 프로젝트 루트에 `.env` 파일을 둘 수 있습니다.

```env
HUGGINGFACE_TOKEN=...
GEMINI_API_KEY=...
```

## 실행 예시

가상환경에서 실행하는 예:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python complaint_analysis.py
```

이미 `.venv`가 있으면 바로 실행할 수 있습니다.

## 출력 파일 요약

- `michuhol_analysis_raw.csv`: 전체 댓글의 원본 데이터와 분석 결과
- `michuhol_negative_comments.csv`: 부정으로 분류된 댓글
- `michuhol_positive_comments.csv`: 긍정/중립으로 분류된 댓글
- `michuhol_performance_report.csv`: 영상별 댓글 수, 이벤트 참여 수, 확정 민원 수, 비율
- `michuhol_wordcloud_positive.png`: 긍정 댓글 키워드 시각화
- `michuhol_wordcloud_negative.png`: 부정 댓글 키워드 시각화

## 주의사항

- 입력 파일 기본값은 `youtube_results.csv`입니다.
- Gemini 호출에는 rate limit 대응 재시도와 대기 로직이 포함되어 있습니다.
- Apple Silicon에서는 `torch`의 MPS 사용 가능 여부에 따라 장치가 자동 선택됩니다.
