import numpy as np, torch, cv2, sys
from PIL import Image
from transformers import SamModel, SamProcessor
proc = SamProcessor.from_pretrained("facebook/sam-vit-base"); model = SamModel.from_pretrained("facebook/sam-vit-base").eval()
def seg(path, box, out, pts=None):
    im = Image.open(path).convert("RGB")
    kw = dict(input_boxes=[[box]])
    inp = proc(im, return_tensors="pt", **kw)
    with torch.no_grad(): o = model(**inp)
    m = proc.image_processor.post_process_masks(o.pred_masks, inp["original_sizes"], inp["reshaped_input_sizes"])[0][0]
    k = o.iou_scores[0, 0].argmax().item(); cv2.imwrite(out, m[k].numpy().astype(np.uint8) * 255)
    print(out, o.iou_scores[0, 0].tolist())
seg("source_flipped.jpg", [85, 110, 245, 335], "m_head.png")
seg("body_s29.png", [175, 45, 590, 1320], "m_body.png")
