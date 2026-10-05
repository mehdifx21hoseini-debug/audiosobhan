import sys, shutil
from gradio_client import Client, handle_file
P = ("Make this a clean natural photograph: even, natural skin tone and soft lighting across the whole face, "
     "both eyeglass lenses fully clear and transparent with the same skin behind them, remove any grey smudge or seam around the right lens. Keep exactly the same person, same face shape, eyes, nose, "
     "mouth, short beard, the same clear rectangular eyeglasses, same hair, white shirt, black tie and black suit, same pose. "
     "Plain white background. Photorealistic.")
c = Client("black-forest-labs/FLUX.1-Kontext-Dev")
res, s = c.predict(input_image=handle_file(sys.argv[1]), prompt=P, seed=int(sys.argv[3]), randomize_seed=False,
                   guidance_scale=2.5, steps=28, api_name="/infer")
shutil.copy(res["path"] if isinstance(res, dict) else res, sys.argv[2]); print("ok", s)
