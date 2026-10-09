"""Clean head silhouette for the front view: remove the dressed head beyond the real head
(background reconstructed), then lay the real head with its full soft matte (ears intact)."""
import cv2, numpy as np
F = cv2.imread("f1_fixed.png").astype(np.float32); D = cv2.imread("d1.png").astype(np.float32)
P = cv2.imread("p1.png").astype(np.float32)
mp_ = cv2.imread("mp1.png", 0).astype(np.float32) / 255; md = cv2.imread("md1.png", 0).astype(np.float32) / 255
pl, fl = np.load("p1_lm.npy"), np.load("f1_lm.npy")
h, w = F.shape[:2]; yy = np.arange(h)[:, None]
M, _ = cv2.estimateAffinePartial2D(pl, fl)
Pw = cv2.warpAffine(P, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
aw = cv2.warpAffine(mp_, M, (w, h), flags=cv2.INTER_LINEAR)
chin = fl[152][1]; ear_lo = max(fl[177][1], fl[401][1]) + 25          # bottom of the ears / jaw corners
zone = (yy < ear_lo).astype(np.float32)                              # head band only (above the shoulders)
zone = cv2.GaussianBlur(zone, (0, 0), 6)
# 1) background plate: dressed image with everything person-like in the head band inpainted to backdrop
person = ((md > 0.3) | (aw > 0.3)) & (yy < ear_lo)
person = cv2.dilate(person.astype(np.uint8), np.ones((7, 7), np.uint8))
plate = cv2.inpaint(np.clip(D, 0, 255).astype(np.uint8), person, 12, cv2.INPAINT_TELEA).astype(np.float32)
plate = cv2.GaussianBlur(plate, (0, 0), 3)
plate += np.random.default_rng(1).normal(0, 1.3, plate.shape)
# 2) real head with its soft matte, colour of P's backdrop is irrelevant now (matte edges only)
#    tiny de-fringe: pull edge pixels toward the head colour, not P's grey
edge = (aw > 0.05) & (aw < 0.95)
Pd = Pw.copy()
bgP = np.float32([179, 179, 179])
Pd[edge] = np.clip((Pw[edge] - bgP * (1 - aw[edge][:, None])) / np.maximum(aw[edge][:, None], 0.25), 0, 255)
head_band = plate * (1 - aw[..., None]) + Pd * aw[..., None]
# 3) use it only in the head band, the rest (neck, shirt, jacket) stays as fixed
k = zone[..., None]
out = F * (1 - k) + head_band * k
cv2.imwrite("f1_final.png", np.clip(out, 0, 255).astype(np.uint8)); print("ok", ear_lo)
