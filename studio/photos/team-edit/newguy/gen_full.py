import sys, shutil
from gradio_client import Client, handle_file
P = ("Zoom out to a full-body photo of this exact man from head to toes, standing upright on the floor facing the camera, "
     "arms crossed exactly as now, same black suit, white shirt and black tie, black suit trousers and black leather shoes, "
     "plain light grey studio background, soft even light. Keep his face, sunglasses, hair and beard the same. Realistic photograph.")
c = Client("black-forest-labs/FLUX.1-Kontext-Dev")
res, s = c.predict(input_image=handle_file("kontext_in2.jpg"), prompt=P, seed=int(sys.argv[2]), randomize_seed=False,
                   guidance_scale=2.5, steps=28, api_name="/infer")
shutil.copy(res["path"] if isinstance(res, dict) else res, sys.argv[1]); print("ok", s)
