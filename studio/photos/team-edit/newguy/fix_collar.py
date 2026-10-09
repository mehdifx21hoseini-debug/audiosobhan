import sys, shutil
from gradio_client import Client, handle_file
P = ("Fix only the neck and shirt collar: the man's neck goes naturally down into a crisp white dress-shirt collar "
     "with the black tie, natural skin tone on the neck, remove the brown patches and stains on the collar. "
     "Keep his face, hair, beard, the black suit, pose and the plain white background exactly the same. Photorealistic.")
c = Client("black-forest-labs/FLUX.1-Kontext-Dev")
res, s = c.predict(input_image=handle_file(sys.argv[1]), prompt=P, seed=int(sys.argv[3]), randomize_seed=False,
                   guidance_scale=2.5, steps=28, api_name="/infer")
shutil.copy(res["path"] if isinstance(res, dict) else res, sys.argv[2]); print("ok", s)
