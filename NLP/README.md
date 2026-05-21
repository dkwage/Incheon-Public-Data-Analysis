# NLP 댓글 분석 파이프라인

YouTube와 Instagram 댓글을 수집해 감성 분석(로컬 모델)과 Gemini 기반 민원 판별을 수행하는 파이썬 프로젝트입니다. 이 리포지토리의 현재 메인 파이프라인은 `complaint_analysis.py`입니다.

## 주요 기능

- 댓글 수집 스크립트로 데이터를 수집
- 로컬 KoELECTRA 모델로 감성(긍정/부정) 분류
- 부정 댓글은 Google Gemini에 전송해 민원 여부(`is_complaint`)와 한 줄 요약(`summary`)을 획득
- 분석 결과와 영상별 성과 리포트를 CSV로 저장

## 파일 구성 (중요)

- `crawl_YT.py` — YouTube 댓글 수집
- `crwal_IG.py` — Instagram 댓글 수집
- `complaint_analysis.py` — 감성 분석 + Gemini 민원 판별(메인 파이프라인)
- `requirements.txt` — 필요한 패키지
- `YT.csv`, `IG.csv` — 수집 대상 목록
- `youtube_results.csv` — 수집된 YouTube 댓글(입력)
- `michuhol_analysis_raw.csv` — 파이프라인 전체 분석 결과 (출력)
- `michuhol_negative_comments.csv` — 부정 댓글만 추출한 파일 (출력)
- `michuhol_performance_report.csv` — 영상별 성과 리포트 (출력)

추가 참고 파일/폴더:

- `.env` — 환경변수(로컬 테스트용, git에 포함하지 마세요)
- `.venv/` — 가상환경(로컬)
- `README.md` — 이 파일
- `requirements.txt` — 설치 의존성
- `youtube_results.csv`, `YT.csv`, `IG.csv` — 샘플 데이터 및 입력 목록

## 동작 흐름

1. `YT.csv` 또는 `IG.csv`에 수집할 대상 URL을 준비합니다.
2. `crawl_YT.py` 또는 `crwal_IG.py`로 댓글을 수집합니다 (`youtube_results.csv` 등).
3. `complaint_analysis.py`를 실행해 감성 분석과 Gemini 민원 판별을 수행합니다.
4. 결과는 `michuhol_analysis_raw.csv`, `michuhol_negative_comments.csv`, `michuhol_performance_report.csv`에 저장됩니다.

## 설치

```bash
python -m pip install -r requirements.txt
```

필요한 추가 패키지(예): `google-genai` 또는 `google-generativeai` (Gemini SDK), `transformers`, `torch`, `huggingface_hub`, `pandas`, `tqdm` 등.

## 환경 변수

환경 변수로 API 키를 설정하세요. 예:

```bash
export YOUTUBE_API_KEY="your-youtube-api-key"
export HUGGINGFACE_TOKEN="your-huggingface-token"
export GEMINI_API_KEY="your-gemini-api-key"
```

또는 프로젝트 루트에 `.env` 파일을 만들어 다음처럼 정의할 수 있습니다 (`.env`는 커밋하지 마세요):

```env
YOUTUBE_API_KEY=...
HUGGINGFACE_TOKEN=...
GEMINI_API_KEY=...
```

## 실행 예시

가상환경에서 실행하는 예:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
.venv/bin/python complaint_analysis.py
```

또는 시스템 파이썬에서 직접:

```bash
python complaint_analysis.py
```

## 출력 파일 요약

- `michuhol_analysis_raw.csv`: 전체 댓글에 대한 분석 결과(감성, 민원 여부, 요약 등)
- `michuhol_negative_comments.csv`: 부정으로 분류된 댓글만 필터링한 파일
- `michuhol_performance_report.csv`: 영상별 통계 및 지표

## 주의사항

- `complaint_analysis.py`는 `GEMINI_API_KEY` 환경 변수가 필요합니다.
- Gemini 호출에는 rate limit과 재시도 로직이 포함되어 있으나, 대량 호출 시 비용과 속도를 고려하세요.
- 모델 로딩 시 `torch`의 MPS(Apple Silicon) 사용 여부에 따라 장치가 결정됩니다.

## 현재 디렉토리(참고)

다음 파일들이 작업 폴더에 존재합니다:

- `.env`
- `.gitignore`
- `.venv/`
- `IG.csv`
- `YT.csv`
- `complaint_analysis.py`
- `crawl_YT.py`
- `crwal_IG.py`
- `michuhol_analysis_raw.csv`
- `michuhol_negative_comments.csv`
- `michuhol_performance_report.csv`
- `requirements.txt`
- `youtube_results.csv`
