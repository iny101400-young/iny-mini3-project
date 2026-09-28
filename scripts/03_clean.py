# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path
# 가격 문구에서 숫자를 찾기 위해 정규식 모듈 re를 불러온다
import re

# 표를 읽고 정제하고 저장하기 위해 pandas를 불러온다
import pandas as pd

# 이 스크립트 위치를 기준으로 data 폴더 경로를 만든다
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# 읽기만 할 원본 CSV 경로
RAW_PATH = DATA_DIR / "raw.csv"
# 정제 결과를 저장할 CSV 경로
CLEAN_PATH = DATA_DIR / "clean.csv"
# 정제 규칙을 세울 때 손으로 센 예상 행 수
EXPECTED_ROWS = 14

# "$숫자/mo" 또는 "$숫자/user/mo" 모양만 찾는 정규식 (숫자 부분만 따로 잡는다)
USD_MONTHLY = re.compile(r"\$(\d+(?:\.\d+)?)/(?:user/)?mo\b")
# 정제 후 열 순서 (price_raw 옆에 price, citation_raw 옆에 citation)
CLEAN_COLUMNS = ["name", "price_raw", "price", "citation_raw", "citation", "ocr_raw", "detail_url", "scraped_at"]


# 가격 원문에서 USD 월 가격 숫자를 꺼내는 함수 (못 꺼내면 NaN)
def parse_price(text):
    # 정규식으로 "$숫자/mo" 또는 "$숫자/user/mo" 부분을 찾는다
    match = USD_MONTHLY.search(text)
    # 찾았으면 숫자 부분만 실수로 바꿔 돌려주고, 못 찾았으면 NaN을 돌려준다
    return float(match.group(1)) if match else float("nan")


# 가격을 못 바꾼 이유를 설명하는 함수
def price_reason(text):
    # 원문이 빈칸이면 빈칸이라고 알려준다
    if text == "":
        # 빈칸 사유를 돌려준다
        return "가격 원문 빈칸"
    # 원문이 "Free plan" 하나뿐이면 유료 금액이 없다고 알려준다
    if text == "Free plan":
        # 무료 요금제만 있다는 사유를 돌려준다
        return "Free plan: 유료 월 금액 없음"
    # 원문이 "Open source"이면 가격 문구가 아니라고 알려준다
    if text == "Open source":
        # 오픈 소스라는 사유를 돌려준다
        return "Open source: 가격 금액 없음"
    # 여러 사유를 모을 빈 목록을 만든다
    parts = []
    # 파운드 기호가 있으면 USD가 아니라고 적는다
    if "£" in text:
        # GBP 통화 사유를 추가한다
        parts.append("통화 GBP(£)")
    # 유로 기호가 있으면 USD가 아니라고 적는다
    if "€" in text:
        # EUR 통화 사유를 추가한다
        parts.append("통화 EUR(€)")
    # 연 과금 표시가 있으면 월 가격이 아니라고 적는다
    if "/yr" in text:
        # 연 과금 사유를 추가한다
        parts.append("과금 주기 /yr")
    # /mo도 /yr도 없으면 기간이 적혀 있지 않다고 적는다
    elif "/mo" not in text:
        # 기간 미표시 사유를 추가한다
        parts.append("과금 주기 미표시")
    # 모은 사유가 있으면 이어 붙여 돌려주고, 없으면 일반 사유를 돌려준다
    return ", ".join(parts) if parts else "USD 월 가격 형식 아님"


# 표의 빈칸 수를 열마다 세는 함수 (빈 문자열과 NaN을 모두 빈칸으로 본다)
def blank_counts(df):
    # 열마다 NaN이거나 앞뒤 공백을 뺀 글자가 비어 있는 칸의 수를 센다
    return {col: int((df[col].isna() | (df[col].astype(str).str.strip() == "")).sum()) for col in df.columns}


# 처리 전/후 요약을 출력하는 함수
def print_summary(title, df):
    # 요약 제목을 출력한다
    print(f"=== {title} ===")
    # 행 수를 출력한다
    print("행 수:", len(df))
    # 확인할 열 이름을 하나씩 돈다
    for col in ["price_raw", "price", "citation_raw", "citation"]:
        # 열이 있으면 dtype을, 없으면 (열 없음)을 출력한다
        print(f"{col} dtype:", df[col].dtype if col in df.columns else "(열 없음)")
    # 열마다 빈칸 수를 출력한다
    print("빈칸 수:", blank_counts(df))
    # detail_url 중복 행 수를 출력한다
    print("detail_url 중복 수:", int(df["detail_url"].duplicated().sum()))
    # 요약 사이에 빈 줄을 넣는다
    print()


# 원본 CSV를 모든 값 글자로, 빈칸은 빈 문자열 그대로 읽는다 (파일은 수정하지 않는다)
raw = pd.read_csv(RAW_PATH, encoding="utf-8-sig", dtype=str, keep_default_na=False)
# 처리 전 요약을 출력한다
print_summary("처리 전 (raw.csv)", raw)

# 원본을 건드리지 않도록 복사본을 만들어 정제한다
df = raw.copy()
# name은 앞뒤 공백만 정리한다
df["name"] = df["name"].str.strip()
# price_raw에서 USD 월 가격 숫자만 꺼내 price 열을 만든다
df["price"] = df["price_raw"].map(parse_price)
# citation_raw를 Yes/No로 바꿔 citation 열을 만든다 (예상 밖 값은 NaN으로 남는다)
df["citation"] = df["citation_raw"].map({"Source citations": "Yes", "": "No"})
# 열 순서를 정리한다 (원본 열은 하나도 지우지 않는다)
df = df[CLEAN_COLUMNS]

# citation으로 못 바꾼 예상 밖 값이 있으면 알려준다
if df["citation"].isna().any():
    # 예상 밖 citation_raw 값을 출력한다
    print("citation으로 못 바꾼 값:", df.loc[df["citation"].isna(), "citation_raw"].unique().tolist())

# 가격을 숫자로 못 바꾼 행을 먼저 출력한다
print("=== price를 숫자로 못 바꾼 행 (price = NaN) ===")
# price가 NaN인 행을 하나씩 돈다
for idx, row in df[df["price"].isna()].iterrows():
    # 행 번호, 이름, 가격 원문, 제외 사유를 출력한다
    print(f"{idx}행 | {row['name']} | {row['price_raw']!r} | {price_reason(row['price_raw'])}")
# 목록 끝에 빈 줄을 넣는다
print()

# 행 번호별 제외 사유를 모을 사전을 만든다
exclude = {}
# 표의 행을 하나씩 돈다
for idx, row in df.iterrows():
    # 이 행의 제외 사유를 모을 빈 목록을 만든다
    reasons = []
    # price가 NaN이면 사유를 추가한다
    if pd.isna(row["price"]):
        # 가격 사유를 추가한다
        reasons.append("price NaN (" + price_reason(row["price_raw"]) + ")")
    # name이 빈칸이면 사유를 추가한다
    if row["name"] == "":
        # 이름 빈칸 사유를 추가한다
        reasons.append("name 빈칸")
    # detail_url이 빈칸이면 사유를 추가한다
    if row["detail_url"].strip() == "":
        # 주소 빈칸 사유를 추가한다
        reasons.append("detail_url 빈칸")
    # 사유가 하나라도 있으면 사전에 기록한다
    if reasons:
        # 행 번호에 사유 목록을 연결한다
        exclude[idx] = reasons

# 앞에서 제외되지 않은 행만 남긴다
kept = df.drop(index=list(exclude))
# 남은 행 중 detail_url이 앞 행과 겹치는 행을 찾는다 (첫 행은 남긴다)
dup_mask = kept["detail_url"].duplicated(keep="first")
# 겹치는 행을 하나씩 돈다
for idx in kept.index[dup_mask]:
    # 중복 사유를 기록한다
    exclude[idx] = ["detail_url 중복 (첫 행만 남김)"]
# 중복 행까지 뺀 최종 표를 만들고 행 번호를 0부터 다시 매긴다
clean = kept[~dup_mask].reset_index(drop=True)

# 제외된 행과 사유를 출력한다
print(f"=== 제외된 행 ({len(exclude)}개) ===")
# 제외된 행을 행 번호 순서대로 돈다
for idx in sorted(exclude):
    # 행 번호, 이름, 사유를 출력한다
    print(f"{idx}행 | {df.loc[idx, 'name']} | {' / '.join(exclude[idx])}")
# 목록 끝에 빈 줄을 넣는다
print()

# 정제한 표를 clean.csv로 저장한다 (행 번호 없이, utf-8-sig로)
clean.to_csv(CLEAN_PATH, index=False, encoding="utf-8-sig")
# 저장 위치를 출력한다
print("저장 완료:", CLEAN_PATH)
# 빈 줄을 넣는다
print()

# 처리 후 요약을 출력한다
print_summary("처리 후 (clean 표)", clean)

# 저장한 clean.csv를 다시 읽어 첫 행을 확인한다 (빈칸은 빈 문자열 그대로)
saved = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig", keep_default_na=False)
# 첫 행 제목을 출력한다
print("=== clean.csv 첫 행 ===")
# 확인할 열을 하나씩 돈다
for col in ["name", "price_raw", "price", "citation_raw", "citation"]:
    # 열 이름과 값을 출력한다 (repr로 글자/숫자 구분이 보이게)
    print(f"{col}: {saved.loc[0, col]!r}")
# 빈 줄을 넣는다
print()

# 예상 행 수와 실제 행 수를 비교한다
print(f"예상 {EXPECTED_ROWS}행 / 실제 clean.csv {len(saved)}행 →", "같음" if len(saved) == EXPECTED_ROWS else "다름")
