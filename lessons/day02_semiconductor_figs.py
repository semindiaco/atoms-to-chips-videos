"""Diagrams for Day 2: What is a semiconductor? Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"
rng = np.random.default_rng(2)

# 1. Metal: fixed ions in a sea of free electrons
fig, ax = canvas(); ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.set_aspect("equal")
for i in range(5):
    for j in range(4):
        x, y = 1.2 + i * 1.9, 1.3 + j * 1.75
        ax.add_patch(P.Circle((x, y), 0.45, color=AMBER, zorder=2))
        ax.text(x, y, "+", ha="center", va="center", fontsize=26, color=BG, weight="bold", zorder=3)
ions = [(1.2 + i * 1.9, 1.3 + j * 1.75) for i in range(5) for j in range(4)]
placed = 0
while placed < 32:
    x, y = rng.uniform(0.3, 9.7), rng.uniform(0.4, 7.4)
    if min((x - a) ** 2 + (y - b) ** 2 for a, b in ions) < 0.75 ** 2: continue
    placed += 1
    ax.add_patch(P.Circle((x, y), 0.13, color=CYAN, zorder=4))
for y in (2.15, 4.75):
    ax.annotate("", xy=(9.6, y), xytext=(0.4, y), arrowprops=dict(arrowstyle="-|>", color=CYAN, lw=2, alpha=.55), zorder=1)
ax.text(5, 7.85, "Metal: a 'sea' of free electrons", ha="center", fontsize=26, weight="bold")
ax.text(5, -0.15, "metal ions (+) stay put  ·  electrons (blue) roam freely", ha="center", fontsize=19, color=MUTED)
save(fig, OUT + "day02_metal_sea.png")

# 2. Insulator: every electron locked in a bond
fig, ax = canvas(); n = 4; ax.set_xlim(-0.8, n - 0.2); ax.set_ylim(-1.1, n - 0.1); ax.set_aspect("equal")
for i in range(n):
    for j in range(n):
        for di, dj in ((1, 0), (0, 1)):
            if i + di < n and j + dj < n:
                ax.plot([i, i + di], [j, j + dj], color=MUTED, lw=3, zorder=1)
                mx, my = i + di / 2, j + dj / 2
                off = 0.09
                for s in (-1, 1):
                    ax.add_patch(P.Circle((mx + s * off * dj, my + s * off * di), 0.065, color=CYAN, zorder=3))
for i in range(n):
    for j in range(n):
        ax.add_patch(P.Circle((i, j), 0.27, color=VIOLET, zorder=2))
ax.add_patch(P.FancyBboxPatch((1.36, -0.18), 0.28, 0.36, boxstyle="round,pad=0.03", fill=False, ec=AMBER, lw=3, zorder=5))
ax.annotate("2 electrons locked\nin every bond", xy=(1.5, -0.22), xytext=(1.5, -0.68), ha="center", va="center", fontsize=19,
            color=AMBER, arrowprops=dict(arrowstyle="->", color=AMBER, lw=2))
ax.text(1.5, n - 0.25, "Insulator: no free electrons", ha="center", fontsize=26, weight="bold")
save(fig, OUT + "day02_insulator_bonds.png")

# 3. Resistivity ladder (log scale)
fig = plt.figure(figsize=(14, 6.6), dpi=100); ax = fig.add_axes([0.03, 0.2, 0.94, 0.68])
ax.set_xlim(-9, 18); ax.set_ylim(0, 10); ax.set_axis_off()
zones = [(-9, -5, CYAN, "CONDUCTORS"), (-5, 6, AMBER, "SEMICONDUCTORS"), (8, 18, VIOLET, "INSULATORS")]
for a, b, c, t in zones:
    ax.add_patch(P.Rectangle((a, 4.2), b - a, 1.2, color=c, alpha=.9))
    ax.text((a + b) / 2, 4.8, t, ha="center", va="center", fontsize=18, color=BG, weight="bold")
for e in range(-8, 19, 4):
    ax.plot([e, e], [3.9, 4.2], color=MUTED, lw=2)
    ax.text(e, 3.3, f"$10^{{{e}}}$", ha="center", fontsize=20, color=MUTED)
mats = [(np.log10(1.7e-8), "Copper", 1), (np.log10(1e-7), "Iron", 0),
        (np.log10(0.46), "Germanium", 1), (np.log10(2.3e3), "Pure\nsilicon", 0),
        (np.log10(1e-2), "Doped\nsilicon", 0),
        (np.log10(1e12), "Glass", 1), (np.log10(1e14), "Rubber", 0), (np.log10(7e17), "Quartz", 1)]
for x, name, up in mats:
    if up:
        ax.plot([x, x], [5.4, 7.0], color=WHITE, lw=2); ax.add_patch(P.Circle((x, 5.4), 0.18, color=WHITE))
        ax.text(x, 7.3, name, ha="center", va="bottom", fontsize=19)
    else:
        ax.plot([x, x], [1.6, 4.2], color=WHITE, lw=2); ax.add_patch(P.Circle((x, 4.2), 0.18, color=WHITE))
        ax.text(x, 1.4, name, ha="center", va="top", fontsize=19)
fig.text(0.5, 0.94, "Resistivity at room temperature (ohm-metres, approximate)", ha="center", fontsize=24, weight="bold")
fig.text(0.5, 0.04, "each step to the right = 10,000 times more resistance", ha="center", fontsize=19, color=MUTED)
save(fig, OUT + "day02_resistivity_ladder.png")

# 4. Three band pictures side by side
fig = plt.figure(figsize=(14, 6.6), dpi=100); ax = fig.add_axes([0.02, 0.04, 0.96, 0.86])
ax.set_xlim(0, 30); ax.set_ylim(0, 10); ax.set_axis_off()
for k, (name, cb, vb, gap) in enumerate([("Metal", 4.4, 5.0, "overlap"), ("Semiconductor", 6.0, 4.6, "small gap"),
                                         ("Insulator", 7.7, 3.0, "huge gap")]):
    x0 = 1.5 + k * 10
    ax.add_patch(P.FancyBboxPatch((x0, cb), 6, 9.2 - cb, boxstyle="round,pad=0.05", color=CYAN, alpha=.85))
    ax.add_patch(P.FancyBboxPatch((x0, 0.8), 6, vb - 0.8, boxstyle="round,pad=0.05", color=AMBER, alpha=.85))
    ax.text(x0 + 3, 9.75, name, ha="center", fontsize=26, weight="bold")
    if gap != "overlap":
        ax.annotate("", xy=(x0 + 6.7, cb), xytext=(x0 + 6.7, vb), arrowprops=dict(arrowstyle="<->", color=WHITE, lw=2.5))
        ax.text(x0 + 3, (cb + vb) / 2, gap, ha="center", va="center", fontsize=20, color=WHITE)
    else:
        ax.text(x0 + 3, (cb + vb) / 2 + 0.05, "bands overlap", ha="center", va="center", fontsize=18, color=BG, weight="bold")
    ax.text(x0 + 3, (cb + 9.2) / 2, "conduction\nband", ha="center", va="center", fontsize=17, color=BG, weight="bold")
    ax.text(x0 + 3, (vb + 0.8) / 2, "valence\nband", ha="center", va="center", fontsize=17, color=BG, weight="bold")
ax.annotate("", xy=(0.6, 9.3), xytext=(0.6, 0.8), arrowprops=dict(arrowstyle="->", color=MUTED, lw=2))
ax.text(0.2, 5, "Energy", rotation=90, va="center", ha="center", color=MUTED)
save(fig, OUT + "day02_three_bands.png")

# 5. Resistance vs temperature (illustrative)
fig, ax = canvas(1000, 800, axis=True)
t = np.linspace(0, 1, 200)
ax.plot(t, 0.35 + 0.35 * t, color=CYAN, lw=5, label="Metal")
ax.plot(t, 0.15 + 0.8 * np.exp(-4 * t), color=AMBER, lw=5, label="Semiconductor")
ax.text(0.97, 0.74, "metal:\nresistance rises", ha="right", va="bottom", fontsize=20, color=CYAN)
ax.text(0.2, 0.75, "semiconductor:\nresistance falls fast", ha="left", va="bottom", fontsize=20, color=AMBER)
ax.set_xlabel("Temperature  →", fontsize=22); ax.set_ylabel("Resistance  →", fontsize=22)
ax.set_xticks([]); ax.set_yticks([]); ax.set_ylim(0, 1.05)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.axes[0].set_position([0.12, 0.14, 0.84, 0.78])
fig.text(0.54, 0.95, "Heat it up (illustrative)", ha="center", fontsize=26, weight="bold")
save(fig, OUT + "day02_temperature.png")

# 6. Doped silicon lattice
fig, ax = lattice("P")
ax.text(2, -0.72, "Silicon with one phosphorus atom", ha="center", fontsize=24, weight="bold")
save(fig, OUT + "day02_lattice_P.png")

# 7. From control to chip
fig, ax = flow(["Control\nconductivity", "Build a\nswitch", "Transistor", "Billions\n= a chip"], [AMBER, CYAN, GREEN, VIOLET])
save(fig, OUT + "day02_control_to_chip.png")
print("figs ok")
