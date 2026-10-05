"""Clean the dark leftover next to Sobhan's left shoe by cloning matching carpet."""
import sys, cv2, numpy as np
img = cv2.imread(sys.argv[1]).astype(np.float32)
p3 = cv2.dilate((cv2.imread("mask_p3.png", 0) > 0).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
x0, y0, x1, y1 = 1135, 1455, 1235, 1540
lum = img.mean(2)
m = np.zeros(lum.shape, bool); m[y0:y1, x0:x1] = lum[y0:y1, x0:x1] < 95
m &= ~p3
m = cv2.dilate(m.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
m &= ~p3
ring = cv2.dilate(m.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
ring &= ~m & ~p3
ys, xs = np.nonzero(ring)
best = None
for dx in range(-260, -40, 2):
    for dy in range(-30, 31, 2):
        d = ((img[ys + dy, xs + dx] - img[ys, xs]) ** 2).mean()
        if best is None or d < best[0]: best = (d, dx, dy)
_, dx, dy = best
src = np.roll(np.roll(img, -dy, 0), -dx, 1)
a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2)[..., None]
a[p3] = 0
out = img * (1 - a) + src * a
cv2.imwrite(sys.argv[2], np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 95])
print("offset", dx, dy, "px", m.sum())
