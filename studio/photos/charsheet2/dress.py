"""Clothes-only edit of one reference view (FLUX.1 Kontext). usage: dress.py in.jpg out.png seed"""
import sys, shutil
from gradio_client import Client, handle_file
P = ("Change only his clothes: he now wears a tailored mid-blue linen blazer with a subtle herringbone texture, "
     "a crisp white dress shirt with an open collar and no tie, and a red-and-gold patterned silk pocket square "
     "in the left breast pocket. Keep his face, head, hair, beard, expression, head angle, pose, framing and the plain "
     "light grey background exactly the same. Photorealistic.")
c = Client("black-forest-labs/FLUX.1-Kontext-Dev")
res, s = c.predict(input_image=handle_file(sys.argv[1]), prompt=P, seed=int(sys.argv[3]), randomize_seed=False,
                   guidance_scale=2.5, steps=28, api_name="/infer")
shutil.copy(res["path"] if isinstance(res, dict) else res, sys.argv[2]); print("ok", sys.argv[2])
