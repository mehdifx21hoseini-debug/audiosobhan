"""Lift person 4's face/hands naturally (midtone/shadow lift, colour kept). usage: in out"""
import sys, cv2, numpy as np
im = cv2.imread(sys.argv[1]); H, W = im.shape[:2]
lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
m = cv2.imread("mask_p4.png", 0) > 0
yy = np.arange(H)[:, None]
skin = m & (lab[..., 1] > 134) & (lab[..., 0] > 35)
skin = cv2.morphologyEx(skin.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)) > 0
head = m & (yy < 470)                                   # face, beard, ears, neck
w = np.where(head, 0.75, 0) + np.where(skin, 0.25, 0) + np.where(skin & (yy >= 470), 0.75, 0)
w = cv2.GaussianBlur(np.clip(w, 0, 1).astype(np.float32), (0, 0), 6) * m
w = cv2.GaussianBlur(w, (0, 0), 1.0)
L = lab[..., 0]
lift = 16 * np.clip(1 - np.abs(L - 105) / 140, 0, 1) + 6 * np.clip(1 - L / 90, 0, 1)   # mids + a little shadow
lab[..., 0] = L + lift * w
lab[..., 1] = 128 + (lab[..., 1] - 128) * (1 - 0.06 * w)                              # keep skin from turning orange
out = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
cv2.imwrite(sys.argv[2], out, [cv2.IMWRITE_JPEG_QUALITY, 95])
s = skin & (yy < 470)
print("face L before/after", np.median(L[s]), np.median(lab[..., 0][s]))
