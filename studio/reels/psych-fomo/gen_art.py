"""FOMO illustration variants with local SDXL-Turbo (no identity needed)."""
import torch
from diffusers import AutoPipelineForText2Image
torch.set_num_threads(4)
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.bfloat16)
BASE = ("half-body portrait of an adult male trader in a navy blazer and white shirt, holding a smartphone close to his face, "
        "staring at a steep rising green stock chart on the phone screen, wide fearful eyes, raised worried eyebrows, tense jaw, "
        "a bead of sweat on his temple, anxious fear of missing out, ")
STYLES = {
 "clay": "premium 3D clay render, soft matte materials, Pixar quality character, adult proportions, soft studio light, subtle gold accents, clean pure white background, highly detailed",
 "edit": "editorial magazine illustration, detailed digital painting, cinematic warm light, subtle navy and gold palette, clean white background, highly detailed face",
}
for name, st in STYLES.items():
    for seed in (3, 8, 21):
        img = pipe(BASE + st, num_inference_steps=4, guidance_scale=0.0, width=896, height=896, generator=torch.Generator().manual_seed(seed)).images[0]
        img.save(f"art/{name}_{seed}.png"); print("ok", name, seed, flush=True)
