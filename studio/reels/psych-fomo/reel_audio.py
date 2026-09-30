"""psych-fomo audio: original voice (voice-02, 0-45.7s, untouched), soft educational bed ducked under it, few subtle UI sfx. Loudness to -14 LUFS."""
import json, os, subprocess, numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
TL = json.load(open("tl.json")); T = TL["T"]; SR = 48000; N = int(T * SR)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "../voice-02/voice_original.m4a", "-t", "45.9", "-ac", "1", "-ar", str(SR), "voice.wav"], check=True)
v, _ = sf.read("voice.wav", dtype="float32"); voice = np.zeros(N); voice[:len(v)] = v[:N]
t = np.arange(N) / SR; rng = np.random.default_rng(2); mus = np.zeros(N); sfx = np.zeros(N)
def add(buf, at, sig):
    s = int(at * SR)
    if s < 0: sig = sig[-s:]; s = 0
    e = min(N, s + len(sig))
    if s < N: buf[s:e] += sig[:e - s]
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
def tone(f, d, a, dec=2.0):
    tt = np.arange(int(d * SR)) / SR; return a * np.minimum(1, tt / .01) * np.exp(-tt * dec) * np.sin(2 * np.pi * f * tt)
def pad(at, ms, d, a):
    tt = np.arange(int(d * SR)) / SR; env = np.minimum(1, tt / .6) * np.minimum(1, (d - tt) / .6)
    add(mus, at, env * a * sum(np.sin(2 * np.pi * hz(m) * tt) for m in ms))
def whoosh(at, d=.5, a=.12):
    n = int(d * SR); x = np.convolve(rng.standard_normal(n), np.ones(12) / 12, "same") * np.sin(np.linspace(0, np.pi, n)) ** 2 * a; add(sfx, at - d * .5, x)
def pop(at, a=.12):
    tt = np.arange(int(.08 * SR)) / SR; add(sfx, at, np.sin(2 * np.pi * (600 + 2000 * tt) * tt) * np.exp(-tt * 45) * a)
# bed: tense minor first half, resolving major at the lesson
bar = 2.4
for i, b0 in enumerate(np.arange(0, T, bar)):
    ch = [[45, 52, 57], [41, 48, 53], [43, 50, 55], [40, 47, 52]][i % 4] if b0 < 25 else [[48, 55, 60], [45, 52, 57], [41, 48, 53], [43, 50, 55]][i % 4]
    pad(b0, ch, bar + .6, .02)
    for q in range(4): add(mus, b0 + q * bar / 4, tone(hz(ch[q % 3] + 24), .9, .012, 3))
for a, _ in TL["slides"]: whoosh(a + .05, .6, .1)
for tt in (5.42, 6.98, 10.54, 7.2, 34.0, 34.3, 34.6): pop(tt, .08)
for tt in (16.9, 17.75, 18.55): add(sfx, tt, tone(880, .25, .05, 8))
add(sfx, 44.6, tone(1318, 1.2, .08, 3)); add(sfx, 44.72, tone(1760, 1.0, .06, 3))
env = np.convolve((np.abs(voice) > .015).astype(float), np.ones(int(.35 * SR)) / int(.35 * SR), "same")
mix = voice + (mus * (1 - .6 * np.clip(env * 3, 0, 1)) + sfx) * np.minimum(1, (T - t) / .8).clip(0, 1)
sf.write("mix_pre.wav", mix.astype(np.float32), SR)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "mix_pre.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", "reel_mix.wav"], check=True)
print("audio ok")
