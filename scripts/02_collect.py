# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path
# 상대 주소를 전체 주소로 바꾸기 위해 urljoin을 불러온다
from urllib.parse import urljoin
# 현재 시각을 기록하기 위해 datetime을 불러온다
from datetime import datetime
# 한국 시간대를 지정하기 위해 ZoneInfo를 불러온다
from zoneinfo import ZoneInfo

# 웹 페이지를 요청하기 위해 requests를 불러온다
import requests
# HTML을 해석하기 위해 BeautifulSoup을 불러온다
from bs4 import BeautifulSoup
# 표를 만들고 합치고 CSV로 저장하기 위해 pandas를 불러온다
import pandas as pd

# 수집할 목록 페이지 주소 목록 (다음 페이지가 없으므로 1페이지만 넣는다)
PAGE_URLS = ["https://www.itechguides.com/best/ai-pdf-assistants/"]
# 이 스크립트 파일 위치를 기준으로 ../data/raw.csv 경로를 만든다
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw.csv"
# 요청할 때 함께 보낼 브라우저 정보(User-Agent)
HEADERS = {"User-Agent": "Mozilla/5.0"}
# CSV 열 이름과 순서 (01_collect_p1.py와 같다)
COLUMNS = ["name", "price_raw", "citation_raw", "ocr_raw", "detail_url", "scraped_at"]


# 목록 페이지 하나를 요청해서 행 목록과 상태 코드를 돌려주는 함수
def collect_page(page_url):
    # 목록 페이지를 한 번만 요청한다 (30초가 지나면 중단)
    response = requests.get(page_url, headers=HEADERS, timeout=30)
    # 응답 상태 코드를 출력한다
    print("응답 상태 코드:", response.status_code)

    # 응답 헤더의 Content-Type 값을 가져온다 (없으면 빈 문자열)
    content_type = response.headers.get("Content-Type", "")
    # 헤더에 charset이 적혀 있지 않으면 본문 내용으로 추정한 인코딩을 쓴다
    if "charset" not in content_type.lower():
        # 추정한 인코딩으로 응답 인코딩을 설정한다
        response.encoding = response.apparent_encoding
    # 실제로 사용한 인코딩을 출력한다
    print("사용한 인코딩:", response.encoding)

    # 상태 코드가 200이 아니면 빈 행 목록을 돌려준다
    if response.status_code != 200:
        # 상태 코드와 빈 목록을 함께 돌려준다
        return response.status_code, []

    # 응답 HTML을 BeautifulSoup으로 해석한다
    soup = BeautifulSoup(response.text, "html.parser")
    # full ranking 영역(data-ax-surface="ranking"인 목록)을 찾는다
    ranking = soup.select_one('ol.td-list[data-ax-surface="ranking"]')
    # ranking 영역이 있으면 그 바로 아래 li.td-row만 고르고, 없으면 빈 목록으로 둔다
    rows = ranking.select(":scope > li.td-row") if ranking else []

    # 이 페이지의 모든 행에 똑같이 넣을 수집 시점을 한국 시간으로 기록한다
    scraped_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")

    # 수집한 행을 담을 빈 목록을 만든다
    records = []
    # ranking 영역의 항목을 하나씩 돈다
    for row in rows:
        # 도구 이름이 적힌 링크를 찾는다
        name_tag = row.select_one("a.td-name")
        # 가격 문구가 적힌 칸을 찾는다
        price_tag = row.select_one("span.td-rprice")
        # 특징 목록(Stand-out features)의 글자를 모두 모은다
        features = [li.get_text(strip=True) for li in row.select("ul.td-rspecs li")]
        # 한 행의 값을 사전으로 만든다
        record = {
            # 도구 이름 글자를 그대로 넣는다 (없으면 빈 문자열)
            "name": name_tag.get_text(strip=True) if name_tag else "",
            # 가격 문구 전체를 그대로 넣는다 (없으면 빈 문자열)
            "price_raw": price_tag.get_text(strip=True) if price_tag else "",
            # 특징 중 "Source citations" 글자가 있으면 그 글자를, 없으면 빈 문자열을 넣는다
            "citation_raw": next((f for f in features if f == "Source citations"), ""),
            # 특징 중 "Scanned PDF support" 글자가 있으면 그 글자를, 없으면 빈 문자열을 넣는다
            "ocr_raw": next((f for f in features if f == "Scanned PDF support"), ""),
            # 이름 링크의 href를 목록 주소 기준 전체 주소로 바꾼다 (없으면 빈 문자열)
            "detail_url": urljoin(page_url, name_tag["href"]) if name_tag and name_tag.get("href") else "",
            # 코드가 기록한 수집 시점을 넣는다
            "scraped_at": scraped_at,
        }
        # 완성한 행을 목록에 추가한다
        records.append(record)

    # 상태 코드와 행 목록을 함께 돌려준다
    return response.status_code, records


# 페이지별 표를 담을 빈 목록을 만든다
page_tables = []
# 목록 주소를 하나씩 돈다 (지금은 1페이지뿐이다)
for page_no, page_url in enumerate(PAGE_URLS, start=1):
    # 페이지 번호와 주소를 출력한다
    print(f"[{page_no}페이지] {page_url}")
    # 페이지를 요청하고 행을 뽑는다
    status, records = collect_page(page_url)
    # 이 페이지의 행 수를 출력한다
    print(f"{page_no}페이지 행 수:", len(records))
    # 상태 코드가 200이 아니거나 행이 0개면 CSV를 만들지 않고 끝낸다
    if status != 200 or len(records) == 0:
        # 중단 이유를 출력한다
        print("상태 코드가 200이 아니거나 0행이므로 raw.csv를 만들지 않습니다.")
        # 프로그램을 종료한다
        raise SystemExit(1)
    # 이 페이지의 행을 열 순서를 고정한 표로 만들어 목록에 넣는다
    page_tables.append(pd.DataFrame(records, columns=COLUMNS))

# 페이지별 표를 위아래로 합치고 행 번호를 0부터 다시 매긴다
df = pd.concat(page_tables, ignore_index=True)

# 저장할 폴더가 없으면 만든다
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
# 합친 표를 CSV로 저장한다 (행 번호 없이, 엑셀에서 한글이 안 깨지는 utf-8-sig로)
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
# 저장한 위치를 출력한다
print("저장 완료:", OUTPUT_PATH)

# 합계 행 수를 출력한다
print("합계 행 수:", len(df))
# 서로 다른 detail_url 개수를 출력한다
print("서로 다른 detail_url 개수:", df["detail_url"].nunique())

# 표본 행 번호를 정한다: 첫 행, 가운데 행(전체 행 수 // 2), 마지막 행
sample_positions = [0, len(df) // 2, len(df) - 1]
# 표본 행을 하나씩 돈다
for pos in sample_positions:
    # 행 번호를 출력한다
    print(f"--- 표본 행 {pos} ---")
    # 그 행의 모든 열을 "열 이름: 값" 형태로 출력한다
    for col in COLUMNS:
        # 값을 repr로 감싸 빈 문자열도 눈에 보이게 출력한다
        print(f"{col}: {df.loc[pos, col]!r}")
