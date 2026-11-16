# Daily runbook: Atoms to Chips

The daily scheduled task follows these steps once each morning (IST). The goal is to make the next video in `plan.md` and leave it in Metricool as a **draft for 1:00 PM (13:00) IST**, so the channel owner approves each post with one click.

## 1. Set up (fresh session each day)
```bash
git clone --depth 1 https://github.com/semindiaco/atoms-to-chips-videos ~/atc && cd ~/atc
pip install --break-system-packages -q kokoro-onnx soundfile matplotlib
mkdir -p kokoro && for f in kokoro-v1.0.onnx voices-v1.0.bin; do curl -sSLf -o kokoro/$f "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"; done
```

## 2. Pick today's video
- Open `plan.md`. The first line marked `[ ]` is today's episode. Today's date, the IST day number and the posted list in `posted.md` must agree. Never make the same episode twice. If `posted.md` already has an episode scheduled for today (09:00 or 13:00), stop (the 2026-11-14 00:42 intro does not count).

## 3. Write the lesson file `lessons/dayNN_<slug>.json`
Copy the structure of `lessons/day01_intro.json`:
- `label`: playlist and episode, e.g. "BASICS · EP 1" (standalone videos: "SPECIAL").
- `series`: the playlist name, e.g. "Semiconductor Basics".
- `thumb_tag`, `thumb_line1`, `thumb_line2`: short, all caps, each line at most about 12 characters.
- `yt_title`: under 70 characters, e.g. "What Is a Semiconductor? | Semiconductor Basics Ep 1 | Atoms to Chips".
- `yt_description`: 2–3 sentence summary, then a line `In this lesson:` followed by a blank line (the builder replaces it with real chapter timestamps), then "Next video", then hashtags. Do not add any "AI-generated" line.
- `slides`: 12–16 slides. The first has `kind: title`, the last `kind: outro` (teasing tomorrow's topic from `plan.md`). The others have a `head` and either 3–5 short `points` or the fields of their kind. Total narration (`say`) is **1,100–1,400 words**, for 7–9 minutes.
- **Visual variety (required, so the channel never looks templated):** see `tools/build.py` `slide_img` for every slide kind.
  - Use at least **5 diagram slides** (`split` or `figure`) and at least **3 other non-bullet slides** (`compare`, `stat`, `quote`). Never put two plain bullet slides back to back.
  - Draw the diagrams yourself, specific to the topic, in `lessons/dayNN_<slug>_figs.py`. Use `tools/figkit.py`, which has ready helpers (band_diagram, lattice, flow, bars, layers, wafer) and the brand colours for custom matplotlib drawings. Save the PNGs to `out/figs/` and reference them in slides as `"figure": "out/figs/<name>.png"`. Copy each PNG to `figs/` in the repo and commit it, so the figures are kept.
  - Each video should have at least one diagram that's new, not reused from an earlier episode. Vary the opening: a question, a surprising fact (`stat`) or a short story.
  - Every slide's `say` must describe what the diagram shows ("look at the gap between these two bands…").
  - Look at a contact sheet of all slides before publishing. Fix overlaps or cut-off text, and redraw any diagram that's wrong or unclear.
- **Animation synced to the narration (required for every video).** `tools/animate.py` voices each *beat* separately and makes things happen exactly when they are spoken. Read the docstring at the top of `tools/animate.py`: it lists every beat key. The video must feel alive all the time. Something should move or appear at least every 5–8 seconds.
  - On every `split` and `figure` slide, replace `say` with a `beats` list. A beat is one or two short sentences: `{"say": "...", ...keys}`.
  - **Build diagrams up step by step.** Draw each diagram in stages with `save_step()` in the figs script, and give the slide `"figure": [step0.png, step1.png, ...]`. Switch steps with `"step": k` as the narration introduces each part, so the viewer never sees a complex picture all at once. Use at least 3 multi-step diagrams per video.
  - **Pointer:** `"point": "<anchor>"` plus a short `"label"`, used 2–4 times per diagram and moving as the narration walks through it. Define anchors in the figs script with `anchor("name", ax, x, y)` before `save_step()` or `save()`.
  - **Camera zoom:** `"zoom": 1.6` (centred on the beat's point, or `"zoom_on"`) to push into a detail, then `"zoom": 1` to pull back. Use at least twice per video.
  - **Draw-on circle:** `"circle": "<anchor>"` to ring the key spot.
  - **Flow:** `"flow": ["a", "b", "c"]` streams glowing particles along a path through the anchors. Use it for anything that moves: electrons, current, gas into a chamber, a wafer going through steps. Use at least twice per video.
  - **Jargon buster:** `"define": {"term": "...", "meaning": "..."}` the first time any technical word is used. The meaning must be under 12 everyday words.
  - **Quiz:** add 1–2 `quiz` slides per video (`"question"`, 3 `"options"`, `"answer"` index). Beat 1 asks and says "pause and think", and the last beat has `"reveal": true` and explains the answer in one sentence.
  - Captions, slide transitions, count-ups, word-by-word quotes and compare reveals happen automatically.
  - Before publishing, check the motion: pull frames at several moments of 3–4 slides with `ffmpeg -ss <sec> -i out/dayNN/work/sNN.mp4 -frames:v 1 frame.png`. Confirm that the pointer, circles and flows land on the right spots, the zoom keeps the important part in view, and no card hides what is being explained.
- **Make it easy for non-technical viewers (required).** Write for a curious 14-year-old, or a parent with no science background:
  - **Start every new idea with an everyday analogy, then the real term.** For example: energy bands are floors of a building; doping is a pinch of salt in soup; a transistor is a tap for electricity; a cleanroom is a hospital operating theatre multiplied by a thousand; lithography is stencil spray-painting with light. Draw the analogy where possible.
  - Use short sentences (mostly under 15 words) and plain words. Define any unit or symbol before using it, or leave it out. Prefer comparisons ("a thousand times thinner than a hair") to bare numbers.
  - One idea per slide, and 3–4 bullets of at most 6 words each. The narration carries the detail; the screen shows the key words.
  - Hook in the first 15 seconds with a question or surprise from daily life (your phone, your car, a solar panel). Give a one-line "why this matters to you" early on.
  - About every 2 minutes, recap in one sentence ("So far: ..."). End with a three-point summary before the outro.
  - Speak to the viewer: "you", "imagine", "look at this".
- Content rules: accurate, textbook-level science and industry practice. Write numbers as words in `say` ("three hundred millimetres"). Check any current-affairs fact (company plans, fab projects, figures) with a web search that day, and say when it's from. Never mention Debye Labs or any proprietary chamber or process details. No copyrighted images or text.

## 4. Build
```bash
python3 tools/build.py lessons/dayNN_<slug>.json out/dayNN   # runs lessons/dayNN_<slug>_figs.py first if present
ffmpeg -loglevel error -y -i out/dayNN/<slug>.mp4 -c:v libx264 -preset veryfast -crf 26 -c:a copy -movflags +faststart videos/<slug>.mp4
cp out/dayNN/<slug>_thumb.jpg thumbs/ && mkdir -p figs && cp out/figs/* figs/ 2>/dev/null
```
Rendering takes about 1.2× the video length (about 10 minutes for an 8-minute video). Check that it worked: view 2–3 slide PNGs in `out/dayNN/work/` and the thumbnail, check that no text overflows, and confirm the duration is 6–10 minutes.

## 5. Publish the files
Commit `lessons/`, `videos/`, `thumbs/`, `figs/`, mark the episode `[x]` in `plan.md`, and append a line to `posted.md`: `YYYY-MM-DD 13:00 | dayNN | title | metricool post id`. Push to `main`.
The public URLs are `https://raw.githubusercontent.com/semindiaco/atoms-to-chips-videos/main/videos/<slug>.mp4` (and `/thumbs/<slug>_thumb.jpg`).

## 6. Create the Metricool draft
Use the Metricool tool `createScheduledPost` with blogId `8089583`, date today 13:00 +05:30, and `draft: true`. Fill in: the media URL, `videoThumbnailUrl`, the providers `youtube`, and the text from the generated `_description.txt`. The YouTube data is: title, type "video", privacy "public", tags, category "EDUCATION", madeForKids false, isAiGeneratedContent false.
The post stays a draft. The channel owner reviews it in the Metricool planner and confirms it. Never publish without their approval.

## 7. Report
Send the owner a short message with the title, the Metricool planner link, and anything that went wrong.
