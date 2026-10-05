"""Cut out the user's full-body suit image (white bg) -> person3.png / person3_alpha.png"""
import cv2, numpy as np
im = cv2.imread("user_full_v2.jpg").astype(np.float32)
m = (cv2.imread("m_user_v2.png", 0) > 0).astype(np.uint8)
white = (im.min(2) > 236).astype(np.uint8)
n, lab = cv2.connectedComponents(white)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bgw = np.isin(lab, list(border))
trust = np.zeros_like(bgw); trust[188:265, 352:472] = True     # collar: shirt white touches the white bg, trust SAM here
m[bgw & ~trust] = 0
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
n, lab2, st, _ = cv2.connectedComponentsWithStats(m)
m = np.isin(lab2, [i for i in range(1, n) if st[i, 4] > 2000]).astype(np.uint8)
inv = (1 - m).astype(np.uint8); cv2.floodFill(inv, None, (0, 0), 0); m |= inv          # enclosed holes
fg = im.copy()
a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)
edge = (a > 0.02) & (a < 0.98)
fg[edge] = np.clip((fg[edge] - 255 * (1 - a[edge][:, None])) / np.maximum(a[edge][:, None], 0.3), 0, 255)   # de-fringe white
cv2.imwrite("person3.png", fg.astype(np.uint8)); cv2.imwrite("person3_alpha.png", (a * 255).astype(np.uint8))
c = (fg * a[..., None] + np.array([215, 220, 225.]) * (1 - a[..., None])).astype(np.uint8)
cv2.imwrite("/tmp/claude-0/-home-user-audiosobhan/545c7dd5-268d-5bb8-892d-0cd1ca011ec2/scratchpad/u3.jpg", cv2.resize(c[150:300, 330:520], None, fx=2, fy=2))
