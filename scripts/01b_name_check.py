# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# HTML을 해석하기 위해 BeautifulSoup을 불러온다
from bs4 import BeautifulSoup
# CSV를 읽기 위해 pandas를 불러온다
import pandas as pd

# 이 스크립트 위치를 기준으로 data 폴더 경로를 만든다
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# 이미 받아 둔 목록 HTML 파일 경로 (페이지를 다시 요청하지 않는다)
HTML_PATH = DATA_DIR / "raw_p1.html"
# 수집해 둔 CSV 파일 경로 (읽기만 한다)
CSV_PATH = DATA_DIR / "raw_p1.csv"

# 저장된 HTML 파일을 utf-8로 읽는다
html = HTML_PATH.read_text(encoding="utf-8")
# 읽은 HTML을 BeautifulSoup으로 해석한다
soup = BeautifulSoup(html, "html.parser")
# full ranking 영역 바로 아래의 li.td-row 항목만 고른다
rows = soup.select('ol.td-list[data-ax-surface="ranking"] > li.td-row')

# CSV를 읽는다 (빈 칸을 NaN이 아닌 빈 문자열로, 모든 값을 글자로)
df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", keep_default_na=False, dtype=str)

# HTML 항목 수와 CSV 행 수를 출력한다
print("HTML 항목 수:", len(rows), "/ CSV 행 수:", len(df))

# 이름이 서로 다른 항목을 담을 빈 목록을 만든다
mismatches = []
# HTML 항목과 CSV 행을 순서대로 짝지어 돈다
for i, (row, csv_name) in enumerate(zip(rows, df["name"])):
    # 화면에 표시되는 이름 링크를 찾는다
    name_tag = row.select_one("a.td-name")
    # 링크 안의 보이는 글자를 앞뒤 공백만 빼고 가져온다 (없으면 빈 문자열)
    shown_name = name_tag.get_text(strip=True) if name_tag else ""
    # 보이는 이름과 CSV의 name 값이 다르면 기록한다
    if shown_name != csv_name:
        # 행 번호, 보이는 이름, CSV 이름을 함께 남긴다
        mismatches.append((i, shown_name, csv_name))

# 서로 다른 항목을 하나씩 출력한다
for i, shown_name, csv_name in mismatches:
    # 어떤 행에서 어떻게 다른지 보여 준다
    print(f"{i}행: 화면 '{shown_name}' / CSV '{csv_name}'")

# 서로 다른 항목 수를 정해진 형태로 출력한다
print(f"잘려 보이는 이름: {len(mismatches)}개")
