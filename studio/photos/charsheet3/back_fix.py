"""Back view: restore the real back of the head (p3) onto the dressed render, match the blazer colour to the front views."""
import cv2, numpy as np
P = cv2.imread("p3.png").astype(np.float32); D = cv2.imread("d3.png").astype(np.float32)
F = cv2.imread("f1_final.png").astype(np.float32)
mat = cv2.imread("mp3.png", 0).astype(np.float32) / 255
h, w = P.shape[:2]; yy = np.arange(h)[:, None]
b, g, r = P[..., 0], P[..., 1], P[..., 2]
polo = (b > r + 10) & (mat > 0.5)
top_polo = np.nonzero(cv2.morphologyEx(polo.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)).sum(1) > 30)[0].min()
head = mat * (yy < top_polo - 6)
# align p3 -> d3 on the head (ECC, affine)
gp = cv2.GaussianBlur(cv2.cvtColor(P.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 2)
gd = cv2.GaussianBlur(cv2.cvtColor(D.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 2)
hm = (cv2.erode((head > 0.5).astype(np.uint8), np.ones((9, 9), np.uint8)) * 255)
best = None
for s in (0.95, 1.0, 1.05):
    for dy in (-30, -10, 10):
        W0 = np.float32([[s, 0, w / 2 * (1 - s)], [0, s, dy]])
        try:
            cc, W1 = cv2.findTransformECC(gp, gd, W0.copy(), cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 150, 1e-6), hm, 5)
        except cv2.error:
            continue
        if best is None or cc > best[0]: best = (cc, W1)
print("ecc", round(best[0], 3))
Wm = best[1]
Pw = cv2.warpAffine(P, Wm, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
hw = cv2.warpAffine(head, Wm, (w, h))
# keep the render's white shirt collar & blazer over the neck
Dl = cv2.cvtColor(D.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
cloth = ((Dl[..., 0] > 200) & (np.abs(Dl[..., 1] - 128) < 8)) | (D[..., 0] > D[..., 2] + 25)
cloth = cv2.morphologyEx(cloth.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
hw[cloth > 0] = 0
# remove the render's own head where the real head doesn't reach (inpaint background)
md = (cv2.GaussianBlur(gd, (0, 0), 1) < 150) & (yy < np.nonzero(cloth.sum(1) > 30)[0].min()) & ~(cloth > 0)
extra = (md & (hw < 0.5)).astype(np.uint8)
extra = cv2.morphologyEx(extra, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
Dc = cv2.inpaint(np.clip(D, 0, 255).astype(np.uint8), cv2.dilate(extra, np.ones((5, 5), np.uint8)), 9, cv2.INPAINT_TELEA).astype(np.float32)
hw = cv2.GaussianBlur(hw, (0, 0), 1.2)
out = Dc * (1 - hw[..., None]) + Pw * hw[..., None]
# blazer colour to match the front views
Fl = cv2.cvtColor(F.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
fj = (F[..., 0] > F[..., 2] + 25); Ol = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
oj = (out[..., 0] > out[..., 2] + 25) & (yy > np.nonzero(cloth.sum(1) > 30)[0].min())
ojs = cv2.GaussianBlur(oj.astype(np.float32), (0, 0), 1.2)
for c in range(3):
    t = (Ol[..., c] - Ol[..., c][oj].mean()) * min(1.0, Fl[..., c][fj].std() / max(Ol[..., c][oj].std(), 1e-3)) + Fl[..., c][fj].mean()
    Ol[..., c] = Ol[..., c] * (1 - ojs) + t * ojs
out = cv2.cvtColor(np.clip(Ol, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
cv2.imwrite("f4_back.png", out); print("ok")
