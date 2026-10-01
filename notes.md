# 미니3: BuildWise AI

## 다시 실행하는 순서

1. 수집 스크립트 01_collect_p1.py와 02_collect.py는 다시 실행하지 않음
2. scripts/03_clean.py 실행 → data/clean.csv 갱신
3. scripts/04_stats.py 실행 → 기초 통계 확인
4. scripts/05_hist.py와 scripts/06_by_category.py 실행 → 필수 차트 갱신
5. scripts/07_export_json.py 실행 → data/data.json 갱신

## ① 환경 확인 출력

```
$ python3 scripts/00_env_check.py
환경 확인용 가상 예시
  PDF AI 도구   월 요금
0    가짜PDF봇   9900
1   테스트문서AI  14900
2     예시요약기  19900
(3, 2)
```

## ② 첫 페이지 수집 — data/raw_p1.csv

```
응답 상태: 200
수집한 행 수: 27

첫 행 (index 0)
name:         AI PDF Reader
price_raw:    Free plan · paid from $0.99/mo
citation_raw: Source citations
ocr_raw:      Scanned PDF support
detail_url:   https://www.itechguides.com/products/ai-pdf-reader/
```

## ③ notes.md — M02 한 페이지 수집

화면에서 센 항목 27개 = 수집 27행

| 행 | 열 | CSV 값 | 원래 화면 | 같나 |
|---|---|---|---|---|
| 0 | name | AI PDF Reader | AI PDF Reader | 같음 |
| 0 | price_raw | Free plan · paid from $0.99/mo | Free plan · paid from $0.99/mo | 같음 |
| 0 | citation_raw | Source citations | Source citations: Yes | 다름 |

목록 페이지에서는 기능명 문구만 수집되어 상세 화면의 실제 값 Yes까지는 포함되지 않음

잘려 보이는 이름 0개

## M03 표본 3행 대조

| 표본 | 행 번호 | 이름 | 숫자 | 범주 | 확인한 곳 |
|---|---|---|---|---|---|
| 앞 | 0 | 같음 (AI PDF Reader) | 같음 (Free plan · paid from $0.99/mo) | 같음 (CSV의 Source citations는 상세 화면에서 Source citations = Yes로 확인) | 상세 화면 |
| 가운데 | 13 | 같음 (ResearchPal AI Paraphraser) | 같음 (Free plan · paid from $8.25/mo (annual)) | 같음 (CSV의 Source citations는 상세 화면에서 Source citations = Yes로 확인) | 상세 화면 |
| 끝 | 26 | 같음 (Paperpal) | 같음 (Free plan · paid from $12/user/mo (annual)) | 같음 (CSV는 빈 값이고 상세 화면에도 Source citations 항목이 없음) | 상세 화면 |

판정: 표본 3행의 이름·숫자·범주 9칸 모두 원문과 같음

## M04 정제

### 정제 전 생김새 조사

- 전체 27행
- detail_url 중복 0개
- price_raw 빈칸 1개
- citation_raw 빈칸 7개
- ocr_raw 빈칸 17개
- price_raw에는 USD($), GBP(£), EUR(€) 통화가 섞여 있음
- 가격 기준에는 /mo, /user/mo, /yr, 기간 미표시가 섞여 있음
- 숫자가 없는 가격 원문은 Free plan 8행, Open source 2행, 빈칸 1행
- trial 문구가 있는 값도 있음

### 정제 규칙

1. price_raw는 이번 M04에서 "USD 월 가격이 명확하게 적힌 값"만 price 숫자 열로 바꾼다.
   - $숫자/mo → 숫자만 price에 저장
   - $숫자/user/mo → 숫자만 price에 저장
   - (annual)이 붙어 있어도 원문에 /mo가 명시되어 있으면 표시된 월 금액을 price에 저장한다.
   - trial 문구는 가격 숫자에 포함하지 않는다.

2. 아래 값은 이번 price 비교에서 억지로 바꾸지 않는다.
   - Free plan
   - Open source
   - 빈칸
   - From €10처럼 기간이 명확하지 않은 값
   - £150/yr처럼 통화와 과금 주기가 다른 값
   이런 값은 price를 NaN으로 두고, 사유를 출력한 뒤 clean.csv에서는 제외한다.

3. citation_raw는
   - Source citations → Yes
   - 빈칸 → No
   로 바꿔 citation 범주 열을 만든다.

4. name은 앞뒤 공백만 정리한다.

5. 원본 열은 삭제하지 않고 그대로 남긴다.
   price_raw 옆에 price, citation_raw 옆에 citation을 새로 만든다.

6. 못 바꾼 값에 0이나 평균값을 넣지 않는다.

7. 환율 환산은 이번 M04 필수 정제에서는 하지 않는다.
   원화 환산은 이후 BuildWise 확장 단계에서 원 통화·적용 환율·환율 기준일을 함께 기록해 계산한다.

### 첫 줄 손 검산 — 정제 실행 전

| 원문 | 손으로 바꿀 값 | clean.csv 값 | 같나 |
|---|---|---|---|
| Free plan · paid from $0.99/mo | 0.99 | 0.99 | 같음 |
| Source citations | Yes | Yes | 같음 |

### 처리 전후 확인

- 행 수: 27 → 14
- price_raw dtype: object → price dtype: float64
- citation_raw dtype: object → citation dtype: object
- price_raw 빈칸: 1 → price 빈칸: 0
- citation_raw 빈칸: 7 → citation 빈칸: 0
- detail_url 중복 수: 0 → 0
- 제외된 행: 13개
- 제외 사유: Free plan 8개, Open source 2개, 가격 원문 빈칸 1개, EUR 기간 미표시 1개, GBP 연 단위 1개

판정: 첫 줄 손 검산 2항목 모두 clean.csv 결과와 같음

## M05 데이터 점검표 (초안)

| 점검 항목 | 처리 전 | 처리 후 | 규칙·근거 |
|---|---|---|---|
| 수집 범위 | 목록 주소 https://www.itechguides.com/best/ai-pdf-assistants/ · 1페이지 · 원본 27행 | 미확인 | 노션 수집 기록서 |
| 행 수 | 27행 | 14행 | 27 − 13 = 14 (M04 처리 전후 확인) |
| 숫자 열 | price_raw: object | price: float64 | M04 정제 규칙 1·2: USD 월 가격이 명확한 값($숫자/mo, $숫자/user/mo)만 숫자로 바꾸고 나머지는 NaN. 첫 줄 손 검산 0.99 = clean.csv 0.99 |
| 범주 열 | citation_raw: object | citation: object | M04 정제 규칙 3: Source citations → Yes, 빈칸 → No. 첫 줄 손 검산 Yes = clean.csv Yes |
| 공백 | 미확인 | 미확인 | M04 정제 규칙 4: name은 앞뒤 공백만 정리 |
| 필수값 빈칸 | price_raw 빈칸 1 · citation_raw 빈칸 7 · name·detail_url 빈칸 미확인 | price 빈칸 0 · citation 빈칸 0 · name·detail_url 빈칸 미확인 | M04 정제 규칙 2·3·6: 빈 가격은 price NaN으로 두고 제외(0·평균 채움 없음), 빈 citation_raw는 No |
| detail_url 중복 | 0 | 0 | M04 처리 전후 확인 |
| 뺀 행 | — | 13행 | M04 처리 전후 확인: Free plan 8개, Open source 2개, 가격 원문 빈칸 1개, EUR 기간 미표시 1개, GBP 연 단위 1개 |
| 표본 3행 대조 | 앞 0 · 가운데 13 · 끝 26행, 이름·숫자·범주 9칸 모두 원문과 같음 | 미확인 | M03 판정 (상세 화면에서 확인) |

## M06 EDA 질문 1 · 분포

질문:
PDF AI의 USD 월 시작 가격(price)은 어느 가격대에 많이 몰려 있나?

축:
- 가로축: Price (USD)
- 세로축: Number of tools

구간 경계:
[0, 10, 20, 30, 40, 50]

구간 규칙:
- 왼쪽 끝 포함, 오른쪽 끝 미포함
- 마지막 40~50 구간만 오른쪽 끝 50 포함

구간:
- 0 이상 10 미만
- 10 이상 20 미만
- 20 이상 30 미만
- 30 이상 40 미만
- 40 이상 50 이하

결과
- 분석 대상 14개
- 가격 구간별 개수: [0,10) 8개 · [10,20) 5개 · [20,30) 0개 · [30,40) 0개 · [40,50] 1개
- 관찰: 가격 $0~10 구간이 8개로 가장 많음

## M07 EDA 질문 2 · 범주별 비교

질문:
출처 인용 기능(citation) 유무에 따라 PDF AI의 USD 월 시작 가격(price) 평균은 다른가?

축:
- 가로축: Citation support
- 세로축: Average price (USD)

범주 순서:
- Yes
- No

결과
- Citation Yes: 10개 · 평균 가격 $8.46
- Citation No: 4개 · 평균 가격 $20.75
- 관찰: 현재 표본에서 Citation No 평균 가격이 Yes보다 높게 나타남
- 한계: Citation No는 4개뿐이고 PDF.ai API $49가 포함되어 평균에 영향을 받으므로, Citation 여부 때문에 가격이 달라진다고 해석할 수 없음

## M09 비교 화면 뼈대

JSON 14개 = 화면 14개

| 카드 | 번호 | 이름 | 숫자 | 범주 | 화면과 같나 |
|---|---:|---|---:|---|---|
| 앞 | 0 | AI PDF Reader | 0.99 | Yes | 같음 ($0.99 · Yes) |
| 가운데 | 7 | ChatDOC | 8.99 | Yes | 같음 ($8.99 · Yes) |
| 끝 | 13 | Paperpal | 12.0 | No | 같음 ($12 · No) |

앞 카드 detail_url: https://www.itechguides.com/products/ai-pdf-reader/

「원래 화면 보기」(앞 카드) - 원래 상품 화면 열림

범위 카드 대조 - 조건 입력 없음 · 후보 비교는 목록만 있음 · 근거 설명 없음 → 다음 칸에서 조건 입력부터

## M10 조건 필터

선택 확장 문장 : 조건에 맞는 도구가 없을 때, 조건은 그대로 두고 예산만 올리면 얼마부터 · 출처 인용 조건만 풀면 몇 개인지 알려 준다

| 경우 | 조건 | 화면 개수 | data.json 따로 센 개수 | 같나 |
|---|---|---:|---:|---|
| 정상 | 예산 10 · Citation Yes | 8 | 8 | 같음 |
| 후보 1개 | 예산 10 · Citation No | 1 | 1 | 같음 |
| 후보 없음 | 예산 9 · Citation No | 0 | 0 | 같음 |

후보 1개 - pdfAssistant.ai · $9.99 · Citation No

후보 없음 안내 - 「현재 조건에 맞는 후보가 없습니다. 예산을 $9.99까지 올리면 후보가 생깁니다. 출처 인용 조건을 풀면 6개가 보입니다.」 - data.json을 따로 센 숫자와 같음

## M11 배포본 v1

근거 영역 문장

그림 1 관찰 - 가격 $0~10 구간이 8개로 가장 많음

그림 2 관찰 - 현재 표본에서 Citation No 평균 가격은 $20.75, Yes는 $8.46으로 나타남

한계 - Citation No는 4개뿐이고 $49 항목이 포함되어 평균에 영향을 받으므로, Citation 여부 때문에 가격이 달라진다고 해석할 수 없음

출처 - iTechGuides 「Best AI PDF Assistants in 2026: Researched & Ranked」 · 2026-09-28 수집 · USD 월 시작 가격으로 비교 가능한 14개

배포 주소 (Domains) :

짝 확인 (짝의 기기)
- 카드 :
- 후보 없음 (예산 9 · Citation No) :
- 그림 두 장 :

## M12 AI 기능 명세와 열쇠

올라갈 목록에 .env 없음 - .gitignore 에 .env 한 줄 확인

### M12 도전 - 같은 조건의 추천 일관성

- 같은 조건이면 같은 추천이 나와야 하나: 예
- 이유: 같은 예산 · Citation 조건과 같은 후보 목록인데 추천이 매번 바뀌면 결과를 비교하고 검증하기 어려움
- 다음 칸 프롬프트에 추가할 것: 전달한 후보의 name · price · citation만 사용하고, 같은 입력에서는 같은 기준으로 1개를 고르도록 요청

## M13 AI 추천 동작본

배포 주소 (Domains) : https://iny-pdf-compare.vercel.app

환경변수 GEMINI_API_KEY - Production 등록 · Redeploy 완료

| 조건 | AI에게 넘긴 후보 | 추천된 이름 | 후보 안? |
|---|---|---|---|
| 예산 10 · Citation Yes | 가격 낮은 순 최대 5개 | AI PDF Reader | 예 |
| 예산 10 · Citation No | 가격 낮은 순 최대 5개 | pdfAssistant.ai | 예 |

두 조건의 추천이 서로 다른가 : 예

후보 없음 (예산 9 · Citation No) - AI를 부르지 않고 M10 안내만 표시

같은 조건 반복 - 예산 10 · Citation Yes로 두 번 눌러도 AI PDF Reader로 동일

소스 보기에서 Gemini API 키 값 : 안 보임
.env 주소 직접 접근 : 404
/api/recommend.js 직접 접근 : 소스 코드 노출 안 됨

## M17 이벤트 도착

| 이벤트 | 미리보기 | DebugView | 누른 횟수 | 도착 횟수 |
|---|---|---|---|---|
| filter_candidates | 쪽지만 들어옴 | 태그 없음 | - | - |
| request_recommendation | 쪽지만 들어옴 | 태그 없음 | - | - |
| select_item | 실행됨 | 도착 · item_list_name : ai_recommendation | 2 | 2 |

게시한 버전 : 미니3 select_item 추가

## M18 짝 테스트

1. 예산에 10을 입력함
2. 출처 인용을 Yes로 바꾸고 [적용]을 누름 - 화면에서 눈에 띄는 변화가 없어 잠시 화면을 봄
3. 화면 아래 카드 목록을 보고 「원래 화면 보기」를 클릭한 뒤, 열린 외부 화면을 닫고 과제 문장을 다시 봄
4. 「이 조건으로 추천받기」를 누르고 추천 결과의 가격과 Citation 값을 보며 잠시 머문 뒤 추천 이유를 읽음
5. AI 추천 표시가 붙은 카드의 「원래 화면 보기」를 한 번 더 클릭하고 끝냄

짝이 끝냈나 : 예 - 끝났습니다
머문 자리 : 추천 결과 화면 - Citation의 뜻과 $0.99가 1달러 미만인지 확인하며 잠시 머묾

※ 결석으로 인해 이번 테스트는 혼자 사용자 역할로 대체 진행

### 더 해보기 - 휴대폰 테스트

1. 예산에 10을 입력하고 출처 인용을 Yes로 바꿈
2. [적용]을 세 번 눌렀지만 눈에 띄는 변화가 없어 반복해서 누름
3. 예산 입력칸을 누르자 화면이 확대되고 카드 일부가 오른쪽으로 잘려 보임
4. 「이 조건으로 추천받기」를 누름
5. 추천된 카드의 「원래 화면 보기」를 누르고 끝냄

컴퓨터와 다르게 보인 자리 :
- [적용] 후 변화가 잘 보이지 않아 같은 버튼을 세 번 누름
- 예산 입력칸을 누른 뒤 화면이 확대되어 카드 오른쪽이 잘려 보임

## M19 한 곳 고치기

|  | 바꾸기 전 (M18) | 바꾼 뒤 (M19) |
|---|---|---|
| 과제 | 월 10달러 안에서 출처를 인용할 수 있는 PDF AI 하나와 이유 찾기 | 같음 |
| 끝냈나 | 예 | 예 |
| 머문 자리 | Citation의 뜻과 $0.99가 1달러 미만인지 확인하며 잠시 머묾 | $0.99가 1달러 미만인지 확인하며 잠시 머묾 |
| 다시 볼 방법으로 본 것 | Citation 뜻을 따로 생각하며 멈춤 | 「출처 인용 기능을 지원합니다.」를 보고 멈추지 않음 |

한 사람 · 한 번의 결과

다음 개선 후보 : $0.99 표기에서 여전히 잠시 멈춤

### 더 해보기 - 이상한 값 확인

- 예산에 -5를 입력하고 [적용]을 누름
- 화면에 「예산은 0 이상의 숫자로 입력해 주세요」가 표시됨
- 잘못된 값과 수정 기준을 화면에서 바로 알려 주므로 추가 개선하지 않음
