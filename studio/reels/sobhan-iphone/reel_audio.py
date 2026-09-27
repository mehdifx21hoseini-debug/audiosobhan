"""Audio for sobhan-iphone: cleaned voice (-14 LUFS) + a few restrained sfx on graphic beats. No music bed:
the music (Shape of My Heart) is added later inside Instagram, so the mix leaves room for it."""
import json, subprocess, numpy as np, soundfile as sf, pyloudnorm as pyln, os

FF = os.environ.get("FFMPEG", "ffmpeg"); SR = 48000; TL = json.load(open("tl.json")); T = TL["T"]; VE = TL["voice_end"]
subprocess.run([FF, "-y", "-loglevel", "error", "-i", "voice_cut.wav", "-ac", "1", "-ar", str(SR), "-af",
                "highpass=f=80,afftdn=nr=8:nf=-50:tn=1,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=3500:t=q:w=1.2:g=2,"
                "acompressor=threshold=-24dB:ratio=2.2:attack=10:release=150:makeup=2", "voice_clean.wav"], check=True)
v, _ = sf.read("voice_clean.wav"); N = int(T * SR); voice = np.zeros(N); voice[:len(v)] = v[:N]
rng = np.random.default_rng(5); sfx = np.zeros(N)


def add(at, sig):
    i = int(at * SR); j = min(N, i + len(sig))
    if 0 <= i < N: sfx[i:j] += sig[:j - i]
def noise(d, smooth=10): return np.convolve(rng.standard_normal(int(d * SR)), np.ones(smooth) / smooth, "same")
def whoosh(at, d=.6, a=.35): add(at - d * .55, noise(d) * np.sin(np.linspace(0, np.pi, int(d * SR))) ** 2 * a)
def tone(f, d, a, dec=3.0, harm=(1, .35, .12)):
    t = np.arange(int(d * SR)) / SR; return sum(h * np.sin(2 * np.pi * f * (k + 1) * t) for k, h in enumerate(harm)) * np.exp(-t * dec) * a
def tick(at, a=.25, f=2600):
    t = np.arange(int(.05 * SR)) / SR; add(at, (np.sin(2 * np.pi * f * t) * .6 + rng.standard_normal(len(t)) * .4) * np.exp(-t * 110) * a)
def chime(at, a=.12, f=1318.5):
    add(at, tone(f, 1.6, a)); add(at + .07, tone(f * 1.5, 1.4, a * .6)); add(at + .14, tone(f * 2, 1.2, a * .35))
def boom(at, a=.55, f0=42):
    t = np.arange(int(1.6 * SR)) / SR; add(at, np.sin(2 * np.pi * (f0 + 70 * np.exp(-t * 10)) * t) * np.exp(-t * 2.6) * a)
def riser(at, d, a=.28):
    n = noise(d, 4) * np.linspace(0, 1, int(d * SR)) ** 2.2 * a; t = np.arange(len(n)) / SR
    add(at - d, n + np.sin(2 * np.pi * (200 * t + 500 * t ** 2 / d)) * np.linspace(0, 1, len(n)) ** 3 * a * .25)


P, Q, L, St = TL["price"], TL["quote"], TL["ladder"], TL["state"]
whoosh(P["in"] + .15, .55, .3)
for k in range(8): tick(P["count"] + k * .09, .1 + .02 * k, 2200 + 120 * k)      # counter roll
chime(P["count"] + .78, .09, 1760)
whoosh(Q["in"], .8, .28); boom(Q["in"] + .02, .3, 38)
for k, r in enumerate(("r1", "r2", "r3")): tick(L[r] - .02, .22, 1500 + 400 * k); whoosh(L[r] + .05, .35, .12)
whoosh(St["in"], .8, .28); boom(St["w"][0], .38, 36); tick(St["w"][9], .2, 1200)
riser(VE + 1.15, 1.1, .22); boom(VE + 1.15, .6, 34); chime(VE + 1.2, .14, 1046.5); chime(VE + 1.62, .08, 2093)
whoosh(VE + .05, .9, .22)

meter = pyln.Meter(SR); g = 10 ** ((-17.2 - meter.integrated_loudness(voice[:int(VE * SR)])) / 20)
voice *= g; sfx *= g * .9
fade = np.ones(N); fl = int(.3 * SR); fade[-fl:] = np.linspace(1, 0, fl)
mix = (voice + sfx) * fade
sf.write("mix_pre.wav", mix, SR, subtype="FLOAT")
for trim in (0, 1, 2):                                   # brick-wall limit at -1 dBTP, then re-aim at -14 LUFS
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", "mix_pre.wav", "-af", "alimiter=limit=0.87:attack=3:release=60:level=false,aresample=48000", "-ac", "2", "-c:a", "pcm_s24le", "reel_mix.wav"], check=True)
    out, _ = sf.read("reel_mix.wav"); I = meter.integrated_loudness(out[:int(VE * SR)])
    print("pass", trim, "integrated", round(I, 2), "LUFS, peak", round(20 * np.log10(np.max(np.abs(out))), 2), "dBFS")
    if abs(I + 14) < .3: break
    mix *= 10 ** ((-14 - I) / 20); sf.write("mix_pre.wav", mix, SR, subtype="FLOAT")
os.remove("mix_pre.wav")
