# 파일 경로를 다루기 위해 pathlib의 Path를 불러온다
from pathlib import Path

# 화면 창 없이 파일로만 그림을 저장하도록 matplotlib를 불러온다
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
# 새로 저장할 그림 경로 (기존 hist.png와 다른 이름)
CHART_PATH = PROJECT_DIR / "charts" / "hist_half.png"
# 5달러 간격 구간 경계
BINS = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
# 기존 10달러 폭 그래프에서 가장 높았던 구간 (0 이상 10 미만)
OLD_TOP = (0, 10)
# 막대 색 (05_hist.py와 같은 단일 색)
BAR_COLOR = "#2a78d6"
# 그림 바탕 색
SURFACE = "#fcfcfb"
# 본문 글자 색
TEXT_PRIMARY = "#0b0b0b"
# 보조 글자 색
TEXT_SECONDARY = "#52514e"

# 기존 hist.png를 덮어쓰지 않도록 저장 경로를 한 번 더 확인한다
assert CHART_PATH.name != "hist.png"

# clean.csv를 읽는다 (파일은 수정하지 않는다)
df = pd.read_csv(CLEAN_PATH, encoding="utf-8-sig", keep_default_na=False)
# price 열만 꺼낸다
price = df["price"]
# 가격 개수(n)를 센다
n = int(price.count())

# 그림과 축을 만든다 (가로 9인치, 세로 5인치)
fig, ax = plt.subplots(figsize=(9, 5), facecolor=SURFACE)
# 축 안쪽 바탕 색을 정한다
ax.set_facecolor(SURFACE)
# 히스토그램을 그린다 (왼쪽 끝 포함·오른쪽 끝 미포함, 마지막 구간만 50 포함)
counts, edges, bars = ax.hist(price, bins=BINS, color=BAR_COLOR, edgecolor=SURFACE, linewidth=2)

# 막대마다 위에 개수를 적는다
for count, left, right in zip(counts, edges[:-1], edges[1:]):
    # 막대 가운데 위에 정수 개수를 쓴다
    ax.text((left + right) / 2, count + 0.1, f"{int(count)}", ha="center", va="bottom", color=TEXT_PRIMARY, fontsize=10)

# 제목을 영어로 적는다
ax.set_title(f"PDF AI monthly price distribution, 5 USD bins (n = {n})", color=TEXT_PRIMARY, fontsize=13, loc="left")
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


# 구간 이름을 만드는 함수 (마지막 구간만 "이하")
def bin_label(left, right, is_last):
    # 마지막 구간이면 오른쪽 끝 포함, 아니면 미포함으로 적는다
    return f"{int(left)} 이상 {int(right)} {'이하' if is_last else '미만'}"


# 구간 이름 목록을 만든다
labels = [bin_label(l, r, i == len(counts) - 1) for i, (l, r) in enumerate(zip(edges[:-1], edges[1:]))]
# 빈도표 머리를 출력한다
print("| 구간 (USD) | 개수 |")
# 표 구분선을 출력한다
print("|---|---:|")
# 구간 이름과 개수를 한 줄씩 출력한다
for label, count in zip(labels, counts):
    # 구간 한 줄을 출력한다
    print(f"| {label} | {int(count)} |")
# 빈도 합을 구한다
total = int(counts.sum())
# 합계 줄을 출력한다
print(f"| 합계 | {total} |")
# 빈 줄을 넣는다
print()

# 1. 빈도 합이 14인지 출력한다
print(f"1. 빈도 합 {total} →", "14와 같음" if total == 14 else "14와 다름")

# 가장 큰 개수를 구한다
top = counts.max()
# 가장 큰 개수를 가진 구간 번호를 모두 고른다 (같은 높이가 여럿일 수 있다)
top_idx = [i for i, c in enumerate(counts) if c == top]
# 2. 가장 높은 막대 구간과 개수를 출력한다
print("2. 가장 높은 막대:", ", ".join(labels[i] for i in top_idx), f"({int(top)}개)")

# 가장 높은 막대가 모두 기존 0~10 구간 안에 있는지 확인한다
inside = all(OLD_TOP[0] <= edges[i] and edges[i + 1] <= OLD_TOP[1] for i in top_idx)
# 가장 높은 막대가 기존 구간과 똑같은 범위인지 확인한다
same = len(top_idx) == 1 and (edges[top_idx[0]], edges[top_idx[0] + 1]) == OLD_TOP
# 3. 기존 그래프와 비교한 결과를 출력한다
if same:
    # 범위가 똑같으면 그대로라고 적는다
    print("3. 기존 10달러 폭 최고 구간 0 이상 10 미만과 같은 범위 → 그대로")
# 범위는 다르지만 기존 구간 안에 들어 있으면
elif inside:
    # 기존 구간 안에서 더 좁혀졌다고 적는다
    print(f"3. 기존 10달러 폭 최고 구간 0 이상 10 미만 → 5달러 폭에서는 {', '.join(labels[i] for i in top_idx)} (기존 구간 안에서 위치가 좁혀짐)")
# 기존 구간 밖으로 나가면
else:
    # 위치가 바뀌었다고 적는다
    print(f"3. 기존 10달러 폭 최고 구간 0 이상 10 미만 → 5달러 폭에서는 {', '.join(labels[i] for i in top_idx)} (기존 구간 밖으로 바뀜)")
