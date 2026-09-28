# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# 화면 창 없이 파일로만 그림을 저장하도록 matplotlib 백엔드를 Agg로 정한다
import matplotlib
# 백엔드를 Agg(파일 저장 전용)로 설정한다
matplotlib.use("Agg")
# 그래프를 그리기 위해 pyplot을 불러온다
import matplotlib.pyplot as plt
# CSV를 읽기 위해 pandas를 불러온다
import pandas as pd

# 프로젝트 폴더 경로를 만든다 (scripts 폴더의 한 단계 위)
PROJECT_DIR = Path(__file__).resolve().parent.parent
# 읽기만 할 clean.csv 경로
CLEAN_PATH = PROJECT_DIR / "data" / "clean.csv"
# 그림을 저장할 경로
CHART_PATH = PROJECT_DIR / "charts" / "hist.png"
# 고정 구간 경계
BINS = [0, 10, 20, 30, 40, 50]
# 표에 쓸 구간 이름 (마지막 구간만 50 포함)
BIN_LABELS = ["0 이상 10 미만", "10 이상 20 미만", "20 이상 30 미만", "30 이상 40 미만", "40 이상 50 이하"]
# 직접 센 0 이상 10 미만 개수
HAND_COUNT_0_10 = 8
# 막대 색 (한 가지 계열만 쓰는 단일 색)
BAR_COLOR = "#2a78d6"
# 그림 바탕 색
SURFACE = "#fcfcfb"
# 본문 글자 색
TEXT_PRIMARY = "#0b0b0b"
# 보조 글자 색 (축 눈금 등)
TEXT_SECONDARY = "#52514e"

# clean.csv를 읽는다 (파일은 수정하지 않는다)
df = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig", keep_default_na=False)
# price 열만 꺼낸다
price = df["price"]
# 가격 개수(n)를 센다
n = int(price.count())

# 그림과 축을 만든다 (가로 8인치, 세로 5인치)
fig, ax = plt.subplots(figsize=(8, 5), facecolor=SURFACE)
# 축 안쪽 바탕 색을 정한다
ax.set_facecolor(SURFACE)
# 히스토그램을 그린다 (왼쪽 끝 포함·오른쪽 끝 미포함, 마지막 구간만 50 포함)
counts, edges, bars = ax.hist(price, bins=BINS, color=BAR_COLOR, edgecolor=SURFACE, linewidth=2)

# 막대마다 위에 개수를 적는다
for count, left, right in zip(counts, edges[:-1], edges[1:]):
    # 막대 가운데 위에 정수 개수를 쓴다
    ax.text((left + right) / 2, count + 0.15, f"{int(count)}", ha="center", va="bottom", color=TEXT_PRIMARY, fontsize=11)

# 제목을 영어로 적는다
ax.set_title(f"PDF AI monthly price distribution (n = {n})", color=TEXT_PRIMARY, fontsize=13, loc="left")
# 가로축 이름을 적는다
ax.set_xlabel("Price (USD)", color=TEXT_SECONDARY)
# 세로축 이름을 적는다
ax.set_ylabel("Number of tools", color=TEXT_SECONDARY)
# 가로축 눈금을 구간 경계와 똑같이 둔다
ax.set_xticks(BINS)
# 세로축 위쪽에 숫자 글자가 들어갈 여유를 둔다
ax.set_ylim(0, max(counts) + 1)
# 세로축 눈금을 정수로만 둔다
ax.yaxis.get_major_locator().set_params(integer=True)
# 눈금 글자 색을 보조 색으로 정한다
ax.tick_params(colors=TEXT_SECONDARY)
# 가로 방향 보조선을 옅게 깔고 막대 뒤로 보낸다
ax.grid(axis="y", color="#e4e3df", linewidth=0.8)
# 보조선을 막대 뒤에 그린다
ax.set_axisbelow(True)
# 위쪽·오른쪽 테두리를 없앤다
ax.spines[["top", "right"]].set_visible(False)
# 왼쪽·아래쪽 테두리를 옅게 만든다
ax.spines[["left", "bottom"]].set_color("#c9c8c3")

# charts 폴더가 없으면 만든다
CHART_PATH.parent.mkdir(parents=True, exist_ok=True)
# 여백을 정리한다
fig.tight_layout()
# 그림을 PNG 파일로만 저장한다 (plt.show는 쓰지 않는다)
fig.savefig(CHART_PATH, dpi=150, facecolor=SURFACE)
# 저장 위치를 출력한다
print("저장 완료:", CHART_PATH)
# 빈 줄을 넣는다
print()

# 구간별 빈도 표 머리를 출력한다
print("| 구간 (USD) | 개수 |")
# 표 구분선을 출력한다 (개수 열은 오른쪽 정렬)
print("|---|---:|")
# 구간 이름과 개수를 한 줄씩 출력한다
for label, count in zip(BIN_LABELS, counts):
    # 구간 한 줄을 출력한다
    print(f"| {label} | {int(count)} |")
# 빈도 합을 구한다
total = int(counts.sum())
# 합계 줄을 출력한다
print(f"| 합계 | {total} |")
# 빈 줄을 넣는다
print()

# 빈도 합과 전체 행 수를 나란히 출력하고 같은지 적는다
print(f"빈도 합 {total} / clean.csv 전체 행 수 {len(df)} →", "같음" if total == len(df) else "다름")
# 0 이상 10 미만 구간 개수를 꺼낸다
first_bin = int(counts[0])
# 0 이상 10 미만 개수를 출력한다
print("0 이상 10 미만 구간 개수:", first_bin)
# 직접 센 값과 비교한 결과를 출력한다
print(f"직접 센 값 {HAND_COUNT_0_10} / 계산값 {first_bin} →", "같음" if first_bin == HAND_COUNT_0_10 else "다름")
