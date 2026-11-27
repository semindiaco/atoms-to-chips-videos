"""Diagrams for Day 15: Slicing, lapping and polishing wafers (From Sand to Wafer, Ep 4).
Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"
SILVER = "#9fb3c8"
SILVER2 = "#c9d6e3"
STEEL = "#3a4a66"
DUST = "#c98a5a"
WATER = "#2a6f9e"
rng = np.random.default_rng(15)


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
    return ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=col, weight="bold", zorder=z,
                   bbox=dict(fc=BG, ec=col, boxstyle="round,pad=0.4", lw=2), linespacing=1.15)


def arrow(ax, a, b, col=WHITE, lw=3, rad=0.0, z=6, ms=26):
    ax.annotate("", xy=b, xytext=a, zorder=z,
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, mutation_scale=ms, connectionstyle=f"arc3,rad={rad}"))


def rough(x0, x1, y, amp, n=80, seed=0):
    r = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, n)
    ys = y + amp * (r.uniform(-1, 1, n) * 0.7 + 0.3 * np.sin(xs * 5))
    return xs, ys


# ---------------------------------------------------------------- 1. The journey: log to mirror
fig, ax = wide()
steps = [("1", "slice", CYAN), ("2", "round\nthe edge", CYAN), ("3", "lap", AMBER),
         ("4", "etch", AMBER), ("5", "polish", GREEN), ("6", "clean\n& check", GREEN)]
xs = [1.25 + i * 2.3 for i in range(6)]
groups = [(0, 2), (2, 4), (4, 6)]


def box(i):
    n, t, c = steps[i]; x = xs[i]
    ax.add_patch(P.FancyBboxPatch((x - 0.95, 2.6), 1.9, 1.9, boxstyle="round,pad=0.06", fc=SEAT, ec=c, lw=3, zorder=3))
    ax.add_patch(P.Circle((x, 4.5), 0.32, fc=c, ec="none", zorder=4))
    ax.text(x, 4.5, n, ha="center", va="center", fontsize=18, color=BG, weight="bold", zorder=5)
    ax.text(x, 3.45, t, ha="center", va="center", fontsize=20, color=WHITE, weight="bold", zorder=5, linespacing=1.1)
    if i > 0:
        arrow(ax, (xs[i - 1] + 1.0, 3.5), (x - 1.0, 3.5), MUTED, lw=2.5, ms=20)
    anchor(f"s{i+1}", ax, x, 3.5)


ax.text(7.0, 6.05, "from crystal log to mirror-smooth wafer", ha="center", fontsize=22, color=WHITE, weight="bold")
for i in range(2): box(i)
ax.text(2.4, 1.7, "cut and shape", ha="center", fontsize=17, color=CYAN)
save_step(fig, OUT + "day15_journey_0.png")
for i in range(2, 4): box(i)
ax.text(7.0, 1.7, "flatten and heal", ha="center", fontsize=17, color=AMBER)
save_step(fig, OUT + "day15_journey_1.png")
for i in range(4, 6): box(i)
ax.text(11.6, 1.7, "shine and inspect", ha="center", fontsize=17, color=GREEN)
save_step(fig, OUT + "day15_journey_2.png")
# rough slice -> mirror wafer under the row
xr, yr = rough(1.0, 4.0, 0.75, 0.12, seed=1)
ax.fill_between(xr, 0.35, yr, color=SILVER, alpha=0.8, zorder=3)
ax.text(2.5, 0.05, "rough slice", ha="center", fontsize=15, color=MUTED)
ax.add_patch(P.Rectangle((10.0, 0.4), 3.0, 0.32, fc=SILVER2, ec=WHITE, lw=1.5, zorder=3))
ax.text(11.5, 0.05, "mirror wafer", ha="center", fontsize=15, color=WHITE)
arrow(ax, (4.4, 0.6), (9.7, 0.6), WHITE, lw=2.5, ms=22)
anchor("rough", ax, 2.5, 0.6); anchor("mirror", ax, 11.5, 0.6)
save(fig, OUT + "day15_journey_3.png")


# ---------------------------------------------------------------- 2. Multi-wire saw (top view)
fig, ax = wide()
RL, RR = 2.2, 11.8
for x in (RL, RR):
    ax.add_patch(P.FancyBboxPatch((x - 0.45, 0.6), 0.9, 4.9, boxstyle="round,pad=0.05", fc=STEEL, ec=SILVER2, lw=2.5, zorder=2))
wy = np.linspace(0.85, 5.25, 22)
for y in wy:
    ax.plot([RL, RR], [y, y], color=SILVER2, lw=1.4, zorder=3)
ax.text(RL, 6.05, "roller", ha="center", fontsize=18, color=SILVER2, weight="bold")
ax.text(RR, 6.05, "roller", ha="center", fontsize=18, color=SILVER2, weight="bold")
ax.text(7.0, 6.05, "one long wire, wound round and round", ha="center", fontsize=19, color=WHITE, weight="bold")
anchor("rollerL", ax, RL, 3.05); anchor("web", ax, 7.0, 3.05)
anchor("w_l", ax, RL + 0.5, wy[11]); anchor("w_r", ax, RR - 0.5, wy[11])
save_step(fig, OUT + "day15_saw_0.png")

# ingot block pressed into the web
ax.add_patch(P.FancyBboxPatch((6.0, 0.45), 2.0, 5.2, boxstyle="round,pad=0.04", fc=SILVER, ec=WHITE, lw=2, alpha=0.55, zorder=4))
for k in range(60):
    ax.add_patch(P.Circle((rng.uniform(5.3, 8.7), rng.uniform(0.7, 5.4)), 0.045, color=DUST, zorder=5))
tag(ax, 4.15, 0.25, "grit in a liquid: slurry", DUST, fs=15)
tag(ax, 9.85, 4.6, "ingot pressed\ninto the wires", WHITE, fs=15)
anchor("ingot", ax, 7.0, 3.05); anchor("slurry", ax, 5.6, 1.4)
save_step(fig, OUT + "day15_saw_1.png")

# result: hundreds of slices
for y in wy:
    ax.plot([6.0, 8.0], [y, y], color=BG, lw=3.5, zorder=6)
tag(ax, 9.85, 1.6, "hundreds of\nwafers in one cut", GREEN, fs=15)
anchor("result", ax, 7.0, 3.05)
save_step(fig, OUT + "day15_saw_2.png")
tag(ax, 4.15, 4.6, "like an egg slicer", AMBER, fs=16)
anchor("egg", ax, 4.15, 4.6)
save(fig, OUT + "day15_saw_3.png")


# ---------------------------------------------------------------- 3. Kerf loss (split, square)
fig, ax = square()
ax.text(5.0, 9.0, "side view of the cut ingot", ha="center", fontsize=22, color=WHITE, weight="bold")
x = 0.8
for i in range(9):
    ax.add_patch(P.Rectangle((x, 4.2), 0.62, 3.8, fc=SILVER, ec=WHITE, lw=1.2, zorder=3))
    x += 0.62
    if i < 8:
        ax.add_patch(P.Rectangle((x, 4.2), 0.25, 3.8, fc="#3a2410", ec="none", zorder=2))
        for k in range(5):
            ax.add_patch(P.Circle((x + rng.uniform(0.04, 0.21), rng.uniform(4.3, 7.9)), 0.04, color=DUST, zorder=3))
        x += 0.25
ax.text(1.11, 3.6, "wafer", ha="center", fontsize=18, color=SILVER2, weight="bold")
arrow(ax, (1.11, 3.8), (1.11, 4.15), SILVER2, lw=2, ms=16)
ax.text(5.5, 3.6, "gap = sawdust", ha="center", fontsize=18, color=DUST, weight="bold")
arrow(ax, (5.0, 3.85), (4.67, 4.15), DUST, lw=2, ms=16)
anchor("slices", ax, 4.6, 6.1); anchor("gap", ax, 4.67, 6.1)
save_step(fig, OUT + "day15_kerf_0.png")

# share bar
ax.add_patch(P.Rectangle((0.8, 1.1), 6.0, 1.0, fc=SILVER, ec=WHITE, lw=1.5, zorder=3))
ax.add_patch(P.Rectangle((6.8, 1.1), 2.4, 1.0, fc=DUST, ec=WHITE, lw=1.5, zorder=3))
ax.text(3.8, 1.6, "becomes wafers", ha="center", va="center", fontsize=18, color=BG, weight="bold", zorder=4)
ax.text(8.0, 1.6, "lost", ha="center", va="center", fontsize=18, color=BG, weight="bold", zorder=4)
ax.text(5.0, 0.45, "a quarter or more never becomes a wafer", ha="center", fontsize=16, color=MUTED)
anchor("lost", ax, 8.0, 1.6); anchor("bar", ax, 5.0, 1.6)
save(fig, OUT + "day15_kerf_1.png")


# ---------------------------------------------------------------- 4. Rounding the edge (cross-section)
fig, ax = wide()
ax.text(7.0, 6.05, "the wafer's edge, seen from the side (hugely enlarged)", ha="center", fontsize=19, color=WHITE, weight="bold")
ax.add_patch(P.Rectangle((0.5, 2.4), 5.0, 1.6, fc=SILVER, ec=WHITE, lw=2, zorder=3))
# chip at the sharp corner
ax.add_patch(P.Polygon([(5.5, 4.0), (5.05, 4.0), (5.5, 3.55)], closed=True, fc=BG, ec=RED, lw=2.5, zorder=4))
ax.plot([5.2, 4.75, 4.95], [3.8, 3.35, 3.05], color=RED, lw=2, zorder=4)
t_sharp = tag(ax, 3.0, 1.2, "sharp corner: chips and cracks", RED, fs=16)
anchor("sharp", ax, 5.3, 3.8)
save_step(fig, OUT + "day15_edge_0.png")

# grinding wheel with a shaped groove
gx, gy = 9.0, 3.2
ax.add_patch(P.Circle((gx, gy), 1.9, fc=STEEL, ec=SILVER2, lw=3, zorder=3))
ax.add_patch(P.Ellipse((gx - 1.9, gy), 0.9, 1.7, fc=BG, ec=AMBER, lw=3, zorder=4))
arrow(ax, (gx + 0.9, gy + 1.5), (gx + 1.5, gy + 0.8), AMBER, lw=3, rad=-0.3)
ax.text(gx + 0.4, gy - 2.45, "shaped grinding wheel", ha="center", fontsize=17, color=AMBER, weight="bold")
anchor("wheel", ax, gx, gy); anchor("groove", ax, gx - 1.9, gy)
save_step(fig, OUT + "day15_edge_1.png")

# after: rounded nose (redraw left half)
ax.add_patch(P.Rectangle((0.3, 0.6), 6.0, 4.7, fc=BG, ec="none", zorder=5))
ax.add_patch(P.Rectangle((0.5, 2.4), 4.4, 1.6, fc=SILVER, ec="none", zorder=6))
ax.add_patch(P.Ellipse((4.9, 3.2), 1.3, 1.6, fc=SILVER, ec="none", zorder=6))
ax.plot([0.5, 4.9], [4.0, 4.0], color=WHITE, lw=2, zorder=7); ax.plot([0.5, 4.9], [2.4, 2.4], color=WHITE, lw=2, zorder=7)
th = np.linspace(-np.pi / 2, np.pi / 2, 60)
ax.plot(4.9 + 0.65 * np.cos(th), 3.2 + 0.8 * np.sin(th), color=WHITE, lw=2, zorder=7)
t_sharp.set_visible(False)
tag(ax, 3.0, 1.2, "rounded edge: strong and smooth", GREEN, fs=16)
tag(ax, 3.0, 5.0, "like smoothing a glass table's edge", AMBER, fs=15)
anchor("round", ax, 5.0, 3.2)
save(fig, OUT + "day15_edge_2.png")


# ---------------------------------------------------------------- 5. Lapping (side view)
fig, ax = wide()
PX0, PX1 = 0.8, 8.6
ax.add_patch(P.Rectangle((PX0, 0.9), PX1 - PX0, 0.8, fc=STEEL, ec=SILVER2, lw=2.5, zorder=3))
ax.text((PX0 + PX1) / 2, 1.3, "bottom plate", ha="center", va="center", fontsize=17, color=WHITE, weight="bold", zorder=4)
for x in (1.6, 3.8, 6.0):
    ax.add_patch(P.Rectangle((x, 1.75), 1.6, 0.42, fc=SILVER, ec=WHITE, lw=1.5, zorder=4))
t_w = ax.text(4.7, 2.75, "wafers", ha="center", fontsize=17, color=SILVER2, weight="bold")
arrow(ax, (1.3, 0.55), (3.3, 0.55), MUTED, lw=2, rad=0.15, ms=18)
anchor("wafers", ax, 4.6, 1.96); anchor("bottom", ax, 4.7, 1.3)
save_step(fig, OUT + "day15_lap_0.png")

ax.add_patch(P.Rectangle((PX0, 2.25), PX1 - PX0, 0.8, fc=STEEL, ec=SILVER2, lw=2.5, zorder=3))
ax.text((PX0 + PX1) / 2, 2.65, "top plate", ha="center", va="center", fontsize=17, color=WHITE, weight="bold", zorder=4)
t_w.set_visible(False)
for k in range(70):
    ax.add_patch(P.Circle((rng.uniform(1.0, 8.4), rng.choice([1.72, 2.2])), 0.035, color=DUST, zorder=5))
arrow(ax, (4.7, 4.1), (4.7, 3.15), WHITE, lw=3)
ax.text(4.7, 4.35, "pressed together, both plates turn", ha="center", fontsize=17, color=WHITE)
tag(ax, 4.7, 5.6, "gritty slurry grinds both faces", DUST, fs=16)
anchor("sandwich", ax, 4.7, 2.0); anchor("press", ax, 4.7, 3.6)
anchor("in", ax, 1.2, 1.96); anchor("out", ax, 8.2, 1.96)
save_step(fig, OUT + "day15_lap_1.png")

# zoom panel: before vs after
ax.add_patch(P.FancyBboxPatch((9.2, 0.6), 4.5, 5.2, boxstyle="round,pad=0.05", fc=SEAT, ec=AMBER, lw=2.5, zorder=2))
xr, yr = rough(9.5, 13.4, 4.4, 0.28, seed=3)
ax.fill_between(xr, 3.7, yr, color=SILVER, zorder=3)
ax.text(11.45, 5.3, "before: saw marks", ha="center", fontsize=16, color=MUTED, zorder=4)
xr, yr = rough(9.5, 13.4, 1.95, 0.04, seed=4)
ax.fill_between(xr, 1.3, yr, color=SILVER2, zorder=3)
ax.text(11.45, 2.55, "after: flat and even", ha="center", fontsize=16, color=GREEN, weight="bold", zorder=4)
ax.text(11.45, 0.85, "both faces parallel", ha="center", fontsize=15, color=WHITE, zorder=4)
anchor("before", ax, 11.45, 4.4); anchor("after", ax, 11.45, 1.9)
save(fig, OUT + "day15_lap_2.png")


# ---------------------------------------------------------------- 6. Etching away the damage
fig, ax = wide()
ax.text(7.0, 6.05, "a slice of wafer, seen from the side (enlarged)", ha="center", fontsize=19, color=WHITE, weight="bold")
X0, X1 = 2.0, 12.0
ax.add_patch(P.Rectangle((X0, 2.3), X1 - X0, 1.8, fc=SILVER, ec="none", zorder=3))
# damaged skin top and bottom
dmg = [ax.add_patch(P.Rectangle((X0, 3.75), X1 - X0, 0.35, fc="#7f8da0", ec="none", zorder=4)),
       ax.add_patch(P.Rectangle((X0, 2.3), X1 - X0, 0.35, fc="#7f8da0", ec="none", zorder=4))]
for x in np.linspace(2.4, 11.6, 16):
    dmg += ax.plot([x, x + rng.uniform(-0.15, 0.15)], [4.1, 3.75 + rng.uniform(-0.05, 0.05)], color=RED, lw=1.6, zorder=5)
    dmg += ax.plot([x + 0.25, x + 0.25 + rng.uniform(-0.15, 0.15)], [2.3, 2.65], color=RED, lw=1.6, zorder=5)
body = ax.patches[-3]
t_dmg = tag(ax, 7.0, 4.95, "damaged skin: tiny hidden cracks", RED, fs=16)
anchor("damage", ax, 7.0, 3.93); anchor("bulk", ax, 7.0, 3.2)
save_step(fig, OUT + "day15_etch_0.png")

# bath
ax.add_patch(P.FancyBboxPatch((1.2, 1.1), 11.6, 4.0, boxstyle="round,pad=0.05", fc=WATER, ec=CYAN, lw=2.5, alpha=0.35, zorder=2))
for k in range(30):
    ax.add_patch(P.Circle((rng.uniform(1.5, 12.5), rng.uniform(1.3, 4.9)), rng.uniform(0.05, 0.11), fc="none", ec=CYAN, lw=1.2, zorder=6))
tag(ax, 7.0, 0.55, "a chemical bath eats away the damaged skin", CYAN, fs=16)
anchor("bath", ax, 2.0, 4.6); anchor("bath2", ax, 7.0, 4.5)
save_step(fig, OUT + "day15_etch_1.png")

# after: clean, slightly thinner
for a in dmg: a.set_visible(False)
body.set_visible(False)
ax.add_patch(P.Rectangle((X0, 2.65), X1 - X0, 1.1, fc=SILVER, ec=WHITE, lw=2, zorder=8))
t_dmg.set_visible(False)
tag(ax, 7.0, 4.95, "healthy crystal, no cracks", GREEN, fs=16)
tag(ax, 11.2, 1.75, "like peeling a\nbruised apple", AMBER, fs=15)
anchor("clean", ax, 7.0, 3.2); anchor("apple", ax, 11.2, 1.75)
save(fig, OUT + "day15_etch_2.png")


# ---------------------------------------------------------------- 7. Polishing (CMP)
fig, ax = wide()
PCX, PCY = 5.6, 2.2
ax.add_patch(P.Ellipse((PCX, PCY - 0.35), 9.4, 2.6, fc=STEEL, ec=SILVER2, lw=2, zorder=2))
ax.add_patch(P.Ellipse((PCX, PCY), 9.4, 2.6, fc="#24324a", ec=SILVER2, lw=2.5, zorder=3))
arrow(ax, (PCX - 3.2, PCY - 1.6), (PCX + 0.5, PCY - 1.85), MUTED, lw=2.5, rad=0.15, ms=20)
ax.text(PCX, PCY - 0.15, "soft pad on a spinning table", ha="center", fontsize=17, color=WHITE, weight="bold", zorder=4)
anchor("pad", ax, PCX, PCY - 0.1)
save_step(fig, OUT + "day15_polish_0.png")

HX = PCX + 1.8
ax.add_patch(P.Rectangle((HX - 0.18, 4.4), 0.36, 1.8, fc=SILVER, ec="none", zorder=5))
ax.add_patch(P.Ellipse((HX, 4.2), 2.4, 0.7, fc=SILVER2, ec=WHITE, lw=2, zorder=6))
ax.add_patch(P.Rectangle((HX - 1.2, 3.55), 2.4, 0.65, fc=SILVER2, ec="none", zorder=6))
ax.add_patch(P.Ellipse((HX, 3.55), 2.4, 0.7, fc=CYAN, ec=WHITE, lw=2, zorder=6))
arrow(ax, (HX - 0.7, 5.5), (HX - 0.7, 4.6), WHITE, lw=3)
ax.text(HX - 0.9, 5.75, "pressed down gently", ha="right", fontsize=16, color=WHITE)
ax.text(HX - 2.6, 3.95, "wafer, face down", ha="center", fontsize=16, color=CYAN, weight="bold")
anchor("head", ax, HX, 3.9)
save_step(fig, OUT + "day15_polish_1.png")

NX = PCX - 2.6
ax.plot([NX - 1.8, NX, NX], [5.9, 5.9, 4.4], color=SILVER2, lw=5, zorder=5, solid_capstyle="round")
for y in (4.0, 3.5, 3.0):
    ax.add_patch(P.Circle((NX, y), 0.1, fc=WHITE, ec="none", alpha=0.9, zorder=6))
ax.add_patch(P.Ellipse((NX + 0.3, 2.55), 1.2, 0.3, fc=WHITE, alpha=0.55, zorder=4))
ax.text(NX - 1.2, 6.25, "slurry", ha="center", fontsize=17, color=WHITE, weight="bold")
anchor("nozzle", ax, NX, 4.6); anchor("drop", ax, NX + 0.3, 2.55); anchor("under", ax, HX, 3.2)
save_step(fig, OUT + "day15_polish_2.png")

ax.add_patch(P.FancyBboxPatch((10.25, 0.4), 3.5, 5.6, boxstyle="round,pad=0.05", fc=SEAT, ec=GREEN, lw=2.5, zorder=7))
xr, yr = rough(10.5, 13.5, 4.35, 0.09, seed=6)
ax.fill_between(xr, 3.75, yr, color=SILVER, zorder=8)
ax.text(12.0, 5.25, "before", ha="center", fontsize=16, color=MUTED, zorder=8)
ax.add_patch(P.Rectangle((10.5, 1.2), 3.0, 0.75, fc=SILVER2, ec=WHITE, lw=1.5, zorder=8))
ax.text(12.0, 2.45, "after: a mirror", ha="center", fontsize=16, color=GREEN, weight="bold", zorder=8)
ax.text(12.0, 0.75, "bumps ~ one atom", ha="center", fontsize=15, color=WHITE, zorder=8)
anchor("before", ax, 12.0, 4.3); anchor("mirror", ax, 12.0, 1.6)
save(fig, OUT + "day15_polish_3.png")


# ---------------------------------------------------------------- 8. Clean, check, ship
fig, ax = wide()
for i, (lab, col) in enumerate((("chemical\nbath", CYAN), ("pure water\nrinse", WATER), ("dry", SILVER2))):
    x = 1.0 + i * 1.6
    ax.add_patch(P.Rectangle((x, 1.4), 1.3, 2.0, fc=col, ec=WHITE, lw=2, alpha=0.45, zorder=2))
    ax.add_patch(P.Rectangle((x + 0.6, 1.8), 0.08, 2.1, fc=SILVER, ec="none", zorder=3))
    ax.text(x + 0.65, 0.75, lab, ha="center", va="center", fontsize=14, color=WHITE, linespacing=1.05)
ax.text(3.05, 5.3, "1. clean", ha="center", fontsize=21, color=CYAN, weight="bold")
anchor("clean", ax, 3.05, 2.6); anchor("t1", ax, 1.65, 2.4); anchor("t3", ax, 4.45, 2.4)
save_step(fig, OUT + "day15_ship_0.png")

ax.add_patch(P.Ellipse((7.6, 1.9), 2.8, 0.9, fc=SILVER2, ec=WHITE, lw=2, zorder=3))
ax.plot([7.0, 7.6], [4.3, 1.95], color=RED, lw=3, zorder=4)
ax.add_patch(P.Rectangle((6.6, 4.3), 0.8, 0.5, fc=STEEL, ec=SILVER2, lw=2, zorder=4))
ax.add_patch(P.Circle((7.6, 1.95), 0.09, fc=RED, zorder=5))
ax.text(7.6, 5.3, "2. check", ha="center", fontsize=21, color=RED, weight="bold")
ax.text(7.6, 0.75, "lasers hunt for specks", ha="center", fontsize=14, color=WHITE)
anchor("laser", ax, 7.6, 2.2)
save_step(fig, OUT + "day15_ship_1.png")

ax.add_patch(P.FancyBboxPatch((10.6, 1.3), 2.6, 2.9, boxstyle="round,pad=0.08", fc=SEAT, ec=GREEN, lw=3, zorder=3))
for k in range(9):
    ax.plot([10.9, 12.9], [1.6 + k * 0.3, 1.6 + k * 0.3], color=SILVER2, lw=3, zorder=4)
ax.text(11.9, 5.3, "3. ship", ha="center", fontsize=21, color=GREEN, weight="bold")
ax.text(11.9, 0.75, "sealed box to the chip fab", ha="center", fontsize=14, color=WHITE)
anchor("box", ax, 11.9, 2.75)
arrow(ax, (5.0, 2.4), (6.0, 2.2), MUTED, lw=2.5, ms=20); arrow(ax, (9.2, 2.2), (10.4, 2.6), MUTED, lw=2.5, ms=20)
save(fig, OUT + "day15_ship_2.png")
print("figs ok")
