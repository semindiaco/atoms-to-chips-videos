#!/usr/bin/env python3
"""Atoms to Chips video builder: lesson JSON -> MP4 + thumbnail + description.
Usage: python3 tools/build.py lessons/dayNN_slug.json out/dayNN
If lessons/dayNN_slug_figs.py exists it is run first (from the repo root) to draw the diagrams.
"""
import json, os, subprocess, sys, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style import BG as NAVY, GRID as NAVY2, CYAN as TEAL, AMBER as GOLD, WHITE as CREAM, MUTED, mark, font as _f
from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/opentype/inter/"
W, H = 1920, 1080


def font(w, s):
    return ImageFont.truetype(F + f"Inter-{w}.otf", s)


def wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def bars(d, x0, y0, w, h, n=5, color=GOLD):
    gap = w * 0.06; bw = (w - gap * (n - 1)) / n
    for i in range(n):
        bh = h * (1.55 ** i) / (1.55 ** (n - 1))
        x = x0 + i * (bw + gap)
        d.rounded_rectangle([x, y0 + h - bh, x + bw, y0 + h], radius=bw * 0.18, fill=color)


SERIES_ACCENT = {  # one accent colour per playlist, so episodes don't all look the same
    "semiconductor basics": (56, 205, 230), "from sand to wafer": (255, 176, 59),
    "inside the cleanroom": (46, 196, 160), "how chips are made": (167, 139, 250),
    "vacuum & equipment": (255, 107, 107), "packaging & test": (120, 200, 120),
    "industry & careers": (255, 205, 90),
}


def accent(lesson):
    return SERIES_ACCENT.get(lesson.get("series", "").lower(), GOLD)


def base(lesson, idx, total):
    A = accent(lesson)
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    for i in range(0, W, 80): d.line([(i, 0), (i, H)], fill=NAVY2, width=1)
    for j in range(0, H, 80): d.line([(0, j), (W, j)], fill=NAVY2, width=1)
    mark(d, 125, 85, 42, lw=3)
    d.text((190, 85), "ATOMS TO CHIPS", font=font("Bold", 28), fill=CREAM, anchor="lm")
    d.text((W - 80, 85), lesson["label"], font=font("Bold", 28), fill=A, anchor="rm")
    d.rectangle([0, H - 10, W, H], fill=NAVY2)
    d.rectangle([0, H - 10, int(W * (idx + 1) / total), H], fill=A)
    d.text((80, H - 50), "youtube.com/@AtomsToChips", font=font("Medium", 22), fill=MUTED, anchor="lm")
    return im, d


def heading(d, text, x, y, maxw, A, size=84):
    for ln in wrap(d, text, font("Black", size), maxw):
        d.text((x, y), ln, font=font("Black", size), fill=CREAM, anchor="lm"); y += int(size * 1.2)
    d.rectangle([x, y - 20, x + 180, y - 12], fill=A)
    return y + 60


def bullets(d, pts, x, y, maxw, A, big=True):
    fs, lh, gap = (54, 72, 28) if big and len(pts) <= 5 else (44, 58, 18)
    for p in pts:
        d.ellipse([x + 5, y - 12, x + 29, y + 12], fill=A)
        for ln in wrap(d, p, font("SemiBold", fs), maxw):
            d.text((x + 60, y), ln, font=font("SemiBold", fs), fill=CREAM, anchor="lm"); y += lh
        y += gap
    return y


def paste_fig(im, path, box):
    """Fit an image into box (x0, y0, x1, y1), centred."""
    fig = Image.open(path).convert("RGBA")
    bw, bh = box[2] - box[0], box[3] - box[1]
    r = min(bw / fig.width, bh / fig.height)
    fig = fig.resize((int(fig.width * r), int(fig.height * r)), Image.LANCZOS)
    im.paste(fig, (box[0] + (bw - fig.width) // 2, box[1] + (bh - fig.height) // 2), fig)


def slide_img(lesson, s, idx, total, path, root="."):
    """Slide kinds:
    title / outro : head + sub, centred
    points        : head + 3-5 bullets (default)
    split         : head + bullets on the left, figure on the right   ("figure": path)
    figure        : head + one large figure + optional caption        ("figure", "caption")
    compare       : head + two columns  ("left": {"title","points"}, "right": {...})
    stat          : one big number/phrase + caption  ("stat", "caption")
    quote         : one key sentence in large type ("quote")
    """
    im, d = base(lesson, idx, total); A = accent(lesson)
    kind = s.get("kind", "points")
    fig = os.path.join(root, s["figure"]) if s.get("figure") else None
    if kind in ("title", "outro"):
        d.text((W // 2, 360), lesson["series"].upper() if kind == "title" else "COMING UP", font=font("Bold", 34), fill=A, anchor="mm")
        y = 470
        for ln in wrap(d, s["head"], font("Black", 110), 1300):
            d.text((W // 2, y), ln, font=font("Black", 110), fill=CREAM, anchor="mm"); y += 130
        for ln in wrap(d, s.get("sub", ""), font("Medium", 48), 1500):
            d.text((W // 2, y + 30), ln, font=font("Medium", 48), fill=A, anchor="mm"); y += 62
    elif kind == "split":
        y = heading(d, s["head"], 120, 230, 820, A, size=72)
        bullets(d, s.get("points", []), 120, y, 760, A, big=False)
        if fig: paste_fig(im, fig, (1000, 170, 1840, 980))
    elif kind == "figure":
        d.text((W // 2, 200), s["head"], font=font("Black", 68), fill=CREAM, anchor="mm")
        if fig: paste_fig(im, fig, (260, 260, 1660, 920))
        if s.get("caption"):
            d.text((W // 2, 965), s["caption"], font=font("Medium", 38), fill=A, anchor="mm")
    elif kind == "compare":
        y = heading(d, s["head"], 120, 230, 1700, A, size=76)
        for col, x in ((s.get("left", {}), 120), (s.get("right", {}), 1000)):
            d.rounded_rectangle([x, y - 10, x + 800, 940], radius=28, outline=A, width=4)
            d.text((x + 50, y + 50), col.get("title", ""), font=font("Black", 52), fill=A, anchor="lm")
            yy = y + 140
            for p in col.get("points", []):
                for ln in wrap(d, p, font("SemiBold", 40), 690):
                    d.text((x + 50, yy), ln, font=font("SemiBold", 40), fill=CREAM, anchor="lm"); yy += 54
                yy += 22
    elif kind == "stat":
        d.text((W // 2, 470), s["stat"], font=font("Black", 190), fill=A, anchor="mm")
        y = 640
        for ln in wrap(d, s.get("caption", ""), font("SemiBold", 52), 1500):
            d.text((W // 2, y), ln, font=font("SemiBold", 52), fill=CREAM, anchor="mm"); y += 68
    elif kind == "quote":
        d.text((160, 300), "\u201c", font=font("Black", 220), fill=A, anchor="lm")
        y = 430
        for ln in wrap(d, s["quote"], font("Bold", 76), 1560):
            d.text((180, y), ln, font=font("Bold", 76), fill=CREAM, anchor="lm"); y += 98
    else:
        y = heading(d, s["head"], 120, 230, 1700, A)
        bullets(d, s.get("points", []), 120, y, 1550, A)
    im.save(path)


def thumbnail(lesson, path):
    im = Image.new("RGB", (1280, 720), NAVY); d = ImageDraw.Draw(im)
    mark(d, 1030, 360, 190, lw=10)
    tag = lesson.get("thumb_tag", f"EP {lesson['day']}")
    tw = d.textlength(tag, font=font("Black", 44))
    A = accent(lesson)
    d.rounded_rectangle([60, 60, 60 + tw + 60, 130], radius=16, fill=A)
    d.text((90, 95), tag, font=font("Black", 44), fill=NAVY, anchor="lm")
    fs = 96  # shrink both lines together so neither runs into the logo mark
    while fs > 56 and max(d.textlength(lesson[k], font=font("Black", fs)) for k in ("thumb_line1", "thumb_line2")) > 760:
        fs -= 4
    d.text((60, 300), lesson["thumb_line1"], font=font("Black", fs), fill=CREAM, anchor="lm")
    d.text((60, 300 + int(fs * 1.25)), lesson["thumb_line2"], font=font("Black", fs), fill=A, anchor="lm")
    d.text((60, 640), "ATOMS TO CHIPS", font=font("Bold", 36), fill=TEAL, anchor="lm")
    im.save(path)


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


KOKORO = None
VOICE = os.environ.get("ATC_VOICE", "af_heart")


def tts(text, wav):
    """Natural voice via Kokoro (voice af_heart by default)."""
    global KOKORO
    import soundfile as sf, numpy as np
    from kokoro_onnx import Kokoro
    if KOKORO is None:
        d = os.environ.get("ATC_KOKORO", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kokoro"))
        KOKORO = Kokoro(f"{d}/kokoro-v1.0.onnx", f"{d}/voices-v1.0.bin")
    samples, sr = KOKORO.create(text, voice=VOICE, speed=1.0, lang="en-us")
    sf.write(wav, samples, sr, subtype="PCM_16")


def main():
    lesson_path, out = sys.argv[1:3]
    lesson = json.load(open(lesson_path))
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    figs_py = lesson_path[:-5] + "_figs.py"
    if os.path.exists(figs_py):
        subprocess.run([sys.executable, os.path.abspath(figs_py)], check=True, cwd=root)
    os.makedirs(out, exist_ok=True)
    work = os.path.join(out, "work"); os.makedirs(work, exist_ok=True)
    import animate, numpy as np, soundfile as sf
    R = animate.Renderer(sys.modules[__name__], lesson, root)
    slides = lesson["slides"]; parts = []; chapters = []; t = 0.0
    for i, s in enumerate(slides):
        wav = f"{work}/s{i:02d}.wav"; mp4 = f"{work}/s{i:02d}.mp4"
        png = f"{work}/s{i:02d}.png"
        slide_img(lesson, s, i, len(slides), png, root)  # still frame, used for contact sheets
        beats = animate.auto_assign(s, animate.beats_of(s))
        # voice each beat separately so on-screen events land exactly on the words
        chunks, starts, pos, sr = [], [], 0.0, 24000
        for k, b in enumerate(beats):
            bw = f"{work}/s{i:02d}_b{k:02d}.wav"
            tts(b["say"], bw)
            a, sr = sf.read(bw)
            starts.append(pos)
            chunks.append(a); pos += len(a) / sr
            gap = animate.GAP if k < len(beats) - 1 else animate.TAIL
            chunks.append(np.zeros(int(gap * sr))); pos += gap
        audio = np.concatenate(chunks)
        sf.write(wav, audio, sr, subtype="PCM_16")
        dur = len(audio) / sr
        chapters.append((t, s.get("chapter") or s.get("head") or s.get("stat") or "Key idea"))
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                              "-s", f"{animate.W}x{animate.H}", "-r", str(animate.FPS), "-i", "-", "-i", wav,
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                              "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", mp4],
                             stdin=subprocess.PIPE)
        R.render_slide(s, beats, starts, dur, i, len(slides), p.stdin, t)
        p.stdin.close(); p.wait()
        if p.returncode:
            raise SystemExit(f"ffmpeg failed on slide {i}")
        t += dur
        parts.append(mp4)
    lst = f"{work}/list.txt"
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    name = lesson.get("slug", f"day{lesson['day']:02d}")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
         "-movflags", "+faststart", f"{out}/{name}.mp4"])
    thumbnail(lesson, f"{out}/{name}_thumb.jpg")
    # description with real chapter timestamps
    ch = "\n".join(f"{int(a//60)}:{int(a%60):02d} {h}" for a, h in chapters)
    desc = lesson["yt_description"]
    start = desc.find("In this lesson:")
    end = desc.find("\n\n", start)
    if start != -1:
        desc = desc[:start] + "Chapters:\n" + ch + desc[end:]
    open(f"{out}/{name}_description.txt", "w").write(desc)
    print(f"{out}/{name}.mp4", f"{t/60:.1f} min")


if __name__ == "__main__":
    main()
