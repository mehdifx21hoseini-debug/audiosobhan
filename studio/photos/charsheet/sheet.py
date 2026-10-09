"""Assemble the character turnaround sheet."""
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

BG = (226, 227, 229)
PANEL_H = 1400
# real 3/4 photo, cut out onto the same grey as the generated views
src = cv2.imread("sobhan_front.jpg").astype(np.float32)
m = cv2.imread("m_sobhan.png", 0).astype(np.float32) / 255
m = cv2.GaussianBlur(cv2.erode(m, np.ones((3, 3), np.uint8)), (0, 0), 1.0)[..., None]
real = src * m + np.float32(BG[::-1]) * (1 - m)
cv2.imwrite("v_real34.png", real.astype(np.uint8)[200:2000, 30:1230])     # same head-to-thigh scale as the other views

views = [("l_front.png", "روبه‌رو", "Front"),
         ("v_real34.png", "سه‌رخ (عکس اصلی)", "3/4 — original"),
         ("l_q_other.png", "سه‌رخ", "3/4"),
         ("v_p_left.png", "نیم‌رخ", "Profile"),
         ("v_back.png", "پشت", "Back")]

def fit(path):
    im = Image.open(path).convert("RGB")
    # match framing: crop to head..mid-thigh by aspect 2:3 around the person
    w, h = im.size
    if w / h > 832 / 1248:
        nw = int(h * 832 / 1248); im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w * 1248 / 832); im = im.crop((0, 0, w, nh))
    return im.resize((int(PANEL_H * 832 / 1248), PANEL_H), Image.LANCZOS)

panels = [fit(p) for p, _, _ in views]
pw = panels[0].width; gap = 36; margin = 70; top = 230; label_h = 150
W = margin * 2 + pw * len(panels) + gap * (len(panels) - 1)
H = top + PANEL_H + label_h + 60
sheet = Image.new("RGB", (W, H), (245, 245, 246))
d = ImageDraw.Draw(sheet)
fa_b = ImageFont.truetype("../../fonts/Vazirmatn-Black.ttf", 84, layout_engine=ImageFont.Layout.RAQM)
fa_m = ImageFont.truetype("../../fonts/Vazirmatn-Bold.ttf", 46, layout_engine=ImageFont.Layout.RAQM)
en = ImageFont.truetype("/home/user/tools/fonts/Montserrat.ttf", 30); en.set_variation_by_axes([600])
en_t = ImageFont.truetype("/home/user/tools/fonts/Montserrat.ttf", 34); en_t.set_variation_by_axes([500])
d.text((W - margin, 95), "کاراکتر شیت — سبحان صمدی", font=fa_b, fill=(41, 56, 108), anchor="rm", direction="rtl", language="fa")
d.text((margin, 95), "CHARACTER SHEET  ·  SOBHAN SAMADI", font=en_t, fill=(184, 145, 74), anchor="lm")
d.line([(margin, 175), (W - margin, 175)], fill=(214, 216, 220), width=3)
for i, (p, (_, fa, e)) in enumerate(zip(panels, views)):
    x = W - margin - (i + 1) * pw - i * gap                     # RTL order: first view on the right
    sheet.paste(p, (x, top))
    d.rectangle([x, top, x + pw - 1, top + PANEL_H - 1], outline=(214, 216, 220), width=2)
    cx = x + pw // 2
    d.text((cx, top + PANEL_H + 55), fa, font=fa_m, fill=(41, 56, 108), anchor="mm", direction="rtl", language="fa")
    d.text((cx, top + PANEL_H + 112), e.upper(), font=en, fill=(150, 150, 155), anchor="mm")
sheet.save("sobhan_character_sheet.png")
sheet.convert("RGB").save("sobhan_character_sheet.jpg", quality=95)
print(sheet.size)
