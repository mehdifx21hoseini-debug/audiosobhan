"""Person masks with SAM (box prompts) -> removal mask for persons 1 & 2."""
import numpy as np, torch, cv2
from PIL import Image
from transformers import SamModel, SamProcessor
im = Image.open("original.jpg").convert("RGB")
boxes = {"p1": [585, 262, 900, 1570], "p2": [880, 168, 1200, 1530], "p3": [1105, 258, 1560, 1600],
         "p4": [1445, 240, 1750, 1565], "p5": [1725, 265, 2035, 1595]}
proc = SamProcessor.from_pretrained("facebook/sam-vit-base"); model = SamModel.from_pretrained("facebook/sam-vit-base").eval()
for k, b in boxes.items():
    inp = proc(im, input_boxes=[[b]], return_tensors="pt")
    with torch.no_grad(): out = model(**inp)
    m = proc.image_processor.post_process_masks(out.pred_masks, inp["original_sizes"], inp["reshaped_input_sizes"])[0][0]
    best = out.iou_scores[0, 0].argmax().item()
    mk = m[best].numpy().astype(np.uint8) * 255
    cv2.imwrite(f"mask_{k}.png", mk); print(k, out.iou_scores[0, 0].tolist(), mk.mean() / 255)
