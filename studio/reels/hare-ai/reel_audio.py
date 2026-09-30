"""Music + sound design for the 8 s AI hare reel (no voice): 120 bpm, every cut lands on a beat."""
import json, os, numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, "tl.json"))); T = TL["T"]; SR = 48000; N = int(T * SR); S = TL["shots"]; BEAT = 60 / TL["bpm"]
rng = np.random.default_rng(7); t = np.arange(N) / SR
mus = np.zeros(N); sfx = np.zeros(N)
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

# ---- EYE: heartbeat + dark drone, riser into the cut ----
a, b = S["eye"]; pad(0, [33, 40, 45], b + .3, .06)
for x in (0.5, 1.0): heart(x, .9)
riser(b, 1.2, .45); whoosh(b + .05, .5, .7)
# ---- RUN: full beat, bass on the root, candles tick ----
a, b = S["run"]; impact(a, .7)
for i, x in enumerate(np.arange(a, b - .01, BEAT)):
    kick(x); hat(x + BEAT / 2); hat(x + BEAT / 4, .06); hat(x + 3 * BEAT / 4, .06)
    if i % 2: snare(x)
    bass(x, [33, 33, 36, 38, 40][i % 5], BEAT * .9)
for i in range(8): pop(a + .8 + i * .16, .22)
for x in np.arange(a + .8, b, .06): click(x, .04, 2600)
riser(b, .8, .5)
# ---- CRASH: the drop -> impact, glitch, everything cuts out ----
a, b = S["crash"]; impact(a, 1.0); boom(a, .9, 32); glitch(a + .02, .3, .35)
for x in (a + .55, a + .8, a + 1.05): glitch(x, .08, .25)
sweep_down(a + .1, 1.1, .2, 900, 60); whoosh(a + .1, .6, .4)
for k in range(3): add(sfx, a + .6 + k * .3, tone(880 if k % 2 == 0 else 660, .25, .07, 6, (1, .2)))
# ---- TORTOISE: warm major pad, one slow steady kick per 2 beats ----
a, b = S["tort"]; pad(a, [48, 52, 55, 59], b - a + 1.2, .05)
for x in np.arange(a, b + .9, 2 * BEAT): kick(x, .5)
for i, m in enumerate([72, 76, 79, 83]): add(mus, a + .1 + i * BEAT / 2, tone(hz(m), 1.2, .06, 2.5))
# ---- END: logo sting ----
a, b = S["end"]; whoosh(a, .5, .4); ding(a + .05, .16, 1568); ding(a + .2, .13, 2093); boom(a, .4, 50)
# ---- mix ----
fade = np.minimum(1, np.minimum(t / .05, (T - t) / .25)).clip(0, 1)
mix = (mus * .8 + sfx * .7) * fade; mix = np.tanh(mix * 1.3) / np.tanh(1.3) * .95
sf.write(os.path.join(HERE, "reel_mix.wav"), np.stack([mix, mix], 1).astype(np.float32), SR); print("audio ok", T)
