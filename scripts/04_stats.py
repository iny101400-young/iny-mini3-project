# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# CSV를 읽고 통계를 계산하기 위해 pandas를 불러온다
import pandas as pd

# 이 스크립트 위치를 기준으로 data/clean.csv 경로를 만든다 (읽기만 한다)
CLEAN_PATH = Path(__file__).resolve().parent.parent / "data" / "clean.csv"

# clean.csv를 읽는다 (빈칸은 빈 문자열 그대로, price는 숫자로 읽힌다)
df = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig", keep_default_na=False)
# price 열을 따로 꺼낸다
price = df["price"]

# price 값의 개수를 센다 (NaN은 세지 않는다)
count = int(price.count())
# 가장 작은 가격을 구한다
min_price = price.min()
# 가장 큰 가격을 구한다
max_price = price.max()
# 평균 가격을 구한다
mean_price = price.mean()
# 중앙값을 구한다
median_price = price.median()

# 통계 표를 항목과 값 두 열로 만든다
stats = pd.DataFrame({
    # 항목 이름 목록
    "항목": ["개수", "최소", "최대", "평균", "중앙값"],
    # 값 목록 (평균만 소수 둘째 자리, 중앙값은 계산값 그대로)
    "값": [count, min_price, max_price, f"{mean_price:.2f}", median_price],
})
# 통계 표 제목을 출력한다
print("=== price 통계 ===")
# 통계 표를 행 번호 없이 출력한다
print(stats.to_string(index=False))
# 빈 줄을 넣는다
print()

# 최소값과 같은 가격을 가진 행을 모두 고른다
min_rows = df.loc[price == min_price, ["name", "price", "citation"]]
# 최소값 행 제목을 출력한다
print("=== 최소값 행 ===")
# 최소값 행을 출력한다
print(min_rows.to_string())
# 빈 줄을 넣는다
print()

# 최대값과 같은 가격을 가진 행을 모두 고른다
max_rows = df.loc[price == max_price, ["name", "price", "citation"]]
# 최대값 행 제목을 출력한다
print("=== 최대값 행 ===")
# 최대값 행을 출력한다
print(max_rows.to_string())
# 빈 줄을 넣는다
print()

# price 개수와 전체 행 수를 나란히 출력하고 같은지 적는다
print(f"price 개수 {count} / clean.csv 전체 행 수 {len(df)} →", "같음" if count == len(df) else "다름")

# 평균과 중앙값을 비교할 문장을 정한다
if mean_price > median_price:
    # 평균이 더 크면 그 사실을 적는다
    compare = "평균이 중앙값보다 큼"
# 중앙값이 더 크면
elif mean_price < median_price:
    # 중앙값이 더 크다고 적는다
    compare = "중앙값이 평균보다 큼"
# 둘이 같으면
else:
    # 같다고 적는다
    compare = "평균과 중앙값이 같음"
# 비교 결과를 한 줄로 출력한다
print(f"평균 {mean_price:.2f} / 중앙값 {median_price} → {compare}")
