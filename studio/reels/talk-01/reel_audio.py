"""Audio for talk-01: cleaned voice + soft inspiring music bed (ducked) + restrained sfx on graphic beats."""
import json, os, subprocess, numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
TL = json.load(open("tl.json")); T = TL["T"]; SR = 48000; N = int(T * SR); S = TL["subs"]; VE = TL["voice_end"]; OFF = TL["src_offset"]
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(OFF), "-to", str(OFF + VE), "-i", "raw48.wav", "-af",
    "highpass=f=80,afftdn=nr=10:nf=-42:tn=1,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=2,deesser=i=0.25,acompressor=threshold=-20dB:ratio=2.5:attack=10:release=150:makeup=3",
    "voice_clean.wav"], check=True)
v, _ = sf.read("voice_clean.wav", dtype="float32"); voice = np.zeros(N); voice[:len(v)] = v[:N]
rng = np.random.default_rng(3); t = np.arange(N) / SR; mus = np.zeros(N); sfx = np.zeros(N); BEAT = 60 / 96
def add(buf, at, sig):
    s = int(at * SR)
    if s < 0: sig = sig[-s:]; s = 0
    if s >= N or len(sig) == 0: return
    e = min(N, s + len(sig)); buf[s:e] += sig[:e - s]
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
def tone(f, d, a, dec=2.5, harm=(1, .3, .1)):
    tt = np.arange(int(d * SR)) / SR; env = np.minimum(1, tt / .006) * np.exp(-tt * dec)
    return a * env * sum(h * np.sin(2 * np.pi * f * (k + 1) * tt) for k, h in enumerate(harm))
def noise(d, smooth=10): return np.convolve(rng.standard_normal(int(d * SR)), np.ones(smooth) / smooth, "same")
def whoosh(at, d=.7, a=.5): n = noise(d) * np.sin(np.linspace(0, np.pi, int(d * SR))) ** 2 * a; add(sfx, at - d * .6, n)
def riser(at, d=1.2, a=.4): n = noise(d, 6) * np.linspace(0, 1, int(d * SR)) ** 2 * a; add(sfx, at - d, n)
def boom(at, a=.8, f0=40):
    tt = np.arange(int(1.2 * SR)) / SR; add(sfx, at, np.sin(2 * np.pi * (f0 + 90 * np.exp(-tt * 14)) * tt) * np.exp(-tt * 3.2) * a)
def impact(at, a=.6):
    boom(at, a * .9); tt = np.arange(int(.3 * SR)) / SR; add(sfx, at, rng.standard_normal(len(tt)) * np.exp(-tt * 25) * a * .5)
def click(at, a=.35, f=2400):
    tt = np.arange(int(.06 * SR)) / SR; add(sfx, at, (np.sin(2 * np.pi * f * tt) * .5 + rng.standard_normal(len(tt)) * .5) * np.exp(-tt * 90) * a)
def clack(at, a=.5):   # domino hitting domino / table
    tt = np.arange(int(.12 * SR)) / SR
    add(sfx, at, (np.sin(2 * np.pi * 1300 * tt) + .6 * np.sin(2 * np.pi * 2750 * tt) + rng.standard_normal(len(tt)) * .4) * np.exp(-tt * 55) * a)
def chip(at, a=.3): clack(at, a); add(sfx, at + .03, tone(3200, .15, a * .3, 30, (1,)))
def pop(at, a=.3):
    tt = np.arange(int(.1 * SR)) / SR; add(sfx, at, np.sin(2 * np.pi * (500 + 2500 * tt) * tt) * np.exp(-tt * 40) * a)
def ding(at, a=.2, f=1568):
    add(sfx, at, tone(f, 1.4, a, 3.5, (1, .5, .2))); add(sfx, at + .09, tone(f * 1.26, 1.2, a * .8, 3.5, (1, .4)))
def cash(at, a=.25): ding(at, a, 2093); click(at, .3, 1800); click(at + .05, .25, 2200)
def sweep_down(at, d, a=.18, f0=700, f1=180):
    n = int(d * SR); tt = np.arange(n) / SR; f = f0 + (f1 - f0) * (tt / d); ph = 2 * np.pi * np.cumsum(f) / SR
    add(sfx, at, np.sin(ph) * np.minimum(1, tt / .05) * np.minimum(1, (d - tt) / .1) * a)
def kick(at, a=.9):
    tt = np.arange(int(.4 * SR)) / SR; add(mus, at, np.sin(2 * np.pi * (45 + 140 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) * a)
def hat(at, a=.12):
    tt = np.arange(int(.05 * SR)) / SR; n = rng.standard_normal(len(tt)); n = n - np.convolve(n, np.ones(4) / 4, "same"); add(mus, at, n * np.exp(-tt * 70) * a)
def snare(at, a=.35):
    tt = np.arange(int(.25 * SR)) / SR; add(mus, at, (rng.standard_normal(len(tt)) * .7 + np.sin(2 * np.pi * 190 * tt) * .5) * np.exp(-tt * 18) * a)
def bass(at, m, d, a=.3):
    tt = np.arange(int(d * SR)) / SR; f = hz(m); add(mus, at, np.tanh(3 * np.sin(2 * np.pi * f * tt)) * np.minimum(1, tt / .01) * np.exp(-tt * 2) * a)
def pad(at, ms, d, a=.05):
    tt = np.arange(int(d * SR)) / SR; env = np.minimum(1, tt / .4) * np.minimum(1, (d - tt) / .5)
    add(mus, at, env * a * sum(np.sin(2 * np.pi * hz(m) * tt * (1 + dt)) for m in ms for dt in (-.003, 0, .003)))
def heart(at, a=.8): kick(at, a * .8); kick(at + .16, a * .5)
def glitch(at, d=.25, a=.3):
    n = int(d * SR); x = np.repeat(rng.standard_normal(n // 200 + 1), 200)[:n] * np.sign(np.sin(np.arange(n) / SR * 2 * np.pi * 80)); add(sfx, at, x * a * np.exp(-np.arange(n) / SR * 6))

W = lambda i, k: S[i]["wt"][k][0]
# ---- music: F - C - Dm - Bb, soft piano arps + pad + light pulse from line 2 ----
prog = [[41, 53, 57, 60], [36, 52, 55, 60], [38, 50, 53, 57], [34, 50, 53, 58]]
bar = 4 * BEAT; b0 = 0.0; k = 0
while b0 < T:
    ch = prog[k % 4]; pad(b0, ch[1:], bar + .3, .028); bass(b0, ch[0], bar * .95, .12)
    for q in range(8): add(mus, b0 + q * BEAT / 2, tone(hz(ch[1:][q % 3] + 12 + (12 if q in (3, 7) else 0)), 1.0, .035, 3))
    if b0 >= S[1]["dst"][0] - .1:
        for q in range(4): kick(b0 + q * BEAT, .22); hat(b0 + q * BEAT + BEAT / 2, .05)
    k += 1; b0 += bar
# ---- sfx on graphic beats ----
whoosh(.05, .5, .25); ding(.25, .07, 1568)
whoosh(S[1]["dst"][0], .5, .3); pop(W(1, 3), .2); pop(W(1, 5), .2); pop(W(2, 1), .18); clack(W(2, 1) + .3, .15)
cash(W(2, 3), .16)
whoosh(S[3]["dst"][0], .5, .3); impact(W(3, 6), .45)
whoosh(S[4]["dst"][0], .5, .3); pop(W(6, 1), .18); pop(W(6, 3), .18)
whoosh(S[7]["dst"][0], .5, .25); ding(W(7, 3), .07, 1318); ding(W(7, 5), .08, 1568)
whoosh(S[8]["dst"][0], .45, .25); pop(W(8, 0), .2); pop(W(8, 4), .2)
whoosh(S[10]["dst"][0], .5, .3)
for i in range(12): pop(W(10, 4) + i * .09, .09)
riser(S[13]["dst"][0], .9, .18); boom(S[13]["dst"][0], .35, 45); ding(S[13]["dst"][0] + .1, .08, 1318)
ding(S[15]["dst"][0] + .1, .07, 1568)
whoosh(VE, .6, .35); ding(VE + .15, .12, 1568); ding(VE + .3, .1, 2093); boom(VE + .1, .3, 50)
# ---- mix ----
env = np.convolve((np.abs(voice) > .02).astype(float), np.ones(int(.35 * SR)) / int(.35 * SR), "same")
duck = 1 - .72 * np.clip(env * 3, 0, 1)
fade = np.minimum(1, np.minimum(t / .3, (T - t) / .5)).clip(0, 1)
mix = (mus * .55 * duck + sfx * .5 * (1 - .4 * np.clip(env * 3, 0, 1))) * fade + voice
sf.write("mix_pre.wav", np.stack([mix, mix], 1).astype(np.float32), SR)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "mix_pre.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", "reel_mix.wav"], check=True)
print("audio ok", T)
