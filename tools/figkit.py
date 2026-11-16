"""figkit: on-brand diagram helpers for Atoms to Chips (matplotlib).

Every figure is a PNG with a transparent-looking dark background that matches the slides.
Use in lessons/dayNN_figs.py:

    import sys; sys.path.insert(0, "tools")
    from figkit import *
    fig, ax = canvas()            # 1000x800 px by default
    ... draw with matplotlib ...
    save(fig, "out/figs/dayNN_bands.png")

Pointer anchors: call anchor("gap", ax, x, y) before save(); the video pointer can then
glide to that spot when a beat says {"point": "gap"}.

Helpers:
    band_diagram(kind)            # "metal" | "semiconductor" | "insulator"
    lattice(dopant=None)          # silicon lattice, dopant "P" (n-type) or "B" (p-type)
    flow(steps)                   # left-to-right process flow boxes
    bars(labels, values, unit)    # simple bar chart
    layers(stack)                 # cross-section stack [(name, thickness, color), ...]
    wafer(diameter_mm, dies=True) # top view of a wafer with die grid
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import matplotlib.patches as P
import numpy as np, os

BG = "#080e1a"; GRID = "#101c2e"; CYAN = "#38cde6"; AMBER = "#ffb03b"; WHITE = "#eef4fa"
MUTED = "#8ca0b9"; RED = "#ff6b6b"; GREEN = "#2ec4a0"; VIOLET = "#a78bfa"
PALETTE = [CYAN, AMBER, GREEN, VIOLET, RED]

for f in font_manager.findSystemFonts("/usr/share/fonts/opentype/inter"):
    font_manager.fontManager.addfont(f)
plt.rcParams.update({
    "font.family": "Inter", "font.size": 20, "text.color": WHITE, "axes.labelcolor": WHITE,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": MUTED,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
})


def canvas(w=1000, h=800, axis=False):
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
    ax = fig.add_axes([0.04, 0.05, 0.92, 0.9])
    if not axis:
        ax.set_axis_off()
    return fig, ax


_ANCHORS = {}


def anchor(name, ax, x, y, fig=None):
    """Register a named point (in the axes' data coordinates) that the narration can point at.
    In a lesson beat: {"say": "...", "point": "<name>", "label": "optional callout"}."""
    fig = fig or ax.figure
    _ANCHORS.setdefault(id(fig), {})[name] = (ax, x, y)


def _write_anchors(fig, path, pop):
    pts = (_ANCHORS.pop if pop else _ANCHORS.get)(id(fig), {})
    if pts:
        import json
        W, H = fig.get_size_inches() * fig.dpi
        out = {}
        for name, (ax, x, y) in pts.items():
            px, py = ax.transData.transform((x, y))
            out[name] = [round(px / W, 4), round(1 - py / H, 4)]
        json.dump(out, open(os.path.splitext(path)[0] + ".anchors.json", "w"), indent=1)


def save_step(fig, path):
    """Save the figure as it looks right now (one build step) and keep drawing on it.
    Typical use: draw part 1 -> save_step(fig, ".../x_0.png"); draw part 2 -> save_step(..._1.png);
    ...; the slide uses "figure": [".../x_0.png", ".../x_1.png", ...] and beats switch with "step": k."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, dpi=100, transparent=True)
    _write_anchors(fig, path, pop=False)
    return path


def save(fig, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, dpi=100, transparent=True)
    _write_anchors(fig, path, pop=True)
    plt.close(fig)
    return path


def band_diagram(kind="semiconductor"):
    fig, ax = canvas(); ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    gaps = {"metal": (5.2, 4.8), "semiconductor": (6.2, 4.6), "insulator": (8.4, 3.2)}
    cb, vb = gaps[kind]
    if kind == "metal":
        ax.add_patch(P.FancyBboxPatch((2, 1), 6, 4.2, boxstyle="round,pad=0.05", color=AMBER, alpha=.85))
        ax.add_patch(P.FancyBboxPatch((2, 4.8), 6, 4, boxstyle="round,pad=0.05", color=CYAN, alpha=.85))
        ax.text(5, 4.95, "bands overlap", ha="center", va="center", fontsize=22, color=BG, weight="bold")
    else:
        ax.add_patch(P.FancyBboxPatch((2, cb), 6, 9.2 - cb, boxstyle="round,pad=0.05", color=CYAN, alpha=.85))
        ax.add_patch(P.FancyBboxPatch((2, 0.8), 6, vb - 0.8, boxstyle="round,pad=0.05", color=AMBER, alpha=.85))
        ax.annotate("", xy=(8.6, cb), xytext=(8.6, vb), arrowprops=dict(arrowstyle="<->", color=WHITE, lw=2.5))
        ax.text(8.8, (cb + vb) / 2, "band\ngap", va="center", fontsize=22, color=WHITE)
    ax.text(5, 8.2 if kind != "insulator" else 9.0, "Conduction band", ha="center", fontsize=22, color=BG, weight="bold")
    ax.text(5, 1.6, "Valence band", ha="center", fontsize=22, color=BG, weight="bold")
    ax.text(5, 9.75, kind.capitalize(), ha="center", fontsize=30, weight="bold")
    ax.annotate("", xy=(0.9, 9.3), xytext=(0.9, 0.8), arrowprops=dict(arrowstyle="->", color=MUTED, lw=2))
    ax.text(0.5, 5, "Energy", rotation=90, va="center", ha="center", color=MUTED)
    return fig, ax


def lattice(dopant=None, n=5):
    fig, ax = canvas(); ax.set_xlim(-0.8, n - 0.2); ax.set_ylim(-0.8, n - 0.2); ax.set_aspect("equal")
    c = n // 2
    for i in range(n):
        for j in range(n):
            if i < n - 1: ax.plot([i, i + 1], [j, j], color=MUTED, lw=3, zorder=1)
            if j < n - 1: ax.plot([i, i], [j, j + 1], color=MUTED, lw=3, zorder=1)
    for i in range(n):
        for j in range(n):
            special = dopant and (i, j) == (c, c)
            col = (GREEN if dopant == "P" else VIOLET) if special else CYAN
            ax.add_patch(P.Circle((i, j), 0.28, color=col, zorder=2))
            ax.text(i, j, dopant if special else "Si", ha="center", va="center", fontsize=17, color=BG, weight="bold", zorder=3)
    if dopant == "P":
        ax.add_patch(P.Circle((c + 0.5, c + 0.5), 0.11, color=AMBER, zorder=4))
        ax.annotate("extra electron", xy=(c + 0.5, c + 0.5), xytext=(n - 0.6, n - 0.35), fontsize=18, color=AMBER, zorder=5,
                    ha="right", arrowprops=dict(arrowstyle="->", color=AMBER, lw=2), bbox=dict(fc=BG, ec="none"))
    if dopant == "B":
        ax.add_patch(P.Circle((c + 0.5, c), 0.11, fill=False, ec=AMBER, lw=3, zorder=4))
        ax.text(c + 0.55, c + 0.22, "hole", fontsize=18, color=AMBER, zorder=4)
    return fig, ax


def flow(steps, colors=None):
    k = len(steps); fig, ax = canvas(1600, 500); ax.set_xlim(0, k * 3); ax.set_ylim(0, 3)
    for i, s in enumerate(steps):
        col = (colors or PALETTE)[i % len(colors or PALETTE)]
        ax.add_patch(P.FancyBboxPatch((i * 3 + 0.2, 0.9), 2.3, 1.3, boxstyle="round,pad=0.08", color=col))
        ax.text(i * 3 + 1.35, 1.55, s, ha="center", va="center", fontsize=20, color=BG, weight="bold", wrap=True)
        if i < k - 1:
            ax.annotate("", xy=(i * 3 + 3.15, 1.55), xytext=(i * 3 + 2.6, 1.55), arrowprops=dict(arrowstyle="-|>", color=WHITE, lw=2.5))
    return fig, ax


def bars(labels, values, unit="", colors=None):
    fig, ax = canvas(1000, 800, axis=True)
    ax.bar(labels, values, color=colors or PALETTE[: len(values)], width=0.6)
    for i, v in enumerate(values):
        ax.text(i, v, f"{v:g}{unit}", ha="center", va="bottom", fontsize=22, weight="bold")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    return fig, ax


def layers(stack):
    fig, ax = canvas(); tot = sum(t for _, t, _ in stack); y = 0
    ax.set_xlim(0, 10); ax.set_ylim(0, tot * 1.05)
    for name, t, col in stack:
        ax.add_patch(P.Rectangle((1, y), 6, t, color=col, ec=BG, lw=2))
        ax.text(7.3, y + t / 2, name, va="center", fontsize=22)
        y += t
    return fig, ax


def wafer(diameter_mm=300, dies=True):
    fig, ax = canvas(); ax.set_aspect("equal"); r = 1; ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15)
    ax.add_patch(P.Circle((0, 0), r, color="#9fb3c8"))
    if dies:
        s = 0.12
        for x in np.arange(-r, r, s):
            for y in np.arange(-r, r, s):
                if (x + s) ** 2 + (y + s) ** 2 < r ** 2 and x ** 2 + y ** 2 < r ** 2 and (x + s) ** 2 + y ** 2 < r ** 2 and x ** 2 + (y + s) ** 2 < r ** 2:
                    ax.add_patch(P.Rectangle((x + 0.008, y + 0.008), s - 0.016, s - 0.016, color=CYAN, alpha=.75))
    ax.add_patch(P.Wedge((0, -r), 0.04, 0, 180, color=BG))  # notch
    ax.text(0, -1.12, f"{diameter_mm} mm wafer", ha="center", fontsize=24, weight="bold")
    return fig, ax
