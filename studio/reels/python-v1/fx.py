"""Visual building blocks: animated trading background, bull hero, transitions (morph/iris/whip/glitch)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H = 1080, 1920
S = "/tmp/claude-0/-home-user-audiosobhan/3aca99c1-5242-55c0-aa78-8fa0bb877a30/scratchpad/"
FB = S + "demo/package/fonts/ttf/Vazirmatn-Black.ttf"
FM = S + "demo/package/fonts/ttf/Vazirmatn-Medium.ttf"
FX = S + "demo/package/fonts/ttf/Vazirmatn-ExtraBold.ttf"
GOLD, GOLD2, WHITE, NAVY = (212, 160, 23), (240, 205, 120), (246, 242, 234), (9, 16, 32)
GREEN, RED = (38, 214, 140), (240, 70, 80)
_fc = {}
def font(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def ease_io(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def back(t):  # overshoot
    t = max(0.0, min(1.0, t)); c = 1.7; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

# ---------------- animated trading background ----------------
rnd = random.Random(3)
def _candles(n=140, seed=5):
    r = random.Random(seed); p, out = 100.0, []
    for i in range(n):
        drift = -(p - 100) * 0.06 + 1.1 * math.sin(i / 9)
        o = p; c = o + r.gauss(drift, 1.3); hi = max(o, c) + abs(r.gauss(0, .9)); lo = min(o, c) - abs(r.gauss(0, .9))
        out.append((o, hi, lo, c)); p = c
    return out
CANDLES = _candles()
CW = 34  # candle spacing px
def _chart_layer():
    lo = min(c[2] for c in CANDLES); hi = max(c[1] for c in CANDLES)
    w, h = CW * len(CANDLES) + W, 950
    y = lambda v: 80 + (hi - v) / (hi - lo) * (h - 160)
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(base)
    ma, pts = [], []
    for i, (o, hh, ll, c) in enumerate(CANDLES):
        x = W // 2 + i * CW; col = GREEN if c >= o else RED
        d.line([(x, y(hh)), (x, y(ll))], fill=col + (200,), width=3)
        d.rectangle([x - 11, y(max(o, c)), x + 11, y(min(o, c)) + 2], fill=col + (235,))
        ma.append(c); pts.append((x, y(sum(ma[-12:]) / len(ma[-12:]))))
    d.line(pts, fill=GOLD2 + (255,), width=5, joint="curve")
    glow = base.filter(ImageFilter.GaussianBlur(14))
    out = Image.alpha_composite(glow, base)
    return out, pts
CHART, MA_PTS = _chart_layer()

def _grid_floor():
    g = Image.new("RGBA", (W, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    vx, vy = W / 2, -260
    for k in range(-22, 23):
        d.line([(vx, vy), (W / 2 + k * 150, 700)], fill=GOLD + (70,), width=2)
    return g
FLOOR = _grid_floor()

def _bg_base():
    y = np.linspace(0, 1, H)[:, None, None]
    top, mid = np.array([4, 7, 16]), np.array([14, 28, 58])
    arr = top * (1 - y) + mid * y
    arr = np.broadcast_to(arr, (H, W, 3)).copy()
    xx = np.linspace(-1, 1, W)[None, :]; yy = np.linspace(-1, 1, H)[:, None]
    glow = np.exp(-((xx) ** 2 * 2.2 + (yy + .1) ** 2 * 3.0))[..., None]
    arr += glow * np.array([40, 50, 90])
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")
BASE = _bg_base()

TICK = ["BTC  67,420  ▲2.4%", "USDT  1.000", "XAU  2,388  ▲0.8%", "EUR/USD  1.0871  ▼0.2%", "NASDAQ  18,210  ▲1.1%",
        "ETH  3,512  ▲3.1%", "S&P500  5,480  ▲0.6%", "OIL  78.4  ▼1.3%"]
def _ticker():
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
    parts, x = [], 30
    strip = Image.new("RGBA", (6000, 70), (6, 10, 20, 230)); d = ImageDraw.Draw(strip)
    for i in range(3):
        for s in TICK:
            col = GREEN if "▲" in s else RED if "▼" in s else GOLD2
            d.text((x, 14), s, font=f, fill=col + (255,)); x += int(f.getlength(s)) + 70
    d.line([(0, 0), (6000, 0)], fill=GOLD + (255,), width=3)
    return strip, int(x / 3)
TICKER, TICKW = _ticker()

PARTS = [(rnd.random() * W, rnd.random() * H, rnd.uniform(2, 7), rnd.uniform(15, 60), rnd.uniform(0, 6.28)) for _ in range(70)]

def trading_bg(t, chart_alpha=1.0, ticker=True):
    img = BASE.copy()
    # perspective floor, scrolling
    fl = FLOOR.copy(); d = ImageDraw.Draw(fl)
    for k in range(12):
        z = ((k + (t * 0.8) % 1) / 12) ** 2.2
        d.line([(0, z * 700), (W, z * 700)], fill=GOLD + (int(30 + 60 * z),), width=2)
    img.alpha_composite(fl, (0, H - 700))
    # light beams
    beams = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(beams)
    for i, bx in enumerate([180, 540, 900]):
        a = int(18 + 14 * math.sin(t * 1.3 + i * 2))
        bd.polygon([(bx - 40, 0), (bx + 40, 0), (bx + 260, H), (bx - 260, H)], fill=(120, 150, 255, a))
    img.alpha_composite(beams.filter(ImageFilter.GaussianBlur(30)))
    # chart, drawing itself leftwards
    if chart_alpha > 0:
        off = int(t * 55) % (CHART.width - W - 400)
        crop = CHART.crop((off, 0, off + W, CHART.height))
        if chart_alpha < 1: crop.putalpha(crop.getchannel("A").point(lambda v: int(v * chart_alpha)))
        img.alpha_composite(crop, (0, 520))
        # live price dot on MA
        px = W // 2 + int(t * 55 + W / 2 - W // 2)
        idx = min(len(MA_PTS) - 1, max(0, int((off + W * .72 - W // 2) / CW)))
        mx, my = MA_PTS[idx]
        r = 10 + 5 * math.sin(t * 8)
        dd = ImageDraw.Draw(img)
        dd.ellipse([mx - off - r, my + 520 - r, mx - off + r, my + 520 + r], fill=GOLD2 + (int(255 * chart_alpha),))
    # bokeh particles
    pl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
    for (x, y, s, sp, ph) in PARTS:
        yy = (y - t * sp) % H; a = int(90 + 80 * math.sin(t * 2 + ph))
        pd.ellipse([x - s, yy - s, x + s, yy + s], fill=GOLD2 + (a,))
    img.alpha_composite(pl.filter(ImageFilter.GaussianBlur(1.5)))
    if ticker:
        o = int(t * 140) % TICKW
        img.alpha_composite(TICKER.crop((o, 0, o + W, 70)), (0, H - 70))
    return img

# ---------------- bull hero ----------------
BULL = Image.open("/root/.claude/uploads/3aca99c1-5242-55c0-aa78-8fa0bb877a30/01b67ede-image.png").convert("RGB")
_bs = 1920 * 1.18 / BULL.height
BULL = BULL.resize((int(BULL.width * _bs), int(BULL.height * _bs)), Image.LANCZOS)
def bull(t, dur):
    p = t / dur
    z = 1.0 + 0.10 * ease_io(p)
    cw, ch = W / z * (BULL.height / 1920 / 1.18), H / z * (BULL.height / 1920 / 1.18)
    cx = BULL.width * (0.42 + 0.06 * p); cy = BULL.height * 0.52
    im = BULL.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BILINEAR).convert("RGBA")
    # grade: vignette + bottom darkening
    v = np.linspace(0, 1, H)[:, None]
    dark = (np.clip((v - .45) / .55, 0, 1) ** 1.3 * 235).astype(np.uint8)
    top = (np.clip((.42 - v) / .42, 0, 1) ** .8 * 205).astype(np.uint8)
    m = np.broadcast_to(np.maximum(dark, top), (H, W))
    im.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, H), 5), Image.new("L", (W, H), 8), Image.new("L", (W, H), 18), Image.fromarray(np.ascontiguousarray(m))]))
    return im

def light_sweep(img, t, y0, y1, a=1.0):
    """diagonal shine moving across a band"""
    x = -400 + (W + 800) * (t % 1)
    L = Image.new("L", (W, H), 0); d = ImageDraw.Draw(L)
    d.polygon([(x, y0), (x + 140, y0), (x + 40, y1), (x - 100, y1)], fill=int(110 * a))
    L = L.filter(ImageFilter.GaussianBlur(20))
    img.alpha_composite(Image.merge("RGBA", [Image.new("L", (W, H), 255)] * 3 + [L]))

# ---------------- transitions (operate on RGB numpy) ----------------
NOISE = np.array(Image.effect_noise((W // 8, H // 8), 90).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(10)), dtype=np.float32)
NOISE = (NOISE - NOISE.min()) / (NOISE.max() - NOISE.min())

def morph(a, b, p):
    """liquid gold-edged morph: noise-thresholded dissolve with warp"""
    p = ease_io(p)
    A = np.asarray(a, np.float32); B = np.asarray(b, np.float32)
    thr = p * 1.25 - 0.12
    m = np.clip((thr - NOISE) / 0.12, 0, 1)[..., None]
    edge = np.clip(1 - np.abs(thr - NOISE) / 0.03, 0, 1)[..., None]
    out = A * (1 - m) + B * m
    out = out * (1 - edge) + np.array(GOLD2, np.float32) * edge
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

def iris(a, b, p, cx=W / 2, cy=H * .42):
    p = ease_io(p); r = p * math.hypot(W, H)
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    out = Image.composite(b, a, m)
    ImageDraw.Draw(out).ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD2, width=10)
    return out

def whip(a, b, p):
    """zoom-blur whip pan"""
    src = a if p < .5 else b
    k = 1 - abs(p - .5) * 2  # 0..1..0
    z = 1 + .35 * k
    im = src.resize((int(W * z), int(H * z)), Image.BILINEAR)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    if k > .05:
        arr = np.asarray(im, np.float32); acc = arr.copy()
        for s in range(1, 6): acc += np.roll(arr, int(s * 18 * k), axis=0)
        im = Image.fromarray((acc / 6).astype(np.uint8))
    return im

def glitch(img, amt, seed=0):
    if amt <= 0: return img
    r = random.Random(seed)
    arr = np.asarray(img).copy()
    sh = int(18 * amt)
    arr[..., 0] = np.roll(arr[..., 0], sh, 1); arr[..., 2] = np.roll(arr[..., 2], -sh, 1)
    for _ in range(int(10 * amt)):
        y = r.randrange(0, H - 60); h = r.randrange(8, 60); dx = r.randrange(-80, 80)
        arr[y:y + h] = np.roll(arr[y:y + h], int(dx * amt), 1)
    return Image.fromarray(arr)

# ---------------- text helpers ----------------
def text(img, xy, s, f, fill, alpha=1.0, anchor="mm", shadow=True, maxw=W - 140, stroke=0, sc=(0, 0, 0)):
    if alpha <= 0: return
    while f.getlength(s, direction="rtl") > maxw: f = font(f.path, f.size - 3)
    bb = f.getbbox(s, direction="rtl", anchor=anchor, stroke_width=stroke)
    pad = 40
    lw, lh = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    o = (pad - bb[0], pad - bb[1])
    if shadow:
        d.text((o[0] + 4, o[1] + 7), s, font=f, fill=(0, 0, 0, 170), anchor=anchor, direction="rtl", stroke_width=stroke)
        layer = layer.filter(ImageFilter.GaussianBlur(7)); d = ImageDraw.Draw(layer)
    d.text(o, s, font=f, fill=fill + (255,), anchor=anchor, direction="rtl", stroke_width=stroke, stroke_fill=sc + (255,))
    if alpha < 1: layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(layer, (int(xy[0] - o[0]), int(xy[1] - o[1])))

def text_img(s, f, fill, stroke=0, sc=(0, 0, 0), maxw=W - 140):
    while f.getlength(s, direction="rtl") > maxw: f = font(f.path, f.size - 3)
    bb = f.getbbox(s, direction="rtl", stroke_width=stroke)
    im = Image.new("RGBA", (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), s, font=f, fill=fill + (255,), direction="rtl", stroke_width=stroke, stroke_fill=sc + (255,))
    return im

def paste(img, im, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if alpha <= 0 or scale <= 0.01: return
    if scale != 1: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if rot: im = im.rotate(rot, Image.BILINEAR, expand=True)
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def flip3d(im, p):
    """card flip-in around the vertical axis (p: 0 edge-on -> 1 flat)"""
    p = max(0.001, min(1, p)); w, h = im.size
    k = math.cos((1 - p) * math.pi / 2); nw = max(2, int(w * k)); sk = (1 - k) * h * 0.18
    # perspective: right edge taller than left
    coeffs = _persp([(0, sk), (nw, 0), (nw, h), (0, h - sk)], [(0, 0), (w, 0), (w, h), (0, h)])
    return im.transform((nw, h), Image.PERSPECTIVE, coeffs, Image.BILINEAR)

def _persp(pa, pb):
    A = []
    for (x, y), (X, Y) in zip(pa, pb):
        A += [[x, y, 1, 0, 0, 0, -X * x, -X * y], [0, 0, 0, x, y, 1, -Y * x, -Y * y]]
    A = np.array(A, float); B = np.array(pb, float).reshape(8)
    return np.linalg.solve(A, B).tolist()

def counter(v0, v1, p, fmt="{:,.0f}"):
    return fmt.format(v0 + (v1 - v0) * ease(p))

def fa(s): return str(s).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))
