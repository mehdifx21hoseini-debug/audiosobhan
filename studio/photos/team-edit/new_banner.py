"""Replace the backdrop with a new clean banner design and map it into the photo.

1. design.png  - flat print design (white, logo + academy name on top, navy base band)
2. the design is warped onto the curved banner (bottom follows the stand),
   lit with the banner's own shading, softened like the lens blur, then put
   behind the people (SAM masks) -> step4_banner.png
"""
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

BR = "../../brand/"; FN = "../../fonts/"
NAVY, GOLD = (41, 56, 108), (184, 145, 74)
DW, DH = 1533, 1330                       # design px == photo px (banner is ~flat)

def font(path, size, wght=None):
    f = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    if wght: f.set_variation_by_axes([wght])
    return f

def tracked(d, xy, text, f, fill, track):
    w = sum(f.getlength(c) for c in text) + track * (len(text) - 1)
    x, y = xy[0] - w / 2, xy[1]
    for c in text:
        d.text((x, y), c, font=f, fill=fill, anchor="ls"); x += f.getlength(c) + track
    return w

# ---------------------------------------------------------------- design
SS = 2
D = Image.new("RGB", (DW * SS, DH * SS), "white"); d = ImageDraw.Draw(D)
# header lockup: [logo] [persian name / english name], centred on the banner
logo = Image.open(BR + "logo_navy_gold.png").convert("RGBA")
lh = 180 * SS; logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
fa = font(FN + "Vazirmatn-Black.ttf", 84 * SS)
en = font("/home/user/tools/fonts/Montserrat.ttf", 31 * SS, 600)
fa_txt, en_txt = "آکادمی سبحان صمدی", "SOBHAN SAMADI ACADEMY"
fa_w = d.textlength(fa_txt, font=fa, direction="rtl", language="fa")
en_w = sum(en.getlength(c) for c in en_txt) + 9 * SS * (len(en_txt) - 1)
txt_w = max(fa_w, en_w); gap = 44 * SS
total = logo.width + gap + txt_w
cx, top = DW * SS / 2, 112 * SS
x_logo = cx + total / 2 - logo.width                      # logo on the right (RTL reading order)
D.paste(logo, (int(x_logo), int(top)), logo)
tx_c = x_logo - gap - txt_w / 2
d.text((tx_c, top + 100 * SS), fa_txt, font=fa, fill=NAVY, anchor="ms", direction="rtl", language="fa")
tracked(d, (tx_c, top + 156 * SS), en_txt, en, GOLD, 9 * SS)
# navy base band with a fine gold rule and the web / instagram line
band_h = 262 * SS; by = DH * SS - band_h
d.rectangle([0, by, DW * SS, DH * SS], fill=NAVY)
d.rectangle([0, by, DW * SS, by + 7 * SS], fill=GOLD)
small = font("/home/user/tools/fonts/Montserrat.ttf", 30 * SS, 500)
tracked(d, (300 * SS, by + 125 * SS), "sobhansamadi.com", small, (235, 225, 200), 4 * SS)
tracked(d, (300 * SS, by + 180 * SS), "@sobhansamadi", small, GOLD, 4 * SS)
D = D.resize((DW, DH), Image.LANCZOS); D.save("design.png")

# ---------------------------------------------------------------- photo mapping
img = cv2.imread("step3_text.png").astype(np.float32)
H, W = img.shape[:2]
BX0, BX1 = 591, 2131
def quad(pts):
    c = np.polyfit([p[0] for p in pts], [p[1] for p in pts], 2); return lambda x: np.polyval(c, x)
band_bot = quad([(615, 1279), (1180, 1255), (2060, 1295)])
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
bot = band_bot(xx)
# design row for each photo pixel (bottom of print sits on the stand), slight perspective scale
scale = 1 + (xx - 655) * (2 / 1210) / 137
mx = (xx - BX0).astype(np.float32)
my = (DH - (bot - yy) / scale).astype(np.float32)
Dm = cv2.cvtColor(np.array(D), cv2.COLOR_RGB2BGR).astype(np.float32)
warped = cv2.remap(Dm, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

# banner shading: white level of the current backdrop with logos/people removed
people = np.zeros((H, W), np.uint8)
for k in ("p3", "p4", "p5"): people |= (cv2.imread(f"mask_{k}.png", 0) > 0).astype(np.uint8)
closed = cv2.morphologyEx(people, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35)))
b_, g_, r_ = [img[..., i] for i in range(3)]
dark_neutral = ((b_ + g_ + r_) / 3 < 85) & (b_ - r_ < 14)      # suit/shadow, not banner print
people = people | (closed.astype(bool) & dark_neutral).astype(np.uint8)
band_top = quad([(615, 1020), (900, 1005), (2060, 1039)])
white_zone = (yy < band_top(xx) - 8) & (xx > BX0 + 8) & (xx < BX1 - 8)
mx_ = cv2.dilate(img, cv2.getStructuringElement(cv2.MORPH_RECT, (71, 71)))
hole = (~white_zone | (cv2.dilate(people, np.ones((91, 91), np.uint8)) > 0)).astype(np.uint8)
s = 4
sm = cv2.resize(mx_, None, fx=1 / s, fy=1 / s, interpolation=cv2.INTER_AREA)
hs = cv2.resize(hole, (sm.shape[1], sm.shape[0]), interpolation=cv2.INTER_NEAREST)
sm = cv2.inpaint(np.clip(sm, 0, 255).astype(np.uint8), hs, 25, cv2.INPAINT_TELEA).astype(np.float32)
shade = cv2.resize(cv2.GaussianBlur(sm, (0, 0), 8), (W, H), interpolation=cv2.INTER_CUBIC)
shade *= 0.975                                   # local max sits a touch above the true paper level

flare = 0.10                                     # veiling glare lifts the darks like the real print
out_b = shade * ((warped / 255) * (1 - flare) + flare)
out_b = cv2.GaussianBlur(out_b, (0, 0), 1.6)     # lens defocus on the backdrop
out_b += np.random.default_rng(7).normal(0, 2.0, out_b.shape)

region = ((xx >= BX0) & (xx < BX1) & (yy < bot)).astype(np.float32)
region = cv2.GaussianBlur(region, (0, 0), 1.0)
keep = cv2.GaussianBlur((people > 0).astype(np.float32), (0, 0), 0.8)
A = (region * (1 - keep))[..., None]
res = img * (1 - A) + out_b * A
cv2.imwrite("step4_banner.png", np.clip(res, 0, 255).astype(np.uint8))
print("ok")
