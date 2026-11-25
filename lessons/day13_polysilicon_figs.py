"""Diagrams for Day 13: From quartz sand to electronic-grade polysilicon (From Sand to Wafer, Ep 2).
Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"
SAND = "#e3c27f"
QUARTZ = "#dfe8f1"
SILVER = "#9fb3c8"
SILVER2 = "#c9d6e3"
STEEL = "#3a4a66"
HOT = "#ff7a2f"
rng = np.random.default_rng(13)


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


def atom(ax, x, y, r, col, txt, fs=18, z=5):
    ax.add_patch(P.Circle((x, y), r, fc=col, ec=WHITE, lw=2, zorder=z))
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, color=BG, weight="bold", zorder=z + 1)


def rock(ax, x, y, s, col=QUARTZ, z=3):
    k = rng.integers(6, 9)
    ang = np.sort(rng.uniform(0, 2 * np.pi, k))
    rad = s * rng.uniform(0.7, 1.0, k)
    pts = np.c_[x + rad * np.cos(ang), y + rad * np.sin(ang) * 0.8]
    ax.add_patch(P.Polygon(pts, closed=True, fc=col, ec="#ffffff", lw=1.5, alpha=0.95, zorder=z))


# ---------------------------------------------------------------- 1. Sand is silicon in disguise
fig, ax = wide()
# sand pile
xs = rng.uniform(0.6, 4.6, 900); hmax = 2.6 * (1 - ((xs - 2.6) / 2.1) ** 2)
ys = 0.6 + rng.uniform(0, 1, 900) * np.clip(hmax, 0, None)
cols = np.where(rng.uniform(0, 1, 900) < 0.12, "#a0784a", SAND)
ax.scatter(xs, ys, s=18, c=cols, zorder=3)
ax.plot([0.4, 4.8], [0.55, 0.55], color=MUTED, lw=2)
ax.text(2.6, 3.9, "ordinary sand", ha="center", fontsize=22, color=AMBER, weight="bold")
anchor("sand", ax, 2.6, 1.6)
save_step(fig, OUT + "day13_sand_0.png")

# magnified grain: silicon locked to oxygen
ax.add_patch(P.Circle((7.4, 3.0), 2.0, fc=SEAT, ec=AMBER, lw=3, zorder=2))
ax.plot([3.4, 5.45], [2.1, 2.55], color=AMBER, lw=2, ls=(0, (4, 3)))
ax.plot([3.4, 5.6], [2.1, 3.85], color=AMBER, lw=2, ls=(0, (4, 3)))
ax.add_patch(P.Circle((3.4, 2.1), 0.18, fc="none", ec=AMBER, lw=2, zorder=4))
for dx, dy in ((1.15, 0), (-1.15, 0), (0, 1.15), (0, -1.15)):
    ax.plot([7.4, 7.4 + dx], [3.0, 3.0 + dy], color=MUTED, lw=4, zorder=4)
    atom(ax, 7.4 + dx, 3.0 + dy, 0.36, RED, "O")
atom(ax, 7.4, 3.0, 0.5, CYAN, "Si", fs=22)
ax.text(7.4, 5.45, "inside one grain", ha="center", fontsize=19, color=WHITE)
tag(ax, 7.4, 0.45, "silicon locked to oxygen", CYAN, fs=18)
anchor("si", ax, 7.4, 3.0); anchor("o", ax, 8.55, 3.0); anchor("grain", ax, 7.4, 3.0)
save_step(fig, OUT + "day13_sand_1.png")

# best source: quartz lumps
for (x, y, s) in ((11.0, 2.0, 0.55), (12.2, 2.2, 0.7), (11.6, 3.1, 0.5), (12.9, 3.2, 0.45), (10.9, 3.0, 0.35)):
    rock(ax, x, y, s)
ax.text(11.9, 4.5, "best source:", ha="center", fontsize=19, color=WHITE)
ax.text(11.9, 4.0, "pure quartz lumps", ha="center", fontsize=21, color=GREEN, weight="bold")
anchor("quartz", ax, 11.9, 2.6)
save(fig, OUT + "day13_sand_2.png")


# ---------------------------------------------------------------- 2. The arc furnace
fig, ax = wide()
FX, FW, FB, FT = 4.6, 4.4, 0.9, 4.2   # furnace centre x, width, bottom, top
ax.add_patch(P.FancyBboxPatch((FX - FW / 2, FB), FW, FT - FB, boxstyle="round,pad=0.05", fc=STEEL, ec=SILVER2, lw=3, zorder=2))
ax.add_patch(P.Rectangle((FX - FW / 2 + 0.3, FB + 0.3), FW - 0.6, FT - FB - 0.5, fc="#1a2233", zorder=3))
for i in range(160):  # the charge: quartz + carbon
    x = rng.uniform(FX - FW / 2 + 0.45, FX + FW / 2 - 0.45); y = rng.uniform(FB + 1.2, FT - 0.4)
    ax.add_patch(P.Circle((x, y), 0.09, color=QUARTZ if i % 2 else "#4b4b4b", zorder=4))
ax.text(FX, FT + 1.55, "giant furnace", ha="center", fontsize=22, color=WHITE, weight="bold")
tag(ax, 11.1, 5.4, "quartz + carbon go in", AMBER, fs=18)
arrow(ax, (9.0, 5.4), (FX + 1.4, FT + 0.2), AMBER, rad=0.15)
anchor("furnace", ax, FX, 2.6); anchor("charge", ax, FX, 3.2); anchor("in", ax, 9.1, 5.3)
ELX = [FX - 1.2, FX, FX + 1.2]
for x in ELX:
    ax.add_patch(P.Rectangle((x - 0.22, 2.0), 0.44, FT + 1.1 - 2.0, fc="#555c66", ec=SILVER2, lw=1.5, zorder=6))
save_step(fig, OUT + "day13_furnace_0.png")

for x in ELX:  # arcs glowing at the electrode tips
    ax.add_patch(P.Circle((x, 1.75), 0.55, color=HOT, alpha=0.35, zorder=5))
    ax.add_patch(P.Circle((x, 1.75), 0.3, color="#ffd27a", alpha=0.9, zorder=5))
tag(ax, 11.1, 4.1, "electric arcs: about 2,000 °C", RED, fs=18)
anchor("arc", ax, FX, 1.75); anchor("e_top", ax, FX, FT + 1.0)
save_step(fig, OUT + "day13_furnace_1.png")

# gas out, silicon tapped out
arrow(ax, (FX + 1.7, FT + 0.3), (FX + 2.9, FT + 1.6), MUTED, rad=-0.2)
ax.text(FX + 3.1, FT + 1.85, "carbon monoxide gas", fontsize=16, color=MUTED, ha="left")
ax.add_patch(P.Rectangle((FX + FW / 2 - 0.1, FB + 0.35), 1.6, 0.22, color="#ffc56a", zorder=6))
ax.add_patch(P.Wedge((FX + FW / 2 + 2.3, FB + 0.1), 0.8, 180, 360, fc=STEEL, ec=SILVER2, lw=2, zorder=5))
ax.add_patch(P.Rectangle((FX + FW / 2 + 1.6, FB - 0.25), 1.4, 0.3, color="#ffc56a", zorder=6))
tag(ax, 11.1, 2.6, "liquid silicon, 98–99% pure", GREEN, fs=18)
anchor("gas", ax, FX + 2.7, FT + 1.4); anchor("tap", ax, FX + FW / 2 + 0.6, FB + 0.46)
anchor("ladle", ax, FX + FW / 2 + 2.3, FB - 0.2)
save(fig, OUT + "day13_furnace_2.png")


# ---------------------------------------------------------------- 3. Turning silicon into a liquid (trichlorosilane)
fig, ax = wide()
# powder
ax.add_patch(P.FancyBboxPatch((0.6, 1.6), 2.8, 2.2, boxstyle="round,pad=0.08", fc=SEAT, ec=SILVER2, lw=2.5, zorder=2))
for i in range(140):
    ax.add_patch(P.Circle((rng.uniform(0.85, 3.15), rng.uniform(1.8, 3.55)), 0.07, color=SILVER, zorder=3))
ax.text(2.0, 4.35, "crushed silicon", ha="center", fontsize=19, color=WHITE, weight="bold")
anchor("powder", ax, 2.0, 2.7)
save_step(fig, OUT + "day13_tcs_0.png")

ax.add_patch(P.FancyBboxPatch((5.2, 1.2), 3.0, 3.2, boxstyle="round,pad=0.1", fc=STEEL, ec=AMBER, lw=3, zorder=2))
ax.text(6.7, 3.3, "reactor", ha="center", fontsize=21, color=WHITE, weight="bold", zorder=4)
ax.text(6.7, 2.55, "about 300 °C", ha="center", fontsize=18, color=AMBER, zorder=4)
arrow(ax, (3.5, 2.7), (5.1, 2.7), SILVER)
ax.text(6.7, 5.75, "hydrogen chloride gas", ha="center", fontsize=18, color=VIOLET, weight="bold")
arrow(ax, (6.7, 5.45), (6.7, 4.55), VIOLET)
anchor("reactor", ax, 6.7, 2.9); anchor("hcl", ax, 6.7, 5.6); anchor("r_in", ax, 3.6, 2.7)
save_step(fig, OUT + "day13_tcs_1.png")

# output flask
arrow(ax, (8.3, 2.7), (9.7, 2.7), CYAN)
ax.add_patch(P.Circle((11.2, 2.2), 1.25, fc="none", ec=SILVER2, lw=3, zorder=3))
ax.add_patch(P.Rectangle((10.9, 3.35), 0.6, 1.1, fc=BG, ec=SILVER2, lw=3, zorder=2))
ax.add_patch(P.Wedge((11.2, 2.2), 1.18, 180, 360, fc=CYAN, alpha=0.45, zorder=2))
for (x, y) in ((10.6, 1.7), (11.5, 1.45), (11.9, 1.9)):
    ax.add_patch(P.Circle((x, y), 0.08, color=RED, zorder=4))
ax.text(11.2, 5.4, "trichlorosilane", ha="center", fontsize=21, color=CYAN, weight="bold")
ax.text(11.2, 4.85, "a clear liquid, boils at 32 °C", ha="center", fontsize=16, color=WHITE)
tag(ax, 11.2, 0.35, "impurities come along too", RED, fs=16)
anchor("tcs", ax, 11.2, 1.9); anchor("imp", ax, 11.5, 1.6); anchor("out", ax, 9.9, 2.7)
save(fig, OUT + "day13_tcs_2.png")


# ---------------------------------------------------------------- 4. Distillation
fig, ax = wide()
# boiling flask (left-bottom)
ax.add_patch(P.Circle((3.0, 1.55), 1.15, fc="none", ec=SILVER2, lw=3, zorder=3))
ax.add_patch(P.Wedge((3.0, 1.55), 1.08, 180, 360, fc=CYAN, alpha=0.4, zorder=2))
for i in range(14):
    ax.add_patch(P.Circle((rng.uniform(2.2, 3.8), rng.uniform(0.75, 1.45)), 0.08, color=[RED, AMBER, VIOLET][i % 3], zorder=4))
for x in (2.5, 3.0, 3.5):  # flame
    ax.add_patch(P.Polygon([[x - 0.18, 0.0], [x + 0.18, 0.0], [x, 0.38]], color=HOT, zorder=2))
ax.text(1.0, 2.9, "mixed liquid", ha="center", fontsize=17, color=WHITE, weight="bold")
anchor("mix", ax, 3.0, 1.2); anchor("heat", ax, 3.0, 0.2)
# column
ax.add_patch(P.Rectangle((2.7, 2.65), 0.6, 3.2, fc=SEAT, ec=SILVER2, lw=2.5, zorder=2))
for yy in np.arange(3.0, 5.7, 0.45):
    ax.plot([2.72, 3.28], [yy, yy], color=MUTED, lw=1.5, zorder=3)
ax.text(1.25, 4.4, "tall\ncolumn", ha="center", fontsize=17, color=MUTED, linespacing=1.2)
anchor("col_b", ax, 3.0, 2.9); anchor("col_m", ax, 3.0, 4.3); anchor("col_t", ax, 3.0, 5.7)
save_step(fig, OUT + "day13_still_0.png")

# condenser to clean collector
ax.plot([3.3, 7.6], [5.75, 4.4], color=SILVER2, lw=10, solid_capstyle="round", zorder=2)
ax.plot([3.3, 7.6], [5.75, 4.4], color=BG, lw=5, solid_capstyle="round", zorder=3)
ax.add_patch(P.Rectangle((7.1, 1.0), 1.1, 2.6, fc="none", ec=SILVER2, lw=3, zorder=3))
ax.add_patch(P.Rectangle((7.17, 1.05), 0.96, 1.6, fc=CYAN, alpha=0.75, zorder=2))
ax.text(7.65, 0.45, "pure liquid", ha="center", fontsize=18, color=GREEN, weight="bold")
anchor("cond", ax, 5.4, 5.1); anchor("pure", ax, 7.65, 1.9); anchor("drip", ax, 7.6, 4.2)
save_step(fig, OUT + "day13_still_1.png")

tag(ax, 11.3, 4.6, "each liquid boils at\nits own temperature", AMBER, fs=17)
tag(ax, 11.3, 2.6, "impurities left behind", RED, fs=17)
tag(ax, 11.3, 0.9, "repeat, again and again", CYAN, fs=17)
arrow(ax, (9.55, 2.4), (4.25, 1.2), RED, lw=2, rad=-0.15, ms=20)
anchor("rule", ax, 11.3, 4.6); anchor("left", ax, 3.0, 1.0); anchor("again", ax, 11.3, 0.9)
save(fig, OUT + "day13_still_2.png")


# ---------------------------------------------------------------- 5. Siemens reactor (with rock-candy analogy)
fig, ax = wide()
# rock candy analogy on the right
ax.add_patch(P.FancyBboxPatch((10.0, 0.6), 2.8, 3.6, boxstyle="round,pad=0.08", fc="#14324a", ec=SILVER2, lw=2.5, alpha=0.9, zorder=2))
ax.plot([11.4, 11.4], [4.9, 1.0], color=WHITE, lw=2, zorder=3)
ax.plot([10.6, 12.2], [4.9, 4.9], color=AMBER, lw=5, zorder=3)
for i in range(22):
    y = rng.uniform(1.1, 3.6); s = rng.uniform(0.12, 0.25)
    ax.add_patch(P.RegularPolygon((11.4 + rng.uniform(-0.25, 0.25), y), 4, radius=s, orientation=0.4, fc=QUARTZ, ec=WHITE, lw=1, alpha=0.9, zorder=4))
ax.text(11.4, 5.55, "rock candy grows", ha="center", fontsize=18, color=AMBER, weight="bold")
ax.text(11.4, 0.1, "sugar crystals on a string", ha="center", fontsize=15, color=WHITE)
anchor("candy", ax, 11.4, 2.4)
save_step(fig, OUT + "day13_siemens_0.png")

# bell jar with thin hairpin rods
JX = 4.6
ax.add_patch(P.Rectangle((JX - 3.0, 0.5), 6.0, 0.35, fc=STEEL, ec=SILVER2, lw=2, zorder=3))
ax.add_patch(P.Rectangle((JX - 2.6, 0.85), 5.2, 2.7, fc="#0f1b2c", ec="none", zorder=1))
ax.add_patch(P.Wedge((JX, 3.5), 2.6, 0, 180, fc="#0f1b2c", ec="none", zorder=1))
ax.add_patch(P.Arc((JX, 3.5), 5.2, 5.2, theta1=0, theta2=180, color=SILVER2, lw=3, zorder=2))
ax.plot([JX - 2.6, JX - 2.6], [0.85, 3.5], color=SILVER2, lw=3, zorder=2)
ax.plot([JX + 2.6, JX + 2.6], [0.85, 3.5], color=SILVER2, lw=3, zorder=2)
ax.text(JX, 6.3, "Siemens reactor", ha="center", fontsize=22, color=WHITE, weight="bold")


def hairpin(x, w, lw, col=HOT, z=4):
    ax.plot([x - 0.5, x - 0.5, x + 0.5, x + 0.5], [0.85, 4.0, 4.0, 0.85], color=col, lw=lw, solid_capstyle="butt", solid_joinstyle="round", zorder=z)


hairpin(JX - 1.1, 1, 5); hairpin(JX + 1.1, 1, 5)
tag(ax, JX, 4.7, "thin silicon rods, about 1,100 °C", HOT, fs=15)
anchor("jar", ax, JX, 2.8); anchor("rod", ax, JX - 1.6, 2.4)
save_step(fig, OUT + "day13_siemens_1.png")

# gas in, silicon sticks to the rods
arrow(ax, (JX - 4.3, 0.68), (JX - 2.9, 0.68), CYAN, lw=3)
ax.text(0.15, 1.25, "gas in", fontsize=16, color=CYAN, weight="bold")
for i in range(26):
    ax.add_patch(P.Circle((rng.uniform(JX - 2.2, JX + 2.2), rng.uniform(1.1, 3.8)), 0.05, color=CYAN, alpha=0.8, zorder=3))
arrow(ax, (JX + 2.9, 0.68), (JX + 4.4, 0.68), MUTED, lw=3)
ax.text(JX + 3.0, 1.25, "used gas out", fontsize=15, color=MUTED)
anchor("gas_in", ax, JX - 4.2, 0.68); anchor("g_mid", ax, JX - 0.6, 2.3); anchor("rod_mid", ax, JX - 1.6, 2.4)
anchor("g_out", ax, JX + 4.3, 0.68); anchor("g_mid2", ax, JX + 0.6, 1.4)
save_step(fig, OUT + "day13_siemens_2.png")

# days later: thick rods
hairpin(JX - 1.1, 1, 24, col="#aab8c8", z=5); hairpin(JX + 1.1, 1, 24, col="#aab8c8", z=5)
tag(ax, JX, 4.7, "days later: rods thicker than your arm", GREEN, fs=15, z=12)
anchor("thick", ax, JX - 1.6, 2.4)
save(fig, OUT + "day13_siemens_3.png")


# ---------------------------------------------------------------- 6. Rod -> chunks -> bag
fig, ax = wide()
ax.add_patch(P.FancyBboxPatch((0.6, 2.4), 3.6, 1.3, boxstyle="round,pad=0.05,rounding_size=0.5", fc="#aab8c8", ec=WHITE, lw=2, zorder=3))
ax.text(2.4, 4.4, "one silicon rod", ha="center", fontsize=19, color=WHITE, weight="bold")
anchor("rod", ax, 2.4, 3.05)
save_step(fig, OUT + "day13_chunks_0.png")

arrow(ax, (4.5, 3.05), (5.6, 3.05), WHITE)
for (x, y, s) in ((6.4, 2.4, 0.45), (7.3, 2.6, 0.5), (8.1, 2.3, 0.4), (6.8, 3.4, 0.42), (7.8, 3.35, 0.45), (8.7, 3.0, 0.35), (6.1, 3.2, 0.3)):
    rock(ax, x, y, s, col="#aab8c8")
ax.text(7.4, 4.4, "broken into chunks", ha="center", fontsize=19, color=WHITE, weight="bold")
tag(ax, 7.4, 1.2, "POLYSILICON", CYAN, fs=19)
anchor("chunks", ax, 7.4, 2.9)
save_step(fig, OUT + "day13_chunks_1.png")

arrow(ax, (9.2, 3.05), (10.2, 3.05), WHITE)
ax.add_patch(P.FancyBboxPatch((10.5, 1.6), 2.6, 2.9, boxstyle="round,pad=0.08,rounding_size=0.4", fc="#9fd8e6", ec=WHITE, lw=2, alpha=0.25, zorder=2))
for (x, y, s) in ((11.2, 2.3, 0.35), (12.2, 2.2, 0.35), (11.7, 3.0, 0.38), (11.1, 3.5, 0.3), (12.4, 3.3, 0.3)):
    rock(ax, x, y, s, col="#aab8c8")
ax.text(11.8, 5.0, "washed, then sealed", ha="center", fontsize=17, color=WHITE, weight="bold")
ax.text(11.8, 0.95, "in ultra-clean bags", ha="center", fontsize=17, color=GREEN)
anchor("bag", ax, 11.8, 3.0)
save(fig, OUT + "day13_chunks_2.png")


# ---------------------------------------------------------------- 7. How pure? (split, square)
fig, ax = square()
ax.text(5, 9.1, "metal grade", ha="center", fontsize=23, color=AMBER, weight="bold")
for i in range(20):
    for j in range(5):
        bad = (i, j) == (13, 2)
        ax.add_patch(P.Circle((1.2 + i * 0.4, 5.3 + j * 0.62), 0.14, color=RED if bad else SILVER, zorder=3))
ax.text(5, 4.35, "about 1 atom in 100 is wrong", ha="center", fontsize=18, color=WHITE)
anchor("grid", ax, 5, 6.55); anchor("bad", ax, 1.2 + 13 * 0.4, 5.3 + 2 * 0.62)
save_step(fig, OUT + "day13_pure_0.png")

ax.add_patch(P.FancyBboxPatch((0.6, 0.4), 8.8, 3.1, boxstyle="round,pad=0.05", fc=SEAT, ec=GREEN, lw=2.5, zorder=1))
ax.text(5, 2.75, "chip grade", ha="center", fontsize=23, color=GREEN, weight="bold")
ax.text(5, 1.75, "about 1 in 100,000,000,000", ha="center", fontsize=22, color=CYAN, weight="bold")
ax.text(5, 0.95, "a hundred billion", ha="center", fontsize=17, color=WHITE)
anchor("chip", ax, 5, 1.8)
save(fig, OUT + "day13_pure_1.png")


# ---------------------------------------------------------------- 8. Where it goes (split, square)
fig, ax = square()
ax.add_patch(P.Wedge((5, 5.4), 3.2, 99, 441, fc=AMBER, ec=BG, lw=3, zorder=2))   # solar: big slice
ax.add_patch(P.Wedge((5.12, 5.6), 3.2, 81, 99, fc=CYAN, ec=BG, lw=3, zorder=2))     # chips: small slice
ax.text(5, 4.6, "solar\npanels", ha="center", fontsize=24, color=BG, weight="bold", linespacing=1.1, zorder=4)
ax.text(5.3, 9.15, "chips: a small slice", ha="center", fontsize=19, color=CYAN, weight="bold")
anchor("solar", ax, 5, 4.6); anchor("chips", ax, 5.25, 7.7)
save_step(fig, OUT + "day13_use_0.png")

tag(ax, 5, 1.35, "solar grade: mostly made in China", AMBER, fs=17)
anchor("china", ax, 5, 1.35)
save_step(fig, OUT + "day13_use_1.png")

tag(ax, 5, 0.35, "India: first plants still being planned", GREEN, fs=17)
anchor("india", ax, 5, 0.35)
save(fig, OUT + "day13_use_2.png")
print("figs ok")
