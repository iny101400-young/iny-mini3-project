# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path
# JSON 파일을 쓰고 읽기 위해 json 모듈을 불러온다
import json

# CSV를 읽기 위해 pandas를 불러온다
import pandas as pd

# 이 스크립트 위치를 기준으로 data 폴더 경로를 만든다
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# 읽기만 할 clean.csv 경로
CLEAN_PATH = DATA_DIR / "clean.csv"
# 새로 저장할 data.json 경로
JSON_PATH = DATA_DIR / "data.json"
# JSON에 넣을 열 네 개 (이 순서대로)
COLUMNS = ["name", "price", "citation", "detail_url"]

# clean.csv를 읽는다 (빈칸은 빈 문자열 그대로, price는 숫자로 읽힌다)
df = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig", keep_default_na=False)
# 네 열만 고른다
subset = df[COLUMNS]
# 한 행을 사전 하나로 바꾼 records 목록을 만든다 (price는 숫자 그대로)
records = subset.to_dict(orient="records")

# data.json을 utf-8로 연다
with open(JSON_PATH, "w", encoding="utf-8") as f:
    # 한글을 글자 그대로(ensure_ascii=False), 들여쓰기 2칸으로 저장한다
    json.dump(records, f, ensure_ascii=False, indent=2)
# 저장 위치를 출력한다
print("저장 완료:", JSON_PATH)
# 빈 줄을 넣는다
print()

# 저장한 data.json을 다시 읽는다
with open(JSON_PATH, encoding="utf-8") as f:
    # JSON 목록을 파이썬 목록으로 불러온다
    loaded = json.load(f)

# 1. data.json 항목 수를 출력한다
print("1. data.json 항목 수:", len(loaded))
# 2. clean.csv 행 수를 출력한다
print("2. clean.csv 행 수:", len(df))
# 3. 두 숫자가 같은지 출력한다
print("3. 항목 수와 행 수:", "같음" if len(loaded) == len(df) else "다름")
# 빈 줄을 넣는다
print()

# data.json 첫 항목을 꺼낸다
json_first = loaded[0]
# clean.csv 첫 행의 네 값을 사전으로 꺼낸다
csv_first = subset.iloc[0].to_dict()

# 4. data.json 첫 항목 제목을 출력한다
print("4. data.json 첫 항목")
# 네 열을 하나씩 돈다
for col in COLUMNS:
    # 값과 파이썬 자료형을 함께 출력한다 (price가 숫자인지 보이게)
    print(f"   {col}: {json_first[col]!r} ({type(json_first[col]).__name__})")
# 5. clean.csv 첫 행 제목을 출력한다
print("5. clean.csv 첫 행")
# 네 열을 하나씩 돈다
for col in COLUMNS:
    # 값을 출력한다
    print(f"   {col}: {csv_first[col]!r}")
# 빈 줄을 넣는다
print()

# 네 값이 각각 같은지 확인한다
matches = {col: json_first[col] == csv_first[col] for col in COLUMNS}
# 열마다 같음/다름을 출력한다
print("6. 첫 항목 값 비교:", ", ".join(f"{col} {'같음' if ok else '다름'}" for col, ok in matches.items()))
# 네 값이 모두 같은지 한 줄로 출력한다
print("   네 값 모두:", "일치" if all(matches.values()) else "불일치")
