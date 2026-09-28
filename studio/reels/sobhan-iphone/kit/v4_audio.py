"""v04 mix: cleaned voice (-14 LUFS), the guitar bed from Sobhan's reference reel (personal-use cut), a handful of very soft sfx."""
import json, os, subprocess, numpy as np, soundfile as sf, pyloudnorm as pyln
FF = os.environ.get("FFMPEG", "ffmpeg"); SR = 48000; TL = json.load(open("tl.json")); VE = TL["voice_end"]; T = VE + 4.6; N = int(T * SR); S = TL["subs"]
v, _ = sf.read("../voice_clean.wav"); voice = np.zeros(N); voice[:min(N, len(v))] = v[:N]
rng = np.random.default_rng(4); sfx = np.zeros(N)
def add(at, sig): i = int(at * SR); j = min(N, i + len(sig)); sfx[i:j] += sig[:j - i] if 0 <= i < N else 0
def noise(d, sm=12): return np.convolve(rng.standard_normal(int(d * SR)), np.ones(sm) / sm, "same")
def whoosh(at, d=.6, a=.1): add(at - d * .5, noise(d) * np.sin(np.linspace(0, np.pi, int(d * SR))) ** 2 * a)
def tone(f, d, a, dec=3.):
    t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * dec) * a
def boom(at, a=.35, f0=38):
    t = np.arange(int(1.6 * SR)) / SR; add(at, np.sin(2 * np.pi * (f0 + 60 * np.exp(-t * 10)) * t) * np.exp(-t * 2.6) * a)
# panel slides: barely-there air
for a in (TL["assets"]["in"], S[8]["dst"][0] - .15, S[17]["dst"][0] - .15, S[24]["dst"][0] - .25): whoosh(a + .3, .6, .07)
# outro: soft boom + chime on the logo landing
boom(VE + 1.9, .38); add(VE + 1.95, tone(1046.5, 2.0, .06)); add(VE + 2.05, tone(1568, 1.8, .035))
m, msr = sf.read(os.environ["MUSIC"]); m = m.mean(1) if m.ndim > 1 else m
if msr != SR: m = np.interp(np.arange(int(len(m) * SR / msr)) * msr / SR, np.arange(len(m)), m)
bed = m.copy(); xf = int(1.5 * SR)
while len(bed) < N: nxt = m[int(3 * SR):]; w = np.linspace(0, 1, xf); bed = np.concatenate([bed[:-xf], bed[-xf:] * (1 - w) + nxt[:xf] * w, nxt[xf:]])
bed = bed[:N]; tt = np.arange(N) / SR
env = np.clip(tt / .6, 0, 1) * 10 ** (6 * np.clip((tt - VE) / .8, 0, 1) / 20) * np.clip((T - tt) / 1.0, 0, 1)
meter = pyln.Meter(SR); g = 10 ** ((-17.2 - meter.integrated_loudness(voice[:int(VE * SR)])) / 20); voice *= g; sfx *= g
bed *= 10 ** ((-17.2 - 14 - meter.integrated_loudness(bed)) / 20)
mix = voice + sfx + bed * env; sf.write("mix_pre.wav", mix, SR, subtype="FLOAT")
for p in range(3):
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", "mix_pre.wav", "-af", "alimiter=limit=0.87:attack=3:release=60:level=false", "-ac", "2", "-c:a", "pcm_s24le", "v4_mix.wav"], check=True)
    out, _ = sf.read("v4_mix.wav"); I = meter.integrated_loudness(out[:int(VE * SR)]); print("pass", p, round(I, 2))
    if abs(I + 14) < .3: break
    mix *= 10 ** ((-14 - I) / 20); sf.write("mix_pre.wav", mix, SR, subtype="FLOAT")
os.remove("mix_pre.wav")
