"""Clean final cutouts on one uniform studio background (2x resolution)."""
import cv2, numpy as np
H2, W2 = 2048, 1018
yy, xx = np.mgrid[0:H2, 0:W2].astype(np.float32)
# studio backdrop: soft light grey with a gentle centre glow
r = np.sqrt(((xx - W2 / 2) / W2) ** 2 + ((yy - H2 * 0.35) / H2) ** 2)
bg = np.float32([212, 211, 209])[None, None, :] + (1 - np.clip(r / 0.8, 0, 1))[..., None] * 18
bg += np.random.default_rng(0).normal(0, 0.8, bg.shape)
for f in ("f1_final", "f3_smile", "f2", "f4_back"):
    im = cv2.imread(f + ".png"); im = cv2.resize(im, (W2, H2), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    a = cv2.imread("cut_" + f + ".png", 0).astype(np.float32) / 255
    a = np.clip((a - 0.04) / 0.92, 0, 1)                 # drop faint halo/ghost strands
    # colour decontamination: estimate the old backdrop locally and remove it from semi-transparent edges
    solid_bg = (a < 0.02).astype(np.float32)
    est = cv2.GaussianBlur(im * solid_bg[..., None], (0, 0), 15) / np.maximum(cv2.GaussianBlur(solid_bg, (0, 0), 15), 1e-3)[..., None]
    edge = (a > 0.02) & (a < 0.98)
    fg = im.copy()
    fg[edge] = np.clip((im[edge] - est[edge] * (1 - a[edge][:, None])) / np.maximum(a[edge][:, None], 0.15), 0, 255)
    out = fg * a[..., None] + bg * (1 - a[..., None])
    cv2.imwrite("clean_" + f + ".png", np.clip(out, 0, 255).astype(np.uint8))
print("ok")
