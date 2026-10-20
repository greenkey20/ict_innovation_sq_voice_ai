"""소리 cheat sheet 2장 세트를 matplotlib로 그려 PNG로 저장합니다. (AI 이미지 생성이 아니라 코드로 그린 그림)

  sound_cheatsheet_1_main.png  : 용어 + 공식 + 계산 예시 + 파형 + 코드 + 주의를 한 장에 합친 메인 시트
  sound_cheatsheet_2_deep.png  : 심화 Q&A (나이퀴스트, 한 주기 샘플 수, 시각, 사인 공식, 옥타브, 반음/평균율)

실행: python make_sound_cheatsheet.py   (같은 폴더에 PNG 2개가 만들어집니다)
글자/공식은 build_sheet1(), build_sheet2() 안의 내용만 고치면 됩니다.

표기 약속(모든 곳에서 통일):
  샘플 수 N, 샘플링 레이트 SR, 길이 t(초), 진폭 A, 주파수 f, 주기 T
마크업: **굵게**, `코드`, {p|보라 굵게}, {u|파랑 굵게}, {y|노랑 형광}
  ★ = 주의할 점,  † = 수업 자료에는 없던 보충 설명,  `코드` = 수업 노트북에서 인용
"""
import re
import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

DPI = 150
avail = {f.name for f in fm.fontManager.ttflist}
BODY = next((n for n in ["NanumGothic", "AppleGothic", "Malgun Gothic", "Noto Sans CJK KR"] if n in avail), "sans-serif")
HEAD = next((n for n in ["NanumSquareRound", "NanumGothic", BODY] if n in avail), BODY)
MONO = next((n for n in ["Menlo", "DejaVu Sans Mono", "Courier New"] if n in avail), "monospace")
plt.rcParams["axes.unicode_minus"] = False

# ---------- 색 (초록 계열 + 보라/파랑/라임/노랑 강조, 붉은 계열 사용 안 함) ----------
BG = "#f0fdf4"
INK = "#14281d"
G_DEEP, G_MID, G_SOFT, G_PALE = "#14532d", "#15803d", "#86efac", "#dcfce7"
LIME, LIME_D = "#a3e635", "#4d7c0f"
YEL, YEL_BG, YEL_INK = "#facc15", "#fef9c3", "#422006"
PUR, PUR_BG = "#7c3aed", "#ede9fe"
BLU, BLU_BG = "#2563eb", "#dbeafe"
CODE_BG, CODE_EC, CODE_INK = "#ecfccb", "#84cc16", "#1e1b4b"

STYLE = {
    "n": dict(color=INK, family=BODY, weight="normal"),
    "b": dict(color=G_DEEP, family=BODY, weight="bold"),
    "p": dict(color=PUR, family=BODY, weight="bold"),
    "u": dict(color=BLU, family=BODY, weight="bold"),
    "y": dict(color=YEL_INK, family=BODY, weight="bold"),
    "c": dict(color=CODE_INK, family=[MONO, BODY], weight="normal"),
}
TOKEN_RE = re.compile(r"(\*\*.+?\*\*|\{[puyb]\|.+?\}|`.+?`)")


def parse(markup):
    out = []
    for part in TOKEN_RE.split(markup):
        if not part:
            continue
        if part.startswith("**"):
            out.append(("b", part[2:-2]))
        elif part.startswith("{") and part[2] == "|":
            out.append((part[1], part[3:-1]))
        elif part.startswith("`"):
            out.append(("c", part[1:-1]))
        else:
            out.append(("n", part))
    return out


class Sheet:
    draw_ok = True

    def __init__(self, W, H):
        self.W, self.H = W, H
        self.fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
        self.fig.patch.set_facecolor(BG)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(H, 0)
        self.ax.axis("off")
        self.r = self.fig.canvas.get_renderer()
        self.cache = {}

    @staticmethod
    def px(pt):
        return pt * DPI / 72.0

    def width(self, text, kind, size):
        key = (text, kind, size)
        if key not in self.cache:
            st = STYLE[kind]
            t = self.ax.text(0, 0, text, fontsize=size * (0.93 if kind == "c" else 1.0), fontfamily=st["family"],
                             fontweight=st["weight"])
            self.cache[key] = t.get_window_extent(self.r).width
            t.remove()
        return self.cache[key]

    def para(self, x, y, w, markup, size=14, lh=1.55, dry=False, indent=0):
        """폭 w 안에서 줄바꿈하며 한 문단 배치. dry=True면 그리지 않고 끝 y만 반환."""
        toks = parse(markup)
        space = self.px(size) * 0.30
        cx, cy = x + indent, y
        line_h = self.px(size) * lh
        base = self.px(size) * 1.02
        for kind, text in toks:
            pieces = [text] if kind == "c" else [p for p in re.split(r"(\s+)", text) if p != ""]
            for p in pieces:
                if p.isspace():
                    if cx > x + indent + 1:
                        cx += space
                    continue
                wd = self.width(p, kind, size) + (self.px(size) * 0.25 if kind == "c" else 0)
                if cx + wd > x + w and cx > x + indent + 1:
                    cx = x + indent
                    cy += line_h
                if not dry:
                    st = STYLE[kind]
                    kw = dict(fontsize=size * (0.93 if kind == "c" else 1.0), fontfamily=st["family"],
                              fontweight=st["weight"], color=st["color"], va="baseline", ha="left")
                    if kind == "c":
                        kw["bbox"] = dict(boxstyle="round,pad=0.16", fc=CODE_BG, ec=CODE_EC, lw=0.9)
                        self.ax.text(cx + self.px(size) * 0.12, cy + base, p, **kw)
                    elif kind == "y":
                        kw["bbox"] = dict(boxstyle="round,pad=0.12", fc=YEL, ec="none")
                        self.ax.text(cx, cy + base, p, **kw)
                    else:
                        self.ax.text(cx, cy + base, p, **kw)
                cx += wd
        return cy + line_h

    def items(self, x, y, w, its, dry=False):
        for it in its:
            kind = it[0]
            if kind == "p":
                y = self.para(x, y, w, it[1], size=it[2] if len(it) > 2 else 14, dry=dry) + 6
            elif kind == "gap":
                y += it[1]
            elif kind == "note":
                size = it[2] if len(it) > 2 else 12.5
                h = self.para(x + 18, y + 8, w - 36, it[1], size=size, dry=True) - y + 8
                if not dry:
                    self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=10",
                                                     fc=YEL_BG, ec=YEL, lw=2))
                    self.para(x + 18, y + 8, w - 36, it[1], size=size)
                y += h + 10
            elif kind == "code":
                lines = it[1]
                size = it[2] if len(it) > 2 else 12.2
                lh = self.px(size) * 1.5
                h = lh * len(lines) + 22
                if not dry:
                    self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=10",
                                                     fc=CODE_BG, ec=CODE_EC, lw=1.6))
                    for k, ln in enumerate(lines):
                        self.ax.text(x + 16, y + 11 + k * lh + self.px(size) * 1.0, ln, fontsize=size, fontfamily=[MONO, BODY],
                                     color=CODE_INK, va="baseline", ha="left")
                y += h + 10
            elif kind == "table":
                _, ratios, rows, size, header = it
                tot = sum(ratios)
                cw = [w * r / tot for r in ratios]
                for ri, row in enumerate(rows):
                    hs = [self.para(0, 0, cw[ci] - 20, cell, size=size, dry=True) for ci, cell in enumerate(row)]
                    rh = max(hs) + 10
                    if not dry:
                        if header and ri == 0:
                            self.ax.add_patch(Rectangle((x, y), w, rh, fc=G_SOFT, ec="none"))
                        elif ri % 2 == 0:
                            self.ax.add_patch(Rectangle((x, y), w, rh, fc="#ecfdf5", ec="none"))
                        cx = x
                        for ci, cell in enumerate(row):
                            self.para(cx + 10, y + 5, cw[ci] - 20, cell, size=size)
                            cx += cw[ci]
                    y += rh
                y += 8
            elif kind == "fig":
                h = it[1]
                if not dry:
                    pad = it[3] if len(it) > 3 else False      # True면 눈금/축 이름이 들어갈 여백을 안쪽에 남김
                    l, b, ww, hh = (0.07, 0.17, 0.91, 0.78) if pad else (0.0, 0.0, 1.0, 1.0)
                    sub = self.fig.add_axes([(x + l * w) / self.W, 1 - (y + (b + hh) * h * 0 + h - b * h) / self.H if False else
                                             1 - (y + h) / self.H + b * h / self.H, ww * w / self.W, hh * h / self.H])
                    sub.patch.set_alpha(0)
                    it[2](sub)
                y += h + 8
        return y

    def card(self, x, y, w, title, its, num=None, head=G_MID, fill=G_PALE, edge=G_MID, force_h=None, tsize=19):
        pad = 26
        head_h = 66
        body_y = y + head_h + 16
        end = self.items(x + pad, body_y, w - 2 * pad, its, dry=True)
        h = max(end - y + pad - 8, force_h or 0)
        if self.draw_ok:
            self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=22", fc=fill, ec=edge, lw=3))
            self.ax.add_patch(FancyBboxPatch((x, y), w, head_h, boxstyle="round,pad=0,rounding_size=22", fc=head, ec=edge, lw=3))
            self.ax.add_patch(Rectangle((x + 2, y + head_h - 24), w - 4, 24, fc=head, ec="none"))
            tx = x + 24
            if num:
                self.ax.add_patch(Circle((x + 44, y + head_h / 2), 22, fc=LIME, ec="white", lw=2))
                self.ax.text(x + 44, y + head_h / 2 + 1, num, fontsize=14 if len(num) <= 2 else 12, fontfamily=HEAD, fontweight="bold",
                             color=G_DEEP, ha="center", va="center")
                tx = x + 80
            self.ax.text(tx, y + head_h / 2 + 1, title, fontsize=tsize, fontfamily=HEAD, fontweight="bold", color="white",
                         ha="left", va="center")
            self.items(x + pad, body_y, w - 2 * pad, its, dry=False)
        return h

    def card_h(self, x, y, w, title, its, **kw):
        self.draw_ok = False
        h = self.card(x, y, w, title, its, **kw)
        self.draw_ok = True
        return h

    def row(self, y, specs, gap=36, margin=40):
        """specs: [(title, items, kwargs, width_ratio)] -> 같은 높이로 나란히. 반환: 다음 y"""
        total = self.W - 2 * margin - gap * (len(specs) - 1)
        rs = sum(s[3] for s in specs)
        ws = [total * s[3] / rs for s in specs]
        hs, x = [], margin
        for (title, its, kw, _), w in zip(specs, ws):
            hs.append(self.card_h(x, y, w, title, its, **kw))
            x += w + gap
        H = max(hs)
        x = margin
        for (title, its, kw, _), w in zip(specs, ws):
            self.card(x, y, w, title, its, force_h=H, **kw)
            x += w + gap
        return y + H + 34

    def header(self, title, sub, tag):
        self.ax.add_patch(FancyBboxPatch((40, 36), self.W - 80, 190, boxstyle="round,pad=0,rounding_size=30", fc=G_DEEP, ec=G_DEEP))
        self.ax.add_patch(Rectangle((80, 206), self.W - 160, 12, fc=LIME, ec="none"))
        self.ax.text(90, 108, title, fontsize=40, fontfamily=HEAD, fontweight="bold", color="white", va="center")
        self.ax.text(90, 172, sub, fontsize=16, fontfamily=BODY, color="#bbf7d0", va="center")
        self.ax.text(self.W - 90, 108, tag, fontsize=18, fontfamily=BODY, color=LIME, va="center", ha="right", fontweight="bold")
        return 260


# =====================================================================
#  공통 숫자 (그림과 예시에 쓰는 값은 모두 여기서 계산)
# =====================================================================
SR = 16000
F_DO = 262           # 수업에서 쓴 '도'
A_DEMO = 0.3
T_MS = 1000 / F_DO   # 3.817 ms
DT_MS = 1000 / SR    # 0.0625 ms

# 수업 노트북에서 인용한 코드 줄 (노트북이 같은 폴더에 있으면 실제로 들어 있는지 확인)
QUOTES = [
    "sample_count = int(round(sr * duration))",
    "time = np.arange(len(tone)) / SR",
    "period_ms = 1 / frequency * 1000",
    "samples_per_period = SR / frequency",
    "sound = amplitude * np.sin(2 * np.pi * frequency * time)",
    "if not (0 < frequency < sr / 2):",
    "seconds = sample_count / sample_rate",
    "notes = [262, 294, 330, 349, 392]",
    "louder = make_tone(frequency=440, duration=0.5, amplitude=0.3)",
    "repeats_10ms = frequency * 0.01",
    "display(Audio(tone, rate=SR, normalize=False))",
    "for frequency in [220, 440, 880, 1760]:",
]


def verify_quotes():
    nb = os.path.join(os.path.dirname(os.path.abspath(__file__)), "01_소리가_숫자가_되는_과정.ipynb")
    if not os.path.exists(nb):
        print("(노트북이 같은 폴더에 없어 코드 인용 확인은 건너뜀)")
        return
    src = "\n".join("".join(c["source"]) for c in json.load(open(nb, encoding="utf-8"))["cells"])
    src = re.sub(r"\s+", " ", src)
    missing = [q for q in QUOTES if re.sub(r"\s+", " ", q) not in src]
    print("코드 인용 확인:", "모두 노트북에 있음" if not missing else f"노트북에 없음 -> {missing}")


# =====================================================================
#  그림들
# =====================================================================
def wave_figure(ax):
    """262 Hz(도) 파형, SR=16000 점, 처음 10 ms (= 160개 샘플). 용어를 그림 위에 직접 표시."""
    bb = ax.get_position()   # 위(보조 눈금)·아래(축 이름)에 글자 공간을 남기려고 축을 안쪽으로 줄임
    ax.set_position([bb.x0 + 0.04 * bb.width, bb.y0 + 0.17 * bb.height, bb.width * 0.95, bb.height * 0.68])
    n = np.arange(0, 160)
    t = n / SR * 1000
    tc = np.linspace(0, 10, 2000)
    A = A_DEMO
    ax.plot(tc, A * np.sin(2 * np.pi * F_DO * tc / 1000), color=G_MID, lw=2.4, zorder=2)
    ax.vlines(t, 0, A * np.sin(2 * np.pi * F_DO * t / 1000), color=G_SOFT, lw=1.0, zorder=1)
    ax.plot(t, A * np.sin(2 * np.pi * F_DO * t / 1000), "o", color=PUR, ms=4.2, zorder=3)
    ax.axhline(0, color=INK, lw=1.2)
    ax.set_xlim(-0.15, 10.2)
    ax.set_ylim(-0.62, 0.56)
    ax.set_yticks([-A, 0, A])
    ax.set_yticklabels(["-A", "0", "+A"], fontfamily=BODY, fontsize=13, color=BLU)
    ax.set_xticks(range(0, 11))
    ax.set_xticklabels([f"{k}" for k in range(11)], fontfamily=BODY, fontsize=12.5, color=INK)
    ax.set_xlabel("시간 t (ms)  =  n ÷ SR × 1000", fontfamily=BODY, fontsize=13.5, color=G_DEEP, labelpad=4)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(G_MID)
    ax.spines["bottom"].set_color(G_MID)
    ax.tick_params(colors=G_MID)
    top = ax.twiny()
    top.set_xlim(ax.get_xlim())
    ticks = list(range(0, 11))
    top.set_xticks(ticks)
    top.set_xticklabels([f"n={int(k * SR / 1000)}" for k in ticks], fontfamily=BODY, fontsize=11.5, color=PUR)
    top.tick_params(colors=PUR, length=4)
    top.spines["top"].set_color(PUR)
    for s in ["left", "right", "bottom"]:
        top.spines[s].set_visible(False)
    ax.annotate("", xy=(0.95, A), xytext=(0.95, 0), arrowprops=dict(arrowstyle="<->", color=BLU, lw=2.6))
    ax.text(1.12, 0.15, "④ 진폭 A = 0.3\n(소리 크기)", color=BLU, fontsize=14, fontfamily=BODY, fontweight="bold", va="center",
            bbox=dict(fc=BLU_BG, ec=BLU, boxstyle="round,pad=0.25"))
    ax.annotate("", xy=(T_MS, -0.40), xytext=(0, -0.40), arrowprops=dict(arrowstyle="<->", color=PUR, lw=2.8))
    ax.text(T_MS / 2, -0.52, "⑥ 주기 T = 1/f = 3.82 ms\n(⑤ 주파수 f = 262 Hz)", color=PUR, fontsize=14, fontfamily=BODY,
            fontweight="bold", ha="center", va="center", bbox=dict(fc=PUR_BG, ec=PUR, boxstyle="round,pad=0.25"))
    ax.annotate("", xy=(T_MS * 2, -0.40), xytext=(T_MS, -0.40), arrowprops=dict(arrowstyle="<->", color=LIME_D, lw=2.8))
    ax.text(T_MS * 1.5 + 0.35, -0.52, "⑦ 한 주기의 샘플 수\nSR ÷ f = 61.1개", color=LIME_D, fontsize=14, fontfamily=BODY,
            fontweight="bold", ha="center", va="center", bbox=dict(fc="#f7fee7", ec=LIME, boxstyle="round,pad=0.25"))
    k0 = 100
    mid_t = (t[k0] + t[k0 + 1]) / 2
    mid_y = A * np.sin(2 * np.pi * F_DO * mid_t / 1000)
    ax.plot([t[k0], t[k0 + 1]], [A * np.sin(2 * np.pi * F_DO * t[k0] / 1000), A * np.sin(2 * np.pi * F_DO * t[k0 + 1] / 1000)],
            "o", color=LIME, ms=9, mec=G_DEEP, mew=1.6, zorder=5)
    ax.annotate("② 샘플 간격 = 1/SR = 0.0625 ms\n(바로 옆 두 점 사이)", xy=(mid_t, mid_y), xytext=(t[k0] + 0.3, 0.48),
                color=G_DEEP, fontsize=13.5, fontfamily=BODY, fontweight="bold", ha="center", va="center",
                arrowprops=dict(arrowstyle="->", color=G_DEEP, lw=2),
                bbox=dict(fc=G_PALE, ec=G_MID, boxstyle="round,pad=0.25"))
    ax.text(0.04, 0.47, "● 보라 점 하나 = ① 샘플\n이 그림 전체 = 처음 10 ms = 160개", color=PUR, fontsize=13.5, fontfamily=BODY,
            fontweight="bold", ha="left", va="center")
    ax.annotate("n=48번째 샘플\n시각 = 48 ÷ 16000 = 3 ms", xy=(3.0, A * np.sin(2 * np.pi * F_DO * 3.0 / 1000)), xytext=(3.55, 0.40),
                color=G_DEEP, fontsize=13.5, fontfamily=BODY, fontweight="bold", va="center",
                arrowprops=dict(arrowstyle="->", color=G_DEEP, lw=2),
                bbox=dict(fc="white", ec=G_DEEP, boxstyle="round,pad=0.25"))


def alias_figure(ax):
    n = np.arange(0, 11)
    t = n / SR * 1000
    tc = np.linspace(0, 10 * DT_MS, 800)
    ax.plot(tc, np.cos(2 * np.pi * 7000 * tc / 1000), color=PUR, lw=2.4, label="7000 Hz")
    ax.plot(tc, np.cos(2 * np.pi * 9000 * tc / 1000), color=BLU, lw=2.4, ls="--", label="9000 Hz (8000 초과)")
    ax.plot(t, np.cos(2 * np.pi * 7000 * t / 1000), "o", color=LIME_D, ms=12, mec="white", mew=1.6, zorder=5,
            label="샘플 (SR=16000)")
    ax.axhline(0, color=INK, lw=1)
    ax.set_ylim(-1.35, 2.05)
    ax.set_xlabel("시간 t (ms)", fontfamily=BODY, fontsize=13)
    ax.set_yticks([-1, 0, 1])
    ax.tick_params(labelsize=12)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.legend(loc="upper center", ncol=3, prop={"family": BODY, "size": 11.5}, frameon=True, framealpha=0.95,
              columnspacing=1.2, handletextpad=0.5)


def timeline_figure(ax):
    ax.set_xlim(-1.4, 11.0)
    ax.set_ylim(-1.9, 1.95)
    ax.axis("off")
    ax.annotate("", xy=(10.8, 0), xytext=(-0.9, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.4))
    pts = [(0, "n=0", "0 ms"), (2, "n=1", "0.0625 ms"), (4, "n=2", "0.125 ms"), (6, "n=3", "0.1875 ms"),
           (9.0, "n=16", "1 ms"), (10.3, "…", "")]
    for xv, nl, tl in pts[:-1]:
        ax.add_patch(Circle((xv, 0), 0.17, fc=PUR, ec="white", lw=1.6, zorder=3))
        ax.text(xv, 0.62, nl, ha="center", va="center", fontsize=14, fontfamily=BODY, color=PUR, fontweight="bold")
        ax.text(xv, -0.66, tl, ha="center", va="center", fontsize=12.5, fontfamily=BODY, color=G_DEEP)
    ax.text(7.5, 0.0, "…", ha="center", va="center", fontsize=22, color=INK, bbox=dict(fc="#ffffff", ec="none", pad=1))
    ax.annotate("", xy=(2, -1.15), xytext=(0, -1.15), arrowprops=dict(arrowstyle="<->", color=LIME_D, lw=2.4))
    ax.text(1.0, -1.6, "1/SR = 0.0625 ms (찰칵 간격)", ha="center", va="center", fontsize=12.5, fontfamily=BODY, color=LIME_D,
            fontweight="bold")
    ax.text(4.8, 1.45, "n번째 찰칵의 시각 = n × (1/SR) = n ÷ SR", ha="center", va="center", fontsize=15,
            fontfamily=BODY, color=G_DEEP, fontweight="bold", bbox=dict(fc="white", ec=G_MID, boxstyle="round,pad=0.35"))


def sine_figure(ax):
    tc = np.linspace(0, 4.2, 1500)
    ax.plot(tc, A_DEMO * np.sin(2 * np.pi * F_DO * tc / 1000), color=G_MID, lw=2.6)
    ax.axhline(0, color=INK, lw=1)
    for nn in [0, 15, 30, 46, 61]:
        tt = nn / SR * 1000
        yy = A_DEMO * np.sin(2 * np.pi * F_DO * tt / 1000)
        ax.plot([tt], [yy], "o", color=PUR, ms=11, mec="white", mew=1.6, zorder=4)
        up = yy >= -0.01
        ax.text(tt + (0.12 if nn == 0 else 0), yy + (0.06 if up else -0.06), f"n={nn}\n{yy:+.3f}", ha="left" if nn == 0 else "center",
                va="bottom" if up else "top",
                fontsize=11.5, fontfamily=BODY, color=PUR, fontweight="bold")
    ax.set_ylim(-0.6, 0.6)
    ax.set_xlim(-0.2, 4.4)
    ax.set_xlabel("시간 t (ms)", fontfamily=BODY, fontsize=13)
    ax.set_yticks([-A_DEMO, 0, A_DEMO])
    ax.tick_params(labelsize=12)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)


def cycle_figure(ax):
    n = np.arange(0, 62)
    t = n / SR * 1000
    tc = np.linspace(0, T_MS, 500)
    ax.plot(tc, np.sin(2 * np.pi * F_DO * tc / 1000), color=G_MID, lw=2.4)
    ax.plot(t, np.sin(2 * np.pi * F_DO * t / 1000), "o", color=PUR, ms=5)
    ax.axhline(0, color=INK, lw=1)
    ax.set_ylim(-1.5, 1.7)
    ax.set_xlim(-0.1, T_MS + 0.1)
    ax.set_xlabel("한 주기 = 3.82 ms 동안", fontfamily=BODY, fontsize=13)
    ax.text(T_MS / 2, 1.3, "점이 약 61개  (= 16000 ÷ 262)", ha="center", fontsize=14, fontfamily=BODY, color=PUR, fontweight="bold")
    ax.set_yticks([])
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)


def keyboard_figure(ax):
    ax.set_xlim(-0.3, 8.3)
    ax.set_ylim(-0.4, 4.8)
    ax.axis("off")
    white = [("도", 261.63), ("레", 293.66), ("미", 329.63), ("파", 349.23), ("솔", 392.00), ("라", 440.00), ("시", 493.88), ("도", 523.25)]
    for i, (nm, f) in enumerate(white):
        ax.add_patch(Rectangle((i, 0), 0.96, 2.6, fc="white", ec=INK, lw=1.6))
        ax.text(i + 0.48, 0.32, nm, ha="center", fontsize=14, fontfamily=BODY, fontweight="bold", color=G_DEEP)
        ax.text(i + 0.48, 0.85, f"{f:.0f}", ha="center", fontsize=12.5, fontfamily=BODY, color=INK)
    blacks = {0: 277.18, 1: 311.13, 3: 369.99, 4: 415.30, 5: 466.16}
    for i, f in blacks.items():
        ax.add_patch(Rectangle((i + 0.68, 1.15), 0.6, 1.45, fc=G_DEEP, ec=INK, lw=1.4, zorder=3))
        ax.text(i + 0.98, 1.3, f"{f:.0f}", ha="center", fontsize=11, fontfamily=BODY, color="white", zorder=4)
    ax.annotate("", xy=(0.98, 2.95), xytext=(0.48, 2.95), arrowprops=dict(arrowstyle="->", color=PUR, lw=2.6))
    ax.text(1.12, 3.22, "도 → 도#: 반음 1칸 = × 1.0595  (262 → 277)", ha="left", va="center", fontsize=13, fontfamily=BODY,
            color=PUR, fontweight="bold")
    ax.annotate("", xy=(7.48, 4.15), xytext=(0.48, 4.15), arrowprops=dict(arrowstyle="->", color=BLU, lw=2.8))
    ax.text(4.0, 4.5, "도 → 높은 도 = 반음 12칸 = (1.0595)^12 = × 2  (한 옥타브)", ha="center", va="center", fontsize=14,
            fontfamily=BODY, color=BLU, fontweight="bold")


# =====================================================================
#  시트 1: 메인
# =====================================================================
def build_sheet1(H=7300):
    S = Sheet(2400, H)
    y = S.header("소리 CHEAT SHEET ①  한 장 요약",
                 "용어 · 공식 · 계산 예시 · 파형 · 수업 코드 · 주의를 한 지면에서   |   표기: 샘플 수 N · 샘플링 레이트 SR · 길이 t · 진폭 A · 주파수 f · 주기 T   |   기준 SR = 16000",
                 "ICT 혁신 스퀘어 · 017_sound")
    wave_items = [
        ("p", "아래 **하나의 그림**에 오늘 배운 용어가 모두 있습니다. 번호(①~⑧)는 아래 카드의 번호와 같습니다. "
              "소리는 수업의 **도(262 Hz)**, SR = 16000 기준이고, 점은 실제 개수(10 ms 동안 160개)로 그렸습니다.", 14),
        ("fig", 800, wave_figure),
        ("note", "★ **읽는 순서**: 가로축 아래는 시간 t(ms), 위는 샘플 번호 n.  n번째 점의 시각은 `n ÷ SR`.  "
                 "점 사이(1/SR)는 **모든 소리에 같고**, 주기 T는 **음마다 다르다**.", 13),
    ]
    h = S.card(40, y, S.W - 80, "파형 지도 — 용어가 그림 어디에 있나", wave_items, tsize=21)
    y += h + 34

    c1 = ("샘플 · 샘플 수 N", [
        ("p", "**샘플** = 한 순간에 읽은 소리 값 **하나**(배열의 원소 1개).  **샘플 수 N** = 배열 전체의 개수.", 14),
        ("p", "공식  `N = SR × t`   (t는 초)", 15),
        ("p", "예) 도를 **0.4초** 녹음 → `16000 × 0.4 = 6400`개", 14),
        ("code", ["sample_count = int(round(sr * duration))"]),
        ("note", "★ **N은 전체** 샘플 수.  한 주기의 샘플 수(⑦)와 다르다. 길이(초)는 N이 아니라 `N ÷ SR`(③).", 12.5),
    ], dict(num="①"))
    c2 = ("샘플링 레이트 SR", [
        ("p", "소리를 **1초에 몇 번 읽어서 기록**하나.  단위 **Hz = 샘플/초**.  이 수업은 `SR = 16000` (16 kHz, 1 kHz = 1000 Hz).", 14),
        ("p", "샘플 간격 `1/SR` = 1 ÷ 16000 = **0.0625 ms**  (그림의 ② 간격)", 14),
        ("p", "SR을 2배 → 점이 **2배 촘촘**해질 뿐 **소리 높이는 그대로**.", 14),
        ("note", "★ 주파수 f와 **단위가 같은 Hz**지만 다르다: **f = 소리가 진동하는 횟수, SR = 기록하는 횟수**.", 12.5),
    ], dict(num="②"))
    y = S.row(y, [(c1[0], c1[1], c1[2], 1), (c2[0], c2[1], c2[2], 1)])

    c3 = ("길이 t (초)", [
        ("p", "배열이 나타내는 **시간**.", 14),
        ("p", "공식  `t = N ÷ SR`", 15),
        ("p", "예) `6400 ÷ 16000 = 0.4초`.   같은 **32000개**도 SR 16000이면 **2초**, SR 8000이면 **4초**.", 14),
        ("code", ["seconds = sample_count / sample_rate"]),
        ("note", "★ 길이는 **그 배열을 만든 SR**로 나눈다.  단위 확인: (샘플) ÷ (샘플/초) = **초**.", 12.5),
    ], dict(num="③"))
    c4 = ("진폭 A", [
        ("p", "기준선(0)에서 **얼마나 크게 흔들리나** = **소리 크기**.  그림에서 파형의 **최대 높이**.", 14),
        ("p", "예) `A = 0.1` vs `A = 0.3`: 같은 f라서 반복 간격은 같고 **높이만 3배**.  forte(f)·piano(p) ≈ 진폭 크기†", 14),
        ("code", ["louder = make_tone(frequency=440, duration=0.5, amplitude=0.3)"], 11.4),
        ("note", "★ `make_tone`은 진폭 **0 ~ 0.8**만 허용.  진폭을 바꿔도 **음 높이는 그대로**.", 12.5),
    ], dict(num="④"))
    y = S.row(y, [(c3[0], c3[1], c3[2], 1), (c4[0], c4[1], c4[2], 1)])

    c5 = ("주파수 f", [
        ("p", "**1초에 파형이 몇 번 반복**(진동)하나.  단위 **Hz = 진동/초** = **음의 높낮이**.  f가 클수록 높은 음.", 14),
        ("p", "예) 도 262 · 레 294 · 미 330 · 파 349 · 솔 392 · 라 **440** Hz", 14),
        ("p", "**옥타브**† = f가 **정확히 2배**인 음 사이의 간격 (도 262 → 높은 도 524).  수업 코드의 220·440·880·1760이 라(A)의 옥타브.", 13.5),
        ("code", ["notes = [262, 294, 330, 349, 392]"]),
        ("note", "★ f는 **소리 자체의 성질**.  기록 방식인 SR(②)과 헷갈리지 말 것.", 12.5),
    ], dict(num="⑤"))
    c6 = ("주기 T", [
        ("p", "파형이 **한 번 오르내리는 데 걸리는 시간**.  f의 **역수**.", 14),
        ("p", "공식  `T = 1 ÷ f`  (초)   `T = 1000 ÷ f`  (ms)", 15),
        ("p", "예) 262 Hz → `1000 ÷ 262` = **3.82 ms**.   440 Hz → **2.27 ms**.   **f 2배 → T 절반**.", 14),
        ("code", ["period_ms = 1 / frequency * 1000"]),
        ("note", "★ **주기 T**(소리의 성질)와 **샘플 간격 1/SR**(기록 간격)은 둘 다 시간이지만 **다른 것**.", 12.5),
    ], dict(num="⑥"))
    y = S.row(y, [(c5[0], c5[1], c5[2], 1), (c6[0], c6[1], c6[2], 1)])

    c7 = ("한 주기의 샘플 수", [
        ("p", "한 번 오르내림을 **몇 개의 점으로 기록**하나.", 14),
        ("p", "공식  `SR ÷ f`   ( = T ÷ (1/SR) )", 15),
        ("p", "예) `16000 ÷ 262` = **61.1개**(소수여도 정상).   f 2배(524 Hz) → **30.5개**.   `f = SR/2`면 **2개**.", 14),
        ("code", ["samples_per_period = SR / frequency"]),
        ("note", "★ **전체 N**과 혼동 금지.  왜 `SR ÷ f`인지는 시트 ②의 Q2.", 12.5),
    ], dict(num="⑦"))
    c8 = ("n번째 샘플의 시각", [
        ("p", "n번째 점을 **몇 초(ms)에 읽었나**.  n은 **0부터** 센다.", 14),
        ("p", "공식  `시각(초) = n ÷ SR`    `시각(ms) = n ÷ SR × 1000`", 15),
        ("p", "예) n=0 → **0 ms** · n=16 → **1 ms** · n=159 → **9.9375 ms** · (0.4초 음의 마지막 n=6399 → 399.9375 ms)", 14),
        ("code", ["time = np.arange(len(tone)) / SR"]),
        ("note", "★ ms로 바꿀 땐 `÷ SR` **다음에** `× 1000`.  \"처음 10 ms\" = `SR × 0.01` = 160개 (0.01 = 10 ms를 **초**로 쓴 값). 시트 ② Q4.", 12.5),
    ], dict(num="⑧"))
    y = S.row(y, [(c7[0], c7[1], c7[2], 1), (c8[0], c8[1], c8[2], 1)])

    c9 = ("사인파  y(t) = A·sin(2π·f·t)", [
        ("p", "**A 진폭 · f 주파수 · t 시간** 세 값으로 소리 하나가 완전히 정해진다.  `make_tone`이 소리를 만드는 **핵심 한 줄**.", 14),
        ("code", ["sound = amplitude * np.sin(2 * np.pi * frequency * time)"], 11.4),
        ("p", "예) A=0.3, f=262 Hz:  t=0.9375 ms(n=15) → **0.300**(꼭대기) · t=1.875 ms(n=30) → **0.016**(≈0) · t=2.875 ms(n=46) → **-0.300**", 14),
        ("note", "★ 주기 T만큼 지나면 같은 값: `y(t) = y(t+T)`.  왜 2π? 시트 ② Q5.", 12.5),
    ], dict(num="⑨"))
    c10 = ("나이퀴스트 SR÷2 (한계)", [
        ("p", "구분해서 기록할 수 있는 **최대 주파수** = `SR ÷ 2` = **8000 Hz**.  (**그 미만**만 가능)", 14),
        ("p", "예) 9000 Hz를 기록하면 **7000 Hz와 똑같은 샘플**이 나와 7000 Hz로 둔갑†.   → 시트 ② Q1", 14),
        ("code", ["if not (0 < frequency < sr / 2):"]),
        ("note", "★ `make_tone`의 f는 **0 < f < SR/2**.  f = SR/2(8000 Hz)도 안 됨(소리가 0이 될 수 있음).", 12.5),
    ], dict(num="⑩"))
    y = S.row(y, [(c9[0], c9[1], c9[2], 1), (c10[0], c10[1], c10[2], 1)])

    note_rows = [
        ["**음**", "도", "레", "미", "파", "솔", "라"],
        ["**f (Hz)**", "262", "294", "330", "349", "392", "440"],
        ["**T (ms)**", "3.82", "3.40", "3.03", "2.87", "2.55", "2.27"],
        ["**SR÷f (개)**", "61.1", "54.4", "48.5", "45.8", "40.8", "36.4"],
    ]
    c11 = ("음 높이 · 옥타브† · 반음†", [
        ("table", [1.5, 1, 1, 1, 1, 1, 1], note_rows, 13.5, True),
        ("p", "**높은 음 = f가 크다 = T가 짧다 = 한 주기의 점이 적다.**  건반은 왼쪽이 낮은 음, 오른쪽이 높은 음.", 14),
        ("p", "**옥타브**† `×2` (도 262 → 524).   **반음 1칸**† = f에 `× 1.0595` (= 2의 12제곱근), **12번 곱하면 ×2 = 1옥타브**.  자세한 이야기는 시트 ② Q6·Q7.", 14),
        ("code", ["for frequency in [220, 440, 880, 1760]:"]),
        ("note", "† = 수업 자료에는 없던 보충 설명.   `코드` = 수업 노트북에서 인용.   ★ = 주의할 점.", 12.5),
    ], dict(num="⑪"))
    c12 = ("단위 · 재생 · 자주 쓰는 코드", [
        ("table", [1.15, 2.4], [
            ["**1 kHz**", "= 1000 Hz   (16 kHz = 16000 Hz)"],
            ["**1 초**", "= 1000 ms     (ms → 초: `÷ 1000`)"],
            ["**처음 10 ms**", "= `SR × 0.01`개 (0.01 = 10ms의 초 단위)"],
            ["**단위 검산**", "(샘플/초) × 초 = 샘플,   (샘플) ÷ (샘플/초) = 초"],
        ], 13.2, False),
        ("code", ["display(Audio(tone, rate=SR, normalize=False))",
                  "repeats_10ms = frequency * 0.01   # 10 ms 동안 반복 횟수"], 11.4),
        ("note", "★ `rate`는 **그 배열을 만든 SR**과 같게.  `normalize=False`는 소리 크기를 자동으로 키우지 않는다는 뜻.", 12.5),
    ], dict(num="⑫"))
    y = S.row(y, [(c11[0], c11[1], c11[2], 1.15), (c12[0], c12[1], c12[2], 1)])

    story = [
        ("p", "**주인공: 0.4초짜리 \"도\"(262 Hz)**.  스피커 막이 **1초에 262번**({p|⑤ 주파수 f = 262 Hz}) 떨립니다. 한 번 떨리는 데 걸리는 시간이 {p|⑥ 주기 T = 1÷262 = 3.82 ms}. "
              "떨림의 세기는 {u|④ 진폭 A = 0.3}이고, 이걸 `A·sin(2π·f·t)`로 쓴 것이 {p|⑨ 사인파}입니다.", 14.5),
        ("p", "**녹음기**는 1초에 **16000번** 소리를 읽습니다({b|② SR = 16000}). 그러니 **1/16000초 = 0.0625 ms마다 \"찰칵\"** 하고 값을 하나 저장합니다. 이 값 하나가 **① 샘플**입니다.", 14.5),
        ("p", "녹음 시간은 **0.4초**({b|③ 길이 t})이니 찰칵 횟수, 즉 **① 샘플 수 N = SR × t = 16000 × 0.4 = 6400개**. 배열 길이가 6400이고, 길이를 거꾸로 확인하면 `6400 ÷ 16000 = 0.4초`.", 14.5),
        ("p", "**n번째 찰칵**은 녹음을 시작하고 `n × 0.0625 ms`가 지난 순간입니다({b|⑧ 시각 = n ÷ SR}). 첫 찰칵(n=0)은 0 ms, n=16은 1 ms, n=160은 10 ms. 그래서 `time = np.arange(len(tone)) / SR`로 가로축을 만듭니다.", 14.5),
        ("p", "도 한 번 떨림(3.82 ms) 동안 찰칵은 몇 번? {p|⑦ SR ÷ f = 16000 ÷ 262 = 61.1번}. 즉 부드러운 곡선 한 번을 **약 61개의 점**으로 기록한 셈입니다.", 14.5),
        ("p", "소리를 **한 옥타브 올려**(f ×2 = 524 Hz) 같은 SR로 녹음하면 주기는 **절반**(1.91 ms), 한 주기의 점도 **절반**(30.5개). 점이 모자라지 않으려면 f는 {u|⑩ SR÷2 = 8000 Hz 미만}이어야 하고, `make_tone`이 이를 검사합니다.", 14.5),
        ("p", "마지막으로 **SR만 8000으로** 바꾸면? 소리 높이(f)는 그대로, 점 간격은 0.125 ms로 **성겨지고**, 같은 0.4초는 **3200개**가 됩니다. {y|★ SR은 \"기록 촘촘함\", f는 \"소리 높낮이\".}", 14.5),
    ]
    h = S.card(40, y, S.W - 80, "스토리로 recap — \"도\" 한 음을 녹음하는 하루", story, tsize=21, head=PUR, fill=PUR_BG, edge=PUR)
    y += h + 30
    S.ax.text(S.W / 2, y + 14, "수업 노트북: 017_sound/01_소리가_숫자가_되는_과정.ipynb   |   만든 코드: make_sound_cheatsheet.py   |   † 보충 설명은 일반 지식(음악·신호처리)이며 이 환경에서 출처를 확인한 것은 아닙니다",
              fontsize=12.2, fontfamily=BODY, color=G_MID, ha="center", va="center")
    return S, y + 60


# =====================================================================
#  시트 2: 심화 Q&A
# =====================================================================
def build_sheet2(H=8400):
    S = Sheet(2400, H)
    y = S.header("소리 CHEAT SHEET ②  심화 Q&A",
                 "시트 ①을 보다가 \"왜?\"가 생기는 7가지.  각 칸은 결론 → 이유 → 숫자 예시 순서   |   † = 수업 자료에는 없던 보충 설명   ★ = 주의",
                 "ICT 혁신 스퀘어 · 017_sound")

    q1_text = [
        ("p", "**결론**: 숫자로 **저장은 되지만 \"구분\"이 안 된다.**  SR÷2 이상의 소리는 **더 낮은 주파수의 소리와 똑같은 샘플**이 되어, 어떤 소리였는지 **알아낼 수 없다**(에일리어싱†).", 14.5),
        ("p", "**왜 (why)**: 한 주기의 점 수는 `SR ÷ f`.  이 값이 **2 미만**(= f > SR÷2)이면 오르내림을 따라가기엔 점이 모자라서, 점들이 **다른 느린 파형** 위에도 그대로 놓입니다.", 14.5),
        ("p", "**왜 \"미만\"인가 (why not 같음)**: f = SR÷2 = 8000 Hz는 한 주기에 점이 **딱 2개**. 점이 파형의 0점에만 찍히면 `sin`은 **샘플이 전부 0**(소리가 사라짐), `cos`은 +1, -1이 번갈아 나와 **위상에 따라 달라집니다**.", 14.5),
        ("table", [1.1, 1.0, 2.6], [
            ["**실제 f**", "**기록되는 f**", "**이유 (SR = 16000, 계산으로 확인)**"],
            ["9000 Hz", "{p|7000 Hz}", "`cos` 샘플이 n = 0~63 **모두 일치** (16000 - 9000 = 7000)"],
            ["15000 Hz", "{p|1000 Hz}", "샘플 값 1.000, 0.924, 0.707, 0.383 … **똑같음**"],
            ["16000 Hz", "{p|0 Hz}", "샘플이 **전부 1** (변하지 않는 값)"],
        ], 13.5, True),
        ("p", "규칙†: SR÷2 < f < SR 이면 기록되는 주파수 = `SR - f`.  이름과 일반 규칙은 † 보충, 위 표의 숫자는 직접 계산.", 13),
        ("note", "★ 그래서 `make_tone`은 `f ≥ SR/2`를 아예 **막아 둡니다**(ValueError).  실제 녹음은 SR/2를 넘는 소리가 섞이지 않게 **필터**로 미리 거른다는 것이 코드 주석의 \"경계에서 여유를 두고 필터\"의 뜻으로 보입니다(제 해석).", 12.5),
    ]
    q1_fig = [
        ("p", "SR = 16000으로 기록한 샘플(●)은 **두 소리에서 완전히 같은 점**입니다.", 14),
        ("fig", 600, alias_figure, True),
        ("p", "점만 보면 **7000 Hz인지 9000 Hz인지 구별 불가** → 높은 소리가 낮은 소리로 \"접혀\" 들어옵니다.", 14),
    ]
    y = S.row(y, [("Q1. SR÷2 이상은 표현이 불가능한가?  (나이퀴스트)", q1_text, dict(num="Q1"), 1.35),
                  ("그림: 9000 Hz가 7000 Hz로 둔갑", q1_fig, dict(head=PUR, fill=PUR_BG, edge=PUR), 1)])

    q2_left = [
        ("p", "**결론**: 1초에 점이 `SR`개, 파형이 `f`번 반복 → **한 번 반복(한 주기)당 점 = SR ÷ f**.", 14.5),
        ("p", "**길 ① 나눠 세기(사탕)**  사탕 **16000개**를 봉지 **262개**에 똑같이 나눠 담으면 봉지당 `16000 ÷ 262` = **61.07개**.  여기서 사탕 = 샘플, 봉지 = 주기.", 14.5),
        ("p", "**길 ② 시간 비교**  한 주기가 걸리는 시간 `T = 1/f = 3.817 ms`, 점은 `1/SR = 0.0625 ms`마다 하나.  **점 개수 = T ÷ (1/SR) = 3.817 ÷ 0.0625 = 61.07개**.  (식으로는 `(1/f) ÷ (1/SR) = SR/f`)", 14.5),
        ("p", "**단위**  (샘플/초) ÷ (주기/초) = **샘플/주기**.  초가 약분되어 \"주기 한 번당 샘플 수\"만 남습니다.", 14.5),
        ("p", "**검산**  `61.07 × 262 ≈ 16000`  (한 주기 점 수 × 1초의 주기 수 = 1초의 전체 점 수).", 14.5),
        ("note", "★ **소수(61.07)가 나오는 건 정상**.  주기가 점 간격의 정수배가 아니라서, 어떤 주기는 61개 어떤 주기는 62개로 찍힙니다.", 12.5),
    ]
    q2_right = [
        ("fig", 520, cycle_figure, True),
        ("table", [1.2, 1.3, 1.3], [
            ["**f (Hz)**", "**T (ms)**", "**SR ÷ f**"],
            ["262", "3.82", "61.1"],
            ["524 (×2)", "1.91", "30.5"],
            ["1000", "1.00", "16.0"],
            ["8000", "0.125", "2.0 (경계)"],
        ], 13.5, True),
    ]
    y = S.row(y, [("Q2. 한 주기의 샘플 수가 왜 SR ÷ f 인가?", q2_left, dict(num="Q2"), 1.25),
                  ("그림: 도 한 주기 = 점 약 61개", q2_right, dict(head=LIME_D, fill="#f7fee7", edge=LIME_D), 1)])

    q3 = [
        ("p", "**이야기**: 녹음기는 녹음 버튼을 누른 순간부터 **1/16000초(0.0625 ms)마다 \"찰칵\"** 하고 소리를 읽어 저장합니다.  **n = 찰칵 번호**(0부터).  첫 찰칵은 버튼을 누른 바로 그 순간이라 n=0, 시각 0.", 14.5),
        ("fig", 330, timeline_figure),
        ("table", [0.8, 1.2, 3.0], [
            ["**n**", "**시각**", "**계산**"],
            ["0", "0 ms", "`0 ÷ 16000`  (녹음 시작 순간)"],
            ["16", "1 ms", "`16 ÷ 16000 = 0.001초`  (1초에 16000개이므로 1 ms에 16개)"],
            ["160", "10 ms", "`160 ÷ 16000 = 0.01초`"],
            ["6399", "399.9375 ms", "`6399 ÷ 16000`  (0.4초 음의 마지막 점, 0.4초 직전)"],
        ], 13.5, True),
        ("p", "**코드**: `time = np.arange(len(tone)) / SR` → `time[n]`이 n번째 샘플의 시각(초).  그래프에서는 ms로 보려고 `time[:160] * 1000`.", 14),
        ("note", "★ 한 줄 요약: **시각 = 샘플 번호 × 샘플 간격 = n × (1/SR) = n ÷ SR**.   n은 파이썬 인덱스처럼 **0부터**.", 12.5),
    ]
    q4 = [
        ("p", "**0.01의 단위는 초(s)**.  10 ms = 10 ÷ 1000 초 = **0.01초**.  공식 `N = SR × t`의 **t 자리에 0.01초를 넣은** 것입니다.", 14.5),
        ("p", "`16000 × 0.01 = 160`개   (단위: (샘플/초) × 초 = 샘플)", 14.5),
        ("p", "**별도 공식인가? → 아닙니다.**  새로운 법칙이 아니라 `N = SR × t`의 **한 경우(계산 예시)** 입니다.  그래서 시트 ①에서는 공식 목록에서 빼고 ⑫ 단위표에 계산 예시로 옮겼습니다.", 14.5),
        ("p", "**그런데 자주 쓰는 이유**: 그래프에서 소리의 **앞부분만 확대**할 때 구간 길이를 샘플 개수로 바꾸는 패턴입니다.  수업 코드의 `time[:160] * 1000`에서 **160 = 16000 × 0.01** 입니다(앞 10 ms).", 14.5),
        ("note", "† 앞으로 배울 음성 처리(STFT)에서도 \"창 길이(예: 25 ms) × SR = 샘플 수\" 같은 **같은 계산**이 반복됩니다(일반 지식, 이번에 확인한 것은 아님).  중요한 것은 **ms를 초로 바꿔 SR에 곱한다**는 습관입니다.", 12.5),
    ]
    y = S.row(y, [("Q3. n번째 샘플의 시각은 무슨 뜻인가?  (타임라인)", q3, dict(num="Q3"), 1.3),
                  ("Q4. 처음 10 ms = SR × 0.01 ?", q4, dict(num="Q4", head=PUR, fill=PUR_BG, edge=PUR), 1)])

    q5_left = [
        ("p", "**풀어 읽기** (도: A=0.3, f=262 Hz, t = 1.875 ms 일 때)", 14.5),
        ("p", "① `f × t` = 262 × 0.001875 = **0.491** → \"지금까지 **0.491 바퀴**(주기) 돌았다\"", 14.5),
        ("p", "② `2π × 0.491` = **3.087 rad** → sin 함수는 **각도(라디안)** 를 받고, **한 바퀴 = 2π**라서 \"바퀴 수 × 2π\"로 각도를 만든다", 14.5),
        ("p", "③ `sin(3.087)` = **0.055**  →  ④ `A × 0.055` = 0.3 × 0.055 ≈ **0.016**  (거의 0: 한 바퀴의 절반 부근이라 0을 지나는 중)", 14.5),
        ("p", "**이야기**: 초침 끝이 원 위를 돈다고 상상하세요.  한 바퀴가 한 주기, 초침의 **높이**가 소리의 값입니다.  f는 \"1초에 몇 바퀴\", A는 \"원의 반지름\", t가 지나면 바퀴 수 `f × t`가 늘고, 그 순간의 높이가 `y(t)`.", 14.5),
        ("p", "**왜 중요한가**  ① 이 한 줄이 `make_tone`이 **소리를 만드는** 전부.  ② A·f·t **세 값으로 순수한 소리 하나가 완전히 정해진다.**  ③ 앞으로 배울 FFT·스펙트로그램은 복잡한 소리를 **이런 사인파의 합으로 분해**해서 \"어떤 f가 얼마나 큰 A로 들어 있나\"를 보는 것†.", 14.5),
        ("note", "★ `y(t) = y(t+T)`: **주기 T만큼 지나면 같은 값**으로 돌아옴(주기적).  440 Hz에서 `t`와 `t+1/440`을 비교하면 최대 차이가 `4e-13`(계산 오차)였습니다.", 12.5),
    ]
    q5_right = [
        ("fig", 520, sine_figure, True),
        ("table", [0.6, 1.1, 1.5], [
            ["**n**", "**t (ms)**", "**y = 0.3·sin(2π·262·t)**"],
            ["0", "0", "0.000"],
            ["15", "0.9375", "{u|0.300} (꼭대기)"],
            ["30", "1.875", "0.016 (≈0)"],
            ["46", "2.875", "{u|-0.300} (바닥)"],
            ["61", "3.8125", "-0.002 (한 주기 끝 ≈ 0)"],
        ], 13, True),
    ]
    y = S.row(y, [("Q5. 사인파 공식 — 풀어 읽기와 왜 중요한가", q5_left, dict(num="Q5"), 1.35),
                  ("그림: 도(262 Hz)의 사인파와 계산한 점", q5_right, dict(head=BLU, fill=BLU_BG, edge=BLU), 1)])

    q6 = [
        ("p", "**용어입니다.**  **옥타브(octave)** = 주파수가 **정확히 2배**(또는 ½)인 두 음 사이의 간격.  같은 이름의 음(도 → 높은 도)으로 들립니다.", 14.5),
        ("p", "**수업 자료에는 없던 용어**†입니다. 제가 \"낮은 음이 뭐야?\" 질문에 답하면서 도입했어요.  그래서 시트 ①에서는 \"무엇을 바꾸면 무엇이 달라지나\" 표의 **한 줄**이 아니라 **용어**로 다루는 것이 맞아, ⑤ 주파수 카드와 ⑪ 음 높이 카드에 넣었습니다.", 14.5),
        ("p", "**수업 코드와의 연결**: 수업의 `for frequency in [220, 440, 880, 1760]:` 이 라(A)의 **옥타브 4개**(×2씩)입니다.  주기가 절반씩 줄어드는 것을 출력으로 봤습니다.", 14.5),
        ("table", [1, 1, 1, 1], [
            ["**음**", "**f (Hz)**", "**T (ms)**", "**SR÷f**"],
            ["라 A3", "220", "4.55", "72.7"],
            ["라 A4", "440", "2.27", "36.4"],
            ["라 A5", "880", "1.14", "18.2"],
            ["라 A6", "1760", "0.57", "9.1"],
        ], 13.5, True),
    ]
    q7 = [
        ("p", "**네, 주파수(Hz)에 곱하는 비율**입니다.  `1.0595 = 2의 12제곱근 = 2^(1/12)`.  12번 곱하면 `2^(12/12) = 2` → **한 옥타브**.  계산: `1.0594631^12 = 2.0000000`.", 14.5),
        ("p", "**이야기**  피아노 한 옥타브는 반음 12칸(흰건반 7 + 검은건반 5).  도(261.63)에서 반음마다 `× 1.0595`를 곱해 올라가면 도#(277.18) → 레(293.66) … 라(440.00, 9칸) … 높은 도(523.25, 12칸).  **수업의 262·294·330·349·392는 이 값을 반올림**한 것입니다.", 14.5),
        ("p", "**평균율(12-TET)†**: 한 옥타브를 **12개의 같은 비율 칸**으로 나눈 조율.  어느 음에서 시작해도 음정의 비율이 같아서 **조(key)를 바꿔도**(이조) 음 사이 관계가 그대로입니다.  그래서 **한 대의 피아노로 모든 조성**을 칠 수 있습니다.", 14.5),
        ("p", "**바흐와의 관계†**: 바흐의 『평균율 클라비어곡집』(1722)은 **24개 모든 장·단조**로 쓴 곡집으로 유명해서 \"모든 조를 쓸 수 있는 조율\"의 상징처럼 이야기됩니다.  다만 당시의 \"well-tempered\"가 오늘날의 **12평균율**(모든 반음 비율이 정확히 동일)과 **똑같았는지는 학자들 사이에 논쟁**이 있습니다.", 14.5),
        ("note", "† 평균율·바흐 설명은 일반 지식이고 **이번에 출처를 확인하지 못했습니다**.  숫자(1.0595, 12제곱, 각 음의 Hz)는 직접 계산했습니다.  "
                 "참고: 수업의 도 262를 2배 하면 524지만 건반의 정확한 높은 도는 523.25 Hz — 262가 261.63을 **반올림한 값**이라서 생기는 작은 차이입니다.", 12.5),
        ("fig", 470, keyboard_figure),
    ]
    y = S.row(y, [("Q6. 옥타브는 용어인가?  (수업 자료에 있었나)", q6, dict(num="Q6"), 1),
                  ("Q7. 반음 1칸 = f × 1.0595?  평균율·바흐와 관계?", q7, dict(num="Q7", head=PUR, fill=PUR_BG, edge=PUR), 1.45)])

    S.ax.text(S.W / 2, y + 14, "수업 노트북: 017_sound/01_소리가_숫자가_되는_과정.ipynb   |   만든 코드: make_sound_cheatsheet.py   |   † 보충 설명은 일반 지식(음악·신호처리)",
              fontsize=12.2, fontfamily=BODY, color=G_MID, ha="center", va="center")
    return S, y + 60


def save(S, y_end, path):
    S.fig.savefig(path, dpi=DPI, facecolor=BG)
    print("saved", os.path.basename(path), "| 내용 끝 y =", int(y_end), "/ 캔버스 높이", S.H)


if __name__ == "__main__":
    verify_quotes()
    here = os.path.dirname(os.path.abspath(__file__))
    # 1차: 큰 캔버스로 내용 높이를 재고, 2차: 그 높이에 맞춰 다시 그린다
    for builder, name in [(build_sheet1, "sound_cheatsheet_1_main.png"), (build_sheet2, "sound_cheatsheet_2_deep.png")]:
        _, y_end = builder()
        plt.close("all")
        S, y_end = builder(int(y_end) + 10)
        save(S, y_end, os.path.join(here, name))
        plt.close("all")
