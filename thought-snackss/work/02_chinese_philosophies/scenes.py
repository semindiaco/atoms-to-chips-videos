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
        ctx.set_source_rgba(0.02, 0.02, 0.06, dark); ctx.rectangle(0, 600, W, 800); ctx.fill()
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
    human(ctx, hx + math.sin(t * 8) * 6 * (t < nv), 930, 150 * a, color=GREEN)
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
        x, y = lerp(CX, CX + 250, q), lerp(jy - 60, 560, q)
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

LOGO = cairo.ImageSurface.create_from_png("/mnt/user-data/outputs/ts_bust_terracotta.png")
def watermark(ctx):
    d = 92; x, y = 90, 105
    ctx.save(); ctx.arc(x + d / 2, y + d / 2, d / 2, 0, 2 * math.pi); ctx.clip()
    ctx.translate(x, y); ctx.scale(d / 1080, d / 1080); ctx.set_source_surface(LOGO, 0, 0); ctx.paint(); ctx.restore()
    ctx.arc(x + d / 2, y + d / 2, d / 2, 0, 2 * math.pi); ctx.set_source_rgba(0.99, 0.8, 0.42, 0.9); ctx.set_line_width(4); ctx.stroke()
    font(ctx, 36); ctx.move_to(x + d + 20, y + d / 2 + 13); ctx.text_path("@thought.snackss")
    ctx.set_source_rgba(0.04, 0.03, 0.12, 0.8); ctx.set_line_width(6); ctx.stroke_preserve(); ctx.set_source_rgb(0.97, 0.93, 0.85); ctx.fill()

