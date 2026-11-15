"""Narration-synced slide animation for Atoms to Chips.

Each slide's narration is split into beats (explicit "beats" list, or one beat per sentence of "say").
Every beat is voiced separately, so its start time is known exactly, and things on screen happen
on the beat they are spoken:

    bullets slide in one by one          ("show": n  -> n bullets visible from this beat)
    a pointer glides to a diagram spot   ("point": "<anchor name>" or [fx, fy] in 0..1 of the figure)
    a callout label appears by it        ("label": "short text")
    a diagram wipes in, then slowly zooms
    big numbers count up, quotes appear word by word, compare columns appear in turn
    the background grid drifts so the frame is never frozen

Frames are drawn with Pillow and piped to ffmpeg.
"""
import json, math, os, re, subprocess
from PIL import Image, ImageDraw, ImageFilter

FPS = 30
W, H = 1920, 1080
GAP = 0.22          # silence between beats (s)
TAIL = 0.7          # silence at the end of a slide (s)


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


# ---------- beats ----------
def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", text.strip())
    # merge very short sentences into the previous one, so beats aren't choppy
    out = []
    for p in parts:
        if out and len(p.split()) < 5:
            out[-1] += " " + p
        else:
            out.append(p)
    return out


def beats_of(slide):
    if slide.get("beats"):
        return [dict(b) for b in slide["beats"]]
    return [{"say": s} for s in split_sentences(slide["say"])]


def auto_assign(slide, beats):
    """Fill in reveal steps that the lesson didn't set explicitly."""
    kind = slide.get("kind", "points")
    n = len(beats)
    pts = slide.get("points", [])
    if kind in ("points", "split") and pts and not any("show" in b for b in beats):
        # spread bullet reveals across the beats; the first bullet comes with the first beat
        for k in range(len(pts)):
            i = min(n - 1, math.floor(k * n / len(pts)))
            beats[i]["show"] = max(beats[i].get("show", 0), k + 1)
    shown = 0
    for b in beats:
        shown = max(shown, b.get("show", shown))
        b["show"] = shown
    if kind == "compare" and not any("right" in b for b in beats):
        beats[min(n - 1, max(1, n // 2))]["right"] = True
    return beats


# ---------- layers ----------
class Sprite:
    """An RGBA element cut from a full-frame layer, remembered with its position."""

    def __init__(self, layer):
        bb = layer.getbbox() or (0, 0, 1, 1)
        self.img = layer.crop(bb)
        self.x, self.y = bb[0], bb[1]
        self.alpha = self.img.getchannel("A")

    def draw(self, frame, a=1.0, dx=0, dy=0, dim=1.0):
        if a <= 0.01:
            return
        img = self.img
        if dim < 0.999:
            img = Image.eval(img, lambda v: v)  # copy
            r, g, b, al = img.split()
            r, g, b = (ch.point(lambda v: int(v * dim)) for ch in (r, g, b))
            img = Image.merge("RGBA", (r, g, b, al))
        if a < 0.999:
            img = img.copy()
            img.putalpha(self.alpha.point(lambda v: int(v * a)))
        frame.alpha_composite(img, (int(self.x + dx), int(self.y + dy)))


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


class Renderer:
    def __init__(self, B, lesson, root):
        """B: the build module (fonts, colours, wrap, base drawing helpers)."""
        self.B, self.lesson, self.root = B, lesson, root
        self.A = B.accent(lesson)
        # oversized grid tile that drifts slowly
        g = Image.new("RGB", (W + 160, H + 160), B.NAVY)
        d = ImageDraw.Draw(g)
        for i in range(0, W + 160, 80): d.line([(i, 0), (i, H + 160)], fill=B.NAVY2, width=1)
        for j in range(0, H + 160, 80): d.line([(0, j), (W + 160, j)], fill=B.NAVY2, width=1)
        self.grid = g
        self.pointer_pos = None  # carried across beats within a slide

    # chrome (logo, label, footer) drawn once per slide; progress bar per frame
    def chrome(self):
        B = self.B
        L = layer(); d = ImageDraw.Draw(L)
        B.mark(d, 125, 85, 42, lw=3)
        d.text((190, 85), "ATOMS TO CHIPS", font=B.font("Bold", 28), fill=B.CREAM, anchor="lm")
        d.text((W - 80, 85), self.lesson["label"], font=B.font("Bold", 28), fill=self.A, anchor="rm")
        d.text((80, H - 50), "youtube.com/@AtomsToChips", font=B.font("Medium", 22), fill=B.MUTED, anchor="lm")
        return L

    def background(self, t):
        ox = int((t * 6) % 80); oy = int((t * 3.5) % 80)
        return self.grid.crop((ox, oy, ox + W, oy + H)).convert("RGBA")

    # ---------- element builders ----------
    def heading_sprite(self, text, x, y, maxw, size=84, center=False):
        B = self.B; L = layer(); d = ImageDraw.Draw(L)
        f = B.font("Black", size)
        lines = B.wrap(d, text, f, maxw)
        for ln in lines:
            if center:
                d.text((W // 2, y), ln, font=f, fill=B.CREAM, anchor="mm")
            else:
                d.text((x, y), ln, font=f, fill=B.CREAM, anchor="lm")
            y += int(size * 1.2)
        return Sprite(L), y

    def bullet_sprites(self, pts, x, y, maxw, big=True):
        B = self.B
        fs, lh, gap = (54, 72, 28) if big and len(pts) <= 5 else (44, 58, 18)
        out = []
        for p in pts:
            L = layer(); d = ImageDraw.Draw(L)
            d.ellipse([x + 5, y - 12, x + 29, y + 12], fill=self.A)
            y0 = y
            for ln in B.wrap(d, p, B.font("SemiBold", fs), maxw):
                d.text((x + 60, y), ln, font=B.font("SemiBold", fs), fill=B.CREAM, anchor="lm"); y += lh
            out.append((Sprite(L), y0))
            y += gap
        return out

    def figure_sprite(self, path, box):
        fig = Image.open(path).convert("RGBA")
        bw, bh = box[2] - box[0], box[3] - box[1]
        r = min(bw / fig.width, bh / fig.height)
        fig = fig.resize((int(fig.width * r), int(fig.height * r)), Image.LANCZOS)
        x = box[0] + (bw - fig.width) // 2; y = box[1] + (bh - fig.height) // 2
        anchors = {}
        ap = os.path.splitext(path)[0] + ".anchors.json"
        if os.path.exists(ap):
            anchors = json.load(open(ap))
        return {"img": fig, "x": x, "y": y, "anchors": anchors}

    # ---------- drawing helpers per frame ----------
    def draw_figure(self, frame, F, t_since, zoom):
        """Wipe in left->right over 0.9 s, then hold with a slow zoom about the centre."""
        img = F["img"]
        w, h = img.size
        z = zoom
        if abs(z - 1) > 1e-3:
            img = img.resize((int(w * z), int(h * z)), Image.BILINEAR)
        cx, cy = F["x"] + w / 2, F["y"] + h / 2
        x0, y0 = int(cx - img.width / 2), int(cy - img.height / 2)
        p = ease_out(t_since / 0.9)
        if p < 1:
            cut = int(img.width * p)
            if cut <= 0:
                return
            img = img.crop((0, 0, cut, img.height))
        frame.alpha_composite(img, (x0, y0))

    def fig_point(self, F, key, zoom):
        if isinstance(key, (list, tuple)):
            fx, fy = key
        else:
            fx, fy = F["anchors"].get(key, (None, None))
            if fx is None:
                return None
        w, h = F["img"].size
        cx, cy = F["x"] + w / 2, F["y"] + h / 2
        return (cx + (fx * w - w / 2) * zoom, cy + (fy * h - h / 2) * zoom)

    def draw_pointer(self, frame, pos, t, label=None, label_a=1.0):
        B = self.B
        d = ImageDraw.Draw(frame)
        x, y = pos
        # pulsing ring
        ph = (t * 1.6) % 1.0
        r1 = 26 + 34 * ph
        a1 = int(200 * (1 - ph))
        ring = layer(); rd = ImageDraw.Draw(ring)
        rd.ellipse([x - r1, y - r1, x + r1, y + r1], outline=self.A + (a1,), width=5)
        rd.ellipse([x - 22, y - 22, x + 22, y + 22], outline=self.A + (255,), width=5)
        frame.alpha_composite(ring)
        # arrow cursor, tip at (x+14, y+14) pointing up-left at the spot
        s = 1.0
        tip = (x + 16, y + 16)
        pts = [(0, 0), (0, 44), (11, 34), (19, 52), (27, 48), (19, 31), (34, 31)]
        poly = [(tip[0] + px * s, tip[1] + py * s) for px, py in pts]
        sh = [(px + 3, py + 4) for px, py in poly]
        d.polygon(sh, fill=(0, 0, 0))
        d.polygon(poly, fill=B.CREAM, outline=(20, 20, 20))
        if label and label_a > 0.01:
            f = B.font("Bold", 34)
            tw = d.textlength(label, font=f)
            # prefer below-right of the pointer; otherwise flip, keeping clear of the diagram spot
            lx = x + 70; ly = y + 40
            if lx + tw + 40 > W - 40:
                lx = W - 40 - tw - 40; ly = y + 90
            if ly + 60 > H - 80: ly = y - 120
            box = layer(); bd = ImageDraw.Draw(box)
            bd.rounded_rectangle([lx, ly, lx + tw + 40, ly + 60], radius=14, fill=self.A + (int(235 * label_a),))
            bd.text((lx + 20, ly + 30), label, font=f, fill=B.NAVY + (int(255 * label_a),), anchor="lm")
            frame.alpha_composite(box)

    # ---------- main per-slide render ----------
    def render_slide(self, slide, beats, starts, dur, idx, total, pipe, t_global0):
        B = self.B; A = self.A
        kind = slide.get("kind", "points")
        chrome = self.chrome()
        fig = None
        if slide.get("figure"):
            fp = os.path.join(self.root, slide["figure"])
            box = (1000, 170, 1840, 980) if kind == "split" else (260, 260, 1660, 920)
            fig = self.figure_sprite(fp, box)

        els = {}
        if kind in ("title", "outro"):
            L = layer(); d = ImageDraw.Draw(L)
            d.text((W // 2, 360), self.lesson["series"].upper() if kind == "title" else "COMING UP",
                   font=B.font("Bold", 34), fill=A, anchor="mm")
            els["kicker"] = Sprite(L)
            els["head"], y = self.heading_sprite(slide["head"], 0, 470, 1300, size=110, center=True)
            L = layer(); d = ImageDraw.Draw(L); yy = y + 30
            for ln in B.wrap(d, slide.get("sub", ""), B.font("Medium", 48), 1500):
                d.text((W // 2, yy), ln, font=B.font("Medium", 48), fill=A, anchor="mm"); yy += 62
            els["sub"] = Sprite(L)
        elif kind in ("points", "split"):
            big = kind == "points"
            maxw = 1700 if big else 820
            els["head"], y = self.heading_sprite(slide["head"], 120, 230, maxw, size=84 if big else 72)
            els["rule_y"] = y - 16
            els["bullets"] = self.bullet_sprites(slide.get("points", []), 120, y + 60, 1550 if big else 760, big)
        elif kind == "figure":
            L = layer(); d = ImageDraw.Draw(L)
            d.text((W // 2, 200), slide["head"], font=B.font("Black", 68), fill=B.CREAM, anchor="mm")
            els["head"] = Sprite(L)
            if slide.get("caption"):
                L = layer(); d = ImageDraw.Draw(L)
                d.text((W // 2, 965), slide["caption"], font=B.font("Medium", 38), fill=A, anchor="mm")
                els["caption"] = Sprite(L)
        elif kind == "compare":
            els["head"], y = self.heading_sprite(slide["head"], 120, 230, 1700, size=76)
            els["rule_y"] = y - 16
            for side, x in (("left", 120), ("right", 1000)):
                col = slide.get(side, {})
                L = layer(); d = ImageDraw.Draw(L)
                d.rounded_rectangle([x, y + 50, x + 800, 940], radius=28, outline=A, width=4)
                d.text((x + 50, y + 110), col.get("title", ""), font=B.font("Black", 52), fill=A, anchor="lm")
                yy = y + 200
                for p in col.get("points", []):
                    for ln in B.wrap(d, p, B.font("SemiBold", 40), 690):
                        d.text((x + 50, yy), ln, font=B.font("SemiBold", 40), fill=B.CREAM, anchor="lm"); yy += 54
                    yy += 22
                els[side] = Sprite(L)
        elif kind == "stat":
            L = layer(); d = ImageDraw.Draw(L); y = 640
            for ln in B.wrap(d, slide.get("caption", ""), B.font("SemiBold", 52), 1500):
                d.text((W // 2, y), ln, font=B.font("SemiBold", 52), fill=B.CREAM, anchor="mm"); y += 68
            els["caption"] = Sprite(L)
        elif kind == "quote":
            L = layer(); d = ImageDraw.Draw(L)
            d.text((160, 300), "“", font=B.font("Black", 220), fill=A, anchor="lm")
            els["qmark"] = Sprite(L)
            d0 = ImageDraw.Draw(layer())
            els["qlines"] = B.wrap(d0, slide["quote"], B.font("Bold", 76), 1560)

        # which beat is active at time t (seconds from slide start)
        def beat_at(t):
            i = 0
            for k, s in enumerate(starts):
                if t >= s: i = k
            return i

        nframes = int(round(dur * FPS))
        for fi in range(nframes):
            t = fi / FPS
            tg = t_global0 + t
            frame = self.background(tg)
            frame.alpha_composite(chrome)
            bi = beat_at(t)
            b = beats[bi]
            # progress bar (whole video)
            pd = ImageDraw.Draw(frame)
            pd.rectangle([0, H - 10, W, H], fill=B.NAVY2)
            pd.rectangle([0, H - 10, int(W * (idx + (t / dur)) / total), H], fill=A)

            if kind in ("title", "outro"):
                els["kicker"].draw(frame, ease(t / 0.4), dy=-20 * (1 - ease(t / 0.4)))
                els["head"].draw(frame, ease((t - 0.15) / 0.5), dy=30 * (1 - ease_out((t - 0.15) / 0.5)))
                els["sub"].draw(frame, ease((t - 0.6) / 0.5))
            elif kind in ("points", "split"):
                p = ease_out(t / 0.5)
                els["head"].draw(frame, p, dx=-60 * (1 - p))
                ry = els["rule_y"]
                pd.rectangle([120, ry - 4, 120 + int(180 * ease_out((t - 0.2) / 0.5)), ry + 4], fill=A)
                show = b.get("show", 0)
                for k, (sp, by) in enumerate(els["bullets"]):
                    if k >= show:
                        continue
                    t_in = starts[next(j for j, bb in enumerate(beats) if bb.get("show", 0) > k)]
                    q = ease_out((t - t_in) / 0.45)
                    current = (k == show - 1)
                    sp.draw(frame, q, dx=-50 * (1 - q), dim=1.0 if current else 0.62)
                    if current and q > 0:
                        pd.rectangle([96, by - 26, 104, by + 26], fill=A)
            elif kind == "figure":
                p = ease_out(t / 0.5)
                els["head"].draw(frame, p, dy=-20 * (1 - p))
                if "caption" in els:
                    t_c = starts[min(1, len(starts) - 1)] if len(starts) > 1 else 1.0
                    els["caption"].draw(frame, ease((t - t_c) / 0.5), dy=15 * (1 - ease((t - t_c) / 0.5)))
            elif kind == "compare":
                p = ease_out(t / 0.5)
                els["head"].draw(frame, p, dx=-60 * (1 - p))
                ry = els["rule_y"]
                pd.rectangle([120, ry - 4, 120 + int(180 * ease_out((t - 0.2) / 0.5)), ry + 4], fill=A)
                ql = ease_out((t - 0.3) / 0.6)
                els["left"].draw(frame, ql, dy=40 * (1 - ql))
                t_r = next((starts[j] for j, bb in enumerate(beats) if bb.get("right")), dur * 0.5)
                qr = ease_out((t - t_r) / 0.6)
                els["right"].draw(frame, qr, dy=40 * (1 - qr))
            elif kind == "stat":
                stat = slide["stat"]
                m = re.search(r"\d[\d,]*\.?\d*", stat)
                q = ease_out(t / 1.3)
                if m:
                    num = float(m.group().replace(",", ""))
                    dec = len(m.group().split(".")[1]) if "." in m.group() else 0
                    cur = num * q
                    txt = f"{cur:,.{dec}f}" if "," in m.group() else f"{cur:.{dec}f}"
                    shown = stat[:m.start()] + txt + stat[m.end():]
                else:
                    shown = stat
                sc = 0.85 + 0.15 * q
                f = B.font("Black", int(190 * sc))
                pd.text((W // 2, 470), shown, font=f, fill=A, anchor="mm")
                els["caption"].draw(frame, ease((t - 0.9) / 0.5), dy=20 * (1 - ease((t - 0.9) / 0.5)))
            elif kind == "quote":
                els["qmark"].draw(frame, ease(t / 0.4))
                words_total = sum(len(l.split()) for l in els["qlines"])
                speak_end = max(1.0, (starts[-1] if len(starts) > 1 else 0) + 0.7 * (dur - (starts[-1] if len(starts) > 1 else 0)))
                n_show = int(words_total * clamp((t - 0.2) / (speak_end * 0.8))) + 1
                y = 430; f = B.font("Bold", 76); c = 0
                for ln in els["qlines"]:
                    x = 180
                    for w in ln.split():
                        if c < n_show:
                            pd.text((x, y), w, font=f, fill=B.CREAM, anchor="lm")
                        x += pd.textlength(w + " ", font=f); c += 1
                    y += 98

            # diagram + pointer
            if fig is not None:
                t0 = 0.25
                zoom = 1.0 + 0.035 * ease(t / max(dur, 1))
                self.draw_figure(frame, fig, t - t0, zoom)
                key = b.get("point")
                if key is not None and t - t0 > 0.9:
                    target = self.fig_point(fig, key, zoom)
                    if target:
                        # glide from where the pointer was at the start of this beat
                        t_b = max(starts[bi], t0 + 0.9)
                        prev = None
                        for j in range(bi - 1, -1, -1):
                            if beats[j].get("point") is not None:
                                prev = self.fig_point(fig, beats[j]["point"], zoom); break
                        if prev is None:
                            prev = (target[0] + 220, target[1] + 160)
                        g = ease((t - t_b) / 0.7)
                        pos = (prev[0] + (target[0] - prev[0]) * g, prev[1] + (target[1] - prev[1]) * g)
                        self.draw_pointer(frame, pos, t, b.get("label"), ease((t - t_b - 0.5) / 0.4))

            # soft fade from black at the very start of each slide
            if t < 0.2:
                frame = Image.blend(Image.new("RGBA", (W, H), B.NAVY + (255,)), frame, t / 0.2)
            pipe.write(frame.convert("RGB").tobytes())
