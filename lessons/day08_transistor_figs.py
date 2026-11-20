"""Diagrams for Day 8: The transistor. Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"
WATER = "#2f7fd1"


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


def lamp(ax, x, y, on, r=0.42):
    ax.add_patch(P.Circle((x, y), r, fc=AMBER if on else SEAT, ec=WHITE, lw=2.5, zorder=3))
    if on:
        for a in np.linspace(0, 2 * np.pi, 9)[:-1]:
            ax.plot([x + (r + 0.13) * np.cos(a), x + (r + 0.38) * np.cos(a)],
                    [y + (r + 0.13) * np.sin(a), y + (r + 0.38) * np.sin(a)], color=AMBER, lw=3, zorder=3)


def battery(ax, x, y, left="−", right="+", label="battery", col=AMBER, w=1.6):
    ax.add_patch(P.FancyBboxPatch((x - w / 2, y - 0.45), w, 0.9, boxstyle="round,pad=0.03", fc=SEAT, ec=col, lw=3, zorder=2))
    ax.text(x - w / 4, y - 0.02, left, ha="center", va="center", fontsize=28, color=col, weight="bold", zorder=3)
    ax.text(x + w / 4, y - 0.02, right, ha="center", va="center", fontsize=28, color=col, weight="bold", zorder=3)
    if label:
        ax.text(x, y - 0.85, label, ha="center", fontsize=16, color=MUTED)


# ---------------------------------------------------------------- 1. A tap for electricity (figure)
def pipe(ax, opened):
    ax.add_patch(P.Rectangle((0.6, 3.45), 7.6, 1.1, color=SEAT, zorder=1))
    ax.plot([0.6, 8.2], [4.55, 4.55], color=MUTED, lw=4, zorder=2)
    ax.plot([0.6, 8.2], [3.45, 3.45], color=MUTED, lw=4, zorder=2)
    if opened:
        ax.add_patch(P.Rectangle((0.6, 3.5), 7.6, 1.0, color=WATER, alpha=.6, zorder=1.5))
    else:
        ax.add_patch(P.Rectangle((0.6, 3.5), 3.8, 1.0, color=WATER, alpha=.6, zorder=1.5))
    # the gate inside the pipe
    gy = 4.45 if opened else 3.5
    ax.add_patch(P.Rectangle((4.25, gy), 0.3, 1.0 if not opened else 0.12, color=WHITE, zorder=4))
    # stem and knob
    ax.plot([4.4, 4.4], [4.55, 5.25], color=MUTED, lw=5, zorder=3)
    ax.add_patch(P.Ellipse((4.4, 5.35), 1.3, 0.32, color=CYAN, zorder=4))


fig, ax = wide()
ax.text(4.4, 6.2, "A tap in a water pipe", ha="center", fontsize=24, weight="bold")
pipe(ax, False)
ax.text(4.4, 2.6, "tap closed: no flow", ha="center", fontsize=19, color=RED, weight="bold")
for nm, xy in {"knob": (4.4, 5.35), "tap": (4.4, 4.0), "pipe_in": (1.0, 4.0), "pipe_out": (7.8, 4.0), "water": (2.4, 4.0)}.items():
    anchor(nm, ax, *xy)
save_step(fig, OUT + "day08_tap_0.png")
reset(ax)
ax.text(4.4, 6.2, "A tap in a water pipe", ha="center", fontsize=24, weight="bold")
pipe(ax, True)
arrow(ax, (3.5, 5.75), (5.3, 5.75), col=CYAN, lw=2.5, rad=-0.35, ms=18)
ax.text(2.3, 5.75, "small twist", ha="center", va="center", fontsize=17, color=CYAN, weight="bold")
ax.text(4.4, 2.6, "big flow of water", ha="center", fontsize=19, color=GREEN, weight="bold")
arrow(ax, (5.6, 3.0), (7.6, 3.0), col=GREEN, lw=3)
for nm, xy in {"knob": (4.4, 5.35), "tap": (4.4, 4.0), "pipe_in": (1.0, 4.0), "pipe_out": (7.8, 4.0), "flowlbl": (4.4, 2.6)}.items():
    anchor(nm, ax, *xy)
save_step(fig, OUT + "day08_tap_1.png")
# the electrical version
ax.plot([9.0, 13.6], [6.55, 6.55], alpha=0)
ax.text(11.3, 6.2, "A transistor", ha="center", fontsize=24, weight="bold", color=AMBER)
ax.plot([8.9, 10.2], [4.0, 4.0], color=WHITE, lw=6, zorder=2)
ax.plot([12.4, 13.7], [4.0, 4.0], color=WHITE, lw=6, zorder=2)
ax.add_patch(P.FancyBboxPatch((10.2, 3.3), 2.2, 1.4, boxstyle="round,pad=0.05", fc=SEAT, ec=AMBER, lw=3, zorder=3))
ax.text(11.3, 4.0, "switch", ha="center", va="center", fontsize=19, color=AMBER, weight="bold", zorder=4)
ax.plot([11.3, 11.3], [4.7, 5.5], color=CYAN, lw=2.5, zorder=2)
ax.text(11.3, 5.75, "tiny control signal", ha="center", fontsize=16, color=CYAN, weight="bold")
ax.text(11.3, 2.6, "big current", ha="center", fontsize=19, color=GREEN, weight="bold")
arrow(ax, (10.1, 3.0), (12.5, 3.0), col=GREEN, lw=3)
for nm, xy in {"tr": (11.3, 4.0), "ctrl": (11.3, 5.6), "big_in": (9.0, 4.0), "big_out": (13.6, 4.0), "ctrl_top": (11.3, 5.5)}.items():
    anchor(nm, ax, *xy)
save(fig, OUT + "day08_tap_2.png")


# ---------------------------------------------------------------- 2. The sandwich (figure)
X0, X1, X2, X3 = 2.0, 6.4, 7.6, 12.0   # emitter | base | collector
YB, YT = 2.2, 4.4


def block(ax, x0, x1, col, name, sub, ly=1.55):
    ax.add_patch(P.Rectangle((x0, YB), x1 - x0, YT - YB, fc=SEAT, ec=col, lw=3, zorder=2))
    ax.text((x0 + x1) / 2, ly, name, ha="center", fontsize=20, color=col, weight="bold")
    ax.text((x0 + x1) / 2, ly - 0.5, sub, ha="center", fontsize=15, color=MUTED)


def fill_carriers(ax, x0, x1, kind, n=10):
    xs = np.linspace(x0 + 0.45, x1 - 0.45, n)
    for k, x in enumerate(xs):
        y = 2.85 if k % 2 else 3.75
        (electron if kind == "e" else hole)(ax, x, y, r=0.18)


fig, ax = wide()
ax.text(7, 6.15, "Build a transistor: an n–p–n sandwich", ha="center", fontsize=23, weight="bold")
block(ax, X0, X1, GREEN, "n", "emitter")
fill_carriers(ax, X0, X1, "e", 8)
anchor("emitter", ax, (X0 + X1) / 2, 3.3)
save_step(fig, OUT + "day08_npn_0.png")
block(ax, X1, X2, VIOLET, "p", "base")
hole(ax, 7.0, 2.85, r=0.18); hole(ax, 7.0, 3.75, r=0.18)
anchor("base", ax, 7.0, 3.3); anchor("thin", ax, 7.0, 4.75)
ax.annotate("", xy=(X1, 4.75), xytext=(X2, 4.75), arrowprops=dict(arrowstyle="<->", color=CYAN, lw=2.2))
ax.text(7.0, 5.0, "very thin", ha="center", fontsize=16, color=CYAN, weight="bold")
save_step(fig, OUT + "day08_npn_1.png")
block(ax, X2, X3, GREEN, "n", "collector")
fill_carriers(ax, X2, X3, "e", 8)
anchor("collector", ax, (X2 + X3) / 2, 3.3)
save_step(fig, OUT + "day08_npn_2.png")


def mini_diode(ax, x, y, flip=False, col=WHITE):
    s = -1 if flip else 1
    ax.add_patch(P.Polygon([(x - 0.35 * s, y - 0.3), (x - 0.35 * s, y + 0.3), (x + 0.2 * s, y)], color=col, zorder=7))
    ax.plot([x + 0.25 * s, x + 0.25 * s], [y - 0.3, y + 0.3], color=col, lw=4, zorder=7)


# two diodes back to back: p->n arrows point outward from the base
mini_diode(ax, X1, 5.65, flip=True, col=CYAN)
mini_diode(ax, X2, 5.65, flip=False, col=CYAN)
ax.text(5.6, 5.6, "junction 1", ha="right", fontsize=17, color=CYAN, weight="bold")
ax.text(8.4, 5.6, "junction 2", ha="left", fontsize=17, color=CYAN, weight="bold")
ax.plot([X1, X1], [YB - 0.1, YT + 0.1], color=CYAN, lw=2, ls="--", zorder=5)
ax.plot([X2, X2], [YB - 0.1, YT + 0.1], color=CYAN, lw=2, ls="--", zorder=5)
anchor("j1", ax, X1, 3.3); anchor("j2", ax, X2, 3.3); anchor("diodes", ax, 7.0, 5.65)
save(fig, OUT + "day08_npn_3.png")


# ---------------------------------------------------------------- 3/4. Off and on circuits (figure)
EX0, EX1, BX1, CX1 = 2.6, 6.0, 6.8, 10.6
BY0, BY1 = 3.3, 4.5
MY = (BY0 + BY1) / 2


def tcircuit(ax, title, base_on, zone1, zone2, lit=False, inject=False, label=None, lcol=GREEN):
    reset(ax)
    ax.text(7, 6.3, title, ha="center", fontsize=23, weight="bold")
    # main loop wires
    ax.plot([EX0, 1.2, 1.2, 6.2], [MY, MY, 0.9, 0.9], color=MUTED, lw=4, zorder=1)
    ax.plot([CX1, 12.6, 12.6, 7.8], [MY, MY, 0.9, 0.9], color=MUTED, lw=4, zorder=1)
    battery(ax, 7.0, 0.9, "−", "+", "big battery")
    lamp(ax, 12.6, 2.3, lit)
    ax.text(13.45, 2.3, "lamp", va="center", fontsize=15, color=MUTED)
    # sandwich
    ax.add_patch(P.Rectangle((EX0, BY0), EX1 - EX0, BY1 - BY0, fc=SEAT, ec=GREEN, lw=3, zorder=2))
    ax.add_patch(P.Rectangle((EX1, BY0), BX1 - EX1, BY1 - BY0, fc=SEAT, ec=VIOLET, lw=3, zorder=2))
    ax.add_patch(P.Rectangle((BX1, BY0), CX1 - BX1, BY1 - BY0, fc=SEAT, ec=GREEN, lw=3, zorder=2))
    ax.text((EX0 + EX1) / 2, 2.75, "emitter", ha="center", fontsize=16, color=GREEN, weight="bold")
    ax.text((EX1 + BX1) / 2, 2.75, "base", ha="center", fontsize=16, color=VIOLET, weight="bold")
    ax.text((BX1 + CX1) / 2, 2.75, "collector", ha="center", fontsize=16, color=GREEN, weight="bold")
    # empty zones
    if zone1 > 0.02:
        ax.add_patch(P.Rectangle((EX1 - zone1, BY0 + 0.03), zone1 * 1.4, BY1 - BY0 - 0.06, color=BG, alpha=.85, zorder=2.5))
    if zone2 > 0.02:
        ax.add_patch(P.Rectangle((BX1 - 0.2, BY0 + 0.03), zone2 + 0.2, BY1 - BY0 - 0.06, color=BG, alpha=.85, zorder=2.5))
        ax.add_patch(P.Rectangle((BX1 - 0.2, BY0 + 0.03), zone2 + 0.2, BY1 - BY0 - 0.06, fill=False, ec=CYAN, lw=2, ls="--", zorder=2.6))
    for k, x in enumerate(np.arange(EX0 + 0.4, EX1 - zone1 - 0.15, 0.6)):
        electron(ax, x, MY + (0.28 if k % 2 else -0.28), r=0.17)
    for k, x in enumerate(np.arange(CX1 - 0.4, BX1 + zone2 + 0.15, -0.6)):
        electron(ax, x, MY + (0.28 if k % 2 else -0.28), r=0.17)
    if inject:
        for y in (MY + 0.3, MY - 0.3):
            electron(ax, 6.4, y, r=0.15, z=6)
    # base wire with a small battery and a switch
    ax.plot([6.4, 6.4, 5.2], [BY1, 5.5, 5.5], color=MUTED, lw=3, zorder=1)
    ax.plot([4.2, 1.2, 1.2], [5.5, 5.5, MY], color=MUTED, lw=3, zorder=1)
    if base_on:
        ax.plot([4.2, 5.2], [5.5, 5.5], color=CYAN, lw=3, zorder=2)
    else:
        ax.plot([4.2, 5.05], [5.5, 5.95], color=MUTED, lw=3, zorder=2)
    ax.add_patch(P.Circle((4.2, 5.5), 0.08, color=WHITE, zorder=3)); ax.add_patch(P.Circle((5.2, 5.5), 0.08, color=WHITE, zorder=3))
    ax.add_patch(P.FancyBboxPatch((2.2, 5.18), 1.1, 0.64, boxstyle="round,pad=0.03", fc=SEAT, ec=CYAN, lw=2.5, zorder=2))
    ax.text(2.48, 5.48, "−", ha="center", va="center", fontsize=20, color=CYAN, weight="bold", zorder=3)
    ax.text(3.02, 5.48, "+", ha="center", va="center", fontsize=20, color=CYAN, weight="bold", zorder=3)
    ax.text(4.7, 6.0 if base_on else 6.15, "", fontsize=1)
    ax.text(8.6, 5.5, "small push on the base: " + ("ON" if base_on else "OFF"), ha="center", va="center",
            fontsize=17, color=CYAN if base_on else MUTED, weight="bold")
    if label:
        tag(ax, 7.0, 2.05, label, col=lcol, fs=17)
    for nm, xy in {"bat": (7.0, 0.9), "bat_l": (6.2, 0.9), "bl": (1.2, 0.9), "tl": (1.2, MY), "e_end": (EX0, MY),
                   "emitter": ((EX0 + EX1) / 2, MY), "j1": (EX1, MY), "base": (6.4, MY), "j2": (BX1 + 0.3, MY),
                   "collector": ((BX1 + CX1) / 2, MY), "c_end": (CX1, MY), "tr": (12.6, MY), "lamp": (12.6, 2.3),
                   "br": (12.6, 0.9), "bat_r": (7.8, 0.9), "sw": (4.7, 5.6), "small": (2.75, 5.5), "b_top": (6.4, 5.5),
                   "b_mid": (6.4, BY1), "tagpos": (7.0, 2.05), "wall": (BX1 + 0.4, MY), "cap": (8.6, 5.5)}.items():
        anchor(nm, ax, *xy)


fig, ax = wide()
tcircuit(ax, "No push on the base", False, 0.35, 0.35)
save_step(fig, OUT + "day08_off_0.png")
tcircuit(ax, "Junction 2 is reverse biased: a wide wall", False, 0.35, 1.2)
save_step(fig, OUT + "day08_off_1.png")
tcircuit(ax, "Switch OFF: no current, lamp dark", False, 0.35, 1.2, label="OFF", lcol=RED)
save(fig, OUT + "day08_off_2.png")

fig, ax = wide()
tcircuit(ax, "A small push on the base", True, 0.35, 1.2)
save_step(fig, OUT + "day08_on_0.png")
tcircuit(ax, "Junction 1 opens: electrons rush into the base", True, 0.0, 1.2, inject=True)
save_step(fig, OUT + "day08_on_1.png")
tcircuit(ax, "The base is thin: most shoot straight through", True, 0.0, 1.2, inject=True)
arrow(ax, (6.0, 2.0), (9.2, 2.0), col=AMBER, lw=3)
ax.text(10.9, 2.0, "about 99 in 100", ha="center", va="center", fontsize=16, color=AMBER, weight="bold")
arrow(ax, (6.75, 4.8), (6.75, 5.25), col=CYAN, lw=2, ms=16)
ax.text(7.05, 4.95, "1 in 100", ha="left", va="center", fontsize=14, color=CYAN, weight="bold")
save_step(fig, OUT + "day08_on_2.png")
tcircuit(ax, "Switch ON: big current, lamp lit", True, 0.0, 1.2, lit=True, inject=True, label="ON", lcol=GREEN)
save(fig, OUT + "day08_on_3.png")


# ---------------------------------------------------------------- 5. Amplifier (figure)
def wave(ax, x0, x1, yc, amp, col, lw=4, cycles=3):
    t = np.linspace(0, cycles * 2 * np.pi, 400)
    xs = x0 + (x1 - x0) * t / t[-1]
    ax.plot([x0, x1], [yc, yc], color=MUTED, lw=1.5, ls="--")
    ax.plot(xs, yc + amp * np.sin(t), color=col, lw=lw)


fig, ax = wide()
ax.text(7, 6.25, "Small wiggle in, big wiggle out", ha="center", fontsize=23, weight="bold")
wave(ax, 0.6, 4.4, 3.3, 0.3, CYAN)
ax.text(2.5, 1.6, "tiny signal\n(from a microphone)", ha="center", fontsize=17, color=CYAN)
anchor("in", ax, 2.5, 3.3); anchor("in_start", ax, 0.6, 3.3); anchor("in_end", ax, 4.4, 3.3)
save_step(fig, OUT + "day08_amp_0.png")
ax.plot([4.6, 5.6], [3.3, 3.3], color=WHITE, lw=4); ax.plot([8.4, 9.4], [3.3, 3.3], color=WHITE, lw=4)
ax.add_patch(P.FancyBboxPatch((5.6, 2.6), 2.8, 1.4, boxstyle="round,pad=0.05", fc=SEAT, ec=AMBER, lw=3, zorder=3))
ax.text(7.0, 3.3, "transistor", ha="center", va="center", fontsize=19, color=AMBER, weight="bold", zorder=4)
ax.plot([7.0, 7.0], [4.0, 4.9], color=MUTED, lw=3)
ax.text(7.0, 5.15, "power from a battery", ha="center", fontsize=15, color=MUTED)
anchor("tr", ax, 7.0, 3.3); anchor("power", ax, 7.0, 5.0); anchor("tr_in", ax, 4.6, 3.3); anchor("tr_out", ax, 9.4, 3.3)
save_step(fig, OUT + "day08_amp_1.png")
wave(ax, 9.6, 13.4, 3.3, 1.7, GREEN)
ax.text(11.5, 0.9, "same shape, much bigger\n(to drive a speaker)", ha="center", fontsize=17, color=GREEN)
anchor("out", ax, 11.5, 3.3); anchor("peak", ax, 10.25, 5.0); anchor("out_end", ax, 13.4, 3.3)
save(fig, OUT + "day08_amp_2.png")


# ---------------------------------------------------------------- 6. Ones and zeros (split)
fig, ax = canvas(1000, 960)
reset(ax, (0, 10), (0, 9.6))
lamp(ax, 2.8, 7.6, False, r=0.75)
lamp(ax, 7.2, 7.6, True, r=0.75)
ax.text(2.8, 5.9, "OFF = 0", ha="center", fontsize=26, color=MUTED, weight="bold")
ax.text(7.2, 5.9, "ON = 1", ha="center", fontsize=26, color=AMBER, weight="bold")
anchor("off", ax, 2.8, 7.2); anchor("on", ax, 7.2, 7.2)
save_step(fig, OUT + "day08_bits_0.png")
bits = "01000001"
for i, b in enumerate(bits):
    x = 0.95 + i * 1.16
    lamp(ax, x, 3.8, b == "1", r=0.36)
    ax.text(x, 2.45, b, ha="center", fontsize=26, color=AMBER if b == "1" else MUTED, weight="bold")
anchor("row", ax, 5.0, 3.6); anchor("bit_a", ax, 2.11, 3.8); anchor("bit_b", ax, 9.07, 3.8)
save_step(fig, OUT + "day08_bits_1.png")
ax.text(5.0, 1.55, "eight switches = the letter  A", ha="center", fontsize=24, color=GREEN, weight="bold")
anchor("letter", ax, 5.0, 1.65)
save(fig, OUT + "day08_bits_2.png")


# ---------------------------------------------------------------- 7. AND logic (figure)
def sw(ax, x0, name, on):
    """A transistor drawn as a labelled switch on the top wire (y=4.0) between x0 and x0+1.6."""
    ax.add_patch(P.FancyBboxPatch((x0, 3.4), 1.6, 1.2, boxstyle="round,pad=0.05", fc=SEAT, ec=GREEN if on else RED, lw=3, zorder=2))
    ax.add_patch(P.Circle((x0 + 0.3, 4.0), 0.08, color=WHITE, zorder=4)); ax.add_patch(P.Circle((x0 + 1.3, 4.0), 0.08, color=WHITE, zorder=4))
    if on:
        ax.plot([x0 + 0.3, x0 + 1.3], [4.0, 4.0], color=GREEN, lw=4, zorder=3)
    else:
        ax.plot([x0 + 0.3, x0 + 1.15], [4.0, 4.45], color=RED, lw=4, zorder=3)
    ax.plot([x0 + 0.8, x0 + 0.8], [4.6, 5.25], color=CYAN, lw=2.5)
    ax.text(x0 + 0.8, 5.55, f"{name}: {'ON' if on else 'OFF'}", ha="center", fontsize=18, color=GREEN if on else RED, weight="bold")


def and_circuit(ax, a, b, title, note=None, ncol=MUTED):
    reset(ax)
    ax.text(7, 6.3, title, ha="center", fontsize=23, weight="bold")
    ax.plot([1.2, 3.6], [4.0, 4.0], color=MUTED, lw=4, zorder=1)
    ax.plot([5.2, 7.6], [4.0, 4.0], color=MUTED, lw=4, zorder=1)
    ax.plot([9.2, 12.6, 12.6, 7.8], [4.0, 4.0, 0.9, 0.9], color=MUTED, lw=4, zorder=1)
    ax.plot([1.2, 1.2, 6.2], [4.0, 0.9, 0.9], color=MUTED, lw=4, zorder=1)
    battery(ax, 7.0, 0.9, "+", "−", "battery")
    sw(ax, 3.6, "A", a); sw(ax, 7.6, "B", b)
    lamp(ax, 12.6, 2.4, a and b)
    ax.text(13.45, 2.4, "lamp", va="center", fontsize=15, color=MUTED)
    if note:
        ax.text(6.9, 2.45, note, ha="center", va="center", fontsize=18, color=ncol, weight="bold")
    for nm, xy in {"A": (4.4, 4.0), "B": (8.4, 4.0), "lamp": (12.6, 2.4), "tl": (1.2, 4.0), "bl": (1.2, 0.9),
                   "bat_l": (6.2, 0.9), "tr": (12.6, 4.0), "br": (12.6, 0.9), "bat_r": (7.8, 0.9), "note": (6.9, 2.45),
                   "mid": (6.4, 4.0)}.items():
        anchor(nm, ax, *xy)


fig, ax = wide()
and_circuit(ax, False, False, "Two transistor switches in a row", "both off: lamp dark", RED)
save_step(fig, OUT + "day08_and_0.png")
and_circuit(ax, True, False, "Two transistor switches in a row", "only A on: still dark", RED)
save_step(fig, OUT + "day08_and_1.png")
and_circuit(ax, True, True, "Two transistor switches in a row", "A and B on: lamp lights!", GREEN)
save_step(fig, OUT + "day08_and_2.png")
and_circuit(ax, True, True, "An AND gate: on only if A AND B are on", "computers are built from millions of these", AMBER)
save(fig, OUT + "day08_and_3.png")
print("figs done")
