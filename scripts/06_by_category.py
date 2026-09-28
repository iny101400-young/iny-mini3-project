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
# 새로 저장할 그림 경로
CHART_PATH = PROJECT_DIR / "charts" / "by_category.png"
# 범주 순서 (반드시 Yes 먼저, No 다음)
ORDER = ["Yes", "No"]
# 막대 색 (주황색 단일 색)
BAR_COLOR = "#eb6834"
# 그림 바탕 색
SURFACE = "#fcfcfb"
# 본문 글자 색
TEXT_PRIMARY = "#0b0b0b"
# 보조 글자 색
TEXT_SECONDARY = "#52514e"

# 기존 히스토그램을 덮어쓰지 않도록 저장 이름을 한 번 더 확인한다
assert CHART_PATH.name not in ("hist.png", "hist_half.png")

# clean.csv를 읽는다 (빈칸은 빈 문자열 그대로, 파일은 수정하지 않는다)
df = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig", keep_default_na=False)
# 전체 행 수를 센다
n_total = len(df)

# citation별로 price의 개수·합·평균을 구하고 범주 순서를 Yes, No로 맞춘다
groups = df.groupby("citation")["price"].agg(["count", "sum", "mean"]).reindex(ORDER)

# 그림과 축을 만든다 (가로 6인치, 세로 5인치)
fig, ax = plt.subplots(figsize=(6, 5), facecolor=SURFACE)
# 축 안쪽 바탕 색을 정한다
ax.set_facecolor(SURFACE)
# 범주별 평균 막대를 그린다 (막대 폭은 0.5로 가늘게)
bars = ax.bar(ORDER, groups["mean"], color=BAR_COLOR, width=0.5)

# 막대마다 위에 평균과 개수를 두 줄로 적는다
for bar, (label, row) in zip(bars, groups.iterrows()):
    # 막대 가운데 위에 "$평균" 과 "n=개수"를 쓴다
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, f"${row['mean']:.2f}\nn={int(row['count'])}",
            ha="center", va="bottom", color=TEXT_PRIMARY, fontsize=11)

# 제목을 영어로 적는다
ax.set_title(f"Average monthly price by citation support (n = {n_total})", color=TEXT_PRIMARY, fontsize=12, loc="left")
# 가로축 이름을 적는다
ax.set_xlabel("Citation support", color=TEXT_SECONDARY)
# 세로축 이름을 적는다
ax.set_ylabel("Average price (USD)", color=TEXT_SECONDARY)
# 세로축 위쪽에 두 줄 글자가 들어갈 여유를 둔다
ax.set_ylim(0, groups["mean"].max() * 1.3)
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
# 그림을 PNG 파일로만 저장한다 (plt.show는 쓰지 않는다)
fig.savefig(CHART_PATH, dpi=150, facecolor=SURFACE)
# 저장 위치를 출력한다
print("저장 완료:", CHART_PATH)
# 빈 줄을 넣는다
print()

# 그룹별 표 머리를 출력한다
print("| citation | 개수 | 합 | 평균 |")
# 표 구분선을 출력한다 (숫자 열은 오른쪽 정렬)
print("|---|---:|---:|---:|")
# 범주 순서대로 한 줄씩 출력한다
for label, row in groups.iterrows():
    # 개수는 정수, 합과 평균은 소수 둘째 자리로 출력한다
    print(f"| {label} | {int(row['count'])} | {row['sum']:.2f} | {row['mean']:.2f} |")
# 빈 줄을 넣는다
print()

# 그룹별 개수의 합을 구한다
count_sum = int(groups["count"].sum())
# 1. 개수 합과 전체 행 수를 나란히 출력하고 같은지 적는다
print(f"1. 그룹 개수 합 {count_sum} / clean.csv 전체 행 수 {n_total} →", "같음" if count_sum == n_total else "다름")
# 가장 작은 그룹의 개수를 구한다
min_count = groups["count"].min()
# 가장 작은 개수를 가진 그룹을 모두 고른다
smallest = [label for label, c in groups["count"].items() if c == min_count]
# 2. 가장 작은 그룹을 출력한다
print(f"2. 가장 작은 그룹: {', '.join(smallest)} ({int(min_count)}개)")
# 3. 그룹별 평균을 소수 둘째 자리로 출력한다
print("3. 그룹별 평균:", " / ".join(f"{label} {row['mean']:.2f}" for label, row in groups.iterrows()))
