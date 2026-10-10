import sys, shutil
from gradio_client import Client, handle_file
P = ("This is a rear view: we see the man from directly behind. Change only his clothes: he wears a tailored mid-blue "
     "linen blazer seen from the BACK (back panel of the jacket with the centre back seam, shoulders and the back of the "
     "collar), and the back of a white shirt collar is visible just above the blazer collar at the nape of the neck. "
     "No lapels, no buttons, no pocket square, nothing from the front of the jacket. Keep the back of his head, hair, "
     "ears, neck, framing and the plain light grey background exactly the same. Photorealistic.")
c = Client("black-forest-labs/FLUX.1-Kontext-Dev")
res, s = c.predict(input_image=handle_file(sys.argv[1]), prompt=P, seed=int(sys.argv[3]), randomize_seed=False,
                   guidance_scale=2.5, steps=28, api_name="/infer")
shutil.copy(res["path"] if isinstance(res, dict) else res, sys.argv[2]); print("ok", sys.argv[2])
