import json, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro("/home/claude/tts/kokoro-v1.0.onnx", "/home/claude/tts/voices-v1.0.bin")
out = {}
for s in json.load(open("script.json")):
    a, sr = k.create(s["say"], voice="af_heart", speed=1.08, lang="en-us")
    sf.write(f"a_{s['id']}.wav", a, sr); out[s["id"]] = len(a)/sr; print(s["id"], round(len(a)/sr,2))
json.dump(out, open("durs.json","w")); print(sum(out.values()))
