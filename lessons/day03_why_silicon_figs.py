"""Diagrams for Day 3: Why silicon? Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np

OUT = "out/figs/"

# 1. Earth's crust by mass (approximate textbook values)
fig = plt.figure(figsize=(14, 6.6), dpi=100); ax = fig.add_axes([0.17, 0.12, 0.78, 0.72])
els = ["Oxygen", "Silicon", "Aluminium", "Iron", "Calcium", "All others"]
vals = [46, 28, 8, 5, 4, 9]
cols = [MUTED, CYAN, MUTED, MUTED, MUTED, MUTED]
ax.barh(els[::-1], vals[::-1], color=cols[::-1], height=0.62)
for i, v in enumerate(vals[::-1]):
    ax.text(v + 0.8, i, f"~{v}%", va="center", fontsize=22, weight="bold", color=CYAN if els[::-1][i] == "Silicon" else WHITE)
ax.set_xlim(0, 55); ax.set_xticks([])
for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
ax.tick_params(axis="y", labelsize=22, colors=WHITE, length=0)
fig.text(0.5, 0.92, "What Earth's crust is made of (by mass, approximate)", ha="center", fontsize=26, weight="bold")
fig.text(0.5, 0.03, "silicon is never found pure: it is locked up with oxygen in sand, quartz and rock", ha="center", fontsize=19, color=MUTED)
save(fig, OUT + "day03_crust.png")

# 2. The silicon atom: 14 electrons in shells 2, 8, 4
fig, ax = canvas(); ax.set_xlim(-5, 5); ax.set_ylim(-4.6, 4.4); ax.set_aspect("equal")
ax.add_patch(P.Circle((0, 0), 0.8, color=AMBER, zorder=3))
ax.text(0, 0, "14+", ha="center", va="center", fontsize=24, color=BG, weight="bold", zorder=4)
for r, n, col in ((1.5, 2, MUTED), (2.5, 8, MUTED), (3.5, 4, CYAN)):
    ax.add_patch(P.Circle((0, 0), r, fill=False, ec=col, lw=2.5 if col == CYAN else 1.5, ls="-" if col == CYAN else "--", zorder=1))
    for k in range(n):
        a = 2 * np.pi * k / n + np.pi / 4
        ax.add_patch(P.Circle((r * np.cos(a), r * np.sin(a)), 0.22 if col == CYAN else 0.17, color=col if col == CYAN else WHITE, zorder=2))
ax.annotate("4 outer (valence)\nelectrons", xy=(3.5 * np.cos(np.pi / 4) + 0.15, 3.5 * np.sin(np.pi / 4) + 0.15),
            xytext=(4.9, 3.9), ha="right", va="center", fontsize=19, color=CYAN, arrowprops=dict(arrowstyle="->", color=CYAN, lw=2))
ax.text(0, -4.3, "Silicon: 14 electrons  =  2 + 8 + 4", ha="center", fontsize=24, weight="bold")
save(fig, OUT + "day03_si_atom.png")

# 3. Each silicon atom bonds to four neighbours (flattened picture)
fig, ax = canvas(); ax.set_xlim(-3.4, 3.4); ax.set_ylim(-3.6, 3.1); ax.set_aspect("equal")
nb = [(0, 2.2), (2.2, 0), (0, -2.2), (-2.2, 0)]
for x, y in nb:
    ax.plot([0, x], [0, y], color=MUTED, lw=4, zorder=1)
    for s in (-1, 1):
        ox, oy = (0.1 * s, 0) if x == 0 else (0, 0.1 * s)
        ax.add_patch(P.Circle((x / 2 + ox, y / 2 + oy), 0.09, color=CYAN, zorder=3))
    ax.add_patch(P.Circle((x, y), 0.45, color=VIOLET, zorder=2))
    ax.text(x, y, "Si", ha="center", va="center", fontsize=19, color=BG, weight="bold", zorder=3)
ax.add_patch(P.Circle((0, 0), 0.55, color=AMBER, zorder=2))
ax.text(0, 0, "Si", ha="center", va="center", fontsize=22, color=BG, weight="bold", zorder=3)
ax.add_patch(P.FancyBboxPatch((0.75, -0.3), 0.6, 0.6, boxstyle="round,pad=0.05", fill=False, ec=AMBER, lw=3, zorder=5))
ax.annotate("one shared pair\n= one bond", xy=(1.4, 0.3), xytext=(2.9, 1.9), ha="center", fontsize=18, color=AMBER,
            arrowprops=dict(arrowstyle="->", color=AMBER, lw=2))
ax.text(0, -3.3, "4 bonds, 8 shared electrons: a stable, tidy crystal", ha="center", fontsize=21, weight="bold")
save(fig, OUT + "day03_four_bonds.png")

# 4. Bandgap 'Goldilocks' chart
fig = plt.figure(figsize=(14, 6.6), dpi=100); ax = fig.add_axes([0.08, 0.24, 0.88, 0.6])
names = ["Germanium", "Silicon", "Gallium\narsenide", "Silicon\ncarbide", "Gallium\nnitride"]
gaps = [0.66, 1.12, 1.42, 3.26, 3.4]
cols = [RED, CYAN, MUTED, MUTED, MUTED]
ax.bar(names, gaps, color=cols, width=0.6)
for i, g in enumerate(gaps):
    ax.text(i, g + 0.06, f"{g:g} eV", ha="center", va="bottom", fontsize=22, weight="bold", color=cols[i] if i < 2 else WHITE)
ax.set_ylim(0, 4); ax.set_yticks([])
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.tick_params(axis="x", labelsize=20, colors=WHITE, length=0)
fig.text(0.5, 0.92, "Bandgap at room temperature (electron-volts)", ha="center", fontsize=26, weight="bold")
fig.text(0.5, 0.03, "too small: leaks when warm  ·  silicon: just right for everyday logic  ·  wide: power and LEDs", ha="center", fontsize=19, color=MUTED)
save(fig, OUT + "day03_bandgaps.png")

# 5. Thermally freed electrons vs temperature: germanium vs silicon (n_i ~ T^1.5 exp(-Eg/2kT))
fig, ax = canvas(1000, 800, axis=True)
T = np.linspace(250, 450, 200); k = 8.617e-5
def ni(n300, eg): return n300 * (T / 300) ** 1.5 * np.exp(-eg / (2 * k) * (1 / T - 1 / 300))
ax.semilogy(T - 273, ni(2.0e13, 0.66), color=RED, lw=5)
ax.semilogy(T - 273, ni(1.0e10, 1.12), color=CYAN, lw=5)
ax.text(60, 4e14, "germanium", color=RED, fontsize=22, weight="bold")
ax.text(95, 3e10, "silicon", color=CYAN, fontsize=22, weight="bold")
ax.annotate("thousands of times more\nat room temperature", xy=(27, 1e11), xytext=(85, 1e9), fontsize=18, color=WHITE,
            arrowprops=dict(arrowstyle="->", color=WHITE, lw=2))
ax.plot([27, 27], [1e10, 2e13], color=WHITE, lw=2, ls=":")
ax.set_xlabel("Temperature (°C)", fontsize=22); ax.set_ylabel("Heat-freed electrons (log scale)", fontsize=20)
ax.set_yticks([]); ax.minorticks_off(); ax.tick_params(labelsize=18)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.set_position([0.12, 0.14, 0.84, 0.76])
fig.text(0.54, 0.95, "Leakage when warm (approximate)", ha="center", fontsize=26, weight="bold")
save(fig, OUT + "day03_leakage.png")

# 6. Native oxide: heat silicon in oxygen, glass grows on top
fig, ax = canvas(); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
for x0, title, ox in ((0.4, "Before", 0), (5.4, "After heating in oxygen", 1.4)):
    if not ox:
        ax.add_patch(P.Rectangle((x0, 1.5), 4.2, 4.5, color="#6d7f96"))
        ax.text(x0 + 2.1, 3.6, "silicon", ha="center", va="center", fontsize=22, color=BG, weight="bold")
    else:
        ax.add_patch(P.Rectangle((x0, 6.0 - 0.6), 4.2, ox, color=GREEN, alpha=.9))
        ax.text(x0 + 2.1, 6.1, "silicon dioxide\n(glass, insulator)", ha="center", va="center", fontsize=17, color=BG, weight="bold")
        ax.add_patch(P.Rectangle((x0, 1.5), 4.2, 3.9, color="#6d7f96"))
        ax.text(x0 + 2.1, 3.4, "silicon", ha="center", va="center", fontsize=22, color=BG, weight="bold")
    ax.text(x0 + 2.1, 0.8, title, ha="center", fontsize=19, color=MUTED)
for i in range(4):
    ax.annotate("", xy=(6.0 + i * 1.0, 7.0), xytext=(6.0 + i * 1.0, 8.3), arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=2.5))
ax.text(7.5, 8.6, "O₂ + heat", ha="center", fontsize=20, color=AMBER, weight="bold")
ax.annotate("", xy=(5.2, 3.7), xytext=(4.8, 3.7), arrowprops=dict(arrowstyle="-|>", color=WHITE, lw=3))
ax.text(5, 9.6, "Silicon grows its own insulator", ha="center", fontsize=26, weight="bold")
save(fig, OUT + "day03_native_oxide.png")

# 7. Timeline: germanium to silicon
fig = plt.figure(figsize=(16, 6), dpi=100); ax = fig.add_axes([0.02, 0.05, 0.96, 0.85])
ax.set_xlim(0, 16); ax.set_ylim(0, 6); ax.set_axis_off()
ax.plot([0.8, 15.2], [3, 3], color=MUTED, lw=4)
ev = [(1.8, "1947", "First transistor\n(germanium)", RED), (5.6, "1954", "First silicon\ntransistors", CYAN),
      (9.4, "1959", "Silicon oxide\nplanar process, IC", GREEN), (13.2, "Today", "Billions of silicon\ntransistors per chip", AMBER)]
for i, (x, yr, txt, c) in enumerate(ev):
    ax.add_patch(P.Circle((x, 3), 0.28, color=c, zorder=3))
    ax.text(x, 3.75, yr, ha="center", va="bottom", fontsize=28, weight="bold", color=c)
    ax.text(x, 2.25, txt, ha="center", va="top", fontsize=20, color=WHITE)
save(fig, OUT + "day03_timeline.png")
print("figs ok")
