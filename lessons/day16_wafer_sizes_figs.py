"""Diagrams for Day 16: Wafer sizes, why 300 mm matters (From Sand to Wafer, Ep 5).
Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"
SILVER = "#9fb3c8"
SILVER2 = "#c9d6e3"
STEEL = "#3a4a66"


def wide(w=14, h=6.6):
    fig = plt.figure(figsize=(w, h), dpi=100)
    ax = fig.add_axes([0.02, 0.03, 0.96, 0.94]); ax.set_axis_off()
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.set_aspect("equal")
    return fig, ax


def square(w=10, h=9.6):
    fig = plt.figure(figsize=(w, h), dpi=100)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96]); ax.set_axis_off()
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.set_aspect("equal")
    return fig, ax


def tag(ax, x, y, text, col=GREEN, fs=18, z=9):
    return ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=col, weight="bold", zorder=z,
                   bbox=dict(fc=BG, ec=col, boxstyle="round,pad=0.4", lw=2), linespacing=1.15)


def arrow(ax, a, b, col=WHITE, lw=3, rad=0.0, z=6, ms=26, style="-|>"):
    ax.annotate("", xy=b, xytext=a, zorder=z,
                arrowprops=dict(arrowstyle=style, color=col, lw=lw, mutation_scale=ms, connectionstyle=f"arc3,rad={rad}"))


def disc(ax, x, y, r, fc=SILVER, ec=WHITE, lw=2, z=3, notch=True):
    ax.add_patch(P.Circle((x, y), r, fc=fc, ec=ec, lw=lw, zorder=z))
    if notch:
        ax.add_patch(P.Circle((x, y - r), max(0.04, r * 0.035), fc=BG, ec="none", zorder=z + 0.5))


def dies(ax, cx, cy, R, s, excl=0.0, z=4):
    """Draw a die grid on a wafer of radius R; whole dies cyan, cut-off edge dies red.
    Returns (whole, partial)."""
    Rin = R - excl
    best = None
    for ox in np.linspace(0, s, 9):
        for oy in np.linspace(0, s, 9):
            w, p = [], []
            for x in np.arange(-R - s + ox, R, s):
                for y in np.arange(-R - s + oy, R, s):
                    c = [(x, y), (x + s, y), (x, y + s), (x + s, y + s)]
                    ins = sum(a * a + b * b < Rin * Rin for a, b in c)
                    if ins == 4: w.append((x, y))
                    elif ins > 0: p.append((x, y))
            if best is None or len(w) > len(best[0]): best = (w, p)
    w, p = best
    g = s * 0.07
    for x, y in w:
        ax.add_patch(P.Rectangle((cx + x + g, cy + y + g), s - 2 * g, s - 2 * g, fc=CYAN, ec="none", alpha=0.85, zorder=z))
    clip = P.Circle((cx, cy), R, transform=ax.transData)
    for x, y in p:
        r = P.Rectangle((cx + x + g, cy + y + g), s - 2 * g, s - 2 * g, fc=RED, ec="none", alpha=0.8, zorder=z)
        ax.add_patch(r); r.set_clip_path(clip)
    return len(w), len(p)


# ---------------------------------------------------------------- 1. History: wafers keep growing (true scale)
fig, ax = wide()
sizes = [(25, "1960s", "1 inch"), (50, "1960s", "2 inch"), (100, "1970s", "100 mm"),
         (150, "1980s", "150 mm"), (200, "1990s", "200 mm"), (300, "2000s", "300 mm")]
k = 0.0135  # units per mm
x = 0.45; cy = 3.25
pos = []
for d, _, _ in sizes:
    r = d * k / 2
    pos.append((x + r, r)); x += 2 * r + 0.42
ax.text(7.0, 6.15, "wafer sizes over the years (drawn to scale)", ha="center", fontsize=21, color=WHITE, weight="bold")


def hist(i, col):
    d, dec, name = sizes[i]; xc, r = pos[i]
    disc(ax, xc, cy, r, fc=SILVER if i < 5 else SILVER2, ec=col, lw=2.5)
    ax.text(xc, cy - r - 0.45, name, ha="center", fontsize=17, color=col, weight="bold")
    ax.text(xc, cy - r - 0.95, dec, ha="center", fontsize=15, color=MUTED)
    anchor(f"h{i}", ax, xc, cy)


hist(0, CYAN); hist(1, CYAN)
anchor("coin", ax, pos[0][0], cy)
save_step(fig, OUT + "day16_history_0.png")
hist(2, CYAN); hist(3, AMBER)
save_step(fig, OUT + "day16_history_1.png")
hist(4, AMBER)
save_step(fig, OUT + "day16_history_2.png")
hist(5, GREEN)
tag(ax, pos[5][0], cy + pos[5][1] + 0.35, "dinner plate", GREEN, fs=15)
save(fig, OUT + "day16_history_3.png")


# ---------------------------------------------------------------- 2. Area: 1.5x wider -> 2.25x area
fig, ax = wide()
ax.text(7.0, 6.15, "a little wider means a lot more room", ha="center", fontsize=21, color=WHITE, weight="bold")
cA, cB = (2.4, 3.0), (6.4, 3.0)
rA, rB = 1.4, 2.1
disc(ax, *cA, rA)
arrow(ax, (cA[0] - rA, cA[1]), (cA[0] + rA, cA[1]), BG, lw=2.5, ms=18, style="<|-|>", z=7)
ax.text(cA[0], cA[1] + 0.35, "20 cm", ha="center", fontsize=18, color=BG, weight="bold", zorder=8)
ax.text(cA[0], 0.75, "200 mm", ha="center", fontsize=18, color=SILVER2, weight="bold")
anchor("small", ax, *cA)
save_step(fig, OUT + "day16_area_0.png")
disc(ax, *cB, rB, fc=SILVER2)
arrow(ax, (cB[0] - rB, cB[1]), (cB[0] + rB, cB[1]), BG, lw=2.5, ms=18, style="<|-|>", z=7)
ax.text(cB[0], cB[1] + 0.35, "30 cm", ha="center", fontsize=18, color=BG, weight="bold", zorder=8)
ax.text(cB[0], 0.45, "300 mm: 1.5 times wider", ha="center", fontsize=18, color=WHITE, weight="bold")
anchor("big", ax, *cB)
save_step(fig, OUT + "day16_area_1.png")
# square tiles: 2x2 vs 3x3
s = 0.55
for i in range(2):
    for j in range(2):
        ax.add_patch(P.Rectangle((9.3 + i * s, 3.6 + j * s), s * 0.92, s * 0.92, fc=AMBER, ec="none", zorder=4))
for i in range(3):
    for j in range(3):
        ax.add_patch(P.Rectangle((11.3 + i * s, 3.35 + j * s), s * 0.92, s * 0.92, fc=GREEN, ec="none", zorder=4))
ax.text(9.85, 3.15, "2 wide\n4 tiles", ha="center", va="top", fontsize=16, color=AMBER, weight="bold")
ax.text(12.1, 3.15, "3 wide\n9 tiles", ha="center", va="top", fontsize=16, color=GREEN, weight="bold")
anchor("tiles", ax, 11.2, 4.1)
save_step(fig, OUT + "day16_area_2.png")
tag(ax, 11.2, 0.75, "1.5x wider = 2.25x the area", WHITE, fs=17)
anchor("rule", ax, 11.2, 0.75)
save(fig, OUT + "day16_area_3.png")


# ---------------------------------------------------------------- 3. Edge loss (split, square), big 20 mm chips
fig, ax = square()
ax.text(5.0, 9.1, "big chips, same size on both", ha="center", fontsize=22, color=WHITE, weight="bold")
u = 0.0175  # units per mm
RA, RB = 100 * u, 150 * u
cA, cB = (2.0, 6.0), (6.75, 4.3)
disc(ax, *cA, RA, fc=STEEL, ec=SILVER2)
wA, pA = dies(ax, *cA, RA, 20 * u, excl=3 * u)
ax.text(cA[0], cA[1] + RA + 0.35, "200 mm", ha="center", fontsize=18, color=SILVER2, weight="bold")
anchor("edgeA", ax, cA[0] - RA * 0.78, cA[1] - RA * 0.55); anchor("waferA", ax, *cA)
save_step(fig, OUT + "day16_edge_0.png")
disc(ax, *cB, RB, fc=STEEL, ec=SILVER2)
wB, pB = dies(ax, *cB, RB, 20 * u, excl=3 * u)
ax.text(cB[0], cB[1] + RB + 0.3, "300 mm", ha="center", fontsize=18, color=SILVER2, weight="bold")
anchor("waferB", ax, *cB)
save_step(fig, OUT + "day16_edge_1.png")
ax.text(2.0, 3.3, f"{wA} whole\n{pA} cut off", ha="center", va="center", fontsize=18, color=WHITE, weight="bold", linespacing=1.3)
ax.text(6.75, 1.1, f"{wB} whole   {pB} cut off", ha="center", va="center", fontsize=18, color=WHITE, weight="bold")
anchor("countA", ax, 2.0, 3.3); anchor("countB", ax, 6.75, 1.1)
save(fig, OUT + "day16_edge_2.png")
print("edge dies", wA, pA, wB, pB)


# ---------------------------------------------------------------- 4. Cost per chip
fig, ax = wide()
ax.text(7.0, 6.15, "a machine treats the whole wafer in one go", ha="center", fontsize=21, color=WHITE, weight="bold")
ax.add_patch(P.FancyBboxPatch((4.6, 2.1), 4.8, 2.7, boxstyle="round,pad=0.08", fc=SEAT, ec=CYAN, lw=3, zorder=3))
ax.text(7.0, 4.2, "one process step", ha="center", va="center", fontsize=20, color=WHITE, weight="bold", zorder=4)
disc(ax, 1.9, 3.45, 1.1, fc=SILVER2)
disc(ax, 12.1, 3.45, 1.1, fc=SILVER2)
ax.text(1.9, 1.85, "in", ha="center", fontsize=17, color=MUTED)
ax.text(12.1, 1.85, "out", ha="center", fontsize=17, color=MUTED)
arrow(ax, (3.1, 3.45), (4.5, 3.45), MUTED, lw=2.5, ms=20); arrow(ax, (9.5, 3.45), (10.9, 3.45), MUTED, lw=2.5, ms=20)
anchor("in", ax, 1.9, 3.45); anchor("tool", ax, 7.0, 3.45); anchor("out", ax, 12.1, 3.45)
save_step(fig, OUT + "day16_cost_0.png")
plt.close(fig)

fig, ax = wide()
ax.text(7.0, 6.15, "more chips share the cost of every step", ha="center", fontsize=21, color=WHITE, weight="bold")
# left: chips per pass bars
base = 1.0
ax.plot([0.8, 6.2], [base, base], color=MUTED, lw=2)
for x, v, col, lab in [(2.2, wA, AMBER, "200 mm"), (4.8, wB, GREEN, "300 mm")]:
    h = v / 148 * 3.8
    ax.add_patch(P.Rectangle((x - 0.6, base), 1.2, h, fc=col, ec="none", zorder=3))
    ax.text(x, base + h + 0.3, str(v), ha="center", fontsize=20, color=col, weight="bold")
    ax.text(x, base - 0.4, lab, ha="center", fontsize=16, color=WHITE)
ax.text(3.5, 0.0, "big chips per wafer", ha="center", fontsize=17, color=MUTED, weight="bold")
anchor("chips", ax, 3.5, 3.0); anchor("chips300", ax, 4.8, 3.2)
save_step(fig, OUT + "day16_cost_1.png")
ax.plot([7.8, 13.2], [base, base], color=MUTED, lw=2)
for x, v, col, lab in [(9.2, 1.0, AMBER, "200 mm"), (11.8, 0.7, GREEN, "300 mm")]:
    h = v * 3.8
    ax.add_patch(P.Rectangle((x - 0.6, base), 1.2, h, fc=col, ec="none", zorder=3))
    ax.text(x, base - 0.4, lab, ha="center", fontsize=16, color=WHITE)
ax.text(10.5, 0.0, "cost per chip (rough guide)", ha="center", fontsize=17, color=MUTED, weight="bold")
ax.text(11.8, base + 0.7 * 3.8 + 0.3, "about 30% less", ha="center", fontsize=17, color=GREEN, weight="bold")
anchor("cost", ax, 10.5, 3.0); anchor("cost300", ax, 11.8, 2.6)
save(fig, OUT + "day16_cost_2.png")


# ---------------------------------------------------------------- 5. Why bigger is harder
fig, ax = wide()
ax.text(7.0, 6.15, "bigger wafers are harder to make and move", ha="center", fontsize=21, color=WHITE, weight="bold")
# weight
disc(ax, 1.3, 3.6, 0.8); disc(ax, 3.5, 3.6, 1.2, fc=SILVER2)
ax.text(1.3, 2.35, "200 mm\nabout 53 g", ha="center", va="top", fontsize=15, color=WHITE, weight="bold", linespacing=1.2)
ax.text(3.5, 2.05, "300 mm\nabout 128 g", ha="center", va="top", fontsize=15, color=WHITE, weight="bold", linespacing=1.2)
tag(ax, 2.4, 5.3, "heavier", AMBER, fs=16)
anchor("weight", ax, 3.5, 3.6)
save_step(fig, OUT + "day16_hard_0.png")
# sag: a thin sheet held at the edges
xs = np.linspace(5.6, 9.4, 60)
ys = 4.3 - 0.75 * np.sin(np.pi * (xs - 5.6) / 3.8)
ax.plot(xs, ys, color=SILVER2, lw=6, solid_capstyle="round", zorder=4)
for xp in (5.6, 9.4):
    ax.add_patch(P.Polygon([(xp - 0.25, 3.7), (xp + 0.25, 3.7), (xp, 4.25)], fc=STEEL, ec=SILVER2, lw=1.5, zorder=3))
ax.text(7.5, 2.75, "wide and thin = it sags", ha="center", fontsize=16, color=WHITE, weight="bold")
ax.text(7.5, 2.15, "so 300 mm wafers are made\na little thicker", ha="center", va="top", fontsize=14, color=MUTED, linespacing=1.2)
anchor("sag", ax, 7.5, 3.6)
save_step(fig, OUT + "day16_hard_1.png")
# bigger crystal
ax.add_patch(P.FancyBboxPatch((10.85, 1.2), 1.0, 3.6, boxstyle="round,pad=0.05", fc=SILVER, ec=WHITE, lw=1.5, zorder=3))
ax.add_patch(P.FancyBboxPatch((12.25, 0.6), 1.5, 4.9, boxstyle="round,pad=0.05", fc=SILVER2, ec=WHITE, lw=1.5, zorder=3))
ax.text(11.35, 0.7, "200", ha="center", fontsize=14, color=MUTED, weight="bold")
ax.text(13.0, 0.1, "300", ha="center", fontsize=14, color=MUTED, weight="bold")
tag(ax, 12.3, 5.65, "huge crystal", AMBER, fs=15)
anchor("ingot", ax, 13.0, 3.0)
save_step(fig, OUT + "day16_hard_2.png")
tag(ax, 7.5, 0.6, "every machine built new", RED, fs=17)
anchor("machines", ax, 7.5, 0.6)
save(fig, OUT + "day16_hard_3.png")


# ---------------------------------------------------------------- 6. FOUPs and overhead transport
fig, ax = wide()
ax.text(7.0, 6.15, "robots carry the wafers", ha="center", fontsize=21, color=WHITE, weight="bold")
# FOUP box with 25 slots, side view
bx, by, bw, bh = 1.0, 0.9, 2.6, 3.0
ax.add_patch(P.FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.08", fc=SEAT, ec=AMBER, lw=3, zorder=3))
for i in range(25):
    y = by + 0.15 + i * (bh - 0.3) / 24
    ax.plot([bx + 0.25, bx + bw - 0.25], [y, y], color=SILVER2, lw=1.6, zorder=4)
ax.text(bx + bw / 2, by - 0.4, "sealed box: 25 wafers", ha="center", fontsize=15, color=AMBER, weight="bold")
anchor("foup", ax, bx + bw / 2, by + bh / 2)
save_step(fig, OUT + "day16_foup_0.png")
# overhead rail and vehicle
ax.plot([4.4, 13.6], [5.2, 5.2], color=SILVER2, lw=5, zorder=3)
ax.text(9.0, 5.55, "track on the ceiling", ha="center", fontsize=15, color=MUTED)
ax.add_patch(P.FancyBboxPatch((5.0, 4.45), 1.1, 0.6, boxstyle="round,pad=0.04", fc=AMBER, ec="none", zorder=5))
anchor("r0", ax, 4.6, 5.2); anchor("r1", ax, 9.0, 5.2); anchor("r2", ax, 13.4, 5.2); anchor("cart", ax, 5.55, 4.75)
save_step(fig, OUT + "day16_foup_1.png")
# tools below
for i, name in enumerate(["print", "etch", "clean"]):
    x = 6.3 + i * 2.6
    ax.add_patch(P.FancyBboxPatch((x - 0.95, 0.7), 1.9, 2.3, boxstyle="round,pad=0.06", fc=SEAT, ec=CYAN, lw=2.5, zorder=3))
    ax.text(x, 1.85, name, ha="center", va="center", fontsize=17, color=WHITE, weight="bold", zorder=4)
    arrow(ax, (x, 4.35), (x, 3.15), MUTED, lw=2, ms=18)
anchor("t0", ax, 6.3, 1.85); anchor("t1", ax, 8.9, 1.85); anchor("t2", ax, 11.5, 1.85)
anchor("drop", ax, 8.9, 3.75)
save(fig, OUT + "day16_foup_2.png")


# ---------------------------------------------------------------- 7. The 450 mm story
fig, ax = wide()
ax.text(7.0, 6.15, "the next jump: 450 mm", ha="center", fontsize=21, color=WHITE, weight="bold")
u = 0.0105
disc(ax, 2.2, 3.0, 150 * u, fc=SILVER)
disc(ax, 6.6, 3.0, 225 * u, fc=SILVER2)
ax.text(2.2, 0.85, "300 mm", ha="center", fontsize=18, color=SILVER2, weight="bold")
ax.text(6.6, 0.05, "450 mm", ha="center", fontsize=18, color=WHITE, weight="bold")
anchor("w300", ax, 2.2, 3.0); anchor("w450", ax, 6.6, 3.0)
save_step(fig, OUT + "day16_450_0.png")
tag(ax, 6.6, 3.0, "2.25x the\narea again", GREEN, fs=17)
save_step(fig, OUT + "day16_450_1.png")
tag(ax, 11.4, 4.4, "hundreds of new\nmachine designs", AMBER, fs=16)
tag(ax, 11.4, 2.5, "very few buyers", AMBER, fs=16)
anchor("cost", ax, 11.4, 3.45)
save_step(fig, OUT + "day16_450_2.png")
tag(ax, 11.4, 0.75, "put on hold\naround 2016-17", RED, fs=16)
anchor("hold", ax, 11.4, 0.75)
save(fig, OUT + "day16_450_3.png")


# ---------------------------------------------------------------- 8. India (split, square)
fig, ax = square()
ax.text(5.0, 9.05, "India's first big fab", ha="center", fontsize=22, color=WHITE, weight="bold")
# fab building
ax.add_patch(P.Rectangle((3.0, 3.2), 6.2, 3.0, fc=SEAT, ec=CYAN, lw=3, zorder=3))
ax.add_patch(P.Polygon([(3.0, 6.2), (6.1, 7.4), (9.2, 6.2)], fc=SEAT, ec=CYAN, lw=3, zorder=3))
for i in range(5):
    ax.add_patch(P.Rectangle((3.5 + i * 1.15, 4.6), 0.7, 0.7, fc=CYAN, alpha=0.5, ec="none", zorder=4))
ax.text(6.1, 3.75, "Dholera, Gujarat", ha="center", fontsize=17, color=WHITE, weight="bold", zorder=5)
anchor("fab", ax, 6.1, 4.9)
save_step(fig, OUT + "day16_india_0.png")
disc(ax, 1.3, 4.7, 0.85, fc=SILVER2)
ax.text(1.3, 3.45, "300 mm", ha="center", fontsize=16, color=SILVER2, weight="bold")
anchor("wafer", ax, 1.3, 4.7); anchor("door", ax, 3.3, 4.7)
save_step(fig, OUT + "day16_india_1.png")
tag(ax, 5.0, 1.6, "planned: up to\n50,000 wafers a month", GREEN, fs=17)
anchor("plan", ax, 5.0, 1.6)
save(fig, OUT + "day16_india_2.png")
