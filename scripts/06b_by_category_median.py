# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# 화면 창 없이 파일로만 그림을 저장하도록 matplotlib를 불러온다
import matplotlib
# 백엔드를 Agg(파일 저장 전용)로 설정한다
matplotlib.use("Agg")
# 그래프를 그리기 위해 pyplot을 불러온다
import matplotlib.pyplot as plt
# CSV를 읽고 그룹별로 계산하기 위해 pandas를 불러온다
import pandas as pd

# 프로젝트 폴더 경로를 만든다 (scripts 폴더의 한 단계 위)
PROJECT_DIR = Path(__file__).resolve().parent.parent
# 읽기만 할 clean.csv 경로
CLEAN_PATH = PROJECT_DIR / "data" / "clean.csv"
# 새로 저장할 그림 경로 (기존 by_category.png와 다른 이름)
CHART_PATH = PROJECT_DIR / "charts" / "by_category_median.png"
# 범주 순서 (반드시 Yes 먼저, No 다음)
ORDER = ["Yes", "No"]
# 막대 색 (초록색 단일 색)
BAR_COLOR = "#008300"
# 그림 바탕 색 (앞 그래프들과 같은 흰 배경)
SURFACE = "#fcfcfb"
# 본문 글자 색
TEXT_PRIMARY = "#0b0b0b"
# 보조 글자 색
TEXT_SECONDARY = "#52514e"

# 기존 그림들을 덮어쓰지 않도록 저장 이름을 한 번 더 확인한다
assert CHART_PATH.name not in ("by_category.png", "hist.png", "hist_half.png")

# clean.csv를 읽는다 (빈칸은 빈 문자열 그대로, 파일은 수정하지 않는다)
df = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig", keep_default_na=False)
# 전체 행 수를 센다
n_total = len(df)

# citation별로 price의 개수·평균·중앙값을 구하고 범주 순서를 Yes, No로 맞춘다
groups = df.groupby("citation")["price"].agg(["count", "mean", "median"]).reindex(ORDER)

# 그림과 축을 만든다 (by_category.png와 같은 가로 6인치, 세로 5인치)
fig, ax = plt.subplots(figsize=(6, 5), facecolor=SURFACE)
# 축 안쪽 바탕 색을 정한다
ax.set_facecolor(SURFACE)
# 범주별 중앙값 막대를 그린다 (막대 폭 0.5)
bars = ax.bar(ORDER, groups["median"], color=BAR_COLOR, width=0.5)

# 막대마다 위에 중앙값과 개수를 두 줄로 적는다
for bar, (label, row) in zip(bars, groups.iterrows()):
    # 막대 가운데 위에 "$중앙값" 과 "n=개수"를 쓴다
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2, f"${row['median']:.2f}\nn={int(row['count'])}",
            ha="center", va="bottom", color=TEXT_PRIMARY, fontsize=11)

# 제목을 영어로 적는다
ax.set_title(f"Median monthly price by citation support (n = {n_total})", color=TEXT_PRIMARY, fontsize=12, loc="left")
# 가로축 이름을 적는다
ax.set_xlabel("Citation support", color=TEXT_SECONDARY)
# 세로축 이름을 적는다
ax.set_ylabel("Median price (USD)", color=TEXT_SECONDARY)
# 세로축 위쪽에 두 줄 글자가 들어갈 여유를 둔다
ax.set_ylim(0, groups["median"].max() * 1.3)
# 눈금 글자 색을 보조 색으로 정한다
ax.tick_params(colors=TEXT_SECONDARY)
# 가로 방향 보조선을 옅게 깐다
ax.grid(axis="y", color="#e4e3df", linewidth=0.8)
# 보조선을 막대 뒤에 그린다
ax.set_axisbelow(True)
# 위쪽·오른쪽 테두리를 없앤다
ax.spines[["top", "right"]].set_visible(False)
# 왼쪽·아래쪽 테두리를 옅게 만든다
ax.spines[["left", "bottom"]].set_color("#c9c8c3")

# 여백을 정리한다
fig.tight_layout()
# 그림을 새 PNG 파일로만 저장한다 (plt.show는 쓰지 않는다)
fig.savefig(CHART_PATH, dpi=150, facecolor=SURFACE)
# 저장 위치를 출력한다
print("저장 완료:", CHART_PATH)
# 빈 줄을 넣는다
print()

# 평균·중앙값 표 머리를 출력한다
print("| citation | 평균 | 중앙값 |")
# 표 구분선을 출력한다 (숫자 열은 오른쪽 정렬)
print("|---|---:|---:|")
# 범주 순서대로 한 줄씩 출력한다
for label, row in groups.iterrows():
    # 평균과 중앙값을 소수 둘째 자리로 출력한다
    print(f"| {label} | {row['mean']:.2f} | {row['median']:.2f} |")
# 빈 줄을 넣는다
print()


# 두 그룹 중 더 높은 쪽을 알려 주는 함수
def higher(col):
    # Yes 값과 No 값을 꺼낸다
    yes, no = groups.loc["Yes", col], groups.loc["No", col]
    # 더 큰 쪽 이름을 돌려주고, 같으면 "같음"을 돌려준다
    return "Yes" if yes > no else "No" if no > yes else "같음"


# 평균 기준으로 더 높은 그룹을 구한다
mean_high = higher("mean")
# 중앙값 기준으로 더 높은 그룹을 구한다
median_high = higher("median")
# 1. 평균 기준 결과를 출력한다
print(f"1. 평균 기준 더 높은 그룹: {mean_high} (Yes {groups.loc['Yes', 'mean']:.2f} / No {groups.loc['No', 'mean']:.2f})")
# 2. 중앙값 기준 결과를 출력한다
print(f"2. 중앙값 기준 더 높은 그룹: {median_high} (Yes {groups.loc['Yes', 'median']:.2f} / No {groups.loc['No', 'median']:.2f})")
# 3. 두 기준에서 순서가 바뀌었는지 출력한다
print("3. 평균과 중앙값의 그룹 순서:", "그대로" if mean_high == median_high else "바뀜")

# price가 가장 큰 행을 모두 고른다
max_rows = df.loc[df["price"] == df["price"].max(), ["name", "price", "citation"]]
# 4. 최댓값 행의 이름·가격·그룹을 출력한다
for _, row in max_rows.iterrows():
    # 이름, 가격, citation 그룹을 한 줄로 출력한다
    print(f"4. price 최댓값 {row['price']} → {row['name']} / citation 그룹: {row['citation']}")
