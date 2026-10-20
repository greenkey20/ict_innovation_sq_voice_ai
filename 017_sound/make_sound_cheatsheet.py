"""소리/Sampling cheat sheet 포스터를 matplotlib로 그려 PNG로 저장합니다.

실행: python make_sound_cheatsheet.py  (같은 폴더에 sound_cheatsheet.png 생성)
글자/공식은 아래 TEXT 부분만 고치면 됩니다. 폰트는 NanumGothic/NanumSquareRound(없으면 AppleGothic 등) 사용.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---------- 폰트 ----------
avail = {f.name for f in fm.fontManager.ttflist}
BODY = next((n for n in ["NanumGothic", "AppleGothic", "Malgun Gothic", "Noto Sans CJK KR"] if n in avail), "sans-serif")
HEAD = next((n for n in ["NanumSquareRound ExtraBold", "NanumSquareRound Bold", "NanumGothicExtraBold", BODY] if n in avail), BODY)
MONO = BODY
plt.rcParams["axes.unicode_minus"] = False

# ---------- 색 ----------
INK = "#1f2937"
C = dict(
    blue="#dbeafe", blue_d="#1d4ed8",
    green="#dcfce7", green_d="#15803d",
    amber="#fef3c7", amber_d="#b45309",
    rose="#ffe4e6", rose_d="#be123c",
    violet="#ede9fe", violet_d="#6d28d9",
    gray="#f3f4f6", gray_d="#4b5563",
    teal="#ccfbf1", teal_d="#0f766e",
)

W, H = 100.0, 137.5
fig = plt.figure(figsize=(16, 22), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
fig.patch.set_facecolor("white")


def card(x, y, w, h, title, fill, edge, title_size=17):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2",
                                fc=fill, ec=edge, lw=2.2))
    ax.add_patch(FancyBboxPatch((x, y + h - 3.6), w, 3.6, boxstyle="round,pad=0,rounding_size=1.2",
                                fc=edge, ec=edge, lw=2.2))
    ax.text(x + 1.2, y + h - 1.8, title, color="white", fontsize=title_size, fontfamily=HEAD,
            va="center", ha="left")


def lines(x, y, items, size=12.2, gap=2.25, color=INK, family=None, weight="normal"):
    """items: 문자열 리스트. y에서 아래로 gap씩 내려가며 출력. ('' 는 빈 줄)"""
    for k, t in enumerate(items):
        if isinstance(t, tuple):
            txt, kw = t
        else:
            txt, kw = t, {}
        ax.text(x, y - k * gap, txt, fontsize=kw.get("size", size), color=kw.get("color", color),
                fontfamily=kw.get("family", family or BODY), va="top", ha="left", weight=kw.get("weight", weight))


# ================= 헤더 =================
ax.add_patch(FancyBboxPatch((1.5, 128.2), 97, 8.2, boxstyle="round,pad=0,rounding_size=1.5", fc="#111827", ec="#111827"))
ax.text(4, 133.6, "소리 다루기 CHEAT SHEET", color="white", fontsize=34, fontfamily=HEAD, va="center")
ax.text(4, 130.2, "소리 → 숫자 배열 → 그래프·재생   |   정의 · 공식 · 단위 · 흔한 실수   (이 수업 기준 SR = 16000)",
        color="#d1d5db", fontsize=14.5, fontfamily=BODY, va="center")
ax.text(96, 133.6, "ICT 혁신 스퀘어\n017_sound", color="#9ca3af", fontsize=12.5, fontfamily=BODY, va="center", ha="right")

# ================= 1. 파이프라인 =================
card(1.5, 104.5, 97, 22.2, "① 소리가 숫자가 되는 과정", C["blue"], C["blue_d"])
steps = [
    ("소리", "공기 압력이\n빠르게 변함\n(진동)", C["amber"], C["amber_d"]),
    ("마이크", "압력 변화를\n전기 신호(전압)로\n바꿈", C["rose"], C["rose_d"]),
    ("샘플링", "1초에 SR번\n값을 읽어 기록\n(점 찍기)", C["green"], C["green_d"]),
    ("숫자 배열", "np.ndarray\nshape = (N,)\n값 범위 -1 ~ 1", C["violet"], C["violet_d"]),
    ("재생·분석", "스피커/Audio로 재생\n그래프로 확인\n(이후 FFT·모델)", C["teal"], C["teal_d"]),
]
bx, bw, by, bh, gap = 3.0, 16.6, 107.4, 13.0, 2.6
for i, (t, d, f, e) in enumerate(steps):
    x = bx + i * (bw + gap)
    ax.add_patch(FancyBboxPatch((x, by), bw, bh, boxstyle="round,pad=0,rounding_size=1.0", fc=f, ec=e, lw=2))
    ax.text(x + bw / 2, by + bh - 1.8, t, fontsize=15.5, fontfamily=HEAD, color=e, ha="center", va="top")
    ax.text(x + bw / 2, by + bh - 5.4, d, fontsize=11.6, fontfamily=BODY, color=INK, ha="center", va="top", linespacing=1.45)
    if i < len(steps) - 1:
        ax.add_patch(FancyArrowPatch((x + bw + 0.2, by + bh / 2), (x + bw + gap - 0.2, by + bh / 2),
                                     arrowstyle="-|>", mutation_scale=22, color=INK, lw=2.2))
ax.text(50, 106.0, "핵심: 연속적인 소리를 일정한 간격(1/SR초)마다 한 점씩 읽어 숫자로 저장한 것이 '샘플'이고, 그 점들의 모음이 배열이다.",
        fontsize=12.6, fontfamily=BODY, color=INK, ha="center", va="center", weight="bold")

# ================= 2. 파형 그림 + 용어 =================
card(1.5, 62.3, 47, 40.5, "② 파형 읽는 법 (그림)", C["amber"], C["amber_d"])
wax = fig.add_axes([0.035, 0.548, 0.44, 0.158])  # 비율 좌표 (x, y, w, h)
t_c = np.linspace(0, 2, 600)
A = 0.8
f_demo = 1.0
wax.plot(t_c, A * np.sin(2 * np.pi * f_demo * t_c), color="#9ca3af", lw=1.6, zorder=1)
n = 17  # 샘플 점(그림용: 두 번 오르내림을 17점으로 기록)
t_s = np.linspace(0, 2, n)
wax.plot(t_s, A * np.sin(2 * np.pi * f_demo * t_s), "o", color="#dc2626", ms=6.5, zorder=3)
wax.vlines(t_s, 0, A * np.sin(2 * np.pi * f_demo * t_s), color="#fca5a5", lw=0.9, zorder=2)
wax.axhline(0, color=INK, lw=1)
wax.set_ylim(-1.7, 1.75); wax.set_xlim(-0.05, 2.1)
wax.set_xticks([]); wax.set_yticks([])
for s in wax.spines.values():
    s.set_visible(False)
wax.patch.set_alpha(0)
# 진폭
wax.annotate("", xy=(0.25, 0.8), xytext=(0.25, 0), arrowprops=dict(arrowstyle="<->", color="#2563eb", lw=2))
wax.text(0.30, 0.42, "진폭 A (소리 크기)", color="#2563eb", fontsize=11.5, fontfamily=BODY, va="center", bbox=dict(fc="#fef3c7", ec="none", pad=1.5))
# 주기
wax.annotate("", xy=(1.0, -1.15), xytext=(0, -1.15), arrowprops=dict(arrowstyle="<->", color="#15803d", lw=2))
wax.text(0.5, -1.5, "주기 T = 1/f (한 번 오르내리는 시간)", color="#15803d", fontsize=11.3, fontfamily=BODY, ha="center", va="center")
# 샘플 간격
dt = t_s[1] - t_s[0]
wax.annotate("", xy=(t_s[10] + dt, 1.12), xytext=(t_s[10], 1.12), arrowprops=dict(arrowstyle="<->", color="#dc2626", lw=2))
wax.text(t_s[10] + dt / 2, 1.5, "샘플 간격 = 1/SR", color="#dc2626", fontsize=11.3, fontfamily=BODY, ha="center", va="center")
wax.text(1.78, 0.08, "시간 t →", color=INK, fontsize=11, fontfamily=BODY, va="bottom")
wax.text(0.12, 1.5, "● = 샘플 (1초에 SR개)", color="#dc2626", fontsize=11.3, fontfamily=BODY, va="center")
lines(2.7, 73.6, [
    "• 점이 촘촘할수록(SR↑) 원래 파형에 가까움",
    "• 점이 적으면 곡선이 지그재그로 보임",
    "• 파형이 같은 값으로 돌아오는 간격 = 주기",
    "• 샘플 간격(1/SR)은 모든 소리에 같다. 주기는 음마다 다르다",
], size=11.6, gap=2.25)

card(51.5, 62.3, 47, 40.5, "③ 핵심 용어 사전", C["green"], C["green_d"])
lines(53.0, 98.4, [
    ("샘플 (sample)", dict(weight="bold", color=C["green_d"], size=13)),
    "  한 시점에 읽은 소리 값 하나 (배열의 원소 1개)",
    ("샘플링 레이트 SR", dict(weight="bold", color=C["green_d"], size=13)),
    "  1초 동안 읽는 샘플 수.  단위 Hz = 샘플/초 (16 kHz = 16000)",
    ("진폭 (amplitude)", dict(weight="bold", color=C["green_d"], size=13)),
    "  기준선(0)에서 얼마나 크게 흔들리나 = 소리의 크기",
    ("주파수 f (frequency)", dict(weight="bold", color=C["green_d"], size=13)),
    "  1초에 몇 번 진동하나. 단위 Hz = 진동/초 = 음의 높낮이",
    ("주기 T (period)", dict(weight="bold", color=C["green_d"], size=13)),
    "  한 번 진동하는 데 걸리는 시간 = 1/f (초, ms)",
    ("길이 (duration)", dict(weight="bold", color=C["green_d"], size=13)),
    "  녹음 시간(초) = 샘플 수 ÷ SR",
    ("나이퀴스트 주파수", dict(weight="bold", color=C["green_d"], size=13)),
    "  SR÷2. 표현 가능한 최대 주파수 (make_tone: 0 < f < SR/2)",
], size=11.6, gap=2.55)

# ================= 3. 공식 =================
card(1.5, 31.5, 47, 29.4, "④ 공식 (이것만 있으면 계산 끝)", C["violet"], C["violet_d"])
lines(3.0, 56.9, [
    ("샘플 수  N = SR × 길이(초)", dict(size=13.2, weight="bold")),
    ("길이(초) = N ÷ SR", dict(size=13.2, weight="bold")),
    ("주기  T = 1 ÷ f      (ms:  1000 ÷ f)", dict(size=13.2, weight="bold")),
    ("주파수  f = 1 ÷ T", dict(size=13.2, weight="bold")),
    ("한 주기의 샘플 수 = SR ÷ f", dict(size=13.2, weight="bold")),
    ("n번째 샘플의 시각(ms) = n ÷ SR × 1000", dict(size=13.2, weight="bold")),
    ("일정 시간 동안 반복 횟수 = f × 시간(초)", dict(size=13.2, weight="bold")),
    ("처음 10 ms의 샘플 수 = SR × 0.01", dict(size=13.2, weight="bold")),
    ("사인파  y(t) = A · sin(2π · f · t)", dict(size=13.2, weight="bold", color=C["violet_d"])),
    "   A: 진폭   f: 주파수   t: 시간(초)   (y(t) = y(t+T))",
    ("단위가 헷갈리면:  (샘플/초) × 초 = 샘플", dict(size=12.0, color=C["rose_d"], weight="bold")),
], size=11.5, gap=2.30)

card(51.5, 31.5, 47, 29.4, "⑤ 무엇을 바꾸면 무엇이 달라지나", C["rose"], C["rose_d"])
# 표 (수동)
hx = [53.0, 66.5, 76.8, 87.2]
heads = ["바꾸는 것", "소리 높낮이", "소리 크기", "그 밖에"]
for x, h_ in zip(hx, heads):
    ax.text(x, 56.9, h_, fontsize=11.8, fontfamily=HEAD, color=C["rose_d"], va="top")
ax.plot([52.6, 97.4], [54.6, 54.6], color=C["rose_d"], lw=1.4)
rows = [
    ("주파수 f ↑", "높아짐", "그대로", "주기↓, 한 주기 샘플↓"),
    ("진폭 A ↑", "그대로", "커짐", "파형 키만 커짐"),
    ("길이 ↑", "그대로", "그대로", "샘플 수 N ↑"),
    ("SR ↑", "그대로", "그대로", "점 더 촘촘, N ↑"),
    ("옥타브 +1", "f ×2", "그대로", "주기·한 주기 샘플 ×½"),
]
for r, row in enumerate(rows):
    y = 53.6 - r * 3.9
    for x, cell in zip(hx, row):
        ax.text(x, y, cell, fontsize=10.6, fontfamily=BODY, color=INK, va="top", weight="bold" if x == hx[0] else "normal")
    ax.plot([52.6, 97.4], [y - 2.9, y - 2.9], color="#fecdd3", lw=0.8)
lines(53.0, 33.8 + 0.0, [("★ SR을 올려도 소리가 높아지지 않는다.  SR = 기록 촘촘함,  f = 소리 높낮이", dict(size=11.4, weight="bold", color=C["rose_d"]))], gap=2.0)
# (위 표 아래 보조 문구가 카드 아래로 넘지 않게 y는 카드 바닥 근처)

# ================= 4. 음/단위 + 예시 =================
card(1.5, 1.8, 31, 27.6, "⑥ 단위·음 높이", C["teal"], C["teal_d"])
lines(3.0, 25.4, [
    ("단위 변환", dict(weight="bold", color=C["teal_d"], size=12.6)),
    "1 kHz = 1000 Hz   (16 kHz = 16000 Hz)",
    "1초 = 1000 ms     (ms를 초로: ÷1000)",
    ("음 ↔ 주파수 (대략)", dict(weight="bold", color=C["teal_d"], size=12.6)),
    "도 262 · 레 294 · 미 330 · 파 349 · 솔 392",
    "라(A4) = 440 Hz (조율 기준)",
    "한 옥타브 ↑ = 주파수 ×2 (도 262 -> 높은 도 524)",
    "반음 1칸 ↑ = ×1.0595 (12번이면 ×2)",
    "건반: 왼쪽 = 낮은 음, 오른쪽 = 높은 음",
    "악상 기호 f(포르테)·p(피아노) ≈ 진폭 크기",
    ("SR 예시 (참고)", dict(weight="bold", color=C["teal_d"], size=12.6)),
    "전화 8 kHz · 이 수업/음성 16 kHz · CD 44.1 kHz",
    "사람이 듣는 범위 약 20 Hz ~ 20 kHz (일반 지식)",
], size=10.0, gap=1.84)

card(34.5, 1.8, 31, 27.6, "⑦ 계산 예시 (SR = 16000)", C["amber"], C["amber_d"])
lines(36.0, 25.4, [
    ("0.4초 음의 샘플 수", dict(weight="bold", color=C["amber_d"], size=12.4)),
    "  16000 × 0.4 = 6400개",
    ("32000개를 SR 16000으로 읽으면", dict(weight="bold", color=C["amber_d"], size=12.4)),
    "  32000 ÷ 16000 = 2초  (SR 8000이면 4초)",
    ("도 262 Hz", dict(weight="bold", color=C["amber_d"], size=12.4)),
    "  주기 1000÷262 = 3.82 ms",
    "  한 주기 샘플 16000÷262 = 61.1개",
    ("440 Hz (라)", dict(weight="bold", color=C["amber_d"], size=12.4)),
    "  주기 = 2.27 ms,  한 주기 샘플 = 36.4개",
    "  10 ms 동안 4.4번 반복",
    ("f를 2배로: 주기 ½, 한 주기 샘플 ½", dict(weight="bold", color=C["rose_d"], size=11.6)),
], size=10.8, gap=2.15)

card(68.5, 1.8, 30, 27.6, "⑧ 자주 하는 실수 체크", C["gray"], C["gray_d"])
lines(70.0, 25.4, [
    "[ ] 주파수 vs SR: 둘 다 Hz지만\n   진동 횟수 vs 기록 횟수",
    "[ ] 주기 vs 샘플 간격(1/SR):\n   파형 한 번 vs 기록 간격",
    "[ ] 한 주기의 샘플 수 vs\n   전체 샘플 수(SR×초)",
    "[ ] ms 변환: ÷SR 다음 ×1000",
    "[ ] make_tone: 진폭 0~0.8,\n   0 < f < SR/2",
    "[ ] Audio(..., normalize=False),\n   rate = 배열을 만든 SR",
    "[ ] 단위 확인:\n   (샘플/초)×초 = 샘플",
], size=10.6, gap=3.3)

# ================= 5. 코드 스니펫 (우측 하단 띠) =================
ax.add_patch(FancyBboxPatch((1.5, 0.15), 97, 1.55, boxstyle="round,pad=0,rounding_size=0.6", fc="#111827", ec="#111827"))
ax.text(3, 0.93, "time = np.arange(N) / SR      tone = make_tone(frequency, duration, amplitude, sr)      "
                 "plt.plot(time[:n] * 1000, tone[:n], '.-')      display(Audio(tone, rate=SR, normalize=False))",
        color="#e5e7eb", fontsize=9.6, fontfamily=BODY, va="center")

fig.savefig("sound_cheatsheet.png", dpi=150, facecolor="white")
print("saved sound_cheatsheet.png")
