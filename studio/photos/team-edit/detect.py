import cv2, numpy as np
im = cv2.imread("original.jpg"); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
def peaks(tpl_box, region, thr):
    x0, y0, x1, y1 = tpl_box; t = g[y0:y1, x0:x1]
    rx0, ry0, rx1, ry1 = region
    r = cv2.matchTemplate(g[ry0:ry1, rx0:rx1], t, cv2.TM_CCOEFF_NORMED)
    pts = []
    while True:
        _, v, _, (x, y) = cv2.minMaxLoc(r)
        if v < thr: break
        pts.append((x + rx0, y + ry0, round(v, 2)))
        cv2.rectangle(r, (x - 45, y - 60), (x + 45, y + 60), -1, -1)
    return sorted(pts, key=lambda p: (p[1] // 60, p[0]))
W = peaks((655, 55, 760, 185), (585, 0, 2130, 1040), 0.35)
print("white", len(W)); [print(p) for p in W]
