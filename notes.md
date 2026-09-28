# 미니3: BuildWise AI

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

## M07 EDA 질문 2 · 범주별 비교

질문:
출처 인용 기능(citation) 유무에 따라 PDF AI의 USD 월 시작 가격(price) 평균은 다른가?

축:
- 가로축: Citation support
- 세로축: Average price (USD)

범주 순서:
- Yes
- No
