"""Narration-synced slide animation for Atoms to Chips.

Each slide's narration is split into beats (an explicit "beats" list, or one beat per sentence of "say").
Each beat is voiced separately, so its start time is known exactly and on-screen events land on the
words. Beat keys (all optional):

    "show": n            bullets visible from this beat (points / split slides)
    "step": k            switch a multi-step diagram to step k (0-based), cross-fading: the diagram
                         builds up piece by piece. Slide "figure" is then a list of PNG paths.
    "point": "<anchor>"  an arrow pointer glides to that spot on the diagram and pulses there
                         (or [fx, fy] as fractions of the figure image)
    "label": "text"      short callout next to the pointer
    "circle": "<anchor>" a ring is drawn around that spot (add "r": radius in px, default 70)
    "zoom": 1.8          camera pushes into the diagram, centred on this beat's "point" or
                         "zoom_on" anchor. It stays zoomed until a later beat sets "zoom": 1.
    "flow": ["a", "b", ...]  glowing particles stream along the path through these anchors
                         (electrons moving, current flowing, gas entering a chamber...)
    "define": {"term": "Bandgap", "meaning": "the energy jump an electron needs to move"}
                         a jargon-buster card slides in at the bottom right
    "right": true        compare slides: the right column appears now
    "reveal": true       quiz slides: the correct answer lights up now

Other motion is automatic: word-by-word captions at the bottom, a slide-in transition for each
slide, a drifting background grid, diagram wipe-in and slow drift, count-up numbers, quotes appearing
word by word.
Frames are drawn with Pillow and piped to ffmpeg.
"""
import json, math, os, re
from PIL import Image, ImageDraw

FPS = 30
W, H = 1920, 1080
GAP = 0.22          # silence between beats (s)
TAIL = 0.7          # silence at the end of a slide (s)
CAPTIONS = True
CAP_Y = 1018        # caption baseline centre


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    """Overshoot a little, then settle (for 'pop' entrances)."""
    x = clamp(x); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


# ---------- beats ----------
def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", text.strip())
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
    """Fill in reveal steps that the lesson didn't set explicitly, and carry state forward."""
    kind = slide.get("kind", "points")
    n = len(beats)
    pts = slide.get("points", [])
    if kind in ("points", "split") and pts and not any("show" in b for b in beats):
        for k in range(len(pts)):
            i = min(n - 1, math.floor(k * n / len(pts)))
            beats[i]["show"] = max(beats[i].get("show", 0), k + 1)
    shown = 0; step = 0; zoom = 1.0; zc = None
    for b in beats:
        shown = max(shown, b.get("show", shown)); b["show"] = shown
        step = b.get("step", step); b["step"] = step
        if "zoom" in b:
            zoom = float(b["zoom"]); zc = b.get("zoom_on", b.get("point", zc))
        b["_zoom"] = zoom; b["_zc"] = zc
    if kind == "compare" and not any("right" in b for b in beats):
        beats[min(n - 1, max(1, n // 2))]["right"] = True
    if kind == "quiz" and not any("reveal" in b for b in beats):
        beats[-1]["reveal"] = True
    return beats


def word_times(text, t0, t1):
    """Approximate when each word is spoken inside a beat (by character share)."""
    words = text.split()
    if not words:
        return []
    lens = [len(w) + 1 for w in words]
    tot = sum(lens); span = max(0.3, (t1 - t0))
    out, acc = [], 0
    for w, l in zip(words, lens):
        out.append((w, t0 + span * acc / tot)); acc += l
    return out


# ---------- layers ----------
class Sprite:
    """An RGBA element cut from a full-frame layer, remembered with its position."""

    def __init__(self, layer):
        bb = layer.getbbox() or (0, 0, 1, 1)
        self.img = layer.crop(bb)
        self.x, self.y = bb[0], bb[1]
        self.alpha = self.img.getchannel("A")
        self._dim = None

    def draw(self, frame, a=1.0, dx=0, dy=0, dim=1.0, scale=1.0):
        if a <= 0.01:
            return
        img = self.img
        if dim < 0.999:
            if self._dim is None or self._dim[0] != dim:
                r, g, b, al = img.split()
                r, g, b = (ch.point(lambda v: int(v * dim)) for ch in (r, g, b))
                self._dim = (dim, Image.merge("RGBA", (r, g, b, al)))
            img = self._dim[1]
        x, y = self.x, self.y
        if abs(scale - 1) > 0.005:
            w, h = img.size
            img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BILINEAR)
            x -= (img.width - w) / 2; y -= (img.height - h) / 2
        if a < 0.999:
            img = img.copy()
            img.putalpha(img.getchannel("A").point(lambda v: int(v * a)))
        frame.alpha_composite(img, (int(x + dx), int(y + dy)))


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


class Renderer:
    def __init__(self, B, lesson, root):
        """B: the build module (fonts, colours, wrap, base drawing helpers)."""
        self.B, self.lesson, self.root = B, lesson, root
        self.A = tuple(B.accent(lesson))
        g = Image.new("RGB", (W + 160, H + 160), B.NAVY)
        d = ImageDraw.Draw(g)
        for i in range(0, W + 160, 80): d.line([(i, 0), (i, H + 160)], fill=B.NAVY2, width=1)
        for j in range(0, H + 160, 80): d.line([(0, j), (W + 160, j)], fill=B.NAVY2, width=1)
        self.grid = g

    def chrome(self):
        B = self.B
        L = layer(); d = ImageDraw.Draw(L)
        B.mark(d, 125, 85, 42, lw=3)
        d.text((190, 85), "ATOMS TO CHIPS", font=B.font("Bold", 28), fill=B.CREAM, anchor="lm")
        d.text((W - 80, 85), self.lesson["label"], font=B.font("Bold", 28), fill=self.A, anchor="rm")
        return L

    def background(self, t):
        ox = int((t * 6) % 80); oy = int((t * 3.5) % 80)
        return self.grid.crop((ox, oy, ox + W, oy + H)).convert("RGBA")

    # ---------- element builders ----------
    def heading_sprite(self, text, x, y, maxw, size=84, center=False):
        B = self.B; L = layer(); d = ImageDraw.Draw(L)
        f = B.font("Black", size)
        for ln in B.wrap(d, text, f, maxw):
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

    def figure_set(self, paths, box):
        """Load one or more diagram steps, all scaled the same way into box."""
        imgs = [Image.open(p).convert("RGBA") for p in paths]
        bw, bh = box[2] - box[0], box[3] - box[1]
        r = min(bw / imgs[0].width, bh / imgs[0].height)
        imgs = [im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS) for im in imgs]
        w, h = imgs[0].size
        anchors = {}
        for p in paths:  # later steps may add anchors
            ap = os.path.splitext(p)[0] + ".anchors.json"
            if os.path.exists(ap):
                anchors.update(json.load(open(ap)))
        return {"imgs": imgs, "box": box, "ox": (bw - w) // 2, "oy": (bh - h) // 2, "w": w, "h": h,
                "anchors": anchors}

    # figure-local px -> frame px under the current camera
    def cam(self, F, z, zc_local):
        bw, bh = F["box"][2] - F["box"][0], F["box"][3] - F["box"][1]
        cx, cy = bw / 2, bh / 2
        if zc_local is None:
            px, py = F["ox"] + F["w"] / 2, F["oy"] + F["h"] / 2
        else:
            px, py = F["ox"] + zc_local[0], F["oy"] + zc_local[1]
        k = clamp((z - 1) / 0.8)  # how far to slide the zoom centre toward the box centre
        sx, sy = px + (cx - px) * k, py + (cy - py) * k

        def f(q):  # q in figure-local px
            qx, qy = F["ox"] + q[0], F["oy"] + q[1]
            return (F["box"][0] + sx + (qx - px) * z, F["box"][1] + sy + (qy - py) * z)
        return f

    def local(self, F, key):
        if key is None:
            return None
        if isinstance(key, (list, tuple)):
            fx, fy = key
        else:
            v = F["anchors"].get(key)
            if v is None:
                return None
            fx, fy = v
        return (fx * F["w"], fy * F["h"])

    def draw_figure(self, frame, F, t_since, step_a, step_b, mix, z, zc_local):
        """Wipe in (first 0.9 s), cross-fade between build steps, camera zoom, clipped to its box."""
        bw, bh = F["box"][2] - F["box"][0], F["box"][3] - F["box"][1]
        img = F["imgs"][step_b]
        if mix < 0.999 and step_a != step_b:
            img = Image.blend(F["imgs"][step_a], F["imgs"][step_b], mix)
        to = self.cam(F, z, zc_local)
        x0, y0 = to((0, 0))
        if abs(z - 1) > 1e-3:
            img = img.resize((max(1, int(F["w"] * z)), max(1, int(F["h"] * z))), Image.BILINEAR)
        p = ease_out(t_since / 0.9)
        if p <= 0:
            return
        if p < 1:
            img = img.crop((0, 0, max(1, int(img.width * p)), img.height))
        canvas = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        canvas.paste(img, (int(x0 - F["box"][0]), int(y0 - F["box"][1])), img)
        frame.alpha_composite(canvas, (F["box"][0], F["box"][1]))

    def draw_pointer(self, frame, pos, t, label=None, label_a=1.0):
        B = self.B
        d = ImageDraw.Draw(frame)
        x, y = pos
        ph = (t * 1.6) % 1.0
        r1 = 26 + 34 * ph; a1 = int(200 * (1 - ph))
        ring = layer(); rd = ImageDraw.Draw(ring)
        rd.ellipse([x - r1, y - r1, x + r1, y + r1], outline=self.A + (a1,), width=5)
        rd.ellipse([x - 22, y - 22, x + 22, y + 22], outline=self.A + (255,), width=5)
        frame.alpha_composite(ring)
        tip = (x + 16, y + 16)
        pts = [(0, 0), (0, 44), (11, 34), (19, 52), (27, 48), (19, 31), (34, 31)]
        poly = [(tip[0] + px, tip[1] + py) for px, py in pts]
        d.polygon([(px + 3, py + 4) for px, py in poly], fill=(0, 0, 0))
        d.polygon(poly, fill=B.CREAM, outline=(20, 20, 20))
        if label and label_a > 0.01:
            f = B.font("Bold", 34)
            tw = d.textlength(label, font=f)
            lx = x + 70; ly = y + 40
            if lx + tw + 40 > W - 40:
                lx = W - 40 - tw - 40; ly = y + 90
            if ly + 60 > 960: ly = y - 120
            box = layer(); bd = ImageDraw.Draw(box)
            bd.rounded_rectangle([lx, ly, lx + tw + 40, ly + 60], radius=14, fill=self.A + (int(235 * label_a),))
            bd.text((lx + 20, ly + 30), label, font=f, fill=tuple(B.NAVY) + (int(255 * label_a),), anchor="lm")
            frame.alpha_composite(box)

    def draw_circle(self, frame, pos, r, p):
        """Ring that draws itself on (p from 0 to 1)."""
        if p <= 0:
            return
        L = layer(); d = ImageDraw.Draw(L)
        x, y = pos
        d.arc([x - r, y - r * 0.8, x + r, y + r * 0.8], -90, -90 + 360 * p, fill=(255, 210, 90, 255), width=7)
        frame.alpha_composite(L)

    def draw_flow(self, frame, path, t, a=1.0):
        """Particles streaming along a polyline."""
        if len(path) < 2 or a <= 0.01:
            return
        segs = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        lens = [math.dist(p, q) for p, q in segs]
        tot = sum(lens) or 1
        L = layer(); d = ImageDraw.Draw(L)
        for p, q in segs:  # faint guide line
            d.line([p, q], fill=self.A + (int(70 * a),), width=4)
        n = max(5, int(tot / 70))
        speed = 0.45  # path lengths per second
        for k in range(n):
            u = ((t * speed) + k / n) % 1.0
            s = u * tot
            for (p, q), l in zip(segs, lens):
                if s <= l:
                    f = s / l if l else 0
                    x = p[0] + (q[0] - p[0]) * f; y = p[1] + (q[1] - p[1]) * f
                    break
                s -= l
            fade = min(1, u * 6, (1 - u) * 6)
            al = int(255 * a * fade)
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=self.A + (int(al * 0.25),))
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(255, 225, 120, al))
        frame.alpha_composite(L)

    def draw_define(self, frame, term, meaning, p, left=False):
        """Jargon-buster card sliding up at the bottom right."""
        if p <= 0.01:
            return
        B = self.B
        L = layer(); d = ImageDraw.Draw(L)
        f1 = B.font("Black", 34); f2 = B.font("Medium", 30)
        lines = B.wrap(d, meaning, f2, 560)
        h = 70 + 40 * len(lines) + 20
        x0 = 120 if left else W - 680; y1 = 950
        y0 = y1 - h + int(60 * (1 - ease_out(p)))
        al = int(245 * ease(p))
        d.rounded_rectangle([x0, y0, x0 + 620, y0 + h], radius=20, fill=(14, 26, 44, al), outline=self.A + (al,), width=3)
        d.text((x0 + 28, y0 + 38), "JARGON BUSTER", font=B.font("Bold", 20), fill=self.A + (al,), anchor="lm")
        d.text((x0 + 230, y0 + 38), term, font=f1, fill=tuple(B.CREAM) + (al,), anchor="lm")
        yy = y0 + 88
        for ln in lines:
            d.text((x0 + 28, yy), ln, font=f2, fill=tuple(B.CREAM) + (al,), anchor="lm"); yy += 40
        frame.alpha_composite(L)

    def draw_captions(self, frame, words, t):
        """Show the current phrase (up to ~7 words), highlighting the word being spoken."""
        if not words:
            return
        B = self.B
        i = 0
        for k, (_, ts) in enumerate(words):
            if ts <= t: i = k
        if t < words[0][1] - 0.1 or t > words[-1][1] + 1.2:
            return
        start = (i // 7) * 7
        chunk = words[start:start + 7]
        f = B.font("Bold", 40)
        d = ImageDraw.Draw(frame)
        txt = " ".join(w for w, _ in chunk)
        tw = d.textlength(txt, font=f)
        L = layer(); ld = ImageDraw.Draw(L)
        ld.rounded_rectangle([W / 2 - tw / 2 - 26, CAP_Y - 34, W / 2 + tw / 2 + 26, CAP_Y + 34], radius=16, fill=(0, 0, 0, 170))
        frame.alpha_composite(L)
        x = W / 2 - tw / 2
        for k, (w, _) in enumerate(chunk):
            cur = (start + k == i)
            d.text((x, CAP_Y), w, font=f, fill=self.A if cur else tuple(B.CREAM), anchor="lm")
            x += d.textlength(w + " ", font=f)

    # ---------- main per-slide render ----------
    def render_slide(self, slide, beats, starts, dur, idx, total, pipe, t_global0, beat_durs=None):
        B = self.B; A = self.A
        kind = slide.get("kind", "points")
        chrome = self.chrome()
        F = None
        if slide.get("figure"):
            paths = slide["figure"] if isinstance(slide["figure"], list) else [slide["figure"]]
            paths = [os.path.join(self.root, p) for p in paths]
            box = (1000, 170, 1840, 940) if kind == "split" else (240, 250, 1680, 900)
            F = self.figure_set(paths, box)

        # captions: word timing per beat
        words = []
        for k, b in enumerate(beats):
            t1 = starts[k] + (beat_durs[k] if beat_durs else ((starts[k + 1] - GAP) if k + 1 < len(starts) else dur - TAIL))
            words += word_times(b["say"], starts[k], t1)

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
            els["head"], y = self.heading_sprite(slide["head"], 120, 230, 1700 if big else 820, size=84 if big else 72)
            els["rule_y"] = y - 16
            els["bullets"] = self.bullet_sprites(slide.get("points", []), 120, y + 60, 1550 if big else 760, big)
        elif kind == "figure":
            L = layer(); d = ImageDraw.Draw(L)
            d.text((W // 2, 195), slide["head"], font=B.font("Black", 68), fill=B.CREAM, anchor="mm")
            els["head"] = Sprite(L)
            if slide.get("caption"):
                L = layer(); d = ImageDraw.Draw(L)
                d.text((W // 2, 935), slide["caption"], font=B.font("Medium", 36), fill=A, anchor="mm")
                els["caption"] = Sprite(L)
        elif kind == "compare":
            els["head"], y = self.heading_sprite(slide["head"], 120, 230, 1700, size=76)
            els["rule_y"] = y - 16
            for side, x in (("left", 120), ("right", 1000)):
                col = slide.get(side, {})
                L = layer(); d = ImageDraw.Draw(L)
                d.rounded_rectangle([x, y + 40, x + 800, 930], radius=28, outline=A, width=4)
                d.text((x + 50, y + 100), col.get("title", ""), font=B.font("Black", 52), fill=A, anchor="lm")
                yy = y + 190
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
            els["qlines"] = B.wrap(ImageDraw.Draw(layer()), slide["quote"], B.font("Bold", 76), 1560)
        elif kind == "quiz":
            L = layer(); d = ImageDraw.Draw(L)
            d.text((W // 2, 210), "QUICK CHECK", font=B.font("Bold", 34), fill=A, anchor="mm")
            y = 300
            for ln in B.wrap(d, slide["question"], B.font("Black", 64), 1600):
                d.text((W // 2, y), ln, font=B.font("Black", 64), fill=B.CREAM, anchor="mm"); y += 78
            els["q"] = Sprite(L)
            els["opts"] = []
            oy = max(y + 50, 470)
            for k, o in enumerate(slide["options"]):
                Lo = layer(); do = ImageDraw.Draw(Lo)
                do.rounded_rectangle([360, oy, 1560, oy + 110], radius=24, fill=(18, 32, 56, 255), outline=tuple(B.MUTED) + (255,), width=3)
                do.text((420, oy + 55), "ABCD"[k], font=B.font("Black", 44), fill=A, anchor="mm")
                do.text((480, oy + 55), o, font=B.font("SemiBold", 44), fill=B.CREAM, anchor="lm")
                Lc = layer(); dc = ImageDraw.Draw(Lc)
                dc.rounded_rectangle([360, oy, 1560, oy + 110], radius=24, fill=A + (255,))
                dc.text((420, oy + 55), "ABCD"[k], font=B.font("Black", 44), fill=B.NAVY, anchor="mm")
                dc.text((480, oy + 55), o, font=B.font("Bold", 44), fill=B.NAVY, anchor="lm")
                els["opts"].append((Sprite(Lo), Sprite(Lc)))
                oy += 135

        def beat_at(t):
            i = 0
            for k, s in enumerate(starts):
                if t >= s: i = k
            return i

        def first_beat(pred):
            return next((starts[j] for j, bb in enumerate(beats) if pred(bb)), None)

        nframes = int(round(dur * FPS))
        for fi in range(nframes):
            t = fi / FPS
            frame = self.background(t_global0 + t)
            frame.alpha_composite(chrome)
            bi = beat_at(t); b = beats[bi]
            tb = t - starts[bi]  # time inside this beat
            pd = ImageDraw.Draw(frame)

            if kind in ("title", "outro"):
                els["kicker"].draw(frame, ease(t / 0.4), dy=-20 * (1 - ease(t / 0.4)))
                els["head"].draw(frame, ease((t - 0.15) / 0.5), scale=0.9 + 0.1 * ease_back((t - 0.15) / 0.6))
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
                    t_in = first_beat(lambda bb: bb.get("show", 0) > k) or 0
                    q = (t - t_in) / 0.45
                    current = (k == show - 1)
                    sp.draw(frame, ease_out(q), dx=-50 * (1 - ease_out(q)), dim=1.0 if current else 0.6,
                            scale=0.92 + 0.08 * ease_back(q) if q < 1 else 1.0)
                    if current and q > 0:
                        pd.rectangle([96, by - 26, 104, by + 26], fill=A)
            elif kind == "figure":
                p = ease_out(t / 0.5)
                els["head"].draw(frame, p, dy=-20 * (1 - p))
                if "caption" in els:
                    t_c = starts[min(1, len(starts) - 1)] if len(starts) > 1 else 1.0
                    q = ease((t - t_c) / 0.5)
                    els["caption"].draw(frame, q, dy=15 * (1 - q))
            elif kind == "compare":
                p = ease_out(t / 0.5)
                els["head"].draw(frame, p, dx=-60 * (1 - p))
                ry = els["rule_y"]
                pd.rectangle([120, ry - 4, 120 + int(180 * ease_out((t - 0.2) / 0.5)), ry + 4], fill=A)
                ql = (t - 0.3) / 0.6
                els["left"].draw(frame, ease_out(ql), dy=40 * (1 - ease_out(ql)))
                t_r = first_beat(lambda bb: bb.get("right")) or dur * 0.5
                qr = (t - t_r) / 0.6
                els["right"].draw(frame, ease_out(qr), dx=60 * (1 - ease_out(qr)))
            elif kind == "stat":
                stat = slide["stat"]
                m = re.search(r"\d[\d,]*\.?\d*", stat)
                q = ease_out(t / 1.3)
                if m:
                    num = float(m.group().replace(",", ""))
                    dec = len(m.group().split(".")[1]) if "." in m.group() else 0
                    txt = f"{num * q:,.{dec}f}" if "," in m.group() else f"{num * q:.{dec}f}"
                    shown = stat[:m.start()] + txt + stat[m.end():]
                else:
                    shown = stat
                sc = 0.8 + 0.2 * ease_back(t / 0.9)
                pd.text((W // 2, 470), shown, font=B.font("Black", max(20, int(190 * sc))), fill=A, anchor="mm")
                els["caption"].draw(frame, ease((t - 0.9) / 0.5), dy=20 * (1 - ease((t - 0.9) / 0.5)))
            elif kind == "quote":
                els["qmark"].draw(frame, ease(t / 0.4), scale=0.7 + 0.3 * ease_back(t / 0.5))
                words_total = sum(len(l.split()) for l in els["qlines"])
                speak_end = max(1.0, dur - TAIL)
                n_show = int(words_total * clamp((t - 0.2) / (speak_end * 0.85))) + 1
                y = 430; f = B.font("Bold", 76); c = 0
                for ln in els["qlines"]:
                    x = 180
                    for w in ln.split():
                        if c < n_show:
                            pd.text((x, y), w, font=f, fill=B.CREAM, anchor="lm")
                        x += pd.textlength(w + " ", font=f); c += 1
                    y += 98
            elif kind == "quiz":
                els["q"].draw(frame, ease(t / 0.5), scale=0.92 + 0.08 * ease_back(t / 0.6))
                t_rev = first_beat(lambda bb: bb.get("reveal"))
                for k, (so, sc_) in enumerate(els["opts"]):
                    q = (t - 0.5 - 0.25 * k) / 0.45
                    so.draw(frame, ease_out(q), dx=-80 * (1 - ease_out(q)))
                    if t_rev is not None and t >= t_rev:
                        r = (t - t_rev) / 0.4
                        if k == slide["answer"]:
                            sc_.draw(frame, ease(r), scale=1 + 0.04 * math.sin(clamp(r) * math.pi))
                        else:
                            so.draw(frame, 0.55 * ease(r), dim=0.3)
                if t_rev is None or t < t_rev:  # countdown ring while the viewer thinks
                    tt = t_rev if t_rev else dur
                    left = max(0, tt - t)
                    pd.text((1700, 210), f"{int(math.ceil(left))}", font=B.font("Black", 48), fill=A, anchor="mm")

            # diagram, camera, pointer, circles, flows
            if F is not None:
                t0 = 0.25
                # build step cross-fade
                st = b.get("step", 0)
                prev_st = beats[bi - 1].get("step", 0) if bi > 0 else st
                mix = ease(tb / 0.6) if st != prev_st else 1.0
                # camera: interpolate from the previous beat's zoom to this beat's
                z1 = b["_zoom"]; c1 = self.local(F, b["_zc"])
                z0 = beats[bi - 1]["_zoom"] if bi > 0 else 1.0
                c0 = self.local(F, beats[bi - 1]["_zc"]) if bi > 0 else None
                g = ease(tb / 0.9)
                z = z0 + (z1 - z0) * g
                if c0 is None: c0 = c1
                if c1 is None: c1 = c0
                zc = None if c1 is None else (c0[0] + (c1[0] - c0[0]) * g, c0[1] + (c1[1] - c0[1]) * g)
                z *= 1.0 + 0.03 * ease(t / max(dur, 1))  # slow drift
                self.draw_figure(frame, F, t - t0, prev_st if st != prev_st else st, st, mix, z, zc)
                to = self.cam(F, z, zc)
                ready = t - t0 > 0.9
                if ready and b.get("flow"):
                    path = [self.local(F, k) for k in b["flow"]]
                    if all(path):
                        self.draw_flow(frame, [to(p) for p in path], t, ease(tb / 0.5))
                if ready and b.get("circle") is not None:
                    c = self.local(F, b["circle"])
                    if c:
                        self.draw_circle(frame, to(c), b.get("r", 70) * z, ease_out(tb / 0.7))
                if ready and b.get("point") is not None:
                    tgt = self.local(F, b["point"])
                    if tgt:
                        prev = None
                        for j in range(bi - 1, -1, -1):
                            if beats[j].get("point") is not None:
                                prev = self.local(F, beats[j]["point"]); break
                        tgt_s = to(tgt)
                        prev_s = to(prev) if prev else (tgt_s[0] + 220, tgt_s[1] + 160)
                        tb2 = t - max(starts[bi], t0 + 0.9)
                        g2 = ease(tb2 / 0.7)
                        pos = (prev_s[0] + (tgt_s[0] - prev_s[0]) * g2, prev_s[1] + (tgt_s[1] - prev_s[1]) * g2)
                        self.draw_pointer(frame, pos, t, b.get("label"), ease((tb2 - 0.5) / 0.4))

            # jargon buster
            if b.get("define"):
                dd = b["define"]
                bend = starts[bi + 1] if bi + 1 < len(starts) else dur
                p_in = ease_out(tb / 0.5); p_out = 1 - ease((t - (bend - 0.4)) / 0.4)
                self.draw_define(frame, dd.get("term", ""), dd.get("meaning", ""), min(p_in, p_out), left=(kind == "split"))

            if CAPTIONS:
                self.draw_captions(frame, words, t)

            # progress bar (whole video)
            pd = ImageDraw.Draw(frame)
            pd.rectangle([0, H - 8, W, H], fill=B.NAVY2)
            pd.rectangle([0, H - 8, int(W * (idx + (t / dur)) / total), H], fill=A)

            # slide-in transition: content arrives from the right with a quick fade
            if t < 0.35:
                q = ease_out(t / 0.35)
                bg = self.background(t_global0 + t)
                shifted = Image.new("RGBA", (W, H)); shifted.alpha_composite(bg)
                shifted.alpha_composite(frame.crop((0, 0, W - int(120 * (1 - q)), H)), (int(120 * (1 - q)), 0))
                frame = Image.blend(bg, shifted, q)
            pipe.write(frame.convert("RGB").tobytes())
