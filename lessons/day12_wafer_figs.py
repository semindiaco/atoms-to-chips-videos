"""Diagrams for Day 12: What is a wafer? (From Sand to Wafer, Ep 1). Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"
SILVER = "#9fb3c8"
SILVER2 = "#c9d6e3"
DOUGH = "#e8c07a"
COPPER = "#e0915a"
BASE = "#3a4a66"


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


def die_grid(ax, cx, cy, r, s, col=CYAN, edge=None, gap=0.06, alpha=0.85, z=3):
    """Square dies of side s on a grid centred on the disc (cx, cy, r). Partial edge dies in `edge` colour if given."""
    full, part = [], []
    n = int(np.ceil(r / s)) + 1
    for i in range(-n, n):
        for j in range(-n, n):
            x, y = cx - s / 2 + i * s, cy - s / 2 + j * s
            cs = [((x + a - cx) ** 2 + (y + b - cy) ** 2) for a in (0, s) for b in (0, s)]
            inside = sum(c <= (r * 0.96) ** 2 for c in cs)
            if inside == 4:
                full.append((x, y))
            elif inside > 0:
                part.append((x, y))
    for x, y in full:
        ax.add_patch(P.Rectangle((x + gap / 2, y + gap / 2), s - gap, s - gap, color=col, alpha=alpha, zorder=z))
    if edge:
        for x, y in part:
            ax.add_patch(P.Rectangle((x + gap / 2, y + gap / 2), s - gap, s - gap, color=edge, alpha=0.75, zorder=z))
        # mask everything outside the disc, then redraw the rim and notch
        ax.add_patch(P.Wedge((cx, cy), r + 0.7, 0, 360, width=0.7, color=BG, zorder=z + 1))
        ax.add_patch(P.Circle((cx, cy), r, fill=False, ec=SILVER2, lw=3, zorder=z + 2))
        ax.add_patch(P.Wedge((cx, cy - r), r * 0.06, 0, 180, color=BG, zorder=z + 3))
    return full, part


def disc(ax, cx, cy, r, notch=True, z=2):
    ax.add_patch(P.Circle((cx, cy), r, fc=SILVER, ec=SILVER2, lw=3, zorder=z))
    ax.add_patch(P.Circle((cx - r * 0.35, cy + r * 0.4), r * 0.35, color="white", alpha=0.06, zorder=z))
    if notch:
        ax.add_patch(P.Wedge((cx, cy - r), r * 0.06, 0, 180, color=BG, zorder=z + 5))


# ---------------------------------------------------------------- 1. Cookies from a sheet of dough
fig, ax = wide()
CX, CY, RR = 4.2, 3.2, 2.7
ax.add_patch(P.Circle((CX, CY), RR, fc=DOUGH, ec="#c99a4e", lw=4, zorder=2))
ax.text(CX, CY + RR + 0.25, "one big sheet of dough", ha="center", fontsize=20, color=AMBER, weight="bold")
anchor("dough", ax, CX, CY)
save_step(fig, OUT + "day12_cookie_0.png")

S = 0.62
full, _ = die_grid(ax, CX, CY, RR, S, col="#b5823a", gap=0.12, alpha=1)
ax.text(10.6, 5.0, "press out many\nsquare cookies at once", ha="center", fontsize=19, color=WHITE, linespacing=1.3)
anchor("grid", ax, CX + 0.9, CY + 0.9)
save_step(fig, OUT + "day12_cookie_1.png")

# lift one cookie out
x0, y0 = CX + 1 * S - S / 2, CY - S / 2  # one die right of centre
ax.add_patch(P.Rectangle((x0 + 0.06, y0 + 0.06), S - 0.12, S - 0.12, color=BG, zorder=4))
ax.add_patch(P.FancyBboxPatch((10.0, 2.35), 1.2, 1.2, boxstyle="round,pad=0.04", fc="#b5823a", ec=AMBER, lw=3, zorder=4))
arrow(ax, (x0 + S + 0.2, y0 + S / 2), (9.75, 2.95), AMBER, lw=3, rad=-0.15)
anchor("hole", ax, x0 + S / 2, y0 + S / 2); anchor("one", ax, 10.6, 2.95)
save_step(fig, OUT + "day12_cookie_2.png")

tag(ax, CX, 0.12, "dough sheet = WAFER", CYAN, fs=19)
tag(ax, 10.6, 1.75, "one cookie = one CHIP (a die)", GREEN, fs=19)
anchor("lab_w", ax, CX, 0.25); anchor("lab_c", ax, 10.6, 1.75)
save(fig, OUT + "day12_cookie_3.png")


# ---------------------------------------------------------------- 2. Jumbled crystal vs one perfect crystal (split)
fig, ax = square()
rng = np.random.default_rng(4)


def dots(ax, x0, y0, w, h, ang, col, sp=0.36, clipbox=None):
    c, s = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    cx, cy = x0 + w / 2, y0 + h / 2
    for i in range(-14, 15):
        for j in range(-14, 15):
            px, py = cx + sp * (i * c - j * s), cy + sp * (i * s + j * c)
            if clipbox(px, py):
                ax.add_patch(P.Circle((px, py), 0.1, color=col, zorder=3))


ax.text(5, 9.15, "jumbled: many small crystals", ha="center", fontsize=21, color=RED, weight="bold")
ax.add_patch(P.FancyBboxPatch((0.6, 5.1), 8.8, 3.5, boxstyle="round,pad=0.05", fc=SEAT, ec=RED, lw=2.5, zorder=1))
cuts = [0.6, 3.3, 6.2, 9.4]
angs = [0, 28, -20]
for k in range(3):
    xa, xb = cuts[k], cuts[k + 1]
    sl = 0.6 * (k - 1)
    def inside(px, py, xa=xa, xb=xb, sl=sl, k=k):
        lo = xa + (py - 6.85) * (0.35 if k > 0 else 0)
        hi = xb + (py - 6.85) * (0.35 if k < 2 else 0)
        return lo + 0.12 < px < hi - 0.12 and 5.3 < py < 8.4
    dots(ax, xa, 5.1, xb - xa, 3.5, angs[k], RED if k == 1 else "#e88d8d", clipbox=inside)
for xb in cuts[1:3]:
    ax.plot([xb - 0.35 * 1.75, xb + 0.35 * 1.75], [5.1, 8.6], color=AMBER, lw=3, ls=(0, (4, 3)), zorder=4)
ax.text(3.3 + 0.75, 4.75, "borders trip up electrons", ha="center", fontsize=16, color=AMBER)
anchor("poly", ax, 5, 6.85); anchor("bound", ax, 3.3, 6.85)
save_step(fig, OUT + "day12_crystal_0.png")

ax.text(5, 4.05, "single crystal: one perfect pattern", ha="center", fontsize=21, color=GREEN, weight="bold")
ax.add_patch(P.FancyBboxPatch((0.6, 0.3), 8.8, 3.3, boxstyle="round,pad=0.05", fc=SEAT, ec=GREEN, lw=2.5, zorder=1))
dots(ax, 0.6, 0.3, 8.8, 3.3, 0, CYAN, clipbox=lambda px, py: 0.75 < px < 9.25 and 0.45 < py < 3.45)
anchor("single", ax, 5, 1.95)
anchor("s_l", ax, 0.9, 1.95); anchor("s_m", ax, 5, 1.95); anchor("s_r", ax, 9.1, 1.95)
anchor("p_l", ax, 0.9, 6.85); anchor("p_m", ax, 3.0, 7.3); anchor("p_x", ax, 3.3, 6.4)
save_step(fig, OUT + "day12_crystal_1.png")
save(fig, OUT + "day12_crystal_2.png")


# ---------------------------------------------------------------- 3. Anatomy of a wafer (top view)
fig, ax = wide()
CX, CY, RR = 4.0, 3.3, 3.0
disc(ax, CX, CY, RR)
ax.text(10.2, 6.1, "a 300 mm silicon wafer", ha="center", fontsize=22, color=WHITE, weight="bold")
tag(ax, 10.2, 5.25, "about 30 cm across", CYAN, fs=18)
anchor("disc", ax, CX, CY); anchor("notch", ax, CX, CY - RR + 0.05)
save_step(fig, OUT + "day12_anatomy_0.png")

ax.text(CX + 1.3, CY - RR - 0.05, "notch: shows which way is up", ha="left", va="center", fontsize=15, color=AMBER, zorder=10)
save_step(fig, OUT + "day12_anatomy_1.png")

S = 0.5
full, part = die_grid(ax, CX, CY, RR, S, col=CYAN, edge=None, gap=0.07)
tag(ax, 10.2, 4.35, "each square = one die (a chip)", GREEN, fs=18)
anchor("die", ax, CX + 0.0, CY + 0.0)
save_step(fig, OUT + "day12_anatomy_2.png")

die_grid(ax, CX, CY, RR, S, col=CYAN, edge=MUTED, gap=0.07)
tag(ax, 10.2, 3.45, "edge pieces: cut off, wasted", MUTED, fs=18)
tag(ax, 10.2, 2.55, "gaps between dies: saw lanes", AMBER, fs=18)
anchor("edge", ax, CX - RR + 0.35, CY + 0.25)
anchor("lane", ax, CX + S / 2, CY + 1.0)
save(fig, OUT + "day12_anatomy_3.png")


# ---------------------------------------------------------------- 4. Mirror-flat (cross-section + scale-up)
fig, ax = wide()
ax.add_patch(P.Rectangle((1.0, 4.4), 12.0, 0.18, color=SILVER, zorder=3))
ax.text(7, 5.25, "300 mm wide", ha="center", fontsize=19, color=WHITE, weight="bold")
arrow(ax, (5.8, 5.25), (1.05, 5.25), MUTED, lw=2, ms=18); arrow(ax, (8.2, 5.25), (12.95, 5.25), MUTED, lw=2, ms=18)
ax.text(13.1, 4.0, "under 1 mm thick", ha="right", fontsize=17, color=CYAN, weight="bold")
ax.text(7, 6.15, "a wafer seen from the side", ha="center", fontsize=21, color=MUTED)
anchor("side", ax, 7, 4.5); anchor("thin", ax, 12.3, 4.5)
save_step(fig, OUT + "day12_flat_0.png")

# zoom bubble on the surface
ax.add_patch(P.Circle((3.0, 4.58), 0.22, fill=False, ec=AMBER, lw=2.5, zorder=5))
ax.plot([3.0, 3.6], [4.36, 3.35], color=AMBER, lw=2); ax.plot([3.0, 6.1], [4.36, 3.35], color=AMBER, lw=1.2, alpha=0)
ax.add_patch(P.FancyBboxPatch((1.2, 0.5), 5.6, 2.8, boxstyle="round,pad=0.05", fc=SEAT, ec=AMBER, lw=2.5, zorder=4))
xs = np.linspace(1.5, 6.5, 300)
ys = 1.6 + 0.07 * np.sin(xs * 9) + 0.04 * np.sin(xs * 23 + 1)
ax.fill_between(xs, 0.8, ys, color=SILVER, zorder=5)
ax.text(4.0, 2.75, "zoom into the surface", ha="center", fontsize=17, color=AMBER, weight="bold")
ax.text(4.0, 2.2, "bumps less than 1 nanometre high", ha="center", fontsize=15, color=WHITE)
anchor("bumps", ax, 4.0, 1.7); anchor("spot", ax, 3.0, 4.55)
save_step(fig, OUT + "day12_flat_1.png")

# scale-up analogy
ax.add_patch(P.FancyBboxPatch((7.4, 0.5), 5.6, 2.8, boxstyle="round,pad=0.05", fc=SEAT, ec=GREEN, lw=2.5, zorder=4))
ax.text(10.2, 2.75, "blow it up to a city", ha="center", fontsize=17, color=GREEN, weight="bold")
ax.text(10.2, 1.85, "wafer = 30 km wide", ha="center", fontsize=17, color=WHITE, zorder=6)
ax.text(10.2, 1.15, "bumps: about a hair wide", ha="center", fontsize=17, color=WHITE, zorder=6)
anchor("city", ax, 10.2, 1.6)
save(fig, OUT + "day12_flat_2.png")


# ---------------------------------------------------------------- 5. The journey: sand to chips
fig, ax = wide()
XS = [1.25, 3.55, 5.85, 8.15, 10.45, 12.75]
Y = 3.4
names = ["sand", "pure silicon", "crystal ingot", "thin slices", "polished wafer", "chips"]
eps = ["", "Ep 2", "Ep 3", "Ep 4", "Ep 4", ""]
cols = [AMBER, SILVER, CYAN, CYAN, SILVER2, GREEN]


def icon(k):
    x = XS[k]
    if k == 0:
        r = np.random.default_rng(1)
        for _ in range(70):
            u, v = r.uniform(-0.8, 0.8), r.uniform(0, 1)
            if v < 0.9 - abs(u) * 0.9:
                ax.add_patch(P.Circle((x + u, Y - 0.6 + v), 0.06, color=DOUGH, zorder=3))
    elif k == 1:
        for (u, v, s) in [(-0.4, -0.3, 0.45), (0.25, -0.35, 0.5), (-0.05, 0.25, 0.42)]:
            ax.add_patch(P.RegularPolygon((x + u, Y + v), 6, radius=s, color=SILVER, ec=SILVER2, lw=2, zorder=3))
    elif k == 2:
        ax.add_patch(P.Rectangle((x - 0.45, Y - 0.9), 0.9, 1.6, color=SILVER, zorder=3))
        ax.add_patch(P.Ellipse((x, Y + 0.7), 0.9, 0.28, color=SILVER2, zorder=4))
        ax.add_patch(P.Ellipse((x, Y - 0.9), 0.9, 0.28, color=SILVER, zorder=3))
        ax.add_patch(P.Polygon([(x - 0.45, Y - 0.9), (x, Y - 1.35), (x + 0.45, Y - 0.9)], color=SILVER, zorder=3))
    elif k == 3:
        for i in range(4):
            ax.add_patch(P.Ellipse((x - 0.45 + i * 0.3, Y - 0.1 + i * 0.12), 0.35, 1.3, color=SILVER, ec=BG, lw=2, zorder=3 + i))
    elif k == 4:
        ax.add_patch(P.Circle((x, Y), 0.85, fc=SILVER2, ec="white", lw=2, zorder=3))
        ax.add_patch(P.Circle((x - 0.3, Y + 0.3), 0.25, color="white", alpha=0.35, zorder=4))
    elif k == 5:
        ax.add_patch(P.Circle((x, Y), 0.85, fc=SILVER, ec=SILVER2, lw=2, zorder=3))
        die_grid(ax, x, Y, 0.85, 0.2, col=GREEN, gap=0.04, z=4)
    ax.text(x, Y - 1.7, names[k], ha="center", fontsize=17, color=cols[k], weight="bold")
    if eps[k]:
        ax.text(x, Y + 1.35, eps[k], ha="center", fontsize=14, color=MUTED)
    anchor(f"j{k}", ax, x, Y)
    if k > 0:
        arrow(ax, (XS[k - 1] + 0.95, Y), (x - 0.95, Y), MUTED, lw=2.5, ms=20)


ax.text(7, 6.0, "From sand to wafer: this playlist", ha="center", fontsize=23, weight="bold")
for k in range(2): icon(k)
save_step(fig, OUT + "day12_journey_0.png")
for k in range(2, 4): icon(k)
save_step(fig, OUT + "day12_journey_1.png")
for k in range(4, 6): icon(k)
save(fig, OUT + "day12_journey_2.png")


# ---------------------------------------------------------------- 6. The wafer is the foundation (cross-section, not to scale)
fig, ax = wide()
ax.add_patch(P.Rectangle((1.5, 0.5), 8.5, 2.6, color=BASE, zorder=2))
ax.text(5.75, 1.8, "the wafer: thick, strong base", ha="center", fontsize=20, color=WHITE, weight="bold", zorder=3)
ax.text(10.4, 1.8, "almost all of\nthe thickness", ha="left", va="center", fontsize=16, color=MUTED, linespacing=1.3)
ax.text(7, 6.15, "a chip, cut open (not to scale)", ha="center", fontsize=21, color=MUTED)
anchor("base", ax, 5.75, 1.8)
save_step(fig, OUT + "day12_build_0.png")

ax.add_patch(P.Rectangle((1.5, 3.1), 8.5, 0.35, color="#56688a", zorder=2))
for i in range(7):
    x = 2.1 + i * 1.15
    ax.add_patch(P.Rectangle((x, 3.1), 0.25, 0.35, color=GREEN, zorder=3))
    ax.add_patch(P.Rectangle((x + 0.55, 3.1), 0.25, 0.35, color=GREEN, zorder=3))
    ax.add_patch(P.Rectangle((x + 0.2, 3.45), 0.65, 0.3, color=AMBER, zorder=3))
ax.text(10.4, 3.4, "transistors: built into\nthe very top skin", ha="left", va="center", fontsize=16, color=GREEN, weight="bold", linespacing=1.3)
anchor("skin", ax, 4.4, 3.4)
save_step(fig, OUT + "day12_build_1.png")

for lvl in range(4):
    y = 3.95 + lvl * 0.5
    ax.add_patch(P.Rectangle((1.5, y - 0.12), 8.5, 0.5, color="#16233a", zorder=1))
    for i in range(5 - (lvl // 2)):
        x = 1.8 + i * (8.0 / (5 - (lvl // 2))) + lvl * 0.2
        ax.add_patch(P.Rectangle((x, y), 1.0 + lvl * 0.25, 0.22, color=COPPER, zorder=3))
        ax.add_patch(P.Rectangle((x + 0.3, y - 0.12), 0.12, 0.14, color=COPPER, zorder=3))
ax.text(10.4, 4.7, "copper wiring\nlayers on top", ha="left", va="center", fontsize=16, color=COPPER, weight="bold", linespacing=1.3)
anchor("wires", ax, 5.75, 4.7)
anchor("up0", ax, 4.0, 2.2); anchor("up1", ax, 4.0, 3.4); anchor("up2", ax, 4.3, 4.4); anchor("up3", ax, 4.6, 5.4)
save(fig, OUT + "day12_build_2.png")


# ---------------------------------------------------------------- 7. How many chips fit on one wafer?
fig, ax = wide()
RR = 1.95
CXS = [2.4, 7.0, 11.6]
specs = [(4.5 / 150 * RR, "tiny sensor chips", "about 3,000", AMBER),
         (10 / 150 * RR, "phone chips", "about 600", CYAN),
         (28 / 150 * RR, "giant AI chips", "about 60", VIOLET)]
ax.text(7, 6.3, "Same 300 mm wafer, different chip sizes", ha="center", fontsize=22, weight="bold")
for k, (s, name, cnt, col) in enumerate(specs):
    cx = CXS[k]; cy = 3.15
    disc(ax, cx, cy, RR)
    nd = len(die_grid(ax, cx, cy, RR, s, col=col, gap=max(0.012, s * 0.1), alpha=0.95, z=4)[0])
    print(name, nd)
    ax.text(cx, cy - RR - 0.45, name, ha="center", fontsize=18, color=col, weight="bold")
    tag(ax, cx, cy + RR + 0.42, cnt, col, fs=17)
    anchor(f"w{k}", ax, cx, cy)
    if k < 2:
        save_step(fig, OUT + f"day12_count_{k}.png")
save(fig, OUT + "day12_count_2.png")


# ---------------------------------------------------------------- 8. A fab: wafers in, chips out (split)
fig, ax = square()
# factory
ax.add_patch(P.Rectangle((2.6, 3.0), 4.8, 3.0, fc=SEAT, ec=MUTED, lw=3, zorder=2))
ax.add_patch(P.Polygon([(2.6, 6.0), (3.8, 6.9), (3.8, 6.0), (5.0, 6.9), (5.0, 6.0), (6.2, 6.9), (6.2, 6.0), (7.4, 6.9), (7.4, 6.0)],
                       fc=SEAT, ec=MUTED, lw=3, zorder=2))
ax.text(5.0, 4.5, "FAB", ha="center", va="center", fontsize=40, color=WHITE, weight="bold", zorder=3)
ax.text(5.0, 7.9, "a chip factory", ha="center", fontsize=21, color=MUTED)
anchor("fab", ax, 5.0, 4.5)
save_step(fig, OUT + "day12_fab_0.png")

for i in range(3):
    ax.add_patch(P.Circle((0.9, 3.6 + i * 0.9), 0.35, fc=SILVER2, ec="white", lw=1.5, zorder=3))
arrow(ax, (1.45, 4.5), (2.5, 4.5), SILVER2, lw=3)
ax.text(0.9, 2.55, "blank\nwafers in", ha="center", va="center", fontsize=16, color=SILVER2, weight="bold", linespacing=1.2)
anchor("in", ax, 0.9, 4.5)
save_step(fig, OUT + "day12_fab_1.png")

for i in range(3):
    ax.add_patch(P.Circle((9.1, 3.6 + i * 0.9), 0.35, fc=SILVER, ec=SILVER2, lw=1.5, zorder=3))
    die_grid(ax, 9.1, 3.6 + i * 0.9, 0.35, 0.12, col=GREEN, gap=0.025, z=4)
arrow(ax, (7.5, 4.5), (8.55, 4.5), GREEN, lw=3)
ax.text(9.1, 2.55, "patterned\nwafers out", ha="center", va="center", fontsize=16, color=GREEN, weight="bold", linespacing=1.2)
tag(ax, 5.0, 1.2, "Dholera plan: up to 50,000 wafers a month", AMBER, fs=17)
anchor("out", ax, 9.1, 4.5); anchor("plan", ax, 5.0, 1.2)
save(fig, OUT + "day12_fab_2.png")
print("figs ok")
