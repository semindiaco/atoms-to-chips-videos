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



# ---- shared bits for "No feeling is final" ----
GREY = (0.55, 0.58, 0.7)

def bubble(ctx, x, y, w, h, color, alpha=1, tail=-1):
    rrect(ctx, x - w / 2, y - h / 2, w, h, min(40, h / 2))
    ctx.set_source_rgba(*color, alpha); ctx.fill()
    ctx.move_to(x + tail * w * 0.25, y + h / 2 - 2); ctx.line_to(x + tail * w * 0.32, y + h / 2 + 40)
    ctx.line_to(x + tail * w * 0.1, y + h / 2 - 2); ctx.close_path(); ctx.fill()

def cloud(ctx, x, y, s, alpha, color=(0.85, 0.85, 0.95)):
    for dx, dy, r in ((-0.6, 0.1, 0.45), (-0.15, -0.2, 0.6), (0.4, 0, 0.5), (0.0, 0.2, 0.5)):
        circle(ctx, x + dx * s, y + dy * s, r * s, color, alpha)

def rain(ctx, x, y, w, t, alpha=1, n=10):
    ctx.set_source_rgba(0.5, 0.75, 1, alpha); ctx.set_line_width(8); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(n):
        xx = x - w / 2 + (i + 0.5) * w / n
        ph = ((t * 2.2 + i * 0.37) % 1)
        yy = y + ph * 260
        ctx.move_to(xx, yy); ctx.line_to(xx - 6, yy + 34); ctx.stroke()

def sun(ctx, x, y, s, t, alpha=1):
    rg = cairo.RadialGradient(x, y, s * 0.3, x, y, s * 2.2)
    rg.add_color_stop_rgba(0, *YEL, 0.45 * alpha); rg.add_color_stop_rgba(1, *YEL, 0)
    ctx.set_source(rg); ctx.arc(x, y, s * 2.2, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgba(*YEL, alpha); ctx.set_line_width(s * 0.12); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(10):
        a = k / 10 * 2 * math.pi + t * 0.6
        ctx.move_to(x + math.cos(a) * s * 1.2, y + math.sin(a) * s * 1.2)
        ctx.line_to(x + math.cos(a) * s * 1.5, y + math.sin(a) * s * 1.5); ctx.stroke()
    circle(ctx, x, y, s, YEL, alpha)
    if alpha > 0.5: face(ctx, x, y, s * 0.7, t, "happy")

def rock(ctx, x, y, s, alpha=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    pts = [(-95, 40), (-80, -30), (-30, -70), (40, -65), (90, -20), (95, 40)]
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path()
    ctx.set_source_rgba(*DARK, alpha); ctx.set_line_width(10); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    ctx.set_source_rgba(*GREY, alpha); ctx.fill()
    circle(ctx, -30, -20, 12, (0.45, 0.48, 0.6), alpha); circle(ctx, 30, 5, 9, (0.45, 0.48, 0.6), alpha)
    ctx.restore()

def half_heart(ctx, x, y, s, side, color=PINK, alpha=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.move_to(0, 35)
    if side < 0:
        ctx.curve_to(-60, -5, -45, -60, 0, -30); ctx.line_to(-8, -12); ctx.line_to(6, 2); ctx.line_to(-6, 18)
    else:
        ctx.curve_to(60, -5, 45, -60, 0, -30); ctx.line_to(-8, -12); ctx.line_to(6, 2); ctx.line_to(-6, 18)
    ctx.close_path(); ctx.set_source_rgba(*color, alpha); ctx.fill()
    ctx.restore()

def mug(ctx, x, y, s, t, alpha=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.set_source_rgba(1, 1, 1, 0.7 * alpha); ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in (-20, 0, 20):
        ctx.move_to(k, -60)
        for i in range(1, 12):
            ctx.line_to(k + math.sin(i * 0.8 - t * 5 + k) * 8, -60 - i * 6)
        ctx.stroke()
    rrect(ctx, -50, -50, 100, 100, 18); ctx.set_source_rgba(*ORANGE, alpha); ctx.fill()
    ctx.set_source_rgba(*ORANGE, alpha); ctx.set_line_width(14)
    ctx.arc(52, 0, 24, -math.pi / 2, math.pi / 2); ctx.stroke()
    ctx.restore()
    if alpha > 0.5: face(ctx, x, y + s * 0.05, s * 0.45, t, "happy")

def plant(ctx, x, y, s, t, grow=1, alpha=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.move_to(-45, 0); ctx.line_to(45, 0); ctx.line_to(32, 70); ctx.line_to(-32, 70); ctx.close_path()
    ctx.set_source_rgba(0.85, 0.45, 0.3, alpha); ctx.fill()
    h = 110 * grow
    ctx.set_source_rgba(*GREEN, alpha); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(0, 0); ctx.line_to(math.sin(t * 2) * 6, -h); ctx.stroke()
    for i, (fy, side) in enumerate(((0.35, -1), (0.6, 1), (0.85, -1), (1.0, 1))):
        q = clamp((grow - fy * 0.7) / 0.3)
        if q > 0:
            ctx.save(); ctx.translate(math.sin(t * 2) * 6 * fy, -h * fy); ctx.rotate(side * 0.6); ctx.scale(q, q)
            ctx.save(); ctx.scale(1, 0.5); circle(ctx, side * 28, 0, 28, GREEN, alpha); ctx.restore(); ctx.restore()
    ctx.restore()

def phone(ctx, x, y, s, alpha=1, rot=0, t=0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s / 100, s / 100)
    rrect(ctx, -60, -110, 120, 220, 22); ctx.set_source_rgba(0.12, 0.12, 0.2, alpha); ctx.fill()
    rrect(ctx, -50, -95, 100, 185, 12); ctx.set_source_rgba(0.85, 0.9, 1, alpha); ctx.fill()
    ctx.restore()

def anchor(ctx, x, y, s, alpha=1, color=YEL):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.set_source_rgba(*color, alpha); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.arc(0, -60, 16, 0, 2 * math.pi); ctx.stroke()
    ctx.move_to(0, -44); ctx.line_to(0, 60); ctx.stroke()
    ctx.move_to(-30, -20); ctx.line_to(30, -20); ctx.stroke()
    ctx.arc(0, 10, 50, 0.15 * math.pi, 0.85 * math.pi); ctx.stroke()
    ctx.restore()

def boat(ctx, x, y, s, t, rot=0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s / 100, s / 100)
    ctx.move_to(-110, -10); ctx.line_to(110, -10); ctx.line_to(75, 45); ctx.line_to(-75, 45); ctx.close_path()
    ctx.set_source_rgb(*CREAM); ctx.fill()
    ctx.rectangle(-110, -10, 220, 14); ctx.set_source_rgb(*PINK); ctx.fill()
    ctx.restore()

def waves(ctx, y, t, alpha=1, color=BLUE):
    ctx.move_to(0, H)
    for i in range(0, W + 20, 20):
        ctx.line_to(i, y + math.sin(i / 90 + t * 2.5) * 18)
    ctx.line_to(W, H); ctx.close_path()
    ctx.set_source_rgba(*color, 0.55 * alpha); ctx.fill()

def wave_y(x, y, t): return y + math.sin(x / 90 + t * 2.5) * 18


def check(ctx, x, y, s, alpha=1, color=GREEN):
    if s <= 0: return
    circle(ctx, x, y, s, color, alpha)
    ctx.set_source_rgba(1, 1, 1, alpha); ctx.set_line_width(s * 0.25); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(x - s * 0.45, y); ctx.line_to(x - s * 0.1, y + s * 0.35); ctx.line_to(x + s * 0.45, y - s * 0.35); ctx.stroke()

# ---- hook ----
def s_hook(ctx, t, D):
    sid = "hook"
    he, su, fo = kw(sid, "heavy"), kw(sid, "sure"), kw(sid, "forever")
    pop_text(ctx, "WILL THIS FEELING", CX, 330, 86, t, 0.1, WHITE)
    pop_text(ctx, "LAST FOREVER?", CX, 440, 96, t, 0.4, YEL)
    squash = 1 - 0.25 * eback(prog(t, he, 0.4))
    bx, by = CX, 1180
    r = 140 * eback(prog(t, 0.15, 0.5))
    # grey rain cloud
    if t > 0.3:
        q = eback(prog(t, 0.3, 0.5))
        cloud(ctx, CX, 700 + math.sin(t * 2) * 8, 150 * q, 0.9, GREY)
        if t > 0.7: rain(ctx, CX, 780, 360, t, 0.8 * prog(t, 0.7, 0.3))
    ctx.save(); ctx.translate(bx, by + r); ctx.scale(1 + (1 - squash) * 0.6, squash); ctx.translate(-bx, -(by + r))
    blobby(ctx, bx, by, r, t, BLUE, "sad", look=(0, -1))
    ctx.restore()
    # heavy rock drops on "heavy"
    if t > he - 0.3:
        q = eo(prog(t, he - 0.3, 0.3))
        rock(ctx, bx, lerp(500, by - r * squash - 50, q), 150, 1)
        pop_text(ctx, "HEAVY", 220, 1000, 64, t, he, (0.75, 0.8, 1), rot=-0.15)
    if t > fo - 0.2:
        q = eback(prog(t, fo - 0.2, 0.4))
        ctx.save(); ctx.translate(860, 980); ctx.scale(q, q)
        ctx.set_source_rgb(*PINK); ctx.set_line_width(22); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for sg in (-1, 1):
            ctx.save(); ctx.translate(sg * 45, 0); ctx.scale(1, 0.75)
            ctx.arc(0, 0, 45, 0, 2 * math.pi); ctx.restore(); ctx.stroke()
        ctx.restore()

# ---- truth ----
def s_truth(ctx, t, D):
    sid = "truth"
    ge, fi, he, pa, we = kw(sid, "gentle"), kw(sid, "final"), kw(sid, "heartbreak"), kw(sid, "passes"), kw(sid, "weather")
    pop_text(ctx, "NO FEELING", CX, 330, 110, t, kw(sid, "no") - 0.1, WHITE)
    pop_text(ctx, "IS FINAL", CX, 450, 110, t, fi - 0.2, YEL)
    if t < he - 0.3:
        fa = 1 - prog(t, he - 0.5, 0.2)
        blobby(ctx, CX, 950 + math.sin(t * 3) * 10, 130 * eback(prog(t, 0.1, 0.4)), t, BLUE, "happy", alpha=fa)
        pop_text(ctx, "A GENTLE TRUTH", CX, 1250, 70, t, ge - 0.2, PINK, end=he - 0.5)
    # heart breaks then mends
    if t > he - 0.3 and t < pa + 0.1:
        q = eback(prog(t, he - 0.3, 0.35))
        gap = 60 * eo(prog(t, he + 0.3, 0.4))
        for sg in (-1, 1):
            half_heart(ctx, CX + sg * gap, 950 + gap * 0.3, 260 * q, sg, PINK)
        pop_text(ctx, "NOT EVEN THIS", CX, 1250, 64, t, he + 0.1, WHITE)
    # weather: cloud drifts away, sun comes out
    if t > pa - 0.2:
        a = prog(t, pa - 0.2, 0.3)
        mv = eio(prog(t, pa, 1.4))
        sun(ctx, CX, 950, 120 * eback(prog(t, pa + 0.2, 0.5)), t)
        cloud(ctx, lerp(CX - 60, -260, mv), 930, 170, 0.95 * a, GREY)
        cloud(ctx, lerp(CX + 120, W + 260, mv), 1030, 130, 0.95 * a, GREY)
        if mv < 0.6: rain(ctx, lerp(CX, -200, mv), 1000, 300, t, a * (1 - mv / 0.6))
        pop_text(ctx, "IT PASSES", CX, 1300, 84, t, pa, GREEN)
        if t > we - 0.1:
            for i in range(5):
                q = eback(prog(t, we - 0.1 + i * 0.08, 0.3))
                ang = -math.pi / 2 + (i - 2) * 0.55
                heart(ctx, CX + math.cos(ang) * 320, 950 + math.sin(ang) * 300 + 40, 45 * q, [PINK, YEL, TEAL, GREEN, PURPLE][i])

# ---- heal ----
def s_heal(ctx, t, D):
    sid = "heal"
    bi, co, pl, te = kw(sid, "big"), kw(sid, "coffee"), kw(sid, "plant"), kw(sid, "text")
    ph = prog(t, co - 0.5, 0.3)
    if ph < 1:
        a = 1 - ph
        # calendar "one big day" that gets crossed out
        q = eback(prog(t, 0.2, 0.4))
        ctx.save(); ctx.translate(CX, 900); ctx.scale(q, q)
        rrect(ctx, -220, -200, 440, 400, 36); ctx.set_source_rgba(*CREAM, a); ctx.fill()
        rrect(ctx, -220, -200, 440, 100, 36); ctx.set_source_rgba(1, 0.4, 0.45, a); ctx.fill()
        ctx.rectangle(-220, -140, 440, 40); ctx.fill()
        ctx.restore()
        text(ctx, "HEALED!", CX, 945, 84, DARK, alpha=a * min(1, q), scale=q, stroke=0)
        pop_text(ctx, "ONE BIG DAY?", CX, 380, 96, t, bi - 0.4, WHITE, end=co - 0.5)
        if t > bi + 0.25:
            c = eo(prog(t, bi + 0.25, 0.3))
            ctx.set_source_rgba(1, 0.3, 0.35, a); ctx.set_line_width(26); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(CX - 240, 700); ctx.line_to(CX - 240 + 480 * c, 700 + 400 * c); ctx.stroke()
            pop_text(ctx, "RARELY", CX, 1260, 70, t, bi + 0.3, PINK)
    if ph > 0:
        pop_text(ctx, "JUST SMALL THINGS", CX, 380, 86, t, co - 0.4, YEL)
        items = ((co, 260, "COFFEE"), (pl, CX, "A PLANT"), (te, 820, "A FRIEND"))
        for i, (st, x, lab) in enumerate(items):
            if t > st - 0.25:
                q = eback(prog(t, st - 0.25, 0.4))
                y = 960 + math.sin(t * 3 + i) * 10
                if i == 0: mug(ctx, x, y, 130 * q, t)
                elif i == 1: plant(ctx, x, y + 20, 130 * q, t, grow=eo(prog(t, st, 1.2)))
                else:
                    phone(ctx, x, y, 95 * q, rot=0.1)
                    if t > st + 0.15:
                        qq = eback(prog(t, st + 0.15, 0.3))
                        bubble(ctx, x, y - 50, 90 * qq, 70 * qq, PINK, 1, tail=-1)
                        heart(ctx, x, y - 52, 40 * qq, WHITE)
                pop_text(ctx, lab, x, 1220, 52, t, st, WHITE)
                check(ctx, x, 1320, 34 * eback(prog(t, st + 0.3, 0.3)))
        blobby(ctx, CX, 690, 70 * eback(prog(t, co - 0.3, 0.4)), t, BLUE, "happy", look=(0, 1))

# ---- anchor ----
def s_anchor(ctx, t, D):
    sid = "anchor"
    ti, an, fi, gi, li = kw(sid, "tiny"), kw(sid, "anchors"), kw(sid, "fix"), kw(sid, "give"), kw(sid, "live")
    wy = 1150
    # storm-ish waves calm down after "anchors"
    calm = eo(prog(t, an, 1.0))
    rot = math.sin(t * 3) * 0.12 * (1 - 0.8 * calm)
    by = wave_y(CX, wy, t) * (1 - 0.7 * calm) + wy * 0.7 * calm - 30
    if t > gi - 0.2:
        sun(ctx, 860, lerp(1100, 640, eo(prog(t, gi - 0.2, 1.2))), 80, t)
    boat(ctx, CX, by + 40, 150, t, rot)
    blobby(ctx, CX, by - 60, 90 * eback(prog(t, 0.15, 0.4)), t, BLUE, "happy" if t > an else "wow", look=(0, 1))
    waves(ctx, wy + 40, t)
    pop_text(ctx, "TINY MOMENTS", CX, 330, 96, t, ti - 0.15, WHITE)
    pop_text(ctx, "= LITTLE ANCHORS", CX, 440, 86, t, an - 0.2, YEL)
    # three tiny glowing icons floating, then chain to the anchor
    if t > ti:
        for i in range(3):
            q = eback(prog(t, ti + i * 0.15, 0.3))
            x = [260, CX, 820][i]; y = 660 + math.sin(t * 2.5 + i) * 15
            fa = 1 - prog(t, gi - 0.4, 0.3)
            if fa <= 0: continue
            circle(ctx, x, y, 46 * q, [ORANGE, GREEN, PINK][i], 0.9 * fa)
            if q > 0.5 and fa > 0.6: face(ctx, x, y, 34 * q, t, "happy")
    if t > an - 0.1:
        d = eo(prog(t, an - 0.1, 0.6))
        ay = lerp(by + 80, 1330, d)
        ctx.set_source_rgba(*CREAM, 0.8); ctx.set_line_width(6); ctx.set_dash([14, 10])
        ctx.move_to(CX + 90, by + 50); ctx.line_to(CX + 90, ay - 60); ctx.stroke(); ctx.set_dash([])
        anchor(ctx, CX + 90, ay, 110)
    if t > fi - 0.2 and t < gi - 0.1:
        pop_text(ctx, "NOT A FIX...", 230, 900, 56, t, fi - 0.2, PINK, rot=-0.1)
    if t > li - 0.3:
        pill(ctx, CX, 1460, 880, 120, DARK, 0.8 * prog(t, li - 0.3, 0.2))
        pop_text(ctx, "SOMETHING TO LIVE FOR", CX, 1460, 58, t, li - 0.3, YEL, stroke=0)

# ---- soft ----
def s_soft(ctx, t, D):
    sid = "soft"
    ge, so, fe, ke = kw(sid, "gentle"), kw(sid, "soft"), kw(sid, "feel"), kw(sid, "keep")
    pop_text(ctx, "BE GENTLE", CX, 330, 104, t, ge - 0.2, WHITE)
    pop_text(ctx, "WITH YOURSELF", CX, 440, 86, t, ge + 0.2, PINK)
    walk = eio(prog(t, ke - 0.1, 1.4))
    bx = lerp(CX, 820, walk)
    hop = abs(math.sin(t * 7)) * 30 * (walk > 0 and walk < 1)
    by = 1050 - hop
    # soft squish pulse
    sq = 1 + 0.08 * math.sin(t * 5) * prog(t, so - 0.2, 0.3)
    r = 140 * eback(prog(t, 0.15, 0.45))
    if t > so - 0.2:
        q = eback(prog(t, so - 0.2, 0.4))
        rg = cairo.RadialGradient(bx, by, r * 0.5, bx, by, r * 2.2)
        rg.add_color_stop_rgba(0, *PINK, 0.35 * q); rg.add_color_stop_rgba(1, *PINK, 0)
        ctx.set_source(rg); ctx.arc(bx, by, r * 2.2, 0, 2 * math.pi); ctx.fill()
    # arms hugging self
    ctx.save(); ctx.translate(bx, by); ctx.scale(1 / sq, sq); ctx.translate(-bx, -by)
    blobby(ctx, bx, by, r, t, BLUE, "happy", look=(1 if walk > 0 else 0, 0))
    ctx.restore()
    if t > ge and walk <= 0:
        heart(ctx, bx + r * 0.85, by - r * 0.85, 60 * eback(prog(t, ge, 0.3)), PINK)
    if t > so - 0.2:
        for i in range(6):
            q = prog(t, so - 0.2 + i * 0.15, 1.6)
            if 0 < q < 1:
                a = i / 6 * 2 * math.pi
                heart(ctx, bx + math.cos(a) * (r + 60), by - q * 260 + math.sin(a) * 40, 34, [PINK, YEL, TEAL][i % 3], 1 - q)
        pop_text(ctx, "STAY SOFT", 260, 1320, 66, t, so - 0.1, YEL, end=ke - 0.2)
    if t > fe - 0.1 and t < ke - 0.1:
        pop_text(ctx, "FEEL IT", 820, 1320, 66, t, fe - 0.1, TEAL)
    if t > ke - 0.1:
        for i in range(6):
            fx = lerp(CX, 820, i / 6)
            if walk > i / 6:
                circle(ctx, fx - 40, 1230 + (i % 2) * 24, 16, WHITE, 0.35)
        pill(ctx, CX, 1440, 640, 120, DARK, 0.8 * prog(t, ke - 0.1, 0.2))
        pop_text(ctx, "KEEP GOING", CX, 1440, 70, t, ke - 0.1, GREEN, stroke=0)

# ---- end ----
def s_end(ctx, t, D):
    sid = "end"
    fl = kw(sid, "follow")
    pop_text(ctx, "NO FEELING", CX, 360, 100, t, 0.1, WHITE)
    pop_text(ctx, "IS FINAL", CX, 470, 100, t, 0.35, YEL)
    for i in range(6):
        a = -math.pi / 2 + i / 6 * 2 * math.pi + t * 0.3
        x = CX + math.cos(a) * 290; y = 950 + math.sin(a) * 290
        s = eback(prog(t, 0.3 + i * 0.1, 0.35))
        if s > 0:
            cookie(ctx, x, y, 58 * s)
    blobby(ctx, CX, 950, 120 * eback(prog(t, 0.2, 0.4)), t, BLUE, "happy")
    heart(ctx, CX + 110, 830 + math.sin(t * 4) * 8, 50 * eback(prog(t, 0.6, 0.3)), PINK)
    if t >= fl - 0.1:
        pul = 1 + 0.05 * math.sin(t * 8)
        ctx.save(); ctx.translate(CX, 1420); ctx.scale(pul, pul); ctx.translate(-CX, -1420)
        pill(ctx, CX, 1420, 880, 130, (1, 0.25, 0.35), eback(prog(t, fl - 0.1, 0.3)))
        pop_text(ctx, "FOLLOW @thought.snackss", CX, 1420, 52, t, fl - 0.1, WHITE, stroke=0)
        ctx.restore()

SCENES = {"hook": s_hook, "truth": s_truth, "heal": s_heal, "anchor": s_anchor, "soft": s_soft, "end": s_end}

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
