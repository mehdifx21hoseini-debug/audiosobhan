"""Sound design for the sanctions reel: real voice + synth music + timed sfx."""
import json, os, numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
# VOICE_CLEAN: voice1 cleaned to 48 kHz mono (see studio/README.md)
VOICE_CLEAN = os.environ.get("VOICE_CLEAN", os.path.join(HERE, "voice1_clean48.wav"))
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

def alarm(at, a=.12, n=2):   # two-tone warning
    for k in range(n): add(sfx, at + k * .28, tone(880 if k % 2 == 0 else 660, .26, a, 6, (1, .2)))
def lockclick(at, a=.5): clack(at, a); click(at + .07, .4, 900); boom(at, .35, 60)

sc = TL["scenes"]; clip = {c["id"]: c for c in TL["clips"]}
def s2d(cid, s): c = clip[cid]; return c["dst"][0] + (s - c["src"][0])
# ---- music: tense minor, pulse after the hook; brighter chord at the solution ----
bpm = 88; beat = 60 / bpm; bar = 4 * beat
prog_dark = [[45, 52, 57, 60], [41, 48, 53, 57], [38, 45, 50, 53], [40, 47, 52, 56]]   # Am F Dm E
prog_lift = [[41, 48, 53, 57], [43, 50, 55, 59], [36, 43, 48, 52], [43, 50, 55, 59]]   # F G C G
k = 0; b0 = 0.0
while b0 < T - .5:
    ch = (prog_lift if b0 >= sc["path"][0] - bar / 2 else prog_dark)[k % 4]
    add(mus, b0, tone(hz(ch[0] - 12), bar, .22, 1.2))
    for q in range(8): add(mus, b0 + q * beat / 2, tone(hz(ch[[1, 2, 3, 2, 1, 2, 3, 2][q]] + 12), .9, .045, 3))
    tt = np.arange(int(bar * SR)) / SR
    for m in ch[1:]: add(mus, b0, .02 * np.minimum(1, tt / .7) * np.minimum(1, (bar - tt) / .5) * np.sin(2 * np.pi * hz(m) * tt))
    k += 1; b0 += bar
for kk, x in enumerate(np.arange(sc["net"][0], sc["outro"][0], beat / 2)):
    tt = np.arange(int(.25 * SR)) / SR; add(mus, x, np.sin(2 * np.pi * (46 + 100 * np.exp(-tt * 32)) * tt) * np.exp(-tt * 10) * (.45 if kk % 2 == 0 else .2))
# ---- HOOK ----
riser(.6, 1.0, .2)
for c in ("c0", "c1", "c2"): whoosh(clip[c]["dst"][0] + .1, .6, .45); pop(clip[c]["dst"][0] + .3, .3)
hit = s2d("c3", 10.58); riser(hit, 1.0, .35); impact(hit, .95); sweep_down(hit + .05, .7, .13, 900, 250); alarm(hit + .5, .08)
# ---- NET ----
s = sc["net"][0]; a4 = clip["c4"]["dst"][0]; whoosh(s + .15, .9, .8)
pop(a4 + .1, .35)
for i in range(7): pop(a4 + .45 + i * .09, .18)
tS = s2d("c4", 163.06); impact(tS, .8); alarm(tS + .3, .1)
tAll = s2d("c4", 165.64)
for i in range(7): click(tAll + i * .22, .25, 1800 + i * 120)
tId = s2d("c4", 170.74); riser(tId, .8, .25)
for i in range(7): ding(tId - .1 + i * .14, .05, 2400)
a5 = clip["c5"]["dst"][0]; whoosh(a5, .7, .5); tL = s2d("c5", 187.80); clack(tL, .5); impact(tL + .05, .55)
# ---- STORY ----
s = sc["story"][0]; whoosh(s + .15, .9, .8); pop(clip["c6"]["dst"][0] + .5, .3); whoosh(clip["c7"]["dst"][0], .6, .35)
tSend = s2d("c8", 744.54); whoosh(tSend - .3, .8, .5); cash(tSend - .8, .2)
tF = s2d("c8", 746.70); lockclick(tF, .6); impact(tF + .05, .9); sweep_down(tF + .1, .9, .15, 700, 120); alarm(tF + .6, .09, 3)
# ---- WALLET ----
s = sc["wallet"][0]; whoosh(s + .15, .9, .8); pop(clip["c9"]["dst"][0], .3)
tNo = s2d("c9", 778.88); impact(tNo, .8); sweep_down(tNo + .05, .5, .12, 800, 300)
a10 = clip["c10"]["dst"][0]; whoosh(a10 - .2, .6, .4); pop(a10 + .15, .4)
tMil = s2d("c10", 806.36)
for i in range(24): pop(tMil - .2 + i * .04, .12)
ding(tMil + .5, .15, 1568); ding(tMil + .65, .12, 2093)
# ---- PATH ----
s = sc["path"][0]; whoosh(s + .15, .9, .8)
for tt_ in (s2d("c11", 386.48), s2d("c11", 387.98), s2d("c11", 394.40)): whoosh(tt_, .5, .35); pop(tt_ + .2, .3)
ding(s2d("c11", 387.98) + .5, .1, 1318); ding(s2d("c11", 394.40) + .5, .12, 1568)
a12 = clip["c12"]["dst"][0]; click(a12 + .8, .3, 2200); click(a12 + 1.6, .3, 2600)
tLow = s2d("c12", 422.08); ding(tLow, .18, 1568); ding(tLow + .12, .15, 2093)
# ---- SOBHAN ----
s = sc["sobhan"][0]; whoosh(s + .1, .9, .5); tOk = s2d("c13", 673.52); ding(tOk + .1, .18, 1318); ding(tOk + .25, .15, 1976)
# ---- OUTRO ----
s = sc["outro"][0]; whoosh(s + .1, .8, .4); ding(s + .3, .15, 1568); ding(s + .45, .12, 2093)
# ---- mix ----
env = np.convolve((np.abs(voice) > .015).astype(float), np.ones(int(.3 * SR)) / int(.3 * SR), "same")
duck = 1 - .7 * np.clip(env * 3, 0, 1)
fade = np.minimum(1, np.minimum(t / .5, (T - t) / .6)).clip(0, 1)
mix = (mus * .75 * duck + sfx * .62 * (1 - .45 * np.clip(env * 3, 0, 1))) * fade + voice * 1.0
mix = np.tanh(mix * 1.1) / np.tanh(1.1) * .95
sf.write(os.path.join(HERE, "reel_mix.wav"), np.stack([mix, mix], 1).astype(np.float32), SR); print("audio ok", T)
