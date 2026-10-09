"""Put the ORIGINAL head (pixel-exact, from the reference panel) back onto the dressed panel.
usage: restore_head.py n   (p{n}.png original, d{n}.png dressed, mp{n}.png matte) -> f{n}.png"""
import sys, os, cv2, numpy as np
n = sys.argv[1]
P = cv2.imread(f"p{n}.png").astype(np.float32); D = cv2.imread(f"d{n}.png").astype(np.float32)
mat = cv2.imread(f"mp{n}.png", 0).astype(np.float32) / 255
h, w = P.shape[:2]
b, g, r = P[..., 0], P[..., 1], P[..., 2]
shirt = (b > r + 10) & (b > g - 5) & (mat > 0.5)                  # blue polo in the original
shirt = cv2.morphologyEx(shirt.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
ys = np.nonzero(shirt.sum(1) > 15)[0]; collar_top = ys.min()
# head mask: person matte above the polo, minus the polo itself
head = mat.copy(); head[shirt > 0] = 0
dark = (P.mean(2) < 70) & (np.arange(h)[:, None] > collar_top)     # polo placket / shadow inside the collar
head[dark] = 0
head *= np.clip((collar_top + 25 - np.arange(h)[:, None]) / 20.0, 0, 1)   # neck ends at the old collar
yy = np.arange(h)[:, None].astype(np.float32)

# alignment original -> dressed
if os.path.exists(f"p{n}_lm.npy") and os.path.exists(f"d{n}_lm.npy"):
    pl, dl = np.load(f"p{n}_lm.npy"), np.load(f"d{n}_lm.npy")
    idx = [33, 133, 362, 263, 1, 4, 61, 291, 152, 234, 454, 10, 70, 300]
    M, _ = cv2.estimateAffinePartial2D(pl[idx], dl[idx], method=cv2.LMEDS)
    chin_y = pl[152][1]
else:
    M = np.float32([[1, 0, 0], [0, 1, 0]]); chin_y = None
# refine with ECC on the head region (grey, blurred)
gp = cv2.GaussianBlur(cv2.cvtColor(P.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 2)
gd = cv2.GaussianBlur(cv2.cvtColor(D.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 2)
hm = (cv2.erode((head > 0.5).astype(np.uint8), np.ones((9, 9), np.uint8)) * 255)
Wm = M.astype(np.float32)
for scale_try in ([1.0] if chin_y is not None else [1.0, 1.1, 1.2, 1.3, 1.4]):
    pass
if chin_y is None:
    # profile: search scale + shift by ECC from several starts, keep the best correlation
    best = None
    ys_, xs_ = np.nonzero(head > 0.5); cyp, cxp = ys_.mean(), xs_.mean()
    md = None
    for s in (1.05, 1.15, 1.25, 1.35):
        for dx in (-40, 0, 40):
            for dy in (-60, -20, 20):
                W0 = np.float32([[s, 0, cxp * (1 - s) + dx + 60], [0, s, cyp * (1 - s) + dy - 60]])
                try:
                    cc, W1 = cv2.findTransformECC(gp, gd, W0.copy(), cv2.MOTION_AFFINE,
                                                  (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1e-5), hm, 5)
                except cv2.error:
                    continue
                if best is None or cc > best[0]: best = (cc, W1)
    print("ecc", round(best[0], 3)); Wm = best[1]
else:
    try:
        cc, Wm = cv2.findTransformECC(gp, gd, Wm.copy(), cv2.MOTION_AFFINE,
                                      (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), hm, 5)
        print("ecc", round(cc, 3))
    except cv2.error as e:
        print("ecc failed, landmarks only")
# ECC returns the map dressed->original (template P, input D): warp P with its inverse
Mi = cv2.invertAffineTransform(Wm) if chin_y is None or True else Wm
# NOTE findTransformECC(template=gp, input=gd) gives W with gd(W x) ~ gp(x); so P -> D coords needs W itself
Pw = cv2.warpAffine(P, Wm, (D.shape[1], D.shape[0]), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP) if False else None
# map original into dressed frame: x_d = W x_p
Pw = cv2.warpAffine(P, Wm, (D.shape[1], D.shape[0]), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
hw = cv2.warpAffine(head, Wm, (D.shape[1], D.shape[0]), flags=cv2.INTER_LINEAR)
# neck: keep the original neck only down to ~ just above where the new shirt collar starts
Dl = cv2.cvtColor(D.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
newshirt = ((Dl[..., 0] > 200) & (np.abs(Dl[..., 1] - 128) < 8)) | ((D[..., 0] > D[..., 2] + 25) & (Dl[..., 0] < 140))
newshirt = cv2.morphologyEx(newshirt.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
hw[newshirt > 0] = 0
hw = cv2.GaussianBlur(cv2.erode(hw, np.ones((3, 3), np.uint8)), (0, 0), 1.5)
# dressed neck below the pasted region: tone it to the original skin
skinP = (head > 0.9) & (P[..., 2] > P[..., 0] + 20) & (P.mean(2) > 80)
skinD = (newshirt == 0) & (hw < 0.1) & (D[..., 2] > D[..., 0] + 20) & (D.mean(2) > 60) & (yy > np.nonzero(hw.sum(1) > 0)[0].mean())
Lp = cv2.cvtColor(P.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
if skinD.sum() > 200:
    for c in range(3):
        Dl[..., c] = np.where(skinD, Dl[..., c] + np.median(Lp[..., c][skinP]) - np.median(Dl[..., c][skinD]) - (6 if c == 0 else 0), Dl[..., c])
    D = np.where(skinD[..., None], cv2.cvtColor(np.clip(Dl, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32), D)
out = D * (1 - hw[..., None]) + Pw * hw[..., None]
cv2.imwrite(f"f{n}.png", np.clip(out, 0, 255).astype(np.uint8))
print("ok", n)
