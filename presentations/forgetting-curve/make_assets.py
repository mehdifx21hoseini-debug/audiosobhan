"""Background gradients + the glowing orb used as the Morph motif."""
import numpy as np
from PIL import Image
out = __file__.rsplit('/', 1)[0] + '/assets/'
W, H = 1920, 1080
y, x = np.mgrid[0:H, 0:W].astype(np.float32)

def dark(cx, cy, name):
    d = np.sqrt(((x - cx) / W) ** 2 + ((y - cy) / H) ** 2)
    t = np.clip(d / 0.95, 0, 1) ** 1.2
    c0, c1 = np.array([0x19, 0x2B, 0x44]), np.array([0x08, 0x10, 0x1C])
    img = c0[None, None] * (1 - t[..., None]) + c1[None, None] * t[..., None]
    img += np.random.default_rng(1).normal(0, 1.2, img.shape)  # anti-banding dither
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out + name)

dark(W * 0.30, H * 0.55, 'bg_dark_hook.png')
dark(W * 0.50, H * 0.40, 'bg_dark_takeaway.png')

S = 800
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
r = np.sqrt((xx - S / 2) ** 2 + (yy - S / 2) ** 2) / (S / 2)
a = np.exp(-(r / 0.55) ** 2) * (r < 1)
orb = np.zeros((S, S, 4), np.uint8)
orb[..., 0], orb[..., 1], orb[..., 2] = 0x16, 0xB5, 0xA6
orb[..., 3] = (a * 255).astype(np.uint8)
Image.fromarray(orb, 'RGBA').save(out + 'orb.png')
print('ok')
