"""Diagrams for Day 10: What is a chip (integrated circuit)? Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"
BOARD = "#14324a"
SI = "#3a4a66"
COPPER = "#e0915a"
METAL = "#b8c4d2"
PKG = "#20262f"


def wide(w=14, h=6.6):
    fig = plt.figure(figsize=(w, h), dpi=100)
    ax = fig.add_axes([0.02, 0.03, 0.96, 0.94]); ax.set_axis_off()
    ax.set_xlim(0, w); ax.set_ylim(0, h)
    return fig, ax


def tag(ax, x, y, text, col=GREEN, fs=18, z=9):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=col, weight="bold", zorder=z,
            bbox=dict(fc=BG, ec=col, boxstyle="round,pad=0.4", lw=2))


def arrow(ax, a, b, col=WHITE, lw=3, rad=0.0, z=6, ms=26):
    ax.annotate("", xy=b, xytext=a, zorder=z,
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, mutation_scale=ms, connectionstyle=f"arc3,rad={rad}"))


# ---------------------------------------------------------------- parts
def transistor(ax, x, y, s=1.0, z=4):
    ax.add_patch(P.Wedge((x, y), 0.35 * s, 0, 180, color="#2b2f36", zorder=z))
    ax.add_patch(P.Rectangle((x - 0.35 * s, y - 0.08 * s), 0.7 * s, 0.08 * s, color="#2b2f36", zorder=z))
    for dx in (-0.2, 0, 0.2):
        ax.plot([x + dx * s, x + dx * s], [y - 0.08 * s, y - 0.55 * s], color=METAL, lw=2.2 * s, zorder=z - 1)


def resistor(ax, x, y, s=1.0, z=4):
    ax.plot([x - 0.6 * s, x + 0.6 * s], [y, y], color=METAL, lw=2.2 * s, zorder=z - 1)
    ax.add_patch(P.FancyBboxPatch((x - 0.32 * s, y - 0.12 * s), 0.64 * s, 0.24 * s, boxstyle="round,pad=0.04",
                                  color="#d9b98a", zorder=z))
    for dx, c in ((-0.17, RED), (-0.05, VIOLET), (0.07, AMBER)):
        ax.add_patch(P.Rectangle((x + dx * s, y - 0.14 * s), 0.06 * s, 0.28 * s, color=c, zorder=z + 1))


def capacitor(ax, x, y, s=1.0, z=4):
    ax.add_patch(P.FancyBboxPatch((x - 0.2 * s, y - 0.1 * s), 0.4 * s, 0.6 * s, boxstyle="round,pad=0.04",
                                  color="#3e7cc9", zorder=z))
    ax.add_patch(P.Rectangle((x - 0.24 * s, y + 0.38 * s), 0.48 * s, 0.1 * s, color=METAL, zorder=z + 1))
    for dx in (-0.1, 0.1):
        ax.plot([x + dx * s, x + dx * s], [y - 0.1 * s, y - 0.5 * s], color=METAL, lw=2.2 * s, zorder=z - 1)


# ---------------------------------------------------------------- 1. Before chips: hand-wired circuits
fig, ax = wide()
ax.text(2.6, 6.05, "separate parts", ha="center", fontsize=21, weight="bold", color=CYAN)
transistor(ax, 2.6, 4.5, 1.3); ax.text(2.6, 3.45, "transistor", ha="center", fontsize=16, color=MUTED)
resistor(ax, 2.6, 2.7, 1.3); ax.text(2.6, 2.1, "resistor", ha="center", fontsize=16, color=MUTED)
capacitor(ax, 2.6, 0.95, 1.1); ax.text(3.35, 0.9, "capacitor", ha="left", fontsize=16, color=MUTED)
for nm, xy in {"parts": (2.6, 3.0), "trans": (2.6, 4.4), "res": (2.6, 2.6)}.items():
    anchor(nm, ax, *xy)
save_step(fig, OUT + "day10_tangle_0.png")

ax.add_patch(P.FancyBboxPatch((5.4, 0.6), 8.1, 5.0, boxstyle="round,pad=0.05", fc=BOARD, ec=GREEN, lw=3, zorder=1))
ax.text(9.45, 6.05, "a circuit, wired by hand", ha="center", fontsize=21, weight="bold", color=GREEN)
rng = np.random.default_rng(3)
pos = [(6.4 + 1.65 * i, 1.5 + 1.45 * j) for j in range(3) for i in range(5)]
kinds = [transistor, resistor, capacitor]
for k, (x, y) in enumerate(pos):
    kinds[k % 3](ax, x, y, 0.62, z=5)
for k in range(len(pos) - 1):
    (x0, y0), (x1, y1) = pos[k], pos[(k + 4) % len(pos)]
    t = np.linspace(0, 1, 30)
    bend = rng.uniform(-0.5, 0.5)
    ax.plot(x0 + (x1 - x0) * t, y0 - 0.3 + (y1 - y0) * t + bend * np.sin(np.pi * t), color=AMBER, lw=1.8, alpha=.85, zorder=3)
for nm, xy in {"board": (9.45, 3.0), "w0": (6.4, 1.2), "w1": (8.05, 2.65), "w2": (9.7, 4.1), "w3": (11.35, 2.65),
               "w4": (13.0, 1.2)}.items():
    anchor(nm, ax, *xy)
save_step(fig, OUT + "day10_tangle_1.png")

jx, jy = 11.35, 3.8
ax.add_patch(P.Circle((jx, jy), 0.42, fill=False, ec=RED, lw=4, zorder=8))
ax.plot([jx - 0.25, jx + 0.25], [jy - 0.25, jy + 0.25], color=RED, lw=4, zorder=8)
ax.plot([jx - 0.25, jx + 0.25], [jy + 0.25, jy - 0.25], color=RED, lw=4, zorder=8)
tag(ax, 9.45, 0.25, "one bad joint = the whole circuit fails", RED, fs=17)
anchor("joint", ax, jx, jy); anchor("fail", ax, 9.45, 0.3)
save(fig, OUT + "day10_tangle_2.png")


# ---------------------------------------------------------------- 2. The big idea: make everything at once
def page(ax, x, y, lines, col=MUTED, w=2.6, h=3.0):
    ax.add_patch(P.FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.04", fc="#e9eef4", ec=WHITE, lw=2, zorder=2))
    for k in range(lines):
        ll = w * (0.75 if k % 3 else 0.6)
        ax.plot([x - w / 2 + 0.25, x - w / 2 + 0.25 + ll], [y + h / 2 - 0.4 - 0.32 * k] * 2, color="#3a4a66", lw=4, zorder=3)


fig, ax = wide()
ax.text(2.4, 6.05, "copy by hand", ha="center", fontsize=21, weight="bold", color=AMBER)
page(ax, 2.4, 3.3, 3)
ax.plot([2.9, 3.6], [3.95, 4.9], color=AMBER, lw=7, solid_capstyle="round", zorder=4)
ax.plot([2.9, 2.83], [3.95, 3.83], color=WHITE, lw=4, zorder=4)
ax.text(2.4, 1.3, "one letter at a time", ha="center", fontsize=17, color=MUTED)
anchor("pen", ax, 2.4, 3.3)
save_step(fig, OUT + "day10_print_0.png")

arrow(ax, (4.2, 3.3), (5.1, 3.3), MUTED, lw=3)
ax.text(7.0, 6.05, "print", ha="center", fontsize=21, weight="bold", color=CYAN)
ax.add_patch(P.Rectangle((5.6, 4.9), 2.8, 0.45, color=CYAN, zorder=4))
ax.add_patch(P.Rectangle((6.85, 5.35), 0.3, 0.5, color=CYAN, zorder=4))
page(ax, 7.0, 3.0, 7)
ax.plot([5.7, 8.3], [4.6, 4.6], color=CYAN, lw=2, ls=":", zorder=3)
ax.text(7.0, 1.0, "the whole page at once", ha="center", fontsize=17, color=MUTED)
anchor("press", ax, 7.0, 3.6)
save_step(fig, OUT + "day10_print_1.png")

arrow(ax, (8.8, 3.3), (9.7, 3.3), MUTED, lw=3)
ax.text(11.7, 6.05, "a chip", ha="center", fontsize=21, weight="bold", color=GREEN)
ax.add_patch(P.Rectangle((10.2, 1.8), 3.0, 3.0, fc=SI, ec=GREEN, lw=3, zorder=2))
for i in range(4):
    for j in range(4):
        x, y = 10.55 + 0.75 * i, 2.15 + 0.75 * j
        ax.add_patch(P.Rectangle((x, y), 0.3, 0.3, color=AMBER, zorder=4))
        if i < 3:
            ax.plot([x + 0.3, x + 0.75], [y + 0.15, y + 0.15], color=COPPER, lw=2, zorder=3)
        if j < 3:
            ax.plot([x + 0.15, x + 0.15], [y + 0.3, y + 0.75], color=COPPER, lw=2, zorder=3)
ax.text(11.7, 1.25, "all parts + wires, together,", ha="center", fontsize=16, color=MUTED)
ax.text(11.7, 0.8, "in one piece of silicon", ha="center", fontsize=16, color=MUTED)
anchor("chip", ax, 11.7, 3.3)
save(fig, OUT + "day10_print_2.png")


# ---------------------------------------------------------------- 3. Inside a chip: a city in layers
fig, ax = wide()
ax.text(7, 6.15, "Slice a chip open: a city in layers", ha="center", fontsize=23, weight="bold")
ax.add_patch(P.Rectangle((1.0, 0.4), 9.4, 1.0, fc=SI, ec=VIOLET, lw=3, zorder=2))
GX = [1.7 + 1.15 * i for i in range(8)]
for x in GX:
    ax.add_patch(P.Rectangle((x - 0.25, 1.4), 0.5, 0.3, color=METAL, zorder=3))
    ax.add_patch(P.Rectangle((x - 0.45, 1.1), 0.25, 0.3, color=AMBER, alpha=.8, zorder=3))
    ax.add_patch(P.Rectangle((x + 0.2, 1.1), 0.25, 0.3, color=AMBER, alpha=.8, zorder=3))
ax.text(10.7, 1.05, "transistors", ha="left", va="center", fontsize=18, color=VIOLET, weight="bold")
ax.text(10.7, 0.62, "(the houses)", ha="left", va="center", fontsize=15, color=MUTED)
anchor("tr", ax, 5.7, 1.3); anchor("trlab", ax, 11.6, 0.9)
save_step(fig, OUT + "day10_layers_0.png")

# thin local wiring layers
for k, y in enumerate((2.0, 2.5, 3.0)):
    for i in range(7):
        x0 = 1.5 + 1.15 * i + (0.3 if k % 2 else 0)
        ax.add_patch(P.Rectangle((x0, y), 0.8, 0.18, color=COPPER, zorder=3))
    for i in range(0, 8, 2 if k else 1):
        ax.add_patch(P.Rectangle((GX[i] - 0.05 + (0.3 if k % 2 else 0) * 0, y - 0.32), 0.1, 0.32, color=COPPER, alpha=.8, zorder=3))
ax.text(10.7, 2.6, "thin copper wires", ha="left", va="center", fontsize=18, color=COPPER, weight="bold")
ax.text(10.7, 2.17, "(the streets)", ha="left", va="center", fontsize=15, color=MUTED)
anchor("local", ax, 5.7, 2.5); anchor("loclab", ax, 11.8, 2.45)
save_step(fig, OUT + "day10_layers_1.png")

for k, (y, h) in enumerate(((3.6, 0.3), (4.25, 0.4))):
    for i in range(4):
        ax.add_patch(P.Rectangle((1.4 + 2.3 * i, y), 1.7, h, color=COPPER, zorder=3))
        ax.add_patch(P.Rectangle((2.15 + 2.3 * i, y - 0.42), 0.18, 0.42, color=COPPER, alpha=.8, zorder=3))
ax.text(10.7, 4.2, "thick wires up top", ha="left", va="center", fontsize=18, color=COPPER, weight="bold")
ax.text(10.7, 3.77, "(the highways)", ha="left", va="center", fontsize=15, color=MUTED)
anchor("global", ax, 5.7, 4.1); anchor("glolab", ax, 11.8, 4.0)
save_step(fig, OUT + "day10_layers_2.png")

for i in range(4):
    x = 2.25 + 2.3 * i
    ax.add_patch(P.Rectangle((x - 0.08, 4.65), 0.16, 0.35, color=METAL, zorder=3))
    ax.add_patch(P.Circle((x, 5.25), 0.3, color=METAL, zorder=4))
ax.text(10.7, 5.25, "contacts to the", ha="left", va="center", fontsize=18, color=WHITE, weight="bold")
ax.text(10.7, 4.85, "outside world", ha="left", va="center", fontsize=18, color=WHITE, weight="bold")
for nm, xy in {"pad": (6.85, 5.25), "v0": (4.0, 1.4), "v1": (4.0, 2.1), "v2": (4.55, 3.0), "v3": (4.55, 3.75),
               "v4": (4.6, 4.45), "v5": (6.85, 4.45), "v6": (6.85, 5.25)}.items():
    anchor(nm, ax, *xy)
save(fig, OUT + "day10_layers_3.png")


# ---------------------------------------------------------------- 4. From switches to a brain: building blocks
def block(ax, x, y, title, sub, col, inner):
    ax.add_patch(P.FancyBboxPatch((x - 1.35, y - 1.25), 2.7, 2.5, boxstyle="round,pad=0.06", fc=SEAT, ec=col, lw=3, zorder=2))
    inner(ax, x, y + 0.15)
    ax.text(x, y - 1.75, title, ha="center", fontsize=19, color=col, weight="bold")
    ax.text(x, y - 2.25, sub, ha="center", fontsize=15, color=MUTED)


def in_tr(ax, x, y):
    transistor(ax, x, y + 0.1, 1.2, z=4)


def in_gate(ax, x, y):
    ax.add_patch(P.Wedge((x - 0.1, y), 0.55, -90, 90, color=CYAN, zorder=4))
    ax.add_patch(P.Rectangle((x - 0.6, y - 0.55), 0.5, 1.1, color=CYAN, zorder=4))
    for dy in (-0.3, 0.3):
        ax.plot([x - 1.0, x - 0.6], [y + dy] * 2, color=WHITE, lw=2.5, zorder=3)
    ax.plot([x + 0.45, x + 0.9], [y, y], color=WHITE, lw=2.5, zorder=3)
    ax.text(x - 0.25, y, "AND", ha="center", va="center", fontsize=12, color=BG, weight="bold", zorder=5)


def in_adder(ax, x, y):
    for i in range(3):
        for j in range(2):
            ax.add_patch(P.Rectangle((x - 0.9 + 0.65 * i, y - 0.55 + 0.65 * j), 0.45, 0.45, color=CYAN, alpha=.85, zorder=4))
    ax.text(x, y + 0.85, "1 + 1 = 2", ha="center", fontsize=14, color=AMBER, weight="bold", zorder=5)


def in_cpu(ax, x, y):
    ax.add_patch(P.Rectangle((x - 0.75, y - 0.75), 1.5, 1.5, fc=PKG, ec=GREEN, lw=2, zorder=4))
    for k in range(5):
        d = -0.6 + 0.3 * k
        for (a, b, c, e) in ((x + d, y + 0.75, x + d, y + 0.95), (x + d, y - 0.75, x + d, y - 0.95),
                             (x - 0.75, y + d, x - 0.95, y + d), (x + 0.75, y + d, x + 0.95, y + d)):
            ax.plot([a, c], [b, e], color=METAL, lw=2.5, zorder=3)
    ax.add_patch(P.Rectangle((x - 0.45, y - 0.45), 0.9, 0.9, color=GREEN, alpha=.6, zorder=5))


fig, ax = wide()
XS = [1.9, 5.3, 8.7, 12.1]
block(ax, XS[0], 3.7, "transistor", "one switch", AMBER, in_tr)
anchor("b0", ax, XS[0], 3.2)
save_step(fig, OUT + "day10_build_0.png")
arrow(ax, (XS[0] + 1.45, 3.7), (XS[1] - 1.45, 3.7), MUTED)
block(ax, XS[1], 3.7, "logic gate", "a few switches", CYAN, in_gate)
anchor("b1", ax, XS[1], 3.2)
save_step(fig, OUT + "day10_build_1.png")
arrow(ax, (XS[1] + 1.45, 3.7), (XS[2] - 1.45, 3.7), MUTED)
block(ax, XS[2], 3.7, "adder", "dozens of gates", CYAN, in_adder)
anchor("b2", ax, XS[2], 3.2)
save_step(fig, OUT + "day10_build_2.png")
arrow(ax, (XS[2] + 1.45, 3.7), (XS[3] - 1.45, 3.7), MUTED)
block(ax, XS[3], 3.7, "processor", "billions of switches", GREEN, in_cpu)
for nm, xy in {"b3": (XS[3], 3.2), "f0": (XS[0], 5.15), "f1": (XS[1], 5.15), "f2": (XS[2], 5.15), "f3": (XS[3], 5.15)}.items():
    anchor(nm, ax, *xy)
save(fig, OUT + "day10_build_3.png")


# ---------------------------------------------------------------- 5. Many chips on one wafer
fig, ax = wide()
WX, WY, R = 3.6, 3.2, 2.75
ax.add_patch(P.Circle((WX, WY), R, color="#9fb3c8", zorder=2))
s = 0.42
cells = []
for x in np.arange(WX - R, WX + R, s):
    for y in np.arange(WY - R, WY + R, s):
        if all((x + a - WX) ** 2 + (y + b - WY) ** 2 < R ** 2 for a in (0, s) for b in (0, s)):
            ax.add_patch(P.Rectangle((x + 0.03, y + 0.03), s - 0.06, s - 0.06, color=CYAN, alpha=.75, zorder=3))
            cells.append((x, y))
ax.text(WX, 0.05, "a wafer: one thin disc of silicon", ha="center", fontsize=17, color=MUTED)
anchor("wafer", ax, WX, WY)
save_step(fig, OUT + "day10_wafer_0.png")

hx, hy = min(cells, key=lambda c: (c[0] - WX - 0.4) ** 2 + (c[1] - WY - 0.4) ** 2)
ax.add_patch(P.Rectangle((hx, hy), s, s, fc=AMBER, ec=WHITE, lw=2, zorder=5))
ax.plot([hx + s, 7.6], [hy + s, 5.4], color=AMBER, lw=1.5, ls="--", zorder=4)
ax.plot([hx + s, 7.6], [hy, 1.4], color=AMBER, lw=1.5, ls="--", zorder=4)
ax.add_patch(P.Rectangle((7.6, 1.4), 4.0, 4.0, fc=SI, ec=AMBER, lw=3, zorder=5))
rng = np.random.default_rng(7)
for i in range(6):
    for j in range(6):
        c = [CYAN, GREEN, VIOLET, AMBER][(i * 7 + j * 3) % 4]
        ax.add_patch(P.Rectangle((7.85 + 0.6 * i, 1.65 + 0.6 * j), 0.5, 0.5, color=c, alpha=.35 + 0.4 * rng.random(), zorder=6))
ax.text(9.6, 5.85, "one die = one chip", ha="center", fontsize=20, color=AMBER, weight="bold")
anchor("die", ax, hx + s / 2, hy + s / 2); anchor("dieZ", ax, 9.6, 3.4)
save_step(fig, OUT + "day10_wafer_1.png")

ax.add_patch(P.FancyBboxPatch((12.1, 2.3), 1.6, 2.2, boxstyle="round,pad=0.04", fc=PKG, ec=MUTED, lw=2, zorder=5))
for k in range(5):
    y = 2.5 + 0.45 * k
    ax.plot([11.85, 12.1], [y, y], color=METAL, lw=3, zorder=4); ax.plot([13.7, 13.95], [y, y], color=METAL, lw=3, zorder=4)
ax.add_patch(P.Rectangle((12.55, 3.05), 0.7, 0.7, color=SI, ec=AMBER, lw=1.5, zorder=6))
arrow(ax, (11.65, 3.4), (12.05, 3.4), AMBER, lw=2, ms=18, z=7)
ax.text(12.9, 1.6, "packaged", ha="center", fontsize=17, color=WHITE, weight="bold")
ax.text(12.9, 1.15, "chip", ha="center", fontsize=17, color=WHITE, weight="bold")
anchor("pkg", ax, 12.9, 3.0)
save(fig, OUT + "day10_wafer_2.png")


# ---------------------------------------------------------------- 6. From one to billions (log scale)
DATA = [("1958", "first chip", 1, "1 transistor"),
        ("1971", "first microprocessor", 2300, "2,300"),
        ("1993", "a 1990s PC chip", 3.1e6, "3 million"),
        ("2024", "a big AI chip", 208e9, "208 billion")]


def count_fig(n):
    fig, ax = wide()
    ax.text(7, 6.25, "Transistors on one chip", ha="center", fontsize=23, weight="bold")
    X0, X1, Y0, Y1 = 2.6, 13.4, 0.9, 5.6
    lv = lambda v: Y0 + (Y1 - Y0) * np.log10(max(v, 1)) / 12
    for v, name in ((1, "one"), (1e3, "a thousand"), (1e6, "a million"), (1e9, "a billion"), (1e12, "a trillion")):
        ax.plot([X0, X1], [lv(v)] * 2, color=GRID, lw=2, zorder=1)
        ax.text(X0 - 0.2, lv(v), name, ha="right", va="center", fontsize=15, color=MUTED)
    for k, (yr, what, v, lab) in enumerate(DATA):
        x = 3.9 + 2.85 * k
        anchor(f"c{k}", ax, x, lv(v) + 0.25)
        anchor(f"cb{k}", ax, x, (Y0 + lv(v)) / 2 + 0.1)
        if k >= n:
            continue
        top = max(lv(v), Y0 + 0.12)
        ax.add_patch(P.Rectangle((x - 0.6, Y0), 1.2, top - Y0, color=PALETTE[k % 4] if k < 3 else GREEN, zorder=3))
        ax.text(x, top + 0.25, lab, ha="center", fontsize=17, weight="bold", color=WHITE, zorder=4)
        ax.text(x, Y0 - 0.32, yr, ha="center", fontsize=17, weight="bold", color=AMBER)
        ax.text(x, Y0 - 0.72, what, ha="center", fontsize=14, color=MUTED)
    return fig, ax


for n in range(1, 5):
    fig, ax = count_fig(n)
    (save if n == 4 else save_step)(fig, OUT + f"day10_count_{n - 1}.png")
    plt.close(fig)


# ---------------------------------------------------------------- 7. Kinds of chips (split, 2x2)
fig = plt.figure(figsize=(8.4, 8.1), dpi=100)
ax = fig.add_axes([0.02, 0.02, 0.96, 0.96]); ax.set_axis_off(); ax.set_xlim(0, 8.4); ax.set_ylim(0, 8.1)
TILES = [(2.1, 6.0, "processor", "thinks", GREEN), (6.3, 6.0, "memory", "remembers", CYAN),
         (2.1, 2.0, "sensor", "senses", AMBER), (6.3, 2.0, "power chip", "controls energy", VIOLET)]


def tile(ax, k):
    x, y, t, sub, c = TILES[k]
    ax.add_patch(P.FancyBboxPatch((x - 1.8, y - 1.75), 3.6, 3.5, boxstyle="round,pad=0.06", fc=SEAT, ec=c, lw=3, zorder=2))
    cy = y + 0.62
    if k == 0:
        in_cpu(ax, x, cy)
    elif k == 1:
        for j in range(3):
            ax.add_patch(P.Rectangle((x - 1.0, cy - 0.65 + 0.48 * j), 2.0, 0.36, fc=PKG, ec=c, lw=2, zorder=4))
            for i in range(6):
                ax.add_patch(P.Rectangle((x - 0.9 + 0.31 * i, cy - 0.59 + 0.48 * j), 0.2, 0.24,
                                         color=c, alpha=.9 if (i + j) % 3 else .3, zorder=5))
    elif k == 2:
        ax.add_patch(P.Circle((x, cy), 0.8, fc=PKG, ec=c, lw=3, zorder=4))
        ax.add_patch(P.Circle((x, cy), 0.45, color="#2f5f9f", zorder=5))
        ax.add_patch(P.Circle((x - 0.15, cy + 0.15), 0.12, color=WHITE, alpha=.8, zorder=6))
    else:
        ax.add_patch(P.Polygon([(x + 0.15, cy + 0.9), (x - 0.5, cy - 0.05), (x - 0.02, cy - 0.05), (x - 0.2, cy - 0.9),
                                (x + 0.5, cy + 0.12), (x + 0.02, cy + 0.12)], color=c, zorder=4))
    ax.text(x, y - 0.75, t, ha="center", fontsize=20, color=c, weight="bold")
    ax.text(x, y - 1.25, sub, ha="center", fontsize=16, color=MUTED)
    anchor(f"k{k}", ax, x, y)


for k in range(4):
    tile(ax, k)
    (save if k == 3 else save_step)(fig, OUT + f"day10_kinds_{k}.png")
