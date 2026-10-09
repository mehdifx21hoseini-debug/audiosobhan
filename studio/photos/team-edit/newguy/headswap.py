"""Put the real head (flipped photo) on the generated suit body."""
import cv2, numpy as np, sys
src = cv2.imread("source_flipped.jpg").astype(np.float32)
body = cv2.imread("body_s29.png").astype(np.float32)
mh = cv2.imread("m_head.png", 0) > 0
mh = cv2.morphologyEx(mh.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))) > 0
ff = (~mh).astype(np.uint8); cv2.floodFill(ff, None, (0, 0), 0)   # fill holes (lenses)
mh = mh | (ff > 0)
lum = src.mean(2)
hull = np.zeros(mh.shape, np.uint8)
cv2.fillPoly(hull, [cv2.convexHull(np.argwhere(mh)[:, ::-1].astype(np.int32))], 1)
glasses = np.zeros_like(mh); glasses[170:240, :] = True
mh |= glasses & (hull > 0) & (lum < 110)
mh = cv2.morphologyEx(mh.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 0
b_, g_, r_ = src[..., 0], src[..., 1], src[..., 2]
mh &= ~((g_ > r_ + 10) & (b_ > r_ + 10))                  # drop the teal t-shirt
mh &= ~((g_ > r_ + 4) & (g_ > b_ + 4))                    # and foliage behind the ear
K = float(sys.argv[1]) if len(sys.argv) > 1 else 1.05
SRC_CHIN, GEN_CHIN = np.array([180, 302]), np.array([388, 224])
NECK_KEEP = 45                                    # px of real neck kept below the chin (source px)
a = mh.astype(np.float32)
yy = np.arange(a.shape[0])[:, None]
a *= np.clip((SRC_CHIN[1] + NECK_KEEP - yy) / 14 + 0.5, 0, 1)   # fade the neck out
a = cv2.GaussianBlur(a, (0, 0), 1.2)
M = np.float32([[K, 0, GEN_CHIN[0] - K * SRC_CHIN[0]], [0, K, GEN_CHIN[1] - K * SRC_CHIN[1]]])
h, w = body.shape[:2]
hw = cv2.warpAffine(src, M, (w, h), flags=cv2.INTER_CUBIC)
aw = cv2.warpAffine(a, M, (w, h))
aw[230:, :334] = 0                                       # trapezius from the t-shirt photo
aw = cv2.GaussianBlur(aw, (0, 0), 0.7)[..., None]
# generated head must disappear where the real one doesn't cover: paint body bg there first
bm = cv2.imread("m_body.png", 0) > 0
gen_head = np.zeros((h, w), bool); gen_head[:248] = True     # generated face/neck above the collar
bg = np.median(body[5:40, 5:120].reshape(-1, 3), 0)
base = body.copy(); base[gen_head & bm] = bg
# neck underlay (shadow side under the turned jaw, down into the collar)
neck_c = np.median(src[300:325, 130:170].reshape(-1, 3), 0)
poly = np.array([(333, 252), (328, 228), (372, 214), (418, 192), (444, 212), (446, 252)], np.int32)
nm = np.zeros((h, w), np.float32); cv2.fillPoly(nm, [poly], 1.0)
nm = cv2.GaussianBlur(nm, (0, 0), 2.5)[..., None]
shadow = np.clip((np.arange(h)[:, None] - 190) / 60.0, 0, 1)[..., None]       # darker right under the jaw
neck_tone = neck_c * (0.55 + 0.25 * shadow)
nm[:] = 0
out = base * (1 - aw) + hw * aw
# shirt collar / suit drawn back over the neck
gl = body.mean(2)
over = bm & ~gen_head & ((gl > 185) | (gl < 70))
over = cv2.GaussianBlur(over.astype(np.float32), (0, 0), 0.8)[..., None]
out = out * (1 - over) + body * over
cv2.imwrite("swap.png", np.clip(out, 0, 255).astype(np.uint8))
# alpha of the whole new person (body below the chin + real head)
A = np.maximum(np.maximum((bm & ~gen_head).astype(np.float32), aw[..., 0]), nm[..., 0])
cv2.imwrite("swap_alpha.png", (np.clip(A, 0, 1) * 255).astype(np.uint8))
cv2.imwrite(sys.argv[2] if len(sys.argv) > 2 else "/tmp/sw.jpg", np.clip(out, 0, 255).astype(np.uint8)[0:520, 170:600])
