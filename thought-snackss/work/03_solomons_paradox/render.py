import cairo, math, json, random, re, subprocess, sys, os

W, H, FPS = 1080, 1920, 30
PAD = 0.45          # silence after each line
LEAD = 0.15         # silence before each line
SCRIPT = json.load(open("script.json"))
DURS = json.load(open("durs.json"))
ORDER = [s["id"] for s in SCRIPT]
TEXT = {s["id"]: s["text"] for s in SCRIPT}
SCENE_LEN = {k: LEAD + DURS[k] + PAD for k in ORDER}
SCENE_START = {}
acc = 0
for k in ORDER:
    SCENE_START[k] = acc
    acc += SCENE_LEN[k]

FONT = "Poppins"
YEL = (1.0, 0.85, 0.2)
WHITE = (1, 1, 1)
PINK = (1.0, 0.45, 0.6)
TEAL = (0.2, 0.85, 0.8)
ORANGE = (1.0, 0.5, 0.35)
GREEN = (0.35, 0.87, 0.5)
BLUE = (0.38, 0.65, 0.98)
PURPLE = (0.66, 0.45, 0.98)

# ---------- word timing (estimated, proportional) ----------
def word_times(sid):
    words = TEXT[sid].split()
    weights = []
    for w in words:
        c = len(re.sub(r"[^A-Za-z0-9]", "", w)) + 2.0
        p = 0
        if w.endswith("..."): p = 7
        elif w[-1] in ".?!": p = 5
        elif w[-1] in ",": p = 2.5
        weights.append((c, p))
    tot = sum(c + p for c, p in weights)
    dur = DURS[sid] - 0.25
    t = LEAD + 0.1
    out = []
    for w, (c, p) in zip(words, weights):
        d = dur * c / tot
        out.append((w, t, t + d))
        t += d + dur * p / tot
    return out

WT = {k: word_times(k) for k in ORDER}

def kw(sid, word, nth=0):
    n = 0
    for w, a, b in WT[sid]:
        if re.sub(r"[^a-z]", "", w.lower()).startswith(word.lower()):
            if n == nth:
                return a
            n += 1
    raise KeyError(word)

# ---------- helpers ----------
def clamp(x, a=0, b=1): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def eo(t): t = clamp(t); return 1 - (1 - t) ** 3
def eio(t): t = clamp(t); return 3 * t * t - 2 * t * t * t
def eback(t):
    t = clamp(t); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def prog(t, a, d): return clamp((t - a) / d)

def font(ctx, size, bold=True):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def text(ctx, s, x, y, size, color=WHITE, alpha=1, scale=1, rot=0, stroke=10, bold=True, maxw=980):
    if alpha <= 0 or scale <= 0: return
    font(ctx, size, bold)
    ext = ctx.text_extents(s)
    k = min(1, maxw / max(1, ext.x_advance))
    ctx.save()
    ctx.translate(x, y); ctx.rotate(rot); ctx.scale(scale * k, scale * k)
    ctx.move_to(-ext.x_advance / 2, size * 0.35)
    ctx.text_path(s)
    if stroke:
        ctx.set_source_rgba(0.04, 0.03, 0.12, alpha)
        ctx.set_line_width(stroke); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
    ctx.set_source_rgba(*color, alpha); ctx.fill()
    ctx.restore()

def pop_text(ctx, s, x, y, size, t, start, color=WHITE, end=None, rot=0, **kw_):
    if t < start: return
    a = 1
    if end is not None and t > end:
        a = 1 - prog(t, end, 0.25)
    text(ctx, s, x, y, size, color, alpha=a, scale=eback(prog(t, start, 0.35)), rot=rot, **kw_)

def circle(ctx, x, y, r, color, alpha=1):
    ctx.arc(x, y, max(0.1, r), 0, 2 * math.pi)
    ctx.set_source_rgba(*color, alpha); ctx.fill()

def blob_path(ctx, x, y, r, t, seed=0, amp=0.04, sx=1, sy=1):
    n = 64
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        rr = r * (1 + amp * math.sin(3 * a + t * 2.1 + seed) + amp * 0.6 * math.sin(5 * a - t * 1.7 + seed * 2))
        px, py = x + rr * math.cos(a) * sx, y + rr * math.sin(a) * sy
        (ctx.move_to if i == 0 else ctx.line_to)(px, py)
    ctx.close_path()

def face(ctx, x, y, s, t, mood="happy", look=(0, 0), blink_seed=0, shades=False):
    # eyes
    ex = 0.32 * s; ey = -0.08 * s; er = 0.17 * s
    blink = 1.0
    ph = (t + blink_seed) % 3.3
    if ph < 0.12: blink = 0.15
    for sgn in (-1, 1):
        cx, cy = x + sgn * ex, y + ey
        ctx.save(); ctx.translate(cx, cy); ctx.scale(1, blink)
        circle(ctx, 0, 0, er, WHITE)
        circle(ctx, look[0] * er * 0.35, look[1] * er * 0.35, er * 0.55, (0.08, 0.06, 0.15))
        circle(ctx, look[0] * er * 0.35 + er * 0.2, look[1] * er * 0.35 - er * 0.2, er * 0.18, WHITE)
        ctx.restore()
        if mood == "sad":
            ctx.set_source_rgb(0.08, 0.06, 0.15); ctx.set_line_width(0.05 * s)
            ctx.move_to(cx - sgn * er * 1.1, cy - er * 1.5); ctx.line_to(cx + sgn * er * 0.6, cy - er * 1.1); ctx.stroke()
    if shades:
        ctx.set_source_rgb(0.05, 0.05, 0.08)
        for sgn in (-1, 1):
            cx = x + sgn * ex
            ctx.rectangle(cx - er * 1.3, y + ey - er * 0.9, er * 2.6, er * 1.6); ctx.fill()
        ctx.set_line_width(0.05 * s); ctx.move_to(x - ex, y + ey - er * 0.4); ctx.line_to(x + ex, y + ey - er * 0.4); ctx.stroke()
    # mouth
    ctx.set_source_rgb(0.08, 0.06, 0.15)
    ctx.set_line_width(0.07 * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    my = y + 0.25 * s
    if mood == "happy":
        ctx.arc(x, my - 0.08 * s, 0.18 * s, 0.15 * math.pi, 0.85 * math.pi); ctx.stroke()
    elif mood == "wow":
        ctx.save(); ctx.translate(x, my); ctx.scale(1, 1.3); ctx.arc(0, 0, 0.09 * s, 0, 2 * math.pi); ctx.restore(); ctx.fill()
    elif mood == "sad":
        ctx.arc(x, my + 0.14 * s, 0.15 * s, 1.2 * math.pi, 1.8 * math.pi); ctx.stroke()
    # blush
    for sgn in (-1, 1):
        circle(ctx, x + sgn * 0.5 * s, y + 0.15 * s, 0.09 * s, (1, 0.5, 0.6), 0.45)

def mito(ctx, x, y, s, t, rot=0, mood="happy", look=(0, 0), alpha=1, faced=True):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    ctx.push_group()
    ctx.save(); ctx.scale(1, 0.55)
    ctx.arc(0, 0, s, 0, 2 * math.pi); ctx.restore()
    ctx.set_source_rgb(*ORANGE); ctx.fill()
    ctx.save(); ctx.scale(1, 0.55); ctx.arc(0, 0, s * 0.86, 0, 2 * math.pi); ctx.restore()
    ctx.set_source_rgb(1, 0.72, 0.6); ctx.fill()
    # cristae
    ctx.set_source_rgb(*ORANGE); ctx.set_line_width(s * 0.07); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    n = 6
    ctx.move_to(-s * 0.75, 0)
    for i in range(n):
        xx = -s * 0.75 + (i + 0.5) * s * 1.5 / n
        yy = (s * 0.36) * (1 if i % 2 == 0 else -1)
        ctx.line_to(xx, yy); ctx.line_to(xx + s * 0.75 / n, 0) if False else None
    ctx.line_to(s * 0.75, 0)
    ctx.stroke()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha)
    ctx.restore()
    if faced and alpha > 0.5:
        face(ctx, x, y + s * 0.02, s * 0.62, t, mood, look)

def bacterium(ctx, x, y, s, t, mood="happy", shades=False, flip=False, color=GREEN, tail=True):
    L, R = s * 1.1, s * 0.5
    ctx.save(); ctx.translate(x, y)
    if flip: ctx.scale(-1, 1)
    if tail:
        ctx.set_source_rgba(*color, 0.9); ctx.set_line_width(s * 0.08); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in (-1, 1):
            ctx.move_to(-L, k * R * 0.3)
            for i in range(1, 30):
                xx = -L - i * s * 0.05
                yy = k * R * 0.3 + math.sin(i * 0.5 - t * 14 + k) * s * 0.12 * (i / 30 + 0.3)
                ctx.line_to(xx, yy)
            ctx.stroke()
    ctx.new_path()
    ctx.arc(-L + R, 0, R, math.pi / 2, 3 * math.pi / 2)
    ctx.arc(L - R, 0, R, -math.pi / 2, math.pi / 2)
    ctx.close_path()
    ctx.set_source_rgb(*color); ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(s * 0.06); ctx.stroke()
    ctx.restore()
    face(ctx, x + (s * 0.15 if not flip else -s * 0.15), y, s * 0.55, t, mood, (1 if not flip else -1, 0), shades=shades)

def big_cell(ctx, x, y, r, t, color=BLUE, mood="happy", faced=True, nucleus=True, look=(0, 0), seed=0, alpha=1, sx=1, sy=1):
    blob_path(ctx, x, y, r, t, seed, sx=sx, sy=sy)
    ctx.set_source_rgba(*color, 0.25 * alpha); ctx.fill_preserve()
    ctx.set_source_rgba(*color, alpha); ctx.set_line_width(12); ctx.stroke()
    if nucleus:
        nx, ny = x - r * 0.35, y - r * 0.3
        blob_path(ctx, nx, ny, r * 0.26, t * 1.3, seed + 3)
        ctx.set_source_rgba(*PURPLE, 0.85 * alpha); ctx.fill()
        circle(ctx, nx + r * 0.05, ny - r * 0.04, r * 0.08, (0.85, 0.7, 1), 0.8 * alpha)
    if faced:
        face(ctx, x + r * 0.05, y - r * 0.62, r * 0.42, t, mood, look)

def bolt(ctx, x, y, s, rot=0, alpha=1, color=YEL):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s / 100, s / 100)
    pts = [(10, -60), (-30, 8), (0, 8), (-12, 60), (34, -14), (4, -14), (22, -60)]
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path()
    ctx.set_source_rgba(0.04, 0.03, 0.12, alpha); ctx.set_line_width(10); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    ctx.set_source_rgba(*color, alpha); ctx.fill()
    ctx.restore()

def house(ctx, x, y, s, alpha=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.move_to(-50, -5); ctx.line_to(0, -50); ctx.line_to(50, -5); ctx.close_path()
    ctx.set_source_rgba(1, 0.4, 0.4, alpha); ctx.fill()
    ctx.rectangle(-36, -8, 72, 56); ctx.set_source_rgba(1, 0.92, 0.75, alpha); ctx.fill()
    ctx.rectangle(-10, 14, 20, 34); ctx.set_source_rgba(0.55, 0.35, 0.2, alpha); ctx.fill()
    ctx.restore()

def apple(ctx, x, y, s, alpha=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    circle(ctx, -14, 6, 34, (0.95, 0.25, 0.3), alpha); circle(ctx, 14, 6, 34, (0.95, 0.25, 0.3), alpha)
    ctx.set_source_rgba(0.45, 0.3, 0.15, alpha); ctx.set_line_width(7); ctx.move_to(0, -24); ctx.line_to(4, -44); ctx.stroke()
    ctx.save(); ctx.translate(18, -38); ctx.rotate(-0.5); ctx.scale(1, 0.5); circle(ctx, 0, 0, 16, GREEN, alpha); ctx.restore()
    ctx.restore()

def dna(ctx, x, y, s, t, alpha=1, rot=0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    ctx.set_line_width(s * 0.12); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for ph, col in ((0, (0.4, 0.8, 1)), (math.pi, (1, 0.5, 0.8))):
        ctx.set_source_rgba(*col, alpha)
        for i in range(21):
            yy = -s + 2 * s * i / 20
            xx = math.sin(i / 20 * 2 * math.pi * 1.2 + ph + t * 3) * s * 0.35
            (ctx.move_to if i == 0 else ctx.line_to)(xx, yy)
        ctx.stroke()
    ctx.set_source_rgba(1, 1, 1, 0.6 * alpha); ctx.set_line_width(s * 0.06)
    for i in range(2, 20, 3):
        yy = -s + 2 * s * i / 20
        xx = math.sin(i / 20 * 2 * math.pi * 1.2 + t * 3) * s * 0.35
        ctx.move_to(xx, yy); ctx.line_to(-xx, yy); ctx.stroke()
    ctx.restore()

def heart(ctx, x, y, s, color=PINK, alpha=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.move_to(0, 35)
    ctx.curve_to(-60, -5, -45, -60, 0, -30)
    ctx.curve_to(45, -60, 60, -5, 0, 35)
    ctx.close_path()
    ctx.set_source_rgba(*color, alpha); ctx.fill()
    ctx.restore()

def tree(ctx, x, y, s, alpha=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.rectangle(-9, 0, 18, 50); ctx.set_source_rgba(0.55, 0.35, 0.2, alpha); ctx.fill()
    for dx, dy, r in ((0, -30, 34), (-26, -5, 26), (26, -5, 26)):
        circle(ctx, dx, dy, r, (0.2, 0.75, 0.4), alpha)
    ctx.restore()

def fish(ctx, x, y, s, t, alpha=1):
    ctx.save(); ctx.translate(x, y + math.sin(t * 4) * 6); ctx.scale(s / 100, s / 100)
    ctx.save(); ctx.scale(1, 0.6); ctx.arc(0, 0, 45, 0, 2 * math.pi); ctx.restore()
    ctx.set_source_rgba(0.3, 0.7, 1, alpha); ctx.fill()
    ctx.move_to(-38, 0); ctx.line_to(-70, -26); ctx.line_to(-70, 26); ctx.close_path(); ctx.fill()
    circle(ctx, 20, -6, 7, WHITE, alpha); circle(ctx, 22, -6, 3.5, (0, 0, 0), alpha)
    ctx.restore()

def human(ctx, x, y, s, alpha=1, color=YEL):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    circle(ctx, 0, -45, 20, color, alpha)
    ctx.set_source_rgba(*color, alpha); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(0, -22); ctx.line_to(0, 22); ctx.stroke()
    ctx.move_to(-28, -12); ctx.line_to(0, -6); ctx.line_to(28, -12); ctx.stroke()
    ctx.move_to(-18, 55); ctx.line_to(0, 22); ctx.line_to(18, 55); ctx.stroke()
    ctx.restore()

def pill(ctx, x, y, w, h, color, alpha=1):
    r = h / 2
    ctx.new_path()
    ctx.arc(x - w / 2 + r, y, r, math.pi / 2, 3 * math.pi / 2)
    ctx.arc(x + w / 2 - r, y, r, -math.pi / 2, math.pi / 2)
    ctx.close_path(); ctx.set_source_rgba(*color, alpha); ctx.fill()

# ---------- background ----------
random.seed(7)
PARTS = [(random.random() * W, random.random() * H, random.uniform(6, 26), random.uniform(0.2, 0.7), random.random() * 6) for _ in range(40)]

def background(ctx, T):
    g = cairo.LinearGradient(0, 0, W, H)
    g.add_color_stop_rgb(0, 0.06, 0.05, 0.17)
    g.add_color_stop_rgb(0.55, 0.11, 0.07, 0.27)
    g.add_color_stop_rgb(1, 0.04, 0.12, 0.22)
    ctx.set_source(g); ctx.paint()
    # soft glows
    for (gx, gy, gr, col) in ((W * 0.2, H * 0.25, 600, PURPLE), (W * 0.85, H * 0.7, 700, TEAL)):
        rg = cairo.RadialGradient(gx + math.sin(T * 0.3) * 60, gy, 0, gx, gy, gr)
        rg.add_color_stop_rgba(0, *col, 0.18); rg.add_color_stop_rgba(1, *col, 0)
        ctx.set_source(rg); ctx.paint()
    for (px, py, r, sp, ph) in PARTS:
        yy = (py - T * sp * 40) % (H + 60) - 30
        xx = px + math.sin(T * 0.8 + ph) * 20
        circle(ctx, xx, yy, r * 0.5, (0.8, 0.85, 1), 0.08)

# ---------- captions ----------
def chunks(sid):
    out, cur = [], []
    for w in WT[sid]:
        cur.append(w)
        if len(cur) >= 4 or w[0][-1] in ".,?!" :
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out

CH = {k: chunks(k) for k in ORDER}

def captions(ctx, sid, t):
    for ch in CH[sid]:
        a, b = ch[0][1], ch[-1][2]
        if a - 0.05 <= t < b + 0.35:
            # layout words
            font(ctx, 66)
            words = [w[0] for w in ch]
            sp = ctx.text_extents("a a").x_advance - ctx.text_extents("aa").x_advance
            widths = [ctx.text_extents(w).x_advance for w in words]
            total = sum(widths) + sp * (len(words) - 1)
            k = min(1, 980 / total)
            sc = eback(prog(t, a - 0.05, 0.22)) * k
            x = W / 2 - total * sc / 2
            y = 1630
            for (w, wa, wb), wd in zip(ch, widths):
                active = wa <= t < max(wb, wa + 0.12) + 0.08
                col = YEL if active else WHITE
                ctx.save(); ctx.translate(x + wd * sc / 2, y)
                s2 = sc
                ctx.scale(s2, s2)
                ctx.move_to(-wd / 2, 22); ctx.text_path(w)
                ctx.set_source_rgb(0.04, 0.03, 0.12); ctx.set_line_width(12); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
                ctx.set_source_rgb(*col); ctx.fill()
                ctx.restore()
                x += (wd + sp) * sc
            return

# ---------- scenes ----------
CX, CY = W / 2, 980
CREAM = (0.97, 0.93, 0.85)
DARK = (0.04, 0.03, 0.12)

def rrect(ctx, x, y, w, h, r):
    ctx.new_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); ctx.close_path()

def blobby(ctx, x, y, r, t, color, mood="happy", look=(0, 0), seed=0, alpha=1, glow=0, sleepy=False):
    if glow > 0:
        rg = cairo.RadialGradient(x, y, r * 0.5, x, y, r * 2)
        rg.add_color_stop_rgba(0, *YEL, 0.35 * glow); rg.add_color_stop_rgba(1, *YEL, 0)
        ctx.set_source(rg); ctx.arc(x, y, r * 2, 0, 2 * math.pi); ctx.fill()
    blob_path(ctx, x, y, r, t, seed, amp=0.05)
    ctx.set_source_rgba(*color, 0.92 * alpha); ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.35 * alpha); ctx.set_line_width(8); ctx.stroke()
    if sleepy:
        s = r * 0.75
        ctx.set_source_rgb(*DARK); ctx.set_line_width(0.06 * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for sg in (-1, 1):
            ctx.arc(x + sg * 0.32 * s, y - 0.08 * s, 0.13 * s, 0.1 * math.pi, 0.9 * math.pi); ctx.stroke()
        ctx.arc(x, y + 0.2 * s, 0.1 * s, 0, 2 * math.pi); ctx.stroke()
    else:
        face(ctx, x, y, r * 0.75, t, mood, look, blink_seed=seed)

def badge(ctx, t, num, title, sub=None, start=0.1, color=YEL):
    # number coin + title
    sc = eback(prog(t, start, 0.35))
    if sc > 0:
        ctx.save(); ctx.translate(CX, 300); ctx.scale(sc, sc)
        circle(ctx, 0, 0, 62, color); circle(ctx, 0, 0, 50, DARK, 0.25)
        ctx.restore()
        text(ctx, str(num), CX, 300, 70, DARK, scale=sc, stroke=0)
    pop_text(ctx, title, CX, 430, 92, t, start + 0.25, WHITE)
    if sub:
        pop_text(ctx, sub, CX, 525, 52, t, start + 0.6, color, stroke=8)

def cookie(ctx, x, y, r, col=(0.85, 0.6, 0.32), bite=True, alpha=1):
    ctx.push_group()
    circle(ctx, x, y, r, col)
    circle(ctx, x, y, r * 0.86, (0.92, 0.7, 0.4))
    random.seed(int(x) + int(y))
    for i in range(6):
        a = random.uniform(0, 2 * math.pi); d = random.uniform(0, r * 0.6)
        circle(ctx, x + math.cos(a) * d, y + math.sin(a) * d, r * 0.1, (0.35, 0.2, 0.12))
    if bite:
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        for dx, dy in ((0.8, -0.55), (0.98, -0.1), (0.55, -0.85)):
            circle(ctx, x + dx * r, y + dy * r, r * 0.28, (0, 0, 0))
        ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha)


# ---- shared bits for Solomon's paradox ----
def bubble(ctx, x, y, w, h, color, alpha=1, tail=-1):
    rrect(ctx, x - w / 2, y - h / 2, w, h, min(40, h / 2))
    ctx.set_source_rgba(*color, alpha); ctx.fill()
    ctx.move_to(x + tail * w * 0.25, y + h / 2 - 2); ctx.line_to(x + tail * w * 0.32, y + h / 2 + 40)
    ctx.line_to(x + tail * w * 0.1, y + h / 2 - 2); ctx.close_path(); ctx.fill()

def knot(ctx, x, y, s, t, alpha=1, color=(1, 0.45, 0.5)):
    # tangled scribble = a problem
    ctx.set_source_rgba(*color, alpha); ctx.set_line_width(9 * s / 100); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(90):
        a = i * 0.37 + t * 1.5
        r = s * (0.45 + 0.35 * math.sin(i * 1.7))
        px, py = x + math.cos(a) * r, y + math.sin(a * 1.3) * r * 0.8
        (ctx.move_to if i == 0 else ctx.line_to)(px, py)
    ctx.stroke()

def bulb(ctx, x, y, s, alpha=1, t=0):
    rg = cairo.RadialGradient(x, y, 5, x, y, s * 1.6)
    rg.add_color_stop_rgba(0, 1, 0.95, 0.5, 0.6 * alpha); rg.add_color_stop_rgba(1, 1, 0.9, 0.4, 0)
    ctx.set_source(rg); ctx.arc(x, y, s * 1.6, 0, 2 * math.pi); ctx.fill()
    circle(ctx, x, y, s * 0.6, YEL, alpha)
    ctx.rectangle(x - s * 0.25, y + s * 0.5, s * 0.5, s * 0.35); ctx.set_source_rgba(0.75, 0.75, 0.8, alpha); ctx.fill()
    ctx.set_source_rgba(*YEL, alpha); ctx.set_line_width(s * 0.08); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(7):
        a = -math.pi + k / 6 * math.pi
        r1 = s * (0.85 + 0.08 * math.sin(t * 6 + k))
        ctx.move_to(x + math.cos(a) * r1, y + math.sin(a) * r1); ctx.line_to(x + math.cos(a) * s * 1.15, y + math.sin(a) * s * 1.15); ctx.stroke()

def crown(ctx, x, y, s, alpha=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.move_to(-60, 30); ctx.line_to(-70, -40); ctx.line_to(-30, -5); ctx.line_to(0, -55); ctx.line_to(30, -5); ctx.line_to(70, -40); ctx.line_to(60, 30); ctx.close_path()
    ctx.set_source_rgba(0.04, 0.03, 0.12, alpha); ctx.set_line_width(10); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    ctx.set_source_rgba(*YEL, alpha); ctx.fill()
    for dx in (-35, 0, 35): circle(ctx, dx, 12, 8, PINK, alpha)
    ctx.restore()

def check(ctx, x, y, s, alpha=1, color=GREEN):
    circle(ctx, x, y, s, color, alpha)
    ctx.set_source_rgba(1, 1, 1, alpha); ctx.set_line_width(s * 0.25); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(x - s * 0.45, y); ctx.line_to(x - s * 0.1, y + s * 0.35); ctx.line_to(x + s * 0.45, y - s * 0.35); ctx.stroke()

def phone(ctx, x, y, s, alpha=1, rot=0, buzz=0, t=0):
    ctx.save(); ctx.translate(x + math.sin(t * 60) * 6 * buzz, y); ctx.rotate(rot); ctx.scale(s / 100, s / 100)
    rrect(ctx, -60, -110, 120, 220, 22); ctx.set_source_rgba(0.12, 0.12, 0.2, alpha); ctx.fill()
    rrect(ctx, -50, -95, 100, 185, 12); ctx.set_source_rgba(0.85, 0.9, 1, alpha); ctx.fill()
    ctx.restore()

def cloud(ctx, x, y, s, alpha):
    for dx, dy, r in ((-0.6, 0.1, 0.45), (-0.15, -0.2, 0.6), (0.4, 0, 0.5), (0.0, 0.2, 0.5)):
        circle(ctx, x + dx * s, y + dy * s, r * s, (0.85, 0.85, 0.95), alpha)

# ---- hook ----
def s_hook(ctx, t, D):
    sid = "hook"
    fr, ea, ha, yo = kw(sid, "friend"), kw(sid, "easy"), kw(sid, "hard"), kw(sid, "yours")
    pop_text(ctx, "WISE FOR OTHERS,", CX, 330, 86, t, 0.1, WHITE)
    pop_text(ctx, "LOST FOR YOURSELF?", CX, 440, 86, t, 0.4, YEL)
    # you (teal) and friend (pink)
    yx = lerp(CX, 330, eio(prog(t, fr - 0.3, 0.6)))
    if t > yo - 0.3:
        knot(ctx, yx, 1050, 230 * eback(prog(t, yo - 0.3, 0.5)), t * 1.6, alpha=0.75)
    blobby(ctx, yx, 1050 + math.sin(t * 3) * 10, 140 * eback(prog(t, 0.2, 0.5)), t, TEAL,
           "wow" if t > ha else "happy", look=(1, 0) if t < ha else (0, 1))
    if t > fr - 0.2:
        s = eback(prog(t, fr - 0.2, 0.4))
        blobby(ctx, 780, 1050 + math.sin(t * 3 + 1) * 10, 120 * s, t, PINK, "sad" if t < ea + 0.3 else "happy", look=(-1, 0), seed=2)
        if t < ea + 0.3:
            knot(ctx, 780, 820, 90 * s, t)
        else:
            q = eback(prog(t, ea + 0.3, 0.3))
            check(ctx, 780, 830, 60 * q)
    if t > ea - 0.1:
        bulb(ctx, yx, 810 - 20 * math.sin(t * 4), 60 * eback(prog(t, ea - 0.1, 0.35)), t=t)
        pop_text(ctx, "EASY!", 780, 1290, 60, t, ea, GREEN)
    if t > yo - 0.3:
        pop_text(ctx, "HARD!", yx, 1290, 60, t, yo - 0.2, (1, 0.5, 0.5))

# ---- king ----
def s_king(ctx, t, D):
    sid = "king"
    so, ki, ev, ex = kw(sid, "solomon"), kw(sid, "king"), kw(sid, "everyone"), kw(sid, "except")
    pop_text(ctx, "SOLOMON'S", CX, 320, 110, t, so - 0.1, YEL)
    pop_text(ctx, "PARADOX", CX, 440, 110, t, so + 0.2, WHITE)
    kx = CX if t < ex else lerp(CX, CX, 1)
    s = eback(prog(t, ki - 0.3, 0.45))
    if t > ex - 0.1:
        knot(ctx, CX, 1000, 230 * eback(prog(t, ex - 0.1, 0.5)), t * 1.5, alpha=0.75)
    if s > 0:
        blobby(ctx, kx, 1000, 140 * s, t, PURPLE, "sad" if t > ex + 0.3 else "happy", look=(0, 0) if t < ex else (0, 1))
        crown(ctx, kx, 820 - 140 * (1 - s) + math.sin(t * 3) * 6, 110 * s, alpha=min(1, s))
    # people around get checks
    if t > ev - 0.3:
        for i in range(5):
            a = math.pi + i / 4 * math.pi * 1.0
            hx, hy = CX + math.cos(a) * 380, 1050 + math.sin(a) * 300 * -1 + 120
            hy = 1300 if i in (0, 4) else (900 if i == 2 else 1130)
            hx = [150, 230, CX, 850, 930][i]
            hy = [1080, 800, 650, 800, 1080][i] if i != 2 else 1300
            q = eback(prog(t, ev - 0.3 + i * 0.12, 0.3))
            human(ctx, hx, hy, 80 * q, color=[PINK, BLUE, GREEN, YEL, TEAL][i])
            if t > ev + i * 0.12 + 0.2:
                check(ctx, hx + 45, hy - 75, 26 * eback(prog(t, ev + i * 0.12 + 0.2, 0.3)))
    if t > ex - 0.1:
        pill(ctx, CX, 1440, 820, 130, DARK, 0.8 * prog(t, ex - 0.1, 0.2))
        pop_text(ctx, "...EXCEPT HIMSELF", CX, 1440, 70, t, ex - 0.1, PINK, stroke=0)

# ---- rude text ----
def s_text(ctx, t, D):
    sid = "text"
    ru, le, yo, re_, ni = kw(sid, "rude"), kw(sid, "let"), kw(sid, "you", 2), kw(sid, "replay"), kw(sid, "night")
    split = eio(prog(t, yo - 0.4, 0.6))
    if split < 1:
        a = 1 - split
        # friend's phone
        phone(ctx, 300, 900, 120 * eback(prog(t, 0.3, 0.4)), alpha=a, rot=-0.08, buzz=prog(t, ru - 0.2, 0.1) * (1 - prog(t, ru + 0.5, 0.1)), t=t)
        if t > ru:
            bubble(ctx, 300, 820, 200, 80, (1, 0.45, 0.5), a * prog(t, ru, 0.2), tail=-1)
            text(ctx, "k.", 300, 820, 54, WHITE, alpha=a * prog(t, ru, 0.2), stroke=0)
        blobby(ctx, 300, 1230, 95 * eback(prog(t, 0.4, 0.4)), t, PINK, "sad", seed=2, alpha=a)
        blobby(ctx, 760, 1150, 120 * eback(prog(t, 0.6, 0.4)), t, TEAL, "happy", look=(-1, 0), alpha=a)
        if t > le - 0.15:
            bubble(ctx, 760, 900, 380, 120, WHITE, a * prog(t, le - 0.15, 0.2), tail=-1)
            pop_text(ctx, "LET IT GO", 760, 900, 58, t, le - 0.15, DARK, stroke=0)
            if a < 1: pass
    if split > 0:
        a = split
        # night: moon, you in bed, replay loop
        circle(ctx, 860, 330 + 0 * t, 70, (1, 0.95, 0.75), a)
        circle(ctx, 890, 310, 62, (0.1, 0.07, 0.25), a)
        rrect(ctx, 200, 1100, 680, 170, 34); ctx.set_source_rgba(0.45, 0.5, 0.85, a); ctx.fill()
        rrect(ctx, 220, 1050, 160, 80, 30); ctx.set_source_rgba(*CREAM, a); ctx.fill()
        blobby(ctx, 380, 1040, 95, t, TEAL, "wow", look=(0.5, -1), alpha=a)
        ctx.rectangle(330, 1110, 560, 160); ctx.set_source_rgba(0.6, 0.65, 0.95, a); ctx.fill()
        phone(ctx, 640, 1000, 70, alpha=a, rot=0.15)
        # thought loop of "k." bubbles circling
        if t > re_ - 0.2:
            n = 6
            for i in range(n):
                q = eback(prog(t, re_ - 0.2 + i * 0.15, 0.3))
                ang = t * 2.2 + i / n * 2 * math.pi
                bx, by = 540 + math.cos(ang) * 320, 740 + math.sin(ang) * 140
                bubble(ctx, bx, by, 130 * q, 70 * q, (1, 0.45, 0.5), a * min(1, q), tail=-1)
                text(ctx, "k.", bx, by, 40, WHITE, alpha=a, scale=q, stroke=0)
            # replay counter
            cnt = int(clamp((t - re_) / 0.12, 0, 99)) + 1
            pop_text(ctx, f"REPLAY x{cnt}", CX, 420, 80, t, re_, YEL)
        if t > ni - 0.2:
            pop_text(ctx, "ALL NIGHT", CX, 1420, 90, t, ni - 0.2, PINK)

# ---- fog ----
def s_fog(ctx, t, D):
    sid = "fog"
    di, wi, cl, fe, fo = kw(sid, "distance"), kw(sid, "wise"), kw(sid, "close"), kw(sid, "feelings"), kw(sid, "fog")
    # zoom from far (small, clear) to close (big, foggy)
    z = eio(prog(t, cl - 0.3, 0.8))
    s = lerp(0.55, 1.35, z)
    # problem box with simple maze
    bx, by = CX, 950
    a = prog(t, 0.2, 0.3)
    ctx.save(); ctx.translate(bx, by); ctx.scale(s, s)
    rrect(ctx, -220, -220, 440, 440, 30); ctx.set_source_rgba(0.2, 0.18, 0.4, a); ctx.fill()
    ctx.set_source_rgba(*YEL, a); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for seg in (((-160, -160), (160, -160)), ((160, -160), (160, 60)), ((-160, -60), (60, -60)), ((-160, -60), (-160, 160)),
                ((-160, 160), (160, 160)), ((60, 60), (60, 160)), ((-60, 40), (60, 40))):
        ctx.move_to(*seg[0]); ctx.line_to(*seg[1]); ctx.stroke()
    # clear path when far
    pa = (1 - z) * prog(t, wi - 0.2, 0.4)
    if pa > 0:
        ctx.set_source_rgba(*GREEN, pa); ctx.set_line_width(10); ctx.set_dash([18, 14], -t * 60)
        ctx.move_to(-200, -110); ctx.line_to(110, -110); ctx.line_to(110, 100); ctx.line_to(200, 100); ctx.stroke(); ctx.set_dash([])
    ctx.restore()
    # wise owl-ish blob far away with telescope look
    if t < cl:
        blobby(ctx, CX, 1330, 80 * eback(prog(t, 0.4, 0.4)), t, TEAL, "happy", look=(0, -1))
        pop_text(ctx, "DISTANCE = CLEAR", CX, 380, 78, t, di, GREEN, end=cl - 0.3)
    if t > wi - 0.1 and t < cl:
        bulb(ctx, CX + 130, 1220, 40 * eback(prog(t, wi - 0.1, 0.3)), t=t)
    # fog rolls in
    if t > fe - 0.4:
        f = eio(prog(t, fe - 0.4, 1.0))
        random.seed(5)
        for i in range(14):
            x0 = random.uniform(-100, W + 100); y0 = random.uniform(650, 1300); r = random.uniform(120, 220)
            side = -1 if x0 < CX else 1
            x = x0 + side * (1 - f) * 700 + math.sin(t * 0.8 + i) * 30
            cloud(ctx, x, y0, r, 0.55 * f)
        blobby(ctx, CX, 1330, 90, t, TEAL, "sad", look=(0, -1))
        pop_text(ctx, "UP CLOSE = FOGGY", CX, 380, 78, t, cl, PINK)
    if t > fo - 0.1:
        pill(ctx, CX, 1460, 760, 120, DARK, 0.8 * prog(t, fo - 0.1, 0.2))
        pop_text(ctx, "FEELINGS FOG IT", CX, 1460, 64, t, fo - 0.1, YEL, stroke=0)

# ---- tip ----
def s_tip(ctx, t, D):
    sid = "tip"
    st, wh, fr, ch, ad = kw(sid, "step"), kw(sid, "what"), kw(sid, "friend", 0), kw(sid, "check"), kw(sid, "advice")
    p1 = 1 - prog(t, ch - 0.4, 0.4)
    if p1 > 0:
        # step back: blob shrinks and moves back, footprints
        back = eio(prog(t, st, 0.8))
        bx, by, r = CX - 220 * back, lerp(1100, 1000, back), lerp(150, 105, back)
        if t > st:
            for i in range(3):
                q = prog(t, st + i * 0.2, 0.2)
                circle(ctx, CX - 60 - i * 70, 1240 + (i % 2) * 30, 18, WHITE, 0.35 * q * p1)
        blobby(ctx, bx, by, r * eback(prog(t, 0.2, 0.4)), t, TEAL, "happy", look=(1, 0), alpha=p1)
        pop_text(ctx, "STEP BACK", CX, 360, 100, t, st - 0.1, YEL, end=ch - 0.5)
        if t > wh - 0.2:
            q = eback(prog(t, wh - 0.2, 0.4))
            bubble(ctx, 640, 700, 640 * q, 200 * q, WHITE, p1 * min(1, q), tail=-1)
            pop_text(ctx, "WHAT WOULD I", 640, 660, 56, t, wh - 0.2, DARK, stroke=0)
            pop_text(ctx, "TELL A FRIEND?", 640, 740, 56, t, fr - 0.2, PINK, stroke=0)
        if t > fr:
            bulb(ctx, bx, by - r - 80, 50 * eback(prog(t, fr, 0.3)), alpha=p1, t=t)
    if t > ch - 0.4:
        a = prog(t, ch - 0.4, 0.4)
        # the advice-giver: blob with many bubbles pointing at others
        ax, ay = CX, 1050
        for i in range(5):
            ang = -math.pi * 0.95 + i / 4 * math.pi * 0.9
            q = eback(prog(t, ch - 0.2 + i * 0.1, 0.3))
            bxx, byy = ax + math.cos(ang) * 340, ay + math.sin(ang) * 330
            bubble(ctx, bxx, byy, 120 * q, 70 * q, [BLUE, GREEN, YEL, PINK, PURPLE][i], a * min(1, q), tail=-1)
            text(ctx, "...", bxx, byy - 8, 44, WHITE, alpha=a, scale=q, stroke=0)
        blobby(ctx, ax, ay, 130, t, PURPLE, "sad" if t < ad else "happy", alpha=a, seed=4)
        pop_text(ctx, "CHECK ON THE", CX, 330, 84, t, ch - 0.2, WHITE)
        pop_text(ctx, "ADVICE-GIVER", CX, 440, 84, t, ch + 0.1, YEL)
        if t > ad - 0.1:
            for i in range(6):
                q = prog(t, ad - 0.1 + i * 0.1, 0.9)
                if 0 < q:
                    hx = lerp([150, 930, 220, 860, 300, 780][i], ax + (i - 2.5) * 30, eio(min(1, q)))
                    hy = lerp(1500, ay - 190, eio(min(1, q)))
                    heart(ctx, hx, hy, 55 * (1 - 0.3 * clamp(q - 1, 0, 1)), PINK, 1)

# ---- end ----
def s_end(ctx, t, D):
    sid = "end"
    fl = kw(sid, "follow")
    pop_text(ctx, "BE YOUR OWN", CX, 360, 100, t, 0.1, WHITE)
    pop_text(ctx, "WISE FRIEND", CX, 470, 100, t, 0.35, YEL)
    for i in range(6):
        a = -math.pi / 2 + i / 6 * 2 * math.pi + t * 0.3
        x = CX + math.cos(a) * 290; y = 950 + math.sin(a) * 290
        s = eback(prog(t, 0.3 + i * 0.1, 0.35))
        if s > 0:
            cookie(ctx, x, y, 58 * s)
    blobby(ctx, CX, 950, 120 * eback(prog(t, 0.2, 0.4)), t, TEAL, "happy")
    heart(ctx, CX + 110, 830 + math.sin(t * 4) * 8, 50 * eback(prog(t, 0.6, 0.3)), PINK)
    if t >= fl - 0.1:
        pul = 1 + 0.05 * math.sin(t * 8)
        ctx.save(); ctx.translate(CX, 1420); ctx.scale(pul, pul); ctx.translate(-CX, -1420)
        pill(ctx, CX, 1420, 880, 130, (1, 0.25, 0.35), eback(prog(t, fl - 0.1, 0.3)))
        pop_text(ctx, "FOLLOW @thought.snackss", CX, 1420, 52, t, fl - 0.1, WHITE, stroke=0)
        ctx.restore()

SCENES = {"hook": s_hook, "king": s_king, "text": s_text, "fog": s_fog, "tip": s_tip, "end": s_end}

def credit(ctx, alpha=0.75):
    return

LOGO = cairo.ImageSurface.create_from_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../branding/logo.png"))
def watermark(ctx):
    d = 92; x, y = 90, 105
    ctx.save(); ctx.arc(x + d / 2, y + d / 2, d / 2, 0, 2 * math.pi); ctx.clip()
    ctx.translate(x, y); ctx.scale(d / 1080, d / 1080); ctx.set_source_surface(LOGO, 0, 0); ctx.paint(); ctx.restore()
    ctx.arc(x + d / 2, y + d / 2, d / 2, 0, 2 * math.pi); ctx.set_source_rgba(0.99, 0.8, 0.42, 0.9); ctx.set_line_width(4); ctx.stroke()
    font(ctx, 36); ctx.move_to(x + d + 20, y + d / 2 + 13); ctx.text_path("@thought.snackss")
    ctx.set_source_rgba(0.04, 0.03, 0.12, 0.8); ctx.set_line_width(6); ctx.stroke_preserve(); ctx.set_source_rgb(0.97, 0.93, 0.85); ctx.fill()

def draw(ctx, sid, t):
    T = SCENE_START[sid] + t
    D = SCENE_LEN[sid]
    background(ctx, T)
    ctx.save()
    # scene entry: quick zoom-settle
    e = prog(t, 0, 0.3)
    sc = lerp(1.06, 1, eo(e))
    ctx.translate(CX, CY); ctx.scale(sc, sc); ctx.translate(-CX, -CY)
    ctx.push_group()
    SCENES[sid](ctx, t, D)
    ctx.pop_group_to_source()
    a = eo(e)
    if sid != "end" and t > D - 0.2:
        a *= 1 - prog(t, D - 0.2, 0.2) * 0.0
    ctx.paint_with_alpha(a)
    ctx.restore()
    captions(ctx, sid, t)
    if sid in ("hook", "end"):
        credit(ctx, 0.75 if sid == "end" else 0.6 * (1 - prog(t, 3.5, 0.5)))
    watermark(ctx)
    # progress bar
    total = sum(SCENE_LEN.values())
    pill(ctx, W / 2, 60, 900, 10, WHITE, 0.15)
    w = 900 * T / total
    ctx.rectangle(W / 2 - 450, 55, w, 10); ctx.set_source_rgba(*YEL, 0.9); ctx.fill()

def render_scene(sid, out=None, still=None):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    if still is not None:
        ctx = cairo.Context(surf); draw(ctx, sid, still); surf.write_to_png(out); return
    n = int(round(SCENE_LEN[sid] * FPS))
    tmp = f"scenes/{sid}.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(n):
        ctx = cairo.Context(surf)
        ctx.set_operator(cairo.OPERATOR_SOURCE); ctx.set_source_rgb(0, 0, 0); ctx.paint(); ctx.set_operator(cairo.OPERATOR_OVER)
        draw(ctx, sid, i / FPS)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, f"scenes/{sid}.mp4")
        print("done", sid, n)

if __name__ == "__main__":
    os.makedirs("scenes", exist_ok=True)
    if sys.argv[1] == "still":
        sid, t = sys.argv[2], float(sys.argv[3])
        render_scene(sid, out=f"still_{sid}_{t}.png", still=t)
    else:
        for sid in sys.argv[2:]:
            render_scene(sid)
