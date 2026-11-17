"""Diagrams for Day 5: Electrons and holes. Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
SEAT = "#1b2b44"


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


def hole(ax, x, y, r=0.2, z=4):
    ax.add_patch(P.Circle((x, y), r, fill=False, ec=WHITE, lw=3, zorder=z))
    ax.text(x, y - 0.01, "+", ha="center", va="center", fontsize=int(r * 85), color=WHITE, weight="bold", zorder=z + 1)


# ---------------------------------------------------------------- 1. The empty seat that moves
def seats(ax, gap, title, ghost=None):
    reset(ax, (0, 14), (0, 6.6))
    ax.text(7, 6.05, title, ha="center", fontsize=25, weight="bold")
    ax.add_patch(P.Rectangle((0.5, 1.55), 13, 0.25, color=MUTED, alpha=.5))  # floor of the row
    for k in range(9):
        x = 1.4 + k * 1.4
        ax.add_patch(P.FancyBboxPatch((x - 0.5, 1.85), 1.0, 1.5, boxstyle="round,pad=0.06", color=SEAT, ec=MUTED, lw=1.5))
        if k == gap:
            ax.text(x, 2.6, "empty", ha="center", va="center", fontsize=15, color=MUTED, style="italic")
            continue
        ax.add_patch(P.FancyBboxPatch((x - 0.38, 2.15), 0.76, 1.05, boxstyle="round,pad=0.08", color=CYAN, alpha=.9, zorder=3))
        ax.add_patch(P.Circle((x, 3.75), 0.3, color=AMBER, zorder=3))
    if ghost is not None:
        a, b = ghost
        xa, xb = 1.4 + a * 1.4, 1.4 + b * 1.4
        ax.annotate("", xy=(xb + 0.1, 4.55), xytext=(xa - 0.1, 4.55),
                    arrowprops=dict(arrowstyle="-|>", color=WHITE, lw=4, mutation_scale=34, connectionstyle="arc3,rad=0.4"))
    return [1.4 + k * 1.4 for k in range(9)]


fig, ax = wide()
xs = seats(ax, 2, "A full row of seats, with one empty")
anchor("gap_a", ax, xs[2], 2.6); anchor("row", ax, xs[6], 3.4)
save_step(fig, OUT + "day05_seats_0.png")
xs = seats(ax, 3, "The next person shuffles over one seat", ghost=(3, 2))
anchor("mover", ax, xs[2], 3.75); anchor("gap_b", ax, xs[3], 2.6)
save_step(fig, OUT + "day05_seats_1.png")
xs = seats(ax, 7, "Keep going: people move left, the gap moves right")
ax.annotate("", xy=(2.0, 0.95), xytext=(7.0, 0.95), arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=4, mutation_scale=30))
ax.text(4.5, 0.4, "people move ←", ha="center", fontsize=20, color=AMBER, weight="bold")
ax.annotate("", xy=(12.0, 0.95), xytext=(7.4, 0.95), arrowprops=dict(arrowstyle="-|>", color=WHITE, lw=4, mutation_scale=30))
ax.text(9.7, 0.4, "empty seat moves →", ha="center", fontsize=20, color=WHITE, weight="bold")
anchor("gap_c", ax, xs[7], 2.6); anchor("people_arrow", ax, 4.5, 0.95); anchor("gap_arrow", ax, 9.7, 0.95)
anchor("path_a", ax, xs[2], 4.5); anchor("path_c", ax, xs[7], 4.5)
save_step(fig, OUT + "day05_seats_2.png")
ax.add_patch(P.FancyBboxPatch((9.9, 4.55), 3.9, 1.05, boxstyle="round,pad=0.08", fc=BG, ec=AMBER, lw=2, zorder=6))
ax.text(11.85, 5.3, "people = electrons", ha="center", fontsize=18, color=AMBER, weight="bold", zorder=7)
ax.text(11.85, 4.82, "empty seat = a hole", ha="center", fontsize=18, color=WHITE, weight="bold", zorder=7)
anchor("legend", ax, 11.85, 5.05)
save(fig, OUT + "day05_seats_3.png")


# ---------------------------------------------------------------- 2. One jump, two carriers (split)
def bands(ax, skip=None):
    reset(ax, (0, 10), (0, 10))
    ax.add_patch(P.FancyBboxPatch((1.2, 6.4), 7.6, 2.6, boxstyle="round,pad=0.05", fc=CYAN, alpha=.18, ec=CYAN, lw=3))
    ax.add_patch(P.FancyBboxPatch((1.2, 1.0), 7.6, 2.6, boxstyle="round,pad=0.05", fc=AMBER, alpha=.30, ec=AMBER, lw=3))
    for i in range(11):
        for j in range(3):
            if (i, j) == skip: continue
            electron(ax, 1.6 + i * 0.68, 1.45 + j * 0.8, r=0.17, sign=False)
    ax.text(5.0, 9.35, "Conduction band (upper floor)", ha="center", fontsize=20, color=CYAN, weight="bold")
    ax.text(5.0, 0.35, "Valence band (lower floor)", ha="center", fontsize=20, color=AMBER, weight="bold")
    ax.annotate("", xy=(0.5, 9.3), xytext=(0.5, 0.8), arrowprops=dict(arrowstyle="->", color=MUTED, lw=2))
    ax.text(0.25, 5.0, "Energy", rotation=90, va="center", ha="center", color=MUTED, fontsize=17)


fig, ax = canvas(1000, 960)
bands(ax)
ax.text(5.0, 7.7, "empty", ha="center", va="center", fontsize=20, color=MUTED, style="italic")
ax.text(5.0, 5.0, "gap", ha="center", va="center", fontsize=20, color=WHITE)
anchor("conduction", ax, 3.0, 7.7); anchor("valence", ax, 3.0, 2.3)
save_step(fig, OUT + "day05_jump_0.png")
hx, hy = 1.6 + 6 * 0.68, 1.45 + 2 * 0.8; ex, ey = hx, 7.6
bands(ax, skip=(6, 2))
ax.add_patch(P.Circle((hx, hy), 0.22, fill=False, ec=WHITE, lw=3, ls="--", zorder=4))
electron(ax, ex, ey, r=0.3)
ax.annotate("", xy=(ex, ey - 0.45), xytext=(hx, hy + 0.35), arrowprops=dict(arrowstyle="-|>", color=WHITE, lw=3.5, mutation_scale=28))
ax.text(ex - 0.35, 5.0, "heat or\nlight", ha="right", va="center", fontsize=19, color=WHITE)
ax.text(ex + 0.5, ey, "free electron", va="center", fontsize=20, color=AMBER, weight="bold")
anchor("from", ax, hx, hy + 0.3); anchor("mid", ax, ex, 5.0); anchor("to", ax, ex, ey - 0.3); anchor("electron", ax, ex, ey)
save_step(fig, OUT + "day05_jump_1.png")
hole(ax, hx, hy, r=0.3, z=6)
ax.text(hx + 0.5, hy + 0.05, "hole", va="center", fontsize=20, color=WHITE, weight="bold", zorder=7,
        bbox=dict(fc=BG, ec="none", pad=3))
anchor("hole", ax, hx, hy)
save_step(fig, OUT + "day05_jump_2.png")
ax.text(8.15, 5.0, "one jump =\ntwo carriers", ha="center", va="center", fontsize=19, color=GREEN, weight="bold",
        bbox=dict(fc=BG, ec=GREEN, boxstyle="round,pad=0.4", lw=2))
anchor("two", ax, 8.15, 5.0); anchor("cb_left", ax, 1.8, 7.6); anchor("vb_right", ax, 8.4, hy)
save(fig, OUT + "day05_jump_3.png")


# ---------------------------------------------------------------- 3. Inside the crystal: bonds, a broken bond, a moving hole
def lattice_bonds(ax, missing=(), title=""):
    reset(ax, (0, 14), (0, 6.6))
    ax.text(5.5, 6.2, title, ha="center", fontsize=23, weight="bold")
    pos = [(1.5 + 2 * i, 1.2 + 2 * j) for i in range(5) for j in range(3)]
    for (x, y) in pos:
        if x < 9: ax.plot([x, x + 2], [y, y], color=MUTED, lw=3, zorder=1)
        if y < 5: ax.plot([x, x], [y, y + 2], color=MUTED, lw=3, zorder=1)
    for (x, y) in pos:
        if x < 9:
            for dy in (0.17, -0.17):
                if (x + 1, y + dy) not in missing:
                    electron(ax, x + 1, y + dy, r=0.11, sign=False, z=3)
        if y < 5:
            for dx in (0.17, -0.17):
                if (x + dx, y + 1) not in missing:
                    electron(ax, x + dx, y + 1, r=0.11, sign=False, z=3)
    for (x, y) in pos:
        ax.add_patch(P.Circle((x, y), 0.36, color=CYAN, zorder=2))
        ax.text(x, y, "Si", ha="center", va="center", fontsize=16, color=BG, weight="bold", zorder=3)
    # legend
    lx = 10.7
    electron(ax, lx, 4.6, r=0.11, sign=False); ax.text(lx + 0.35, 4.6, "bond electron", va="center", fontsize=17)
    electron(ax, lx, 3.8, r=0.2); ax.text(lx + 0.35, 3.8, "free electron", va="center", fontsize=17, color=AMBER)
    hole(ax, lx, 3.0, r=0.2); ax.text(lx + 0.35, 3.0, "hole (missing", va="center", fontsize=17)
    ax.text(lx + 0.35, 2.55, "electron)", va="center", fontsize=17)


h1 = (4.5, 3.2 + 0.17); h2 = (6.5, 3.2 + 0.17)
fig, ax = wide()
lattice_bonds(ax, title="Every bond holds two electrons")
anchor("bond", ax, 4.5, 3.2); anchor("atom", ax, 3.5, 3.2)
save_step(fig, OUT + "day05_lattice_0.png")
lattice_bonds(ax, missing=(h1,), title="Heat breaks one bond")
hole(ax, *h1, r=0.2)
electron(ax, 4.5, 4.35, r=0.22)
ax.annotate("", xy=(4.5, 4.08), xytext=(h1[0], h1[1] + 0.25), arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=2.5))
anchor("hole1", ax, *h1); anchor("free", ax, 4.5, 4.35); anchor("free_far", ax, 9.4, 5.2)
anchor("cell", ax, 4.5, 4.2)
save_step(fig, OUT + "day05_lattice_1.png")
lattice_bonds(ax, missing=(h2,), title="A neighbour fills it, so the hole moves")
hole(ax, *h2, r=0.2)
electron(ax, 8.5, 4.2, r=0.22)
ax.annotate("", xy=(h1[0] + 0.2, h1[1] + 0.35), xytext=(h2[0] - 0.2, h2[1] + 0.35),
            arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=3, connectionstyle="arc3,rad=0.5"))
ax.annotate("", xy=(h2[0] + 0.05, h2[1] - 0.45), xytext=(h1[0] - 0.05, h1[1] - 0.45),
            arrowprops=dict(arrowstyle="-|>", color=WHITE, lw=3, connectionstyle="arc3,rad=0.5"))
ax.text(5.5, 2.15, "hole →", ha="center", fontsize=17, color=WHITE, weight="bold", bbox=dict(fc=BG, ec="none", pad=2), zorder=8)
anchor("hole2", ax, *h2); anchor("hop", ax, 5.5, 3.7)
save(fig, OUT + "day05_lattice_2.png")


# ---------------------------------------------------------------- 4. Drift: a battery pushes both carriers
rng = np.random.default_rng(7)
fig, ax = wide()
ax.add_patch(P.FancyBboxPatch((2.0, 2.3), 10.0, 2.4, boxstyle="round,pad=0.05", fc=SEAT, ec=MUTED, lw=2))
ax.text(7.0, 5.0, "a bar of silicon", ha="center", fontsize=18, color=MUTED)
for k in range(9):
    electron(ax, 2.6 + k * 1.1 + rng.uniform(-0.2, 0.2), 4.05 + rng.uniform(-0.12, 0.12), r=0.19)
    hole(ax, 3.0 + k * 1.05 + rng.uniform(-0.2, 0.2), 2.95 + rng.uniform(-0.12, 0.12), r=0.19)
for x in (2.0, 12.0):
    ax.plot([x, x], [2.3, 0.8], color=WHITE, lw=2.5)
ax.plot([2.0, 6.6], [0.8, 0.8], color=WHITE, lw=2.5); ax.plot([7.4, 12.0], [0.8, 0.8], color=WHITE, lw=2.5)
ax.plot([6.6, 6.6], [0.35, 1.25], color=WHITE, lw=4); ax.plot([7.4, 7.4], [0.55, 1.05], color=WHITE, lw=6)
ax.text(7.0, 0.05, "battery", ha="center", fontsize=16, color=MUTED)
ax.text(1.55, 2.0, "+", ha="center", fontsize=40, color=RED, weight="bold")
ax.text(12.45, 2.0, "−", ha="center", fontsize=40, color=CYAN, weight="bold")
anchor("bar", ax, 7.0, 3.5); anchor("plus", ax, 1.55, 2.3); anchor("minus", ax, 12.45, 2.3)
anchor("e_r", ax, 11.6, 4.05); anchor("e_l", ax, 2.4, 4.05); anchor("h_l", ax, 2.4, 2.95); anchor("h_r", ax, 11.6, 2.95)
save_step(fig, OUT + "day05_drift_0.png")
ax.text(12.6, 4.05, "electrons\n← to +", va="center", fontsize=17, color=AMBER, weight="bold")
save_step(fig, OUT + "day05_drift_1.png")
ax.text(12.6, 2.95, "holes\n→ to −", va="center", fontsize=17, color=WHITE, weight="bold")
save_step(fig, OUT + "day05_drift_2.png")
ax.annotate("", xy=(10.5, 5.75), xytext=(3.5, 5.75), arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=5, mutation_scale=34))
ax.text(7.0, 6.15, "both add up to one current →", ha="center", fontsize=21, color=GREEN, weight="bold")
anchor("current", ax, 7.0, 5.75)
save(fig, OUT + "day05_drift_3.png")


# ---------------------------------------------------------------- 5. Diffusion: crowded to empty
fig, ax = wide()
titles = ["at the start", "a moment later", "evenly spread"]
spreads = [(0.15, 1.2), (0.15, 2.6), (0.15, 3.85)]
for p in range(3):
    x0 = 0.4 + p * 4.6
    ax.add_patch(P.FancyBboxPatch((x0, 1.2), 4.0, 3.9, boxstyle="round,pad=0.05", fc=SEAT, ec=MUTED, lw=2))
    lo, hi = spreads[p]
    pts = rng.uniform(0, 1, (26, 2))
    if p == 0: xs_ = x0 + 0.25 + pts[:, 0] ** 1.0 * 0.95
    elif p == 1: xs_ = x0 + 0.25 + (pts[:, 0] ** 1.6) * 2.6
    else: xs_ = x0 + 0.25 + pts[:, 0] * 3.5
    for x, y in zip(xs_, 1.5 + pts[:, 1] * 3.3):
        electron(ax, x, y, r=0.15, sign=False)
    ax.text(x0 + 2.0, 0.65, titles[p], ha="center", fontsize=19, color=WHITE, weight="bold")
    anchor(f"p{p}", ax, x0 + 2.0, 3.15)
    if p == 0:
        anchor("crowd", ax, x0 + 0.8, 3.15); anchor("empty0", ax, x0 + 3.5, 3.15)
        ax.text(7.0, 6.05, "No push needed: carriers spread from crowded to empty", ha="center", fontsize=22, weight="bold")
        save_step(fig, OUT + "day05_diffusion_0.png")
    elif p == 1:
        anchor("front", ax, x0 + 2.6, 3.15)
        save_step(fig, OUT + "day05_diffusion_1.png")
save(fig, OUT + "day05_diffusion_2.png")


# ---------------------------------------------------------------- 6. Recombination (split)
def rec_base(ax):
    reset(ax, (0, 10), (0, 10))
    ax.add_patch(P.FancyBboxPatch((1.2, 6.4), 7.6, 2.6, boxstyle="round,pad=0.05", fc=CYAN, alpha=.18, ec=CYAN, lw=3))
    ax.add_patch(P.FancyBboxPatch((1.2, 1.0), 7.6, 2.6, boxstyle="round,pad=0.05", fc=AMBER, alpha=.30, ec=AMBER, lw=3))
    ax.text(5.0, 9.35, "Conduction band", ha="center", fontsize=20, color=CYAN, weight="bold")
    ax.text(5.0, 0.35, "Valence band", ha="center", fontsize=20, color=AMBER, weight="bold")


fig, ax = canvas(1000, 960)
rec_base(ax)
ex, ey, hx, hy = 4.0, 7.7, 5.6, 2.3
electron(ax, ex, ey, r=0.32); hole(ax, hx, hy, r=0.32)
ax.text(ex + 0.55, ey, "free electron", va="center", fontsize=19, color=AMBER, weight="bold")
ax.text(hx + 0.55, hy, "hole", va="center", fontsize=19, color=WHITE, weight="bold")
anchor("e", ax, ex, ey); anchor("h", ax, hx, hy); anchor("mid", ax, (ex + hx) / 2, 5.0)
save_step(fig, OUT + "day05_recombine_0.png")
ax.annotate("", xy=(hx - 0.15, hy + 0.45), xytext=(ex, ey - 0.45),
            arrowprops=dict(arrowstyle="-|>", color=WHITE, lw=3.5, mutation_scale=28, ls="--"))
ax.text(2.0, 5.0, "falls back", fontsize=19, color=WHITE, va="center")
save_step(fig, OUT + "day05_recombine_1.png")
rec_base(ax)
electron(ax, hx, hy, r=0.32, sign=False)
for k in range(3):
    xx = np.linspace(6.3, 8.4, 60); ax.plot(xx, hy + 0.9 + k * 0.45 + 0.12 * np.sin(xx * 9), color=RED, lw=2.5)
ax.text(7.3, 4.75, "energy → heat", ha="center", fontsize=19, color=RED, weight="bold")
ax.text(5.0, 7.7, "electron gone", ha="center", va="center", fontsize=19, color=MUTED, style="italic")
ax.text(5.0, 5.4, "the pair disappears", ha="center", fontsize=22, color=GREEN, weight="bold",
        bbox=dict(fc=BG, ec=GREEN, boxstyle="round,pad=0.4", lw=2))
anchor("filled", ax, hx, hy); anchor("heat", ax, 7.3, 3.6); anchor("pair", ax, 5.0, 5.4)
save(fig, OUT + "day05_recombine_2.png")


# ---------------------------------------------------------------- 7. How many carriers? (split)
fig, ax = canvas(1000, 960); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
cols = [(0.4, "Copper", 160, CYAN, "about one free\nelectron per atom"),
        (3.65, "Pure silicon", 0, AMBER, "about one per\nfive trillion atoms"),
        (6.9, "Doped silicon", 22, GREEN, "add a pinch of\nanother element")]
for c, (x0, name, n, col, note) in enumerate(cols):
    ax.add_patch(P.FancyBboxPatch((x0, 2.3), 2.7, 6.0, boxstyle="round,pad=0.05", fc=SEAT, ec=col, lw=3))
    pts = rng.uniform(0, 1, (n, 2))
    for x, y in pts:
        ax.add_patch(P.Circle((x0 + 0.2 + x * 2.3, 2.55 + y * 5.5), 0.09, color=col, zorder=3))
    if n == 0:
        ax.add_patch(P.Circle((x0 + 1.35, 5.3), 0.12, color=col, zorder=3))
    ax.text(x0 + 1.35, 8.95, name, ha="center", fontsize=21, weight="bold", color=col)
    ax.text(x0 + 1.35, 1.85, note, ha="center", va="top", fontsize=16, color=WHITE)
    anchor(["copper", "silicon", "doped"][c], ax, x0 + 1.35, 5.3)
    if c == 0:
        save_step(fig, OUT + "day05_carriers_0.png")
    elif c == 1:
        save_step(fig, OUT + "day05_carriers_1.png")
ax.text(8.25, 9.55, "next episode", ha="center", fontsize=16, color=MUTED, style="italic")
save(fig, OUT + "day05_carriers_2.png")
