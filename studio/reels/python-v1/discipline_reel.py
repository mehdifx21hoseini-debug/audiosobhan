"""Discipline reel: tortoise & hare -> snowball -> 1 month = 4 years -> Sobhan. Real voice, navy/white brand."""
import math, subprocess, sys, random
import numpy as np, soundfile as sf
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
import fx
from fx import W, H, ease, ease_io, back, font, text, text_img, paste

FPS, SR = 30, 48000
S = fx.S; D = S + "demo/"
FF = imageio_ffmpeg.get_ffmpeg_exe()
NAVY0, NAVY1, NAVY2 = (5, 12, 30), (14, 32, 72), (30, 64, 130)
WHITE, ICE, SNOW, GREEN = (244, 247, 252), (130, 190, 255), (225, 236, 250), (70, 220, 150)
RED = (240, 90, 100)

# ---------------- voice edit ----------------
CLIPS = [  # (src_start, src_end, subtitle, scene)
    (709.0, 711.4, "داستان همون لاک‌پشت و خرگوشه‌ست", "race"),
    (712.1, 714.5, "خرگوشه می‌دوه، می‌دوه، می‌دوه...", "race"),
    (716.4, 718.7, "صدها متر از لاک‌پشت جلوتره", "race"),
    (719.1, 723.5, "اما لاک‌پشت استمرار داره", "tortoise"),
    (723.9, 730.2, "لاک‌پشت دیسیپلین داره؛ شاید سرعتش کم باشه، اما تو یک بازه", "tortoise"),
    (730.6, 734.4, "زمانی، همین‌طوری مستمر، ثابت‌قدم میره", "tortoise"),
    (257.1, 261.6, "نتیجه مالی در معامله‌گری واقعاً ضریب می‌خوره", "snow"),
    (277.7, 284.15, "ضریب می‌خوره... مثل گلوله برفی، بزرگ و بزرگ و بزرگ‌تر میشه", "snow"),
    (298.8, 305.9, "شاید توی یک ماه، برابری بکنه با چهار سالی که براش تلاش کردم", "time"),
    (801.5, 804.3, "دیسیپلین، دیسیپلین، دیسیپلین...", "sobhan"),
    (805.9, 810.15, "کسی که دیسیپلین داشته باشه، نتیجه‌ش رو داره", "sobhan"),
    (810.5, 815.3, "چون نتیجه یک‌روزه نیست، یک هفته نیست، یک ماه نیست", "sobhan"),
]
TL, cur = [], 0.5
for i, (s, e, sub, sc) in enumerate(CLIPS):
    if i and CLIPS[i - 1][3] != sc: cur += 0.35
    TL.append((cur, cur + e - s, s, e, sub, sc)); cur += (e - s) + 0.18
OUTRO = 3.2
SCENES = []
for (st, en, s, e, sub, sc) in TL:
    if not SCENES or SCENES[-1][0] != sc: SCENES.append([sc, st - 0.3 if SCENES else 0.0, None])
SCENES.append(["outro", cur + 0.35, None])
T = SCENES[-1][1] + OUTRO
for i in range(len(SCENES)): SCENES[i][2] = SCENES[i + 1][1] if i + 1 < len(SCENES) else T
NF = int(T * FPS)
def clips(sc): return [x for x in TL if x[5] == sc]
def sstart(sc): return next(s for s in SCENES if s[0] == sc)[1]
TRANS = {"tortoise": "whip", "snow": "morph", "time": "iris", "sobhan": "flash", "outro": "morph"}
TD = 0.6

# ---------------- brand assets ----------------
_L = np.asarray(Image.open("/home/user/audiosobhan/images/logo.jpg").convert("RGB")).astype(np.float32)
_a = np.clip((_L.max(2) - 35) / 60, 0, 1)
def _white_logo(y0, y1):
    a = (_a[y0:y1] * 255).astype(np.uint8)
    im = Image.new("RGBA", (a.shape[1], a.shape[0]), WHITE + (0,)); im.putalpha(Image.fromarray(a))
    return im.crop(im.getchannel("A").getbbox())
LOGO_MARK = _white_logo(0, 960)
LOGO_FULL = _white_logo(0, 1223)
WM = LOGO_MARK.resize((int(LOGO_MARK.width * 110 / LOGO_MARK.height), 110), Image.LANCZOS)

P = Image.open("/root/.claude/uploads/3aca99c1-5242-55c0-aa78-8fa0bb877a30/a404741e-image.png").convert("RGBA")
P = P.crop(P.getchannel("A").getbbox()); PH = 1230
P = P.resize((int(P.width * PH / P.height), PH), Image.LANCZOS)
_g = Image.new("RGBA", P.size, ICE + (0,)); _g.putalpha(P.getchannel("A").filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * .75)))
PG = Image.new("RGBA", (P.width + 120, P.height + 60), (0, 0, 0, 0)); PG.alpha_composite(_g, (60, 60)); PG.alpha_composite(P, (60, 60))

# ---------------- backgrounds ----------------
def grad(top, bot):
    y = np.linspace(0, 1, H)[:, None, None]
    arr = np.array(top) * (1 - y) + np.array(bot) * y
    xx = np.linspace(-1, 1, W)[None, :, None]; yy = np.linspace(-1, 1, H)[:, None, None]
    arr = arr + np.exp(-(xx ** 2 * 2 + (yy + .2) ** 2 * 2.5)) * np.array([18, 30, 60])
    return Image.fromarray(np.broadcast_to(arr, (H, W, 3)).clip(0, 255).astype(np.uint8)).convert("RGBA")
BG_NIGHT = grad(NAVY0, NAVY1)
BG_DEEP = grad((3, 8, 20), (10, 24, 56))
rnd = random.Random(4)
STARS = [(rnd.random() * W, rnd.random() * 900, rnd.uniform(1, 3), rnd.random() * 6) for _ in range(110)]
def _skyline(seed, col, hmin, hmax, w=2600):
    r = random.Random(seed); im = Image.new("RGBA", (w, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 0
    while x < w:
        bw = r.randint(50, 140); bh = r.randint(hmin, hmax)
        d.rectangle([x, 700 - bh, x + bw, 700], fill=col + (255,))
        for wy in range(700 - bh + 20, 690, 34):
            for wx in range(x + 12, x + bw - 12, 26):
                if r.random() < .25: d.rectangle([wx, wy, wx + 8, wy + 12], fill=ICE + (r.randint(40, 120),))
        x += bw + r.randint(4, 20)
    return im
SKY_FAR, SKY_NEAR = _skyline(1, (16, 34, 70), 120, 380), _skyline(2, (9, 20, 44), 60, 260)

def night_scene(t, speed=1.0, ground=1260):
    img = BG_NIGHT.copy(); d = ImageDraw.Draw(img, "RGBA")
    for (x, y, s, ph) in STARS:
        a = int(110 + 100 * math.sin(t * 2 + ph)); d.ellipse([x - s, y - s, x + s, y + s], fill=(220, 235, 255, a))
    d.ellipse([760, 170, 900, 310], fill=(235, 242, 255, 235))  # moon
    img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    o1 = int(t * 40 * speed) % 1300; o2 = int(t * 110 * speed) % 1300
    img.alpha_composite(SKY_FAR.crop((o1, 0, o1 + W, 700)), (0, ground - 700))
    img.alpha_composite(SKY_NEAR.crop((o2, 0, o2 + W, 700)), (0, ground - 700 + 60))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, ground + 60, W, H], fill=(8, 18, 40, 255))
    d.line([(0, ground + 60), (W, ground + 60)], fill=ICE + (180,), width=3)
    off = (t * 420 * speed) % 160  # track dashes
    for k in range(-1, 9):
        x = W - (k * 160 + off); d.rectangle([x, ground + 160, x + 80, ground + 170], fill=WHITE + (90,))
    return img

# ---------------- characters (supersampled vector) ----------------
def _ell(cx, cy, rx, ry, ang=0, n=48):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return [(cx + rx * math.cos(k * 2 * math.pi / n) * c - ry * math.sin(k * 2 * math.pi / n) * s,
             cy + rx * math.cos(k * 2 * math.pi / n) * s + ry * math.sin(k * 2 * math.pi / n) * c) for k in range(n)]
FUR, FUR2, EYE = (242, 246, 252, 255), (196, 212, 236, 255), (10, 22, 50, 255)

def hare(phase, pose="run", size=420):
    K = 3; im = Image.new("RGBA", (520 * K, 380 * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    P = lambda pts: [(x * K, y * K) for x, y in pts]
    if pose == "run":
        b = -14 * abs(math.sin(phase))
        d.polygon(P(_ell(175 + 25 * math.sin(phase), 262 + b, 78, 26, -25 + 45 * math.sin(phase))), fill=FUR2)
        d.polygon(P(_ell(330 + 22 * math.cos(phase), 268 + b, 58, 14, 25 * math.cos(phase + .6))), fill=FUR2)
        d.polygon(P(_ell(250, 205 + b, 128, 64, -8)), fill=FUR)
        d.polygon(P(_ell(245, 232 + b, 100, 30, -8)), fill=(222, 232, 246, 255))
        d.polygon(P(_ell(318 + 20 * math.cos(phase + 1), 262 + b, 52, 13, 35 * math.cos(phase + 1))), fill=FUR)
        d.ellipse([(118 - 24) * K, (178 + b - 24) * K, (118 + 24) * K, (178 + b + 24) * K], fill=FUR)
        d.polygon(P(_ell(338, 88 + b, 76, 17, -32 + 6 * math.sin(phase * 2))), fill=FUR)
        d.polygon(P(_ell(338, 88 + b, 58, 8, -32 + 6 * math.sin(phase * 2))), fill=(250, 200, 214, 255))
        d.polygon(P(_ell(362, 96 + b, 70, 15, -22 + 5 * math.sin(phase * 2 + 1))), fill=FUR2)
        d.ellipse([(390 - 50) * K, (152 + b - 50) * K, (390 + 50) * K, (152 + b + 50) * K], fill=FUR)
        d.ellipse([(410 - 8) * K, (140 + b - 8) * K, (410 + 8) * K, (140 + b + 8) * K], fill=EYE)
        d.ellipse([(436 - 6) * K, (162 + b - 5) * K, (436 + 6) * K, (162 + b + 5) * K], fill=(235, 150, 170, 255))
    else:  # sleeping
        d.polygon(P(_ell(250, 300, 135, 58)), fill=FUR)
        d.polygon(P(_ell(250, 320, 110, 28)), fill=(222, 232, 246, 255))
        d.ellipse([(120 - 22) * K, (290 - 22) * K, (120 + 22) * K, (290 + 22) * K], fill=FUR)
        d.polygon(P(_ell(300, 238, 90, 17, 12)), fill=FUR2)
        d.ellipse([(378 - 48) * K, (282 - 46) * K, (378 + 48) * K, (282 + 46) * K], fill=FUR)
        d.line([((392) * K, 276 * K), ((414) * K, 280 * K)], fill=EYE, width=4 * K)
    im = im.resize((size, int(size * 380 / 520)), Image.LANCZOS)
    return im

def tortoise(phase, size=380):
    K = 3; im = Image.new("RGBA", (470 * K, 300 * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    P = lambda pts: [(x * K, y * K) for x, y in pts]
    skin = (150, 176, 206, 255); skin2 = (120, 146, 180, 255)
    for (lx, ph) in [(140, 0), (300, math.pi)]:
        d.polygon(P(_ell(lx + 10 * math.sin(phase + ph), 250 - 5 * max(0, math.sin(phase + ph)), 30, 22)), fill=skin2)
    for (lx, ph) in [(175, math.pi), (335, 0)]:
        d.polygon(P(_ell(lx + 10 * math.sin(phase + ph), 255 - 5 * max(0, math.sin(phase + ph)), 32, 24)), fill=skin)
    hb = 4 * math.sin(phase * 2)
    d.polygon(P(_ell(385, 190 + hb, 34, 16, -15)), fill=skin)
    d.ellipse([(418 - 34) * K, (172 + hb - 30) * K, (418 + 34) * K, (172 + hb + 30) * K], fill=skin)
    d.ellipse([(430 - 6) * K, (164 + hb - 6) * K, (430 + 6) * K, (164 + hb + 6) * K], fill=EYE)
    d.line([(436 * K, 186 * K + hb * K), (448 * K, 182 * K + hb * K)], fill=EYE, width=2 * K)
    d.ellipse([90 * K, 205 * K, 370 * K, 250 * K], fill=(24, 52, 110, 255))  # rim
    shell = Image.new("L", im.size, 0); ImageDraw.Draw(shell).pieslice([80 * K, 60 * K, 380 * K, 360 * K], 180, 360, fill=255)
    sh = Image.new("RGBA", im.size, (36, 76, 150, 255)); sd = ImageDraw.Draw(sh)
    for (hx, hy, r) in [(230, 150, 48), (150, 185, 40), (310, 185, 40), (190, 105, 36), (270, 105, 36)]:
        sd.polygon([((hx + r * math.cos(k * math.pi / 3)) * K, (hy + r * math.sin(k * math.pi / 3)) * K) for k in range(6)], outline=ICE + (255,), width=4 * K, fill=(52, 100, 180, 255))
    sd.ellipse([150 * K, 80 * K, 250 * K, 130 * K], fill=(255, 255, 255, 40))
    im.paste(sh, (0, 0), shell)
    im = im.resize((size, int(size * 300 / 470)), Image.LANCZOS)
    return im

def tree(h=520):
    im = Image.new("RGBA", (420, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([190, h - 230, 230, h], fill=(12, 26, 54, 255))
    for (x, y, r) in [(210, h - 330, 150), (120, h - 270, 100), (300, h - 270, 105), (210, h - 420, 110)]:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(16, 40, 80, 255))
    return im
TREE = tree()

# ---------------- snowball ----------------
def _snowball_sprite(n=600):
    yy, xx = np.mgrid[-1:1:n * 1j, -1:1:n * 1j]; r = np.sqrt(xx ** 2 + yy ** 2)
    shade = np.clip(1 - ((xx + .35) ** 2 + (yy + .35) ** 2) * .45, .55, 1)
    rng = np.random.default_rng(3); tex = np.asarray(Image.fromarray((rng.random((n // 10, n // 10)) * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), np.float32) / 255
    col = np.stack([230 * shade + 20 * tex, 238 * shade + 15 * tex, 252 * shade], -1)
    a = np.clip((1 - r) * n / 4, 0, 1) * 255
    return Image.fromarray(np.dstack([col.clip(0, 255), a]).astype(np.uint8), "RGBA")
BALL = _snowball_sprite()

# ---------------- UI pieces ----------------
def pill(txt, col=ICE, w=None, fsz=58, tc=WHITE, fill=(8, 18, 44, 225)):
    t = text_img(txt, font(fx.FB, fsz), tc)
    w = w or t.width + 110; h = t.height + 56
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=fill, outline=col + (255,), width=4)
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2 - 3)); return im

def calendar(label, big, hl=False):
    w, h = 300, 340
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=WHITE + (255,))
    d.rounded_rectangle([0, 0, w - 1, 96], 30, fill=((40, 170, 120) if hl else NAVY2) + (255,)); d.rectangle([0, 60, w - 1, 96], fill=((40, 170, 120) if hl else NAVY2) + (255,))
    for x in (80, 220): d.rounded_rectangle([x - 9, -14, x + 9, 30], 8, fill=(200, 210, 230, 255))
    t = text_img(label, font(fx.FB, 44), WHITE); im.alpha_composite(t, ((w - t.width) // 2, 48 - t.height // 2))
    t = text_img(big, font(fx.FB, 150), NAVY1 if not hl else (20, 120, 80)); im.alpha_composite(t, ((w - t.width) // 2, 210 - t.height // 2))
    return im
CALS = [calendar("سال", fx.fa(i + 1)) for i in range(4)]
CAL_M = calendar("ماه", "۱", hl=True)

def ltr_img(s, sz, col):
    f = font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", sz); bb = f.getbbox(s)
    im = Image.new("RGBA", (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), s, font=f, fill=col + (255,)); return im

def watermark(img, a=0.6):
    paste(img, WM, W - 95, 120, 1, a)

# ---------------- subtitles ----------------
def subtitle(img, tt):
    for (st, en, s, e, sub, sc) in TL:
        if st - .08 <= tt <= en + .2:
            a = min(ease((tt - st + .08) / .15), ease((en + .2 - tt) / .15))
            f = font(fx.FX, 48); words = sub.split(" ")
            lines = [sub]
            if f.getlength(sub, direction="rtl") > W - 180:
                best = min(range(1, len(words)), key=lambda k: abs(f.getlength(" ".join(words[:k]), direction="rtl") - f.getlength(" ".join(words[k:]), direction="rtl")))
                lines = [" ".join(words[:best]), " ".join(words[best:])]
            prog = max(0, min(1, (tt - st) / max(.3, en - st - .15))); done = prog * sum(len(l) for l in lines)
            y0 = 1650 if len(lines) == 2 else 1700
            mw = max(f.getlength(l, direction="rtl") for l in lines)
            box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(box).rounded_rectangle([W / 2 - mw / 2 - 40, y0 - 48, W / 2 + mw / 2 + 40, y0 + 48 + 74 * (len(lines) - 1)], 38, fill=(2, 6, 18, int(170 * a)))
            img.alpha_composite(box)
            for li, l in enumerate(lines):
                wht = text_img(l, f, WHITE); hl = text_img(l, f, ICE)
                k = max(0, min(1, done / len(l))); done -= len(l)
                m = Image.new("L", hl.size, 0); ImageDraw.Draw(m).rectangle([int(hl.width * (1 - k)), 0, hl.width, hl.height], fill=255)
                paste(img, Image.composite(hl, wht, m), W / 2, y0 + li * 74, 1, a)
            return

# ---------------- scenes ----------------
def sc_race(t, d):
    base = sstart("race"); c = clips("race")
    img = night_scene(t, 1.0 + 1.5 * ease((t - (c[1][0] - base)) / .6))
    t1 = t - (c[0][0] - base)
    a = ease(t1 / .5)
    text(img, (W / 2, 380 + 40 * (1 - a)), "لاک‌پشت و خرگوش", font(fx.FB, 110), WHITE, a)
    ImageDraw.Draw(img).rounded_rectangle([W / 2 - 170 * a, 470, W / 2 + 170 * a, 478], 4, fill=ICE + (255,))
    text(img, (W / 2, 540), "یک درس بزرگ برای معامله‌گرها", font(fx.FM, 46), SNOW, ease((t1 - .5) / .5))
    ground = 1260
    t2 = t - (c[1][0] - base)
    # hare sprints across then far ahead; tortoise slowly enters
    hx = min(W - 110, -300 + 900 * ease(max(0, t) / 2.6) + 520 * ease(t2 / 1.8))
    hs = 400 * (1 - .45 * ease((t - (c[2][0] - base)) / 1.2))
    h = hare(t * 18, "run", int(hs))
    if t2 > 0:  # speed lines
        sl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sl)
        rr = random.Random(int(t * 30))
        for _ in range(14):
            y = ground - rr.randint(40, 300); x = hx - rr.randint(150, 700)
            sd.line([(x, y), (x + rr.randint(120, 300), y)], fill=WHITE + (rr.randint(60, 150),), width=4)
        img.alpha_composite(sl)
    paste(img, h, hx, ground + 60 - h.height / 2 + 10)
    tx = -250 + 420 * ease(max(0, t - 1.0) / 6)
    tt_ = tortoise(t * 3, 300); paste(img, tt_, tx, ground + 60 - tt_.height / 2 + 6)
    t3 = t - (c[2][0] - base)
    if t3 > 0:  # distance meter
        k = ease(t3 / 1.0); x0, x1 = tx + 120, min(W - 60, hx - 60)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        xm = x0 + (x1 - x0) * k
        ld.line([(x0, ground - 250), (xm, ground - 250)], fill=ICE + (255,), width=6)
        ld.line([(x0, ground - 275), (x0, ground - 225)], fill=ICE + (255,), width=6)
        ld.line([(xm, ground - 275), (xm, ground - 225)], fill=ICE + (255,), width=6)
        img.alpha_composite(lay)
        text(img, ((x0 + xm) / 2, ground - 320), "+" + fx.fa(int(300 * k)) + " متر", font(fx.FB, 66), WHITE, min(1, t3 / .3))
    watermark(img)
    return img.convert("RGB")

def sc_tortoise(t, d):
    base = sstart("tortoise"); c = clips("tortoise")
    img = night_scene(t * .25 + 3, .25, ground=1300)
    ground = 1300
    # sleeping hare under a tree, far right
    paste(img, TREE, 860, ground + 60 - TREE.height / 2 + 10, .9, 1)
    hs = hare(0, "sleep", 300); paste(img, hs, 840, ground + 60 - hs.height / 2 + 6)
    for k in range(3):
        ph = (t * .6 + k / 3) % 1
        text(img, (900 + 60 * ph + k * 10, ground - 120 - 180 * ph), "z", font(fx.FB, 40 + 30 * ph), WHITE, (1 - ph) * .9, shadow=False)
    # rising path behind the tortoise (steady steps -> chart)
    tx = 330 + 60 * (t / d)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    steps = int(t * 2.2); pts = []
    for k in range(steps + 1):
        x = 40 + k * 26; y = ground - 30 - k * 14 - 6 * math.sin(k)
        if x > tx - 40: break
        pts.append((x, y))
    if len(pts) > 1:
        ld.line(pts, fill=ICE + (230,), width=8, joint="curve")
        for (x, y) in pts[::3]: ld.ellipse([x - 7, y - 7, x + 7, y + 7], fill=WHITE + (230,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))
    to = tortoise(t * 3.2, 420); paste(img, to, tx, ground + 60 - to.height / 2 + 8)
    # keyword pills
    labels = [("استمرار", c[0][0]), ("دیسیپلین", c[1][0]), ("ثابت‌قدم", c[2][0] - .2)]
    for i, (lab, st) in enumerate(labels):
        lt = t - (st - base) - .3
        if lt > 0: paste(img, pill(lab, fsz=64), W / 2, 380 + i * 170, back(lt / .45), min(1, lt / .2))
    lt = t - (c[1][0] - base) - 2.4
    if lt > 0: text(img, (W / 2, 900), "سرعت کم، ولی هیچ‌وقت نمی‌ایسته", font(fx.FM, 48), SNOW, ease(lt / .5))
    watermark(img)
    return img.convert("RGB")

SNOW_P = [(random.Random(k).random(), random.Random(k + 99).random()) for k in range(120)]
def sc_snow(t, d):
    base = sstart("snow"); c = clips("snow")
    img = BG_DEEP.copy(); dr = ImageDraw.Draw(img, "RGBA")
    for (x, y, s, ph) in STARS[:60]: dr.ellipse([x - s, y - s, x + s, y + s], fill=(220, 235, 255, 120))
    for (px, py) in SNOW_P:  # falling snow
        y = (py * H + t * 90 * (0.5 + px)) % H; x = (px * W + 30 * math.sin(t + py * 9)) % W
        dr.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(240, 246, 255, 150))
    # mountain slope
    dr.polygon([(0, 700), (W, 1500), (W, H), (0, H)], fill=(220, 232, 248, 255))
    dr.polygon([(0, 760), (W, 1560), (W, H), (0, H)], fill=(196, 214, 238, 255))
    dr.line([(0, 700), (W, 1500)], fill=(255, 255, 255, 255), width=6)
    p = min(1, t / (d - .2))
    x = 60 + 820 * ease_io(p); y = 700 + (x / W) * 800
    r = 28 * math.exp(math.log(300 / 28) * ease_io(p) ** 1.2)
    # trail
    tr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(tr)
    for k in range(40):
        q = max(0, p - k * .012); xx = 60 + 820 * ease_io(q); yy = 700 + (xx / W) * 800
        rr = 28 * math.exp(math.log(300 / 28) * ease_io(q) ** 1.2)
        td.ellipse([xx - rr * .9, yy - rr * .25, xx + rr * .9, yy + rr * .25], fill=(255, 255, 255, int(60 * (1 - k / 40))))
    img.alpha_composite(tr.filter(ImageFilter.GaussianBlur(6)))
    ball = BALL.resize((int(r * 2), int(r * 2)), Image.BILINEAR).rotate(-t * 260, Image.BILINEAR)
    img.alpha_composite(ball, (int(x - r), int(y - r * 1.9)))
    # multiplier badges
    mult = [("×2", .15), ("×4", .35), ("×8", .55), ("×16", .72), ("×32", .86)]
    for i, (m, at) in enumerate(mult):
        lt = p - at
        if lt > 0:
            k = min(1, lt / .06); fade = 1 if i == len(mult) - 1 else max(0, 1 - (lt - .12) / .06)
            paste(img, ltr_img(m, 120 + i * 30, ICE if i < 4 else WHITE), W / 2 + 260 - i * 30, 360 + i * 40, back(k), fade)
    lt = t - (c[0][0] - base)
    text(img, (W / 2, 250), "ضریب می‌خوره", font(fx.FB, 96), WHITE, ease(lt / .5))
    lt2 = t - (c[1][0] - base) - 3.5
    if lt2 > 0: paste(img, pill("اثر گلوله برفی", fsz=56), W / 2 - 180, 560, back(lt2 / .45), min(1, lt2 / .2))
    watermark(img)
    return img.convert("RGB")

def sc_time(t, d):
    base = sstart("time"); c = clips("time")
    img = BG_DEEP.copy(); dr = ImageDraw.Draw(img, "RGBA")
    for gx in range(0, W, 90): dr.line([(gx, 0), (gx, H)], fill=(80, 120, 200, 22), width=2)
    for gy in range(0, H, 90): dr.line([(0, gy), (W, gy)], fill=(80, 120, 200, 22), width=2)
    # exponential curve drawing in the background
    k = ease(t / d); pts = []
    for i in range(int(120 * k) + 1):
        u = i / 120; pts.append((60 + u * (W - 120), 1450 - 900 * (math.exp(3.2 * u) - 1) / (math.exp(3.2) - 1)))
    if len(pts) > 1:
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(cv).line(pts, fill=GREEN + (200,), width=8, joint="curve")
        img.alpha_composite(cv.filter(ImageFilter.GaussianBlur(12))); img.alpha_composite(cv)
    lt0 = t - (c[0][0] - base)
    text(img, (W / 2, 270), "صبر + تکرار", font(fx.FB, 80), WHITE, ease(lt0 / .4))
    # four year calendars flip in, then the month card slams
    c1 = c[0]; dur1 = c1[1] - c1[0]; lt1 = t - (c1[0] - base)
    pos = [(W / 2 - 330, 620), (W / 2 - 110, 620), (W / 2 + 110, 620), (W / 2 + 330, 620)]
    slam = dur1 * .55
    for i in range(4):
        li = lt1 - (dur1 * .30 + i * .28)
        if li > 0:
            dim = 1 - .55 * ease((lt1 - slam) / .4)
            cal = fx.flip3d(CALS[i], min(1, li / .3))
            paste(img, cal, pos[i][0] * (1 - 0) , pos[i][1], .62, dim)
    ls = lt1 - (dur1 * .12)
    if ls > 0:
        paste(img, text_img("۴ سال تلاش", font(fx.FB, 60), SNOW), W / 2, 480, 1, ease(ls / .4) * (1 - .5 * ease((lt1 - slam) / .4)))
    lm = lt1 - slam
    if lm > 0:
        sc = 2.4 - 1.4 * ease(lm / .35)
        paste(img, CAL_M, W / 2, 1060, sc * .85, min(1, lm / .15))
        text(img, (W / 2, 1330), "۱ ماه = ۴ سال", font(fx.FB, 110), WHITE, ease((lm - .35) / .4))
        if lm > .35: fx.light_sweep(img, (lm - .35) / 1.2, 1260, 1400, 1)
        if lm < .2: img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(160 * (1 - lm / .2)))))
    watermark(img)
    return img.convert("RGB")

def sc_sobhan(t, d):
    base = sstart("sobhan"); c = clips("sobhan")
    img = BG_DEEP.copy()
    spot = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(spot).ellipse([W / 2 - 520, 380, W / 2 + 520, 1500], fill=(60, 110, 200, 70))
    img.alpha_composite(spot.filter(ImageFilter.GaussianBlur(120)))
    # pulse on each spoken "discipline"
    c0 = c[0]; n = 5; lt0 = t - (c0[0] - base); dur0 = c0[1] - c0[0]
    pulse = 0
    for i in range(n):
        q = lt0 - i * dur0 / n
        if 0 <= q < .35: pulse = max(pulse, 1 - q / .35)
    ba = ease(t / .6)
    word = text_img("دیسیپلین", font(fx.FB, 250), WHITE)
    paste(img, word, W / 2, 700, 1 + .06 * pulse, ba * (.92 if lt0 < dur0 + .3 else .9))
    person(img, W / 2, H + 40 + 700 * (1 - ease(t / .8)), .95, min(1, t / .3))
    if pulse > 0: img.alpha_composite(Image.new("RGBA", (W, H), (180, 210, 255, int(40 * pulse))))
    # "who has discipline, has results"
    lt1 = t - (c[1][0] - base)
    if lt1 > 0:
        paste(img, pill("نتیجه‌ش رو داره", col=GREEN, fsz=60), W / 2, 330, back(lt1 / .45) if lt1 < 2.5 else 1, min(1, lt1 / .2) * (1 - ease((t - (c[2][0] - base)) / .3)))
    # "not 1 day / 1 week / 1 month"
    c2 = c[2]; lt2 = t - (c2[0] - base); dur2 = c2[1] - c2[0]
    for i, lab in enumerate(["یک روز", "یک هفته", "یک ماه"]):
        li = lt2 - i * dur2 / 3
        if li > 0:
            y = 260 + i * 130
            paste(img, pill(lab, col=RED, fsz=50, w=360), W / 2, y, back(li / .4), min(1, li / .15))
            if li > .35:  # strike
                k = ease((li - .35) / .3); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(lay).line([(W / 2 - 150, y), (W / 2 - 150 + 300 * k, y)], fill=RED + (255,), width=8)
                img.alpha_composite(lay)
    # lower third
    lt3 = t - .6
    if lt3 > 0 and lt2 < 0:
        k = ease(lt3 / .5); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        x1 = W - 70; x0 = x1 - 560 * k
        ld.rounded_rectangle([x0, 1420, x1, 1520], 18, fill=(255, 255, 255, 235)); ld.rectangle([x1 - 12, 1435, x1, 1505], fill=NAVY2 + (255,))
        img.alpha_composite(lay)
        text(img, (x1 - 40, 1470), "سبحان صمدی", font(fx.FB, 58), NAVY1, ease((lt3 - .25) / .3), anchor="rm", shadow=False)
    watermark(img)
    return img.convert("RGB")

def person(img, cx, bottom, scale=1.0, alpha=1.0):
    im = PG.resize((int(PG.width * scale), int(PG.height * scale)), Image.BILINEAR) if abs(scale - 1) > 1e-3 else PG
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(cx - im.width / 2), int(bottom - im.height)))

def sc_outro(t, d):
    img = BG_DEEP.copy()
    spot = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(spot).ellipse([W / 2 - 480, 420, W / 2 + 480, 1300], fill=(60, 110, 200, 80))
    img.alpha_composite(spot.filter(ImageFilter.GaussianBlur(120)))
    lg = LOGO_FULL.resize((520, int(520 * LOGO_FULL.height / LOGO_FULL.width)), Image.LANCZOS)
    k = ease_io(t / 1.2)  # wipe reveal bottom -> top
    m = Image.new("L", lg.size, 0); ImageDraw.Draw(m).rectangle([0, int(lg.height * (1 - k)), lg.width, lg.height], fill=255)
    lgm = lg.copy(); lgm.putalpha(Image.composite(lg.getchannel("A"), Image.new("L", lg.size, 0), m))
    paste(img, lgm, W / 2, 820, .96 + .04 * ease(t / 2), 1)
    if 1.0 < t < 2.4:
        sh = Image.new("L", lg.size, 0); x = -200 + (lg.width + 400) * (t - 1.0) / 1.4
        ImageDraw.Draw(sh).polygon([(x, 0), (x + 90, 0), (x - 60, lg.height), (x - 150, lg.height)], fill=200)
        sh = ImageChops_multiply(sh.filter(ImageFilter.GaussianBlur(16)), lg.getchannel("A"))
        glow = Image.new("RGBA", lg.size, ICE + (0,)); glow.putalpha(sh)
        paste(img, glow, W / 2, 820, 1, 1)
    text(img, (W / 2, 1300), "دیسیپلین، راز نتیجه‌های بزرگ", font(fx.FB, 60), WHITE, ease((t - 1.3) / .5))
    text(img, (W / 2, 1400), "فالو کن و برای دوستت بفرست", font(fx.FM, 44), ICE, ease((t - 1.7) / .5))
    return img.convert("RGB")

def ImageChops_multiply(a, b):
    from PIL import ImageChops
    return ImageChops.multiply(a, b)

FN = {"race": sc_race, "tortoise": sc_tortoise, "snow": sc_snow, "time": sc_time, "sobhan": sc_sobhan, "outro": sc_outro}
def scene_frame(i, tt):
    name, s0, s1 = SCENES[i]; return FN[name](tt - s0, s1 - s0)

def _trans(kind, a, b, p):
    if kind == "morph": return fx.morph(a, b, p)
    if kind == "iris": return fx.iris(a, b, p)
    if kind == "whip": return fx.whip(a, b, p)
    if kind == "flash":
        out = Image.blend(a, b, ease_io(p))
        return Image.blend(out, Image.new("RGB", (W, H), (235, 243, 255)), .85 * (1 - abs(p - .5) * 2))
    return b

def render(tt):
    i = max(k for k in range(len(SCENES)) if SCENES[k][1] <= tt)
    frame = scene_frame(i, tt)
    if i + 1 < len(SCENES) and SCENES[i + 1][1] - tt < TD / 2:
        p = .5 - (SCENES[i + 1][1] - tt) / TD
        frame = _trans(TRANS[SCENES[i + 1][0]], frame, scene_frame(i + 1, SCENES[i + 1][1] + .001), p)
    elif i > 0 and tt - SCENES[i][1] < TD / 2:
        p = .5 + (tt - SCENES[i][1]) / TD
        frame = _trans(TRANS[SCENES[i][0]], scene_frame(i - 1, SCENES[i][1] - .001), frame, p)
    img = frame.convert("RGBA")
    subtitle(img, tt)
    if tt < .3: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - tt / .3)))))
    if T - tt < .6: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - (T - tt) / .6)))))
    return img.convert("RGB")

# ---------------- audio ----------------
def build_audio():
    v, sr = sf.read(S + "voice2/clean48.wav", dtype="float32")
    N = int(T * SR); voice = np.zeros(N, np.float32)
    for (st, en, s, e, *_ ) in TL:
        c = v[int(s * sr):int(e * sr)].copy(); f = int(.015 * sr)
        c[:f] *= np.linspace(0, 1, f); c[-f:] *= np.linspace(1, 0, f)
        voice[int(st * SR):int(st * SR) + len(c)] += c
    t = np.arange(N) / SR; mus = np.zeros(N); rng = np.random.default_rng(2)
    bpm = 88; beat = 60 / bpm; bar = beat * 4
    prog = [[48, 55, 60, 64], [43, 50, 55, 59], [45, 52, 57, 60], [41, 48, 53, 57]]  # C G Am F
    def note(start, f, dur, amp):
        s = int(start * SR); L = min(int(dur * SR), N - s)
        if L <= 0: return
        tt = np.arange(L) / SR; env = np.minimum(1, tt / .005) * np.exp(-tt * 2.6)
        mus[s:s + L] += amp * env * (np.sin(2 * np.pi * f * tt) + .35 * np.sin(4 * np.pi * f * tt) + .12 * np.sin(6 * np.pi * f * tt))
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    for b in range(int(T / bar) + 1):
        ch = prog[b % 4]; b0 = b * bar
        for m in ch[:1]: note(b0, hz(m - 12), bar, .20)  # bass
        for q in range(8):  # piano arpeggio
            m = ch[[1, 2, 3, 2, 1, 2, 3, 2][q]] + 12; note(b0 + q * beat / 2, hz(m), 1.2, .07)
        for m in ch[1:]:  # soft pad
            s = int(b0 * SR); L = min(int(bar * SR), N - s)
            if L > 0:
                tt = np.arange(L) / SR; env = np.minimum(1, tt / .8) * np.minimum(1, (bar - tt) / .6)
                mus[s:s + L] += .025 * env * np.sin(2 * np.pi * hz(m) * tt)
    snow_t = sstart("snow")
    for k in np.arange(snow_t, T - OUTRO, beat):  # drums join at the snowball (build)
        s = int(k * SR); L = min(int(.3 * SR), N - s); tt = np.arange(L) / SR
        mus[s:s + L] += np.sin(2 * np.pi * (46 + 100 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) * .45
        hs = int((k + beat / 2) * SR); hl = int(.04 * SR)
        if hs + hl < N: mus[hs:hs + hl] += np.diff(rng.standard_normal(hl + 1)) * np.exp(-np.arange(hl) / SR * 90) * .04
    sfx = np.zeros(N)
    for sc in SCENES[1:]:
        b0 = int(sc[1] * SR); L = int(.9 * SR); s = max(0, b0 - L)
        nz = np.convolve(rng.standard_normal(b0 - s), np.ones(10) / 10, "same"); sfx[s:b0] += nz * np.linspace(0, 1, b0 - s) ** 2 * .3
        tt = np.arange(min(int(1.2 * SR), N - b0)) / SR
        sfx[b0:b0 + len(tt)] += np.sin(2 * np.pi * (38 + 50 * np.exp(-tt * 7)) * tt) * np.exp(-tt * 3) * .7
    # impact on "1 month = 4 years"
    c1 = clips("time")[0]; b0 = int((c1[0] + (c1[1] - c1[0]) * .55) * SR); tt = np.arange(int(1.2 * SR)) / SR
    sfx[b0:b0 + len(tt)] += np.sin(2 * np.pi * (40 + 120 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 3.5) * .9
    env = np.convolve((np.abs(voice) > .015).astype(float), np.ones(int(.3 * SR)) / int(.3 * SR), "same")
    duck = 1 - .7 * np.clip(env * 3, 0, 1)
    fade = np.minimum(1, np.minimum(t / .6, (T - t) / 1.2)).clip(0, 1)
    mix = (mus * .8 * duck + sfx * .6 * (1 - .5 * np.clip(env * 3, 0, 1))) * fade + voice
    mix = np.tanh(mix * 1.1) / np.tanh(1.1) * .95
    sf.write(D + "disc_mix.wav", np.stack([mix, mix], 1).astype(np.float32), SR)

def work(args):
    k, a, b = args; out = D + f"dchunk_{k}.mp4"
    p = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(a, b): p.stdin.write(render(i / FPS).tobytes())
    p.stdin.close(); p.wait(); return out

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "info":
            for s in SCENES: print(s)
            for x in TL: print([round(v, 2) if isinstance(v, float) else v for v in x])
            print("T", T); sys.exit()
        for s in sys.argv[1:]: render(float(s)).save(D + f"dp_{s}.jpg", quality=85)
        sys.exit()
    build_audio()
    n = 4; step = math.ceil(NF / n)
    with Pool(n) as pool: chunks = pool.map(work, [(k, k * step, min(NF, (k + 1) * step)) for k in range(n)])
    open(D + "dchunks.txt", "w").write("".join(f"file '{c}'\n" for c in chunks))
    subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", D + "dchunks.txt", "-i", D + "disc_mix.wav",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", D + "sobhan_discipline_reel.mp4"], check=True)
    print("done", T)
