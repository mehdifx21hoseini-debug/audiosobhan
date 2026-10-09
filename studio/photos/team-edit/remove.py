"""Remove persons 1 & 2 with LaMa (keeps person 3 untouched)."""
import numpy as np, cv2
from PIL import Image
from simple_lama_inpainting import SimpleLama
im = Image.open("original.jpg").convert("RGB")
m12 = (cv2.imread("mask_p1.png", 0) > 0) | (cv2.imread("mask_p2.png", 0) > 0)
p3 = cv2.dilate((cv2.imread("mask_p3.png", 0) > 0).astype(np.uint8), np.ones((3, 3)))
m12 = cv2.morphologyEx(m12.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (71, 71))) > 0  # gap between the two
rm = cv2.dilate(m12.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
# contact shadows under the shoes
rm[1440:1610, 560:1130] |= cv2.dilate(m12.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 41)))[1440:1610, 560:1130]
rm[p3 > 0] = 0
cv2.imwrite("mask_remove.png", rm * 255)
out = SimpleLama()(im, Image.fromarray(rm * 255))
out = out.crop((0, 0) + im.size)
# keep every pixel outside the mask bit-exact
res = np.array(im); o = np.array(out)
soft = cv2.GaussianBlur(rm.astype(np.float32), (9, 9), 0)[..., None]
res = (o * soft + res * (1 - soft)).astype(np.uint8)
res[p3 > 0] = np.array(im)[p3 > 0]
Image.fromarray(res).save("step1_lama.png")
print("ok")
