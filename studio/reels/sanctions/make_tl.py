"""Builds tl.json for the sanctions reel: picks clips from voice1, snaps cut points to quiet frames."""
import json, os, numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
v, sr = sf.read(os.environ.get("VOICE_CLEAN", os.path.join(HERE, "voice1_clean48.wav")), dtype="float32")
hop = int(.01 * sr); rms = np.sqrt(np.convolve(v ** 2, np.ones(hop * 3) / (hop * 3), "same")[::hop])
def quiet(t, lo, hi):   # quietest 10 ms frame in [t+lo, t+hi]
    a, b = int((t + lo) * 100), int((t + hi) * 100); return (a + int(np.argmin(rms[a:b]))) / 100
# (id, src start, src end, scene, gap before)
PLAN = [
 ("c0", 0.20, 2.24, "hook", .6), ("c1", 3.04, 4.28, "hook", .15), ("c2", 6.00, 8.26, "hook", .15), ("c3", 9.82, 12.10, "hook", .2),
 ("c4", 161.76, 172.68, "net", .55), ("c5", 185.62, 188.60, "net", .25),
 ("c6", 702.82, 704.74, "story", .55), ("c7", 710.60, 712.56, "story", .2), ("c8", 741.39, 749.66, "story", .3),
 ("c9", 776.70, 779.40, "wallet", .55), ("c10", 804.92, 808.24, "wallet", .25),
 ("c11", 384.82, 396.64, "path", .55), ("c12", 419.92, 423.76, "path", .25),
 ("c13", 672.46, 675.66, "sobhan", .55),
]
SUBS = {  # clip id -> [(src start, src end, text)]; ^g ^r ^y ^b colour the next word
 "c0": [(None, None, "^bواریز و ^bبرداشت")], "c1": [(None, None, "خرید ^gتتر")], "c2": [(None, None, "کار کردن با ^bبروکر")],
 "c3": [(None, None, "در این ^rشرایط ^rتحریمی به چه شکلیه؟")],
 "c4": [(None, 164.54, "یک صرافی ایرانی ^rتحریم میشه"), (164.54, None, "یعنی ^yهر ^yکیف ^yپولی که با اون صرافی در ارتباط بوده، عملاً ^rشناسایی ^rمیشه")],
 "c5": [(None, None, "عملاً کیف پولت ^rیه ^rلیبل می‌خوره")],
 "c6": [(None, None, "من ^yتجربه ^yخودم بهت بگم")], "c7": [(None, None, "من با اون والکس ^rکار ^rکرده ^rبودم")],
 "c8": [(None, 745.85, "از ^bوالت ^bخودم به کوینکس پول زدم..."), (745.85, None, "پول ^rمسدود ^rشد! خیلی ^rسریع و راحت")],
 "c9": [(None, None, "اون والت رو ^rدیگه ^rباهاش ^rکار ^rنکن")],
 "c10": [(None, None, "یه ^gوالت ^gدیگه... ^gیک ^gمیلیون والت می‌تونی باز کنی")],
 "c11": [(None, 389.26, "می‌خوای نگهداری کنی؟ صرافی باید بیاد ^bبه ^bولتت"), (389.26, None, "می‌خوای ^gمحکم‌تر بشه؟ از یه ولتت ^yبزن ^yبه ^yیه ^yولت ^yدیگه‌ت")],
 "c12": [(None, None, "ریسکش رو ^gبه ^gمراتب ^gکاهش میدی")],
 "c13": [(None, None, "اگه ^gدرست و ^gاصولی پیش بره، ^yجای ^yنگرانی ^yنیست")],
}
clips, subs, scenes, t = [], [], {}, 0.0
for cid, a, b, sc, gap in PLAN:
    a = quiet(a, -.12, .03); b = quiet(b, -.03, .15); t += gap
    d = [round(t, 2), round(t + b - a, 2)]; clips.append({"id": cid, "src": [a, b], "dst": d, "scene": sc})
    for sa, sb, text in SUBS[cid]:
        x = d[0] if sa is None else d[0] + sa - a; y = d[1] if sb is None else d[0] + sb - a
        subs.append({"dst": [round(x, 2), round(y, 2)], "text": text})
    if sc not in scenes: scenes[sc] = [max(0, round(t - gap / 2, 2)), 0]
    scenes[sc][1] = round(d[1] + .25, 2); t = d[1]
names = list(scenes)
for i in range(len(names) - 1): scenes[names[i]][1] = scenes[names[i + 1]][0]
scenes["hook"][0] = 0.0; end = scenes[names[-1]][1]; scenes["outro"] = [end, round(end + 3.4, 2)]
json.dump({"clips": clips, "subs": subs, "scenes": scenes, "T": scenes["outro"][1]}, open(os.path.join(HERE, "tl.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(scenes), "T =", scenes["outro"][1])
