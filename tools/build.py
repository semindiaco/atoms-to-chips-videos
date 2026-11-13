#!/usr/bin/env python3
"""Compound School video builder: lesson JSON -> MP4 + thumbnail.
Usage: python3 build.py lessons/day01.json out_dir voice_model.onnx
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


def base(lesson, idx, total):
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    for i in range(0, W, 80): d.line([(i, 0), (i, H)], fill=NAVY2, width=1)
    for j in range(0, H, 80): d.line([(0, j), (W, j)], fill=NAVY2, width=1)
    mark(d, 125, 85, 42, lw=3)
    d.text((190, 85), "ATOMS TO CHIPS", font=font("Bold", 28), fill=CREAM, anchor="lm")
    d.text((W - 80, 85), lesson["label"], font=font("Bold", 28), fill=GOLD, anchor="rm")
    # progress bar
    d.rectangle([0, H - 10, W, H], fill=NAVY2)
    d.rectangle([0, H - 10, int(W * (idx + 1) / total), H], fill=GOLD)
    d.text((80, H - 50), "youtube.com/@AtomsToChips", font=font("Medium", 22), fill=MUTED, anchor="lm")
    return im, d


def slide_img(lesson, s, idx, total, path):
    im, d = base(lesson, idx, total)
    kind = s.get("kind", "points")
    if kind in ("title", "outro"):
        d.text((W // 2, 360), lesson["series"].upper() if kind == "title" else "COMING UP", font=font("Bold", 34), fill=TEAL, anchor="mm")
        y = 470
        for ln in wrap(d, s["head"], font("Black", 110), 1300):
            d.text((W // 2, y), ln, font=font("Black", 110), fill=CREAM, anchor="mm"); y += 130
        for ln in wrap(d, s.get("sub", ""), font("Medium", 48), 1500):
            d.text((W // 2, y + 30), ln, font=font("Medium", 48), fill=GOLD, anchor="mm"); y += 62
    else:
        y = 230
        for ln in wrap(d, s["head"], font("Black", 84), 1700):
            d.text((120, y), ln, font=font("Black", 84), fill=CREAM, anchor="lm"); y += 100
        d.rectangle([120, y - 20, 300, y - 12], fill=GOLD)
        y += 60
        pts = s.get("points", [])
        fs, lh, gap = (54, 72, 28) if len(pts) <= 5 else (44, 58, 18)
        for p in pts:
            lines = wrap(d, p, font("SemiBold", fs), 1550)
            d.ellipse([125, y - 12, 149, y + 12], fill=GOLD)
            for ln in lines:
                d.text((180, y), ln, font=font("SemiBold", fs), fill=CREAM, anchor="lm"); y += lh
            y += gap
    im.save(path)


def thumbnail(lesson, path):
    im = Image.new("RGB", (1280, 720), NAVY); d = ImageDraw.Draw(im)
    mark(d, 1030, 360, 190, lw=10)
    tag = lesson.get("thumb_tag", f"EP {lesson['day']}")
    tw = d.textlength(tag, font=font("Black", 44))
    d.rounded_rectangle([60, 60, 60 + tw + 60, 130], radius=16, fill=GOLD)
    d.text((90, 95), tag, font=font("Black", 44), fill=NAVY, anchor="lm")
    d.text((60, 300), lesson["thumb_line1"], font=font("Black", 96), fill=CREAM, anchor="lm")
    d.text((60, 420), lesson["thumb_line2"], font=font("Black", 96), fill=GOLD, anchor="lm")
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
    os.makedirs(out, exist_ok=True)
    work = os.path.join(out, "work"); os.makedirs(work, exist_ok=True)
    slides = lesson["slides"]; parts = []; chapters = []; t = 0.0
    for i, s in enumerate(slides):
        png = f"{work}/s{i:02d}.png"; wav = f"{work}/s{i:02d}.wav"; mp4 = f"{work}/s{i:02d}.mp4"
        slide_img(lesson, s, i, len(slides), png)
        tts(s["say"], wav)
        with wave.open(wav) as w:
            dur = w.getnframes() / w.getframerate() + 0.8
        chapters.append((t, s["head"])); t += dur
        run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-i", wav, "-af", "apad=pad_dur=0.8",
             "-t", f"{dur:.2f}", "-vf", "fade=in:0:12,format=yuv420p", "-r", "30",
             "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "20",
             "-c:a", "aac", "-b:a", "160k", "-ar", "44100", mp4])
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
