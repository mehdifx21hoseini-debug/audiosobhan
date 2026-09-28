"""Build tl.json for sobhan-iphone: map whisper word times (source) onto the cut timeline and define subtitle chunks.
Chunk = (first_word_idx, last_word_idx, text). Markers: ^y gold, ^g green, ^r red. ".." marks a censored (half-written) word.
Words are indices into words_large.json (faster-whisper large-v3 on the raw take)."""
import json

W = json.load(open("words_large.json"))
CUTS = json.load(open("cuts.json"))                      # kept source ranges, in order


def dst(t):
    """source seconds -> timeline seconds (clamped into the nearest kept range)."""
    acc = 0.0
    for a, b in CUTS:
        if t < a: return acc
        if t <= b: return round(acc + t - a, 3)
        acc += b - a
    return round(acc, 3)


SUBS = [
    (5, 8, "کسی که ^yتوانمنده می‌گیره"),
    (9, 13, "نوش جونش، حالش رو ببره"),
    (14, 18, "صحبت من دسته از افرادیه"),
    (19, 22, "که ^yطل..ا و ^yدل..ار"),
    (23, 25, "سر..مایه‌گذاری‌شون رو ^rمی‌فرو..شن"),
    (26, 30, "تبدیل به ^rکالای مصرفی می‌کنن"),
    (31, 34, "که صرفاً هدفشون اینه"),
    (35, 40, "خودشون رو به جاری‌شون ^yاثبات بکنن"),
    (41, 46, "این صحبت ^yوارن بافت سال‌های ساله"),
    (47, 52, "که تو مغز منه که می‌گه"),
    # 53-65: quote card (no subtitle)
    (66, 68, "شما وقتی بتونی"),
    (69, 74, "^g۱۰۰ میلیون تومنت رو مدیریت کنی"),
    (75, 82, "می‌تونی ^g۱ میلیارد تومنت رو هم مدیریت کنی"),
    (83, 89, "وقتی بتونی ۱ میلیاردت رو مدیریت کنی"),
    (90, 96, "می‌تونی ^gده تومنت رو هم مدیریت بکنی"),
    (97, 102, "پس نگو اونی که پو..ل داره"),
    (103, 107, "داره پو..لش براش پو..ل میاره"),
    (108, 113, "نه قربونت، اون آدم همون کسیه"),
    (114, 120, "که ^g۱۰۰ تومنش رو تونسته ^gمدیریت بکنه"),
    (121, 123, "و یادت باشه"),
    # 124-133: statement card (no subtitle)
    (134, 138, "خیلی‌ها ^rهوش مالی اشتباهی دارن"),
    (139, 143, "و همین نمی‌ذاره ^gرشد کنن"),
    (144, 149, "من هر روز دارم نکات ارزشمندی رو"),
    (150, 155, "باهات به اشتراک می‌ذارم"),
    (156, 161, "^yنهایت استفاده رو از استوری‌ها ببر"),
]


def spread(i0, i1, n):
    """per-display-word [start,end] on the timeline; display words may differ in count from whisper words."""
    a, b = dst(W[i0]["s"]), dst(W[i1]["e"])
    src = [(dst(W[k]["s"]), dst(W[k]["e"])) for k in range(i0, i1 + 1)]
    if len(src) == n: return [list(x) for x in src]
    step = (b - a) / n
    return [[round(a + k * step, 3), round(a + (k + 1) * step, 3)] for k in range(n)]


subs = []
for i0, i1, text in SUBS:
    n = len(text.split(" "))
    subs.append({"dst": [dst(W[i0]["s"]), dst(W[i1]["e"])], "text": text, "wt": spread(i0, i1, n)})

w = lambda k: dst(W[k]["s"])
VE = round(sum(b - a for a, b in CUTS), 3)
TL = {
    "fps_src": 30, "frames": 1577, "voice_end": VE, "T": round(VE + 4.2, 2),
    "cuts_dst": [round(sum(b - a for a, b in CUTS[:i]), 3) for i in range(len(CUTS))],
    "subs": subs,
    # price card: "آیفون ۱۸ پرومکس ۷۳۰ میلیون تومن"
    "price": {"in": 0.0, "count": w(2), "out": dst(W[8]["e"])},
    # Buffett quote, word by word
    "quote": {"attr": w(43), "in": w(53) - .15, "words": [[w(k), W[k]["w"]] for k in range(53, 66)], "out": dst(W[65]["e"]) + .25},
    # money ladder
    "ladder": {"in": w(66), "r1": w(69), "r2": w(76), "r3": w(91), "out": dst(W[96]["e"]) + .1},
    # statement: "ثروتمند واقعی دنبال اثبات خودش به یک شخص دیگه نیست"
    "state": {"in": w(124) - .1, "w": [w(k) for k in range(124, 134)], "out": dst(W[133]["e"]) + .2},
    "cta": w(156),
    # v2 scenes
    "assets": {"in": w(19) - .25, "gold": w(20), "usd": w(22), "sell": w(25), "cons": w(28), "out": dst(W[30]["e"]) + .2},
    "growth": {"in": w(134) - .2, "bad": w(137), "grow": w(142), "out": dst(W[143]["e"]) + .35},
    "punch": [w(108) - .05, w(113) - .05],
}
# v3 split-screen windows (info panel on top, Sobhan below); between them the frame is full-screen Sobhan
TL["splits"] = [
    [0.0, TL["price"]["out"] + .3, "price"],
    [TL["assets"]["in"], TL["assets"]["out"], "assets"],
    [w(41) - .15, TL["ladder"]["out"], "quote"],          # "این صحبت وارن بافت…" through the money ladder
    [TL["state"]["in"] - .1, TL["growth"]["out"], "state"],
    [w(156) - .25, VE, "cta"],
]
json.dump(TL, open("tl.json", "w"), ensure_ascii=False, indent=1)
print("voice_end", VE, "T", TL["T"], "subs", len(subs))
print("price", TL["price"], "quote in/out", TL["quote"]["in"], TL["quote"]["out"], "ladder", TL["ladder"], "state", TL["state"]["in"], TL["state"]["out"])
