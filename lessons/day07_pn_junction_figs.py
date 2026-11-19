"""Diagrams for Day 7: The p-n junction and the diode. Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"
WATER = "#2f7fd1"
rng = np.random.default_rng(7)


def wide(w=14, h=6.6):
    fig = plt.figure(figsize=(w, h), dpi=100)
    ax = fig.add_axes([0.02, 0.03, 0.96, 0.94]); ax.set_axis_off()
    ax.set_xlim(0, w); ax.set_ylim(0, h)
    return fig, ax


def reset(ax, xl=(0, 14), yl=(0, 6.6)):
    ax.clear(); ax.set_axis_off(); ax.set_xlim(*xl); ax.set_ylim(*yl)


def electron(ax, x, y, r=0.17, z=4):
    ax.add_patch(P.Circle((x, y), r, color=AMBER, zorder=z))
    ax.text(x, y - 0.01, "−", ha="center", va="center", fontsize=int(r * 85), color=BG, weight="bold", zorder=z + 1)


def hole(ax, x, y, r=0.17, z=4):
    ax.add_patch(P.Circle((x, y), r, fill=False, ec=WHITE, lw=2.5, zorder=z))
    ax.text(x, y - 0.01, "+", ha="center", va="center", fontsize=int(r * 85), color=WHITE, weight="bold", zorder=z + 1)


def ion(ax, x, y, sign, s=0.2, z=3):
    col = GREEN if sign == "+" else VIOLET
    ax.add_patch(P.Rectangle((x - s, y - s), 2 * s, 2 * s, color=col, zorder=z))
    ax.text(x, y - 0.02, sign, ha="center", va="center", fontsize=int(s * 80), color=BG, weight="bold", zorder=z + 1)


def tag(ax, x, y, text, col=GREEN, fs=19, z=9):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=col, weight="bold", zorder=z,
            bbox=dict(fc=BG, ec=col, boxstyle="round,pad=0.4", lw=2))


def arrow(ax, a, b, col=WHITE, lw=3, rad=0.0, z=6):
    ax.annotate("", xy=b, xytext=a, zorder=z,
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, mutation_scale=24, connectionstyle=f"arc3,rad={rad}"))


# ---------------------------------------------------------------- 1. A one-way valve (figure)
def pipe(ax, y, state, push=None):
    """state: 'closed' | 'open' | 'blocked'"""
    ax.add_patch(P.Rectangle((1, y - 0.55), 12, 1.1, color=SEAT, zorder=1))
    ax.plot([1, 13], [y + 0.55, y + 0.55], color=MUTED, lw=4, zorder=2)
    ax.plot([1, 13], [y - 0.55, y - 0.55], color=MUTED, lw=4, zorder=2)
    # stop lip on the left of the flap: it lets the flap swing right only
    ax.add_patch(P.Polygon([(6.75, y - 0.55), (6.9, y - 0.55), (6.9, y - 0.3)], color=MUTED, zorder=3))
    if state == "open":
        ax.add_patch(P.Rectangle((1, y - 0.5), 12, 1.0, color=WATER, alpha=.55, zorder=1.5))
        ax.plot([7, 7.85], [y + 0.5, y - 0.15], color=WHITE, lw=6, solid_capstyle="round", zorder=4)
    else:
        if state == "blocked":
            ax.add_patch(P.Rectangle((7.05, y - 0.5), 5.95, 1.0, color=WATER, alpha=.55, zorder=1.5))
        ax.plot([7, 7], [y + 0.5, y - 0.45], color=WHITE, lw=6, solid_capstyle="round", zorder=4)
    ax.add_patch(P.Circle((7, y + 0.5), 0.09, color=AMBER, zorder=5))
    if push == "right":
        arrow(ax, (1.6, y + 1.05), (4.2, y + 1.05), col=CYAN)
        ax.text(2.9, y + 1.45, "push this way", ha="center", fontsize=17, color=CYAN)
    if push == "left":
        arrow(ax, (12.4, y + 1.05), (9.8, y + 1.05), col=CYAN)
        ax.text(11.1, y + 1.45, "push back", ha="center", fontsize=17, color=CYAN)


fig, ax = wide()
ax.text(7, 6.25, "A one-way valve in a water pipe", ha="center", fontsize=24, weight="bold")
pipe(ax, 4.2, "closed")
ax.text(7, 3.05, "a flap that can only swing one way", ha="center", fontsize=18, color=MUTED)
anchor("valve", ax, 7, 4.2); anchor("in_top", ax, 1.6, 4.2); anchor("out_top", ax, 12.6, 4.2)
save_step(fig, OUT + "day07_valve_0.png")
reset(ax)
ax.text(7, 6.25, "A one-way valve in a water pipe", ha="center", fontsize=24, weight="bold")
pipe(ax, 4.2, "open", push="right")
ax.text(13.15, 4.2, "✓", ha="left", va="center", fontsize=34, color=GREEN, weight="bold")
ax.text(7, 3.05, "push forward: the flap opens, water flows", ha="center", fontsize=18, color=GREEN)
anchor("valve", ax, 7.3, 4.2); anchor("in_top", ax, 1.6, 4.2); anchor("out_top", ax, 12.6, 4.2); anchor("mid_top", ax, 7.4, 4.2)
save_step(fig, OUT + "day07_valve_1.png")
pipe(ax, 1.4, "blocked", push="left")
ax.text(13.15, 1.4, "✗", ha="left", va="center", fontsize=34, color=RED, weight="bold")
ax.text(7, 0.25, "push back: the flap slams shut, nothing flows", ha="center", fontsize=18, color=RED)
anchor("valve_bot", ax, 7, 1.4); anchor("push_bot", ax, 10.5, 1.4)
save(fig, OUT + "day07_valve_2.png")


# ---------------------------------------------------------------- 2. Crossing the border (figure)
PH = [(x, y) for x, y in zip(rng.uniform(1.4, 6.2, 22), rng.uniform(0.75, 4.0, 22))]
NE = [(x, y) for x, y in zip(rng.uniform(7.8, 12.6, 22), rng.uniform(0.75, 4.0, 22))]
P_ION = [(1.9 + 0.95 * i, 1.4 + 1.05 * j) for i in range(6) for j in range(4)]
N_ION = [(7.45 + 0.95 * i, 1.4 + 1.05 * j) for i in range(6) for j in range(4)]


def junction(ax, gap=0.0, zone=None, title=""):
    reset(ax)
    ax.text(7, 6.25, title, ha="center", fontsize=23, weight="bold")
    ax.add_patch(P.FancyBboxPatch((1.5 - gap, 0.9), 5.5, 4.0, boxstyle="round,pad=0.04", fc=SEAT, ec=VIOLET, lw=3, zorder=1))
    ax.add_patch(P.FancyBboxPatch((7 + gap, 0.9), 5.5, 4.0, boxstyle="round,pad=0.04", fc=SEAT, ec=GREEN, lw=3, zorder=1))
    ax.text(4.25 - gap, 5.35, "p-type: holes", ha="center", fontsize=20, color=VIOLET, weight="bold")
    ax.text(9.75 + gap, 5.35, "n-type: electrons", ha="center", fontsize=20, color=GREEN, weight="bold")
    if zone:
        ax.add_patch(P.Rectangle((7 - zone, 0.95), 2 * zone, 3.9, color=BG, alpha=.75, zorder=1.5))
    for (x, y) in P_ION:
        if zone is None or x < 7 - zone or x > 7 - zone - 0.01:
            pass
    for (x, y) in P_ION:
        ion(ax, x - gap, y, "−", s=0.13, z=2)
    for (x, y) in N_ION:
        ion(ax, x + gap, y, "+", s=0.13, z=2)
    for (x, y) in PH:
        if zone is None or x + 0.4 < 7 - zone - 0.25:
            hole(ax, x - gap + 0.4, y + 0.42, r=0.17)
    for (x, y) in NE:
        if zone is None or x - 0.4 > 7 + zone + 0.25:
            electron(ax, x + gap - 0.4, y + 0.42, r=0.17)


fig, ax = wide()
junction(ax, gap=0.5, title="Two kinds of doped silicon")
anchor("p", ax, 3.7, 2.9); anchor("n", ax, 10.2, 2.9)
save_step(fig, OUT + "day07_cross_0.png")
junction(ax, title="Join them in one crystal")
anchor("p", ax, 4.2, 2.9); anchor("n", ax, 9.8, 2.9); anchor("border", ax, 7, 2.9)
save_step(fig, OUT + "day07_cross_1.png")
for yy in (1.6, 2.9, 4.2):
    arrow(ax, (8.4, yy), (6.0, yy), col=AMBER, lw=3.5, z=8)
    arrow(ax, (5.6, yy - 0.35), (8.0, yy - 0.35), col=WHITE, lw=3.5, z=8)
ax.text(7, 0.45, "electrons cross left · holes cross right", ha="center", fontsize=18, color=AMBER)
anchor("e_from", ax, 9.8, 3.4); anchor("e_to", ax, 6.2, 3.4); anchor("h_from", ax, 4.2, 2.5); anchor("h_to", ax, 7.8, 2.5)
save_step(fig, OUT + "day07_cross_1b.png")
junction(ax, zone=1.2, title="They meet, cancel out, and leave an empty zone")
for yy in (1.6, 2.9, 4.2):
    ax.add_patch(P.Circle((7, yy + 0.4), 0.28, color=AMBER, alpha=.25, zorder=7))
    ax.add_patch(P.Circle((7, yy + 0.4), 0.12, color=AMBER, zorder=8))
anchor("border", ax, 7, 2.9); anchor("zone", ax, 7, 2.9)
save_step(fig, OUT + "day07_cross_2.png")
junction(ax, zone=1.2, title="Left behind: fixed charges, no free carriers")
ax.annotate("", xy=(5.8, 0.55), xytext=(8.2, 0.55), arrowprops=dict(arrowstyle="<->", color=CYAN, lw=2.5))
ax.text(7, 0.18, "depletion zone", ha="center", fontsize=18, color=CYAN, weight="bold")
anchor("zone", ax, 7, 2.9); anchor("minus", ax, 6.25, 2.45); anchor("plus", ax, 7.6, 2.45); anchor("zlabel", ax, 7, 0.35)
save(fig, OUT + "day07_cross_3.png")


# ---------------------------------------------------------------- 3. The hill (figure)
def zone_panel(ax):
    ax.add_patch(P.FancyBboxPatch((0.6, 0.9), 6.0, 4.2, boxstyle="round,pad=0.04", fc=SEAT, ec=MUTED, lw=2.5))
    ax.add_patch(P.Rectangle((2.6, 0.95), 2.0, 4.1, color=BG, alpha=.8))
    ax.text(1.6, 5.4, "p side", ha="center", fontsize=19, color=VIOLET, weight="bold")
    ax.text(5.6, 5.4, "n side", ha="center", fontsize=19, color=GREEN, weight="bold")
    for y in (1.6, 2.6, 3.6, 4.5):
        ion(ax, 3.1, y, "−", s=0.2); ion(ax, 4.1, y, "+", s=0.2)
        hole(ax, 1.4 + 0.5 * (y % 2), y, r=0.18); electron(ax, 5.6 - 0.4 * (y % 2), y, r=0.18)


fig, ax = wide()
ax.text(3.6, 6.2, "Inside the empty zone", ha="center", fontsize=23, weight="bold")
zone_panel(ax)
anchor("ions", ax, 3.6, 3.1); anchor("minus", ax, 3.1, 2.6); anchor("plus", ax, 4.1, 2.6)
save_step(fig, OUT + "day07_hill_0.png")
arrow(ax, (4.5, 0.55), (2.7, 0.55), col=AMBER, lw=4)
ax.text(3.6, 0.15, "electric push: + side → − side", ha="center", fontsize=16, color=AMBER, weight="bold")
anchor("field", ax, 3.6, 0.5); anchor("e_side", ax, 5.4, 2.6)
save_step(fig, OUT + "day07_hill_1.png")
ax.text(10.4, 6.2, "Like a hill for electrons", ha="center", fontsize=23, weight="bold")
xs = np.linspace(7.4, 13.4, 200)
ys = 1.3 + 2.4 / (1 + np.exp((xs - 10.4) * 3.2))
ax.fill_between(xs, 0.6, ys + 0.6, color=SEAT, zorder=1)
ax.plot(xs, ys + 0.6, color=CYAN, lw=4, zorder=2)
ax.text(8.2, 4.75, "p side", ha="center", fontsize=18, color=VIOLET, weight="bold")
ax.text(12.6, 2.45, "n side", ha="center", fontsize=18, color=GREEN, weight="bold")
for x in (11.9, 12.5, 13.05):
    electron(ax, x, 2.12, r=0.2)
anchor("hill", ax, 10.4, 3.2); anchor("ball", ax, 12.5, 2.1); anchor("top", ax, 8.4, 4.3)
save_step(fig, OUT + "day07_hill_2.png")
ax.annotate("", xy=(13.4, 4.3), xytext=(13.4, 1.9), arrowprops=dict(arrowstyle="<->", color=WHITE, lw=2.5))
ax.text(13.3, 5.0, "about\n0.7 V", ha="center", fontsize=18, color=WHITE, weight="bold")
arrow(ax, (11.6, 2.5), (10.9, 3.1), col=RED, lw=3)
ax.text(11.2, 3.75, "too steep", ha="center", fontsize=16, color=RED, weight="bold")
anchor("height", ax, 13.3, 3.2)
save(fig, OUT + "day07_hill_3.png")


# ---------------------------------------------------------------- 4/5. Forward and reverse circuits (figure)
def circuit(ax, title, forward, zone, lamp=False, pushes=False, pulls=False):
    reset(ax)
    ax.text(7, 6.25, title, ha="center", fontsize=23, weight="bold")
    # wires
    ax.plot([3, 1.4, 1.4, 6.2], [3.7, 3.7, 0.9, 0.9], color=MUTED, lw=4, zorder=1)
    ax.plot([11, 12.6, 12.6, 7.8], [3.7, 3.7, 0.9, 0.9], color=MUTED, lw=4, zorder=1)
    # battery
    ax.add_patch(P.FancyBboxPatch((6.2, 0.45), 1.6, 0.9, boxstyle="round,pad=0.03", fc=SEAT, ec=AMBER, lw=3, zorder=2))
    l, r = ("+", "−") if forward else ("−", "+")
    ax.text(6.55, 0.88, l, ha="center", va="center", fontsize=28, color=AMBER, weight="bold", zorder=3)
    ax.text(7.45, 0.88, r, ha="center", va="center", fontsize=28, color=AMBER, weight="bold", zorder=3)
    ax.text(7, 0.05, "battery", ha="center", fontsize=16, color=MUTED)
    # lamp on the right wire
    ax.add_patch(P.Circle((12.6, 2.3), 0.42, fc=AMBER if lamp else SEAT, ec=WHITE, lw=2.5, zorder=3))
    if lamp:
        for a in np.linspace(0, 2 * np.pi, 9)[:-1]:
            ax.plot([12.6 + 0.55 * np.cos(a), 12.6 + 0.8 * np.cos(a)], [2.3 + 0.55 * np.sin(a), 2.3 + 0.8 * np.sin(a)], color=AMBER, lw=3, zorder=3)
    ax.text(13.35, 2.3, "lamp", va="center", fontsize=15, color=MUTED)
    # the junction bar
    ax.add_patch(P.Rectangle((3, 2.7), 4, 2.0, fc=SEAT, ec=VIOLET, lw=3, zorder=2))
    ax.add_patch(P.Rectangle((7, 2.7), 4, 2.0, fc=SEAT, ec=GREEN, lw=3, zorder=2))
    ax.text(3.5, 5.0, "p", ha="center", fontsize=22, color=VIOLET, weight="bold")
    ax.text(10.5, 5.0, "n", ha="center", fontsize=22, color=GREEN, weight="bold")
    ax.add_patch(P.Rectangle((7 - zone, 2.73), 2 * zone, 1.94, color=BG, alpha=.85, zorder=2.5))
    if zone > 0.15:
        ax.annotate("", xy=(7 - zone, 2.45), xytext=(7 + zone, 2.45), arrowprops=dict(arrowstyle="<->", color=CYAN, lw=2.2))
        ax.text(7, 2.05, "empty zone", ha="center", fontsize=15, color=CYAN, weight="bold")
    for k, x in enumerate(np.arange(3.45, 7 - zone - 0.1, 0.62)):
        hole(ax, x, 3.25 + 0.75 * (k % 2), r=0.18, z=4)
    for k, x in enumerate(np.arange(10.55, 7 + zone + 0.1, -0.62)):
        electron(ax, x, 3.25 + 0.75 * (k % 2), r=0.18, z=4)
    if pushes:
        arrow(ax, (3.4, 5.55), (5.6, 5.55), col=WHITE); arrow(ax, (10.6, 5.55), (8.4, 5.55), col=AMBER)
    if pulls:
        arrow(ax, (5.6, 5.55), (3.4, 5.55), col=WHITE); arrow(ax, (8.4, 5.55), (10.6, 5.55), col=AMBER)


def circuit_anchors(ax):
    for name, xy in {"bat": (7, 0.9), "bat_r": (7.8, 0.9), "br": (12.6, 0.9), "lamp": (12.6, 2.3), "tr": (12.6, 3.7),
                     "n_end": (11, 3.7), "junction": (7, 3.7), "p_end": (3, 3.7), "tl": (1.4, 3.7), "bl": (1.4, 0.9),
                     "bat_l": (6.2, 0.9), "zone": (7, 3.7), "p": (4.6, 3.7), "n": (9.4, 3.7)}.items():
        anchor(name, ax, *xy)


fig, ax = wide()
circuit(ax, "Forward: + to p, − to n", True, 0.9)
circuit_anchors(ax)
save_step(fig, OUT + "day07_fwd_0.png")
circuit(ax, "The battery pushes both crowds to the middle", True, 0.45, pushes=True)
circuit_anchors(ax)
save_step(fig, OUT + "day07_fwd_1.png")
circuit(ax, "The empty zone shrinks: the hill gets lower", True, 0.0, pushes=True)
circuit_anchors(ax)
save_step(fig, OUT + "day07_fwd_2.png")
circuit(ax, "Current flows: the lamp lights up", True, 0.0, lamp=True)
circuit_anchors(ax)
save(fig, OUT + "day07_fwd_3.png")

fig, ax = wide()
circuit(ax, "Reverse: − to p, + to n", False, 0.9)
circuit_anchors(ax)
save_step(fig, OUT + "day07_rev_0.png")
circuit(ax, "The battery pulls both crowds away", False, 1.6, pulls=True)
circuit_anchors(ax)
save_step(fig, OUT + "day07_rev_1.png")
circuit(ax, "The empty zone widens: the hill gets taller", False, 2.1, pulls=True)
ax.text(12.6, 1.55, "dark", ha="center", fontsize=15, color=RED, weight="bold")
circuit_anchors(ax)
save_step(fig, OUT + "day07_rev_2.png")
tag(ax, 7, 2.05, "only a tiny trickle (leakage)", col=RED, fs=17)
anchor("leak", ax, 7, 2.05)
save(fig, OUT + "day07_rev_3.png")


# ---------------------------------------------------------------- 6. The curve (split)
fig, ax = canvas(1000, 960)
reset(ax, (-6, 4), (-2.5, 8))


def axes_base(ax):
    ax.annotate("", xy=(3.8, 0), xytext=(-5.8, 0), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=2.5, mutation_scale=22))
    ax.annotate("", xy=(0, 7.6), xytext=(0, -2.2), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=2.5, mutation_scale=22))
    ax.text(3.7, -0.75, "push\n(volts)", ha="right", fontsize=19, color=MUTED)
    ax.text(0.25, 7.3, "current", fontsize=19, color=MUTED)
    ax.text(2.0, -1.9, "forward →", ha="center", fontsize=18, color=GREEN, weight="bold")
    ax.text(-3.0, -1.9, "← reverse", ha="center", fontsize=18, color=RED, weight="bold")


axes_base(ax)
anchor("origin", ax, 0, 0); anchor("xaxis", ax, 2.8, -0.4); anchor("yaxis", ax, 0.6, 6.8)
save_step(fig, OUT + "day07_curve_0.png")
xr = np.linspace(-5.6, 0, 50)
ax.plot(xr, -0.06 * np.ones_like(xr), color=RED, lw=5)
ax.text(-3.0, 0.5, "almost nothing", ha="center", fontsize=19, color=RED, weight="bold")
anchor("reverse", ax, -3.0, 0.2)
save_step(fig, OUT + "day07_curve_1.png")
xf = np.linspace(0, 1.75, 200)
yf = np.clip(0.004 * (np.exp(xf / 0.26) - 1), 0, 7.3)
ax.plot(xf, yf, color=GREEN, lw=5)
ax.plot([0.7, 0.7], [-0.15, 0.15], color=WHITE, lw=2.5)
anchor("flat", ax, 0.7, 0.35); anchor("knee", ax, 1.55, 2.0); anchor("steep", ax, 1.7, 5.5)
save_step(fig, OUT + "day07_curve_2.png")
ax.text(1.85, 1.2, "switches on\nnear 0.7 V", ha="left", fontsize=18, color=GREEN, weight="bold")
ax.text(0.7, -0.75, "0.7", ha="center", fontsize=16, color=WHITE)
save(fig, OUT + "day07_curve_3.png")


# ---------------------------------------------------------------- 7. The symbol (figure)
fig, ax = wide()
ax.text(7, 6.25, "From p–n junction to diode symbol", ha="center", fontsize=23, weight="bold")
ax.add_patch(P.Rectangle((0.8, 2.6), 1.6, 1.4, fc=SEAT, ec=VIOLET, lw=3))
ax.add_patch(P.Rectangle((2.4, 2.6), 1.6, 1.4, fc=SEAT, ec=GREEN, lw=3))
ax.text(1.6, 3.3, "p", ha="center", va="center", fontsize=30, color=VIOLET, weight="bold")
ax.text(3.2, 3.3, "n", ha="center", va="center", fontsize=30, color=GREEN, weight="bold")
anchor("block", ax, 2.4, 3.3)
save_step(fig, OUT + "day07_symbol_0.png")
arrow(ax, (4.4, 3.3), (5.4, 3.3), col=MUTED)
ax.plot([5.7, 6.9], [3.3, 3.3], color=WHITE, lw=4); ax.plot([8.5, 9.6], [3.3, 3.3], color=WHITE, lw=4)
ax.add_patch(P.Polygon([(6.9, 2.45), (6.9, 4.15), (8.3, 3.3)], color=CYAN))
ax.plot([8.4, 8.4], [2.45, 4.15], color=WHITE, lw=6)
ax.text(6.9, 4.6, "anode (p)", ha="center", fontsize=18, color=VIOLET, weight="bold")
ax.text(8.6, 1.75, "cathode (n)", ha="center", fontsize=18, color=GREEN, weight="bold")
anchor("triangle", ax, 7.4, 3.3); anchor("bar", ax, 8.4, 3.3); anchor("sym", ax, 7.6, 3.3)
save_step(fig, OUT + "day07_symbol_1.png")
arrow(ax, (6.2, 5.3), (9.0, 5.3), col=GREEN)
ax.text(7.6, 5.6, "current allowed this way", ha="center", fontsize=16, color=GREEN)
anchor("dir", ax, 7.6, 5.3)
save_step(fig, OUT + "day07_symbol_2.png")
ax.plot([9.9, 10.6], [3.3, 3.3], color=MUTED, lw=4); ax.plot([12.6, 13.4], [3.3, 3.3], color=MUTED, lw=4)
ax.add_patch(P.FancyBboxPatch((10.6, 2.85), 2.0, 0.9, boxstyle="round,pad=0.05", color="#20242c", ec=MUTED, lw=2))
ax.add_patch(P.Rectangle((12.05, 2.8), 0.32, 1.0, color="#d8dde4"))
ax.text(11.6, 4.35, "real diode", ha="center", fontsize=18, color=WHITE, weight="bold")
ax.text(12.2, 2.0, "stripe = cathode", ha="center", fontsize=16, color=MUTED)
anchor("real", ax, 11.6, 3.3); anchor("stripe", ax, 12.2, 3.3)
save(fig, OUT + "day07_symbol_3.png")


# ---------------------------------------------------------------- 8. Rectifier (figure)
def wave(ax, x0, x1, yc, amp, mode, col, lw=4):
    t = np.linspace(0, 4 * np.pi, 400)
    s = np.sin(t)
    if mode == "half": s = np.clip(s, 0, None)
    if mode == "full": s = np.abs(s)
    xs = x0 + (x1 - x0) * t / t[-1]
    ax.plot(xs, yc + amp * s, color=col, lw=lw)
    ax.plot([x0, x1], [yc, yc], color=MUTED, lw=1.5, ls="--")


fig, ax = wide()
ax.text(7, 6.25, "A diode turns back-and-forth into one-way", ha="center", fontsize=23, weight="bold")
wave(ax, 0.6, 4.6, 3.3, 1.4, "ac", CYAN)
ax.text(2.6, 1.2, "from the wall socket:\nflows back and forth", ha="center", fontsize=17, color=CYAN)
anchor("ac", ax, 2.6, 3.3); anchor("ac_end", ax, 4.6, 3.3); anchor("ac_start", ax, 0.6, 3.3)
save_step(fig, OUT + "day07_rect_0.png")
ax.plot([5.0, 6.0], [3.3, 3.3], color=WHITE, lw=4); ax.plot([7.6, 8.6], [3.3, 3.3], color=WHITE, lw=4)
ax.add_patch(P.Polygon([(6.0, 2.6), (6.0, 4.0), (7.2, 3.3)], color=CYAN))
ax.plot([7.3, 7.3], [2.6, 4.0], color=WHITE, lw=6)
ax.text(6.8, 1.9, "diode", ha="center", fontsize=18, color=WHITE, weight="bold")
anchor("diode", ax, 6.7, 3.3)
save_step(fig, OUT + "day07_rect_1.png")
wave(ax, 9.0, 13.2, 3.3, 1.4, "half", GREEN)
ax.text(11.1, 1.2, "out: only one direction", ha="center", fontsize=17, color=GREEN)
anchor("out", ax, 11.1, 3.3); anchor("out_end", ax, 13.2, 3.3); anchor("out_start", ax, 9.0, 3.3); anchor("gapw", ax, 12.1, 3.4)
save_step(fig, OUT + "day07_rect_2.png")
for art in list(ax.lines)[-2:]:
    art.remove()
for t in ax.texts[-1:]:
    t.remove()
wave(ax, 9.0, 13.2, 3.3, 1.4, "full", GREEN)
ax.text(11.1, 1.2, "with 4 diodes (a bridge):\nboth halves used", ha="center", fontsize=17, color=GREEN)
save(fig, OUT + "day07_rect_3.png")
print("figs done")
