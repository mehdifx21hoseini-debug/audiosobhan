"""Face character sheet from 4 real photos only (no generated faces).
Head+shoulders cut out, put on one neutral background, same head size and eye line,
gentle shared colour balance (the lamp light is warm; skin tone is kept natural)."""
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

BG = np.float32([232, 231, 229])                    # BGR, warm-neutral light grey
SRC = {3: ("src3.jpg", (700, 900)), 4: ("src4.jpg", (800, 900)), 5: ("src5.jpg", (750, 900)), 6: ("src6.jpg", (750, 900))}
ORDER = [(5, "روبه‌رو", "FRONT · NEUTRAL"), (6, "روبه‌رو — لبخند", "FRONT · SMILE"),
         (4, "سه‌رخ / نیم‌رخ راست", "RIGHT SIDE"), (3, "نیم‌رخ چپ", "LEFT PROFILE")]
PW, PH = 1100, 1300                                  # panel size
HEAD_H = 760                                         # crown -> chin, same in every panel
CROWN_Y = 170

def person_mask(i, seed):
    m = (cv2.imread(f"r{i}.png", 0) > 127).astype(np.uint8)          # BiRefNet portrait matte
    n, lab = cv2.connectedComponents(m)
    m = (lab == lab[seed[1], seed[0]]).astype(np.uint8)
    inv = (1 - m).astype(np.uint8); cv2.floodFill(inv, None, (0, 0), 0); m |= inv
    return m

def panel(i):
    path, seed = SRC[i]
    im = cv2.imread(path).astype(np.float32)
    m = person_mask(i, seed)
    ys, xs = np.nonzero(m)
    crown = ys.min()
    # chin: lowest skin row of the head column band above the collar (skin = warm, mid-bright)
    b, g, r = im[..., 0], im[..., 1], im[..., 2]
    skin = (m > 0) & (r > b + 25) & (r > 90)
    rows = np.nonzero(skin.sum(1) > 40)[0]
    chin = rows[rows < 1500].max()
    k = HEAD_H / (chin - crown)
    soft = cv2.imread(f"r{i}.png", 0).astype(np.float32) / 255               # keep the soft hair edge of the matte
    a = soft * cv2.dilate(m, np.ones((15, 15), np.uint8)).astype(np.float32)
    # colour: neutralise the warm cast a little (same correction for all four photos)
    lab = cv2.cvtColor(np.clip(im, 0, 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[..., 2] = 128 + (lab[..., 2] - 128) * 0.88 - 2
    im = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
    comp = im * a[..., None] + BG * (1 - a[..., None])
    comp = cv2.resize(comp, None, fx=k, fy=k, interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
    # place: crown at CROWN_Y, head centred horizontally
    head_cols = np.nonzero(skin[crown:chin].sum(0) > 5)[0]
    cx = (np.nonzero(m[crown:chin].sum(0) > 0)[0].mean() * 0.5 + head_cols.mean() * 0.5) * k
    out = np.tile(BG, (PH, PW, 1)).astype(np.float32)
    ox, oy = int(PW / 2 - cx), int(CROWN_Y - crown * k)
    h, w = comp.shape[:2]
    x0, y0, x1, y1 = max(ox, 0), max(oy, 0), min(ox + w, PW), min(oy + h, PH)
    out[y0:y1, x0:x1] = comp[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    return Image.fromarray(cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB))

panels = [panel(i) for i, _, _ in ORDER]
gap, margin, top, lab_h = 30, 60, 220, 140
W = margin * 2 + PW * 4 + gap * 3; H = top + PH + lab_h + 50
sheet = Image.new("RGB", (W, H), (246, 246, 247)); d = ImageDraw.Draw(sheet)
fa_b = ImageFont.truetype("../../fonts/Vazirmatn-Black.ttf", 80, layout_engine=ImageFont.Layout.RAQM)
fa_m = ImageFont.truetype("../../fonts/Vazirmatn-Bold.ttf", 46, layout_engine=ImageFont.Layout.RAQM)
en = ImageFont.truetype("/home/user/tools/fonts/Montserrat.ttf", 30); en.set_variation_by_axes([600])
en_t = ImageFont.truetype("/home/user/tools/fonts/Montserrat.ttf", 34); en_t.set_variation_by_axes([500])
d.text((W - margin, 95), "کاراکتر شیت چهره — سبحان صمدی", font=fa_b, fill=(41, 56, 108), anchor="rm", direction="rtl", language="fa")
d.text((margin, 95), "FACE REFERENCE  ·  SOBHAN SAMADI", font=en_t, fill=(184, 145, 74), anchor="lm")
d.line([(margin, 170), (W - margin, 170)], fill=(214, 216, 220), width=3)
for n, (p, (_, fa, e)) in enumerate(zip(panels, ORDER)):
    x = W - margin - (n + 1) * PW - n * gap
    sheet.paste(p, (x, top)); d.rectangle([x, top, x + PW - 1, top + PH - 1], outline=(214, 216, 220), width=2)
    d.text((x + PW // 2, top + PH + 52), fa, font=fa_m, fill=(41, 56, 108), anchor="mm", direction="rtl", language="fa")
    d.text((x + PW // 2, top + PH + 108), e, font=en, fill=(150, 150, 155), anchor="mm")
sheet.save("sobhan_face_sheet.jpg", quality=96)
for n, p in enumerate(panels): p.save(f"face_view_{n + 1}.jpg", quality=96)   # single views for video tools
print(sheet.size)
