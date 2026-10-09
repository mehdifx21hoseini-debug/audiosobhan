"""Sound design for the domino reel: real voice + synth music + timed sfx."""
import json, os, numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
# VOICE_CLEAN: voice3 cleaned to 48 kHz mono (see studio/README.md)
VOICE_CLEAN = os.environ.get("VOICE_CLEAN", os.path.join(HERE, "voice3_clean48.wav"))
TL = json.load(open(os.path.join(HERE, "tl.json"))); T = TL["T"]; SR = 48000; N = int(T * SR)
v, sr = sf.read(VOICE_CLEAN, dtype="float32")
voice = np.zeros(N)
for c in TL["clips"]:
    a, b = c["src"]; seg = v[int(a * sr):int(b * sr)].copy(); f = int(.012 * sr)
    seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    s0 = int(c["dst"][0] * SR); voice[s0:s0 + len(seg)] += seg
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

sc = TL["scenes"]; clip = {c["id"]: c for c in TL["clips"]}
def s2d(cid, s): c = clip[cid]; return c["dst"][0] + (s - c["src"][0])
# ---- music: dark, pulsing, builds; chord changes every bar ----
bpm = 92; beat = 60 / bpm; bar = 4 * beat
prog = [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [40, 47, 52, 55]]  # Am F G Em
k = 0; b0 = 0.0
while b0 < T - .5:
    ch = prog[k % 4]
    add(mus, b0, tone(hz(ch[0] - 12), bar, .22, 1.2))
    for q in range(8): add(mus, b0 + q * beat / 2, tone(hz(ch[[1, 2, 3, 2, 1, 2, 3, 2][q]] + 12), .9, .045, 3))
    tt = np.arange(int(bar * SR)) / SR
    for m in ch[1:]: add(mus, b0, .02 * np.minimum(1, tt / .7) * np.minimum(1, (bar - tt) / .5) * np.sin(2 * np.pi * hz(m) * tt))
    k += 1; b0 += bar
for kk, x in enumerate(np.arange(sc["chart"][0], sc["outro"][0], beat / 2)):   # driving pulse after the hook
    tt = np.arange(int(.25 * SR)) / SR; add(mus, x, np.sin(2 * np.pi * (46 + 100 * np.exp(-tt * 32)) * tt) * np.exp(-tt * 10) * (.45 if kk % 2 == 0 else .2))
# ---- HOOK ----
a0 = clip["c0"]["dst"][0]; hit = s2d("c0", 1.95)
riser(.6, 1.0, .25); whoosh(a0 + .15, .6, .5); whoosh(a0 + .35, .6, .45); riser(hit, .8, .35); impact(hit, .9); sweep_down(hit + .05, .6, .12, 900, 300)
# ---- CHART ----
s = sc["chart"][0]; a1 = clip["c1"]["dst"][0]; beat2 = s2d("c1", 10.06); capital = s2d("c1", 13.0)
whoosh(s + .15, .8, .8); whoosh(a1 + .5, 1.0, .15); whoosh(a1 + 1.6, .6, .3); pop(a1 + 1.9, .35); pop(a1 + 2.2, .35); cash(a1 + 2.3, .3)
for x in np.arange(a1 + 2.3, a1 + 3.8, .07): click(x, .05, 2600)
whoosh(beat2, .8, .5); sweep_down(beat2 + .6, 2.6, .12, 520, 110); impact(capital + .2, .75)
# ---- CASINO ----
s = sc["casino"][0]; a2 = clip["c2"]["dst"][0]; a3 = clip["c3"]["dst"][0]; a4 = clip["c4"]["dst"][0]; a5, b5 = clip["c5"]["dst"]
whoosh(s + .2, 1.0, .8); boom(s + .1, .5); pop(a2 + .5, .35)
for i in range(18): chip(a2 + .6 + i * .18 + .35, .22)
pop(s2d("c2", 1166.75), .4); cash(s2d("c2", 1166.75) + .05, .22)
whoosh(a3 - .1, .9, .6)
x, dt = a3 - .1, .045                      # roulette clicks, decelerating
while x < a4 + .1: click(x, .09, 3000); x += dt; dt *= 1.035
impact(a4 + .1, .9); sweep_down(a4 + .15, .9, .15, 600, 90)
for i in range(18): whoosh(a5 + .6 + i * .12 + .55, .35, .08)
impact(s2d("c5", 1219.9) + .2, .8)
# ---- DOMINO ----
s = sc["domino"][0]; a6, b6 = clip["c6"]["dst"]; f0 = s2d("c6", 771.37); gap = (b6 - f0 - .2) / 6
whoosh(s + .2, 1.0, .7); pop(s + .1, .3); whoosh(f0 - .8, .7, .6)
for i in range(6): clack(f0 + i * gap + .3, .55 - i * .02)
impact(f0 + 5 * gap + .3, .6)
# ---- SOBHAN ----
s = sc["sobhan"][0]; a7 = clip["c7"]["dst"][0]; stopT = s2d("c8", 793.2)
n = int(1.0 * SR); tt = np.arange(n) / SR; add(sfx, a7 + .1, noise(1.0, 8) * (tt / 1.0) ** 3 * .35)   # rewind swell
for k2 in range(4): clack(a7 + .2 + k2 * .12 + .3, .35)
impact(stopT + .05, .8); ding(stopT + .1, .18, 1318)
# ---- OUTRO ----
s = sc["outro"][0]; whoosh(s + .1, .8, .4); ding(s + .3, .15, 1568); ding(s + .45, .12, 2093)
# ---- mix ----
env = np.convolve((np.abs(voice) > .015).astype(float), np.ones(int(.3 * SR)) / int(.3 * SR), "same")
duck = 1 - .7 * np.clip(env * 3, 0, 1)
fade = np.minimum(1, np.minimum(t / .5, (T - t) / .6)).clip(0, 1)
mix = (mus * .75 * duck + sfx * .62 * (1 - .45 * np.clip(env * 3, 0, 1))) * fade + voice * 1.0
mix = np.tanh(mix * 1.1) / np.tanh(1.1) * .95
sf.write(os.path.join(HERE, "reel_mix.wav"), np.stack([mix, mix], 1).astype(np.float32), SR); print("audio ok", T)
