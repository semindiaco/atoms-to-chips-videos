"""Diagrams for Day 9: How a MOSFET works. Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"
WATER = "#2f7fd1"
GLASS = "#9fd8e6"
METAL = "#b8c4d2"


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


def tag(ax, x, y, text, col=GREEN, fs=19, z=9):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=col, weight="bold", zorder=z,
            bbox=dict(fc=BG, ec=col, boxstyle="round,pad=0.4", lw=2))


def arrow(ax, a, b, col=WHITE, lw=3, rad=0.0, z=6, ms=24):
    ax.annotate("", xy=b, xytext=a, zorder=z,
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, mutation_scale=ms, connectionstyle=f"arc3,rad={rad}"))


def battery(ax, x, y, left="−", right="+", label="battery", col=AMBER, w=1.5, lfs=15):
    ax.add_patch(P.FancyBboxPatch((x - w / 2, y - 0.4), w, 0.8, boxstyle="round,pad=0.03", fc=SEAT, ec=col, lw=3, zorder=2))
    ax.text(x - w / 4, y - 0.02, left, ha="center", va="center", fontsize=26, color=col, weight="bold", zorder=3)
    ax.text(x + w / 4, y - 0.02, right, ha="center", va="center", fontsize=26, color=col, weight="bold", zorder=3)
    if label:
        ax.text(x, y - 0.8, label, ha="center", fontsize=lfs, color=MUTED)


# ---------------------------------------------------------------- 1. Drawbridge analogy (figure)
def town(ax, x, name):
    ax.add_patch(P.FancyBboxPatch((x - 1.6, 2.3), 3.2, 2.0, boxstyle="round,pad=0.05", fc=SEAT, ec=GREEN, lw=3, zorder=2))
    for dx in (-0.9, 0.0, 0.9):
        ax.add_patch(P.Rectangle((x + dx - 0.3, 3.5), 0.6, 0.5, color=MUTED, zorder=3))
        ax.add_patch(P.Polygon([(x + dx - 0.38, 4.0), (x + dx + 0.38, 4.0), (x + dx, 4.3)], color=MUTED, zorder=3))
    ax.text(x, 1.7, name, ha="center", fontsize=20, color=GREEN, weight="bold")


def cars(ax, xs, y=2.85):
    for x in xs:
        ax.add_patch(P.FancyBboxPatch((x - 0.22, y - 0.14), 0.44, 0.28, boxstyle="round,pad=0.04", color=AMBER, zorder=5))


def river(ax):
    ax.add_patch(P.Rectangle((5.2, 0.6), 3.6, 4.6, color=WATER, alpha=.55, zorder=1))
    for y in (1.2, 2.0, 4.2):
        ax.plot(np.linspace(5.5, 8.5, 40), y + 0.08 * np.sin(np.linspace(0, 6 * np.pi, 40)), color=WHITE, alpha=.4, lw=2)
    ax.text(7.0, 0.9, "river", ha="center", fontsize=16, color=WHITE)


def keeper(ax):
    ax.add_patch(P.Rectangle((6.6, 5.05), 0.8, 0.75, fc=SEAT, ec=CYAN, lw=2.5, zorder=3))
    ax.text(7.0, 6.15, "bridge keeper", ha="center", fontsize=17, color=CYAN, weight="bold")


fig, ax = wide()
river(ax)
town(ax, 2.6, "town A"); town(ax, 11.4, "town B")
cars(ax, [1.6, 2.3, 3.0, 3.7])
for nm, xy in {"a": (2.6, 3.3), "b": (11.4, 3.3), "river": (7.0, 3.0), "carsA": (2.6, 2.85)}.items():
    anchor(nm, ax, *xy)
save_step(fig, OUT + "day09_bridge_0.png")
keeper(ax)
ax.plot([5.2, 5.2], [2.7, 4.9], color=WHITE, lw=7, zorder=4)
ax.plot([8.8, 8.8], [2.7, 4.9], color=WHITE, lw=7, zorder=4)
ax.text(7.0, 2.35, "bridge up: no traffic", ha="center", fontsize=17, color=RED, weight="bold", zorder=6,
        bbox=dict(fc=BG, ec=RED, boxstyle="round,pad=0.3", lw=2))
for nm, xy in {"keeper": (7.0, 5.6), "up": (7.0, 3.8)}.items():
    anchor(nm, ax, *xy)
save_step(fig, OUT + "day09_bridge_1.png")
reset(ax)
river(ax)
town(ax, 2.6, "town A"); town(ax, 11.4, "town B")
keeper(ax)
ax.add_patch(P.Rectangle((4.9, 2.6), 4.2, 0.5, fc=METAL, ec=WHITE, lw=2, zorder=4))
cars(ax, [2.0, 3.0, 5.6, 7.0, 8.4, 10.8], y=2.85)
ax.text(7.0, 3.75, "bridge down: cars flow", ha="center", fontsize=17, color=GREEN, weight="bold", zorder=6,
        bbox=dict(fc=BG, ec=GREEN, boxstyle="round,pad=0.3", lw=2))
for nm, xy in {"deck": (7.0, 2.85), "a_out": (4.2, 2.85), "b_in": (9.8, 2.85), "a": (2.6, 3.3), "b": (11.4, 3.3)}.items():
    anchor(nm, ax, *xy)
save_step(fig, OUT + "day09_bridge_2.png")
for x, t in ((2.6, "= source"), (11.4, "= drain")):
    ax.text(x, 1.15, t, ha="center", fontsize=18, color=AMBER, weight="bold")
ax.text(9.6, 5.45, "= gate", ha="left", fontsize=18, color=AMBER, weight="bold")
anchor("names", ax, 7.0, 5.6)
save(fig, OUT + "day09_bridge_3.png")


# ---------------------------------------------------------------- 2. M-O-S layers (figure)
SX0, SX1 = 1.0, 10.0
SY0, SY1 = 0.6, 3.0        # silicon body
OY1 = 3.35                 # oxide top
GY1 = 4.35                 # gate top
GX0, GX1 = 3.6, 7.4        # gate / oxide width


def body(ax, holes=True, hole_ys=(1.2, 2.2), skip=None):
    ax.add_patch(P.Rectangle((SX0, SY0), SX1 - SX0, SY1 - SY0, fc=SEAT, ec=VIOLET, lw=3, zorder=2))
    if holes:
        for k, x in enumerate(np.arange(SX0 + 0.6, SX1 - 0.3, 0.9)):
            if skip and any(a < x < b for a, b in skip):
                continue
            hole(ax, x, hole_ys[k % 2], r=0.17)


def oxide(ax):
    ax.add_patch(P.Rectangle((GX0, SY1), GX1 - GX0, OY1 - SY1, fc=GLASS, ec=WHITE, lw=1.5, alpha=.9, zorder=3))


def gate(ax):
    ax.add_patch(P.Rectangle((GX0, OY1), GX1 - GX0, GY1 - OY1, fc=METAL, ec=WHITE, lw=2, zorder=3))


def letter(ax, y, L, text, col):
    ax.text(10.8, y, L, ha="center", va="center", fontsize=40, color=col, weight="bold")
    ax.text(11.5, y, text, ha="left", va="center", fontsize=17, color=col, weight="bold")


fig, ax = wide()
ax.text(7, 6.15, "The name, layer by layer: M – O – S", ha="center", fontsize=23, weight="bold")
body(ax)
letter(ax, 1.8, "S", "semiconductor\n(p-type silicon)", VIOLET)
anchor("si", ax, 5.5, 1.7); anchor("S", ax, 11.6, 1.8)
save_step(fig, OUT + "day09_mos_0.png")
oxide(ax)
ax.plot([GX1, 10.2], [3.17, 3.17], color=GLASS, lw=1.5, ls=":")
letter(ax, 3.17, "O", "oxide: a thin\nlayer of glass", GLASS)
anchor("ox", ax, 5.5, 3.17); anchor("O", ax, 11.6, 3.17)
save_step(fig, OUT + "day09_mos_1.png")
gate(ax)
ax.plot([GX1, 10.2], [3.85, 4.6], color=METAL, lw=1.5, ls=":")
letter(ax, 4.6, "M", "metal: the gate", METAL)
ax.text(5.5, 3.85, "gate", ha="center", va="center", fontsize=18, color=BG, weight="bold", zorder=5)
anchor("metal", ax, 5.5, 3.85); anchor("M", ax, 11.6, 4.6)
save_step(fig, OUT + "day09_mos_2.png")
ax.plot([5.5, 5.5], [GY1, 5.25], color=CYAN, lw=3, zorder=2)
ax.text(5.5, 5.5, "control wire", ha="center", fontsize=16, color=CYAN, weight="bold")
ax.text(2.3, 4.0, "glass blocks\ncurrent", ha="center", va="center", fontsize=16, color=RED, weight="bold")
arrow(ax, (3.0, 3.55), (3.55, 3.2), col=RED, lw=2.2, ms=16)
anchor("wire", ax, 5.5, 5.2); anchor("block", ax, 2.3, 4.0)
save(fig, OUT + "day09_mos_3.png")


# ---------------------------------------------------------------- 3/5. Source and drain, off and on (figure)
NX0, NX1 = 2.0, 4.0        # source island
DX0, DX1 = 7.0, 9.0        # drain island
NY0 = 1.7                  # island bottom


def islands(ax, labels=True):
    for x0, x1, nm in ((NX0, NX1, "source"), (DX0, DX1, "drain")):
        ax.add_patch(P.Rectangle((x0, NY0), x1 - x0, SY1 - NY0, fc=SEAT, ec=GREEN, lw=3, zorder=3))
        for k, x in enumerate(np.linspace(x0 + 0.35, x1 - 0.35, 4)):
            electron(ax, x, 2.05 if k % 2 else 2.6, r=0.16, z=5)
        if labels:
            ax.text((x0 + x1) / 2, 1.2, nm, ha="center", fontsize=18, color=GREEN, weight="bold", zorder=6)


def device(ax, title, gate_v=0, holes_low=False, channel=False, drain_bat=True, tagtxt=None, tagcol=RED):
    reset(ax)
    ax.text(7, 6.25, title, ha="center", fontsize=22, weight="bold")
    body(ax, holes=True, hole_ys=(0.95, 1.35) if holes_low else (1.2, 2.3), skip=((NX0 - 0.15, NX1 + 0.15), (DX0 - 0.15, DX1 + 0.15)))
    # cover holes under drain island too
    islands(ax)
    oxide(ax); gate(ax)
    ax.text((GX0 + GX1) / 2, 3.85, "gate", ha="center", va="center", fontsize=17, color=BG, weight="bold", zorder=5)
    if gate_v:
        for x in np.linspace(GX0 + 0.35, GX1 - 0.35, 6):
            ax.text(x, 4.6, "+", ha="center", va="center", fontsize=20, color=AMBER, weight="bold", zorder=6)
    if channel:
        ax.add_patch(P.Rectangle((NX1 - 0.05, 2.7), DX0 - NX1 + 0.1, 0.28, color=GREEN, alpha=.7, zorder=3.5))
        for x in np.linspace(NX1 + 0.3, DX0 - 0.3, 5):
            electron(ax, x, 2.84, r=0.12, z=6)
    # drain circuit: source wire left & up, drain wire right & up, battery on top right
    if drain_bat:
        ax.plot([NX0 + 0.3, NX0 + 0.3], [SY1, 5.3], color=MUTED, lw=3, zorder=1)
        ax.plot([NX0 + 0.3, 10.2], [5.3, 5.3], color=MUTED, lw=3, zorder=1)
        ax.plot([DX1 - 0.3, DX1 - 0.3], [SY1, 4.4], color=MUTED, lw=3, zorder=1)
        ax.plot([DX1 - 0.3, 11.9, 11.9, 11.6], [4.4, 4.4, 5.3, 5.3], color=MUTED, lw=3, zorder=1)
        battery(ax, 10.9, 5.3, "−", "+", "", w=1.4)
        ax.text(12.9, 4.85, "drain\nbattery", ha="center", va="center", fontsize=15, color=MUTED)
    if gate_v:
        ax.plot([(GX0 + GX1) / 2, (GX0 + GX1) / 2], [GY1, 4.95], color=CYAN, lw=3, zorder=2)
        ax.text((GX0 + GX1) / 2 + 0.2, 5.75, "", fontsize=1)
    if tagtxt:
        tag(ax, 11.6, 2.0, tagtxt, col=tagcol, fs=18)
    for nm, xy in {"source": ((NX0 + NX1) / 2, 2.35), "drain": ((DX0 + DX1) / 2, 2.35), "gap": (5.5, 2.3),
                   "gate": (5.5, 3.85), "bat": (10.9, 5.3), "tag": (11.6, 2.0), "gplus": (5.5, 4.6),
                   "channel": (5.5, 2.84), "ch_l": (NX1, 2.84), "ch_r": (DX0, 2.84), "s_in": (NX0 + 0.3, 2.84),
                   "d_out": (DX1 - 0.3, 2.84), "d_up": (DX1 - 0.3, 4.4), "holes": (5.5, 1.15), "ox": (5.5, 3.17),
                   "s_top": (NX0 + 0.3, 5.3), "body": (5.5, 1.2)}.items():
        anchor(nm, ax, *xy)


fig, ax = wide()
reset(ax); ax.text(7, 6.25, "Add two islands of n-type silicon", ha="center", fontsize=22, weight="bold")
body(ax, skip=((NX0 - 0.15, NX1 + 0.15), (DX0 - 0.15, DX1 + 0.15))); oxide(ax); gate(ax)
ax.text(5.5, 3.85, "gate", ha="center", va="center", fontsize=17, color=BG, weight="bold", zorder=5)
for nm, xy in {"gate": (5.5, 3.85), "body": (5.5, 1.2)}.items():
    anchor(nm, ax, *xy)
save_step(fig, OUT + "day09_sd_0.png")
islands(ax)
for nm, xy in {"source": ((NX0 + NX1) / 2, 2.35), "drain": ((DX0 + DX1) / 2, 2.35), "gap": (5.5, 2.3)}.items():
    anchor(nm, ax, *xy)
save_step(fig, OUT + "day09_sd_1.png")
device(ax, "Connect a battery from source to drain", drain_bat=True)
save_step(fig, OUT + "day09_sd_2.png")
device(ax, "Gate at zero: OFF, no road between the islands", drain_bat=True, tagtxt="OFF", tagcol=RED)
ax.plot([5.0, 6.0], [1.95, 2.65], color=RED, lw=4, zorder=7); ax.plot([5.0, 6.0], [2.65, 1.95], color=RED, lw=4, zorder=7)
save(fig, OUT + "day09_sd_3.png")

fig, ax = wide()
device(ax, "Put a positive voltage on the gate", gate_v=1)
save_step(fig, OUT + "day09_on_0.png")
device(ax, "Holes are pushed away from the surface", gate_v=1, holes_low=True)
arrow(ax, (4.6, 2.5), (4.6, 1.65), col=WHITE, lw=2.2, ms=16); arrow(ax, (6.4, 2.5), (6.4, 1.65), col=WHITE, lw=2.2, ms=16)
save_step(fig, OUT + "day09_on_1.png")
device(ax, "Electrons gather under the glass: a channel", gate_v=1, holes_low=True, channel=True)
save_step(fig, OUT + "day09_on_2.png")
device(ax, "Switch ON: current flows source to drain", gate_v=1, holes_low=True, channel=True, tagtxt="ON", tagcol=GREEN)
ax.text(11.6, 3.4, "gate current:\nalmost zero", ha="center", va="center", fontsize=15, color=CYAN, weight="bold")
anchor("gatei", ax, 11.6, 3.4)
save(fig, OUT + "day09_on_3.png")


# ---------------------------------------------------------------- 4. Balloon and paper (figure)
def balloon(ax, x, y, charged=False):
    ax.add_patch(P.Ellipse((x, y), 2.0, 2.5, fc=RED, ec=WHITE, lw=2, alpha=.85, zorder=3))
    ax.plot([x, x - 0.1, x + 0.1, x], [y - 1.25, y - 1.8, y - 2.3, y - 2.8], color=MUTED, lw=2, zorder=2)
    if charged:
        for dx, dy in ((-0.5, -0.6), (0.0, -0.85), (0.5, -0.6), (-0.4, 0.1), (0.4, 0.2)):
            ax.text(x + dx, y + dy, "−", ha="center", va="center", fontsize=24, color=WHITE, weight="bold", zorder=4)


def bits(ax, x0, up=False):
    rng = np.random.default_rng(3)
    for k in range(9):
        x = x0 + (k % 5) * 0.45 - 0.9 + rng.uniform(-0.1, 0.1)
        y = (1.6 + rng.uniform(0, 0.9) if up and k % 3 != 2 else 0.85) + (0.25 if k >= 5 else 0)
        ang = rng.uniform(0, 80)
        ax.add_patch(P.Rectangle((x, y), 0.3, 0.16, angle=ang, color=WHITE, zorder=3))


fig, ax = wide()
ax.text(7, 6.15, "Pulling without touching", ha="center", fontsize=23, weight="bold")
ax.plot([0.5, 13.5], [0.75, 0.75], color=MUTED, lw=3)
balloon(ax, 3.0, 3.8)
bits(ax, 3.0)
ax.text(3.0, 0.25, "plain balloon: nothing happens", ha="center", fontsize=16, color=MUTED)
anchor("b1", ax, 3.0, 3.8); anchor("paper1", ax, 3.0, 1.0)
save_step(fig, OUT + "day09_balloon_0.png")
ax.text(5.6, 4.3, "rub it on\nyour hair", ha="center", va="center", fontsize=17, color=AMBER, weight="bold")
arrow(ax, (6.3, 3.6), (8.2, 3.6), col=AMBER, lw=3)
balloon(ax, 10.5, 4.0, charged=True)
bits(ax, 10.5, up=False)
anchor("b2", ax, 10.5, 4.0); anchor("rub", ax, 5.6, 4.3); anchor("paper2", ax, 10.5, 1.0)
save_step(fig, OUT + "day09_balloon_1.png")
reset(ax)
ax.text(7, 6.15, "Pulling without touching", ha="center", fontsize=23, weight="bold")
ax.plot([0.5, 13.5], [0.75, 0.75], color=MUTED, lw=3)
balloon(ax, 3.0, 3.8); bits(ax, 3.0)
ax.text(3.0, 0.25, "plain balloon: nothing happens", ha="center", fontsize=16, color=MUTED)
balloon(ax, 10.5, 4.0, charged=True)
bits(ax, 10.5, up=True)
ax.text(10.5, 0.25, "charged balloon: paper jumps up", ha="center", fontsize=16, color=GREEN, weight="bold")
ax.text(6.6, 2.4, "an electric field\nreaches across\nthe gap", ha="center", va="center", fontsize=17, color=CYAN, weight="bold")
for y in (1.9, 2.3, 2.7):
    ax.plot([9.3, 9.7], [y, y + 0.25], color=CYAN, lw=2, ls="--")
anchor("b2", ax, 10.5, 4.0); anchor("paper2", ax, 10.5, 2.1); anchor("field", ax, 6.6, 2.4)
save(fig, OUT + "day09_balloon_2.png")


# ---------------------------------------------------------------- 6. Volume knob (split)
fig, ax = canvas(1000, 960)
reset(ax, (0, 10), (0, 9.6))
ax.annotate("", xy=(9.5, 1.5), xytext=(1.2, 1.5), arrowprops=dict(arrowstyle="-|>", color=WHITE, lw=2.5))
ax.annotate("", xy=(1.2, 8.8), xytext=(1.2, 1.5), arrowprops=dict(arrowstyle="-|>", color=WHITE, lw=2.5))
ax.text(5.3, 0.65, "voltage on the gate", ha="center", fontsize=22, color=WHITE)
ax.text(0.55, 5.1, "current through", ha="center", va="center", rotation=90, fontsize=22, color=WHITE)
ax.plot([1.2, 4.0], [1.62, 1.62], color=AMBER, lw=5)
ax.text(2.6, 2.3, "almost\nnothing", ha="center", fontsize=19, color=MUTED, weight="bold")
anchor("flat", ax, 2.6, 2.3)
save_step(fig, OUT + "day09_knob_0.png")
ax.plot([4.0, 4.0], [1.5, 8.2], color=CYAN, lw=2.5, ls="--")
ax.text(4.0, 8.5, "threshold", ha="center", fontsize=21, color=CYAN, weight="bold")
anchor("thr", ax, 4.0, 8.2)
save_step(fig, OUT + "day09_knob_1.png")
xs = np.linspace(4.0, 9.0, 80)
ax.plot(xs, 1.62 + 0.27 * (xs - 4.0) ** 2, color=AMBER, lw=5)
for x, nm in ((5.5, "low"), (7.0, "mid"), (8.6, "high")):
    y = 1.62 + 0.27 * (x - 4.0) ** 2
    ax.add_patch(P.Circle((x, y), 0.18, color=GREEN, zorder=5))
    anchor(nm, ax, x, y)
ax.text(6.0, 6.8, "more voltage,\nmore current", ha="center", fontsize=20, color=GREEN, weight="bold")
anchor("rise", ax, 7.0, 4.0)
save(fig, OUT + "day09_knob_2.png")


# ---------------------------------------------------------------- 7. Grip: planar, fin, gate-all-around (figure)
def gatecol(ax, poly):
    ax.add_patch(P.Polygon(poly, fc=METAL, ec=WHITE, lw=2, alpha=.95, zorder=3))


fig, ax = wide()
ax.text(7, 6.2, "How the gate grips the channel", ha="center", fontsize=23, weight="bold")
# planar
ax.add_patch(P.Rectangle((0.8, 1.2), 3.4, 1.5, fc=SEAT, ec=VIOLET, lw=2.5, zorder=2))
ax.add_patch(P.Rectangle((1.6, 2.45), 1.8, 0.25, color=GREEN, alpha=.8, zorder=3))
gatecol(ax, [(1.6, 2.7), (3.4, 2.7), (3.4, 3.5), (1.6, 3.5)])
ax.text(2.5, 4.3, "flat (planar)", ha="center", fontsize=19, color=WHITE, weight="bold")
ax.text(2.5, 0.65, "grip from the top:\none finger", ha="center", fontsize=15, color=MUTED)
anchor("planar", ax, 2.5, 2.9)
save_step(fig, OUT + "day09_grip_0.png")
# fin
ax.add_patch(P.Rectangle((5.3, 1.2), 3.4, 0.9, fc=SEAT, ec=VIOLET, lw=2.5, zorder=2))
gatecol(ax, [(6.1, 2.1), (6.1, 3.9), (7.9, 3.9), (7.9, 2.1), (7.45, 2.1), (7.45, 3.45), (6.55, 3.45), (6.55, 2.1)])
ax.add_patch(P.Rectangle((6.55, 2.1), 0.9, 1.35, color=GREEN, alpha=.8, zorder=3))
ax.text(7.0, 4.3, "fin (FinFET)", ha="center", fontsize=19, color=WHITE, weight="bold")
ax.text(7.0, 0.65, "grip on three sides:\nthree fingers", ha="center", fontsize=15, color=MUTED)
anchor("fin", ax, 7.0, 2.8)
save_step(fig, OUT + "day09_grip_1.png")
# gate-all-around
ax.add_patch(P.Rectangle((9.8, 1.2), 3.4, 0.6, fc=SEAT, ec=VIOLET, lw=2.5, zorder=2))
gatecol(ax, [(10.5, 1.8), (12.5, 1.8), (12.5, 3.95), (10.5, 3.95)])
for y in (2.1, 2.75, 3.4):
    ax.add_patch(P.Rectangle((10.85, y), 1.3, 0.3, color=GREEN, alpha=.95, zorder=4))
ax.text(11.5, 4.3, "gate-all-around", ha="center", fontsize=19, color=WHITE, weight="bold")
ax.text(11.5, 0.65, "grip on every side:\nyour whole fist", ha="center", fontsize=15, color=MUTED)
anchor("gaa", ax, 11.5, 2.9)
save_step(fig, OUT + "day09_grip_2.png")
for x, t in ((2.5, "until ~2011"), (7.0, "from 2011"), (11.5, "newest chips")):
    ax.text(x, 5.3, t, ha="center", fontsize=17, color=AMBER, weight="bold")
anchor("years", ax, 7.0, 5.3); anchor("yr_gaa", ax, 11.5, 5.3)
save(fig, OUT + "day09_grip_3.png")
print("figs done")
