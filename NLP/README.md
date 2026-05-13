# NLP 댓글 분석 파이프라인

YouTube와 Instagram 댓글을 수집하고, 감성 분석과 민원 판별을 거쳐 결과 리포트를 만드는 파이썬 프로젝트

## 주요 기능

- `YT.csv`의 유튜브 영상 URL을 읽어 댓글을 수집합니다.
- `IG.csv`의 인스타그램 URL을 읽어 댓글을 수집합니다.
- 로컬 감성 분석 모델로 댓글의 긍정/부정을 분류합니다.
- 부정 댓글은 Gemini로 한 번 더 분석해 민원 여부를 판단합니다.
- 영상별 성과 리포트와 원본 분석 결과를 CSV로 저장합니다.

## 파일 구성

- `crawl_YT.py` - YouTube 댓글 수집 스크립트
- `crwal_IG.py` - Instagram 댓글 수집 스크립트
- `sentiment.py` - 댓글 감성 분석 및 민원 판별 스크립트
- `requirements.txt` - 필요한 Python 패키지 목록
- `YT.csv` - YouTube 수집 대상 목록
- `IG.csv` - Instagram 수집 대상 목록
- `youtube_results.csv` - YouTube 수집 결과 예시
- `michuhol_analysis_raw.csv` - 감성 분석 결과
- `michuhol_performance_report.csv` - 영상별 성과 리포트

## 동작 흐름

1. 수집 대상 URL을 CSV에 준비합니다.
2. `crawl_YT.py` 또는 `crwal_IG.py`로 댓글을 수집합니다.
3. `sentiment.py`로 수집된 댓글을 분석합니다.
4. 분석 결과와 성과 리포트를 CSV로 저장합니다.

## 설치

```bash
pip install -r requirements.txt
```

## API 키 분리 방법

저장소에는 키를 직접 쓰지 말고 환경 변수로 넣습니다.

```bash
export YOUTUBE_API_KEY="your-youtube-api-key"
export INSTA_USERNAME="your-instagram-id"
export INSTA_PASSWORD="your-instagram-password"
export HUGGINGFACE_TOKEN="your-huggingface-token"
export GEMINI_API_KEY="your-gemini-api-key"
```

터미널마다 다시 설정하기 번거로우면, 로컬 전용 `.env` 파일을 만들어도 됩니다. 이 프로젝트는 각 스크립트가 표준 라이브러리만으로 `.env`를 자동으로 읽습니다.

예시:

```env
YOUTUBE_API_KEY=your-youtube-api-key
INSTA_USERNAME=your-instagram-id
INSTA_PASSWORD=your-instagram-password
HUGGINGFACE_TOKEN=your-huggingface-token
GEMINI_API_KEY=your-gemini-api-key
```

`.env`는 git에 올리지 마세요.

## 실행 방법

### 1) YouTube 댓글 수집

```bash
python crawl_YT.py
```

입력 파일은 `YT.csv`, 출력 파일은 `youtube_results.csv`입니다.

### 2) Instagram 댓글 수집

```bash
python crwal_IG.py
```

입력 파일은 `IG.csv`를 우선 사용하고, 없으면 `target_links.csv`를 대신 사용합니다. 출력 파일은 `insta_results.csv`입니다.

### 3) 감성 분석 및 민원 판별

```bash
python sentiment.py
```

입력 파일은 `youtube_results.csv`, 출력 파일은 아래 두 개입니다.

- `michuhol_analysis_raw.csv`
- `michuhol_performance_report.csv`

## 필요한 외부 서비스

- YouTube Data API v3
- Hugging Face Hub
- Google Gemini API
