"""User's suit photo on the left of Sobhan, but standing on legs/shoes that were
photographed in this room (person 1's legs from the original shot), so the
perspective, light and floor contact are real.  usage: place_legs.py base.jpg out.jpg"""
import sys, cv2, numpy as np
base = cv2.imread(sys.argv[1]).astype(np.float32)
orig = cv2.imread("original.jpg").astype(np.float32)
lama = cv2.imread("step1_lama.png").astype(np.float32)          # same frame with p1/p2 removed
H, W = base.shape[:2]

# ---------------------------------------------------------------- upper body (user photo)
P = cv2.imread("newguy/person3.png").astype(np.float32)
A = cv2.imread("newguy/person3_alpha.png", 0).astype(np.float32) / 255
ys, xs = np.nonzero(A > 0.5); top, bot, left = ys.min(), ys.max(), xs.min()
H_TARGET, FEET_Y, LEFT_X = 1352, 1566, 836
k = H_TARGET / (bot - top)
HEM = 662                                                   # source row just under the jacket hem
A[HEM:] = 0
A[HEM - 6:HEM] *= np.linspace(1, 0, 6)[:, None]
P = cv2.resize(P[top:bot + 1, left:], None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
A = cv2.resize(A[top:bot + 1, left:], (P.shape[1], P.shape[0]), interpolation=cv2.INTER_AREA)
# grade to the group (person 5 stats)
ref = cv2.cvtColor(base.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)[cv2.imread("mask_p5.png", 0) > 0]
L = cv2.cvtColor(P.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32); S = L[A > 0.9]
for c, wgt in ((0, 0.85), (1, 0.9), (2, 0.9)):
    L[..., c] = (L[..., c] - S[:, c].mean()) * (1 - wgt + wgt * ref[:, c].std() / S[:, c].std()) + \
                (1 - wgt) * S[:, c].mean() + wgt * ref[:, c].mean()
P = cv2.cvtColor(np.clip(L, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
P = P * 0.93 + 0.07 * 200
P = cv2.GaussianBlur(P, (0, 0), 0.85); A = cv2.GaussianBlur(A, (0, 0), 0.9)
P += np.random.default_rng(11).normal(0, 2.6, P.shape)
y0 = FEET_Y - int(round((bot - top) * k)); x0 = LEFT_X
hem_y = y0 + (HEM - top) * k
hip_cx = x0 + (395.5 - left) * k                           # centre of the legs at the hem

# ---------------------------------------------------------------- legs (person 1, original frame)
m1 = cv2.erode((cv2.imread("mask_p1.png", 0) > 0).astype(np.uint8), np.ones((5, 5), np.uint8))
LY0, LY1, LX0, LX1 = 1010, 1650, 600, 910
legs = orig[LY0:LY1, LX0:LX1]; la = m1[LY0:LY1, LX0:LX1].astype(np.float32)
la = cv2.GaussianBlur(la, (0, 0), 0.9)
# real floor shadow of those feet: original / clean floor, blurred to drop the carpet texture
valid = (cv2.dilate((cv2.imread("mask_p1.png", 0) > 0).astype(np.uint8), np.ones((13, 13), np.uint8))[LY0:LY1, LX0:LX1] == 0).astype(np.float32)
raw = np.clip(cv2.GaussianBlur(orig[LY0:LY1, LX0:LX1].mean(2), (0, 0), 3) /
              np.maximum(cv2.GaussianBlur(lama[LY0:LY1, LX0:LX1].mean(2), (0, 0), 3), 1), 0.3, 1.2)
ratio = np.clip(cv2.GaussianBlur(raw * valid, (0, 0), 6) / np.maximum(cv2.GaussianBlur(valid, (0, 0), 6), 1e-3), 0.35, 1.0)
ratio[: int((1480 - LY0))] = 1.0                            # floor only (below the hem of the trousers)
near = cv2.dilate(m1[LY0:LY1, LX0:LX1], cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 41))).astype(np.float32)
near[: int(1480 - LY0)] = 0
near = cv2.GaussianBlur(near, (0, 0), 12)                     # only right around the shoes, feathered
ratio = 1 - (1 - ratio) * near
kl = (FEET_Y - hem_y + 14) / (1563 - LY0)                  # legs reach from under the jacket to the floor
legs = cv2.resize(legs, None, fx=kl, fy=kl, interpolation=cv2.INTER_CUBIC)
la = cv2.resize(la, (legs.shape[1], legs.shape[0]))
ratio = cv2.resize(ratio, (legs.shape[1], legs.shape[0]))
lh, lw = la.shape
lx = int(round(hip_cx - (752 - LX0) * kl)); ly = int(round(FEET_Y - (1563 - LY0) * kl))

out = base.copy()
# floor shadow first, then legs, then the upper body over the hem
sl = (slice(ly, ly + lh), slice(lx, lx + lw))
out[sl] *= ratio[..., None]
# contact shadow following the soles + soft ambient shadow around the feet
sole = np.zeros((H, W), np.float32); amb = np.zeros((H, W), np.float32)
band0 = int(lh * 0.85)
for cx in range(lw):
    r = np.nonzero(la[band0:, cx] > 0.5)[0]
    if len(r):
        yb = ly + band0 + r.max()
        cv2.circle(sole, (lx + cx, yb), 3, 1, -1); cv2.circle(amb, (lx + cx, yb - 6), 16, 1, -1)
sh = np.maximum(cv2.GaussianBlur(sole, (0, 0), 2.2) * 0.8, cv2.GaussianBlur(amb, (0, 0), 12) * 0.45)
out *= (1 - sh[..., None])
out[sl] = out[sl] * (1 - la[..., None]) + legs * la[..., None]
h, w = P.shape[:2]
a = A[..., None]
out[y0:y0 + h, x0:x0 + w] = out[y0:y0 + h, x0:x0 + w] * (1 - a) + P * a
# Sobhan stays in front
front = cv2.GaussianBlur(cv2.imread("mask_p3.png", 0).astype(np.float32) / 255, (0, 0), 0.7)[..., None]
out = out * (1 - front) + base * front
cv2.imwrite(sys.argv[2], np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
print("ok legs scale", round(kl, 3), "at", lx, ly)
