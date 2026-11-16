"""Diagrams for Day 4: Energy bands and the bandgap. Run from the repo root."""
import sys; sys.path.insert(0, "tools")
from figkit import *
import numpy as np
from matplotlib.colors import hsv_to_rgb

OUT = "out/figs/"
SI_GREY = "#6d7f96"


def wide(w=14, h=6.6):
    fig = plt.figure(figsize=(w, h), dpi=100)
    ax = fig.add_axes([0.02, 0.03, 0.96, 0.94]); ax.set_axis_off()
    return fig, ax


# 1. One atom: a ladder of allowed energies (and a staircase analogy)
fig, ax = wide(); ax.set_xlim(0, 14); ax.set_ylim(0, 6.6)
ax.annotate("", xy=(0.6, 6.0), xytext=(0.6, 0.5), arrowprops=dict(arrowstyle="->", color=MUTED, lw=2))
ax.text(0.3, 3.2, "Energy", rotation=90, va="center", ha="center", color=MUTED, fontsize=20)
levels = [(1.0, 2), (2.7, 4), (3.9, 2), (4.6, 0), (5.05, 0)]
for k, (y, ne) in enumerate(levels):
    ax.plot([1.4, 5.8], [y, y], color=CYAN if k < 3 else MUTED, lw=4 if k < 3 else 2.5)
    for e in range(ne):
        ax.add_patch(P.Circle((2.3 + e * 0.75, y + 0.2), 0.14, color=AMBER, zorder=3))
ax.text(6.1, 1.0, "allowed", va="center", fontsize=19, color=CYAN)
ax.text(6.1, 1.85, "forbidden", va="center", fontsize=19, color=RED, style="italic")
ax.add_patch(P.Rectangle((1.4, 1.15), 4.4, 1.4, color=RED, alpha=.10))
ax.text(3.6, 6.15, "One atom (simplified)", ha="center", fontsize=25, weight="bold")
ax.text(3.6, 0.25, "electrons (orange) sit only on the lines", ha="center", fontsize=17, color=MUTED)
anchor("levels", ax, 4.6, 2.7); anchor("forbidden", ax, 3.6, 1.85); anchor("electrons", ax, 2.3, 1.2)
# staircase analogy
ax.plot([8.0, 13.6], [0.8, 0.8], color=MUTED, lw=2)
sx, sy = 8.2, 0.8
for i in range(5):
    ax.add_patch(P.Rectangle((sx + i * 1.05, 0.8), 1.05, (i + 1) * 0.95, color="#1b2b44", ec=MUTED, lw=1.5))
ax.add_patch(P.Circle((sx + 2 * 1.05 + 0.52, 0.8 + 3 * 0.95 + 0.28), 0.26, color=AMBER, zorder=3))
ax.annotate("you can stand on a step,\nnot halfway between", xy=(sx + 2.6, 0.8 + 3 * 0.95 + 0.5), xytext=(10.2, 5.95),
            ha="center", fontsize=18, color=WHITE, arrowprops=dict(arrowstyle="->", color=WHITE, lw=2))
ax.text(10.8, 0.25, "like a staircase", ha="center", fontsize=17, color=MUTED)
anchor("stairs", ax, sx + 2 * 1.05 + 0.52, 0.8 + 3 * 0.95 + 0.28)
save(fig, OUT + "day04_atom_ladder.png")

# 2. Bring atoms together: levels spread into bands
fig, ax = canvas(1000, 960); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
x = np.linspace(2.0, 9.4, 300)
spread = 1.55 * np.exp(-(x - 2.0) / 1.9)
for E0, col, s in ((7.0, CYAN, 1.0), (3.3, AMBER, 0.9)):
    for c in np.linspace(-1, 1, 9):
        ax.plot(x, E0 + s * spread * c, color=col, lw=1.6, alpha=.9)
xs = 3.0; sp = 1.55 * np.exp(-(xs - 2.0) / 1.9)
ax.add_patch(P.Rectangle((2.0, 7.0 - sp), xs - 2.0, 2 * sp, color=CYAN, alpha=.35))
ax.add_patch(P.Rectangle((2.0, 3.3 - 0.9 * sp), xs - 2.0, 1.8 * sp, color=AMBER, alpha=.35))
ax.plot([xs, xs], [0.9, 9.4], color=WHITE, lw=2, ls="--")
ax.text(xs, 9.6, "crystal\nspacing", ha="center", fontsize=17, color=WHITE)
ax.annotate("", xy=(2.45, 7.0 - sp), xytext=(2.45, 3.3 + 0.9 * sp), arrowprops=dict(arrowstyle="<->", color=WHITE, lw=2.5))
ax.text(1.0, 5.15, "gap", fontsize=20, color=WHITE, weight="bold", ha="center")
ax.text(9.5, 7.3, "one level", ha="right", fontsize=17, color=CYAN)
ax.text(9.5, 3.6, "one level", ha="right", fontsize=17, color=AMBER)
ax.text(5.6, 8.85, "band", fontsize=20, color=CYAN, weight="bold")
ax.text(5.6, 1.45, "band", fontsize=20, color=AMBER, weight="bold")
ax.annotate("", xy=(2.2, 0.55), xytext=(9.4, 0.55), arrowprops=dict(arrowstyle="->", color=MUTED, lw=2))
ax.text(5.8, 0.05, "atoms closer together  ←      → far apart", ha="center", fontsize=17, color=MUTED)
ax.text(0.5, 9.0, "Energy", fontsize=18, color=MUTED, rotation=90, va="top")
anchor("far", ax, 8.9, 7.0); anchor("fan", ax, 4.6, 7.0 + 1.55 * np.exp(-(4.6 - 2) / 1.9) * 0.6)
anchor("band", ax, 2.5, 7.0); anchor("gap", ax, 2.45, 5.15)
save(fig, OUT + "day04_levels_to_bands.png")

# 3. Silicon's two bands
fig, ax = wide(); ax.set_xlim(0, 14); ax.set_ylim(0, 6.6)
ax.add_patch(P.FancyBboxPatch((1.6, 4.0), 9.6, 1.9, boxstyle="round,pad=0.05", fc=CYAN, alpha=.18, ec=CYAN, lw=3))
ax.add_patch(P.FancyBboxPatch((1.6, 0.4), 9.6, 1.9, boxstyle="round,pad=0.05", fc=AMBER, alpha=.85, ec=AMBER, lw=3))
rng = np.random.default_rng(4)
for i in range(22):
    for j in range(3):
        ax.add_patch(P.Circle((1.95 + i * 0.43, 0.75 + j * 0.55), 0.13, color=BG, zorder=3))
ax.text(6.4, 5.55, "Conduction band: empty (at absolute zero)", ha="center", fontsize=21, color=CYAN, weight="bold")
ax.text(6.4, 4.45, "free seats: an electron here can move", ha="center", fontsize=17, color=WHITE)
ax.text(6.4, 2.65, "Valence band: full of bonding electrons", ha="center", fontsize=21, color=AMBER, weight="bold")
ax.annotate("", xy=(12.0, 4.0), xytext=(12.0, 2.3), arrowprops=dict(arrowstyle="<->", color=WHITE, lw=3))
ax.text(12.3, 3.45, "bandgap", fontsize=22, color=WHITE, weight="bold", va="center")
ax.text(12.3, 2.85, "1.12 eV", fontsize=24, color=AMBER, weight="bold", va="center")
ax.text(6.4, 3.25, "no allowed energies here", ha="center", fontsize=18, color=RED, style="italic")
ax.annotate("", xy=(0.7, 6.3), xytext=(0.7, 0.3), arrowprops=dict(arrowstyle="->", color=MUTED, lw=2))
ax.text(0.35, 3.3, "Energy", rotation=90, va="center", ha="center", color=MUTED, fontsize=20)
anchor("valence", ax, 3.0, 1.3); anchor("conduction", ax, 3.0, 4.9); anchor("gap", ax, 12.0, 3.15)
anchor("forbidden", ax, 6.4, 3.15)
save(fig, OUT + "day04_si_bands.png")

# 4. Jumping the gap: electron up, hole left behind
fig, ax = canvas(1000, 960); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.add_patch(P.FancyBboxPatch((1.2, 6.4), 7.6, 2.6, boxstyle="round,pad=0.05", fc=CYAN, alpha=.18, ec=CYAN, lw=3))
ax.add_patch(P.FancyBboxPatch((1.2, 1.0), 7.6, 2.6, boxstyle="round,pad=0.05", fc=AMBER, alpha=.85, ec=AMBER, lw=3))
for i in range(11):
    for j in range(3):
        if (i, j) == (6, 2): continue
        ax.add_patch(P.Circle((1.6 + i * 0.68, 1.45 + j * 0.8), 0.17, color=BG, zorder=3))
hx, hy = 1.6 + 6 * 0.68, 1.45 + 2 * 0.8
ax.add_patch(P.Circle((hx, hy), 0.2, fill=False, ec=WHITE, lw=3, zorder=4))
ex, ey = hx, 7.0
ax.add_patch(P.Circle((ex, ey), 0.22, color=AMBER, zorder=4))
ax.annotate("", xy=(ex, ey - 0.35), xytext=(hx, hy + 0.35), arrowprops=dict(arrowstyle="-|>", color=WHITE, lw=3.5, mutation_scale=28))
ax.text(ex - 0.4, 5.0, "energy ≥ gap\n(heat or light)", ha="right", va="center", fontsize=19, color=WHITE)
ax.text(ex + 0.45, ey, "free electron", va="center", fontsize=19, color=AMBER, weight="bold")
ax.text(hx + 0.4, hy - 1.75, "hole left behind", ha="center", fontsize=19, color=WHITE, weight="bold",
        bbox=dict(fc=BG, ec="none", pad=4))
ax.text(5.0, 8.4, "Conduction band", ha="center", fontsize=20, color=CYAN, weight="bold")
ax.text(5.0, 0.35, "Valence band", ha="center", fontsize=20, color=AMBER, weight="bold")
anchor("energy", ax, ex, 5.0); anchor("electron", ax, ex, ey); anchor("hole", ax, hx, hy)
save(fig, OUT + "day04_jump.png")

# 5. Metal, semiconductor, insulator side by side
fig, ax = canvas(1000, 960); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
cols = [(0.3, "Metal", None), (3.6, "Semi-\nconductor", 1.1), (6.9, "Insulator", 4.6)]
for x0, name, gap in cols:
    w = 2.8
    if gap is None:
        ax.add_patch(P.FancyBboxPatch((x0, 1.2), w, 4.6, boxstyle="round,pad=0.04", color=AMBER, alpha=.85))
        ax.add_patch(P.FancyBboxPatch((x0, 4.6), w, 3.6, boxstyle="round,pad=0.04", fc=CYAN, alpha=.25, ec=CYAN, lw=2))
        ax.text(x0 + w / 2, 5.2, "overlap", ha="center", fontsize=17, color=BG, weight="bold")
        lab = "no gap"
    else:
        vtop = 3.9 if gap < 2 else 2.7
        ax.add_patch(P.FancyBboxPatch((x0, 1.2), w, vtop - 1.2, boxstyle="round,pad=0.04", color=AMBER, alpha=.85))
        ax.add_patch(P.FancyBboxPatch((x0, vtop + gap), w, 8.2 - vtop - gap, boxstyle="round,pad=0.04", fc=CYAN, alpha=.25, ec=CYAN, lw=2))
        ax.annotate("", xy=(x0 + w / 2, vtop + gap), xytext=(x0 + w / 2, vtop), arrowprops=dict(arrowstyle="<->", color=WHITE, lw=2.5))
        lab = "small gap\n~1 eV" if gap < 2 else "big gap\n~9 eV (glass)"
        ax.text(x0 + w / 2 + 0.15, vtop + gap / 2, "", fontsize=1)
    ax.text(x0 + w / 2, 9.55, name, ha="center", va="top", fontsize=21, weight="bold")
    ax.text(x0 + w / 2, 0.85, lab, ha="center", va="top", fontsize=17, color=MUTED)
anchor("metal", ax, 1.7, 5.0); anchor("semi", ax, 5.0, 4.45); anchor("insulator", ax, 8.3, 5.0)
save(fig, OUT + "day04_three_materials.png")

# 6. Heat alone: thermal energy vs silicon's gap
fig = plt.figure(figsize=(14, 6.6), dpi=100); ax = fig.add_axes([0.24, 0.30, 0.72, 0.5])
names = ["Typical heat energy\nat room temperature", "Silicon's bandgap"]
vals = [0.026, 1.12]
ax.barh(names[::-1], vals[::-1], color=[CYAN, RED][::-1], height=0.55)
ax.text(0.07, 1, "≈ 0.026 eV", va="center", fontsize=24, weight="bold", color=RED)
ax.text(1.14, 0, "", fontsize=1)
ax.text(1.08, 0, "1.12 eV", va="center", ha="right", fontsize=24, weight="bold", color=BG)
ax.set_xlim(0, 1.25); ax.set_xticks([])
for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
ax.tick_params(axis="y", labelsize=20, colors=WHITE, length=0)
fig.text(0.55, 0.9, "The gap is about 40 times the typical heat energy", ha="center", fontsize=26, weight="bold")
fig.text(0.55, 0.1, "only a rare lucky electron jumps: roughly 1 for every few trillion silicon atoms",
         ha="center", fontsize=20, color=AMBER)
def fanchor(name, fx, fy):  # figure-fraction anchor (top-left origin)
    anchor(name, ax, *ax.transData.inverted().transform(fig.transFigure.transform((fx, fy))))
anchor("heat", ax, 0.026, 1); anchor("gap", ax, 0.85, 0)
fanchor("note", 0.55, 0.13)
save(fig, OUT + "day04_heat.png")

# 7. Light and silicon: absorbed below ~1100 nm, transparent beyond
fig = plt.figure(figsize=(14, 6.6), dpi=100); ax = fig.add_axes([0.05, 0.3, 0.9, 0.42])
lam = np.linspace(300, 1500, 600)
for l0, l1 in zip(lam[:-1], lam[1:]):
    if 400 <= l0 <= 700:
        h = 0.75 * (700 - l0) / 300
        c = hsv_to_rgb((h, 0.85, 0.95))
    elif l0 < 400:
        c = "#5b3fa0"
    else:
        c = "#5a2330"
    ax.axvspan(l0, l1, color=c, lw=0)
ax.axvline(1107, color=WHITE, lw=4)
ax.set_xlim(300, 1500); ax.set_ylim(0, 1); ax.set_yticks([])
ax.set_xticks([400, 700, 1100, 1400]); ax.set_xticklabels(["400 nm", "700 nm", "~1,100 nm", "1,400 nm"], fontsize=19)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.text(550, 0.5, "visible", ha="center", va="center", fontsize=24, weight="bold", color=BG)
ax.text(900, 0.5, "near\ninfrared", ha="center", va="center", fontsize=20, color=WHITE)
fig.text(0.37, 0.86, "absorbed by silicon: photon energy > 1.12 eV", ha="center", fontsize=22, color=AMBER, weight="bold")
fig.text(0.83, 0.86, "passes through", ha="center", fontsize=22, color=CYAN, weight="bold")
ax.annotate("", xy=(310, 1.18), xytext=(1100, 1.18), xycoords="data", annotation_clip=False,
            arrowprops=dict(arrowstyle="<->", color=AMBER, lw=2.5))
ax.annotate("", xy=(1115, 1.18), xytext=(1495, 1.18), annotation_clip=False, arrowprops=dict(arrowstyle="<->", color=CYAN, lw=2.5))
fig.text(0.5, 0.06, "Wavelength of light  (shorter wavelength = more energy per photon)", ha="center", fontsize=20, color=MUTED)
anchor("visible", ax, 550, 0.25); anchor("cutoff", ax, 1107, 0.5); anchor("ir", ax, 1300, 0.5)
save(fig, OUT + "day04_light.png")

# 8. The gap sets the colour: bandgap scale with the visible window
fig = plt.figure(figsize=(14, 6.6), dpi=100); ax = fig.add_axes([0.05, 0.2, 0.9, 0.18])
E = np.linspace(0.4, 3.7, 600)
for e0, e1 in zip(E[:-1], E[1:]):
    l = 1240 / e0
    if 400 <= l <= 700:
        c = hsv_to_rgb((0.75 * (700 - l) / 300, 0.85, 0.95)); a = 1
    else:
        c = "#1b2b44"; a = 1
    ax.axvspan(e0, e1, color=c, alpha=a, lw=0)
ax.set_xlim(0.4, 3.7); ax.set_ylim(0, 1); ax.set_yticks([])
ax.set_xticks([0.5, 1, 1.5, 2, 2.5, 3, 3.5]); ax.tick_params(labelsize=18)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.set_xlabel("Bandgap (electron-volts)", fontsize=20, color=MUTED)
mats = [(0.66, "Germanium", RED, 1), (1.12, "Silicon", CYAN, 2), (1.42, "Gallium\narsenide", WHITE, 1),
        (1.9, "Red LED\n(AlGaInP)", "#ff5a4a", 2), (2.7, "Blue LED\n(InGaN)", "#5a8cff", 1), (3.4, "Gallium\nnitride", VIOLET, 2)]
for e, n, c, row in mats:
    ytxt = 1.5 if row == 1 else 2.9
    ax.plot([e, e], [0, ytxt - 0.15], color=c, lw=3, clip_on=False)
    ax.add_patch(P.Circle((e, 1.0), 0.0, color=c))
    ax.text(e, ytxt, n, ha="center", va="bottom", fontsize=18, color=c, weight="bold", clip_on=False)
fig.text(0.5, 0.92, "Bandgap sets the colour of light a material can give out", ha="center", fontsize=25, weight="bold")
fig.text(0.5, 0.025, "visible light window: about 1.7 to 3.1 eV  ·  silicon's gap is in the infrared", ha="center", fontsize=19, color=MUTED)
anchor("si", ax, 1.12, 0.5); anchor("red", ax, 1.9, 0.5); anchor("blue", ax, 2.7, 0.5); anchor("window", ax, 2.4, 0.15)
save(fig, OUT + "day04_led_colours.png")
print("figs ok")
