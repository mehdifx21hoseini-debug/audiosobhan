"""Keyframes with SDXL-Turbo on CPU. usage: python3 gen.py name "prompt" [seed] [steps]"""
import sys, time, torch
from diffusers import AutoPipelineForText2Image
torch.set_num_threads(4)
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.bfloat16)
STYLE = ", cinematic film still, dramatic rim light, deep navy blue and warm gold color grade, volumetric haze, highly detailed, sharp focus, 35mm photo"
for job in sys.argv[1:]:
    name, prompt, seed, steps = (job.split("|") + ["7", "4"])[:4]
    t = time.time()
    img = pipe(prompt + STYLE, num_inference_steps=int(steps), guidance_scale=0.0, width=768, height=1344,
               generator=torch.Generator().manual_seed(int(seed))).images[0]
    img.save(f"img/{name}.png"); print(name, round(time.time() - t), "s", flush=True)
