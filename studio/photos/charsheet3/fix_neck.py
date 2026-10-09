"""Rebuild the front-view neck from the REAL neck in p1, stretched to reach the new shirt collar."""
import cv2, numpy as np
F = cv2.imread("f1.png").astype(np.float32); P = cv2.imread("p1.png")
pl, fl = np.load("p1_lm.npy"), np.load("f1_lm.npy")
h, w = F.shape[:2]
# 1. real neck in p1 with the polo (collar + placket) inpainted away
b, g, r = [P[..., i].astype(int) for i in range(3)]
polo = ((b > r + 10) | (P.mean(2) < 70)) & (np.arange(P.shape[0])[:, None] > pl[152][1] + 4)
polo = cv2.dilate(polo.astype(np.uint8), np.ones((7, 7), np.uint8))
Pn = cv2.inpaint(P, polo, 15, cv2.INPAINT_TELEA).astype(np.float32)
# 2. map: head similarity (p1 -> f1), plus a stretch below the chin so the neck reaches the collar
M, _ = cv2.estimateAffinePartial2D(pl, fl)
cp, cf = pl[152], fl[152]
SY, SX = 1.25, 1.18                         # below-chin vertical / horizontal stretch (new collar sits lower & wider)
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
s = np.sqrt(M[0, 0] ** 2 + M[1, 0] ** 2)
dy = np.clip(yy - cf[1], 0, None)
src_y = cp[1] + (yy - cf[1]) / s - dy / s * (1 - 1 / SY)
src_x = cp[0] + (xx - cf[0]) / s / np.where(yy > cf[1], 1 + (SX - 1) * np.clip(dy / 60, 0, 1), 1)
neck_src = cv2.remap(Pn, src_x.astype(np.float32), src_y.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
# 3. where to paste: below the jaw line, not on shirt/jacket, inside the neck column
Lf = cv2.cvtColor(F.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
cloth = ((Lf[..., 0] > 200) & (np.abs(Lf[..., 1] - 128) < 8)) | (F[..., 0] > F[..., 2] + 25)
cloth = cv2.morphologyEx(cloth.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
JAW = [234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323, 454]
jaw = fl[JAW]
below = np.zeros((h, w), np.uint8)
poly = np.vstack([jaw, [[jaw[-1][0], h], [jaw[0][0], h]]]).astype(np.int32)
cv2.fillPoly(below, [poly], 1)
m = (below > 0) & ~cloth & (yy < cf[1] + 220)
# only above the first shirt/jacket pixel of each column (shirt shadows are not neck)
first = np.full(w, h)
for x in range(w):
    c = np.nonzero(cloth[int(cf[1]):, x])[0]
    if len(c): first[x] = int(cf[1]) + c[0]
m &= yy < first[None, :]
m &= (xx > jaw[:, 0].min() + 4) & (xx < jaw[:, 0].max() - 4)
m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(np.float32)
# soft at the jaw (keeps the real beard edge), crisp at the collar
jawsoft = np.clip((yy - np.interp(xx, jaw[:, 0], jaw[:, 1])) / 6.0, 0, 1)
a = (cv2.GaussianBlur(m, (0, 0), 1.0) * jawsoft)[..., None]
out = F * (1 - a) + neck_src * a
# collar casts a little shadow on the neck
cl = cv2.dilate(cloth.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32)
shadow = cv2.GaussianBlur(cl, (0, 0), 4) * m * 0.22
out *= (1 - shadow[..., None])
cv2.imwrite("f1_fixed.png", np.clip(out, 0, 255).astype(np.uint8)); print("ok")
