"""Re-letter the banner words hidden behind the removed person's head."""
import sys, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
img = cv2.imread("step2_banner.png").astype(np.float32)
H, W = img.shape[:2]
SS = 4

def glyph_alpha(text, font, wght, box, rtl, track=0):
    f = ImageFont.truetype(font, 80 * SS, layout_engine=ImageFont.Layout.RAQM)
    if wght: f.set_variation_by_axes([wght])
    if track:  # manual tracking for latin
        widths = [f.getbbox(ch)[2] for ch in text]
        cw = sum(widths) + track * SS * (len(text) - 1) + 40 * SS
        im = Image.new("L", (cw, 140 * SS), 0); d = ImageDraw.Draw(im); x = 20 * SS
        for ch, w in zip(text, widths): d.text((x, 20 * SS), ch, font=f, fill=255); x += w + track * SS
    else:
        im = Image.new("L", (900 * SS, 200 * SS), 0)
        ImageDraw.Draw(im).text((450 * SS, 100 * SS), text, font=f, fill=255, anchor="mm",
                                direction="rtl" if rtl else None, language="fa" if rtl else None)
    a = np.array(im); ys, xs = np.nonzero(a > 20)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    x0, y0, x1, y1 = box
    return cv2.resize(a.astype(np.float32) / 255, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)

def put(alpha, box, color, region, sigma):
    x0, y0, x1, y1 = box
    A = np.zeros((H, W), np.float32); A[y0:y1, x0:x1] = alpha
    A = cv2.GaussianBlur(A, (0, 0), sigma)
    rx0, rx1, ry0, ry1 = region
    lim = np.zeros((H, W), np.float32); lim[ry0:ry1, rx0:rx1] = 1
    lim = cv2.GaussianBlur(lim, (0, 0), 3)
    A = (A * lim)[..., None]
    return img * (1 - A) + np.array(color, np.float32) * A

def clear(x0, y0, x1, y1):
    global img
    m = np.zeros((H, W), np.uint8); m[y0:y1, x0:x1] = 255
    u8 = np.clip(img, 0, 255).astype(np.uint8)
    fill = cv2.inpaint(u8, m, 9, cv2.INPAINT_TELEA).astype(np.float32)
    fill = cv2.GaussianBlur(fill, (0, 0), 6)
    noise = np.random.default_rng(5).normal(0, 2.0, fill.shape).astype(np.float32)
    k = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 2)[..., None]
    img = img * (1 - k) + (fill + noise) * k

def fit_h(alpha_full_h, h):  # keep the font's aspect ratio for a target height
    return int(round(alpha_full_h[1] * h / alpha_full_h[0]))

def natural(text, font, wght, rtl, track=0):
    a = glyph_alpha(text, font, wght, (0, 0, 1000, 1000), rtl, track)  # dummy to get aspect
    return a

def aspect(text, font, wght, rtl, track=0):
    f = ImageFont.truetype(font, 80 * SS, layout_engine=ImageFont.Layout.RAQM)
    if wght: f.set_variation_by_axes([wght])
    if track:
        widths = [f.getbbox(ch)[2] for ch in text]; w = sum(widths) + track * SS * (len(text) - 1)
        b = f.getbbox(text); return (b[3] - b[1], w)
    b = f.getbbox(text, direction="rtl" if rtl else None, language="fa" if rtl else None)
    return (b[3] - b[1], b[2] - b[0])

FA = ("صمدی", "../../fonts/Vazirmatn-Bold.ttf", None, True)
fa_top, fa_bot, fa_right = 182, 250, 1130
w = fit_h(aspect(*FA), fa_bot - fa_top)
clear(880, 172, 1135, 258)
box = (fa_right - w, fa_top, fa_right, fa_bot)
img = put(glyph_alpha(FA[0], FA[1], FA[2], box, True), box, (112, 64, 50), (0, W, 0, H), 2.1)

EN = ("Sobhan S", "/home/user/tools/fonts/Montserrat.ttf", 600, False, 9)
en_top, en_bot, en_left = 272, 307, 895
clear(882, 262, 1150, 318)
box = (en_left, en_top, 1146, en_bot)
img = put(glyph_alpha(EN[0], EN[1], EN[2], box, False, EN[4]), box, (142, 168, 190), (0, W, 0, H), 2.1)
cv2.imwrite("step3_text.png", np.clip(img, 0, 255).astype(np.uint8))
Image.open("step3_text.png").crop((860, 160, 1240, 330)).resize((1140, 510)).save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/t.png")
