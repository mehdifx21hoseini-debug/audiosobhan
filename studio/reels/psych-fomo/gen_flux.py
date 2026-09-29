"""FOMO illustration variants with FLUX.1-schnell on Hugging Face (better prompt adherence than local SDXL-Turbo).
Stops cleanly when the ZeroGPU quota runs out; re-run later to continue (existing files are skipped)."""
import os, shutil
from gradio_client import Client
P = ("Premium editorial illustration for an educational slide, clean pure white background, no background scene. "
     "Half-body adult man, early 30s, trader in a navy blazer and white shirt, holding a smartphone in front of him with both hands, "
     "looking DOWN at the phone screen which shows a steep rising green stock chart. Expression of fear and panic: wide eyes, raised worried eyebrows, "
     "tense clenched jaw, a drop of sweat on the temple. Subtle gold accents. {style} High detail, centered, soft shadow under the figure.")
STYLES = {"clay": "Soft matte 3D clay render, modern Pixar-like adult character design, soft studio lighting.",
          "paint": "Refined digital painting, semi-realistic, subtle brush texture, warm cinematic light.",
          "line": "Sophisticated flat vector illustration with fine line details and soft gradients, navy and gold palette."}
os.makedirs("art", exist_ok=True)
c = Client("black-forest-labs/FLUX.1-schnell", verbose=False)
for name, st in STYLES.items():
    for seed in (7, 19):
        out = f"art/flux_{name}_{seed}.png"
        if os.path.exists(out): continue
        try:
            r = c.predict(prompt=P.format(style=st), seed=seed, randomize_seed=False, width=1024, height=1024, num_inference_steps=4, api_name="/infer")
            p = r[0] if isinstance(r, (list, tuple)) else r
            shutil.copy(p["path"] if isinstance(p, dict) else p, out); print("ok", out, flush=True)
        except Exception as e:
            print("stop:", str(e)[:160], flush=True); raise SystemExit
