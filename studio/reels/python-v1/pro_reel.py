"""Surprise reel: real voice of the speaker, trading backgrounds, bull hero, morph/iris/whip/glitch transitions."""
import math, os, subprocess, sys, random
import numpy as np, soundfile as sf
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
import fx
from fx import W, H, GOLD, GOLD2, WHITE, NAVY, GREEN, RED, ease, ease_io, back, font, text, text_img, paste

FPS, SR = 30, 48000
S = fx.S; D = S + "demo/"
FF = imageio_ffmpeg.get_ffmpeg_exe()

# ---------------- voice edit (source seconds in the original recording) ----------------
SEGS = [  # (src_start, src_end, subtitle, scene)
    (0.70, 2.10, "واریز و برداشت", "hook"),
    (3.20, 6.00, "خرید تتر... فروشش", "hook"),
    (6.30, 7.90, "کار کردن با بروکر", "hook"),
    (8.30, 14.10, "در شرایط تحریم به چه شکلیه؟ این ویس خیلی مهمه", "sanction"),
    (14.70, 16.40, "با دقت گوش کن", "sanction"),
    (16.70, 20.24, "اگه اصول رو رعایت کنی، هیچ جای نگرانی نیست", "rule"),
    (31.14, 33.09, "اول اینکه سلام، سلام به روی ماهت", "intro"),
    (36.10, 39.20, "سبحان صمدی هستم؛ می‌خوام در مورد یکی از", "intro"),
    (40.40, 44.82, "مهم‌ترین و پرتکرارترین سؤالات این روزها پاسخ بدم", "intro"),
    (47.50, 55.00, "«آقای صمدی، می‌خوایم تتر بخریم، بریزیم تو بروکر، برداشت بزنیم...»", "question"),
    (55.60, 61.10, "«آقا شرایط تحریم هست، چیکار باید بکنم؟»", "question"),
    (26.20, 30.75, "همین اول کار، بفرست برای تمام دوستان عزیزت", "cta"),
]
GAP_SAME, GAP_SCENE = 0.22, 0.75
TL, cur = [], 0.45
for i, (s, e, sub, sc) in enumerate(SEGS):
    if i and SEGS[i - 1][3] != sc: cur += GAP_SCENE - GAP_SAME
    TL.append((cur, cur + (e - s), s, e, sub, sc)); cur += (e - s) + GAP_SAME
T = cur + 3.2
NF = int(T * FPS)
SCENES = []
for (st, en, s, e, sub, sc) in TL:
    if not SCENES or SCENES[-1][0] != sc: SCENES.append([sc, st - 0.35 if SCENES else 0.0, None])
for i in range(len(SCENES)): SCENES[i][2] = SCENES[i + 1][1] if i + 1 < len(SCENES) else T
SEG_OF = lambda sc: [x for x in TL if x[5] == sc]
TRANS = {"sanction": "whip", "rule": "morph", "intro": "iris", "question": "glitch", "cta": "morph"}
TD = 0.55  # transition duration

# ---------------- assets ----------------
P = Image.open("/root/.claude/uploads/3aca99c1-5242-55c0-aa78-8fa0bb877a30/a404741e-image.png").convert("RGBA")
P = P.crop(P.getchannel("A").getbbox()); PH = 1250
P = P.resize((int(P.width * PH / P.height), PH), Image.LANCZOS)
_g = Image.new("RGBA", P.size, GOLD + (0,)); _g.putalpha(P.getchannel("A").filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(20)).point(lambda v: int(v * .9)))
PG = Image.new("RGBA", (P.width + 120, P.height + 60), (0, 0, 0, 0)); PG.alpha_composite(_g, (60, 60)); PG.alpha_composite(P, (60, 60))
LOGO = Image.open("/home/user/audiosobhan/images/logo.jpg").convert("RGB")
def logo_card(size):
    lg = LOGO.resize((size, int(size * LOGO.height / LOGO.width)), Image.LANCZOS).convert("RGBA")
    pad = int(size * .09); c = Image.new("RGBA", (lg.width + pad * 2, lg.height + pad * 2), (0, 0, 0, 0))
    m = Image.new("L", c.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, c.width - 1, c.height - 1], pad, fill=255)
    c.paste(Image.new("RGBA", c.size, (0, 0, 0, 255)), (0, 0), m)
    ImageDraw.Draw(c).rounded_rectangle([0, 0, c.width - 1, c.height - 1], pad, outline=GOLD + (255,), width=max(3, size // 90))
    c.alpha_composite(lg, (pad, pad)); return c
LOGO_S, LOGO_B = logo_card(120), logo_card(420)
BULL_BLUR = None

def card(txt, w=820, h=150, col=GOLD, fill=(8, 14, 28, 235), f=None, tc=WHITE):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], h // 3, fill=fill, outline=col + (255,), width=4)
    d.rectangle([w - 22, h * .22, w - 10, h * .78], fill=col + (255,))
    t = text_img(txt, f or font(fx.FB, 74), tc, maxw=w - 90)
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2 - 4)); return im
HOOK_CARDS = [card(s) for s in ["واریز و برداشت", "خرید و فروش تتر", "کار با بروکر"]]

def icon_usdt(sz=190):
    im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, sz - 1, sz - 1], fill=(38, 161, 123, 255), outline=GOLD2 + (255,), width=5)
    f = font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", sz * .55)
    d.text((sz / 2, sz / 2 + 4), "₮", font=f, fill=(255, 255, 255, 255), anchor="mm"); return im
def icon_broker(sz=190):
    im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, sz - 1, sz - 1], 36, fill=(20, 40, 80, 255), outline=GOLD2 + (255,), width=5)
    for i, (o, c) in enumerate([(.7, .5), (.5, .62), (.62, .35), (.4, .25)]):
        x = sz * (.2 + i * .2); col = GREEN if c < o else RED
        d.line([(x, sz * min(o, c) - 14), (x, sz * max(o, c) + 14)], fill=col, width=4)
        d.rectangle([x - 12, sz * min(o, c), x + 12, sz * max(o, c)], fill=col)
    return im
def icon_wallet(sz=190):
    im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, sz - 1, sz - 1], 36, fill=(70, 50, 10, 255), outline=GOLD2 + (255,), width=5)
    d.rounded_rectangle([sz * .15, sz * .3, sz * .85, sz * .78], 16, fill=GOLD + (255,))
    d.rounded_rectangle([sz * .58, sz * .44, sz * .9, sz * .64], 10, fill=(40, 28, 5, 255))
    d.ellipse([sz * .66, sz * .5, sz * .74, sz * .58], fill=GOLD2 + (255,))
    return im
ICONS = [(icon_usdt(), "خرید تتر"), (icon_broker(), "واریز به بروکر"), (icon_wallet(), "برداشت")]

def stamp(txt, col=RED):
    t = text_img(txt, font(fx.FB, 150), col)
    im = Image.new("RGBA", (t.width + 80, t.height + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, im.width - 7, im.height - 7], 26, outline=col + (255,), width=12, fill=(20, 0, 0, 120))
    im.alpha_composite(t, (40, 26)); return im
STAMP = stamp("تحریم؟!")

def check_mark(p, cx, cy, r=120):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    a = ease(p * 2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GREEN + (int(255 * a),), width=14, fill=(10, 60, 40, int(160 * a)))
    pts = [(cx - r * .5, cy), (cx - r * .12, cy + r * .4), (cx + r * .55, cy - r * .4)]
    q = ease((p - .3) / .5)
    if q > 0:
        L1 = min(1, q * 2); d.line([pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * L1, pts[0][1] + (pts[1][1] - pts[0][1]) * L1)], fill=GREEN + (255,), width=22)
        if q > .5:
            L2 = (q - .5) * 2; d.line([pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * L2, pts[1][1] + (pts[2][1] - pts[1][1]) * L2)], fill=GREEN + (255,), width=22)
    return im.filter(ImageFilter.GaussianBlur(.6))

def person(img, cx, bottom, scale=1.0, alpha=1.0):
    im = PG if abs(scale - 1) < 1e-3 else PG.resize((int(PG.width * scale), int(PG.height * scale)), Image.BILINEAR)
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(cx - im.width / 2), int(bottom - im.height)))

# ---------------- subtitles: karaoke highlight ----------------
def subtitle(img, tt):
    for (st, en, s, e, sub, sc) in TL:
        if st - .08 <= tt <= en + .2:
            a = min(ease((tt - st + .08) / .15), ease((en + .2 - tt) / .15))
            f = font(fx.FX, 50)
            words = sub.split(" ")
            # wrap to 2 lines if long
            lines = [sub]
            if f.getlength(sub, direction="rtl") > W - 180:
                best = min(range(1, len(words)), key=lambda k: abs(f.getlength(" ".join(words[:k]), direction="rtl") - f.getlength(" ".join(words[k:]), direction="rtl")))
                lines = [" ".join(words[:best]), " ".join(words[best:])]
            prog = max(0, min(1, (tt - st) / max(.3, en - st - .15)))
            total = sum(len(l) for l in lines); done = prog * total
            y0 = 1640 if len(lines) == 2 else 1690
            box = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
            mw = max(f.getlength(l, direction="rtl") for l in lines)
            bd.rounded_rectangle([W / 2 - mw / 2 - 40, y0 - 50, W / 2 + mw / 2 + 40, y0 + 50 + 78 * (len(lines) - 1)], 40, fill=(0, 0, 0, int(165 * a)))
            img.alpha_composite(box)
            for li, l in enumerate(lines):
                y = y0 + li * 78
                wht = text_img(l, f, WHITE); gld = text_img(l, f, GOLD2)
                k = max(0, min(1, done / len(l))); done -= len(l)
                # RTL: reveal gold from the right edge
                m = Image.new("L", gld.size, 0); ImageDraw.Draw(m).rectangle([int(gld.width * (1 - k)), 0, gld.width, gld.height], fill=255)
                gl = Image.composite(gld, wht, m)
                paste(img, gl, W / 2, y, 1, a)
            return

# ---------------- scenes (local time t, duration d) ----------------
def sc_hook(t, d):
    img = fx.trading_bg(t + 2)
    segs = SEG_OF("hook"); base = SCENES[0][1]
    text(img, (W / 2, 330), "سؤال این روزها", font(fx.FM, 58), GOLD2, ease((t - .1) / .4))
    q = 1 + .06 * math.sin(t * 5)
    paste(img, text_img("؟", font(fx.FB, 260), GOLD), W / 2, 560, q * back((t - .1) / .5), 1)
    for i, (st, en, *_ ) in enumerate(segs):
        lt = t - (st - base) + .05
        if lt <= 0: continue
        p = back(lt / .45)
        c = fx.flip3d(HOOK_CARDS[i], min(1, lt / .35))
        paste(img, c, W / 2, 860 + i * 200, .7 + .3 * p, min(1, lt / .15))
    out = img.convert("RGB")
    for (st, en, *_ ) in segs:
        lt = t - (st - base) + .05
        if 0 <= lt < .18: out = fx.glitch(out, 1 - lt / .18, seed=int(st * 10))
    return out

def sc_sanction(t, d):
    img = fx.bull(t, d)
    segs = SEG_OF("sanction"); base = SCENES[1][1]
    a = ease((t - .2) / .3)
    flick = 1 if (t > .9 or int(t * 20) % 3) else .3
    paste(img, text_img("تحریم", font(fx.FB, 260), RED, stroke=6, sc=(20, 0, 0)), W / 2, 420, 1.25 - .25 * ease((t - .2) / .4), a * flick)
    text(img, (W / 2, 620), "واریز و برداشت در شرایط تحریم", font(fx.FB, 60), WHITE, ease((t - .8) / .4))
    t2 = t - (segs[0][0] - base) - 4.2
    if t2 > 0:
        paste(img, card("این ویس خیلی مهمه", w=700, h=130, col=GOLD, fill=(40, 25, 0, 230), f=font(fx.FB, 62), tc=GOLD2), W / 2, 780, back(t2 / .4), min(1, t2 / .2))
    t3 = t - (segs[1][0] - base)
    if t3 > 0:  # "listen carefully" pulse rings
        rings = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(rings)
        for k in range(3):
            ph = ((t3 * .9 + k / 3) % 1); r = 60 + 260 * ph
            rd.ellipse([W / 2 - r, 1080 - r, W / 2 + r, 1080 + r], outline=GOLD2 + (int(200 * (1 - ph)),), width=6)
        img.alpha_composite(rings)
        text(img, (W / 2, 1080), "با دقت گوش کن", font(fx.FB, 70), WHITE, ease(t3 / .3))
    out = img.convert("RGB")
    if t < .25: out = fx.glitch(out, 1 - t / .25, 7)
    return out

def sc_rule(t, d):
    img = fx.bull(t + 6, d + 12)
    img.alpha_composite(Image.new("RGBA", (W, H), (0, 12, 8, 120)))
    text(img, (W / 2, 400 + 50 * (1 - ease(t / .5))), "اگه اصول رو", font(fx.FB, 96), WHITE, ease(t / .5))
    text(img, (W / 2, 530 + 50 * (1 - ease((t - .3) / .5))), "رعایت کنی", font(fx.FB, 120), GOLD2, ease((t - .3) / .5))
    img.alpha_composite(check_mark((t - 1.2) / 1.0, W / 2, 820))
    a = ease((t - 1.9) / .5)
    text(img, (W / 2, 1060), "هیچ جای نگرانی نیست", font(fx.FB, 92), GREEN, a)
    if a > 0: fx.light_sweep(img, (t - 1.9) / 1.4, 980, 1140, a)
    return img.convert("RGB")

def sc_intro(t, d):
    img = fx.trading_bg(t + 8, .55)
    segs = SEG_OF("intro"); base = SCENES[3][1]
    name_t = t - (segs[1][0] - base)
    ba = ease((t - .3) / .7)
    text(img, (W / 2, 690 + 40 * (1 - ba)), "سبحان", font(fx.FB, 270), GOLD, ba * .95)
    e = back(t / 1.0)
    person(img, W / 2, H + 40 + 900 * (1 - ease(t / .9)), .92 + .08 * min(1, e), min(1, t / .3))
    # lower third
    if name_t > 0:
        k = ease(name_t / .5)
        lt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lt)
        x1 = W - 60; x0 = x1 - 640 * k
        ld.rectangle([x0, 1330, x1, 1440], fill=(8, 14, 28, 235)); ld.rectangle([x1 - 14, 1330, x1, 1440], fill=GOLD + (255,))
        ld.rectangle([x0, 1440, x0 + 480 * k, 1500], fill=GOLD + (240,))
        img.alpha_composite(lt)
        text(img, (x1 - 40, 1385), "سبحان صمدی", font(fx.FB, 64), WHITE, ease((name_t - .25) / .3), anchor="rm", shadow=False)
        text(img, (x0 + 460 * k, 1470), "آکادمی سبحان صمدی", font(fx.FB, 38), NAVY, ease((name_t - .4) / .3), anchor="rm", shadow=False)
    q_t = t - (segs[2][0] - base) - 1.0
    if q_t > 0:
        paste(img, card("پرتکرارترین سؤال این روزها", w=760, h=120, f=font(fx.FB, 54), tc=GOLD2), W / 2, 330, back(q_t / .45), min(1, q_t / .2))
    paste(img, LOGO_S, W - 110, 140, 1, ease((t - .6) / .4))
    return img.convert("RGB")

def sc_question(t, d):
    img = fx.trading_bg(t + 30, .35)
    segs = SEG_OF("question"); base = SCENES[4][1]
    m = ease(t / .6)
    person(img, W / 2 + 230 * m, H + 40, .92 - .12 * m, 1)
    q0 = t - (segs[0][0] - base)
    # flow: usdt -> broker -> withdraw, timed across the first question segment
    dur0 = segs[0][1] - segs[0][0]
    marks = [0.35, dur0 * .38, dur0 * .62]
    ys = [520, 830, 1140]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for i in range(3):
        lt = q0 - marks[i]
        if i and lt > -0.4:  # arrow from previous icon
            k = ease((lt + .4) / .4); y1, y2 = ys[i - 1] + 105, ys[i - 1] + 105 + (ys[i] - ys[i - 1] - 210) * k
            ld.line([(260, y1), (260, y2)], fill=GOLD2 + (255,), width=8)
            if k > .9: ld.polygon([(236, y2 - 6), (284, y2 - 6), (260, y2 + 22)], fill=GOLD2 + (255,))
    img.alpha_composite(lay)
    for i, (ic, lab) in enumerate(ICONS):
        lt = q0 - marks[i]
        if lt > 0:
            paste(img, ic, 260, ys[i], back(lt / .4), 1, rot=(1 - ease(lt / .4)) * 25)
            text(img, (430, ys[i]), lab, font(fx.FB, 54), WHITE, ease(lt / .3), anchor="lm", maxw=420)
    q1 = t - (segs[1][0] - base)
    if q1 > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), (30, 0, 0, int(170 * ease(q1 / .4)))))
        sc = 2.2 - 1.2 * ease(q1 / .3)
        paste(img, STAMP, W / 2 - 120, 760, sc, min(1, q1 / .15), rot=12)
        text(img, (W / 2 - 120, 1010), "چیکار باید بکنم؟", font(fx.FB, 80), WHITE, ease((q1 - .6) / .4))
    out = img.convert("RGB")
    if q1 > 0 and q1 < .3: out = fx.glitch(out, 1 - q1 / .3, 11)
    return out

def sc_cta(t, d):
    img = fx.bull(t + 3, d + 6)
    img = img.filter(ImageFilter.GaussianBlur(10 * ease(t / .8)))
    img.alpha_composite(Image.new("RGBA", (W, H), (4, 8, 18, int(150 * ease(t / .8)))))
    paste(img, LOGO_B, W / 2, 470, .85 + .15 * back(t / .7), min(1, t / .4))
    text(img, (W / 2, 830), "این ویدیو رو بفرست", font(fx.FB, 84), WHITE, ease((t - .4) / .4))
    text(img, (W / 2, 950), "برای دوستای معامله‌گرت", font(fx.FB, 84), GOLD2, ease((t - .7) / .4))
    # share arrow icon
    sa = ease((t - 1.0) / .4)
    if sa > 0:
        ic = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); idr = ImageDraw.Draw(ic)
        idr.ellipse([0, 0, 199, 199], fill=GOLD + (255,))
        idr.polygon([(55, 140), (150, 100), (60, 55), (75, 95)], fill=NAVY + (255,))
        paste(img, ic, W / 2, 1150, back((t - 1.0) / .4) * (1 + .05 * math.sin(t * 6)), sa, rot=math.sin(t * 3) * 8)
    fa = ease((t - (d - 3.0)) / .5)
    if fa > 0:
        btn = Image.new("RGBA", (680, 130), (0, 0, 0, 0)); bd = ImageDraw.Draw(btn)
        bd.rounded_rectangle([0, 0, 679, 129], 65, fill=GOLD + (255,))
        t_ = text_img("جواب کامل در پارت بعد", font(fx.FB, 54), NAVY); btn.alpha_composite(t_, ((680 - t_.width) // 2, (130 - t_.height) // 2 - 4))
        paste(img, btn, W / 2, 1400, 1 + .04 * math.sin(t * 6), fa)
    out = img.convert("RGB")
    return out

FN = {"hook": sc_hook, "sanction": sc_sanction, "rule": sc_rule, "intro": sc_intro, "question": sc_question, "cta": sc_cta}
def scene_frame(i, tt):
    name, s0, s1 = SCENES[i]
    return FN[name](tt - s0, s1 - s0)

def render(tt):
    i = max(k for k in range(len(SCENES)) if SCENES[k][1] <= tt)
    frame = scene_frame(i, tt)
    # transition into scene i+1 if close to its start (centered on boundary)
    if i + 1 < len(SCENES) and SCENES[i + 1][1] - tt < TD / 2:
        p = .5 - (SCENES[i + 1][1] - tt) / TD
        frame = _trans(TRANS[SCENES[i + 1][0]], frame, scene_frame(i + 1, SCENES[i + 1][1] + .001), p)
    elif i > 0 and tt - SCENES[i][1] < TD / 2:
        p = .5 + (tt - SCENES[i][1]) / TD
        frame = _trans(TRANS[SCENES[i][0]], scene_frame(i - 1, SCENES[i][1] - .001), frame, p)
    img = frame.convert("RGBA")
    subtitle(img, tt)
    d = ImageDraw.Draw(img); d.rectangle([0, 0, int(W * tt / T), 9], fill=GOLD + (255,))
    if tt < .3: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - tt / .3)))))
    if T - tt < .7: img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - (T - tt) / .7)))))
    return img.convert("RGB")

def _trans(kind, a, b, p):
    if kind == "morph": return fx.morph(a, b, p)
    if kind == "iris": return fx.iris(a, b, p)
    if kind == "whip": return fx.whip(a, b, p)
    if kind == "glitch":
        return fx.glitch(a if p < .5 else b, 1 - abs(p - .5) * 2, int(p * 50))
    return b

# ---------------- audio ----------------
def build_audio():
    v, sr = sf.read(S + "voice/clean48.wav", dtype="float32")
    N = int(T * SR); voice = np.zeros(N, np.float32)
    for (st, en, s, e, *_ ) in TL:
        c = v[int(s * sr):int(e * sr)].copy(); f = int(.02 * sr)
        c[:f] *= np.linspace(0, 1, f); c[-f:] *= np.linspace(1, 0, f)
        voice[int(st * SR):int(st * SR) + len(c)] += c
    t = np.arange(N) / SR; mus = np.zeros(N)
    bpm = 100; beat = 60 / bpm
    chords = [[45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [40, 47, 52, 56]]  # Am F G E  (dark/epic)
    bar = beat * 4
    for b in range(int(T / bar) + 1):
        s = int(b * bar * SR); e = min(N, int((b + 1) * bar * SR) + int(.3 * SR))
        if s >= N: break
        tt = t[s:e] - t[s]; env = np.minimum(1, tt / .15) * np.exp(-tt / 3)
        for m in chords[b % 4]:
            fr = 440 * 2 ** ((m - 69) / 12)
            saw = sum(np.sin(2 * np.pi * fr * k * tt * (1 + .002 * (k % 2))) / k for k in range(1, 7))
            mus[s:e] += env * saw * .05
        fr = 440 * 2 ** ((chords[b % 4][0] - 12 - 69) / 12)  # bass pulses (8ths)
        for q in range(8):
            qs = s + int(q * beat / 2 * SR); L = int(beat / 2 * SR * .9); ttt = np.arange(min(L, N - qs)) / SR
            if len(ttt) > 0: mus[qs:qs + len(ttt)] += np.sin(2 * np.pi * fr * ttt) * np.exp(-ttt * 5) * .22
    rng = np.random.default_rng(1)
    for k in np.arange(0, T - 1.5, beat):  # kick + hats
        s = int(k * SR); L = int(.3 * SR); tt = np.arange(min(L, N - s)) / SR
        mus[s:s + len(tt)] += np.sin(2 * np.pi * (48 + 110 * np.exp(-tt * 35)) * tt) * np.exp(-tt * 10) * .55
        hs = int((k + beat / 2) * SR); hl = int(.05 * SR)
        if hs + hl < N: mus[hs:hs + hl] += np.diff(rng.standard_normal(hl + 1)) * np.exp(-np.arange(hl) / SR * 80) * .05
    sfx = np.zeros(N)
    for sc in SCENES[1:]:  # riser + boom on each transition
        b0 = int(sc[1] * SR); L = int(1.0 * SR); s = max(0, b0 - L)
        nz = rng.standard_normal(b0 - s); ramp = np.linspace(0, 1, b0 - s) ** 2
        nz = np.convolve(nz, np.ones(8) / 8, "same"); sfx[s:b0] += nz * ramp * .35
        tt = np.arange(min(int(.9 * SR), N - b0)) / SR
        sfx[b0:b0 + len(tt)] += np.sin(2 * np.pi * (35 + 60 * np.exp(-tt * 8)) * tt) * np.exp(-tt * 3.5) * .9
    for (st, en, s, e, sub, sc) in TL:  # impacts on hook cards + stamp
        if sc == "hook" or sub.startswith("«شرایط"):
            b0 = int(st * SR); tt = np.arange(int(.5 * SR)) / SR
            sfx[b0:b0 + len(tt)] += (np.sin(2 * np.pi * (60 + 200 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 8) * .6
                                     + rng.standard_normal(len(tt)) * np.exp(-tt * 40) * .25)
    env = np.convolve((np.abs(voice) > .015).astype(float), np.ones(int(.3 * SR)) / int(.3 * SR), "same")
    duck = 1 - .72 * np.clip(env * 3, 0, 1)
    fade = np.minimum(1, np.minimum(t / .8, (T - t) / 1.2)).clip(0, 1)
    mix = (mus * .75 * duck + sfx * .7 * (1 - .5 * np.clip(env * 3, 0, 1))) * fade + voice * 1.0
    mix = np.tanh(mix * 1.1) / np.tanh(1.1) * .95
    st = np.stack([mix + .0 * mus, mix], 1).astype(np.float32)
    sf.write(D + "pro_mix.wav", st, SR)

def work(args):
    k, a, b = args
    out = D + f"chunk_{k}.mp4"
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
        for s in sys.argv[1:]: render(float(s)).save(D + f"pp_{s}.jpg", quality=85)
        sys.exit()
    build_audio()
    n = 4; step = math.ceil(NF / n)
    with Pool(n) as pool: chunks = pool.map(work, [(k, k * step, min(NF, (k + 1) * step)) for k in range(n)])
    open(D + "chunks.txt", "w").write("".join(f"file '{c}'\n" for c in chunks))
    subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", D + "chunks.txt", "-i", D + "pro_mix.wav",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", D + "sobhan_pro_reel.mp4"], check=True)
    print("done", T)
