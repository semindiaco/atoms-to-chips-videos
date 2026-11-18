"""Diagrams for Day 6: Doping, n-type and p-type. Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"
rng = np.random.default_rng(6)


def wide(w=14, h=6.6):
    fig = plt.figure(figsize=(w, h), dpi=100)
    ax = fig.add_axes([0.02, 0.03, 0.96, 0.94]); ax.set_axis_off()
    ax.set_xlim(0, w); ax.set_ylim(0, h)
    return fig, ax


def reset(ax, xl, yl):
    ax.clear(); ax.set_axis_off(); ax.set_xlim(*xl); ax.set_ylim(*yl)


def electron(ax, x, y, r=0.2, sign=True, col=AMBER, z=4):
    ax.add_patch(P.Circle((x, y), r, color=col, zorder=z))
    if sign:
        ax.text(x, y - 0.01, "−", ha="center", va="center", fontsize=int(r * 85), color=BG, weight="bold", zorder=z + 1)


def hole(ax, x, y, r=0.2, z=4, col=WHITE):
    ax.add_patch(P.Circle((x, y), r, fill=False, ec=col, lw=3, zorder=z))
    ax.text(x, y - 0.01, "+", ha="center", va="center", fontsize=int(r * 85), color=col, weight="bold", zorder=z + 1)


def tag(ax, x, y, text, col=GREEN, fs=19, z=9):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=col, weight="bold", zorder=z,
            bbox=dict(fc=BG, ec=col, boxstyle="round,pad=0.4", lw=2))


# ---------------------------------------------------------------- 1. A pinch changes everything (figure)
def bowl(ax, salt=False):
    ax.add_patch(P.Wedge((2.4, 3.2), 1.9, 180, 360, color=SEAT, ec=MUTED, lw=2.5))
    ax.add_patch(P.Ellipse((2.4, 3.2), 3.8, 0.7, color="#c98a3a", alpha=.85))
    ax.text(2.4, 0.75, "a pot of soup", ha="center", fontsize=19, color=MUTED)
    if salt:
        for k in range(14):
            ax.add_patch(P.Circle((2.4 + rng.uniform(-0.35, 0.35), 4.0 + k * 0.09 + rng.uniform(-0.05, 0.05)), 0.045, color=WHITE))
        ax.text(2.4, 5.65, "a pinch of salt", ha="center", fontsize=19, color=WHITE, weight="bold")


SI_FIELD = [(5.6 + i * 0.52, 0.9 + j * 0.52) for i in range(16) for j in range(9)]
DOP = SI_FIELD[8 * 9 + 4]

fig, ax = wide()
ax.text(7, 6.15, "A tiny pinch can change the whole pot", ha="center", fontsize=24, weight="bold")
bowl(ax)
anchor("soup", ax, 2.4, 2.7)
save_step(fig, OUT + "day06_pinch_0.png")
bowl(ax, salt=True)
anchor("salt", ax, 2.4, 4.3)
save_step(fig, OUT + "day06_pinch_1.png")
for (x, y) in SI_FIELD:
    ax.add_patch(P.Circle((x, y), 0.17, color=CYAN, alpha=.85))
ax.text(9.5, 5.65, "pure silicon: identical atoms", ha="center", fontsize=19, color=CYAN, weight="bold")
anchor("field", ax, 7.2, 2.0)
save_step(fig, OUT + "day06_pinch_2.png")
ax.add_patch(P.Circle(DOP, 0.2, color=GREEN, zorder=5))
ax.text(DOP[0], DOP[1] - 0.01, "P", ha="center", va="center", fontsize=12, color=BG, weight="bold", zorder=6)
tag(ax, 11.6, 0.35, "1 in millions", col=GREEN, fs=17)
anchor("dopant", ax, *DOP)
save(fig, OUT + "day06_pinch_3.png")


# ---------------------------------------------------------------- 2. Silicon's four hands (split)
def si_atom(ax, x, y, r=0.55, label="Si", col=CYAN, fs=20):
    ax.add_patch(P.Circle((x, y), r, color=col, zorder=3))
    ax.text(x, y, label, ha="center", va="center", fontsize=fs, color=BG, weight="bold", zorder=4)


fig, ax = canvas(1000, 960)
reset(ax, (0, 10), (0, 10))
ax.text(5, 9.3, "One silicon atom", ha="center", fontsize=24, weight="bold")
si_atom(ax, 5, 5, r=0.9, fs=30)
for dx, dy in ((0, 1.7), (1.7, 0), (0, -1.7), (-1.7, 0)):
    ax.plot([5 + dx * 0.55, 5 + dx], [5 + dy * 0.55, 5 + dy], color=MUTED, lw=3, zorder=1)
    electron(ax, 5 + dx, 5 + dy, r=0.28, sign=False)
ax.text(5, 1.6, "4 outer electrons = 4 \"hands\"", ha="center", fontsize=22, color=AMBER, weight="bold")
anchor("atom", ax, 5, 5); anchor("hand", ax, 6.7, 5)
save_step(fig, OUT + "day06_hands_0.png")

reset(ax, (0, 10), (0, 10))
ax.text(5, 9.3, "Each atom holds hands with 4 neighbours", ha="center", fontsize=22, weight="bold")
G = [(2 + 3 * i, 2.2 + 3 * j) for i in range(3) for j in range(3)]
for (x, y) in G:
    if x < 8: ax.plot([x, x + 3], [y, y], color=MUTED, lw=3, zorder=1)
    if y < 8: ax.plot([x, x], [y, y + 3], color=MUTED, lw=3, zorder=1)
for (x, y) in G:
    if x < 8:
        for d in (0.2, -0.2): electron(ax, x + 1.5, y + d, r=0.15, sign=False)
    if y < 8:
        for d in (0.2, -0.2): electron(ax, x + d, y + 1.5, r=0.15, sign=False)
for (x, y) in G:
    si_atom(ax, x, y)
anchor("bond", ax, 3.5, 5.2); anchor("lattice", ax, 5, 5.2)
save_step(fig, OUT + "day06_hands_1.png")
tag(ax, 5, 0.6, "every hand is held: no free electrons", fs=19)
anchor("full", ax, 5, 0.6)
save(fig, OUT + "day06_hands_2.png")


# ---------------------------------------------------------------- 3/4. n-type and p-type lattices (figure)
POS = [(1.5 + 2 * i, 1.2 + 2 * j) for i in range(5) for j in range(3)]
C = (5.5, 3.2)


def doped_lattice(ax, title, dop=None, missing=(), extra=None):
    reset(ax, (0, 14), (0, 6.6))
    ax.text(5.5, 6.2, title, ha="center", fontsize=23, weight="bold")
    for (x, y) in POS:
        if x < 9: ax.plot([x, x + 2], [y, y], color=MUTED, lw=3, zorder=1)
        if y < 5: ax.plot([x, x], [y, y + 2], color=MUTED, lw=3, zorder=1)
    for (x, y) in POS:
        if x < 9:
            for dy in (0.17, -0.17):
                if (x + 1, y + dy) not in missing: electron(ax, x + 1, y + dy, r=0.11, sign=False, z=3)
        if y < 5:
            for dx in (0.17, -0.17):
                if (x + dx, y + 1) not in missing: electron(ax, x + dx, y + 1, r=0.11, sign=False, z=3)
    for (x, y) in POS:
        if (x, y) == C and dop:
            col = GREEN if dop == "P" else VIOLET
            ax.add_patch(P.Circle((x, y), 0.42, color=col, zorder=2))
            ax.text(x, y, dop, ha="center", va="center", fontsize=19, color=BG, weight="bold", zorder=3)
        else:
            ax.add_patch(P.Circle((x, y), 0.36, color=CYAN, zorder=2))
            ax.text(x, y, "Si", ha="center", va="center", fontsize=16, color=BG, weight="bold", zorder=3)


def legend(ax, rows):
    y = 5.0
    for kind, text, col in rows:
        if kind == "e": electron(ax, 10.6, y, r=0.2)
        elif kind == "h": hole(ax, 10.6, y, r=0.2)
        else:
            ax.add_patch(P.Circle((10.6, y), 0.24, color=col)); ax.text(10.6, y, kind, ha="center", va="center", fontsize=13, color=BG, weight="bold")
        ax.text(11.0, y, text, va="center", fontsize=17, color=col if kind not in ("e", "h") else (AMBER if kind == "e" else WHITE))
        y -= 0.75


fig, ax = wide()
doped_lattice(ax, "Pure silicon: every bond is full")
anchor("si", ax, 3.5, 3.2); anchor("centre", ax, *C)
save_step(fig, OUT + "day06_ntype_0.png")
doped_lattice(ax, "Swap in a phosphorus atom: 5 outer electrons", dop="P")
EX = (C[0] + 0.55, C[1] + 0.55)
electron(ax, *EX, r=0.2)
legend(ax, [("P", "phosphorus", GREEN), ("e", "the extra electron", AMBER)])
anchor("P", ax, *C); anchor("extra", ax, *EX)
save_step(fig, OUT + "day06_ntype_1.png")
doped_lattice(ax, "The extra electron wanders off, free", dop="P")
FREE = (8.5, 4.2)
electron(ax, *FREE, r=0.22)
ax.text(C[0] - 0.62, C[1] + 0.5, "+", ha="center", va="center", fontsize=30, color=GREEN, weight="bold", zorder=6)
ax.annotate("", xy=(FREE[0] - 0.3, FREE[1]), xytext=(EX[0] + 0.1, EX[1] + 0.1),
            arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=3, connectionstyle="arc3,rad=-0.3"))
legend(ax, [("P", "phosphorus: stays put, +", GREEN), ("e", "free electron", AMBER)])
anchor("P", ax, *C); anchor("extra", ax, *EX); anchor("free", ax, *FREE); anchor("plus", ax, C[0] - 0.62, C[1] + 0.5)
anchor("far", ax, 9.4, 1.2); anchor("mid", ax, 7.5, 4.9)
save_step(fig, OUT + "day06_ntype_2.png")
tag(ax, 12.1, 2.0, "Donor atom\n→ n-type", fs=21)
anchor("donor", ax, 12.1, 2.0)
save(fig, OUT + "day06_ntype_3.png")

H1 = (C[0] + 1, C[1] + 0.17)      # empty spot in the bond to the right of boron
H2 = (C[0] + 3, C[1] + 0.17)
fig, ax = wide()
doped_lattice(ax, "Swap in a boron atom: only 3 outer electrons", dop="B", missing=(H1,))
legend(ax, [("B", "boron", VIOLET)])
anchor("B", ax, *C); anchor("gap", ax, *H1)
save_step(fig, OUT + "day06_ptype_0.png")
hole(ax, *H1, r=0.2)
legend(ax, [("B", "boron", VIOLET), ("h", "hole (missing electron)", WHITE)])
anchor("hole1", ax, *H1)
save_step(fig, OUT + "day06_ptype_1.png")
doped_lattice(ax, "A neighbour's electron hops in: the hole moves on", dop="B", missing=(H2,))
hole(ax, *H2, r=0.2)
ax.text(C[0] - 0.62, C[1] + 0.5, "−", ha="center", va="center", fontsize=34, color=VIOLET, weight="bold", zorder=6)
ax.annotate("", xy=(H1[0] + 0.15, H1[1] + 0.35), xytext=(H2[0] - 0.2, H2[1] + 0.35),
            arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=3, connectionstyle="arc3,rad=0.5"))
legend(ax, [("B", "boron: stays put, −", VIOLET), ("h", "hole, free to move", WHITE)])
anchor("hole1", ax, *H1); anchor("hole2", ax, *H2); anchor("minus", ax, C[0] - 0.62, C[1] + 0.5)
anchor("hop", ax, (H1[0] + H2[0]) / 2, H1[1] + 0.6); anchor("far", ax, 9.4, 1.2)
save_step(fig, OUT + "day06_ptype_2.png")
tag(ax, 12.1, 2.0, "Acceptor atom\n→ p-type", col=VIOLET, fs=21)
anchor("acceptor", ax, 12.1, 2.0)
save(fig, OUT + "day06_ptype_3.png")


# ---------------------------------------------------------------- 5. Majority and minority (split)
def box(ax, y0, title, col, n_e, n_h, ions):
    ax.add_patch(P.FancyBboxPatch((0.8, y0), 8.4, 3.3, boxstyle="round,pad=0.05", fc=SEAT, ec=col, lw=3))
    ax.text(5, y0 + 3.75, title, ha="center", fontsize=22, color=col, weight="bold")
    for i in range(7):  # fixed dopant ions in the middle row
        ax.text(1.6 + i * 1.0, y0 + 1.65, ions, ha="center", va="center", fontsize=22, color=MUTED, weight="bold", alpha=.7)
    major = electron if n_e > n_h else hole
    minor = hole if n_e > n_h else electron
    for i in range(8):
        x = 1.4 + i * 0.95 + rng.uniform(-0.15, 0.15)
        y = y0 + (0.7 if i % 2 else 2.6) + rng.uniform(-0.15, 0.15)
        major(ax, x, y, r=0.2)
    minor(ax, 8.6, y0 + 1.65, r=0.2)


fig, ax = canvas(1000, 960)
reset(ax, (0, 10), (0, 10))
box(ax, 5.2, "n-type silicon", GREEN, 8, 1, "+")
anchor("ntype", ax, 5, 6.85); anchor("nfew", ax, 8.6, 6.85)
save_step(fig, OUT + "day06_majority_0.png")
ax.text(5, 4.85, "electrons: many  ·  holes: very few", ha="center", fontsize=17, color=WHITE)
save_step(fig, OUT + "day06_majority_1.png")
box(ax, 0.6, "p-type silicon", VIOLET, 1, 8, "−")
ax.text(5, 0.15, "holes: many  ·  electrons: very few", ha="center", fontsize=17, color=WHITE)
anchor("ptype", ax, 5, 2.25); anchor("pfew", ax, 8.6, 2.25)
save(fig, OUT + "day06_majority_2.png")


# ---------------------------------------------------------------- 6. The dial: how many carriers (figure)
rows = [("Pure silicon", 0, "×1", MUTED),
        ("Lightly doped (1 in 5 million)", 6, "a million ×", GREEN),
        ("Heavily doped (1 in 500)", 10, "ten billion ×", VIOLET),
        ("Copper (a metal)", 13, "ten trillion ×", AMBER)]
fig, ax = wide()
ax.text(7, 6.15, "Free carriers, compared with pure silicon", ha="center", fontsize=24, weight="bold")
ax.text(7, 0.25, "each step on this scale = 10 times more", ha="center", fontsize=16, color=MUTED)
for g in range(14):
    x = 4.9 + g * 0.45
    ax.plot([x, x], [0.7, 5.6], color=GRID, lw=1.5, zorder=0)
for i, (name, lg, txt, col) in enumerate(rows):
    y = 5.0 - i * 1.25
    ax.text(4.6, y, name, ha="right", va="center", fontsize=18, color=WHITE)
    ax.add_patch(P.FancyBboxPatch((4.9, y - 0.33), 0.12 + lg * 0.45, 0.66, boxstyle="round,pad=0.02", color=col))
    ax.text(4.9 + 0.12 + lg * 0.45 + 0.2, y, txt, va="center", fontsize=19, color=col, weight="bold")
    anchor(f"bar{i}", ax, 4.9 + 0.12 + lg * 0.45, y)
    save_step(fig, OUT + f"day06_dial_{i}.png") if i < 3 else save(fig, OUT + f"day06_dial_{i}.png")


# ---------------------------------------------------------------- 7. How do the atoms get in? (figure)
fig, ax = wide()
ax.text(7, 6.15, "Three ways to add the pinch", ha="center", fontsize=24, weight="bold")
# panel 1: melt
ax.add_patch(P.FancyBboxPatch((0.3, 0.7), 4.2, 4.7, boxstyle="round,pad=0.05", fc=BG, ec=MUTED, lw=1.5))
ax.add_patch(P.Rectangle((0.9, 1.3), 3.0, 1.5, color=MUTED, alpha=.5))
ax.add_patch(P.Rectangle((1.05, 1.45), 2.7, 1.1, color=RED, alpha=.55))
ax.add_patch(P.Rectangle((2.15, 2.55), 0.5, 2.2, color=CYAN, alpha=.9))
ax.plot([2.4, 2.4], [4.75, 5.25], color=WHITE, lw=3)
for k in range(9):
    ax.add_patch(P.Circle((1.3 + rng.uniform(0, 2.2), 1.6 + rng.uniform(0, 0.8)), 0.07, color=GREEN))
ax.text(2.4, 0.3, "1. mixed into the melt", ha="center", fontsize=18, color=WHITE, weight="bold")
anchor("melt", ax, 2.4, 2.0); anchor("crystal", ax, 2.4, 3.6)
save_step(fig, OUT + "day06_howin_0.png")
# panel 2: shot in
ax.add_patch(P.FancyBboxPatch((4.9, 0.7), 4.2, 4.7, boxstyle="round,pad=0.05", fc=BG, ec=MUTED, lw=1.5))
ax.add_patch(P.Rectangle((5.3, 1.2), 3.4, 1.0, color=CYAN, alpha=.75))
for k in range(5):
    x = 5.7 + k * 0.65
    ax.annotate("", xy=(x, 2.3), xytext=(x, 4.9), arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.5, mutation_scale=22))
    ax.add_patch(P.Circle((x + 0.1 * rng.uniform(-1, 1), 1.75 + rng.uniform(-0.2, 0.2)), 0.08, color=GREEN, zorder=4))
ax.text(7.0, 0.3, "2. shot in as fast ions", ha="center", fontsize=18, color=WHITE, weight="bold")
anchor("beam_top", ax, 7.0, 5.0); anchor("beam_mid", ax, 7.0, 3.5); anchor("wafer2", ax, 7.0, 1.7)
save_step(fig, OUT + "day06_howin_1.png")
# panel 3: baked in
ax.add_patch(P.FancyBboxPatch((9.5, 0.7), 4.2, 4.7, boxstyle="round,pad=0.05", fc=BG, ec=MUTED, lw=1.5))
ax.add_patch(P.Rectangle((9.9, 1.2), 3.4, 1.0, color=CYAN, alpha=.75))
for k in range(18):
    x = 10.0 + rng.uniform(0, 3.2)
    ax.add_patch(P.Circle((x, 3.0 + rng.uniform(0, 1.6)), 0.07, color=GREEN))
for k in range(8):
    ax.add_patch(P.Circle((10.0 + rng.uniform(0, 3.2), 1.95 + rng.uniform(-0.15, 0.15)), 0.07, color=GREEN))
for k in range(3):
    xx = np.linspace(10.1, 13.1, 60); ax.plot(xx, 4.95 + k * 0.0 + 0.12 * np.sin(xx * 8 + k), color=RED, lw=2.5) if k == 0 else None
ax.text(11.6, 0.3, "3. baked in with heat", ha="center", fontsize=18, color=WHITE, weight="bold")
anchor("gas", ax, 11.6, 3.8); anchor("wafer3", ax, 11.6, 1.9)
save(fig, OUT + "day06_howin_2.png")


# ---------------------------------------------------------------- 8. Why we need both (split)
def block(ax, x0, col, title, kind):
    ax.add_patch(P.FancyBboxPatch((x0, 3.0), 3.6, 4.0, boxstyle="round,pad=0.03", fc=SEAT, ec=col, lw=3))
    ax.text(x0 + 1.8, 7.5, title, ha="center", fontsize=24, color=col, weight="bold")
    for i in range(3):
        for j in range(4):
            x, y = x0 + 0.6 + i * 1.2, 3.5 + j * 1.0
            (hole if kind == "h" else electron)(ax, x, y, r=0.24)


fig, ax = canvas(1000, 960)
reset(ax, (0, 10), (0, 10))
block(ax, 0.6, VIOLET, "p-type", "h")
anchor("p", ax, 2.4, 5.0)
save_step(fig, OUT + "day06_junction_0.png")
block(ax, 5.8, GREEN, "n-type", "e")
anchor("n", ax, 7.6, 5.0)
save_step(fig, OUT + "day06_junction_1.png")
reset(ax, (0, 10), (0, 10))
block(ax, 1.4, VIOLET, "p", "h"); block(ax, 5.0, GREEN, "n", "e")
ax.plot([5.0, 5.0], [2.6, 7.4], color=WHITE, lw=4, ls="--")
tag(ax, 5.0, 1.6, "p–n junction", col=WHITE, fs=22)
ax.text(5.0, 0.55, "next episode: what happens here?", ha="center", fontsize=18, color=AMBER, weight="bold")
anchor("junction", ax, 5.0, 5.0); anchor("n_side", ax, 7.0, 5.0); anchor("p_side", ax, 3.0, 5.0)
save(fig, OUT + "day06_junction_2.png")
print("figs ok")
