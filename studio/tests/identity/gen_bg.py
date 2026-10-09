import torch
from diffusers import AutoPipelineForText2Image
torch.set_num_threads(4)
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.bfloat16)
P = ("empty modern luxury trading office at night, several large monitors glowing with green and red candlestick charts, "
     "deep navy blue walls, warm gold accent lights, city skyline through window, soft bokeh, cinematic, no people, highly detailed, 35mm photo")
for s in (4, 9, 23):
    pipe(P, num_inference_steps=4, guidance_scale=0.0, width=768, height=1344, generator=torch.Generator().manual_seed(s)).images[0].save(f"bg_{s}.png"); print("bg", s, flush=True)
