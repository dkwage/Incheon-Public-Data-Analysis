# 미추홀구 SNS 댓글 데이터 분석 — 발표 패키지 (10분)

- 대상: 미추홀구청 공무원 (데이터 분석 비전문가)
- 구성: Background → Problem → Goal → Implementation → Evaluation → Contribution
- 분량: 14장 / 약 10분 (장당 35~45초)
- 모든 수치는 `NLP/results/` 실제 산출물 기준 (YouTube 46편, 댓글 3,026건)
- SVG는 CSS·변수 없이 색·글꼴을 속성으로 직접 지정 → 그대로 복사해 PowerPoint/Keynote/웹에 삽입해도 검게 깨지지 않음 (라이트 배경 고정)

---

## 슬라이드 1 — 표지

**장표 텍스트**

> ### 댓글 3,026건이 말해준 것
> #### 미추홀구 SNS 반응 데이터 분석 결과 보고
> 분석 대상: 유튜브 게시물 46편 · 댓글 3,026건
> 방법: 자동 수집 → AI 분류 → 통계 검증

**대본 (30초)**

> 안녕하십니까. 오늘은 우리 구 유튜브 채널에 달린 댓글 3,026건을 컴퓨터로 전수 분석한 결과를 보고드리겠습니다.
> 어려운 통계 이야기는 최소로 하고, "우리가 무엇을 알게 되었는지"와 "그래서 무엇을 바꾸면 되는지" 두 가지만 남기도록 하겠습니다.
> 크게 배경, 문제, 목표, 진행 방법, 결과, 기여 순서로 말씀드리겠습니다.

---

## 슬라이드 2 — Background: 우리는 이미 데이터를 매일 만들고 있다

**장표 텍스트**

> ### 홍보 활동은 매일 데이터를 남깁니다
> - 유튜브 게시물 **46편**, 댓글 **3,026건** (분석 시점 누적)
> - 지금까지의 성과 판단 기준: **조회수 · 좋아요 · 댓글 수**
> - 그러나 댓글 안에는 조회수에 없는 정보가 있습니다
>   → 무엇을 **묻는지**, 무엇에 **고맙다 하는지**, 무엇에 **불편하다 하는지**
> - 사람이 3,026건을 다 읽으면 1건 10초만 잡아도 **8시간 이상**

**대본 (45초)**

> 먼저 배경입니다. 우리 구는 이미 홍보를 하면서 매일 데이터를 만들고 있습니다. 지금 유튜브에는 게시물 46편, 댓글 3,026건이 쌓여 있습니다.
> 그런데 성과를 볼 때는 보통 조회수, 좋아요, 댓글 수만 봅니다. 이 숫자들은 "얼마나 많이 봤는지"는 알려주지만, "주민이 무엇을 말했는지"는 알려주지 않습니다.
> 댓글에는 그 정보가 들어 있습니다. 무엇을 묻는지, 무엇에 고마워하는지, 무엇이 불편한지가 다 적혀 있습니다.
> 문제는 양입니다. 3,026건을 한 건에 10초씩만 읽어도 여덟 시간이 넘습니다. 그래서 자동화가 필요했습니다.

---

## 슬라이드 3 — Problem: 댓글 수가 성과를 부풀린다

**장표 텍스트**

> ### 문제 1. 댓글 수의 착시
> 전체 댓글 3,026건 중 **745건(24.6%)이 이벤트 응모 댓글**
> "정답 1번", "참여합니다" — 콘텐츠 반응이 아니라 경품 응모
>
> ### 문제 2. 진짜 민원이 묻힌다
> 3,026건 중 구청 조치가 필요한 민원은 **9건**
> 전체의 0.3% — 눈으로 찾기 어려운 규모
>
> ### 문제 3. 기준이 사람마다 다르다
> "긍정 댓글"의 정의가 담당자마다 달라 **연도별·부서별 비교 불가**

**대본 (50초)**

> 문제는 세 가지였습니다.
> 첫째, 댓글 수가 성과를 부풀립니다. 전체 3,026건 중 745건, 약 4분의 1이 "정답 1번", "참여합니다" 같은 이벤트 응모 댓글이었습니다. 콘텐츠가 좋아서 쓴 반응이 아니라 경품 응모입니다. 이걸 섞어서 세면 잘 만든 영상과 경품을 크게 건 영상이 똑같이 잘한 것으로 보입니다.
> 둘째, 진짜 민원은 묻힙니다. 구청이 실제로 조치해야 할 민원은 3,026건 중 9건이었습니다. 0.3%입니다. 사람이 눈으로 훑어서 찾을 수 있는 규모가 아닙니다.
> 셋째, 기준이 사람마다 다릅니다. "긍정적인 댓글"을 담당자마다 다르게 세면, 작년과 올해를 비교할 수 없습니다.

---

## 슬라이드 4 — Goal: 세 가지 목표

**장표 텍스트**

> ### 이번 분석의 목표
> 1. **분리하기** — 이벤트 응모 댓글과 진짜 반응을 구분해 "순수 긍정률" 산출
> 2. **찾아내기** — 조치가 필요한 민원을 자동으로 뽑아 유형까지 분류
> 3. **비교하기** — 콘텐츠 주제별로 어떤 반응이 나오는지 통계로 확인
>
> 전제 조건: **누가 다시 돌려도 같은 결과** (기준을 코드로 고정)

**대본 (35초)**

> 그래서 목표를 세 가지로 잡았습니다.
> 첫째, 분리하기. 이벤트 응모 댓글을 걸러내고 남은 것만으로 "순수 긍정률"을 계산합니다.
> 둘째, 찾아내기. 조치가 필요한 민원만 자동으로 뽑고, 시설, 교통, 행정 같은 유형까지 붙입니다.
> 셋째, 비교하기. 경제, 행정, 문화 같은 콘텐츠 주제별로 반응이 어떻게 다른지 통계로 확인합니다.
> 그리고 가장 중요한 전제는, 판단 기준을 사람 머릿속이 아니라 코드에 고정해서 누가 다시 돌려도 같은 결과가 나오게 하는 것입니다.

---

## 슬라이드 5 — Implementation: 작업은 5단계

**장표 텍스트**

> ### 자동화 파이프라인 5단계
> 수집 → 정리 → 이벤트 분리 → 감성 판정 → 민원·유형 분류 → 결과 산출

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 200" width="900" height="200" role="img"
     aria-label="파이프라인 5단계: 수집, 정리, 이벤트 분리, 감성 판정, 분류와 집계" font-family="system-ui, -apple-system, 'Segoe UI', sans-serif">
  <g class="flow">
    <rect class="bg" x="0" y="0" width="900" height="200" fill="#fcfcfb"/>
    <g>
      <rect class="card" x="20" y="46" width="150" height="72" rx="10" fill="#e8f1fd" stroke="#2a78d6" stroke-width="1.5"/>
      <text class="t1" x="36" y="76" fill="#0b0b0b" font-size="15px" font-weight="600">1. 수집</text>
      <text class="t2" x="36" y="98" fill="#52514e" font-size="12.5px">유튜브 API 자동 수집</text>
    </g>
    <path class="arrow" d="M176 82 H 196" stroke="#2a78d6" stroke-width="2" fill="none"/><path class="arrow" d="M190 76 l 8 6 l -8 6" stroke="#2a78d6" stroke-width="2" fill="none"/>
    <g>
      <rect class="card" x="200" y="46" width="150" height="72" rx="10" fill="#e8f1fd" stroke="#2a78d6" stroke-width="1.5"/>
      <text class="t1" x="216" y="76" fill="#0b0b0b" font-size="15px" font-weight="600">2. 정리</text>
      <text class="t2" x="216" y="98" fill="#52514e" font-size="12.5px">중복·공백 제거</text>
    </g>
    <path class="arrow" d="M356 82 H 376" stroke="#2a78d6" stroke-width="2" fill="none"/><path class="arrow" d="M370 76 l 8 6 l -8 6" stroke="#2a78d6" stroke-width="2" fill="none"/>
    <g>
      <rect class="card" x="380" y="46" width="150" height="72" rx="10" fill="#e8f1fd" stroke="#2a78d6" stroke-width="1.5"/>
      <text class="t1" x="396" y="76" fill="#0b0b0b" font-size="15px" font-weight="600">3. 이벤트 분리</text>
      <text class="t2" x="396" y="98" fill="#52514e" font-size="12.5px">응모 키워드 규칙</text>
    </g>
    <path class="arrow" d="M536 82 H 556" stroke="#2a78d6" stroke-width="2" fill="none"/><path class="arrow" d="M550 76 l 8 6 l -8 6" stroke="#2a78d6" stroke-width="2" fill="none"/>
    <g>
      <rect class="card" x="560" y="46" width="150" height="72" rx="10" fill="#e8f1fd" stroke="#2a78d6" stroke-width="1.5"/>
      <text class="t1" x="576" y="76" fill="#0b0b0b" font-size="15px" font-weight="600">4. 감성 판정</text>
      <text class="t2" x="576" y="98" fill="#52514e" font-size="12.5px">한국어 AI 모델(로컬)</text>
    </g>
    <path class="arrow" d="M716 82 H 736" stroke="#2a78d6" stroke-width="2" fill="none"/><path class="arrow" d="M730 76 l 8 6 l -8 6" stroke="#2a78d6" stroke-width="2" fill="none"/>
    <g>
      <rect class="card" x="740" y="46" width="140" height="72" rx="10" fill="#e8f1fd" stroke="#2a78d6" stroke-width="1.5"/>
      <text class="t1" x="756" y="76" fill="#0b0b0b" font-size="15px" font-weight="600">5. 분류·집계</text>
      <text class="t2" x="756" y="98" fill="#52514e" font-size="12.5px">민원·긍정 유형</text>
    </g>
    <text class="cap" x="20" y="152" fill="#898781" font-size="12px">사람이 하는 일: 대상 영상 목록 관리 · 결과 검토</text>
    <text class="cap" x="20" y="172" fill="#898781" font-size="12px">기계가 하는 일: 수집 · 판정 · 분류 · 집계 · 표와 그림 생성 (실행 1회로 끝)</text>
  </g>
</svg>
```

**대본 (45초)**

> 작업은 다섯 단계입니다.
> 1단계, 수집입니다. 유튜브가 공식으로 제공하는 연결 통로로 댓글을 자동으로 받아옵니다.
> 2단계, 정리입니다. 같은 댓글이 두 번 들어온 것, 빈 칸을 없앱니다.
> 3단계, 이벤트 분리입니다. "정답", "참여합니다" 같은 응모 표현이 있으면 성과 계산에서 빼고 따로 셉니다.
> 4단계, 감성 판정입니다. 한국어 전용 AI 모델을 담당자 PC 안에서 돌려 긍정인지 부정인지를 나눕니다. 이 단계는 외부로 나가지 않습니다.
> 5단계, 부정으로 나온 댓글만 생성형 AI에 보내서 "이게 진짜 민원인가, 그냥 불만인가"를 판정하고, 긍정 댓글은 여섯 가지 유형으로 묶습니다.
> 사람이 하는 일은 대상 영상 목록 관리와 결과 검토뿐이고, 나머지는 한 번 실행으로 끝납니다.

---

## 슬라이드 6 — Implementation: 판단 기준과 안전장치

**장표 텍스트**

> ### 무엇을 어떻게 판정했는가
> | 단계 | 기준 | 왜 이렇게 했나 |
> |---|---|---|
> | 이벤트 응모 | "정답 / 참여합니다 / 이벤트" 등 키워드 | 규칙이 명확해 사람이 검증 가능 |
> | 긍정·부정 | 한국어 감성 AI 모델(담당자 PC에서 실행) | 3,026건 전수 처리, 외부 전송 없음 |
> | 민원 여부 | 생성형 AI가 "구청 조치 필요"만 민원으로 판정 | 단순 불만과 민원을 구분 |
> | 긍정 유형 | 정보요청·제안·칭찬·공감·응원·일상 6종 | 담당 부서가 바로 쓸 수 있는 구분 |
>
> **비용 통제**: 생성형 AI 호출은 부정 댓글 **24건 + 1회(키워드 묶음)** 뿐 → 전체 3,026건의 0.8%
> **개인정보**: 분석은 전부 담당자 PC에서 실행, 서버 미구축, 외부에 공개되는 화면 없음
>
> <sub>기술 각주: 감성 AI는 댓글을 단어 조각(subword) 단위로 잘라 읽습니다(어휘 35,000개 사전). 키워드 추출만 별도로 한국어 형태소 분석기(Kiwi)를 씁니다.</sub>

**대본 (45초)**

> 판정 기준을 조금 더 풀어 말씀드리겠습니다.
> 이벤트 응모는 키워드 규칙으로 잡습니다. 규칙이라 사람이 눈으로 검증할 수 있습니다.
> 긍정과 부정은 한국어 감성 AI 모델로 3,026건 전부 판정합니다. 이 모델은 담당자 PC 안에서 돌기 때문에 댓글이 밖으로 나가지 않습니다.
> 그다음, 부정으로 분류된 것만 생성형 AI에 보냅니다. 판단 기준은 하나입니다. "구청이 답변하거나 고쳐야 할 일인가." 그렇다면 민원, 아니면 단순 불만입니다.
> 여기서 비용도 같이 잡았습니다. 생성형 AI를 3,026건 전부에 쓰면 시간과 비용이 크게 늘지만, 부정 24건과 키워드 묶음 1회만 호출해서 전체의 1퍼센트 미만으로 줄였습니다.

---

## 슬라이드 7 — Evaluation ①: 댓글 3,026건의 실제 구성

**장표 텍스트**

> ### 댓글 4건 중 1건은 콘텐츠 반응이 아니었습니다
> 이벤트 응모 **745건(24.6%)** · 긍정·중립 **2,257건(74.6%)** · 부정 **24건(0.8%)**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 260" width="900" height="260" role="img"
     aria-label="댓글 3,026건 구성: 이벤트 응모 745건 24.6퍼센트, 긍정·중립 2257건 74.6퍼센트, 부정 24건 0.8퍼센트"
     font-family="system-ui, -apple-system, 'Segoe UI', sans-serif">
  <g class="c1">
    <rect class="bg" x="0" y="0" width="900" height="260" fill="#fcfcfb"/>
    <text class="ttl" x="30" y="34" fill="#0b0b0b" font-size="16px" font-weight="600">댓글 3,026건의 구성</text>
    <text class="sub" x="30" y="56" fill="#52514e" font-size="13px">가로 막대 전체 = 수집된 댓글 3,026건</text>

    <!-- 범례: 2계열 이상이므로 필수 -->
    <g>
      <rect x="30" y="76" width="12" height="12" rx="3" fill="#2a78d6"/>
      <text class="val" x="48" y="87" fill="#52514e" font-size="12.5px">이벤트 응모</text>
      <rect x="150" y="76" width="12" height="12" rx="3" fill="#eb6834"/>
      <text class="val" x="168" y="87" fill="#52514e" font-size="12.5px">긍정·중립(진짜 반응)</text>
      <rect x="330" y="76" width="12" height="12" rx="3" fill="#1baf7a"/>
      <text class="val" x="348" y="87" fill="#52514e" font-size="12.5px">부정</text>
    </g>

    <!-- 누적 막대: 780px = 3,026건 / 745→192px, 2,257→582px, 24→6px / 조각 사이 2px 여백 -->
    <g>
      <path d="M30 112 h186 v24 h-186 z" fill="#2a78d6"/>
      <path d="M218 112 h580 v24 h-580 z" fill="#eb6834"/>
      <path d="M800 112 h2 v24 h-2 z M802 112 a4 4 0 0 1 4 4 v16 a4 4 0 0 1 -4 4 z" fill="#1baf7a"/>
    </g>

    <text class="lbl" x="42" y="129" fill="#ffffff" font-size="13.5px" font-weight="600">745건 · 24.6%</text>
    <text class="lbl" x="230" y="129" fill="#ffffff" font-size="13.5px" font-weight="600">2,257건 · 74.6%</text>

    <!-- 얇은 조각은 지시선으로 밖에 라벨 -->
    <line class="lead" x1="803" y1="112" x2="803" y2="96" stroke="#898781" stroke-width="1"/>
    <text class="val" x="742" y="90" fill="#52514e" font-size="12.5px">부정 24건 · 0.8%</text>

    <text class="lbl" x="30" y="176" fill="#0b0b0b" font-size="13.5px" font-weight="600">이벤트 응모를 빼면 성과 계산 대상은 2,281건</text>
    <text class="val" x="30" y="198" fill="#52514e" font-size="12.5px">그중 부정 24건을 다시 판정 → 구청 조치가 필요한 민원 9건 (전체의 0.3%)</text>
    <text class="mut" x="30" y="228" fill="#898781" font-size="12px">출처: results/michuhol_analysis_raw.csv (n=3,026, 게시물 46편)</text>
  </g>
</svg>
```

**대본 (45초)**

> 첫 번째 결과입니다. 이 가로 막대 하나가 댓글 3,026건 전체입니다.
> 왼쪽 파란 부분이 이벤트 응모 745건, 24.6퍼센트입니다. 4건 중 1건이 콘텐츠 반응이 아니라 경품 응모였습니다.
> 가운데 주황이 실제 긍정 또는 중립 반응 2,257건이고, 맨 오른쪽 아주 얇은 조각이 부정 24건, 0.8퍼센트입니다.
> 여기서 두 가지를 확인했습니다. 하나, 성과를 계산할 때는 응모를 뺀 2,281건만 봐야 한다는 것. 둘, 부정 댓글이 0.8퍼센트로 매우 적고, 그중 실제 조치가 필요한 민원은 9건이라는 것입니다.
> 즉 우리 채널의 여론은 나쁘지 않습니다. 대신 성과 지표는 부풀려져 있었습니다.

---

## 슬라이드 8 — Evaluation ②: 주민이 가장 많이 한 것은 "질문"

**장표 텍스트**

> ### 긍정·중립 댓글 2,257건의 성격
> 1위 **정보요청 573건(25.4%)** — 칭찬·감사(210건)보다 2.7배 많음

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 300" width="900" height="300" role="img"
     aria-label="긍정·중립 댓글 2257건 유형별 건수: 정보요청 573, 일상·감상 560, 제안·아이디어 384, 응원·격려 285, 공감·감동 245, 칭찬·감사 210"
     font-family="system-ui, -apple-system, 'Segoe UI', sans-serif">
  <g class="c2">
    <rect class="bg" x="0" y="0" width="900" height="300" fill="#fcfcfb"/>
    <text class="ttl" x="30" y="32" fill="#0b0b0b" font-size="16px" font-weight="600">긍정·중립 댓글의 유형 (n=2,257)</text>
    <text class="sub" x="30" y="54" fill="#52514e" font-size="13px">가로 길이 = 댓글 건수 · 단일 계열이라 범례 없음</text>

    <!-- 격자: x 190→830 = 0→600건 -->
    <g>
      <line class="grid" x1="190" y1="76" x2="190" y2="252" stroke="#e1e0d9" stroke-width="1"/>
      <line class="grid" x1="403" y1="76" x2="403" y2="252" stroke="#e1e0d9" stroke-width="1"/>
      <line class="grid" x1="616" y1="76" x2="616" y2="252" stroke="#e1e0d9" stroke-width="1"/>
      <line class="grid" x1="830" y1="76" x2="830" y2="252" stroke="#e1e0d9" stroke-width="1"/>
      <text class="tick" x="190" y="270" text-anchor="middle" fill="#898781" font-size="11.5px">0</text>
      <text class="tick" x="403" y="270" text-anchor="middle" fill="#898781" font-size="11.5px">200</text>
      <text class="tick" x="616" y="270" text-anchor="middle" fill="#898781" font-size="11.5px">400</text>
      <text class="tick" x="830" y="270" text-anchor="middle" fill="#898781" font-size="11.5px">600</text>
    </g>

    <!-- 막대: 두께 20px, 데이터 끝만 4px 라운드, 1건 = 1.0667px -->
    <g fill="#2a78d6">
      <path d="M190 82 h607 a4 4 0 0 1 4 4 v12 a4 4 0 0 1 -4 4 h-607 z"/>
      <path d="M190 110 h593 a4 4 0 0 1 4 4 v12 a4 4 0 0 1 -4 4 h-593 z"/>
      <path d="M190 138 h406 a4 4 0 0 1 4 4 v12 a4 4 0 0 1 -4 4 h-406 z"/>
      <path d="M190 166 h300 a4 4 0 0 1 4 4 v12 a4 4 0 0 1 -4 4 h-300 z"/>
      <path d="M190 194 h257 a4 4 0 0 1 4 4 v12 a4 4 0 0 1 -4 4 h-257 z"/>
      <path d="M190 222 h220 a4 4 0 0 1 4 4 v12 a4 4 0 0 1 -4 4 h-220 z"/>
    </g>
    <line class="axis" x1="190" y1="76" x2="190" y2="252" stroke="#c3c2b7" stroke-width="1"/>

    <g class="cat" text-anchor="end" fill="#0b0b0b" font-size="13.5px">
      <text x="176" y="97">정보요청</text>
      <text x="176" y="125">일상·감상</text>
      <text x="176" y="153">제안·아이디어</text>
      <text x="176" y="181">응원·격려</text>
      <text x="176" y="209">공감·감동</text>
      <text x="176" y="237">칭찬·감사</text>
    </g>

    <g class="val" fill="#52514e" font-size="13px" font-weight="600">
      <text x="811" y="97">573</text>
      <text x="797" y="125">560</text>
      <text x="610" y="153">384</text>
      <text x="504" y="181">285</text>
      <text x="461" y="209">245</text>
      <text x="424" y="237">210</text>
    </g>

    <text class="mut" x="30" y="290" fill="#898781" font-size="12px">출처: results/michuhol_analysis_raw.csv — 이벤트 응모·부정 댓글 제외</text>
  </g>
</svg>
```

**대본 (50초)**

> 두 번째 결과입니다. 긍정·중립 댓글 2,257건이 어떤 성격이었는지 나눠봤습니다.
> 1위가 칭찬이 아니라 정보요청이었습니다. 573건, 약 4분의 1입니다. "언제 하나요", "어디서 하나요", "어떻게 신청하나요" 같은 질문입니다. 칭찬·감사는 210건으로, 질문이 칭찬보다 2.7배 많았습니다.
> 세 번째는 제안·아이디어 384건입니다. 주민이 먼저 개선안을 준 겁니다.
> 이건 실무적으로 아주 중요한 신호입니다. 우리 콘텐츠가 관심은 끌었지만, 정작 필요한 안내 정보, 즉 일정, 장소, 신청 방법이 영상이나 설명란에 부족했다는 뜻입니다.
> 바꿔 말하면, 영상 고정 댓글에 일정과 신청 링크만 넣어도 이 질문들 상당수는 미리 해결됩니다.

---

## 슬라이드 9 — Evaluation ③: 이벤트는 숫자를 확실히 올린다

**장표 텍스트**

> ### 이벤트 게시물 8편 vs 일반 게시물 38편
> 게시물당 댓글 **366.4건 vs 2.5건** · 댓글 평균 길이 **99.9자 vs 22.2자**
> 무작위 재배치 10,000회 검증 결과 **우연일 확률 0.01% 미만 (p < 0.0001)**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 300" width="900" height="300" role="img"
     aria-label="이벤트 게시물과 일반 게시물 비교. 게시물당 댓글 수 366.4 대 2.5, 댓글 평균 글자 수 99.9 대 22.2"
     font-family="system-ui, -apple-system, 'Segoe UI', sans-serif">
  <g class="c3">
    <rect class="bg" x="0" y="0" width="900" height="300" fill="#fcfcfb"/>
    <text class="ttl" x="30" y="32" fill="#0b0b0b" font-size="16px" font-weight="600">이벤트 게시물(8편)과 일반 게시물(38편) 비교</text>

    <g>
      <rect x="30" y="48" width="12" height="12" rx="3" fill="#2a78d6"/>
      <text class="val" x="48" y="59" fill="#52514e" font-size="13px" font-weight="600">이벤트 게시물</text>
      <rect x="180" y="48" width="12" height="12" rx="3" fill="#898781"/>
      <text class="val" x="198" y="59" fill="#52514e" font-size="13px" font-weight="600">일반 게시물</text>
    </g>

    <!-- 왼쪽 패널: 게시물당 댓글 수, 0~400건을 250px에 대응 -->
    <g>
      <text class="pnl" x="30" y="96" fill="#0b0b0b" font-size="14px" font-weight="600">게시물당 댓글 수 (건)</text>
      <line class="axis" x1="150" y1="108" x2="150" y2="176" stroke="#c3c2b7" stroke-width="1"/>
      <path d="M150 114 h225 a4 4 0 0 1 4 4 v12 a4 4 0 0 1 -4 4 h-225 z" fill="#2a78d6"/>
      <path d="M150 148 h1.6 v20 h-1.6 z" fill="#898781"/>
      <text class="cat" x="140" y="129" text-anchor="end" fill="#0b0b0b" font-size="13px">이벤트</text>
      <text class="cat" x="140" y="163" text-anchor="end" fill="#0b0b0b" font-size="13px">일반</text>
      <text class="val" x="389" y="129" fill="#52514e" font-size="13px" font-weight="600">366.4</text>
      <text class="val" x="164" y="163" fill="#52514e" font-size="13px" font-weight="600">2.5</text>
      <text class="mut" x="150" y="196" fill="#898781" font-size="12px">이벤트 게시물이 약 147배 많은 댓글을 모았습니다</text>
    </g>

    <!-- 오른쪽 패널: 댓글 평균 글자 수, 0~120자를 250px에 대응 (단위가 달라 축 분리) -->
    <g>
      <text class="pnl" x="470" y="96" fill="#0b0b0b" font-size="14px" font-weight="600">댓글 평균 글자 수 (자)</text>
      <line class="axis" x1="590" y1="108" x2="590" y2="176" stroke="#c3c2b7" stroke-width="1"/>
      <path d="M590 114 h204 a4 4 0 0 1 4 4 v12 a4 4 0 0 1 -4 4 h-204 z" fill="#2a78d6"/>
      <path d="M590 148 h42 a4 4 0 0 1 4 4 v12 a4 4 0 0 1 -4 4 h-42 z" fill="#898781"/>
      <text class="cat" x="580" y="129" text-anchor="end" fill="#0b0b0b" font-size="13px">이벤트</text>
      <text class="cat" x="580" y="163" text-anchor="end" fill="#0b0b0b" font-size="13px">일반</text>
      <text class="val" x="808" y="129" fill="#52514e" font-size="13px" font-weight="600">99.9</text>
      <text class="val" x="646" y="163" fill="#52514e" font-size="13px" font-weight="600">22.2</text>
      <text class="mut" x="590" y="196" fill="#898781" font-size="12px">길이는 길지만, 내용은 대부분 응모 문구였습니다</text>
    </g>

    <text class="mut" x="30" y="242" fill="#898781" font-size="12px">검증 방법: 게시물 46편의 이벤트 여부 라벨을 10,000번 무작위로 섞어 관측된 차이가 우연히 나올 확률을 계산 (순열검정)</text>
    <text class="mut" x="30" y="262" fill="#898781" font-size="12px">결과: 두 지표 모두 p &lt; 0.0001 — 우연으로 보기 어려움 · 두 지표는 단위가 달라 축을 나눠 표시</text>
    <text class="mut" x="30" y="282" fill="#898781" font-size="12px">출처: results/hypothesis_test_by_title.csv, figures/permutation_test_results.png</text>
  </g>
</svg>
```

**대본 (50초)**

> 세 번째 결과입니다. 이벤트를 건 게시물 8편과 일반 게시물 38편을 비교했습니다.
> 왼쪽을 보시면 게시물당 댓글 수가 366건 대 2.5건입니다. 약 147배입니다. 이벤트는 숫자를 확실히 올립니다.
> 오른쪽은 댓글 길이입니다. 100자 대 22자로, 이벤트 쪽 댓글이 훨씬 깁니다. 다만 길이만 길고 내용은 대부분 응모 문구였습니다.
> 이게 우연일 수 있으니, 게시물 46편의 "이벤트다, 아니다" 라벨을 컴퓨터로 1만 번 무작위로 섞어봤습니다. 무작위로 섞었을 때 이만큼 큰 차이가 나오는 경우는 1만 번 중 한 번도 없었습니다. 통계적으로 확실한 차이라는 뜻입니다.
> 한 가지만 덧붙이면, 왼쪽과 오른쪽은 단위가 달라서 일부러 축을 나눠 그렸습니다. 하나의 그래프에 억지로 겹치면 왜곡됩니다.

---

## 슬라이드 10 — Evaluation ④: 그런데 이벤트 비중이 커지면 반응 품질이 떨어진다

**장표 텍스트**

> ### 응모 비중이 높을수록 전체 긍정률은 낮아집니다
> 상관계수 **r = -0.54** (46편, p = 0.0001, 설명력 R² = 0.29)
> 응모 비중이 높은 게시물일수록 "응모 문구만 쓴 댓글" 비율도 급증 (r = 0.94 — 단 8편 기준, 참고용)
> 낙수 효과(이벤트로 들어온 사람이 다른 반응까지 남기는 효과)는 **확인되지 않음** (r = 0.09, p = 0.58)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 340" width="900" height="340" role="img"
     aria-label="게시물 46편 산점도. 가로축 이벤트 응모 비중 퍼센트, 세로축 전체 긍정률 퍼센트. 응모 비중이 높아질수록 긍정률이 낮아지는 음의 추세."
     font-family="system-ui, -apple-system, 'Segoe UI', sans-serif">
  <g class="c4">
    <rect class="bg" x="0" y="0" width="900" height="340" fill="#fcfcfb"/>
    <text class="ttl" x="30" y="32" fill="#0b0b0b" font-size="16px" font-weight="600">게시물 46편: 이벤트 응모 비중 대비 전체 긍정률</text>
    <text class="sub" x="470" y="32" fill="#52514e" font-size="13px">점 하나 = 게시물 1편 (같은 값은 한 점에 겹침)</text>

    <!-- 그림 영역: x 90~690 = 0~100%, y 250~70 = 0~100% -->
    <g>
      <line class="grid" x1="90" y1="70" x2="690" y2="70" stroke="#e1e0d9" stroke-width="1"/>
      <line class="grid" x1="90" y1="115" x2="690" y2="115" stroke="#e1e0d9" stroke-width="1"/>
      <line class="grid" x1="90" y1="160" x2="690" y2="160" stroke="#e1e0d9" stroke-width="1"/>
      <line class="grid" x1="90" y1="205" x2="690" y2="205" stroke="#e1e0d9" stroke-width="1"/>
      <line class="axis" x1="90" y1="250" x2="690" y2="250" stroke="#c3c2b7" stroke-width="1"/>
      <line class="axis" x1="90" y1="70" x2="90" y2="250" stroke="#c3c2b7" stroke-width="1"/>
      <g class="tick" text-anchor="end" fill="#898781" font-size="11.5px">
        <text x="80" y="74">100</text>
        <text x="80" y="119">75</text>
        <text x="80" y="164">50</text>
        <text x="80" y="209">25</text>
        <text x="80" y="254">0</text>
      </g>
      <g class="tick" text-anchor="middle" fill="#898781" font-size="11.5px">
        <text x="90" y="270">0</text>
        <text x="240" y="270">25</text>
        <text x="390" y="270">50</text>
        <text x="540" y="270">75</text>
        <text x="690" y="270">100</text>
      </g>
      <text class="ax" x="390" y="292" text-anchor="middle" fill="#52514e" font-size="12.5px">이벤트 응모 댓글 비중 (%)</text>
      <text class="ax" x="30" y="64" fill="#52514e" font-size="12.5px">전체 긍정률 (%)</text>

      <!-- 추세선: y = 88.03 - 0.852x -->
      <path class="trend" d="M90 91.5 L690 245" stroke="#52514e" stroke-width="2" stroke-linecap="round" fill="none"/>

      <!-- 게시물 46편: 응모 0%인 38편은 모두 x=90에 위치 (겹침은 건수로 표기) -->
      <g class="dot" fill="#2a78d6" stroke="#fcfcfb" stroke-width="2">
        <circle cx="90" cy="250" r="4"/>
        <circle cx="90" cy="190.1" r="4"/>
        <circle cx="90" cy="178" r="4"/>
        <circle cx="90" cy="160" r="4"/>
        <circle cx="90" cy="92.5" r="4"/>
        <circle cx="90" cy="90" r="4"/>
        <circle cx="90" cy="84.4" r="4"/>
        <circle cx="90" cy="70" r="4"/>
        <circle cx="102" cy="73.6" r="4"/>
        <circle cx="104.4" cy="75.8" r="4"/>
        <circle cx="109.2" cy="76.1" r="4"/>
        <circle cx="120" cy="81" r="4"/>
        <circle cx="151.2" cy="88.7" r="4"/>
        <circle cx="418.8" cy="168.6" r="4"/>
        <circle cx="640.8" cy="235.6" r="4"/>
        <circle cx="690" cy="250" r="4"/>
      </g>

      <!-- 겹친 점의 건수 표기 -->
      <line class="lead" x1="98" y1="70" x2="128" y2="62" stroke="#898781" stroke-width="1"/>
      <text class="mut" x="132" y="60" fill="#898781" font-size="12px">이 지점에 29편 (응모 0% · 긍정률 100%)</text>
      <line class="lead" x1="98" y1="249" x2="140" y2="232" stroke="#898781" stroke-width="1"/>
      <text class="mut" x="144" y="229" fill="#898781" font-size="12px">이 지점에 3편 (댓글 1건뿐인 게시물)</text>

      <text class="note" x="360" y="104" fill="#0b0b0b" font-size="13px" font-weight="600">추세선: 응모 비중 10%p 증가 → 긍정률 약 8.5%p 하락</text>
      <text class="mut" x="360" y="124" fill="#898781" font-size="12px">상관 r = -0.54 · p = 0.0001 · 설명력 R² = 0.29 (46편)</text>
    </g>

    <text class="mut" x="30" y="316" fill="#898781" font-size="12px">주의: 상관관계이며 인과관계가 아닙니다. 오른쪽 아래 두 점(응모 55%·92%)이 이벤트 물량이 가장 컸던 게시물입니다.</text>
    <text class="mut" x="30" y="334" fill="#898781" font-size="12px">출처: results/hypothesis_test_by_title.csv (n=46)</text>
  </g>
</svg>
```

**대본 (55초)**

> 네 번째 결과입니다. 여기가 이번 분석의 핵심입니다.
> 점 하나가 게시물 한 편입니다. 가로는 그 게시물 댓글 중 응모가 차지하는 비중, 세로는 전체 긍정률입니다.
> 오른쪽으로 갈수록, 즉 응모 비중이 커질수록 선이 아래로 내려갑니다. 응모 비중이 10퍼센트포인트 올라갈 때 전체 긍정률은 약 8.5퍼센트포인트 떨어졌습니다.
> 이유는 단순합니다. 응모 댓글이 자리를 채워버리기 때문에, 같은 게시물인데도 "진짜 반응"의 비중이 줄어드는 겁니다.
> 그리고 기대했던 낙수 효과, 즉 경품 때문에 들어온 사람이 다른 콘텐츠에도 반응을 남기는 효과는 확인되지 않았습니다.
> 다만 솔직하게 한계도 말씀드리겠습니다. 응모 비중이 높은 게시물은 8편뿐이라 표본이 작습니다. 그리고 이건 상관관계이지 인과관계가 아닙니다. "이벤트를 하지 말자"가 아니라, "이벤트 게시물의 성과는 응모를 뺀 뒤에 봐야 한다"는 결론입니다.

---

## 슬라이드 11 — Evaluation ⑤: 보정하면 주제별 격차가 사라진다

**장표 텍스트**

> ### 같은 데이터, 계산 기준만 바꿨을 때
> | 주제 | 전체 기준 긍정률 | 이벤트 응모 제외 시 | 차이 |
> |---|---|---|---|
> | 경제 (n=1,144) | 62.8% | **99.2%** | +36.3%p |
> | 행정 (n=1,333) | 78.6% | **99.1%** | +20.5%p |
> | 문화 (n=538) | 89.8% | **99.0%** | +9.2%p |
>
> → "경제 콘텐츠는 반응이 나쁘다"는 것은 **사실이 아니라 이벤트 물량의 착시**였습니다

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 320" width="900" height="320" role="img"
     aria-label="주제별 긍정률 비교. 경제 62.8퍼센트에서 99.2퍼센트, 행정 78.6퍼센트에서 99.1퍼센트, 문화 89.8퍼센트에서 99.0퍼센트"
     font-family="system-ui, -apple-system, 'Segoe UI', sans-serif">
  <g class="c5">
    <rect class="bg" x="0" y="0" width="900" height="320" fill="#fcfcfb"/>
    <text class="ttl" x="30" y="32" fill="#0b0b0b" font-size="16px" font-weight="600">주제별 긍정률: 전체 기준 vs 이벤트 응모 제외</text>
    <text class="sub" x="30" y="54" fill="#52514e" font-size="13px">가로 길이 = 긍정률(%)</text>

    <g>
      <rect x="30" y="70" width="12" height="12" rx="3" fill="#2a78d6"/>
      <text class="val" x="48" y="81" fill="#52514e" font-size="13px" font-weight="600">전체 기준</text>
      <rect x="160" y="70" width="12" height="12" rx="3" fill="#eb6834"/>
      <text class="val" x="178" y="81" fill="#52514e" font-size="13px" font-weight="600">이벤트 응모 제외</text>
    </g>

    <!-- 눈금: x 130~730 = 0~100% -->
    <g>
      <line class="grid" x1="280" y1="100" x2="280" y2="268" stroke="#e1e0d9" stroke-width="1"/>
      <line class="grid" x1="430" y1="100" x2="430" y2="268" stroke="#e1e0d9" stroke-width="1"/>
      <line class="grid" x1="580" y1="100" x2="580" y2="268" stroke="#e1e0d9" stroke-width="1"/>
      <line class="grid" x1="730" y1="100" x2="730" y2="268" stroke="#e1e0d9" stroke-width="1"/>
      <line class="axis" x1="130" y1="100" x2="130" y2="268" stroke="#c3c2b7" stroke-width="1"/>
      <g class="tick" text-anchor="middle" fill="#898781" font-size="11.5px">
        <text x="130" y="286">0</text>
        <text x="280" y="286">25</text>
        <text x="430" y="286">50</text>
        <text x="580" y="286">75</text>
        <text x="730" y="286">100</text>
      </g>
    </g>

    <!-- 묶은 막대: 두께 18px, 짝 사이 2px 여백 -->
    <g>
      <text class="cat" x="120" y="128" text-anchor="end" fill="#0b0b0b" font-size="14px" font-weight="600">경제</text>
      <path d="M130 108 h373 a4 4 0 0 1 4 4 v10 a4 4 0 0 1 -4 4 h-373 z" fill="#2a78d6"/>
      <path d="M130 128 h591 a4 4 0 0 1 4 4 v10 a4 4 0 0 1 -4 4 h-591 z" fill="#eb6834"/>
      <text class="val" x="513" y="121" fill="#52514e" font-size="13px" font-weight="600">62.8%</text>
      <text class="val" x="731" y="141" fill="#52514e" font-size="13px" font-weight="600">99.2%</text>

      <text class="cat" x="120" y="184" text-anchor="end" fill="#0b0b0b" font-size="14px" font-weight="600">행정</text>
      <path d="M130 164 h468 a4 4 0 0 1 4 4 v10 a4 4 0 0 1 -4 4 h-468 z" fill="#2a78d6"/>
      <path d="M130 184 h590 a4 4 0 0 1 4 4 v10 a4 4 0 0 1 -4 4 h-590 z" fill="#eb6834"/>
      <text class="val" x="608" y="177" fill="#52514e" font-size="13px" font-weight="600">78.6%</text>
      <text class="val" x="730" y="197" fill="#52514e" font-size="13px" font-weight="600">99.1%</text>

      <text class="cat" x="120" y="240" text-anchor="end" fill="#0b0b0b" font-size="14px" font-weight="600">문화</text>
      <path d="M130 220 h535 a4 4 0 0 1 4 4 v10 a4 4 0 0 1 -4 4 h-535 z" fill="#2a78d6"/>
      <path d="M130 240 h589 a4 4 0 0 1 4 4 v10 a4 4 0 0 1 -4 4 h-589 z" fill="#eb6834"/>
      <text class="val" x="675" y="233" fill="#52514e" font-size="13px" font-weight="600">89.8%</text>
      <text class="val" x="729" y="253" fill="#52514e" font-size="13px" font-weight="600">99.0%</text>
    </g>

    <text class="mut" x="30" y="308" fill="#898781" font-size="12px">출처: results/content_type_topic_event_compare.csv — 경제 n=1,144 · 행정 n=1,333 · 문화 n=538</text>
  </g>
</svg>
```

**대본 (45초)**

> 다섯 번째 결과입니다. 앞의 이야기가 왜 중요한지 보여주는 장면입니다.
> 파란 막대는 지금까지처럼 전체 댓글로 계산한 긍정률입니다. 경제 62.8퍼센트, 행정 78.6퍼센트, 문화 89.8퍼센트로, 경제 콘텐츠가 크게 나쁘게 보입니다.
> 주황 막대는 같은 데이터에서 이벤트 응모만 빼고 다시 계산한 값입니다. 경제 99.2, 행정 99.1, 문화 99.0. 세 주제가 사실상 같아집니다.
> 즉 "경제 콘텐츠는 주민 반응이 나쁘다"는 판단은 사실이 아니었습니다. 경제 콘텐츠에 이벤트를 많이 걸었기 때문에 생긴 착시였습니다.
> 데이터를 바꾼 게 아니라 계산 기준을 바로잡았을 뿐인데 결론이 뒤집혔습니다. 그래서 지표 정의가 중요합니다.

---

## 슬라이드 12 — Evaluation ⑥: 자동으로 찾아낸 민원 9건

**장표 텍스트**

> ### 부정 댓글 24건 → 실제 조치 필요 민원 9건 (전문 공개)
>
> | 유형 | 게시물 | 주민이 쓴 말 (원문) | 요구 사항 |
> |---|---|---|---|
> | 정책·사업 | 새해 인사 | "구청장님! 주민 반대 시 안 하겠다던 약속 지키십시오! 9개 단지 주민 연합은 데이터센터 건립을 결사반대합니다. … 착공 신고를 즉각 반려하십시오!" | 데이터센터 착공 신고 반려 |
> | 정책·사업 | 떡볶이 먹방 | "요즘 대학 상권이라는 게 없습니다 … 유동인구 자체가 없어요. 복지 향상을 고민할 시간에 상권 활성화를 고민해주세요" | 골목상권 활성화 대책 |
> | 정책·사업 | 교통 홍보 | "인천대로 일반화 쓰레기정책" | 인천대로 일반화 정책 재검토 |
> | 교통·도로 | 교통 홍보 | "ㅈㄴ 불편한데 배차간격 길고 느림" | 배차간격 단축·운행 속도 개선 |
> | 시설·환경 | 은행나무 가로수길 | "저걸 열매 안 열리게 하는 방법이 없나??" | 열매 방제·가로수 관리 |
> | 시설·환경 | 은행나무 가로수길 | "은행나무가 아니고 은행나무 열매 때문이지 말은 바로 해야 함" | 악취 등 생활 불편 개선 |
> | 행정·서비스 | 임시체육시설 개장 | "쇼츠 말고 풀버전 영상은 없나요?" | 풀버전 영상 제공 |
> | 행정·서비스 | 떡볶이 먹방 | "아니요 아직도 못 받았습니다😢" | 신청 결과·안내 확인 |
> | 이벤트·행사 | 떡볶이 먹방 | "당첨자입니다 경품이 5월 2일까지 발송이라고 써 있는데 일주일째 오지 않아서 문의드립니다" | 경품 발송 지연 확인 |
>
> 유형별 건수: 정책·사업 3 · 행정·서비스 2 · 시설·환경 2 · 이벤트·행사 1 · 교통·도로 1
> 나머지 15건은 단순 불만·감상으로 분류 (조치 불필요)
> 민원율이 높았던 게시물: 임시체육시설 개장(1/1건), 은행나무 가로수길(2/3건), 교통 정책(2/5건)
>
> **한계**: 민원 9건은 통계 모델을 돌릴 표본이 아님 → 유형별 위험도 비교는 하지 않았습니다

**대본 (40초)**

> 여섯 번째, 민원입니다. 부정으로 분류된 24건을 다시 판정해서, 구청이 실제로 답변하거나 조치해야 할 민원 9건을 뽑았습니다. 이 9건은 요약하지 않고 원문 그대로 올렸습니다. 화면 그대로가 주민이 쓴 문장입니다.
> 몇 개만 읽어보겠습니다. "구청장님, 주민 반대 시 안 하겠다던 약속 지키십시오. 데이터센터 건립을 결사반대합니다." "은행나무가 아니고 은행나무 열매 때문이지." "당첨자입니다, 경품이 일주일째 오지 않아서 문의드립니다."
> 보시면 아시겠지만 성격이 완전히 다릅니다. 하나는 정책 결정 사항, 하나는 생활 민원, 하나는 담당자가 오늘 바로 처리할 수 있는 건입니다. 유형으로는 정책·사업 3건, 행정·서비스 2건, 시설·환경 2건, 이벤트·행사와 교통·도로가 각 1건입니다.
> 나머지 15건은 그냥 불만이나 감상이라 조치가 필요 없다고 판정됐습니다.
> 흥미로운 건 민원이 특정 게시물에 몰린다는 점입니다. 임시체육시설 개장, 은행나무 가로수길, 교통 정책 홍보물에서 나왔습니다. 즉 생활 밀착 시설과 교통 관련 게시물이 민원 창구 역할을 하고 있었습니다.
> 다만 9건은 통계를 돌릴 표본이 아닙니다. 그래서 "어느 유형이 몇 배 위험하다" 같은 계산은 일부러 하지 않았습니다.

---

## 슬라이드 13 — Contribution: 남는 것 세 가지

**장표 텍스트**

> ### 이번 작업이 남긴 것
> 1. **다시 돌릴 수 있는 자동 파이프라인**
>    수집부터 표·그림 생성까지 실행 1회 · 새 영상이 늘어도 같은 방식으로 갱신
> 2. **부풀리지 않는 성과 지표 "순수 긍정률"**
>    이벤트 응모를 제외한 긍정률 → 부서·기간·주제 간 비교 가능
> 3. **주민 목소리의 자동 분류 체계**
>    민원 9건은 담당 부서로 · 정보요청 573건은 콘텐츠 개선 과제로
>
> ### 바로 적용 가능한 세 가지 제안
> - 영상마다 **고정 댓글에 일정·장소·신청 방법** 기재 (정보요청 573건 대응)
> - 이벤트 게시물은 **응모 제외 지표**를 함께 보고
> - 월 1회 파이프라인 실행 → **민원 후보 목록 자동 회람**

**대본 (50초)**

> 마지막으로 이번 작업이 무엇을 남겼는지 정리하겠습니다.
> 첫째, 자동 파이프라인입니다. 수집부터 표와 그림 만들기까지 한 번 실행으로 끝납니다. 영상이 늘어도 같은 방식으로 갱신되고, 담당자가 바뀌어도 결과가 같습니다.
> 둘째, 부풀리지 않는 지표입니다. 이벤트 응모를 제외한 "순수 긍정률"을 쓰면 부서끼리, 작년과 올해를 공정하게 비교할 수 있습니다.
> 셋째, 주민 목소리의 자동 분류입니다. 민원은 담당 부서로 넘기고, 정보요청은 콘텐츠 개선 과제로 넘기면 됩니다.
> 그래서 바로 적용할 수 있는 제안 세 가지를 드립니다. 하나, 영상마다 고정 댓글에 일정, 장소, 신청 방법을 넣는 것. 둘, 이벤트 게시물 보고 시 응모 제외 지표를 함께 쓰는 것. 셋, 한 달에 한 번 이 분석을 돌려서 민원 후보 목록을 회람하는 것입니다.

---

## 슬라이드 14 — 한계와 다음 단계 / Q&A

**장표 텍스트**

> ### 솔직한 한계
> - 분석 대상은 **유튜브 1개 채널** (인스타그램 수집 코드는 준비, 결과 미포함)
> - 이벤트 게시물 **8편**, 민원 **9건** — 표본이 작습니다
> - 모든 수치는 **상관관계·경향성**이며 인과관계가 아닙니다
> - AI 판정은 100% 정확하지 않습니다 → 민원 목록은 **사람 최종 확인 전제**
>
> ### 다음 단계 제안
> - 인스타그램·블로그까지 확대해 채널 간 비교
> - 이벤트 설계 변경 실험: 응모 문구 대신 **질문형 참여**로 유도 후 재측정
> - 민원 판정 정확도 검수 (담당자 100건 샘플 교차 확인)
>
> **감사합니다 — 질문 받겠습니다**

**대본 (35초)**

> 한계도 분명히 말씀드리겠습니다. 이번 분석은 유튜브 한 채널이고, 이벤트 게시물 8편, 민원 9건으로 표본이 작습니다. 그리고 전부 경향성이지 인과관계가 아닙니다. AI 판정도 100퍼센트 정확하지 않으니, 민원 목록은 담당자 확인을 거쳐야 합니다.
> 다음 단계로는 인스타그램까지 확대해서 채널을 비교하는 것, 응모 문구 대신 질문형 참여로 이벤트를 바꿔보고 다시 측정하는 것, 그리고 담당자가 100건 정도를 직접 확인해 AI 판정 정확도를 검수하는 것을 제안드립니다.
> 이상입니다. 질문 받겠습니다.

---

## 부록 A — 예상 질문 대응

| 질문 | 답변 요지 |
|---|---|
| "AI가 판단했다는데 믿을 수 있나?" | 감성 판정은 공개된 한국어 모델, 민원 판정은 생성형 AI. 기준을 문서로 고정했고 원본 댓글과 판정 결과를 CSV로 전부 남겨 사람이 검증 가능. |
| "댓글이 구청 밖으로 나가나?" | 감성 판정은 담당자 PC 내부 처리. 외부 전송은 부정 댓글 24건과 키워드 묶음 1회뿐. 서버 없음, 외부 공개 화면 없음. |
| "이벤트를 하지 말라는 뜻인가?" | 아니다. 이벤트는 도달 확대에 유효(댓글 147배). 다만 성과 보고 시 응모 제외 지표를 함께 봐야 한다는 뜻. |
| "비용이 얼마나 드나?" | 유튜브 수집은 무료 할당량 내, 생성형 AI 호출은 25회 수준. 사실상 담당자 실행 시간만 소요. |
| "우리 부서 콘텐츠는 왜 반응이 없나?" | 댓글 1~3건 게시물이 38편. 반응이 나쁜 게 아니라 노출·유입 자체가 적음. 별도 도달 지표 확인 필요. |
| "AI가 한국어를 어떻게 쪼개서 읽나?" | 감성 모델은 WordPiece 방식(어휘 35,000개)으로 단어를 조각내 읽음. 예: "주차장이 너무 부족해요" → 주차장 / 이 / 너무 / 부족 / 해 / 요. 사전에 없는 고유명사는 조각남(예: 미추홀구 → 미/추/홀/구) → 지역명 자체는 감성 판정에 거의 기여하지 않음. 키워드·워드클라우드는 이와 별개로 형태소 분석기 Kiwi가 명사·형용사만 뽑음. |

## 부록 B — 원본 산출물 위치

| 항목 | 경로 |
|---|---|
| 전체 분석 결과 | `results/michuhol_analysis_raw.csv` (3,026행) |
| 게시물별 성과 | `results/michuhol_performance_report.csv` (46행) |
| 가설검정 지표 | `results/hypothesis_test_by_title.csv` |
| 주제·형식별 비교 | `results/content_type_analysis_topic.csv`, `results/content_type_topic_event_compare.csv` |
| 순열검정 그림 | `figures/permutation_test_results.png`, `figures/permutation_boxplot.png` |
| 워드클라우드 | `figures/michuhol_wordcloud_positive.png`, `figures/michuhol_wordcloud_negative.png` |
| 파이프라인 구조도 | `docs/pipeline_architecture.html` |

## 부록 C — 차트 제작 규칙 (재사용 시 유지할 것)

- 색은 마지막에 결정. 크기 비교는 파란색 한 계열, 두 계열 비교만 파랑+주황(검증 통과 조합).
- 축은 하나만. 단위가 다른 두 지표(댓글 수 / 글자 수)는 그래프를 나눔 — 이중 축 금지.
- 막대 두께 24px 이하, 데이터 끝만 4px 둥글게, 기준선 쪽은 직각.
- 값 라벨은 선택적으로만(막대 끝, 최대값). 모든 점에 숫자 붙이지 않음.
- 2계열 이상이면 범례 필수. 색만으로 구분하게 만들지 않음.
- 라이트·다크 모드 값을 각각 지정 (자동 반전 금지).
- 팔레트 검증 명령: `node scripts/validate_palette.js "#2a78d6,#eb6834,#1baf7a" --mode light --pairs all` → 전 항목 통과 (아쿠아 대비 경고는 직접 라벨로 보완).
