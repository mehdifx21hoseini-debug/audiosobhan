"""Audio for the 20s template-kit demo: Sobhan's cleaned voice (reel segment), Autofahren bed, sfx per template, 3D-logo outro hit."""
import json, os, subprocess, numpy as np, soundfile as sf, pyloudnorm as pyln
FF = os.environ.get("FFMPEG", "ffmpeg"); SR = 48000
TL = json.load(open("tl.json")); S = TL["subs"]; L = TL["ladder"]; st = TL["state"]
OFF = S[10]["dst"][0] - .12; END = st["out"] + .05; D = END - OFF; OUT = 5.2; T = D + OUT; N = int(T * SR); r = lambda x: x - OFF
v, _ = sf.read("../voice_clean.wav"); v = v[int(OFF * SR):int(END * SR)]; voice = np.zeros(N); voice[:len(v)] = v
fl = int(.08 * SR); voice[len(v) - fl:len(v)] *= np.linspace(1, 0, fl)
rng = np.random.default_rng(9); sfx = np.zeros(N)
def add(at, sig, buf=None):
    buf = sfx if buf is None else buf; i = int(at * SR); j = min(N, i + len(sig))
    if 0 <= i < N: buf[i:j] += sig[:j - i]
def noise(d, sm=10): return np.convolve(rng.standard_normal(int(d * SR)), np.ones(sm) / sm, "same")
def whoosh(at, d=.6, a=.3): add(at - d * .55, noise(d) * np.sin(np.linspace(0, np.pi, int(d * SR))) ** 2 * a)
def tone(f, d, a, dec=3., harm=(1, .35, .12)):
    t = np.arange(int(d * SR)) / SR; return sum(h * np.sin(2 * np.pi * f * (k + 1) * t) for k, h in enumerate(harm)) * np.exp(-t * dec) * a
def tick(at, a=.2, f=2600):
    t = np.arange(int(.05 * SR)) / SR; add(at, (np.sin(2 * np.pi * f * t) * .6 + rng.standard_normal(len(t)) * .4) * np.exp(-t * 110) * a)
def tink(at, a=.16, f=2350): add(at, tone(f, .5, a, 14, (1, .5, .3, .2))); add(at, tone(f * 1.47, .4, a * .5, 18, (1,)))
def boom(at, a=.55, f0=40):
    t = np.arange(int(1.6 * SR)) / SR; add(at, np.sin(2 * np.pi * (f0 + 70 * np.exp(-t * 10)) * t) * np.exp(-t * 2.6) * a)
def chime(at, a=.12, f=1318.5): add(at, tone(f, 1.8, a)); add(at + .07, tone(f * 1.5, 1.6, a * .6)); add(at + .14, tone(f * 2, 1.4, a * .35))
def riser(at, d, a=.25):
    n = noise(d, 4) * np.linspace(0, 1, int(d * SR)) ** 2.2 * a; t = np.arange(len(n)) / SR
    add(at - d, n + np.sin(2 * np.pi * (220 * t + 600 * t ** 2 / d)) * np.linspace(0, 1, len(n)) ** 3 * a * .25)
def pop(at, a=.22):
    t = np.arange(int(.12 * SR)) / SR; add(at, np.sin(2 * np.pi * (420 + 2200 * t) * t) * np.exp(-t * 38) * a)
# segment boundaries (same as kit.html)
segs = [r(S[i]["dst"][0] - .15) for i in (12, 15, 17, 19)]
for a in segs: whoosh(a + .15, .55, .2)
for k in range(11): tick(r(L["r1"]) - .2 + k * .075, .09 + .012 * k, 2000 + 90 * k)                  # digits rolling
chime(r(L["r1"]) + .95, .07, 1760)
for i in range(6): tink(r(L["r2"]) - .1 + i * .09 + .45, .12)                                        # bars landing
for k in range(24): tink(r(L["r3"]) - .05 + k * .035 + .45, .07 + .002 * k, 2100 + (k % 5) * 120)
boom(r(L["r3"]) + .1, .3, 44)
t0 = r(S[15]["dst"][0] - .15) + .35; tt = np.arange(int(2.5 * SR)) / SR                                # chart draw: soft rising sweep
add(t0, np.sin(2 * np.pi * (300 * tt + 60 * tt ** 2)) * np.sin(np.linspace(0, np.pi, len(tt))) * .03)
for w in (S[17]["dst"][0] + .25, S[18]["wt"][1][0], S[18]["wt"][4][0]): pop(r(w) + .02, .2); tick(r(w) + .12, .12, 3200)
boom(r(st["w"][9]) + .2, .5, 38); tick(r(st["w"][9]) + .2, .25, 900)                              # "نیست!" stamp
# outro: fly-in, riser into the landing, impact + shimmer
whoosh(D + .6, 1.1, .22); riser(D + 1.95, 1.5, .2); boom(D + 1.95, .65, 34); chime(D + 2.0, .13, 1046.5); chime(D + 2.45, .07, 2093); tick(D + 2.75, .06, 4200)
# music bed
m, msr = sf.read(os.environ["MUSIC"]); m = m.mean(1) if m.ndim > 1 else m; m = m[int(float(os.environ.get("MUSIC_OFFSET", "0")) * msr):]
if msr != SR: m = np.interp(np.arange(int(len(m) * SR / msr)) * msr / SR, np.arange(len(m)), m)
bed = m[:N]; tt = np.arange(N) / SR
env = np.clip(tt / .25, 0, 1) * 10 ** (7 * np.clip((tt - D) / .8, 0, 1) / 20)
env *= np.clip((T - tt) / 1.0, 0, 1)
meter = pyln.Meter(SR); g = 10 ** ((-17.2 - meter.integrated_loudness(voice[:int(D * SR)])) / 20); voice *= g; sfx *= g * .9
bed *= 10 ** ((-17.2 - 11 - meter.integrated_loudness(bed)) / 20)
mix = voice + sfx + bed * env
sf.write("mix_pre.wav", mix, SR, subtype="FLOAT")
for p in range(3):
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", "mix_pre.wav", "-af", "alimiter=limit=0.87:attack=3:release=60:level=false", "-ac", "2", "-c:a", "pcm_s24le", "kit_mix.wav"], check=True)
    out, _ = sf.read("kit_mix.wav"); I = meter.integrated_loudness(out)
    print("pass", p, round(I, 2), "LUFS"); 
    if abs(I + 14) < .3: break
    mix *= 10 ** ((-14 - I) / 20); sf.write("mix_pre.wav", mix, SR, subtype="FLOAT")
os.remove("mix_pre.wav"); print("T", round(T, 2))
