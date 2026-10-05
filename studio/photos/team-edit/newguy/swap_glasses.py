"""Replace the sunglasses face of the added subject with his reference (clear glasses).
Was: Move person 4's facial features toward his reference photo (landmark warp + tone match).
usage: faceswap.py base.jpg out.jpg [strength 0..1] [lift]"""
import sys, cv2, numpy as np
STR = float(sys.argv[3]) if len(sys.argv) > 3 else 0.8
LIFT = float(sys.argv[4]) if len(sys.argv) > 4 else 6.0
CX0, CY0, CX1, CY1, S = 300, 30, 540, 270, 4
base = cv2.imread(sys.argv[1])
dst = cv2.resize(base[CY0:CY1, CX0:CX1], None, fx=S, fy=S, interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
src = cv2.imread("ref_glasses.jpg").astype(np.float32)
dl, sl = np.load("uf_head4x_lm.npy"), np.load("ref_glasses_lm.npy")
h, w = dst.shape[:2]

# piecewise-affine warp of the reference face onto his face geometry
rect = (0, 0, w, h); sub = cv2.Subdiv2D(rect)
for p in dl: sub.insert((float(np.clip(p[0], 0, w - 1)), float(np.clip(p[1], 0, h - 1))))
index = {(round(float(p[0]), 1), round(float(p[1]), 1)): i for i, p in enumerate(np.clip(dl, 0, [w - 1, h - 1]))}
warped = np.zeros_like(dst); cover = np.zeros((h, w), np.float32)
for t in sub.getTriangleList():
    tri = t.reshape(3, 2)
    ids = []
    for q in tri:
        d = np.linalg.norm(dl - q, axis=1); i = int(d.argmin())
        if d[i] > 1.0: break
        ids.append(i)
    if len(ids) < 3: continue
    td, ts = dl[ids].astype(np.float32), sl[ids].astype(np.float32)
    r = cv2.boundingRect(td); x, y, rw, rh = r
    if rw <= 0 or rh <= 0: continue
    M = cv2.getAffineTransform(ts.astype(np.float32), (td - np.float32([x, y])).astype(np.float32))
    patch = cv2.warpAffine(src, M, (rw, rh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    m = np.zeros((rh, rw), np.float32); cv2.fillConvexPoly(m, np.int32(np.round(td - [x, y])), 1.0)
    ya, yb, xa, xb = max(y, 0), min(y + rh, h), max(x, 0), min(x + rw, w)
    pm = m[ya - y:yb - y, xa - x:xb - x][..., None]
    warped[ya:yb, xa:xb] = warped[ya:yb, xa:xb] * (1 - pm) + patch[ya - y:yb - y, xa - x:xb - x] * pm
    cover[ya:yb, xa:xb] = np.maximum(cover[ya:yb, xa:xb], pm[..., 0])

# face mask: inner face (brows -> chin), feathered, keeps his hair, ears and outer beard line
OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149,
        150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
mask = np.zeros((h, w), np.float32); cv2.fillConvexPoly(mask, np.int32(dl[OVAL]), 1.0)
top_y = dl[[70, 63, 105, 66, 107, 336, 296, 334, 293, 300]][:, 1].min() - 14 * S   # above the sunglasses
mask[: int(top_y)] = 0
mask = cv2.erode(mask, np.ones((int(4 * S), int(4 * S)), np.uint8))
mask = cv2.GaussianBlur(mask, (0, 0), 7 * S / 3) * cover

# tone: reference skin re-lit to this room (his own lighting), a touch brighter
Ld = cv2.cvtColor(np.clip(dst, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
Lw = cv2.cvtColor(np.clip(warped, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
mm = mask > 0.6
eye_lo = dl[[1, 4, 5]][:, 1].mean()                      # nose: below the glasses
mm &= (np.arange(h)[:, None] > eye_lo)                   # tone from cheeks/mouth/chin only
mm_d = mm & (Ld[..., 1] > 133) & (Ld[..., 0] > np.median(Ld[..., 0][mm]))   # bare skin, not beard
mm_w = mm & (Lw[..., 1] > 133) & (Lw[..., 0] > np.median(Lw[..., 0][mm]))
for c in range(3):
    ds, ws = Ld[..., c][mm_d], Lw[..., c][mm_w]
    tgt_mean = ds.mean() + (LIFT if c == 0 else 0)
    Lw[..., c] = (Lw[..., c] - ws.mean()) * (ds.std() / max(ws.std(), 1e-3)) * (0.95 if c == 0 else 0.9) + tgt_mean
# low-frequency shading from his photo (same light direction as the room)
shade = cv2.GaussianBlur(Ld[..., 0], (0, 0), 10 * S) - cv2.GaussianBlur(Lw[..., 0], (0, 0), 10 * S)
Lw[..., 0] += shade * 0.0
warped = cv2.cvtColor(np.clip(Lw, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
a = (mask * STR)[..., None]
res = dst * (1 - a) + warped * a
small = cv2.resize(res, (CX1 - CX0, CY1 - CY0), interpolation=cv2.INTER_AREA)
am = cv2.resize(a[..., 0], (CX1 - CX0, CY1 - CY0), interpolation=cv2.INTER_AREA)[..., None]
small += np.random.default_rng(3).normal(0, 2.0, small.shape) * (am > 0.02)
out = base.astype(np.float32)
out[CY0:CY1, CX0:CX1] = out[CY0:CY1, CX0:CX1] * (1 - am) + small * am
cv2.imwrite(sys.argv[2], np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
cv2.imwrite("/tmp/claude-0/-home-user-audiosobhan/545c7dd5-268d-5bb8-892d-0cd1ca011ec2/scratchpad/fsg.jpg",
            np.hstack([base[CY0:CY1, CX0:CX1], np.clip(out[CY0:CY1, CX0:CX1], 0, 255).astype(np.uint8)]))
print("ok")
