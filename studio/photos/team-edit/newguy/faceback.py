"""Lock the real face back onto the Kontext full-body render (ECC-aligned, colour matched)."""
import cv2, numpy as np
src = cv2.imread("source_flipped.jpg"); full = cv2.imread("full_8.png")
mh = cv2.imread("m_head.png", 0) > 0
ff = (~mh).astype(np.uint8); cv2.floodFill(ff, None, (0, 0), 0); mh = mh | (ff > 0)
hull = np.zeros(mh.shape, np.uint8); cv2.fillPoly(hull, [cv2.convexHull(np.argwhere(mh)[:, ::-1].astype(np.int32))], 1)
lum = src.mean(2); band = np.zeros_like(mh); band[170:240] = True
mh |= band & (hull > 0) & (lum < 110)
b, g, r = [src[..., i].astype(int) for i in range(3)]
mh &= ~((g > r + 4) & (g > b + 4)); mh &= ~((g > r + 10) & (b > r + 10))
mh = cv2.morphologyEx(mh.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) > 0
# face region only: stop just under the chin so the render's neck/collar stay
a = mh.astype(np.float32); yy = np.arange(a.shape[0])[:, None]
a *= np.clip((308 - yy) / 8 + 0.5, 0, 1)

jaw = np.array([(40, 262), (113, 262), (118, 275), (128, 287), (145, 298), (170, 305), (200, 302), (245, 288), (245, 360), (40, 360)], np.int32)
cv2.fillPoly(a, [jaw], 0)                                      # keep the face down to the jaw line only
a = cv2.erode(a, np.ones((5, 5), np.uint8)); a = cv2.GaussianBlur(a, (0, 0), 2.5)

# align: warp maps full-image coords -> source coords
s0 = 0.95
W0 = np.float32([[1 / s0, 0, 173 - 366 / s0], [0, 1 / s0, 215 - 175 / s0]])
x0, y0, x1, y1 = 285, 95, 450, 255
tpl = cv2.cvtColor(full, cv2.COLOR_BGR2GRAY)[y0:y1, x0:x1].astype(np.float32)
Wc = W0.copy(); Wc[:, 2] += Wc[:, :2] @ np.float32([x0, y0])        # crop-relative
inp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY).astype(np.float32)
tpl_n = cv2.GaussianBlur(tpl, (0, 0), 1.5); inp_n = cv2.GaussianBlur(inp, (0, 0), 1.5)
_, Wc = cv2.findTransformECC(tpl_n, inp_n, Wc, cv2.MOTION_AFFINE,
                             (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
W = Wc.copy(); W[:, 2] -= W[:, :2] @ np.float32([x0, y0])
# real heads read ~10% larger than the render's: scale the pasted head about the chin
HS, chin = 1.10, np.float32([366, 236])
Wf = cv2.invertAffineTransform(W)                                    # source -> full
Wf = np.vstack([Wf, [0, 0, 1]]); S_ = np.float32([[HS, 0, chin[0] * (1 - HS)], [0, HS, chin[1] * (1 - HS)], [0, 0, 1]])
W = cv2.invertAffineTransform((S_ @ Wf)[:2].astype(np.float32))
print("warp", W)
h, w = full.shape[:2]
face = cv2.warpAffine(src, W, (w, h), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)
al = cv2.warpAffine(a, W, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)[..., None]
# colour match the real skin to the render's lighting (LAB mean/std on the face area)
m = al[..., 0] > 0.8
F = cv2.cvtColor(face, cv2.COLOR_BGR2LAB).astype(np.float32); R = cv2.cvtColor(full, cv2.COLOR_BGR2LAB).astype(np.float32)
for c in range(3):
    fs, rs = F[..., c][m], R[..., c][m]
    F[..., c] = (F[..., c] - fs.mean()) * (0.5 + 0.5 * rs.std() / fs.std()) + rs.mean() * 0.6 + fs.mean() * 0.4
face = cv2.cvtColor(np.clip(F, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
face = cv2.addWeighted(face, 1.6, cv2.GaussianBlur(face, (0, 0), 1.2), -0.6, 0)   # match the render's crispness
out = full * (1 - al) + face * al
cv2.imwrite("person.png", np.clip(out, 0, 255).astype(np.uint8))
cv2.imwrite("/tmp/claude-0/-home-user-audiosobhan/545c7dd5-268d-5bb8-892d-0cd1ca011ec2/scratchpad/fb.jpg",
            np.hstack([full[60:330, 250:490], np.clip(out, 0, 255).astype(np.uint8)[60:330, 250:490]]))
# person alpha: rendered body (its own head removed above the chin) + the real head
bm = (cv2.imread("m_full.png", 0) > 0).astype(np.float32)
CHIN_Y = 229
yy = np.arange(h)[:, None]; xx = np.arange(w)[None, :]
head_zone = (yy < CHIN_Y) & (xx > 270) & (xx < 470)
bm[head_zone] = 0
fb, fg, fr = [full[..., i].astype(np.int32) for i in range(3)]
skinish = (fr > fb + 15) & (full.mean(2) > 60)
bm[(yy < 258) & skinish & (al[..., 0] < 0.5) & ((xx < 334) | (xx > 418))] = 0            # render's own ear / jaw below the cut
bm = cv2.GaussianBlur(bm, (0, 0), 0.8)
A = np.maximum(bm, al[..., 0] * (cv2.GaussianBlur((cv2.imread("m_full.png", 0) > 0).astype(np.float32), (0, 0), 6) > 0.01))
A = np.maximum(A, al[..., 0])
cv2.imwrite("person_alpha.png", (np.clip(A, 0, 1) * 255).astype(np.uint8))
bg = np.array([228, 222, 215], np.float32)
prev = out * A[..., None] + bg * (1 - A[..., None])
cv2.imwrite("/tmp/claude-0/-home-user-audiosobhan/545c7dd5-268d-5bb8-892d-0cd1ca011ec2/scratchpad/fb2.jpg", np.clip(prev, 0, 255).astype(np.uint8)[60:330, 250:490])
