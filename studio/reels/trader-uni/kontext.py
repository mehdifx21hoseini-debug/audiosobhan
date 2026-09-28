"""Pixar-style Sobhan via FLUX.1 Kontext (HF Space). usage: python3 kontext.py out.png seed "prompt" """
import sys, shutil
from gradio_client import Client, handle_file
out, seed, prompt = sys.argv[1], int(sys.argv[2]), sys.argv[3]
c = Client("black-forest-labs/FLUX.1-Kontext-Dev")
res, s = c.predict(input_image=handle_file(sys.argv[4] if len(sys.argv) > 4 else "ref_sobhan.jpg"), prompt=prompt, seed=seed, randomize_seed=False, guidance_scale=2.5, steps=28, api_name="/infer")
shutil.copy(res["path"] if isinstance(res, dict) else res, out); print("ok", out, s)
