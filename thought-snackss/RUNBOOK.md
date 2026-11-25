# Thought Snackss — daily reel runbook

Instagram @thought.snackss ("Philosophy without the headache 🧠 / Bite-sized wisdom, daily").
One reel per day, auto-posted at 13:00 IST via Metricool (blogId 8089583, tz Asia/Calcutta). Read STYLE.md first.

## Steps
1. Open queue.md and take the FIRST unchecked link. If none: stop and tell the owner the queue is empty (do not post anything).
2. Read the article. substack.com/home/post/p-… links redirect to the author's page; if WebFetch refuses it, use a browser tool to read it.
3. Write the reel as script.json (see work/02_chinese_philosophies/script.json): 5–6 scenes, about 30 s total narration (25–35 s; roughly 70–85 words),
   fields id / text (captions) / say (what the voice reads — spell hard words phonetically here).
   - Retell the idea in YOUR OWN words, simply, for people with no philosophy background. Never copy sentences.
   - NEVER mention the article, the author, Substack, or "based on". Present it as Thought Snackss' own snack.
   - Keep it clean and kind: no profanity, no named TV shows/films/celebrities, no copyrighted characters.
   - Scene 1 = hook question; middle = ONE core idea + one everyday example (for list articles, pick the 2–3 strongest points only); last scene says exactly:
     "... Follow Thought Snacks, for your daily bite of wisdom." (spelled "Snacks" in say/text, handle on screen).
4. Voice: tools/tts.py (Kokoro voice af_heart, speed 1.08). Model files:
   https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx and voices-v1.0.bin
   (pip install kokoro-onnx soundfile pycairo --break-system-packages; fix the model paths in tts.py).
5. Visuals: copy tools/render_template.py, keep everything above "# ---------- scenes ----------" and the
   watermark/credit/draw/render code, and write NEW scene functions for this topic (see work/02_*/scenes.py for the
   helpers: badge, blobby, cookie, pill, pop_text, kw(sid, word) for word-timed animation).
   Dynamic: something new appears every 1–2 s, cute characters, labels popping on the spoken word.
   Before rendering all scenes, render stills (python3 render.py still <scene> <t>) of the busiest moments and look at them.
6. Render scenes in parallel (python3 render.py scenes a b c …), run tools/audio.py, concat with ffmpeg -c copy,
   then mix voice + music exactly as in the ffmpeg line in work/README or STYLE.md. Check duration and 4 frames.
7. Save to reels/NN_slug.mp4 and work/NN_slug/ (script.json, scenes.py), tick the link in queue.md,
   add a row to posted.md, commit and push to main.
8. Metricool createScheduledPost: date today 13:00 IST (if already past 13:00, post 10 minutes from now),
   providers instagram, instagramData {type: REEL, showReelOnFeed: true, isAiGenerated: false}, autoPublish true,
   draft false, media = raw.githubusercontent.com URL of the reel, videoCoverMilliseconds = a frame with a big title.
   Caption: hook line + 2–5 short lines of the idea + "Save this for someone who needs it" or a question +
   "Follow @thought.snackss for your daily bite of wisdom." + 8–10 hashtags incl. #philosophy #thoughtsnackss.
9. Finish with a short message to the owner: reel title, post time, Metricool planner link, anything that failed.

## Audio mix command
ffmpeg -i video.mp4 -i voice.wav -i music.wav -filter_complex "[1:a]aresample=48000,volume=1.6,asplit[vo1][vo2];[2:a][vo1]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=300[mu];[vo2][mu]amix=inputs=2:normalize=0,alimiter=limit=0.95[aout]" -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out.mp4
