# Content Factory — Repository Audit

> وضعیت: **ممیزی اولیه** · تاریخ: 2026-09-27 · شاخه: `claude/eager-heisenberg-61sao6`
> هدف این سند: مشخص کردن اینکه برای ساخت «کارخانه‌ی محتوای سبحان صمدی» الان چه چیزی داریم، چه چیزی نداریم، و از کجا باید شروع کرد.
> هیچ معماری جدیدی هنوز پیاده نشده؛ این سند فقط وضعیت فعلی را ثبت می‌کند.

---

## 1. خلاصه‌ی مدیریتی

| موضوع | وضعیت |
|---|---|
| موتور رندر (HTML/GSAP → Chromium → FFmpeg) | ✅ کار می‌کند، پایدار، 1080×1920 / 60fps |
| پردازش صدا (تمیزکاری، برش روی سکوت، میکس، موزیک و SFX سنتز‌شده) | ✅ کار می‌کند، ولی کد در هر ریلز تکرار شده |
| زیرنویس فارسی کارائوکه + رنگ کلمه‌ی کلیدی | ✅ کار می‌کند، ولی زمان‌بندی کلمه‌ای واقعی ندارد (پخش یکنواخت روی جمله) |
| تبدیل گفتار به متن (Whisper medium، زمان کلمه‌ای) | ✅ کار می‌کند، کیفیت متن فارسی متوسط |
| تولید تصویر محلی (SDXL-Turbo) + نقشه‌ی عمق + دوربین 2.5D | ✅ کار می‌کند، ~۵۰ ثانیه برای هر تصویر |
| لب‌خوانی/سرِ سخنگو (SadTalker) | ⚠️ نصب شده، روی CPU بسیار کند (~۸۰ دقیقه برای ۸ ثانیه در حالت 512)، کامل نشده |
| **ساختار داده‌ی مشترک (manifest / storyboard)** | ❌ وجود ندارد — هر ریلز فرمت `tl.json` خودش را دارد |
| **قالب‌ها (templates) و preset ها** | ❌ وجود ندارد — هر ریلز یک `reel.html` دست‌نویس است |
| **QA خودکار** | ❌ وجود ندارد — بررسی با نگاه کردن دستی به فریم‌ها انجام شده |
| Project ID، نسخه‌بندی، state، لاگ | ❌ وجود ندارد |
| Provider abstraction، صف کار، API | ❌ وجود ندارد |
| n8n | ❌ اتصال خراب (بخش 8) |
| هویت برند شخصی سبحان | ❌ تعریف نشده — فعلاً برند «آکادمی» استفاده شده (بخش 7) |

**جمع‌بندی:** «موتور» (render/audio/subtitle/AI-image) به‌صورت اثبات‌شده وجود دارد، ولی «کارخانه» (داده‌ی ساختاریافته، قالب، QA، state، نسخه، provider) وجود ندارد. هر ریلز الان یک پروژه‌ی دست‌ساز است. کار اصلی فاز ۱ استخراج همین موتورها به اجزای قابل‌استفاده‌ی مجدد است — نه نوشتن از صفر.

---

## 2. ساختار فعلی مخزن

```
/                       ← وب‌اپ «کتاب‌های صوتی آکادمی» (محصول جدا، ربطی به ریلز ندارد)
├── index.html, css/, js/ (app.js, data.js, player.js), images/logo.jpg, README.md
└── studio/             ← همه‌ی کارهای ریلز
    ├── brand/          logo_navy_gold.png, logo_white_gold.png, logo_source.png, sobhan.png, grain.png
    ├── fonts/          Vazirmatn (Regular/Medium/Bold/ExtraBold/Black) + OFL
    ├── engine/         render_par.js (رندر موازی فریم‌به‌فریم), chars.js (کاراکتر SVG خرگوش/لاک‌پشت), package.json
    ├── reels/
    │   ├── domino/         ویس ۳ — reel.html, tl.json, reel_audio.py, ph/*.jpg
    │   ├── sanctions/      ویس ۱ — reel.html, tl.json, make_tl.py, reel_audio.py
    │   ├── tortoise-hare/  scene2.html (تست سطح ۱، SVG)
    │   ├── hare-ai/        تست ۸ ثانیه‌ای AI — gen.py, depth.py, reel.html (WebGL), reel_audio.py, img/*.png
    │   ├── sobhan-talk/    اسکلت ویدئوی سخنگو (ناتمام) — face_src.png, reel.html, tl.json
    │   └── python-v1/      موتور قدیمی پایتون (فقط مرجع)
    ├── voice/originals/    ۳ ویس اصلی (.m4a)
    ├── voice/transcripts/  rough (small) و accurate (medium)
    └── output/             ۵ ویدئوی نهایی (.mp4)
```

**ابزارهای خارج از مخزن** (موقت؛ با پاک شدن سرور از بین می‌روند):
- `/home/user/tools/SadTalker`, `/home/user/tools/Wav2Lip` (کلون گیت‌هاب؛ SadTalker با ۴ وصله‌ی سازگاری اصلاح شده)
- `/home/user/tools/st` — virtualenv جدا برای SadTalker/GFPGAN
- `~/.cache/huggingface` — مدل‌ها (SDXL-Turbo، Depth-Anything-V2-Small، Whisper medium) — **۱۵ گیگ**
- پکیج‌های pip سراسری: torch (CPU)، diffusers، transformers، faster-whisper، numpy، soundfile، imageio-ffmpeg
- `/usr/local/bin/ffmpeg` → باینری imageio-ffmpeg (ffmpeg سیستم نصب نبود)

---

## 3. قابلیت‌های فعلی (بر اساس کد)

### 3.1 رندر — `studio/engine/render_par.js`
- صفحه‌ی HTML را در Chromium بدون سر باز می‌کند، `window.seek(t)` را برای هر فریم صدا می‌زند، اسکرین‌شات JPEG را به ffmpeg (libx264، CRF 17) پایپ می‌کند.
- رندر موازی با `--part k/N`؛ فریم‌های نمونه با `stills=t1,t2`.
- قرارداد صفحه: `window.TL` (از `tl.json` کنار صفحه)، `window.DUR`، `window.seek(t)`، `window.ready`.
- WebGL از طریق SwiftShader فعال شده (برای shader پارالاکس).
- **نقطه‌ی قوت:** قطعی (deterministic)، هر فریم قابل بازتولید، مستقل از سرعت ماشین.
- **ضعف:** فقط JPEG (بدون آلفا)، قرارداد صفحه مستند نیست، خطاها فقط در کنسول.

### 3.2 صحنه‌ها — `reels/*/reel.html`
- GSAP timeline + SVG + HTML/CSS؛ فونت Vazirmatn؛ پیش‌فرض‌های برند (کپسول لوگو، زیرنویس، vignette، grain، outro).
- **مشکل اصلی:** بین ریلزها کپی‌پیست شده (استایل‌ها، `setSub`، `karaoke`، `showScene`، `shake`، outro). هیچ component/preset مشترکی وجود ندارد.

### 3.3 صدا — `reels/*/reel_audio.py`, `reels/sanctions/make_tl.py`
- زنجیره‌ی تمیزکاری ویس با ffmpeg (highpass، afftdn، EQ، de-esser، compressor، limiter).
- `make_tl.py`: انتخاب تکه‌ها با `PLAN`، چسباندن لبه‌ها به کم‌صداترین فریم، ساخت زیرنویس و صحنه‌ها → بهترین الگوی موجود برای «storyboard از داده».
- سنتز موزیک (آکورد، بیس، پالس، کیک/هت/اسنر) و SFX (whoosh، riser، impact، click، ding، glitch، heartbeat…) با numpy؛ ducking بر اساس انرژی ویس.
- **ضعف:** توابع SFX در هر فایل کپی شده؛ نرمال‌سازی loudness استاندارد (LUFS) انجام نمی‌شود — فقط `tanh` + سقف ۰.۹۵.

### 3.4 گفتار به متن
- faster-whisper medium (int8، CPU): ~۴۰ دقیقه برای ۱۵ دقیقه صدا؛ زمان کلمه‌ای.
- اسکریپتش در مخزن نیست (در scratchpad اجرا شد) → باید وارد مخزن شود.

### 3.5 تصویر AI و حرکت
- `hare-ai/gen.py`: SDXL-Turbo، 768×1344، ۴ step، ~۵۰ ثانیه/تصویر، bf16 روی CPU.
- `hare-ai/depth.py`: Depth-Anything-V2-Small → نقشه‌ی عمق.
- `hare-ai/reel.html`: shader WebGL با پارالاکس عمق، zoom blur شعاعی، RGB split، رنگ‌بندی هر شات.
- Pollinations تست شد: کیفیت پایین + واترمارک → رد شد.

### 3.6 سرِ سخنگو
- SadTalker (512 + GFPGAN) روی CPU: ~۴۰ ثانیه برای هر ۲ فریم → غیرعملی برای تولید. متوقف شد.

---

## 4. وابستگی‌ها

| جزء | نسخه / منبع | ثبت در مخزن؟ |
|---|---|---|
| Node 22، gsap ^3.15، playwright-core ^1.56 | npm | ✅ `package.json` |
| Chromium | `/opt/pw-browsers` | ❌ فرض محیط |
| FFmpeg | imageio-ffmpeg v7.0.2 | ❌ دستی نصب شد |
| Python 3.11: numpy، soundfile | pip | ❌ `requirements` ندارد |
| torch 2.14 CPU، diffusers 0.40، transformers 5.17 | pip | ❌ |
| faster-whisper | pip | ❌ |
| SadTalker + GFPGAN + basicsr (وصله‌شده) | git + venv | ❌ |

**ریسک:** محیط قابل بازتولید نیست. سرور بعدی یعنی ~۲۰ دقیقه نصب دستی و دانلود ~۲۰ گیگ مدل. نیاز به `requirements.txt` / اسکریپت setup / SessionStart hook.

---

## 5. دارایی‌های موجود

| دارایی | جزئیات | کیفیت |
|---|---|---|
| لوگو نشان «S» با کندل (سرمه‌ای+طلایی) | `logo_navy_gold.png` 281×368، `logo_white_gold.png`، `logo_source.png` 512×512 | ⚠️ وضوح پایین، بدون SVG |
| لوگوی کامل با wordmark «آکادمی سبحان صمدی / Sobhan Samadi Academy» | `images/logo.jpg` 1050×1223 (JPG، پس‌زمینه‌ی سیاه) | ⚠️ بدون شفافیت، مال **آکادمی** |
| عکس سبحان | `sobhan.png` 1498×1050، دوربُری‌شده، نیم‌تنه، روبه‌رو، لبخند، کت آبی | ✅ خوب، ولی فقط **یک** عکس |
| فونت | Vazirmatn (OFL) | ✅ |
| ویس | ۳ ویس (~۱۵–۲۵ دقیقه) | ✅ |
| عکس‌های صحنه | `domino/ph/*.jpg` | ⚠️ مجوز نامشخص (`domino_s.jpg` احتمالاً پیش‌نمایش iStock) |
| تصاویر AI | `hare-ai/img/*` (SDXL-Turbo) | ⚠️ مجوز SDXL-Turbo برای انتشار تجاری باید بررسی شود |

---

## 6. محدودیت‌های فنی محیط

| محدودیت | اثر |
|---|---|
| **بدون GPU**، ۴ هسته CPU | تولید تصویر ~۵۰ ثانیه؛ ویدئوی AI / لب‌خوانی عملاً غیرممکن؛ رندر ۶۰ ثانیه ریلز ~۱۰ دقیقه |
| ۱۵ گیگ RAM | فقط یک کار سنگین AI در هر لحظه |
| **دیسک: فقط ۵.۴ گیگ خالی** (کش HF = ۱۵ گیگ، ابزارها ۴.۵ گیگ، `.git` = ۱۵۸ مگ) | خطر پر شدن دیسک؛ کش باید پاک‌سازی شود |
| سرور موقت | هرچه commit نشود از بین می‌رود؛ مدل‌ها باید دوباره دانلود شوند |
| شبکه | باز: Google، Pinterest، Hugging Face، Freesound، Pollinations، GitHub · بسته: Pexels، Pixabay |
| دسترسی گیت‌هاب | فقط یک مخزن، فقط یک شاخه |
| گوش دادن/تماشا | من صدا را نمی‌شنوم و ویدئو را پخش نمی‌کنم؛ فقط فریم ثابت می‌بینم → کیفیت صدا و روانی حرکت همیشه «بازبینی انسانی» است |
| مجوز اجرای کد خارجی | اجرای کد کلون‌شده نیاز به تأیید صریح کاربر دارد (یک بار رخ داد) |

---

## 7. ریسک‌ها

1. **ابهام برند (بحرانی):** Master Prompt می‌گوید برند «سبحان صمدی — برند شخصی» است، ولی همه‌ی دارایی‌ها و ریلزهای فعلی «آکادمی سبحان صمدی / Sobhan Samadi Academy» هستند. تا روشن نشود، brand engine نباید ساخته شود.
2. **رنگ‌های متناقض:** README ریشه `#1e3a5f` / `#B8860B / #D4A017`؛ studio `#29386c` / `#d6b270`. هیچ‌کدام تأیید رسمی ندارند.
3. **فایل‌های حجیم در Git:** ~۹۰ مگ ویدئو + ۴۷ مگ ویس + ~۳۰ مگ PNG در تاریخچه. با ادامه‌ی این روند مخزن سنگین و کند می‌شود. پیشنهاد: از این به بعد خروجی‌ها در Git نروند (Git LFS یا storage جدا). پاک کردن تاریخچه = بازنویسی history → فقط با اجازه‌ی صریح.
4. **مخزن دو محصول دارد:** وب‌اپ کتاب صوتی در ریشه + studio. کارخانه باید پوشه‌ی مستقل خودش را داشته باشد تا با وب‌اپ قاطی نشود.
5. **هویت و رضایت:** ساخت نسخه‌ی AI یا سخنگوی سبحان فقط با رضایت خودش؛ «حفظ هویت» هنوز تعریف نشده. ساخت چهره‌ی افراد واقعی دیگر (دیپ‌فیک) خارج از محدوده است.
6. **مجوز دارایی‌ها:** عکس‌های domino، مدل SDXL-Turbo، و هر موزیک خارجی قبل از انتشار باید بررسی شوند.
7. **تکرار کد:** هر اصلاح (مثلاً زیرنویس) باید در ۵ فایل تکرار شود → خطا و ناهماهنگی.
8. **وابستگی به من برای QA:** الان QA = نگاه من به چند فریم. قابل اتکا و قابل تکرار نیست.

---

## 8. تشخیص n8n

**مشاهده:** سرور MCP به نام `n8n` در این جلسه پیکربندی شده، ولی موقع اتصال خطا داد:
`502 — SdkHttpError … (CLIENT_HTTP_NOT_IMPLEMENTED)` روی مسیر پروکسی کانکتور.

**آنچه این خطا نشان می‌دهد (و نمی‌دهد):**
- کانکتور **وجود دارد** و به حساب وصل است (پس «تنظیم نشده» نیست).
- 502 یعنی پروکسی کانکتور Anthropic نتوانسته با سرور MCP شما (endpoint نمونه‌ی n8n) گفت‌وگوی درست برقرار کند. `CLIENT_HTTP_NOT_IMPLEMENTED` یعنی سمت مقصد، transport/متد HTTP مورد انتظار را پاسخ نداده.
- آدرس واقعی n8n در خطا پنهان شده؛ من به آن دسترسی مستقیم ندارم.

**علت‌های محتمل (تأییدنشده — باید در سمت n8n بررسی شود):**
1. آدرس ثبت‌شده در کانکتور، آدرس **MCP Server Trigger** نیست (مثلاً آدرس webhook معمولی یا UI است).
2. نمونه‌ی n8n فقط SSE قدیمی را پشتیبانی می‌کند و transport «Streamable HTTP» که کانکتور انتظار دارد را ندارد (نسخه‌ی قدیمی n8n یا نود MCP قدیمی).
3. workflow حاوی MCP Server Trigger فعال (Active) نیست → مسیر production پاسخ نمی‌دهد.
4. نمونه‌ی n8n از اینترنت عمومی در دسترس نیست (localhost/شبکه‌ی خصوصی) یا پشت احراز هویتی است که کانکتور ندارد.

**قدم‌های رفع (سمت شما):**
1. در n8n: workflow با نود **MCP Server Trigger** بسازید/فعال کنید و **Production URL** آن را کپی کنید.
2. n8n را به آخرین نسخه به‌روز کنید (پشتیبانی Streamable HTTP).
3. در https://claude.ai/customize/connectors کانکتور n8n را با همان آدرس دوباره وصل کنید.
4. **یک جلسه‌ی جدید** شروع کنید (کانکتورها فقط در شروع جلسه خوانده می‌شوند).

**اثر بر معماری:** هیچ. طبق اصل «n8n نباید Core باشد»، کارخانه یک API/CLI داخلی می‌سازد که n8n بعداً از بیرون صدایش می‌زند. تا آن موقع n8n لازم نیست.

---

## 9. فرصت‌ها

- `make_tl.py` الگوی درست را دارد (داده → timeline). می‌تواند هسته‌ی **Storyboard Engine** شود.
- قرارداد `window.seek(t)` یک مرز تمیز بین «داده» و «رندر» است → هر template فقط یک صفحه با همین قرارداد.
- رندر قطعی و موازی → امکان **رندر فقط یک صحنه** (scene-level re-render) بدون ساخت دوباره‌ی کل ریلز.
- مجموعه‌ی SFX/موزیک سنتزی → کتابخانه‌ی صوتی بدون مشکل کپی‌رایت، قابل تبدیل به preset.
- WebGL پارالاکس + SDXL-Turbo → یک لایه‌ی بصری «سینمایی» ارزان که روی CPU کار می‌کند.
- Whisper با زمان کلمه‌ای → زیرنویس با زمان‌بندی دقیق کلمه‌ای (الان استفاده نشده).
- بررسی فریم خودکار (bbox متن، ناحیه‌ی امن، فریم سیاه، سطح صدا) با Chromium + ffmpeg کاملاً روی CPU شدنی است.

---

## 10. معماری پیشنهادی (سطح بالا — منتظر تأیید، پیاده نشده)

جزئیات کامل بعد از Intake در «CONTENT FACTORY ARCHITECTURE V1» ارائه می‌شود. جهت کلی:

```
factory/                      ← پکیج مستقل (جدا از وب‌اپ کتاب صوتی)
  core/          project model، state machine، versioning، logging، job runner
  pipeline/      stages: intake → brief → script → storyboard → assets → audio → render → qa
  engines/       audio/ (clean, cut, music, sfx, mix) · subtitles/ · motion/ (GSAP presets) · render/
  providers/     ImageProvider(local_sdxl) · DepthProvider · STTProvider(whisper) · TalkingHead · …
  templates/     هر template = یک صفحه‌ی HTML با قرارداد seek + schema ورودی
  brand/         brand.json (رنگ، فونت، قواعد لوگو، preset زیرنویس) + فایل‌های برند
  qa/            بررسی‌های خودکار + گزارش
  cli.py         تنها ورودی فعلی (بعداً API/Telegram/n8n روی همین)
projects/REEL-0001/
  manifest.json · storyboard.json · research.md · v01/ v02/ final/ · qa_report.json · logs/
```

**تصمیم‌های کلیدی پیشنهادی:**
- **پایتون = ارکستراتور** (صدا، AI، QA، CLI)، **Node/Chromium = فقط رندر**. دلیل: همه‌ی AI و صدا در پایتون است؛ رندر HTML ثابت‌شده و بهترین تایپوگرافی فارسی را دارد.
- **مدل داده‌ی JSON + JSON Schema** برای manifest و storyboard؛ هر مرحله فقط خروجی مرحله‌ی قبل را می‌خواند (قابل retry و cache).
- **Cache بر اساس hash ورودی** برای هر دارایی (تصویر، عمق، صدا، صحنه) → بدون رندر/تولید تکراری.
- **فایل‌های حجیم خارج از Git** (`projects/*/v*/` و `outputs/` در `.gitignore`)؛ فقط manifest، storyboard و کد در Git.

---

## 11. قدم بعدی

1. تکمیل `docs/BRAND_ASSET_INTAKE.md` با کاربر (در حال انجام).
2. ارائه‌ی «CONTENT FACTORY ARCHITECTURE V1» و انتظار برای تأیید.
3. فاز ۱: استخراج موتورهای موجود به `factory/` + ساخت دوباره‌ی یکی از ریلزهای فعلی با آن (برای اثبات اینکه چیزی از دست نرفته).
