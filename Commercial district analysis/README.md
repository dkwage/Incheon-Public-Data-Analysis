# 미추홀구 상권 활성화 분석

인하대 후문 상권을 대상으로 점포·주민인구·버스 이용·학사일정을 분석하는 Python 프로젝트입니다.
사용자가 설정한 경계 안의 업종 구성과 주변 여건을 분석하고, 유동·소비 자료와 연결할 분석 계획을 정리합니다.

## 주요 파일

- `meeting_20260916_inha.ipynb`: 진행 현황, 시각화, 데이터 명세와 공개 샘플.
- `briefing_eda_20260909.ipynb`: 후보 상권 탐색 분석.
- `real_analysis.ipynb`: 공개자료 정제 및 기초 분석.
- `inha_synthetic_card_demo.ipynb`: 합성 카드 데이터 분석 예시. 실제 매출을 의미하지 않습니다.
- `collect_real_data.py`: 공개 API 자료 수집.
- `analyze_inha_boundary.py`: 사용자 경계 기반 점포 분석.
- `prepare_inha_calendar.py`: 학사일정 분석 변수 생성.
- `data/inha_boundary.geojson`: 사용자 지정 조사 경계.
- `docs/`: 조사·분석 계획과 자료 확보 안내.

## 실행 환경

Python 가상환경에서 `pip install -r requirements.txt`로 패키지를 설치합니다.
노트북 실행과 생성 스크립트에는 Jupyter/IPython 환경도 필요합니다.
공공데이터포털 API 키는 `DATA_GO_KR_SERVICE_KEY` 환경변수로 설정합니다.

원본 데이터와 `outputs/`는 저장소에서 제외되어 있습니다. 저장된 노트북 결과는 열람할 수 있지만,
전체 재실행에는 각 문서에 안내된 공개자료를 수집하여 원래 경로에 준비해야 합니다.
실제 카드·통신 본자료 및 국세청 사업체별 자료를 공개한 저장소가 아닙니다.

## 개인정보·인증정보

API 키가 있는 로컬 `sample.ipynb`, 환경설정 파일, 원본 데이터, 생성 산출물은 `.gitignore`로 제외합니다.
향후 사업체별 비공개 자료나 인터뷰 원문은 `private/` 또는 `confidential/`에 보관하고 커밋하지 않습니다.
새 노트북을 공개하기 전에는 코드뿐 아니라 실행 결과와 메타데이터에도 민감정보가 없는지 확인해야 합니다.
