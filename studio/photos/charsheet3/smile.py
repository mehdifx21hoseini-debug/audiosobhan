"""Smiling front view in the blue blazer: real smiling head (src6) on the front-view body."""
import cv2, numpy as np
B = cv2.imread("f1_final.png").astype(np.float32); D = cv2.imread("d1.png").astype(np.float32)
S = cv2.imread("smile_src.jpg").astype(np.float32)
ms = cv2.imread("smile_matte.png", 0).astype(np.float32) / 255
sl, bl = np.load("smile_lm.npy"), np.load("f1f_lm.npy")
h, w = B.shape[:2]; yy = np.arange(h)[:, None].astype(np.float32); xx = np.arange(w)[None, :].astype(np.float32)
# align on stable points (eyes, nose bridge, temples, forehead) - not mouth/chin, which move when smiling
idx = [33, 133, 362, 263, 168, 6, 197, 234, 454, 10, 70, 300, 105, 334]
M, _ = cv2.estimateAffinePartial2D(sl[idx], bl[idx], method=cv2.LMEDS)
Sw = cv2.warpAffine(S, M, (w, h), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
aw = cv2.warpAffine(ms, M, (w, h), flags=cv2.INTER_LINEAR)
swl = (M[:, :2] @ sl.T).T + M[:, 2]                       # smile landmarks in B coords
# colour: lamp-lit selfie -> grade the head to the front view's face (LAB stats on cheeks/forehead)
def skin(img, lm):
    m = np.zeros((h, w), bool)
    for i in (50, 280, 151, 9):
        cx, cy = lm[i].astype(int); m[cy - 7:cy + 7, cx - 7:cx + 7] = True
    return m
Lb = cv2.cvtColor(np.clip(B, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
Ls = cv2.cvtColor(np.clip(Sw, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
mb, mS = skin(B, bl), skin(Sw, swl)
for c in range(3):
    Ls[..., c] = (Ls[..., c] - Ls[..., c][mS].mean()) * (0.85 + 0.15 * Lb[..., c][mb].std() / max(Ls[..., c][mS].std(), 1e-3)) + Lb[..., c][mb].mean()
Sw = cv2.cvtColor(np.clip(Ls, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
# head region: matte, cut a little under the smiling chin, fading into the body's neck
chin = swl[152]; face_h = swl[152][1] - swl[10][1]
cut = chin[1] + 0.08 * face_h
head = aw * np.clip((cut - yy) / (0.05 * face_h), 0, 1)
# below the ears keep only the jaw/chin width (no selfie shoulders/polo)
jaw_half = 0.5 * np.linalg.norm(swl[454] - swl[234]) * 1.02
ear_y = 0.5 * (swl[177][1] + swl[401][1])
JAW = [234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323, 454]
inside = np.zeros((h, w), np.uint8)
pj = swl[JAW].copy(); pj[:, 1] += 3                       # include the beard edge under the jaw
cv2.fillPoly(inside, [np.vstack([[[pj[0][0] - 40, 0]], pj, [[pj[-1][0] + 40, 0]]]).astype(np.int32)], 1)
lim = np.where(yy > ear_y, inside.astype(np.float32), 1.0)
head *= cv2.GaussianBlur(lim, (0, 0), 1.5)
# body behind: remove the old head (and anything above the shoulders) -> backdrop plate
md = cv2.imread("md1.png", 0).astype(np.float32) / 255
ear_lo = max(bl[177][1], bl[401][1]) + 25
oldhead = ((md > 0.3) | (aw > 0.3)) & (yy < ear_lo)
jacket = (B[..., 0] > B[..., 2] + 25) | ((cv2.cvtColor(np.clip(B,0,255).astype(np.uint8), cv2.COLOR_BGR2LAB)[..., 0] > 200))
oldhead &= ~jacket
old_chin_y_guard = h
plate = cv2.inpaint(np.clip(B, 0, 255).astype(np.uint8), cv2.dilate(oldhead.astype(np.uint8), np.ones((9, 9), np.uint8)), 12, cv2.INPAINT_TELEA).astype(np.float32)
plate = cv2.GaussianBlur(plate, (0, 0), 3) + np.random.default_rng(1).normal(0, 1.3, plate.shape)
zone = cv2.GaussianBlur(cv2.dilate(oldhead.astype(np.uint8), np.ones((13, 13), np.uint8)).astype(np.float32), (0, 0), 4)
zone[yy[:, 0] > old_chin_y_guard] = 0 if False else zone[yy[:, 0] > old_chin_y_guard]
base = B * (1 - zone[..., None]) + plate * zone[..., None]
# neck under the new chin stays the body's neck (already the real neck tone); if the smiling jaw is
# higher than the old one, the old beard edge would show: fill it from the neck below
old_chin = bl[152][1]
gap = (yy > cut - 2) & (yy < old_chin + 6) & (np.abs(xx - chin[0]) < 0.42 * face_h) & (head < 0.5)
if gap.any():
    src = np.roll(base, -int(old_chin + 10 - cut), axis=0)
    g = cv2.GaussianBlur(gap.astype(np.float32), (0, 0), 2)[..., None]
    base = base * (1 - g) + src * g
# de-fringe matte edge from the room behind the selfie
edge = (head > 0.03) & (head < 0.97)
bgS = cv2.GaussianBlur(Sw, (0, 0), 8)
Sd = Sw.copy()
Sd[edge] = np.clip((Sw[edge] - bgS[edge] * (1 - head[edge][:, None]) * 0.6) / np.maximum(1 - (1 - head[edge][:, None]) * 0.6, 0.3), 0, 255)
hd = cv2.GaussianBlur(head, (0, 0), 0.7)[..., None]
out = base * (1 - hd) + Sd * hd
cv2.imwrite("f3_smile.png", np.clip(out, 0, 255).astype(np.uint8)); print("ok")
