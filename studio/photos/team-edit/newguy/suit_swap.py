import sys, shutil
from gradio_client import Client, handle_file
P = ("Change only his clothes: he now wears a tailored black two-piece business suit jacket, a crisp white dress shirt "
     "with collar and a slim black tie. Keep his face, sunglasses, hair, beard, head angle, pose, arms and the background "
     "exactly the same. Realistic photograph.")
c = Client("black-forest-labs/FLUX.1-Kontext-Dev")
res, s = c.predict(input_image=handle_file("source_flipped.jpg"), prompt=P, seed=int(sys.argv[2]), randomize_seed=False,
                   guidance_scale=2.5, steps=28, api_name="/infer")
shutil.copy(res["path"] if isinstance(res, dict) else res, sys.argv[1]); print("ok", s)
