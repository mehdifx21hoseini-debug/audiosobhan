"""One character-sheet view of the same man via FLUX.1 Kontext. usage: view.py out.png seed "<view text>" """
import sys, shutil
from gradio_client import Client, handle_file
P = ("Character turnaround reference photo. Show this exact same man " + sys.argv[3] + ", same framing from head to mid-thigh, "
     "standing relaxed with hands clasped in front. Keep his face, skin tone, hairline and short haircut, small moustache, "
     "blue linen blazer, open-collar white shirt, red patterned pocket square and dark trousers exactly the same. "
     "Plain seamless light grey studio background, soft even studio light. Photorealistic.")
c = Client("black-forest-labs/FLUX.1-Kontext-Dev")
res, s = c.predict(input_image=handle_file("sobhan_front.jpg"), prompt=P, seed=int(sys.argv[2]), randomize_seed=False,
                   guidance_scale=2.5, steps=28, api_name="/infer")
shutil.copy(res["path"] if isinstance(res, dict) else res, sys.argv[1]); print("ok", sys.argv[1])
