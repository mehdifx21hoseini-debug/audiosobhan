import sys, shutil
from gradio_client import Client, handle_file
P = ("Fix only the neck: make the man's neck connect naturally and realistically into the white shirt collar, "
     "with natural skin tone and soft shadow under the jaw. Keep the face, sunglasses, hair, beard, suit, tie, pose, "
     "framing and background exactly the same. Realistic photograph.")
c = Client("black-forest-labs/FLUX.1-Kontext-Dev")
res, s = c.predict(input_image=handle_file("rough.png"), prompt=P, seed=int(sys.argv[2]), randomize_seed=False,
                   guidance_scale=2.5, steps=28, api_name="/infer")
shutil.copy(res["path"] if isinstance(res, dict) else res, sys.argv[1]); print("ok", s)
