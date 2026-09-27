# استودیوی ریلز آکادمی سبحان صمدی

ابزار و فایل‌های ساخت ریلزهای اینستاگرام آکادمی: برند، موتور انیمیشن، ویس‌ها و خروجی‌ها.

## راهنمای برند (تأییدشده)

| مورد | مقدار |
|---|---|
| لوگو در ویدیو | **گزینه «الف»**: نشان سفید گرد بالا سمت راست، لوگو با رنگ‌های اصلی + «آکادمی سبحان صمدی» و «Sobhan Samadi Academy» |
| فایل لوگو | `brand/logo_navy_gold.png` (پس‌زمینه شفاف، رنگ اصلی) — `brand/logo_white_gold.png` (نسخه سفید/طلایی) — `brand/logo_source.png` (فایل اصلی) |
| سرمه‌ای | `#29386c` (لوگو) · پس‌زمینه‌ها `#040a1c` → `#1a3572` |
| طلایی | `#d6b270` / روشن `#f0d9a0` |
| رنگ‌های تأکید | سبز سود `#46d696` · قرمز ضرر `#ff6b76` · آبی `#8cc4ff` |
| فونت | Vazirmatn (Black برای تیتر، Bold برای زیرنویس، Medium برای متن) — `fonts/` (مجوز OFL) |
| زیرنویس | کارائوکه؛ کلمه‌های کلیدی رنگی (`^g` سبز، `^r` قرمز، `^y` طلایی، `^b` آبی در `tl.json`) |
| پایان هر ریلز | نشان بزرگ آکادمی + «سیوش کن و برای رفیق معامله‌گرت بفرست» |

## ساختار

```
studio/
  brand/      لوگوها، عکس بدون پس‌زمینه سبحان (sobhan.png)، بافت دانه فیلم
  fonts/      Vazirmatn
  engine/     render_par.js (رندر فریم‌به‌فریم با کروم)، chars.js (خرگوش و لاک‌پشت)
  reels/
    domino/         ریلز «اثر دومینو» (reel.html + tl.json + reel_audio.py + عکس‌ها)
    tortoise-hare/  تست سطح ۱ خرگوش و لاک‌پشت (scene2.html)
    python-v1/      موتور قدیمی پایتون (فقط مرجع؛ مسیرهایش به‌روز نیست)
  voice/
    originals/      ویس‌های اصلی سبحان
    transcripts/    متن ویس‌ها با زمان‌بندی (rough = مدل small، accurate = مدل medium)
  output/     ریلزهای نهایی
```

## ویس‌ها

| فایل | موضوع | ریلز |
|---|---|---|
| `voice1_sanctions_usdt.m4a` | واریز و برداشت، تتر و بروکر در شرایط تحریم | ریلز «تحریم» |
| `voice2_discipline.m4a` | دیسیپلین، لاک‌پشت و خرگوش، گلوله برفی | ریلز خرگوش و لاک‌پشت |
| `voice3_profit_outside_plan.m4a` | سود خارج از پلن، کازینو، اثر دومینو | ریلز «اثر دومینو» |

زمان دقیق تکه‌های استفاده‌شده هر ریلز در `reels/<name>/tl.json` (فیلد `src` = ثانیه در ویس اصلی) ثبت شده.

## ساخت دوباره ریلز «اثر دومینو»

```bash
# 1) ابزارها
cd studio/engine && npm install          # gsap + playwright-core
pip install numpy soundfile              # برای صدا
# 2) تمیز کردن ویس (خروجی کنار reel_audio.py)
ffmpeg -i ../voice/originals/voice3_profit_outside_plan.m4a -ac 1 -ar 48000 \
  -af "highpass=f=75,afftdn=nr=12:nf=-45:tn=1,equalizer=f=200:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=9000:t=q:w=1:g=1.5,deesser=i=0.3,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=4,alimiter=limit=0.9" \
  ../reels/domino/voice3_clean48.wav
# 3) صدا
cd ../reels/domino && python3 reel_audio.py        # -> reel_mix.wav
# 4) تصویر (۴ بخش موازی، ۶۰ فریم)
for k in 0 1 2 3; do node ../../engine/render_par.js reel.html 60 part_$k.mp4 --part $k/4 & done; wait
printf "file 'part_0.mp4'\nfile 'part_1.mp4'\nfile 'part_2.mp4'\nfile 'part_3.mp4'\n" > parts.txt
ffmpeg -f concat -safe 0 -i parts.txt -i reel_mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart domino_reel.mp4
# پیش‌نمایش چند فریم:  node ../../engine/render_par.js reel.html 60 x.mp4 "stills=2.6,27,52"
```

متغیرهای محیطی: `FFMPEG` (مسیر ffmpeg)، `CHROME` (مسیر کروم/کرومیوم)، `VOICE_CLEAN` (مسیر ویس تمیزشده).

## عکس‌ها

عکس‌های `reels/domino/ph/` رو خود آکادمی انتخاب و ارسال کرده. قبل از انتشار، مجوز هر عکس رو چک کنید؛
به‌خصوص `domino_s.jpg` (۶۱۲×۶۱۲ پیکسل) که اندازه‌اش شبیه پیش‌نمایش سایت‌های عکس پولی (مثل iStock) است.
