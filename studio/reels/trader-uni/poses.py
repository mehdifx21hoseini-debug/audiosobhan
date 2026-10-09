"""Batch: the approved painted Sobhan character (char_sobhan.png) in different outfits/expressions via FLUX.1 Kontext.
Stops cleanly when the ZeroGPU quota runs out; re-run later to continue (existing files are skipped)."""
import os, shutil
from gradio_client import Client, handle_file
KEEP = ("Keep this exact character: same face, same very short buzz-cut hair and receding hairline, no beard, "
        "same painted semi-realistic illustration style and rendering. ")
POSES = {
 "p1_class_confident": "Sitting at a wooden student desk in a sunlit university lecture classroom with an open notebook, wearing a light grey knit polo shirt, calm confident expression, mouth closed. Warm golden sunbeams through tall windows, classmates softly blurred behind.",
 "p2_trader_closeup": "Close-up portrait in a sunlit university classroom, wearing a light grey knit polo shirt, looking straight ahead, serious and self-assured, lips slightly parted as if saying one word. Golden side light, shallow depth of field.",
 "p3_determined": "Close-up in a classroom while others laugh in the blurred background, he frowns slightly with a hurt but determined look, jaw set, wearing a light grey knit polo shirt. Dramatic warm side light.",
 "p4_night_trading": "At night in a dark room, sitting in front of two glowing monitors showing candlestick charts, blue screen light on his face, focused intense expression, wearing a dark navy t-shirt.",
 "p5_lost": "At night at a desk, head slightly down, disappointed and exhausted expression, red losing charts on the monitor behind him, wearing a dark navy t-shirt, moody blue and red light.",
 "p6_success_suit": "Standing outdoors at a university graduation ceremony, wearing a sharp dark navy suit with a white open-collar shirt, confident proud smile, graduates in caps blurred behind, bright sunny day.",
}
c = Client("black-forest-labs/FLUX.1-Kontext-Dev")
for name, desc in POSES.items():
    out = f"{name}.png"
    if os.path.exists(out): continue
    try:
        res, _ = c.predict(input_image=handle_file("char_sobhan.png"), prompt=KEEP + desc, seed=7, randomize_seed=False,
                           guidance_scale=2.5, steps=28, api_name="/infer")
        shutil.copy(res["path"] if isinstance(res, dict) else res, out); print("ok", out, flush=True)
    except Exception as e:
        print("stop:", str(e)[:160], flush=True); break
