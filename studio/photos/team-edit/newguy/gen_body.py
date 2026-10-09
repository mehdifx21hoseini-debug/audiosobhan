"""Full-body suit version of the new team member via FLUX.1 Kontext (HF Space).
usage: python3 gen_body.py out.png seed"""
import sys, shutil
from gradio_client import Client, handle_file
P = ("Show this exact same man as a full-body photo from head to toes, standing upright and facing the camera, "
     "wearing a tailored black two-piece business suit, white dress shirt, slim black tie, black leather shoes, "
     "arms relaxed down at his sides, feet together on the floor, plain light grey studio background, soft even light. "
     "Keep his face, sunglasses, hair and short beard exactly the same. Realistic photograph, 50mm lens.")
c = Client("black-forest-labs/FLUX.1-Kontext-Dev")
res, s = c.predict(input_image=handle_file("kontext_in.jpg"), prompt=P, seed=int(sys.argv[2]), randomize_seed=False,
                   guidance_scale=2.5, steps=28, api_name="/infer")
shutil.copy(res["path"] if isinstance(res, dict) else res, sys.argv[1]); print("ok", sys.argv[1], s)
