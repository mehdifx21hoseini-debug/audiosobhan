"""2x super-resolution of the final photo (Real-ESRGAN x2plus), blended with a Lanczos
upscale + fine grain so skin and fabric stay photographic. usage: upscale.py in.jpg out.jpg"""
import sys, cv2, numpy as np, torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
torch.set_num_threads(max(1, torch.get_num_threads()))
model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
up = RealESRGANer(scale=2, model_path="/home/user/tools/esrgan/RealESRGAN_x2plus.pth", model=model,
                  tile=320, tile_pad=16, pre_pad=0, half=False, device="cpu")
im = cv2.imread(sys.argv[1])
sr, _ = up.enhance(im, outscale=2)
lz = cv2.resize(im, (sr.shape[1], sr.shape[0]), interpolation=cv2.INTER_LANCZOS4)
wsr = np.full(sr.shape[:2], 0.75, np.float32)
# person outlines against the bright backdrop: no super-res there (it turns soft edges into halos)
band = np.zeros(im.shape[:2], np.uint8)
for k in ("p3", "p4", "p5"):
    m = (cv2.imread(f"mask_{k}.png", 0) > 0).astype(np.uint8)
    band |= cv2.dilate(m, np.ones((9, 9), np.uint8)) - cv2.erode(m, np.ones((5, 5), np.uint8))
band = cv2.resize(band.astype(np.float32), (sr.shape[1], sr.shape[0]))
band = cv2.GaussianBlur(band, (0, 0), 3)
wsr *= 1 - np.clip(band, 0, 1) * 0.9
out = sr.astype(np.float32) * wsr[..., None] + lz.astype(np.float32) * (1 - wsr[..., None])
out += np.random.default_rng(1).normal(0, 1.6, out.shape[:2])[..., None]
cv2.imwrite(sys.argv[2], np.clip(out, 0, 255).astype(np.uint8),
            [cv2.IMWRITE_JPEG_QUALITY, 97, cv2.IMWRITE_JPEG_SAMPLING_FACTOR, cv2.IMWRITE_JPEG_SAMPLING_FACTOR_444])
print("ok", out.shape)
