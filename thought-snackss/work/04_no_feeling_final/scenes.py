
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

