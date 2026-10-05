"""Rebuild the step-and-repeat banner behind the removed people.

The banner is a regular logo lattice (93 px x ~138 px). Clean logos from the
visible edges are averaged into a tile (as a ratio over the local background),
then the lattice is re-rendered over a smooth background model and composited
only inside the removal mask.
"""
import cv2, numpy as np
O = cv2.imread("original.jpg").astype(np.float32)
B = cv2.imread("step1_lama.png").astype(np.float32)
H, W = O.shape[:2]
R = cv2.imread("mask_remove.png", 0) > 0
p3 = cv2.imread("mask_p3.png", 0) > 0
BX0, BX1, WHITE_END, BLUE_END = 593, 2125, 1030, 1297
TW, TH = 105, 135
def quad(pts):
    c = np.polyfit([p[0] for p in pts], [p[1] for p in pts], 2); return lambda x: np.polyval(c, x)
band_top = quad([(615, 1020), (900, 1005), (2060, 1039)])
band_bot = quad([(615, 1279), (1180, 1255), (2060, 1295)])

def lat(c, r):  # template top-left of lattice cell (col c, row r)
    x = 655 + 93.08 * c
    y = 55 + 137.0 * r + (x - 655) * (8 / 1210) + r * (x - 655) * (2 / 1210)
    return x, y

def refine(x, y, ref):
    x, y = int(round(x)), int(round(y))
    win = O[y - 12:y + TH + 12, x - 12:x + TW + 12].mean(2)
    r = cv2.matchTemplate(win, ref.mean(2), cv2.TM_CCOEFF_NORMED)
    _, v, _, (dx, dy) = cv2.minMaxLoc(r)
    return x - 12 + dx, y - 12 + dy, v

def local_bg(img, bright):
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (31, 31))
    f = cv2.dilate(img, k) if bright else cv2.erode(img, k)
    return cv2.blur(f, (31, 31))

def tile(cells, ref_cell, bright):
    x, y = lat(*ref_cell); x, y = int(round(x)), int(round(y))
    ref = O[y:y + TH, x:x + TW]
    ratios = []
    for c in cells:
        tx, ty, v = refine(*lat(*c), ref)
        if v < 0.4: continue
        pad = 40
        big = O[ty - pad:ty + TH + pad, tx - pad:tx + TW + pad]
        rt = (big / local_bg(big, bright))[pad:-pad, pad:-pad]
        ratios.append(rt)
        print(c, (tx, ty), round(v, 2))
    t = np.median(ratios, 0)
    edge = np.concatenate([t[:6].reshape(-1, 3), t[-6:].reshape(-1, 3), t[:, :6].reshape(-1, 3), t[:, -6:].reshape(-1, 3)])
    base = np.median(edge, 0)                      # plain-background level relative to the local bg map
    # feather the tile into the plain level so no box edges show
    wy = np.minimum(np.arange(TH), np.arange(TH)[::-1]); wx = np.minimum(np.arange(TW), np.arange(TW)[::-1])
    win = np.clip(np.minimum.outer(wy, wx) / 8.0, 0, 1)[..., None]
    t = base + (t - base) * win
    return t, base

white, wbase = tile([(0, 0), (1, 0), (13, 0), (14, 0), (14, 1), (14, 2)], (0, 0), True)
# blue band: same logo drawn light-on-blue. Clean blue logos are all half-hidden,
# so derive the tile from the white logo's coverage and the measured colours.
d = 1 - (white / wbase).mean(2)
alpha = np.clip(d / np.percentile(d, 99.5), 0, 1)[..., None]
bg_c, logo_c = np.array([88, 49, 40], np.float32), np.array([138, 115, 118], np.float32)
bbase = np.ones(3, np.float32)
blue = 1 + alpha * (logo_c / bg_c - 1)

# local background maps, persons removed and interpolated across
people = np.zeros((H, W), np.uint8)
for k in ("p1", "p2", "p3", "p4", "p5"): people |= (cv2.imread(f"mask_{k}.png", 0) > 0).astype(np.uint8)
people = cv2.dilate(people, np.ones((61, 61), np.uint8))
def bgmap(bright, y0, y1):
    sec = O[y0:y1, BX0 + 6:BX1 - 6].copy()
    m = people[y0:y1, BX0 + 6:BX1 - 6].copy()
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (61, 61))
    f = cv2.dilate(sec, k) if bright else cv2.erode(sec, k)
    m = cv2.dilate(m, k)  # morphology spreads person colour
    s = 4
    small = cv2.resize(f, None, fx=1 / s, fy=1 / s, interpolation=cv2.INTER_AREA)
    ms = cv2.resize(m, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    small = cv2.inpaint(np.clip(small, 0, 255).astype(np.uint8), ms, 15, cv2.INPAINT_TELEA).astype(np.float32)
    small = cv2.GaussianBlur(small, (0, 0), 6)
    full = np.zeros((H, W, 3), np.float32)
    full[y0:y1, BX0 + 6:BX1 - 6] = cv2.resize(small, (BX1 - BX0 - 12, y1 - y0), interpolation=cv2.INTER_CUBIC)
    full[y0:y1, :BX0 + 6] = full[y0:y1, BX0 + 6:BX0 + 7]      # replicate to the banner edges
    full[y0:y1, BX1 - 6:] = full[y0:y1, BX1 - 7:BX1 - 6]
    return full
bgW = bgmap(True, 0, WHITE_END); bgB = bgmap(False, WHITE_END - 40, BLUE_END)
yy, xx = np.mgrid[0:H, 0:W]
TOP, BOT = band_top(xx), band_bot(xx)
isW = (yy < TOP); isB = (yy >= TOP) & (yy < BOT)
clean = np.zeros((H, W), bool); clean[1035:1270, 598:640] = True
ys, xs = np.nonzero(clean & isB)
bgB *= np.median(O[ys, xs], 0) / np.median(bgB[ys, xs], 0) / np.median((1 + (blue - 1) * 0.3).reshape(-1, 3), 0)
S = np.where(isW[..., None], bgW * wbase, bgB * bbase)

# render lattice
for r in range(-1, 9):
    for c in range(-1, 16):
        if r in (0, 1) and c > 1: continue          # header text band: logos only on the side groups
        if c in (4, 5) and r >= 7: continue          # QR panel
        x, y = lat(c, r); x, y = int(round(x)), int(round(y))
        T = white if r <= 6 else blue
        y0, y1, x0, x1 = max(y, 0), min(y + TH, H), max(x, BX0), min(x + TW, BX1)
        if y1 <= y0 or x1 <= x0: continue
        base = wbase if r <= 6 else bbase
        sec = (isW if r <= 6 else isB)[y0:y1, x0:x1, None]
        S[y0:y1, x0:x1] *= np.where(sec, T[y0 - y:y1 - y, x0 - x:x1 - x] / base, 1)
# QR panel: the real code is half hidden, so draw a complete one (academy site)
import qrcode
q = qrcode.QRCode(version=3, border=0, error_correction=qrcode.constants.ERROR_CORRECT_M)
q.add_data("https://sobhansamadi.com"); q.make(fit=False)
mods = np.array(q.get_matrix(), np.float32)                       # 29 x 29
qx0, qy0, qs = 1062, 1060, 144
qr = cv2.resize(mods, (qs, qs), interpolation=cv2.INTER_NEAREST)
paper = np.median(O[1208:1218, 1150:1195].reshape(-1, 3), 0)
ink = np.percentile(O[1060:1200, 1140:1200].reshape(-1, 3), 3, axis=0)
px0, px1 = 1052, 1216
pan = (xx >= px0) & (xx < px1) & (yy >= TOP) & (yy < 1222)
S[pan] = paper
blk = np.zeros((H, W), np.float32); blk[qy0:qy0 + qs, qx0:qx0 + qs] = qr
blk = cv2.GaussianBlur(blk, (0, 0), 1.9)[..., None]
S = S * (1 - blk) + ink * blk
# gold base strip, following the curved bottom edge (profile taken from the clean left side)
prof = O[1279:1345, 615:640].mean(1)
for x in range(BX0, 1300):
    b0 = int(round(band_bot(x)))
    S[b0:b0 + len(prof), x] = prof
# film grain like the photo
S += np.random.default_rng(3).normal(0, 2.2, S.shape)

ban = np.zeros((H, W), bool); ban[0:BLUE_END + 50, BX0 - 2:BX1] = True
ban &= yy < (BOT + 60)
full = np.zeros((H, W), bool); full[330:, BX0 - 2:1135] = True       # whole lower banner left of person 3 (kills cast shadows)
M = ((R | full | pan) & ban).astype(np.float32)
M = cv2.GaussianBlur(M, (7, 7), 0)[..., None]
out = B * (1 - M) + S * M
out[p3] = O[p3]
cv2.imwrite("step2_banner.png", np.clip(out, 0, 255).astype(np.uint8))
print("ok")
