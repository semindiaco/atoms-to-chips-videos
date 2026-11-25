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

# ---- hook ----
def s_hook(ctx, t, D):
    sid = "hook"
    pop_text(ctx, "7 ANCIENT", CX, 330, 110, t, 0.1, YEL)
    pop_text(ctx, "CHINESE IDEAS", CX, 450, 100, t, 0.35, WHITE)
    ef, pa, ti, sn = kw(sid, "effort"), kw(sid, "pain"), kw(sid, "time"), kw(sid, "snack")
    blobby(ctx, CX, 1000 + math.sin(t * 3) * 12, 150 * eback(prog(t, 0.2, 0.5)), t, TEAL, "wow" if t > sn else "happy")
    for i in range(7):
        st = 0.5 + i * 0.25
        a = -math.pi / 2 + i / 7 * 2 * math.pi + t * 0.6
        r = 300
        s = eback(prog(t, st, 0.35))
        if s > 0:
            x = CX + math.cos(a) * r; y = 1000 + math.sin(a) * r * 0.85
            if t > sn:
                p = eio(prog(t, sn, 0.6)); x = lerp(x, CX, p * 0.4); y = lerp(y, 1000, p * 0.4)
            cookie(ctx, x, y, 52 * s)
    for k, (w, st, col) in enumerate((("EFFORT", ef, PINK), ("PAIN", pa, BLUE), ("TIME", ti, GREEN))):
        if t >= st - 0.1:
            x = [240, 540, 840][k]
            font(ctx, 50); wd = ctx.text_extents(w).x_advance + 60
            pill(ctx, x, 1420, wd, 96, col, 0.95 * eback(prog(t, st - 0.1, 0.3)))
            pop_text(ctx, w, x, 1420, 50, t, st - 0.1, WHITE, stroke=0)

# ---- yin yang ----
def s_yin(ctx, t, D):
    sid = "yin"
    badge(ctx, t, 1, "YIN & YANG", "THE SUN KEEPS MOVING")
    hl, mv, ld, qt = kw(sid, "hill"), kw(sid, "moving"), kw(sid, "loud"), kw(sid, "quiet")
    hx, hy = CX, 1120
    a = prog(t, hl - 0.3, 0.5)
    # sun path
    sp = eio(prog(t, mv - 0.6, 2.2))
    ang = math.radians(lerp(200, 340, sp))
    sx, sy = hx + math.cos(ang) * 400, hy - 80 + math.sin(ang) * 330
    if a > 0:
        rg = cairo.RadialGradient(sx, sy, 10, sx, sy, 120); rg.add_color_stop_rgba(0, 1, 0.9, 0.4, a); rg.add_color_stop_rgba(1, 1, 0.8, 0.3, 0)
        ctx.set_source(rg); ctx.arc(sx, sy, 120, 0, 2 * math.pi); ctx.fill()
        circle(ctx, sx, sy, 50, (1, 0.85, 0.3), a)
    # hill: two halves shaded according to sun side
    left_lit = 1 - sp
    for side in (-1, 1):
        lit = left_lit if side == -1 else sp
        col = (lerp(0.2, 0.45, lit), lerp(0.25, 0.75, lit), lerp(0.35, 0.4, lit))
        ctx.move_to(hx, hy - 250)
        ctx.curve_to(hx + side * 150, hy - 250, hx + side * 280, hy - 60, hx + side * 420, hy + 60)
        ctx.line_to(hx, hy + 60); ctx.close_path()
        ctx.set_source_rgba(*col, a); ctx.fill()
    if t > hl:
        text(ctx, "YANG", hx + (-200 if sp < 0.5 else 200), hy - 10, 46, YEL, alpha=prog(t, hl, 0.3), stroke=6)
        text(ctx, "YIN", hx + (200 if sp < 0.5 else -200), hy - 10, 46, (0.7, 0.75, 1), alpha=prog(t, hl, 0.3), stroke=6)
    # loud / quiet blobs
    if t >= ld - 0.1:
        sc = eback(prog(t, ld - 0.1, 0.35))
        blobby(ctx, 280, 1400, 90 * sc, t, PINK, "wow")
        pop_text(ctx, "LOUD", 280, 1290, 48, t, ld - 0.1, PINK)
    if t >= qt - 0.1:
        sc = eback(prog(t, qt - 0.1, 0.35))
        blobby(ctx, 800, 1400, 90 * sc, t, BLUE, sleepy=True, seed=2)
        pop_text(ctx, "quiet", 800, 1290, 48, t, qt - 0.1, (0.7, 0.8, 1))

# ---- wu wei ----
def s_wuwei(ctx, t, D):
    sid = "wuwei"
    badge(ctx, t, 2, "WU WEI", "STOP FORCING")
    sl, mud, st_, lv = kw(sid, "sleep"), kw(sid, "muddy"), kw(sid, "stirring"), kw(sid, "still")
    # left: bed with straining blob
    a = prog(t, sl - 0.5, 0.4)
    if a > 0:
        rrect(ctx, 120, 900, 380, 150, 30); ctx.set_source_rgba(0.45, 0.5, 0.85, a); ctx.fill()
        rrect(ctx, 130, 860, 110, 70, 25); ctx.set_source_rgba(*CREAM, a); ctx.fill()
        shake = math.sin(t * 40) * 6 * (1 if t > sl else 0)
        blobby(ctx, 330 + shake, 860, 85, t, TEAL, "wow", alpha=a)
        if t > sl:
            ctx.set_source_rgba(1, 0.4, 0.4, 0.9); ctx.set_line_width(6)
            for i in range(3):
                ctx.move_to(420 + i * 25, 760 - i * 10); ctx.line_to(440 + i * 25, 790 - i * 10); ctx.stroke()
            text(ctx, "zzz?", 260, 730, 50, WHITE, alpha=prog(t, sl, 0.3), stroke=6, rot=-0.1)
            cross_a = prog(t, sl + 0.5, 0.2)
            if cross_a > 0:
                ctx.set_source_rgba(1, 0.35, 0.4, cross_a); ctx.set_line_width(14)
                ctx.move_to(220, 700); ctx.line_to(300, 760); ctx.move_to(300, 700); ctx.line_to(220, 760); ctx.stroke()
    # right: glass of muddy water
    b = prog(t, mud - 0.4, 0.4)
    if b > 0:
        gx, gy, gw, gh = 640, 760, 300, 420
        stir = prog(t, st_ - 0.3, 0.1) * (1 - prog(t, lv, 0.1))
        settle = eio(prog(t, lv, 2.0))
        # water
        ctx.rectangle(gx + 12, gy + 60, gw - 24, gh - 72)
        mc = (lerp(0.55, 0.45, settle), lerp(0.4, 0.75, settle), lerp(0.25, 0.95, settle))
        ctx.set_source_rgba(*mc, 0.85 * b); ctx.fill()
        random.seed(3)
        for i in range(40):
            px = random.uniform(gx + 30, gx + gw - 30)
            py0 = random.uniform(gy + 90, gy + gh - 30)
            swirl = t * 6 * stir
            px2 = px + math.sin(swirl + i) * 40 * stir
            py = lerp(py0, gy + gh - 25 - random.uniform(0, 30), settle)
            circle(ctx, px2, py, 8, (0.35, 0.22, 0.12), b)
        # glass outline
        ctx.set_source_rgba(1, 1, 1, 0.9 * b); ctx.set_line_width(8)
        ctx.move_to(gx, gy); ctx.line_to(gx + 10, gy + gh); ctx.line_to(gx + gw - 10, gy + gh); ctx.line_to(gx + gw, gy); ctx.stroke()
        if stir > 0.05:
            ctx.save(); ctx.translate(gx + gw / 2, gy + 200); ctx.rotate(math.sin(t * 10) * 0.4)
            ctx.set_source_rgb(0.85, 0.85, 0.9); ctx.set_line_width(14); ctx.move_to(0, -250); ctx.line_to(0, 120); ctx.stroke(); ctx.restore()
        if t > lv:
            pop_text(ctx, "LEAVE IT STILL", CX, 1400, 82, t, lv, GREEN)
        elif t > st_:
            pop_text(ctx, "STIRRING = MORE MUD", CX, 1400, 70, t, st_, (1, 0.5, 0.5))

# ---- xiu shen ----
def s_xiu(ctx, t, D):
    sid = "xiu"
    badge(ctx, t, 3, "XIU SHEN", "CULTIVATE YOURSELF")
    ev, wt = kw(sid, "everyone"), kw(sid, "who")
    # center blob with ripples to people around
    blobby(ctx, CX, 950, 120 * eback(prog(t, 0.6, 0.4)), t, TEAL, "happy")
    if t > ev - 0.2 and t < wt:
        for i in range(3):
            q = ((t - ev) * 0.7 + i / 3) % 1
            ctx.set_source_rgba(*YEL, (1 - q) * 0.8); ctx.set_line_width(6)
            ctx.arc(CX, 950, 140 + q * 330, 0, 2 * math.pi); ctx.stroke()
        for k in range(6):
            a = k / 6 * 2 * math.pi + 0.3
            human(ctx, CX + math.cos(a) * 400, 950 + math.sin(a) * 330, 90 * eback(prog(t, ev + k * 0.12, 0.3)), color=[PINK, BLUE, GREEN, YEL, PINK, BLUE][k])
    if t >= wt - 0.3:
        # door closes, spotlight
        p = eio(prog(t, wt - 0.3, 0.8))
        dark = 0.7 * p
        ctx.set_source_rgba(0.02, 0.02, 0.06, dark * 0.8); ctx.paint()
        rg = cairo.RadialGradient(CX, 950, 40, CX, 950, 260); rg.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.35 * p); rg.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
        ctx.set_source(rg); ctx.arc(CX, 950, 260, 0, 2 * math.pi); ctx.fill()
        blobby(ctx, CX, 950, 120, t, TEAL, "happy", look=(math.sin(t * 2), 0))
        # door panel sliding
        dx = lerp(-300, 0, p)
        rrect(ctx, 60 + dx, 640, 220, 380, 14); ctx.set_source_rgba(0.55, 0.35, 0.22, p); ctx.fill()
        circle(ctx, 250 + dx, 830, 12, YEL, p)
        pill(ctx, CX, 1400, 980, 140, DARK, 0.8 * p)
        pop_text(ctx, "WHO ARE YOU WHEN", CX, 1370, 60, t, wt - 0.2, WHITE, stroke=0)
        pop_text(ctx, "NOBODY'S WATCHING?", CX, 1435, 60, t, wt, YEL, stroke=0)

# ---- know = do ----
def s_know(ctx, t, D):
    sid = "know"
    badge(ctx, t, 4, "KNOW = DO", "KNOWING & DOING ARE ONE")
    nv, yt = kw(sid, "never"), kw(sid, "yet")
    # book (know) and running human (do) merge
    m = eio(prog(t, 1.2, 1.2))
    bx = lerp(260, CX - 90, m); hx = lerp(820, CX + 90, m)
    a = prog(t, 0.6, 0.4)
    rrect(ctx, bx - 100, 860, 200, 150, 12); ctx.set_source_rgba(0.95, 0.55, 0.3, a); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(6); ctx.move_to(bx, 860); ctx.line_to(bx, 1010); ctx.stroke()
    text(ctx, "KNOW", bx, 1080, 46, WHITE, alpha=a, stroke=6)
    human(ctx, hx + math.sin(t * 8) * 6 * (t < nv), 930, max(0.5, 150 * a), color=GREEN) if a > 0 else None
    text(ctx, "DO", hx, 1080, 46, WHITE, alpha=a, stroke=6)
    if t > nv - 0.2:
        q = prog(t, nv - 0.2, 0.3)
        # do fades -> know alone with a ?
        pop_text(ctx, "NO DOING?", CX, 1260, 66, t, nv - 0.2, (1, 0.5, 0.5))
    if t > yt - 0.3:
        pill(ctx, CX, 1400, 900, 140, DARK, 0.8 * prog(t, yt - 0.3, 0.2))
        pop_text(ctx, "YOU DON'T KNOW IT YET", CX, 1400, 66, t, yt - 0.3, YEL, stroke=0)

# ---- useless tree ----
def straight_tree(ctx, x, y, s, alpha=1, rot=0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    ctx.rectangle(-12 * s, -260 * s, 24 * s, 260 * s); ctx.set_source_rgba(0.6, 0.4, 0.22, alpha); ctx.fill()
    ctx.move_to(-70 * s, -150 * s); ctx.line_to(0, -380 * s); ctx.line_to(70 * s, -150 * s); ctx.close_path()
    ctx.set_source_rgba(0.25, 0.65, 0.4, alpha); ctx.fill()
    ctx.restore()

def crooked_tree(ctx, x, y, s, t):
    ctx.set_source_rgb(0.5, 0.33, 0.2); ctx.set_line_width(34 * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x, y); ctx.curve_to(x - 60 * s, y - 120 * s, x + 80 * s, y - 180 * s, x - 10 * s, y - 300 * s); ctx.stroke()
    ctx.set_line_width(18 * s)
    ctx.move_to(x + 10 * s, y - 200 * s); ctx.curve_to(x + 90 * s, y - 230 * s, x + 60 * s, y - 300 * s, x + 140 * s, y - 330 * s); ctx.stroke()
    ctx.move_to(x - 20 * s, y - 150 * s); ctx.curve_to(x - 110 * s, y - 180 * s, x - 90 * s, y - 260 * s, x - 160 * s, y - 280 * s); ctx.stroke()
    for dx, dy, r in ((-10, -330, 110), (-140, -290, 80), (140, -340, 85), (60, -400, 80), (-80, -400, 80)):
        circle(ctx, x + dx * s + math.sin(t * 1.5 + dx) * 4, y + dy * s, r * s, (0.25, 0.68, 0.42))

def s_tree(ctx, t, D):
    sid = "tree"
    badge(ctx, t, 5, "THE USELESS TREE")
    cu, cr, kp = kw(sid, "cut"), kw(sid, "crooked"), kw(sid, "keep")
    gy = 1230
    ctx.rectangle(0, gy, W, 40); ctx.set_source_rgba(0.25, 0.55, 0.35, prog(t, 0.3, 0.4)); ctx.fill()
    xs = [150, 330, 750, 930]
    for i, x in enumerate(xs):
        ap = eback(prog(t, 0.6 + i * 0.12, 0.35))
        fall = eio(prog(t, cu + i * 0.2, 0.6))
        gone = 1 - prog(t, cu + i * 0.2 + 0.6, 0.3)
        if ap > 0 and gone > 0:
            straight_tree(ctx, x, gy, 0.9 * ap, alpha=gone, rot=fall * (1.4 if x < CX else -1.4))
        if t > cu + i * 0.2 and gone > 0:
            text(ctx, "CHOP!", x, gy - 400, 40, (1, 0.5, 0.5), alpha=gone, stroke=6)
    if t > 0.5:
        crooked_tree(ctx, CX, gy, 1.0 * eback(prog(t, 0.5, 0.4)), t)
    if t > cr:
        p = eback(prog(t, cr, 0.4))
        blobby(ctx, CX + 150, gy - 60, 70 * p, t, TEAL, sleepy=True, seed=3)
        text(ctx, "z", CX + 220 + math.sin(t * 2) * 10, gy - 170 - (t * 30 % 40), 44, WHITE, alpha=p, stroke=6)
        pop_text(ctx, "IT LIVES ON", CX, 640, 70, t, cr + 0.2, GREEN, end=kp - 0.3)
    if t > kp - 0.2:
        pill(ctx, CX, 1420, 960, 140, DARK, 0.8 * prog(t, kp - 0.2, 0.2))
        pop_text(ctx, "KEEP SOMETHING \"USELESS\"", CX, 1420, 62, t, kp - 0.2, YEL, stroke=0)

# ---- store deeply ----
def s_store(ctx, t, D):
    sid = "store"
    badge(ctx, t, 6, "STORE DEEP", "RELEASE A LITTLE")
    rd, sy, wt = kw(sid, "read"), kw(sid, "say"), kw(sid, "weight")
    jx, jy, jw, jh = CX - 170, 700, 340, 480
    fill = eio(prog(t, 0.6, rd - 0.6 + 1.0))
    a = prog(t, 0.4, 0.3)
    # jar fill
    level = jy + jh - (jh - 40) * fill
    ctx.rectangle(jx + 10, level, jw - 20, jy + jh - level - 10); ctx.set_source_rgba(*YEL, 0.85 * a); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(10)
    rrect(ctx, jx, jy, jw, jh, 30); ctx.stroke()
    rrect(ctx, jx + 40, jy - 40, jw - 80, 50, 12); ctx.set_source_rgba(0.6, 0.45, 0.3, a); ctx.fill()
    # falling ideas
    random.seed(1)
    for i in range(24):
        st = 0.6 + i * 0.12
        q = prog(t, st, 0.6)
        if 0 < q < 1:
            x = jx + 40 + random.uniform(0, jw - 80)
            y = lerp(560, level, q)
            circle(ctx, x, y, 12, random.choice([YEL, PINK, BLUE, GREEN]), 1 - q * 0.3)
    # release: a single glowing drop rises to a speech bubble
    if t > sy - 0.2:
        q = eio(prog(t, sy - 0.2, 0.8))
        x, y = lerp(CX, CX + 300, q), lerp(jy - 60, 640, q)
        rg = cairo.RadialGradient(x, y, 5, x, y, 70); rg.add_color_stop_rgba(0, 1, 0.95, 0.6, 1); rg.add_color_stop_rgba(1, 1, 0.9, 0.4, 0)
        ctx.set_source(rg); ctx.arc(x, y, 70, 0, 2 * math.pi); ctx.fill()
        circle(ctx, x, y, 18, YEL)
    if t > wt - 0.2:
        pill(ctx, CX, 1400, 880, 140, DARK, 0.8 * prog(t, wt - 0.2, 0.2))
        pop_text(ctx, "WORDS WITH WEIGHT", CX, 1400, 72, t, wt - 0.2, YEL, stroke=0)

# ---- flowers have their time ----
def seedling(ctx, x, y, h, wilt=0, alpha=1):
    ctx.set_source_rgba(lerp(0.3, 0.55, wilt), lerp(0.75, 0.45, wilt), lerp(0.4, 0.25, wilt), alpha)
    ctx.set_line_width(8); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    tipx = x + wilt * 40; tipy = y - h * (1 - 0.5 * wilt)
    ctx.move_to(x, y); ctx.curve_to(x, y - h * 0.5, tipx - 10, tipy + 20, tipx, tipy); ctx.stroke()
    for sg in (-1, 1):
        ctx.save(); ctx.translate(tipx, tipy); ctx.rotate(sg * (0.7 + wilt * 0.8) + wilt * 0.6); ctx.scale(1, 0.45)
        ctx.arc(sg * 22, 0, 22, 0, 2 * math.pi); ctx.restore(); ctx.fill()

def flower(ctx, x, y, s, t):
    ctx.set_source_rgb(0.3, 0.75, 0.4); ctx.set_line_width(10); ctx.move_to(x, y); ctx.line_to(x, y - 260 * s); ctx.stroke()
    cx, cy = x, y - 260 * s
    for i in range(8):
        a = i / 8 * 2 * math.pi + t * 0.3
        ctx.save(); ctx.translate(cx + math.cos(a) * 50 * s, cy + math.sin(a) * 50 * s); ctx.rotate(a); ctx.scale(1, 0.55)
        ctx.arc(0, 0, 48 * s, 0, 2 * math.pi); ctx.restore(); ctx.set_source_rgb(*PINK); ctx.fill()
    circle(ctx, cx, cy, 36 * s, YEL)

def s_bloom(ctx, t, D):
    sid = "bloom"
    badge(ctx, t, 7, "FLOWERS HAVE", None)
    pop_text(ctx, "THEIR TIME", CX, 525, 70, t, 0.6, YEL)
    pu, kl, wa, we, wt = kw(sid, "pulled"), kw(sid, "killed"), kw(sid, "water", 0), kw(sid, "weed"), kw(sid, "wait")
    gy = 1180
    ctx.rectangle(80, gy, W - 160, 50); ctx.set_source_rgba(0.45, 0.3, 0.18, prog(t, 0.4, 0.3)); ctx.fill()
    xs = [220, 400, 680, 860]
    if t < wa - 0.3:
        pull = eio(prog(t, pu, 0.8)); wilt = eio(prog(t, kl, 0.8))
        for i, x in enumerate(xs):
            seedling(ctx, x, gy - pull * 60, 90 + pull * 40, wilt, prog(t, 0.6 + i * 0.1, 0.3))
        if t > pu and t < kl + 0.3:
            # hand tugging
            hx = xs[int((t - pu) * 3) % 4]
            circle(ctx, hx, gy - 180 - pull * 60, 40, (1, 0.8, 0.65))
            text(ctx, "GROW!", hx, gy - 260, 44, (1, 0.6, 0.5), stroke=6)
        if t > kl:
            pop_text(ctx, "ALL DEAD", CX, 1370, 80, t, kl + 0.2, (1, 0.45, 0.45))
    else:
        g = eio(prog(t, we, wt - we + 1.0))
        for i, x in enumerate(xs):
            if g < 0.5:
                seedling(ctx, x, gy, 80 + 160 * g, 0)
            else:
                flower(ctx, x, gy, eback(prog(g, 0.5, 0.5)) * 0.9, t)
        if t < we:
            # watering can drops
            for i in range(10):
                q = ((t * 1.5) + i / 10) % 1
                circle(ctx, 300 + i * 50, lerp(800, gy, q), 8, BLUE, 1 - q)
        labs = [("WATER", wa, 220), ("WEED", we, 540), ("WAIT", wt, 860)]
        for w, st, x in labs:
            if t > st - 0.1:
                font(ctx, 52); wd = ctx.text_extents(w).x_advance + 60
                pill(ctx, x, 1400, wd, 100, [BLUE, GREEN, PINK][labs.index((w, st, x))], eback(prog(t, st - 0.1, 0.3)))
                pop_text(ctx, w, x, 1400, 52, t, st - 0.1, WHITE, stroke=0)

# ---- end ----
def s_end(ctx, t, D):
    sid = "end"
    fl = kw(sid, "follow")
    pop_text(ctx, "WHICH SNACK", CX, 360, 100, t, 0.1, WHITE)
    pop_text(ctx, "DID YOU NEED?", CX, 470, 100, t, 0.35, YEL)
    labels = ["YIN & YANG", "WU WEI", "XIU SHEN", "KNOW = DO", "USELESS TREE", "STORE DEEP", "BLOOM TIME"]
    for i, lab in enumerate(labels):
        a = -math.pi / 2 + i / 7 * 2 * math.pi + t * 0.25
        x = CX + math.cos(a) * 290; y = 950 + math.sin(a) * 290
        s = eback(prog(t, 0.3 + i * 0.12, 0.35))
        if s > 0:
            cookie(ctx, x, y, 62 * s)
            text(ctx, str(i + 1), x, y, 46, WHITE, scale=s, stroke=8)
    blobby(ctx, CX, 950, 110 * eback(prog(t, 0.2, 0.4)), t, TEAL, "happy")
    if t >= fl - 0.1:
        pul = 1 + 0.05 * math.sin(t * 8)
        ctx.save(); ctx.translate(CX, 1420); ctx.scale(pul, pul); ctx.translate(-CX, -1420)
        pill(ctx, CX, 1420, 880, 130, (1, 0.25, 0.35), eback(prog(t, fl - 0.1, 0.3)))
        pop_text(ctx, "FOLLOW @thought.snackss", CX, 1420, 52, t, fl - 0.1, WHITE, stroke=0)
        ctx.restore()

SCENES = {"hook": s_hook, "yin": s_yin, "wuwei": s_wuwei, "xiu": s_xiu, "know": s_know,
          "tree": s_tree, "store": s_store, "bloom": s_bloom, "end": s_end}

def credit(ctx, alpha=0.75):
    return

LOGO = cairo.ImageSurface.create_from_png("thought-snackss/branding/logo.png")
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
