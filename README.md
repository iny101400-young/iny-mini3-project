# PDF AI 비교 도우미

## 1. 무엇을 하나

PDF AI 도구 14개의 USD 월 시작 가격과 출처 인용(citation) 여부를 카드로 비교하는 서비스입니다.
예산($)과 출처 인용 조건을 넣어 후보를 줄이고, 「이 조건으로 추천받기」로 AI 추천을 받아 하나를 더 살펴볼 수 있습니다.

## 2. 배포 주소

https://iny-pdf-compare.vercel.app

## 3. 데이터

| 항목 | 내용 |
|---|---|
| 출처 | iTechGuides 「Best AI PDF Assistants in 2026: Researched & Ranked」 목록 페이지 (https://www.itechguides.com/best/ai-pdf-assistants/) 1페이지 |
| 수집 시점 | 2026-09-28 |
| 원본 행 수 | 27행 (`data/raw_p1.csv`) |
| 정제 후 행 수 | 14행 (`data/clean.csv`, `data/data.json`) |
| 뺀 행 | 13행: Free plan 8개 · Open source 2개 · 가격 원문 빈칸 1개 · EUR 기간 미표시 1개 · GBP 연 단위 1개 |

정제한 열

- `price`: `price_raw`에서 USD 월 가격이 명확한 값(`$숫자/mo`, `$숫자/user/mo`)만 숫자로 바꿨습니다(object → float64). 못 바꾼 값에 0이나 평균값을 넣지 않고 그 행을 뺐습니다. 환율 환산은 하지 않았습니다.
- `citation`: `citation_raw`의 `Source citations`는 `Yes`, 빈칸은 `No`로 바꿨습니다.
- `name`: 앞뒤 공백만 정리했습니다.

웹 화면이 읽는 `data/data.json`의 각 항목은 `name` · `price` · `citation` · `detail_url` 네 값입니다.

## 4. AI 추천

- Google Gemini(`gemini-3.5-flash-lite`)를 사용합니다.
- 브라우저는 Gemini를 직접 부르지 않습니다. 「이 조건으로 추천받기」를 누르면 브라우저가 조건(`budget`, `citation`)만 `/api/recommend` 서버 함수로 보냅니다.
- 서버는 `data/data.json`에서 조건에 맞는 후보를 다시 골라 가격 낮은 순(같은 가격이면 이름 순)으로 최대 5개만 Gemini에 넘깁니다. 넘기는 후보 값은 `name` / `price` / `citation` 세 가지입니다.
- Gemini에게서 받는 값은 추천 이름 1개와 이유 2줄입니다. 이유는 각 40자 이하로 제한합니다.
- 서버가 받은 결과를 다시 검증합니다.
  - 추천 이름이 넘긴 후보 안에 글자 그대로 있어야 합니다.
  - 이유 속 숫자는 모두 후보의 `price` 중 하나여야 하고, 추천한 후보의 `price`가 들어 있어야 합니다.
  - 이유 속 `Yes` / `No`에 추천한 후보의 `citation`이 들어 있어야 합니다.
  - 이유가 40자를 넘거나 검증을 통과하지 못하면 화면에 「추천을 확인하지 못했습니다」를 보여 줍니다.
- 후보가 0개면 Gemini를 부르지 않고 조건 필터의 후보 없음 안내만 보여 줍니다.
- 호출 실패나 요청 한도 초과, 20초 안에 답이 없는 경우에는 「잠시 뒤 다시 눌러 주세요」를 보여 줍니다.

API 열쇠는 Vercel 환경변수 `GEMINI_API_KEY`에 둡니다.

## 5. 확인한 것

조건 필터: 화면 개수와 `data/data.json`을 따로 센 개수를 비교했습니다.

| 경우 | 조건 | 화면 개수 | 따로 센 개수 | 같나 |
|---|---|---:|---:|---|
| 정상 | 예산 10 · Citation Yes | 8 | 8 | 같음 |
| 후보 1개 | 예산 10 · Citation No | 1 | 1 | 같음 (pdfAssistant.ai · $9.99 · No) |
| 후보 없음 | 예산 9 · Citation No | 0 | 0 | 같음 |

후보 없음 안내 「현재 조건에 맞는 후보가 없습니다. 예산을 $9.99까지 올리면 후보가 생깁니다. 출처 인용 조건을 풀면 6개가 보입니다.」의 숫자도 `data/data.json`을 따로 센 숫자와 같았습니다.

AI 추천: 추천 이름과 이유 속 가격·Citation 값을 `data/data.json`과 비교했습니다.

| 경우 | 조건 | 후보 수 | AI 불렀나 | 추천 이름 | 이유 속 값 | data.json 값 | 같나 | 후보 안? | 지어낸 말 |
|---|---|---:|---|---|---|---|---|---|---|
| 정상 | 예산 10 · Citation Yes | 8 | 예 | AI PDF Reader | $0.99 · Yes | 0.99 · Yes | 같음 | 예 | 없음 |
| 후보 1개 | 예산 10 · Citation No | 1 | 예 | pdfAssistant.ai | $9.99 · No | 9.99 · No | 같음 | 예 | 없음 |
| 후보 없음 | 예산 9 · Citation No | 0 | 아니오 (M10 안내만) | — | — | — | — | — | — |

- 틀린 값은 없었습니다. 두 추천 모두 이유 속 가격과 Citation 값이 `data/data.json`과 같았습니다. 추천 이름도 각 조건의 후보 안에 있었고, 후보 표에 없는 정보는 나오지 않았습니다.
- 후보 없음(예산 9 · Citation No)에서는 AI를 부르지 않고 후보 없음 안내만 보였습니다.
- 정상 조건(예산 10 · Citation Yes)을 3번 눌렀을 때 3번 모두 AI PDF Reader · $0.99 · Yes가 나왔습니다. 3번 모두 후보 안이었고, 값이 일치했으며, 지어낸 말이 없었습니다.
- 페이지 소스에서 API 열쇠 값이 보이지 않았습니다. `.env` 주소로 직접 접근하면 404가 나왔고, `/api/recommend.js`로 직접 접근해도 소스 코드가 노출되지 않았습니다.

## 6. 한계

- 데이터는 iTechGuides 목록 페이지 한 곳의 1페이지에서 2026-09-28에 수집한 현재 표본입니다.
- 원본 27개 중 USD 월 시작 가격으로 비교할 수 있는 14개만 씁니다. Free plan, Open source, 가격 빈칸, EUR·GBP 가격은 빠져 있습니다.
- `citation`의 `No`는 '지원하지 않음'이라는 뜻이 아닙니다. 원문에 Source citations 표시가 확인되지 않은 경우입니다.
- 현재 표본에서 Citation No 평균 가격($20.75)이 Yes($8.46)보다 높게 나타나지만, No는 4개뿐이고 $49 항목(PDF.ai API)이 평균에 영향을 줍니다. 가격과 Citation의 차이는 관찰일 뿐이며, Citation 여부 때문에 가격이 달라진다고 해석할 수 없습니다.
- AI 추천은 외부 서비스인 Gemini API를 부르므로 그 서비스의 상태나 사용 한도에 따라 추천이 나오지 않을 수 있습니다.
