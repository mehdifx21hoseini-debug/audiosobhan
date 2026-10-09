"""Lock the real face (from sobhan_front.jpg) onto a generated view by landmark-based
piecewise-affine warp of the inner face, tone matched to the view's light.
usage: lock_face.py view.png out.png"""
import sys, cv2, numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="../team-edit/p4ref/face_landmarker.task"), num_faces=1))

def lms(path):
    im = mp.Image.create_from_file(path); r = det.detect(im)
    return np.array([(l.x * im.width, l.y * im.height) for l in r.face_landmarks[0]], np.float32)

src = cv2.imread("sobhan_front.jpg").astype(np.float32); sl = lms("sobhan_front.jpg")
dst = cv2.imread(sys.argv[1]).astype(np.float32); dl = lms(sys.argv[1])
h, w = dst.shape[:2]
sub = cv2.Subdiv2D((0, 0, w, h))
for p in np.clip(dl, 0, [w - 1, h - 1]): sub.insert((float(p[0]), float(p[1])))
warped = np.zeros_like(dst); cover = np.zeros((h, w), np.float32)
for t in sub.getTriangleList():
    ids = []
    for q in t.reshape(3, 2):
        d = np.linalg.norm(dl - q, axis=1); i = int(d.argmin())
        if d[i] > 1.0: break
        ids.append(i)
    if len(ids) < 3: continue
    td = dl[ids].astype(np.float32); ts = sl[ids].astype(np.float32)
    x, y, rw, rh = cv2.boundingRect(td)
    if rw <= 0 or rh <= 0: continue
    M = cv2.getAffineTransform(ts, (td - np.float32([x, y])).astype(np.float32))
    patch = cv2.warpAffine(src, M, (rw, rh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    m = np.zeros((rh, rw), np.float32); cv2.fillConvexPoly(m, np.int32(np.round(td - [x, y])), 1.0)
    ya, yb, xa, xb = max(y, 0), min(y + rh, h), max(x, 0), min(x + rw, w)
    pm = m[ya - y:yb - y, xa - x:xb - x][..., None]
    warped[ya:yb, xa:xb] = warped[ya:yb, xa:xb] * (1 - pm) + patch[ya - y:yb - y, xa - x:xb - x] * pm
    cover[ya:yb, xa:xb] = np.maximum(cover[ya:yb, xa:xb], pm[..., 0])

OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149,
        150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
fw = dl[454][0] - dl[234][0]
ov = dl[OVAL].copy()
top = [0, 1, 2, 3, 33, 34, 35, 32, 4, 31]                  # forehead points of the oval: lift toward the hairline
ov[top, 1] -= 0.10 * (dl[454][0] - dl[234][0])
mask = np.zeros((h, w), np.float32); cv2.fillConvexPoly(mask, np.int32(ov), 1.0)
mask = cv2.erode(mask, np.ones((max(3, int(0.06 * fw)),) * 2, np.uint8))
mask = cv2.GaussianBlur(mask, (0, 0), 0.055 * fw) * cover
warped = np.where(cover[..., None] > 0.5, warped, dst)        # no black outside the warped face (it skews the shading blur)
Ld = cv2.cvtColor(np.clip(dst, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
Lw = cv2.cvtColor(np.clip(warped, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
mm = mask > 0.6
for c in range(3):
    ds, ws = Ld[..., c][mm], Lw[..., c][mm]
    Lw[..., c] = (Lw[..., c] - ws.mean()) * (0.5 + 0.5 * ds.std() / max(ws.std(), 1e-3)) + ds.mean()
shade = cv2.GaussianBlur(Ld[..., 0], (0, 0), 0.25 * fw) - cv2.GaussianBlur(Lw[..., 0], (0, 0), 0.25 * fw)
Lw[..., 0] += shade * 0.8
warped = cv2.cvtColor(np.clip(Lw, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
out = dst * (1 - mask[..., None]) + warped * mask[..., None]
cv2.imwrite(sys.argv[2], np.clip(out, 0, 255).astype(np.uint8))
x0, y0 = int(dl[:, 0].min() - 0.3 * fw), int(dl[:, 1].min() - 0.5 * fw)
x1, y1 = int(dl[:, 0].max() + 0.3 * fw), int(dl[:, 1].max() + 0.2 * fw)
cv2.imwrite("/tmp/claude-0/-home-user-audiosobhan/545c7dd5-268d-5bb8-892d-0cd1ca011ec2/scratchpad/lock_" + sys.argv[2].split(".")[0] + ".jpg",
            np.hstack([dst[y0:y1, x0:x1], np.clip(out, 0, 255)[y0:y1, x0:x1]]).astype(np.uint8))
print("ok")
