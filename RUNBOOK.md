# Daily runbook: Atoms to Chips

The daily scheduled task follows these steps once each morning (IST). The goal is to make the next video in `plan.md` and leave it in Metricool as a **draft for 9:00 AM IST**, so the channel owner approves each post with one click.

## 1. Set up (fresh session each day)
```bash
git clone --depth 1 https://github.com/semindiaco/atoms-to-chips-videos ~/atc && cd ~/atc
pip install --break-system-packages -q kokoro-onnx soundfile
mkdir -p kokoro && for f in kokoro-v1.0.onnx voices-v1.0.bin; do curl -sSLf -o kokoro/$f "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"; done
```

## 2. Pick today's video
- Open `plan.md`. The first line marked `[ ]` is today's episode. Today's date, the IST day number and the posted list in `posted.md` must agree. Never make the same episode twice. If `posted.md` already has an episode scheduled for 09:00 today, stop (the 2026-11-14 00:42 intro does not count).

## 3. Write the lesson file `lessons/dayNN_<slug>.json`
Copy the structure of `lessons/day01_intro.json`:
- `label`: playlist and episode, e.g. "BASICS · EP 1" (standalone videos: "SPECIAL").
- `series`: the playlist name, e.g. "Semiconductor Basics".
- `thumb_tag`, `thumb_line1`, `thumb_line2`: short, all caps, each line at most about 12 characters.
- `yt_title`: under 70 characters, e.g. "What Is a Semiconductor? | Semiconductor Basics Ep 1 | Atoms to Chips".
- `yt_description`: 2–3 sentence summary, then a line `In this lesson:` followed by a blank line (the builder replaces it with real chapter timestamps), then "Next video", then hashtags. Do not add any "AI-generated" line.
- `slides`: 12–16 slides. The first has `kind: title`, the last `kind: outro` (teasing tomorrow's topic from `plan.md`). The others have a `head` and 3–5 short `points`. Total narration (`say`) is **1,100–1,400 words**, for 7–9 minutes.
- **Visual variety (required, so the channel never looks templated):** see `tools/build.py` `slide_img` for every slide kind.
  - Use at least **5 diagram slides** (`split` or `figure`) and at least **3 other non-bullet slides** (`compare`, `stat`, `quote`). Never put two plain bullet slides back to back.
  - Draw the diagrams yourself, specific to the topic, in `lessons/dayNN_<slug>_figs.py`. Use `tools/figkit.py`, which has ready helpers (band_diagram, lattice, flow, bars, layers, wafer) and the brand colours for custom matplotlib drawings. Save the PNGs to `out/figs/` and reference them in slides as `"figure": "out/figs/<name>.png"`. Copy each PNG to `figs/` in the repo and commit it, so the figures are kept.
  - Each video should have at least one diagram that's new, not reused from an earlier episode. Vary the opening: a question, a surprising fact (`stat`) or a short story.
  - Every slide's `say` must describe what the diagram shows ("look at the gap between these two bands…").
  - Look at a contact sheet of all slides before publishing. Fix overlaps or cut-off text, and redraw any diagram that's wrong or unclear.
- Content rules: beginner-friendly, accurate, textbook-level science and industry practice. Write numbers as words in `say` ("three hundred millimetres"). Check any current-affairs fact (company plans, fab projects, figures) with a web search that day, and say when it's from. Never mention Debye Labs or any proprietary chamber or process details. No copyrighted images or text.

## 4. Build
```bash
python3 tools/build.py lessons/dayNN_<slug>.json out/dayNN   # runs lessons/dayNN_<slug>_figs.py first if present
ffmpeg -loglevel error -y -i out/dayNN/<slug>.mp4 -c:v libx264 -preset veryfast -tune stillimage -crf 26 -c:a copy -movflags +faststart videos/<slug>.mp4
cp out/dayNN/<slug>_thumb.jpg thumbs/ && mkdir -p figs && cp out/figs/* figs/ 2>/dev/null
```
Check that it worked: view 2–3 slide PNGs in `out/dayNN/work/` and the thumbnail, check that no text overflows, and confirm the duration is 6–10 minutes.

## 5. Publish the files
Commit `lessons/`, `videos/`, `thumbs/`, `figs/`, mark the episode `[x]` in `plan.md`, and append a line to `posted.md`: `YYYY-MM-DD 09:00 | dayNN | title | metricool post id`. Push to `main`.
The public URLs are `https://raw.githubusercontent.com/semindiaco/atoms-to-chips-videos/main/videos/<slug>.mp4` (and `/thumbs/<slug>_thumb.jpg`).

## 6. Create the Metricool draft
Use the Metricool tool `createScheduledPost` with blogId `8089583`, date today 09:00 +05:30, and `draft: true`. Fill in: the media URL, `videoThumbnailUrl`, the providers `youtube`, and the text from the generated `_description.txt`. The YouTube data is: title, type "video", privacy "public", tags, category "EDUCATION", madeForKids false, isAiGeneratedContent false.
The post stays a draft. The channel owner reviews it in the Metricool planner and confirms it. Never publish without their approval.

## 7. Report
Send the owner a short message with the title, the Metricool planner link, and anything that went wrong.
