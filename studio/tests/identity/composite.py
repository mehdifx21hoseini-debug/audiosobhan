"""Identity-safe composite: real cutout of Sobhan (face untouched) on an AI background, with colour match, light wrap and rim light."""
import numpy as np
from PIL import Image, ImageFilter
W, H = 1080, 1920
bg = Image.open("bg_4.png").convert("RGB"); s = max(W / bg.width, H / bg.height)
bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS); bg = bg.crop(((bg.width - W) // 2, 0, (bg.width - W) // 2 + W, H))
bg = bg.filter(ImageFilter.GaussianBlur(6))                                   # shallow depth of field
B = np.asarray(bg).astype(np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W]; vig = 1 - .45 * (((xx - W / 2) / W) ** 2 + ((yy - H * .45) / H) ** 2) * 2.2
B = np.clip(B * .72 * vig[..., None], 0, 1)                                   # darker so the subject pops
p = Image.open("../../brand/sobhan.png").convert("RGBA"); p = p.crop(p.getbbox())
k = 1.5; p = p.resize((round(p.width * k), round(p.height * k)), Image.LANCZOS)
x0, y0 = (W - p.width) // 2 + 40, H - p.height
P = np.asarray(p).astype(np.float32) / 255; rgb, a = P[..., :3], P[..., 3:]
# place on canvas
C = np.zeros((H, W, 3), np.float32); A = np.zeros((H, W, 1), np.float32)
ys, xs = slice(max(0, y0), y0 + p.height), slice(max(0, x0), min(W, x0 + p.width)); sy, sx = ys.start - y0, xs.start - x0
C[ys, xs] = rgb[sy:sy + ys.stop - ys.start, sx:sx + xs.stop - xs.start]; A[ys, xs] = a[sy:sy + ys.stop - ys.start, sx:sx + xs.stop - xs.start]
# gentle colour match of the subject toward the scene (keeps skin natural: 25%)
m = A[..., 0] > .5; mu_s, mu_b = C[m].mean(0), B.mean((0, 1))
C = np.clip(C * (1 - .25) + (C * (mu_b / mu_s) ** .5 * .92) * .25, 0, 1)
# light wrap: blurred background bleeding into the subject's edges
edge = np.asarray(Image.fromarray((A[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))).astype(np.float32)[..., None] / 255
wrap = (1 - edge) * A; Bb = np.asarray(Image.fromarray((B * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(20))).astype(np.float32) / 255
C = C * (1 - .55 * wrap) + Bb * 1.3 * .55 * wrap
# warm gold rim light from the right (window/lamp side)
rim = np.clip(A - np.roll(A, 10, axis=1), 0, 1); rim = np.asarray(Image.fromarray((rim[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))).astype(np.float32)[..., None] / 255
C = np.clip(C + rim * np.array([1.0, .82, .5]) * .45, 0, 1)
out = B * (1 - A) + C * A
# overall grade: slight contrast + grain-free soft glow
out = np.clip((out - .5) * 1.06 + .5, 0, 1)
Image.fromarray((out * 255).astype(np.uint8)).save("sobhan_trading_room.png"); print("ok", p.size, x0, y0)
