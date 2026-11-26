"""Diagrams for Day 14: Growing a single crystal, the Czochralski process (From Sand to Wafer, Ep 3).
Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"
SILVER = "#9fb3c8"
SILVER2 = "#c9d6e3"
STEEL = "#3a4a66"
HOT = "#ff7a2f"
MELT = "#ffb347"
QUARTZ = "#dfe8f1"
INGOT = "#aab8c8"
rng = np.random.default_rng(14)


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


def grain(ax, cx, cy, R, ang, col):
    """A small crystal grain: a polygon filled with a regular dot pattern at angle ang."""
    k = 6
    a0 = rng.uniform(0, 1)
    th = np.linspace(0, 2 * np.pi, k, endpoint=False) + a0
    rad = R * rng.uniform(0.85, 1.05, k)
    pts = np.c_[cx + rad * np.cos(th), cy + rad * np.sin(th)]
    poly = P.Polygon(pts, closed=True, fc=SEAT, ec=AMBER, lw=2.5, zorder=2)
    ax.add_patch(poly)
    c, s = np.cos(ang), np.sin(ang)
    for i in np.arange(-3, 4):
        for j in np.arange(-3, 4):
            x, y = 0.32 * i, 0.32 * j
            px, py = cx + c * x - s * y, cy + s * x + c * y
            if poly.get_path().contains_point((px, py), radius=-0.08):
                ax.add_patch(P.Circle((px, py), 0.08, color=col, zorder=3))


# ---------------------------------------------------------------- 1. Many crystals vs one crystal
fig, ax = wide()
centres = [(1.6, 4.2), (3.1, 4.6), (2.3, 3.0), (3.9, 3.2), (1.3, 1.8), (2.9, 1.6), (4.3, 1.9)]
for (x, y) in centres:
    grain(ax, x, y, 0.85, rng.uniform(0, np.pi / 2), SILVER)
ax.text(2.8, 6.0, "polysilicon", ha="center", fontsize=23, color=AMBER, weight="bold")
ax.text(2.8, 0.35, "many small crystals, every which way", ha="center", fontsize=16, color=WHITE)
anchor("poly", ax, 2.8, 3.2); anchor("boundary", ax, 2.7, 3.8)
save_step(fig, OUT + "day14_order_0.png")

ax.add_patch(P.FancyBboxPatch((8.4, 1.0), 4.6, 4.4, boxstyle="round,pad=0.05", fc=SEAT, ec=CYAN, lw=3, zorder=2))
for i in range(13):
    for j in range(12):
        ax.add_patch(P.Circle((8.75 + i * 0.33, 1.3 + j * 0.34), 0.08, color=CYAN, zorder=3))
ax.text(10.7, 6.0, "single crystal", ha="center", fontsize=23, color=CYAN, weight="bold")
ax.text(10.7, 0.35, "one pattern, every atom in line", ha="center", fontsize=16, color=WHITE)
arrow(ax, (5.4, 3.2), (8.1, 3.2), WHITE)
ax.text(6.75, 3.65, "melt and regrow", ha="center", fontsize=16, color=MUTED)
anchor("single", ax, 10.7, 3.2)
save_step(fig, OUT + "day14_order_1.png")

tag(ax, 6.85, 1.9, "a crowd\nvs\na marching\nband", GREEN, fs=16)
anchor("band", ax, 6.85, 1.9)
save(fig, OUT + "day14_order_2.png")


# ---------------------------------------------------------------- 2. The seed: new atoms copy its pattern
fig, ax = wide()
SX0, SY0, D = 4.2, 4.0, 0.42
# the seed crystal (top block)
ax.add_patch(P.Rectangle((SX0 - 0.3, SY0 - 0.3), 13 * D + 0.18, 4 * D + 0.25, fc=SEAT, ec=CYAN, lw=3, zorder=2))
for i in range(13):
    for j in range(4):
        ax.add_patch(P.Circle((SX0 + i * D, SY0 + j * D), 0.11, color=CYAN, zorder=3))
ax.text(1.9, 4.6, "seed\ncrystal", ha="center", fontsize=21, color=CYAN, weight="bold", linespacing=1.1)
anchor("seed", ax, SX0 + 6 * D, SY0 + 1.5 * D)
# the melt (bottom)
ax.add_patch(P.Rectangle((SX0 - 0.6, 0.3), 13 * D + 0.8, 2.3, fc="#3a2410", ec=MELT, lw=3, zorder=1))
for k in range(70):
    ax.add_patch(P.Circle((rng.uniform(SX0 - 0.4, SX0 + 12.6 * D), rng.uniform(0.5, 2.4)), 0.1, color=MELT, alpha=0.85, zorder=2))
ax.text(1.9, 1.45, "liquid\nsilicon", ha="center", fontsize=21, color=MELT, weight="bold", linespacing=1.1)
anchor("melt", ax, SX0 + 6 * D, 1.4)
save_step(fig, OUT + "day14_seed_0.png")

# new rows joining underneath, in the same pattern
for j, a in ((1, 0.95), (2, 0.7)):
    for i in range(13):
        ax.add_patch(P.Circle((SX0 + i * D, SY0 - j * D), 0.11, color=GREEN, alpha=a, zorder=3))
for i in (2, 5, 9, 11):
    arrow(ax, (SX0 + i * D + 0.25, 2.2), (SX0 + i * D, SY0 - 2 * D - 0.18), GREEN, lw=2, ms=16)
ax.text(11.6, 3.55, "new atoms join", ha="center", fontsize=19, color=GREEN, weight="bold")
ax.text(11.6, 3.0, "in the same pattern", ha="center", fontsize=17, color=WHITE)
anchor("join", ax, SX0 + 6 * D, SY0 - 1.5 * D); anchor("from", ax, SX0 + 6 * D, 2.0)
save_step(fig, OUT + "day14_seed_1.png")

tag(ax, 11.6, 1.4, "like tiles following\nthe first row", AMBER, fs=17)
anchor("tiles", ax, 11.6, 1.4)
save(fig, OUT + "day14_seed_2.png")


# ---------------------------------------------------------------- 3. The Czochralski puller
fig, ax = wide()
CX = 5.0
# chamber
ax.add_patch(P.FancyBboxPatch((CX - 3.0, 0.3), 6.0, 4.1, boxstyle="round,pad=0.05", fc="#0f1b2c", ec=SILVER2, lw=3, zorder=1))
ax.add_patch(P.Rectangle((CX - 0.7, 4.4), 1.4, 1.9, fc="#0f1b2c", ec=SILVER2, lw=3, zorder=1))
# heaters
for x in (CX - 2.55, CX + 2.25):
    ax.add_patch(P.Rectangle((x, 0.8), 0.3, 2.3, fc=HOT, ec="none", alpha=0.9, zorder=3))
# graphite holder + quartz crucible
ax.add_patch(P.Wedge((CX, 2.3), 1.95, 180, 360, fc="#3d3d44", ec=SILVER, lw=2, zorder=3))
ax.add_patch(P.Wedge((CX, 2.3), 1.7, 180, 360, fc=QUARTZ, ec="none", zorder=4))
ax.add_patch(P.Wedge((CX, 2.3), 1.55, 180, 360, fc="#0f1b2c", ec="none", zorder=4))
ax.text(10.3, 5.6, "inside the puller", ha="center", fontsize=22, color=WHITE, weight="bold")
tag(ax, 10.3, 3.3, "quartz crucible (a bowl)", QUARTZ, fs=16)
tag(ax, 10.3, 2.1, "heaters", HOT, fs=16)
arrow(ax, (8.55, 3.2), (CX + 1.5, 1.6), QUARTZ, lw=2, rad=-0.1, ms=18)
arrow(ax, (9.35, 1.95), (CX + 2.6, 1.6), HOT, lw=2, ms=18)
anchor("chamber", ax, CX, 2.4); anchor("crucible", ax, CX, 1.1); anchor("heater", ax, CX + 2.4, 1.9)
save_step(fig, OUT + "day14_puller_0.png")

# melt
ax.add_patch(P.Wedge((CX, 2.0), 1.5, 180, 360, fc=MELT, ec="none", alpha=0.95, zorder=5))
ax.add_patch(P.Wedge((CX, 2.0), 1.5, 180, 360, fc="none", ec="#ffe2a8", lw=2, zorder=5))
tag(ax, 10.3, 0.9, "melt: about 1,400 °C", MELT, fs=16)
anchor("melt", ax, CX, 1.25)
save_step(fig, OUT + "day14_puller_1.png")

# seed on a cable
ax.plot([CX, CX], [6.3, 2.5], color=SILVER2, lw=2, zorder=6)
ax.add_patch(P.Rectangle((CX - 0.12, 2.0), 0.24, 0.55, fc=CYAN, ec=WHITE, lw=1.5, zorder=7))
tag(ax, 10.3, 4.45, "seed on a pulling cable", CYAN, fs=16)
anchor("seed", ax, CX, 2.3); anchor("top", ax, CX, 6.1)
save_step(fig, OUT + "day14_puller_2.png")

# ingot growing, argon flowing, rotation
ax.add_patch(P.Rectangle((CX - 0.12, 3.95), 0.24, 0.5, fc=CYAN, ec=WHITE, lw=1.5, zorder=7))
ax.add_patch(P.Polygon([[CX - 0.05, 3.95], [CX + 0.05, 3.95], [CX + 0.05, 3.7], [CX + 0.95, 3.1], [CX + 0.95, 2.05],
                        [CX - 0.95, 2.05], [CX - 0.95, 3.1], [CX - 0.05, 3.7]], closed=True, fc=INGOT, ec=WHITE, lw=2, zorder=7))
arrow(ax, (CX - 0.55, 4.7), (CX + 0.55, 4.7), GREEN, lw=2.5, rad=0.35, ms=18)
arrow(ax, (CX + 1.2, 0.55), (CX - 1.2, 0.55), VIOLET, lw=2.5, rad=0.25, ms=18)
ax.text(CX - 1.95, 5.75, "argon gas", fontsize=16, color=VIOLET, ha="center", weight="bold")
arrow(ax, (CX - 1.25, 5.75), (CX - 0.75, 5.4), VIOLET, lw=2, ms=16)
anchor("ingot", ax, CX, 2.8); anchor("ar_in", ax, CX - 0.3, 5.9); anchor("ar_mid", ax, CX - 1.3, 2.6)
anchor("ar_out", ax, CX - 2.7, 0.6); anchor("spin", ax, CX, 4.75)
anchor("sp1", ax, CX - 0.5, 4.75); anchor("sp2", ax, CX + 0.5, 4.75)
save(fig, OUT + "day14_puller_3.png")


# ---------------------------------------------------------------- 4. Growth stages: dip, neck, shoulder, body, tail
fig, ax = wide()
XS = [1.4, 4.2, 7.0, 9.9, 12.6]
BASE = 1.0  # melt line


def meltline(x):
    ax.add_patch(P.Rectangle((x - 1.1, 0.3), 2.2, BASE - 0.3, fc=MELT, ec="none", alpha=0.85, zorder=2))


def seed(x, y):
    ax.plot([x, x], [6.3, y + 0.5], color=SILVER2, lw=2, zorder=3)
    ax.add_patch(P.Rectangle((x - 0.12, y), 0.24, 0.5, fc=CYAN, ec=WHITE, lw=1.5, zorder=4))


def label(x, n, t, col=WHITE):
    ax.text(x, 0.0 + 0.02, f"{n}. {t}", ha="center", va="bottom", fontsize=17, color=col, weight="bold", zorder=6)


meltline(XS[0]); seed(XS[0], BASE - 0.05)
label(XS[0], 1, "dip", CYAN)
anchor("dip", ax, XS[0], BASE + 0.2)
save_step(fig, OUT + "day14_stages_0.png")

meltline(XS[1]); seed(XS[1], 3.6)
ax.add_patch(P.Rectangle((XS[1] - 0.045, BASE), 0.09, 3.6 - BASE, fc=INGOT, ec=WHITE, lw=1, zorder=4))
label(XS[1], 2, "neck", GREEN)
anchor("neck", ax, XS[1], 2.3)
save_step(fig, OUT + "day14_stages_1.png")

# shoulder
meltline(XS[2]); seed(XS[2], 4.6)
ax.add_patch(P.Rectangle((XS[2] - 0.045, 2.6), 0.09, 2.0, fc=INGOT, ec=WHITE, lw=1, zorder=4))
ax.add_patch(P.Polygon([[XS[2] - 0.05, 2.6], [XS[2] + 0.05, 2.6], [XS[2] + 0.85, BASE], [XS[2] - 0.85, BASE]], closed=True, fc=INGOT, ec=WHITE, lw=1.5, zorder=4))
label(XS[2], 3, "shoulder", AMBER)
anchor("shoulder", ax, XS[2], 1.8)
# body
meltline(XS[3]); seed(XS[3], 5.6)
ax.add_patch(P.Rectangle((XS[3] - 0.045, 4.8), 0.09, 0.8, fc=INGOT, ec=WHITE, lw=1, zorder=4))
ax.add_patch(P.Polygon([[XS[3] - 0.05, 4.8], [XS[3] + 0.05, 4.8], [XS[3] + 0.85, 4.0], [XS[3] + 0.85, BASE],
                        [XS[3] - 0.85, BASE], [XS[3] - 0.85, 4.0]], closed=True, fc=INGOT, ec=WHITE, lw=1.5, zorder=4))
label(XS[3], 4, "body", CYAN)
anchor("body", ax, XS[3], 2.6)
save_step(fig, OUT + "day14_stages_2.png")

# tail: lifted clear of the melt
meltline(XS[4]); seed(XS[4], 5.9)
ax.add_patch(P.Rectangle((XS[4] - 0.045, 5.3), 0.09, 0.6, fc=INGOT, ec=WHITE, lw=1, zorder=4))
ax.add_patch(P.Polygon([[XS[4] - 0.05, 5.3], [XS[4] + 0.05, 5.3], [XS[4] + 0.85, 4.6], [XS[4] + 0.85, 2.5],
                        [XS[4] + 0.05, 1.5], [XS[4] - 0.05, 1.5], [XS[4] - 0.85, 2.5], [XS[4] - 0.85, 4.6]], closed=True, fc=INGOT, ec=WHITE, lw=1.5, zorder=4))
label(XS[4], 5, "tail", VIOLET)
anchor("tail", ax, XS[4], 1.9); anchor("done", ax, XS[4], 3.5)
save(fig, OUT + "day14_stages_3.png")


# ---------------------------------------------------------------- 5. Pull speed sets the width (split, square)
fig, ax = square()


def mini(x, w, col, ttl, sub):
    ax.add_patch(P.Rectangle((x - 1.5, 1.2), 3.0, 0.9, fc=MELT, ec="none", alpha=0.85, zorder=2))
    ax.add_patch(P.Rectangle((x - w / 2, 2.1), w, 4.6, fc=INGOT, ec=WHITE, lw=2, zorder=3))
    ax.add_patch(P.Ellipse((x, 2.1), w + 0.35, 0.35, fc="none", ec="#fff3c4", lw=4, zorder=4))
    ax.plot([x, x], [6.7, 8.2], color=SILVER2, lw=2)
    ax.text(x, 9.0, ttl, ha="center", fontsize=23, color=col, weight="bold")
    ax.text(x, 0.55, sub, ha="center", fontsize=18, color=WHITE)


mini(2.6, 2.4, GREEN, "slow pull", "thicker crystal")
arrow(ax, (4.3, 7.0), (4.3, 8.1), GREEN, lw=3, ms=20)
anchor("slow", ax, 2.6, 4.3); anchor("ring", ax, 2.6, 2.1)
save_step(fig, OUT + "day14_speed_0.png")

mini(7.4, 1.1, AMBER, "fast pull", "thinner crystal")
arrow(ax, (8.4, 6.4), (8.4, 8.4), AMBER, lw=3, ms=20)
arrow(ax, (8.75, 6.4), (8.75, 8.4), AMBER, lw=3, ms=20)
anchor("fast", ax, 7.4, 4.3)
save(fig, OUT + "day14_speed_1.png")


# ---------------------------------------------------------------- 6. Stirring, dopant and oxygen
fig, ax = wide()
CX = 5.0
ax.add_patch(P.Wedge((CX, 3.6), 3.0, 180, 360, fc=QUARTZ, ec="none", zorder=2))
ax.add_patch(P.Wedge((CX, 3.6), 2.8, 180, 360, fc=MELT, ec="none", alpha=0.9, zorder=3))
ax.add_patch(P.Rectangle((CX - 0.9, 3.6), 1.8, 2.7, fc=INGOT, ec=WHITE, lw=2, zorder=5))
arrow(ax, (CX - 0.8, 6.1), (CX + 0.8, 6.1), GREEN, lw=3, rad=0.35, ms=20)
arrow(ax, (CX + 2.0, 0.45), (CX - 2.0, 0.45), VIOLET, lw=3, rad=0.25, ms=20)
ax.text(CX + 1.5, 6.15, "crystal spins", fontsize=16, color=GREEN, weight="bold")
ax.text(CX + 2.3, 0.15, "bowl spins the other way", fontsize=16, color=VIOLET, weight="bold")
# convection loops in the melt
for sgn in (-1, 1):
    arrow(ax, (CX + sgn * 2.3, 2.0), (CX + sgn * 1.2, 3.25), "#7a3c00", lw=2.5, rad=sgn * -0.4, ms=18, z=4)
    arrow(ax, (CX + sgn * 1.1, 2.6), (CX + sgn * 1.9, 1.1), "#7a3c00", lw=2.5, rad=sgn * -0.4, ms=18, z=4)
anchor("crystal", ax, CX, 5.0); anchor("bowl", ax, CX, 0.9)
anchor("m1", ax, CX - 2.3, 2.0); anchor("m2", ax, CX - 1.3, 3.2); anchor("m3", ax, CX - 1.1, 2.4); anchor("m4", ax, CX - 1.9, 1.2)
tag(ax, 11.0, 5.4, "stirred like soup", GREEN, fs=17)
anchor("stir", ax, CX - 1.6, 2.3)
save_step(fig, OUT + "day14_stir_0.png")

# a pinch of dopant
for (x, y) in ((CX + 1.6, 3.0), (CX + 2.0, 2.2), (CX + 0.8, 1.6), (CX - 1.5, 2.6), (CX - 0.6, 1.4), (CX + 1.2, 2.5)):
    ax.add_patch(P.Circle((x, y), 0.12, color=RED, ec=WHITE, lw=1, zorder=6))
tag(ax, 11.0, 3.9, "a pinch of boron\nor phosphorus", RED, fs=17)
anchor("dopant", ax, CX + 1.5, 2.6); anchor("dop_in", ax, CX + 2.4, 5.0)
save_step(fig, OUT + "day14_stir_1.png")

# oxygen from the crucible wall, argon sweeping it away
for (x, y) in ((CX - 2.55, 2.4), (CX - 2.2, 1.6), (CX + 2.5, 2.6), (CX + 2.1, 1.5), (CX, 0.95)):
    ax.add_patch(P.Circle((x, y), 0.1, color=CYAN, ec=WHITE, lw=1, zorder=6))
tag(ax, 11.0, 2.3, "oxygen from the\nquartz bowl", CYAN, fs=17)
tag(ax, 11.0, 0.8, "argon carries gas away", VIOLET, fs=17)
anchor("oxy", ax, CX - 2.4, 2.1); anchor("ar_a", ax, CX - 0.7, 6.4); anchor("ar_b", ax, CX - 1.6, 3.9)
anchor("ar_c", ax, CX - 3.4, 3.7); anchor("ar_d", ax, CX - 3.6, 0.6)
save(fig, OUT + "day14_stir_2.png")


# ---------------------------------------------------------------- 7. After growth: crop, grind, notch
fig, ax = wide()


def ingot_side(x0, x1, y, r, cones=True, col=INGOT):
    pts = [[x0 + (0.8 if cones else 0), y + r], [x1 - (0.6 if cones else 0), y + r]]
    if cones:
        pts += [[x1, y + 0.08], [x1, y - 0.08]]
    pts += [[x1 - (0.6 if cones else 0), y - r], [x0 + (0.8 if cones else 0), y - r]]
    if cones:
        pts += [[x0, y - 0.08], [x0, y + 0.08]]
    ax.add_patch(P.Polygon(pts, closed=True, fc=col, ec=WHITE, lw=2, zorder=3))


ingot_side(0.8, 8.6, 4.4, 0.95)
ax.text(4.7, 5.9, "a fresh ingot: up to about 2 m long", ha="center", fontsize=19, color=WHITE, weight="bold")
anchor("ingot", ax, 4.7, 4.4)
save_step(fig, OUT + "day14_finish_0.png")

for x in (1.6, 8.0):
    ax.plot([x, x], [3.2, 5.6], color=RED, lw=3, ls=(0, (5, 3)), zorder=5)
tag(ax, 11.4, 4.4, "1. cut off the ends", RED, fs=17)
anchor("ends", ax, 1.2, 4.4); anchor("end2", ax, 8.3, 4.4)
save_step(fig, OUT + "day14_finish_1.png")

ingot_side(1.6, 8.0, 1.8, 0.85, cones=False, col="#c3cfdc")
ax.add_patch(P.Circle((10.0, 1.8), 0.85, fc="#c3cfdc", ec=WHITE, lw=2, zorder=3))
ax.add_patch(P.Wedge((10.0, 0.95), 0.16, 0, 180, fc=BG, ec=WHITE, lw=1.5, zorder=4))
tag(ax, 11.95, 2.9, "2. ground perfectly round", GREEN, fs=16)
tag(ax, 12.1, 1.15, "3. a tiny notch", AMBER, fs=16)
anchor("round", ax, 4.8, 1.8); anchor("notch", ax, 10.0, 1.05); anchor("end_view", ax, 10.0, 1.8)
anchor("a", ax, 4.7, 3.5); anchor("b", ax, 4.7, 2.6)
save(fig, OUT + "day14_finish_2.png")


# ---------------------------------------------------------------- 8. Who grows them (split, square)
fig, ax = square()
ax.text(5, 9.0, "chip-grade crystals", ha="center", fontsize=23, color=CYAN, weight="bold")
for (x, y, t) in ((2.6, 7.2, "Japan"), (7.4, 7.2, "Taiwan"), (2.6, 5.4, "Germany"), (7.4, 5.4, "South Korea")):
    ax.add_patch(P.FancyBboxPatch((x - 2.0, y - 0.6), 4.0, 1.2, boxstyle="round,pad=0.05", fc=SEAT, ec=CYAN, lw=2, zorder=2))
    ax.text(x, y, t, ha="center", va="center", fontsize=21, color=WHITE, weight="bold", zorder=3)
ax.text(5, 4.2, "a handful of big wafer makers", ha="center", fontsize=17, color=MUTED)
anchor("makers", ax, 5, 6.3)
save_step(fig, OUT + "day14_world_0.png")

ax.add_patch(P.FancyBboxPatch((0.6, 0.5), 8.8, 2.8, boxstyle="round,pad=0.05", fc=SEAT, ec=GREEN, lw=2.5, zorder=1))
ax.text(5, 2.55, "India", ha="center", fontsize=24, color=GREEN, weight="bold")
ax.text(5, 1.7, "Mundra, Gujarat: big ingots", ha="center", fontsize=19, color=WHITE)
ax.text(5, 1.05, "for solar panels (since 2022)", ha="center", fontsize=17, color=AMBER)
anchor("india", ax, 5, 1.9)
save(fig, OUT + "day14_world_1.png")
print("figs ok")
