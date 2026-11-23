"""Diagrams for Day 11: Moore's Law, what it really says, and is it dead? Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"
SI = "#3a4a66"
COPPER = "#e0915a"
METAL = "#b8c4d2"
PKG = "#20262f"
GATE = "#7f8fa6"


def wide(w=14, h=6.6):
    fig = plt.figure(figsize=(w, h), dpi=100)
    ax = fig.add_axes([0.02, 0.03, 0.96, 0.94]); ax.set_axis_off()
    ax.set_xlim(0, w); ax.set_ylim(0, h)
    return fig, ax


def square(w=10, h=9.6):
    fig = plt.figure(figsize=(w, h), dpi=100)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96]); ax.set_axis_off()
    ax.set_xlim(0, w); ax.set_ylim(0, h)
    return fig, ax


def tag(ax, x, y, text, col=GREEN, fs=18, z=9):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=col, weight="bold", zorder=z,
            bbox=dict(fc=BG, ec=col, boxstyle="round,pad=0.4", lw=2))


def arrow(ax, a, b, col=WHITE, lw=3, rad=0.0, z=6, ms=26):
    ax.annotate("", xy=b, xytext=a, zorder=z,
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, mutation_scale=ms, connectionstyle=f"arc3,rad={rad}"))


# ---------------------------------------------------------------- 1. Moore's 1965 chart
fig, ax = wide()
X0, X1, Y0 = 1.6, 12.6, 0.7
yr = lambda y: X0 + (y - 1959) * (X1 - X0) / 16
lv = lambda p: Y0 + p * 0.3          # p = power of two
ax.plot([X0, X1 + 0.3], [Y0, Y0], color=MUTED, lw=2)
ax.plot([X0, X0], [Y0, lv(16) + 0.3], color=MUTED, lw=2)
for y in (1959, 1962, 1965, 1968, 1971, 1975):
    ax.text(yr(y), Y0 - 0.35, str(y), ha="center", fontsize=15, color=MUTED)
for p, lab in ((0, "1"), (4, "16"), (8, "256"), (12, "4,000"), (16, "65,000")):
    ax.plot([X0 - 0.1, X1], [lv(p)] * 2, color=GRID, lw=1.5, zorder=0)
    ax.text(X0 - 0.2, lv(p), lab, ha="right", va="center", fontsize=15, color=MUTED)
ax.text(X0 - 0.2, lv(16) + 0.5, "parts per chip", ha="left", fontsize=17, color=CYAN, weight="bold")
ax.text(X1 - 0.2, lv(16) + 0.5, "Moore, 1965", ha="right", fontsize=19, color=WHITE, weight="bold")
ax.text(X1 + 0.35, Y0 + 0.05, "year", ha="left", va="center", fontsize=15, color=MUTED)
ax.text(X0 + 0.25, lv(14.6), "each line up = 16 times more", ha="left", fontsize=14, color=MUTED)
anchor("axes", ax, yr(1962), lv(7)); anchor("yaxis", ax, X0 - 0.55, lv(8))
save_step(fig, OUT + "day11_paper_0.png")

pts = [(1959, 0), (1962, 3), (1963, 4), (1964, 5), (1965, 6)]
ax.plot([yr(a) for a, _ in pts], [lv(b) for _, b in pts], color=CYAN, lw=3, zorder=3)
for a, b in pts:
    ax.add_patch(P.Circle((yr(a), lv(b)), 0.13, color=CYAN, zorder=4))
ax.text(yr(1959) + 0.9, lv(0) + 0.06, "1 part", fontsize=15, color=CYAN, weight="bold")
ax.text(yr(1965) + 0.25, lv(6) - 0.15, "about 64", fontsize=15, color=CYAN, weight="bold")
anchor("p59", ax, yr(1959), lv(0)); anchor("p65", ax, yr(1965), lv(6))
anchor("p62", ax, yr(1962), lv(3)); anchor("p64", ax, yr(1964), lv(5))
save_step(fig, OUT + "day11_paper_1.png")

ax.plot([yr(1965), yr(1975)], [lv(6), lv(16)], color=AMBER, lw=3, ls=(0, (6, 4)), zorder=3)
ax.add_patch(P.Circle((yr(1975), lv(16)), 0.16, color=AMBER, zorder=4))
tag(ax, yr(1975) - 1.6, lv(16) - 0.15, "about 65,000?", AMBER, fs=17)
ax.text(yr(1970) + 0.4, lv(10.2), "keep doubling\nevery year", ha="left", fontsize=15, color=AMBER)
anchor("p75", ax, yr(1975), lv(16)); anchor("p70", ax, yr(1970), lv(11))
save(fig, OUT + "day11_paper_2.png")


# ---------------------------------------------------------------- 2. Doubling: a magic coin jar
def jar(ax, x, y, n, col=AMBER, w=1.45, h=2.2):
    ax.add_patch(P.FancyBboxPatch((x - w / 2, y), w, h, boxstyle="round,pad=0.05", fc=SEAT, ec=MUTED, lw=2, zorder=2))
    ax.add_patch(P.Rectangle((x - w / 2 + 0.1, y + h - 0.02), w - 0.2, 0.18, color=MUTED, zorder=3))
    cols = 1 if n == 1 else 2 if n <= 4 else 4 if n <= 16 else 8
    rows = int(np.ceil(n / cols))
    s = min((w - 0.2) / cols, (h - 0.3) / max(rows, 1))
    r = s * 0.42
    for k in range(n):
        i, j = k % cols, k // cols
        cx = x - (cols - 1) * s / 2 + i * s
        cy = y + 0.15 + r + j * s
        ax.add_patch(P.Circle((cx, cy), r, color=col, zorder=4))
    ax.text(x, y - 0.45, f"{n}", ha="center", fontsize=22, color=WHITE, weight="bold")


fig, ax = wide()
ax.text(7, 6.05, "A magic jar: the coins double every day", ha="center", fontsize=23, weight="bold")
JX = [1.2 + 1.9 * i for i in range(7)]
NS = [1, 2, 4, 8, 16, 32, 64]
for k in range(3):
    jar(ax, JX[k], 2.6, NS[k])
    ax.text(JX[k], 5.1, f"day {k + 1}", ha="center", fontsize=15, color=MUTED)
for k in range(7):
    anchor(f"j{k}", ax, JX[k], 3.6)
save_step(fig, OUT + "day11_double_0.png")
for k in range(3, 7):
    jar(ax, JX[k], 2.6, NS[k])
    ax.text(JX[k], 5.1, f"day {k + 1}", ha="center", fontsize=15, color=MUTED)
save_step(fig, OUT + "day11_double_1.png")
tag(ax, 7, 0.9, "after 30 doublings: over 1,000,000,000 coins", GREEN, fs=21)
anchor("big", ax, 7, 0.9)
save(fig, OUT + "day11_double_2.png")


# ---------------------------------------------------------------- 3. The self-fulfilling loop (split, square)
fig, ax = square()
C = (5.0, 4.8); RR = 3.0
nodes = [("pred", "the prediction", "double every\ntwo years", CYAN, 90),
         ("plan", "everyone plans", "chipmakers, tools,\ndesigners", AMBER, 0),
         ("invest", "invest & invent", "billions spent\nto stay on time", VIOLET, -90),
         ("real", "it comes true", "and the pattern\ncontinues", GREEN, 180)]
pos = {}
for k, (nm, t1, t2, col, ang) in enumerate(nodes):
    a = np.radians(ang)
    x, y = C[0] + RR * np.cos(a), C[1] + RR * np.sin(a)
    pos[nm] = (x, y)
for k, (nm, t1, t2, col, ang) in enumerate(nodes):
    x, y = pos[nm]
    ax.add_patch(P.FancyBboxPatch((x - 1.45, y - 0.75), 2.9, 1.5, boxstyle="round,pad=0.06", fc=SEAT, ec=col, lw=3, zorder=3))
    ax.text(x, y + 0.3, t1, ha="center", va="center", fontsize=19, color=col, weight="bold", zorder=4)
    ax.text(x, y - 0.3, t2, ha="center", va="center", fontsize=13, color=MUTED, zorder=4, linespacing=1.1)
    anchor(nm, ax, x, y)
    if k > 0:
        a0 = np.radians(nodes[k - 1][4] - 32); a1 = np.radians(ang + 32)
        arrow(ax, (C[0] + RR * np.cos(a0), C[1] + RR * np.sin(a0)), (C[0] + RR * np.cos(a1), C[1] + RR * np.sin(a1)),
              MUTED, lw=3, rad=-0.25)
    if k == 3:
        a0 = np.radians(180 - 32); a1 = np.radians(90 + 32)
        arrow(ax, (C[0] + RR * np.cos(a0), C[1] + RR * np.sin(a0)), (C[0] + RR * np.cos(a1), C[1] + RR * np.sin(a1)),
              MUTED, lw=3, rad=-0.25)
        ax.text(C[0], C[1], "a target\nthat makes\nitself come true", ha="center", va="center", fontsize=16,
                color=WHITE, weight="bold", zorder=4)
    save_step(fig, OUT + f"day11_loop_{k}.png") if k < 3 else save(fig, OUT + f"day11_loop_{k}.png")


# ---------------------------------------------------------------- 4. Sixty years on the line (real chips, log scale)
fig, ax = wide()
X0, X1, Y0 = 1.9, 13.0, 0.75
yx = lambda y: X0 + (y - 1970) * (X1 - X0) / 56
ly = lambda n: Y0 + (np.log10(n) - 3) * 0.6       # 10^3 .. 10^12
ax.plot([X0, X1], [Y0, Y0], color=MUTED, lw=2)
ax.plot([X0, X0], [Y0, ly(1e12)], color=MUTED, lw=2)
for y in (1970, 1980, 1990, 2000, 2010, 2020):
    ax.text(yx(y), Y0 - 0.38, str(y), ha="center", fontsize=15, color=MUTED)
for e, lab in ((3, "thousand"), (6, "million"), (9, "billion"), (12, "trillion")):
    ax.plot([X0, X1], [ly(10 ** e)] * 2, color=GRID, lw=1.5, zorder=0)
    ax.text(X0 - 0.15, ly(10 ** e), lab, ha="right", va="center", fontsize=15, color=MUTED)
ax.text(X0 + 0.1, ly(1e12) + 0.3, "transistors per chip  (each line up = 10 times more)", ha="left", fontsize=15, color=CYAN)
anchor("axis", ax, X0 - 0.8, ly(1e6))
chips = [(1971, 2300, "Intel 4004", "c71", 0), (1978, 29000, "8086", "c78", 0), (1985, 275000, "386", "c85", 0),
         (1993, 3.1e6, "Pentium", "c93", 1), (2000, 42e6, "Pentium 4", "c00", 1), (2006, 291e6, "Core 2", "c06", 1),
         (2011, 2.27e9, "Core i7", "c11", 2), (2020, 54.2e9, "A100", "c20", 2),
         (2024, 208e9, "Blackwell", "c24", 2)]
for st in range(3):
    for (y, n, nm, an, s) in chips:
        if s != st:
            continue
        x, yy = yx(y), ly(n)
        ax.add_patch(P.Circle((x, yy), 0.13, color=[CYAN, AMBER, GREEN][s], zorder=5))
        ax.text(x + 0.2, yy - 0.32 if an != "c71" else yy + 0.12, nm, ha="left", fontsize=13, color=[CYAN, AMBER, GREEN][s], weight="bold", zorder=5)
        anchor(an, ax, x, yy)
    save_step(fig, OUT + f"day11_trend_{st}.png")
ts = np.array([1976, 2025])
ax.plot(yx(ts), ly(2300 * 2 ** ((ts - 1971) / 2)), color=WHITE, lw=2.5, ls=(0, (6, 4)), zorder=4, alpha=.8)
tag(ax, yx(1984), ly(3e9), "doubling about every two years", WHITE, fs=17)
anchor("trend", ax, yx(1984), ly(3e9))
save(fig, OUT + "day11_trend_3.png")


# ---------------------------------------------------------------- 5. The trick: shrink everything
def card(ax, x, y, words, fs, w=3.4, h=2.6):
    ax.add_patch(P.FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.05", fc="#e9eef4", ec=WHITE, lw=2, zorder=2))
    ax.text(x, y, words, ha="center", va="center", fontsize=fs, color="#1b2b44", weight="bold", zorder=3, linespacing=1.15)


fig, ax = wide()
ax.text(2.4, 6.0, "big writing", ha="center", fontsize=20, weight="bold", color=AMBER)
card(ax, 2.4, 3.6, "chips\nare\nsmall", 30)
ax.text(2.4, 1.85, "3 words fit", ha="center", fontsize=16, color=MUTED)
anchor("card1", ax, 2.4, 3.6)
save_step(fig, OUT + "day11_shrink_0.png")
arrow(ax, (4.3, 3.6), (5.0, 3.6), MUTED)
ax.text(6.9, 6.0, "smaller writing", ha="center", fontsize=20, weight="bold", color=CYAN)
card(ax, 6.9, 3.6, "chips are small\nand they keep\ngetting smaller", 17)
ax.text(6.9, 1.85, "same card, twice the words", ha="center", fontsize=16, color=MUTED)
anchor("card2", ax, 6.9, 3.6)
save_step(fig, OUT + "day11_shrink_1.png")
ax.plot([9.1, 9.1], [0.6, 6.2], color=GRID, lw=2)
ax.text(11.6, 6.0, "on a chip", ha="center", fontsize=20, weight="bold", color=GREEN)
S = 2.0
ax.add_patch(P.Rectangle((9.6, 3.0), S, S, fc=SI, ec=AMBER, lw=3, zorder=3))
ax.text(9.6 + S / 2, 3.0 + S / 2, "old\nsize", ha="center", va="center", fontsize=15, color=WHITE, weight="bold", zorder=4)
ax.text(9.6 + S / 2, 2.65, "area 1", ha="center", fontsize=15, color=AMBER)
s = S * 0.7
# two shrunk squares stacked, same total area as the old one
ax.add_patch(P.Rectangle((12.0, 3.0), s, s, fc=SI, ec=CYAN, lw=3, zorder=3))
ax.add_patch(P.Rectangle((12.0, 3.0 + s + 0.05), s, s, fc=SI, ec=CYAN, lw=3, zorder=3))
ax.text(12.0 + s / 2, 3.0 + s / 2, "new", ha="center", va="center", fontsize=14, color=WHITE, weight="bold", zorder=4)
ax.text(12.0 + s / 2, 3.0 + 1.5 * s + 0.05, "new", ha="center", va="center", fontsize=14, color=WHITE, weight="bold", zorder=4)
ax.text(12.0 + s + 0.15, 3.0 + s / 2, "0.7", ha="left", va="center", fontsize=15, color=CYAN)
ax.text(12.0 + s / 2, 2.65, "each about half", ha="center", fontsize=15, color=CYAN)
tag(ax, 11.6, 1.4, "sides x 0.7  =  half the area", GREEN, fs=16)
ax.text(11.6, 0.55, "twice as many on the same chip", ha="center", fontsize=15, color=MUTED)
anchor("big", ax, 9.6 + S / 2, 3.0 + S / 2); anchor("small", ax, 12.0 + s / 2, 3.0 + s / 2)
anchor("pair", ax, 12.0 + s / 2, 3.0 + s); anchor("tag", ax, 11.6, 1.4)
save(fig, OUT + "day11_shrink_2.png")


# ---------------------------------------------------------------- 6. The free lunch ends: clock speed hits the heat wall
fig, ax = wide()
X0, X1, Y0 = 1.6, 12.8, 0.8
cx = lambda y: X0 + (y - 1990) * (X1 - X0) / 35
cy = lambda g: Y0 + g * 0.82          # GHz
ax.plot([X0, X1], [Y0, Y0], color=MUTED, lw=2)
ax.plot([X0, X0], [Y0, cy(6.2)], color=MUTED, lw=2)
for y in (1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025):
    ax.text(cx(y), Y0 - 0.38, str(y), ha="center", fontsize=15, color=MUTED)
for g in (0, 2, 4, 6):
    ax.plot([X0, X1], [cy(g)] * 2, color=GRID, lw=1.5, zorder=0)
    ax.text(X0 - 0.15, cy(g), f"{g}", ha="right", va="center", fontsize=15, color=MUTED)
ax.text(X0 + 0.1, cy(6.2) + 0.2, "top chip speed  (billions of ticks a second)", ha="left", fontsize=15, color=CYAN)
rise = [(1990, 0.033), (1993, 0.066), (1995, 0.13), (1997, 0.3), (1999, 0.6), (2000, 1.3), (2002, 2.8), (2004, 3.8)]
ax.plot([cx(a) for a, _ in rise], [cy(b) for _, b in rise], color=CYAN, lw=4, zorder=3)
ax.text(cx(1996.5) - 0.2, cy(2.5), "smaller = faster", ha="center", fontsize=17, color=CYAN, weight="bold")
for nm, (a, b) in zip(("r0", "r1", "r2", "r3"), ((1990, 0.033), (1999, 0.6), (2002, 2.8), (2004, 3.8))):
    anchor(nm, ax, cx(a), cy(b))
anchor("rise", ax, cx(1999), cy(1.4))
save_step(fig, OUT + "day11_heat_0.png")
flat = [(2004, 3.8), (2007, 3.3), (2010, 3.6), (2013, 4.0), (2016, 4.2), (2019, 5.0), (2022, 5.5), (2025, 5.7)]
ax.plot([cx(a) for a, _ in flat], [cy(b) for _, b in flat], color=AMBER, lw=4, zorder=3)
ax.add_patch(P.Rectangle((cx(2004.6) - 0.12, cy(0.2)), 0.24, cy(6.0) - cy(0.2), color=RED, alpha=.35, zorder=1))
tag(ax, cx(2005), cy(1.0), "the heat wall", RED, fs=17)
ax.text(cx(2016), cy(3.0), "only a slow climb", ha="center", fontsize=17, color=AMBER, weight="bold")
anchor("wall", ax, cx(2005), cy(1.0)); anchor("flat", ax, cx(2014), cy(4.1))
save_step(fig, OUT + "day11_heat_1.png")
# more cores instead
bx, by = cx(2016) - 1.1, cy(0.35)
ax.add_patch(P.FancyBboxPatch((bx, by), 2.2, 1.55, boxstyle="round,pad=0.04", fc=PKG, ec=GREEN, lw=3, zorder=4))
for i in range(4):
    for j in range(2):
        ax.add_patch(P.Rectangle((bx + 0.15 + 0.5 * i, by + 0.15 + 0.65 * j), 0.4, 0.55, color=GREEN, alpha=.8, zorder=5))
ax.text(bx + 2.45, by + 0.78, "more cores\ninstead", ha="left", va="center", fontsize=16, color=GREEN, weight="bold")
anchor("cores", ax, bx + 1.1, by + 0.78)
save(fig, OUT + "day11_heat_2.png")


# ---------------------------------------------------------------- 7. Build up, not out: transistors go 3D (end-on views)
fig, ax = wide()
XS = [1.9, 5.3, 8.7, 12.1]
ax.text(XS[0], 6.05, "a city builds up", ha="center", fontsize=19, weight="bold", color=AMBER)
ax.add_patch(P.Rectangle((0.5, 0.9), 2.8, 0.12, color=MUTED, zorder=2))
for (x, w, h) in ((0.75, 0.55, 0.8), (1.45, 0.6, 3.6), (2.2, 0.55, 2.4), (2.85, 0.35, 0.6)):
    ax.add_patch(P.Rectangle((x, 1.02), w, h, fc=SEAT, ec=AMBER, lw=2, zorder=3))
    for yy in np.arange(1.25, 1.02 + h - 0.2, 0.4):
        ax.add_patch(P.Rectangle((x + 0.12, yy), w - 0.24, 0.16, color=AMBER, alpha=.6, zorder=4))
ax.text(XS[0], 0.4, "short of land? go tall", ha="center", fontsize=15, color=MUTED)
anchor("city", ax, XS[0], 2.6)
save_step(fig, OUT + "day11_3d_0.png")


def base(ax, x):
    ax.add_patch(P.Rectangle((x - 1.3, 0.9), 2.6, 0.9, fc=SI, ec=VIOLET, lw=2, zorder=2))
    ax.text(x, 1.3, "silicon", ha="center", va="center", fontsize=13, color=MUTED, zorder=3)


# planar
x = XS[1]
ax.text(x, 6.05, "flat", ha="center", fontsize=19, weight="bold", color=CYAN)
base(ax, x)
ax.add_patch(P.Rectangle((x - 1.0, 1.8), 2.0, 0.35, color=CYAN, zorder=3))
ax.add_patch(P.Rectangle((x - 1.0, 2.15), 2.0, 0.8, fc=GATE, ec=WHITE, lw=2, zorder=3))
ax.text(x, 2.55, "gate", ha="center", va="center", fontsize=14, color=BG, weight="bold", zorder=4)
ax.text(x, 3.4, "gate on top only", ha="center", fontsize=14, color=MUTED)
ax.text(x, 0.4, "until about 2011", ha="center", fontsize=15, color=MUTED)
anchor("g0", ax, x, 2.2)
save_step(fig, OUT + "day11_3d_1.png")
# finfet
x = XS[2]
ax.text(x, 6.05, "fin", ha="center", fontsize=19, weight="bold", color=CYAN)
base(ax, x)
ax.add_patch(P.Rectangle((x - 0.85, 1.8), 1.7, 2.5, fc=GATE, ec=WHITE, lw=2, zorder=3))
ax.add_patch(P.Rectangle((x - 0.25, 1.8), 0.5, 2.0, color=CYAN, zorder=4))
ax.text(x, 4.0, "gate", ha="center", va="center", fontsize=14, color=BG, weight="bold", zorder=5)
ax.text(x, 4.75, "gate on 3 sides", ha="center", fontsize=14, color=MUTED)
ax.text(x, 0.4, "from about 2011", ha="center", fontsize=15, color=MUTED)
anchor("g1", ax, x, 2.8)
save_step(fig, OUT + "day11_3d_2.png")
# gate-all-around nanosheets
x = XS[3]
ax.text(x, 6.05, "gate all around", ha="center", fontsize=19, weight="bold", color=GREEN)
base(ax, x)
ax.add_patch(P.Rectangle((x - 1.1, 1.8), 2.2, 3.0, fc=GATE, ec=WHITE, lw=2, zorder=3))
for k in range(3):
    ax.add_patch(P.Rectangle((x - 0.75, 2.2 + 0.8 * k), 1.5, 0.3, color=CYAN, zorder=4))
ax.text(x, 4.5, "gate", ha="center", va="center", fontsize=14, color=BG, weight="bold", zorder=5)
ax.text(x, 5.25, "stacked sheets", ha="center", fontsize=14, color=MUTED)
ax.text(x, 0.4, "newest chips, 2020s", ha="center", fontsize=15, color=MUTED)
anchor("g2", ax, x, 3.2)
for k in range(3):
    arrow(ax, (XS[k] + 1.35, 2.6), (XS[k + 1] - 1.4, 2.6), MUTED, lw=2.5) if k > 0 else None
save(fig, OUT + "day11_3d_3.png")


# ---------------------------------------------------------------- 8. Chiplets: team up and stack (split, square)
fig, ax = square()
ax.text(5, 9.0, "one giant chip", ha="center", fontsize=21, weight="bold", color=AMBER)
ax.add_patch(P.Rectangle((2.6, 5.0), 4.8, 3.4, fc=SI, ec=AMBER, lw=3, zorder=2))
for i in range(8):
    for j in range(5):
        ax.add_patch(P.Rectangle((2.8 + 0.58 * i, 5.2 + 0.62 * j), 0.42, 0.44, color=CYAN, alpha=.55, zorder=3))
fx, fy = 6.3, 7.6
ax.add_patch(P.Circle((fx, fy), 0.32, color=RED, zorder=5))
ax.text(5, 4.45, "one tiny flaw can spoil it all", ha="center", fontsize=16, color=RED)
anchor("big", ax, 5, 6.7); anchor("flaw", ax, fx, fy)
save_step(fig, OUT + "day11_chiplets_0.png")
# split into chiplets (below)
ax.text(5, 3.95, "small chiplets, joined on one base", ha="center", fontsize=19, weight="bold", color=GREEN)
CX = [1.6, 3.9, 6.2, 8.5]
cols = [CYAN, CYAN, VIOLET, GREEN]
for k, x in enumerate(CX):
    ax.add_patch(P.Rectangle((x - 0.9, 1.45), 1.8, 1.6, fc=SI, ec=cols[k], lw=3, zorder=4))
    for i in range(3):
        for j in range(2):
            ax.add_patch(P.Rectangle((x - 0.75 + 0.52 * i, 1.65 + 0.7 * j), 0.38, 0.5, color=cols[k], alpha=.55, zorder=5))
    anchor(f"c{k + 1}", ax, x, 2.25)
save_step(fig, OUT + "day11_chiplets_1.png")
ax.add_patch(P.FancyBboxPatch((0.4, 0.7), 9.2, 0.55, boxstyle="round,pad=0.04", fc=PKG, ec=MUTED, lw=2, zorder=3))
ax.text(5, 0.25, "one base, very short links", ha="center", fontsize=15, color=MUTED)
for k in range(3):
    ax.add_patch(P.Rectangle((CX[k] + 0.9, 1.0), CX[k + 1] - CX[k] - 1.8, 0.14, color=COPPER, zorder=4))
anchor("base", ax, 5, 1.6)
save_step(fig, OUT + "day11_chiplets_2.png")
# stack memory on top of the last chiplet
x = CX[3]
for k in range(2):
    ax.add_patch(P.Rectangle((x - 0.8, 3.05 + 0.02 + 0.28 * k), 1.6, 0.24, fc="#2d6b5e", ec=GREEN, lw=1.5, zorder=6))
ax.text(x - 1.0, 3.35, "stacked", ha="right", va="center", fontsize=14, color=GREEN, weight="bold", zorder=6)
anchor("stack", ax, x, 3.0)
save(fig, OUT + "day11_chiplets_3.png")
print("figs ok")
