"""Depth maps (Depth-Anything-V2) for 2.5D camera moves. usage: python3 depth.py eye4 run2 ..."""
import sys, numpy as np, torch
from PIL import Image, ImageFilter
from transformers import pipeline
pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device="cpu")
for n in sys.argv[1:]:
    im = Image.open(f"img/{n}.png").convert("RGB"); d = pipe(im)["predicted_depth"]
    d = torch.nn.functional.interpolate(d[None] if d.dim() == 3 else d[None, None], size=im.size[::-1], mode="bicubic")[0, 0].numpy()
    d = (d - d.min()) / (d.max() - d.min())                     # 1 = near
    Image.fromarray((d * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)).save(f"img/{n}_d.png"); print(n)
