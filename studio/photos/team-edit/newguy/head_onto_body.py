"""Put the reference person's whole head (hair, face, neck) on the suited body in user_full.jpg.
Similarity transform from facial landmarks; the body's collar/jacket is drawn back over the neck.
-> user_full_head.jpg"""
import cv2, numpy as np
body = cv2.imread("user_full.jpg").astype(np.float32)
ref = cv2.imread("ref_front.jpg").astype(np.float32)
mr = (cv2.imread("m_ref_head.png", 0) > 0).astype(np.uint8)
mr = cv2.morphologyEx(mr, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
inv = (1 - mr).astype(np.uint8); cv2.floodFill(inv, None, (0, 0), 0); mr |= inv
b, g, r = [ref[..., i] for i in range(3)]
mr[(b > r + 15) & (b > g)] = 0                          # drop the blue t-shirt
tl = np.load("uf_head4x_lm.npy") / 4 + np.float32([300, 30])   # target landmarks in body coords
rl = np.load("ref_front_lm.npy")
idx = [33, 133, 362, 263, 1, 4, 61, 291, 152, 234, 454, 10]
M, _ = cv2.estimateAffinePartial2D(rl[idx], tl[idx], method=cv2.LMEDS)
# the old head was bigger than the face-landmark fit implies: grow ~12% about the chin, and halve the tilt
chin = tl[152]
ang = np.arctan2(M[1, 0], M[0, 0]) * 0.5; sc = np.sqrt(M[0, 0] ** 2 + M[1, 0] ** 2) * 1.12
rc = rl[152]
M = np.float32([[sc * np.cos(ang), -sc * np.sin(ang), 0], [sc * np.sin(ang), sc * np.cos(ang), 0]])
M[:, 2] = chin + np.float32([9, 3]) - M[:, :2] @ rc      # centre the jaw over the collar/neck
# keep only a short neck below the chin (it ends inside the collar)
face_h = rl[152][1] - rl[10][1]
cut = int(rc[1] + 0.06 * face_h)                          # new head ends just under the chin ...
fade = np.clip((cut - np.arange(mr.shape[0])[:, None]) / (0.10 * face_h) + 0.5, 0, 1)   # ... fading into the body's own neck
mr = mr.astype(np.float32) * fade
# below the jawline keep only a neck strip under the chin (no side neck/shadow from the selfie)
JAW = [234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323, 454]
above = np.zeros(mr.shape, np.float32)
pts = rl[JAW].astype(np.int32)
poly = np.vstack([[[pts[0][0], 0]], pts, [[pts[-1][0], 0]]])
cv2.fillPoly(above, [poly], 1.0)
cv2.rectangle(above, (0, 0), (mr.shape[1], int(rl[[132, 361]][:, 1].max())), 1.0, -1)   # hair, forehead and ears
strip = np.zeros(mr.shape, np.float32)
fw = rl[454][0] - rl[234][0]
cv2.rectangle(strip, (int(rc[0] - 0.22 * fw), int(rc[1] - 0.1 * face_h)), (int(rc[0] + 0.22 * fw), mr.shape[0]), 1.0, -1)
keep = np.maximum(above, strip)
keep = cv2.GaussianBlur(keep, (0, 0), 0.012 * face_h)
mr = mr * keep
s = np.sqrt(M[0, 0] ** 2 + M[1, 0] ** 2)
print("scale", round(s, 3), "rot deg", round(np.degrees(np.arctan2(M[1, 0], M[0, 0])), 2))
H, W = body.shape[:2]
head = cv2.warpAffine(ref, M, (W, H), flags=cv2.INTER_AREA)
ha = cv2.warpAffine(mr, M, (W, H), flags=cv2.INTER_LINEAR)
ha = cv2.GaussianBlur(cv2.erode(ha, np.ones((2, 2), np.uint8)), (0, 0), 0.8)

# remove the old head: white background where the old person (above the collar) is not covered by the new head
mu = cv2.imread("m_user.png", 0) > 0
chin_y = int(tl[152][1])
old_head = mu.copy(); old_head[chin_y - 25:] = False
canvas = body.copy()
canvas[old_head] = 255
# body's own neck (inside the collar) re-toned to the new face's skin
neck = mu & (np.arange(H)[:, None] >= chin_y - 25) & (np.arange(H)[:, None] < chin_y + 70) & (body[..., 2] > body[..., 0] + 12) & (body.mean(2) > 60)
face_skin = (ha > 0.9) & (head[..., 2] > head[..., 0] + 15) & (head.mean(2) > 90) & (np.arange(H)[:, None] < chin_y - 30)
Lb_ = cv2.cvtColor(np.clip(canvas, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
Lh_ = cv2.cvtColor(np.clip(head, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
for c in range(3):
    d = np.median(Lh_[..., c][face_skin]) - np.median(Lb_[..., c][neck]) - (8 if c == 0 else 0)   # necks sit a bit darker
    Lb_[..., c] = np.where(neck, Lb_[..., c] + d, Lb_[..., c])
canvas = np.where(neck[..., None], cv2.cvtColor(np.clip(Lb_, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32), canvas)
# fill the old neck gap between chin and collar with skin later covered by the new neck; body over neck:
yy = np.arange(H)[:, None]
lum = body.mean(2)
clothes = mu & (yy > chin_y - 2) & ((lum < 70) | ((lum > 175) & (np.abs(body[..., 2] - body[..., 0]) < 25)))  # jacket / white shirt
clothes = cv2.morphologyEx(clothes.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(np.float32)
clothes = cv2.GaussianBlur(clothes, (0, 0), 0.8)

# old jaw/neck sticking out beside the new jaw -> background (the collar/jacket are drawn back on top below)
nx = M[:, :2] @ rl[152] + M[:, 2]
jaw_w = np.linalg.norm((M[:, :2] @ rl[172] + M[:, 2]) - (M[:, :2] @ rl[397] + M[:, 2]))
band = np.abs(np.arange(W)[None, :] - nx[0]) < jaw_w * 0.40
side = mu & (yy >= chin_y - 25) & (yy < chin_y + 45) & ~band & (ha < 0.5) & (((body[..., 2] > body[..., 0] + 12) & (body.mean(2) > 60)) | ((yy < chin_y + 6) & (body.mean(2) < 110)))   # skin, or beard above the collar
canvas[side] = 255
# tone: keep his own skin colour but take out the warm lamp cast so it sits on a white studio shot
out = canvas * (1 - ha[..., None]) + head * ha[..., None]
out = out * (1 - clothes[..., None]) + body * clothes[..., None]
cv2.imwrite("dbg_ha.png", (ha * 255).astype(np.uint8)); cv2.imwrite("user_full_head.jpg", np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 97])
cv2.imwrite("/tmp/claude-0/-home-user-audiosobhan/545c7dd5-268d-5bb8-892d-0cd1ca011ec2/scratchpad/hob.jpg",
            np.hstack([body[0:420, 200:640], np.clip(out, 0, 255)[0:420, 200:640]]).astype(np.uint8))
