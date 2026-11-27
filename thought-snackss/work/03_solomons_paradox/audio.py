import json, numpy as np, soundfile as sf
import render as r
sr = 24000
parts = []
for k in r.ORDER:
    a, s = sf.read(f"a_{k}.wav")
    assert s == sr
    n = int(round(r.SCENE_LEN[k] * 30)) / 30 * sr
    seg = np.zeros(int(n))
    st = int(r.LEAD * sr)
    seg[st:st + len(a)] = a[:len(seg) - st]
    parts.append(seg)
voice = np.concatenate(parts)
# music bed: soft pad + plucky arpeggio, 96 bpm, C G Am F
SR = 48000
T = len(voice) / sr
t = np.arange(int(T * SR)) / SR
def note(m): return 440 * 2 ** ((m - 69) / 12)
chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
beat = 60 / 96
bar = beat * 4
music = np.zeros_like(t)
for ci in range(int(T / bar) + 1):
    ch = chords[ci % 4]
    t0 = ci * bar
    m = (t >= t0) & (t < t0 + bar + 0.5)
    tt = t[m] - t0
    env = np.minimum(1, tt / 0.4) * np.exp(-np.maximum(0, tt - bar) * 6)
    for n in ch:
        music[m] += 0.05 * env * np.sin(2 * np.pi * note(n - 12) * tt)
    for j in range(8):
        n = ch[[0, 1, 2, 1, 0, 2, 1, 2][j]] + 12
        s0 = t0 + j * beat / 2
        mm = (t >= s0) & (t < s0 + 0.6)
        tt2 = t[mm] - s0
        music[mm] += 0.06 * np.exp(-tt2 * 7) * (np.sin(2 * np.pi * note(n) * tt2) + 0.3 * np.sin(4 * np.pi * note(n) * tt2))
    # soft kick on beats
    for j in range(4):
        s0 = t0 + j * beat
        mm = (t >= s0) & (t < s0 + 0.25)
        tt2 = t[mm] - s0
        music[mm] += 0.12 * np.exp(-tt2 * 18) * np.sin(2 * np.pi * (50 + 80 * np.exp(-tt2 * 30)) * tt2)
music *= 0.5 / np.max(np.abs(music))
fade = np.minimum(1, np.minimum(t / 0.5, (T - t) / 1.5))
music *= fade * 0.35
sf.write("voice.wav", voice, sr)
sf.write("music.wav", music, SR)
print(T)
