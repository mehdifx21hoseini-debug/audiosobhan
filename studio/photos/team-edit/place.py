"""Place the new team member. usage: place.py base.jpg out.jpg [left]  (left = in place of the removed pair)"""
import sys, cv2, numpy as np
base = cv2.imread(sys.argv[1]).astype(np.float32)
LEFT = len(sys.argv) > 3 and sys.argv[3] == "left"
tag = "person2" if LEFT else "person"
P = cv2.imread(f"newguy/{tag}.png").astype(np.float32)
A = cv2.imread(f"newguy/{tag}_alpha.png", 0).astype(np.float32) / 255
ys, xs = np.nonzero(A > 0.5)
top, bot, left, right = ys.min(), ys.max(), xs.min(), xs.max()
H_TARGET, FEET_Y, LEFT_X = (1292, 1568, 806) if LEFT else (1318, 1597, 2018)                    # p5: ~1320 px tall, feet at ~1590
k = H_TARGET / (bot - top)
P = cv2.resize(P[top:bot + 1, left:right + 1], None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
A = cv2.resize(A[top:bot + 1, left:right + 1], (P.shape[1], P.shape[0]), interpolation=cv2.INTER_AREA)
# grade to the group's look: LAB stats of person 5 (dark suit + face), partial transfer
ref_m = cv2.imread("mask_p5.png", 0) > 0
R = cv2.cvtColor(base.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)[ref_m]
L = cv2.cvtColor(P.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
pm = A > 0.9; S = L[pm]
for c, wgt in ((0, 0.8), (1, 0.7), (2, 0.7)):
    L[..., c] = (L[..., c] - S[:, c].mean()) * (1 - wgt + wgt * R[:, c].std() / S[:, c].std()) + \
                (1 - wgt) * S[:, c].mean() + wgt * R[:, c].mean()
P = cv2.cvtColor(np.clip(L, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
P = P * 0.93 + 0.07 * 200                                        # lifted blacks like the rest
P = cv2.GaussianBlur(P, (0, 0), 0.55)                           # same softness as the photo
P += np.random.default_rng(11).normal(0, 2.6, P.shape)
h, w = P.shape[:2]; y0 = FEET_Y - h; x0 = LEFT_X
H, W = base.shape[:2]
# soft contact shadow on the carpet + faint ambient occlusion
sh = np.zeros((H, W), np.float32)
cv2.ellipse(sh, (x0 + w // 2, FEET_Y - 6), (int(w * 0.46), 22), 0, 0, 360, 1, -1)
sh = cv2.GaussianBlur(sh, (0, 0), 14) * 0.55
foot = np.zeros((H, W), np.float32)
cv2.ellipse(foot, (x0 + w // 2, FEET_Y - 4), (int(w * 0.36), 9), 0, 0, 360, 1, -1)
sh = np.maximum(sh, cv2.GaussianBlur(foot, (0, 0), 4) * 0.75)
out = base * (1 - sh[..., None])
# person
xa, xb = max(x0, 0), min(x0 + w, W); ya, yb = max(y0, 0), min(y0 + h, H)
a = A[ya - y0:yb - y0, xa - x0:xb - x0][..., None]
out[ya:yb, xa:xb] = out[ya:yb, xa:xb] * (1 - a) + P[ya - y0:yb - y0, xa - x0:xb - x0] * a
# people in front of him (Sobhan overlaps his right shoulder)
if LEFT:
    front = cv2.imread("mask_p3.png", 0).astype(np.float32) / 255
    front = cv2.GaussianBlur(front, (0, 0), 0.7)[..., None]
    out = out * (1 - front) + base * front
cv2.imwrite(sys.argv[2], np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
print("ok", (x0, y0, w, h))
