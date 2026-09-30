# Future Integration Architecture
## Telegram Control Center · Human Approval · Instagram Publishing

> وضعیت: **طراحی — پیاده نشده** · تاریخ: 2026-09-27
> مبنا: `docs/CONTENT_FACTORY_AUDIT.md`. این سند مشخص می‌کند که Core چطور ساخته شود تا Telegram، Instagram و n8n بعداً **بدون بازنویسی Core** اضافه شوند.
> اصل حاکم: *Future-ready architecture without premature implementation.*

---

## 0. نتیجه‌ی مقایسه (وضعیت فعلی در برابر نیازها)

الان در مخزن **هیچ Core** وجود ندارد که Telegram یا Instagram بخواهند به آن وصل شوند: نه Project ID، نه state، نه نسخه، نه صف کار، نه API. هر ریلز یک پوشه‌ی دست‌ساز است و با دستورهای shell اجرا می‌شود.

پس «refactor برای آماده‌سازی» عملاً همان **ساخت Core در فاز ۱** است. خبر خوب: هیچ کدی وجود ندارد که بعداً مانع شود، و موتورهای موجود (render، audio، subtitle، AI image) بدون تغییر اساسی زیر Core قرار می‌گیرند.

---

## 1. چه چیزهایی همین الان آماده‌اند

| جزء | وضعیت برای یکپارچه‌سازی آینده |
|---|---|
| رندر قطعی (`render_par.js`، قرارداد `window.seek`) | ✅ مستقل از رابط؛ می‌تواند داخل Worker اجرا شود |
| رندر موازی بخش‌به‌بخش (`--part k/N`) | ✅ پایه‌ی رندر فقط یک صحنه |
| Whisper با زمان کلمه‌ای | ✅ همان چیزی است که ورودی ویس تلگرام لازم دارد |
| زنجیره‌ی تمیزکاری صدا | ✅ |
| الگوی «داده → timeline» در `make_tl.py` | ✅ پایه‌ی Storyboard Engine |
| خروجی MP4 استاندارد (H.264، 9:16، ≤۹۰ ثانیه ممکن) | ✅ با شرایط Reels اینستاگرام سازگار است |

## 2. چه چیزهایی نیاز به Refactor دارند

| مورد فعلی | مشکل | Refactor |
|---|---|---|
| `reels/<name>/` با فایل‌های دست‌ساز | بدون Project ID، بدون نسخه | → `projects/REEL-XXXX/` با manifest و `vNN/` |
| `tl.json` با schema متفاوت در هر ریلز | ماشین نمی‌تواند بخواند یا تغییر دهد | → `storyboard.json` با JSON Schema واحد |
| `reel.html` کپی‌پیست‌شده | تغییر فقط-هوک یا فقط-یک-صحنه ممکن نیست | → template + component + preset؛ صحنه‌ها از داده ساخته شوند |
| `reel_audio.py` تکراری | | → `engines/audio` با preset ها |
| اجرای دستی با shell | بدون log، retry، state | → `JobRunner` + stageهای ثبت‌شده |
| خروجی‌ها و ویس‌ها داخل Git | مخزن سنگین می‌شود؛ آدرس عمومی برای اینستاگرام ندارد | → `StorageProvider`؛ Git فقط برای کد و metadata |
| ابزارهای خارج از مخزن (SadTalker، مدل‌ها) | قابل بازتولید نیست | → `requirements` + اسکریپت setup |

## 3. Abstractionهایی که **همین الان** (فاز ۱) ساخته شوند

فقط مواردی که بدون آن‌ها Core بعداً باید بازنویسی شود:

| Abstraction | چرا الان | حداقل پیاده‌سازی فاز ۱ |
|---|---|---|
| **Project + Manifest** (`project_id`، `workspace_id`، `owner_id`) | Telegram، تأیید، نسخه و انتشار همه به Project ID وصل‌اند | فایل JSON روی دیسک |
| **State Machine** (بخش 7) | بدون آن، تأیید و انتشار با boolean های پراکنده خراب می‌شود | enum + جدول گذارهای مجاز + تاریخچه |
| **Versioning** (بخش 13) | revise فقط-هوک و «برگرد به v02» | پوشه‌ی `vNN/` غیرقابل‌تغییر |
| **Stage/Job interface** (`run(project, version) → artifacts`) | Worker آینده همین را صدا می‌زند؛ retry یک مرحله | اجرای هم‌زمان (sync) از CLI |
| **Event bus داخلی** (`emit("render.completed", …)`) | اعلان تلگرام بعداً فقط یک subscriber است | لاگ به فایل `events.jsonl` |
| **StorageProvider** | اینستاگرام آدرس عمومی لازم دارد؛ نباید مسیر محلی در Core hard-code شود | `LocalStorage` |
| **Provider interfaces** (Image، Depth، STT، TalkingHead، Music، Voice) | طبق Master Prompt | پیاده‌سازی‌های محلی فعلی |
| **Audit log** (who/what/when/project/action/result) | افزودنش بعداً یعنی گم شدن تاریخچه | `audit.jsonl` برای هر پروژه |
| **CLI واحد** (`factory new/status/render/approve/…`) | همین فرمان‌ها بعداً endpoint های API و intent های تلگرام می‌شوند | پایتون |

## 4. چه چیزهایی **فعلاً ساخته نشوند**

- Telegram Bot، Instagram Publisher، OAuth، workflow n8n
- سرور HTTP API (تا وقتی CLI و لایه‌ی سرویس پایدار نشده؛ API یک لایه‌ی نازک روی همان سرویس‌ها خواهد بود)
- صف پیام خارجی (Redis/RabbitMQ)، microservice ها، Kubernetes
- Object storage ابری، پلتفرم چندکاربره، Web UI
- Intent Router با LLM

## 5. Telegram دقیقاً از کجا وصل می‌شود

```
Telegram ──► TelegramAdapter (interfaces/telegram/)
                 │  • احراز هویت (AUTHORIZED_USERS / CHAT_IDS)
                 │  • تبدیل پیام/ویس/فایل → Command یا Message
                 │  • تبدیل Event → پیام/دکمه‌ی تلگرام
                 ▼
          ContentManager (conversation + intent + project context)
                 │
                 ▼
          ProjectService  ◄── همان سرویسی که CLI امروز صدا می‌زند
                 │
                 ▼
          JobQueue ──► Worker ──► Pipeline stages ──► Events ──► TelegramAdapter.notify
```

- **Adapter هیچ منطق کسب‌وکاری ندارد**؛ فقط ترجمه می‌کند. هر کاری که از تلگرام ممکن است، از CLI هم ممکن است.
- ویس تلگرام → `STTProvider` (همان Whisper) → متن قابل‌ویرایش در پروژه ذخیره می‌شود.
- دکمه‌های ✅✏️🔄❌ = فراخوانی `approve / revise / regenerate / reject` روی `ProjectService`.
- **Callback ها با `project_id + version + action_nonce`**، تا دکمه‌ی یک پیام قدیمی نسخه‌ی اشتباه را تأیید نکند.
- محدودیت: API استاندارد ربات تلگرام برای ارسال فایل ~۵۰MB سقف دارد → فایل `DELIVERY` جدا از `MASTER` لازم است (بخش 8). با سرور محلی Bot API سقف بالاتر است (در صورت نیاز). *(باید هنگام پیاده‌سازی دوباره بررسی شود.)*

## 6. Instagram Publishing دقیقاً از کجا وصل می‌شود

```
ProjectService.approve(version)            ← فقط از وضعیت READY_FOR_REVIEW
        │
        ▼
PublishingService.enqueue(PublishJob{project, version, platform, account, caption, cover, hashtags, publish_at})
        │
        ▼
JobQueue ──► PublishWorker ──► PublishingProvider (interface)
                                   ├─ InstagramProvider   (آینده)
                                   ├─ TelegramChannelProvider (آینده)
                                   └─ DryRunProvider      (فاز ۱: فقط لاگ — برای تست جریان)
```

**آنچه درباره‌ی API اینستاگرام تا امروز می‌دانیم (قبل از پیاده‌سازی باید دوباره از مستندات رسمی Meta تأیید شود):**
- فقط حساب **Business یا Creator** متصل به یک صفحه‌ی فیسبوک، با اپ Meta و مجوز `instagram_business_content_publish`.
- انتشار دو مرحله‌ای است: ساخت container با `media_type=REELS` و سپس `media_publish`.
- ویدئو باید MP4 (H.264)، 9:16 و ۵ تا ۹۰ ثانیه باشد تا در تب Reels نمایش داده شود.
- سقف روزانه‌ی انتشار از طریق API برای هر حساب وجود دارد (منابع ۵۰ و ۱۰۰ پست در ۲۴ ساعت گزارش کرده‌اند — متناقض) + سقف ۵۰ container منتشرنشده.
- Meta ویدئو را از یک **آدرس عمومی** می‌گیرد → `StorageProvider` باید بتواند URL عمومی/امضاشده‌ی موقت بدهد (سرور موقت فعلی نمی‌تواند). *(یا آپلود resumable — باید بررسی شود.)*

**نتیجه برای طراحی:** `PublishJob` باید وضعیت container را ذخیره کند (`container_id`) تا retry باعث انتشار دوباره نشود، و سقف روزانه در صف کنترل شود.

## 7. State Machine پیشنهادی

### وضعیت پروژه

```
IDEA ─► BRIEF_READY ─► SCRIPT_DRAFT ─► SCRIPT_APPROVED ─► PRODUCTION ─► RENDERING ─► QA ─► READY_FOR_REVIEW ─► APPROVED ─► PUBLISHING ─► PUBLISHED
                          ▲    │                                                           │         │
                          └────┘ revise (نسخه‌ی جدید)                                        │         └─► SCHEDULED ─► PUBLISHING
                                                                                          └─ revise ─► PRODUCTION (فقط صحنه‌های تغییرکرده)
هر وضعیت ─► FAILED ─► RETRYING ─► (همان مرحله)      ·   REJECTED   ·   CANCELLED
```

- گذارها در یک جدول صریح تعریف می‌شوند؛ هر گذار غیرمجاز خطا می‌دهد.
- هر گذار در `history` ثبت می‌شود: `{from, to, at, actor, reason}`.
- **دروازه‌های انسانی:** `SCRIPT_DRAFT → SCRIPT_APPROVED` و `READY_FOR_REVIEW → APPROVED`. هیچ agentی نمی‌تواند این دو را خودش انجام دهد (`actor` باید کاربر باشد).
- `FAILED` مرحله و علت را نگه می‌دارد؛ retry فقط همان مرحله را اجرا می‌کند.

### وضعیت‌های جدا (جدا از پروژه)
- **Job:** `QUEUED → RUNNING → SUCCEEDED | FAILED → RETRYING | CANCELLED`
- **Publish:** `PENDING → PROCESSING → PUBLISHED | FAILED → RETRYING | CANCELLED` (+ `SCHEDULED`)

## 8. Storage Strategy

| نوع داده | محل | در Git؟ |
|---|---|---|
| کد، template، preset، `brand.json`، schema | مخزن | ✅ |
| `manifest.json`، `storyboard.json`، `script.md`، `research.md/json`، `qa_report.*` | `projects/REEL-XXXX/` | ✅ (کوچک، مهم، قابل diff) |
| ویس خام، دارایی‌های تولیدشده، فریم‌ها، MASTER، DELIVERY | `StorageProvider` | ❌ |
| کش (hash → دارایی) | `LocalStorage/cache/` | ❌ |

- **LocalStorage** (فاز ۱): دیسک سرور. ⚠️ موقت → تا ObjectStorage نیاید، فقط خروجی نهایی‌ای که کاربر بخواهد حفظ شود.
- **ObjectStorage** (فاز ۷): S3-compatible (مثلاً Cloudflare R2 یا Backblaze B2) → آدرس امضاشده برای اینستاگرام و آرشیو دائمی.
- Manifest فقط **شناسه‌ی دارایی** (`asset_id`، `sha256`، `storage_uri`) را نگه می‌دارد، نه مسیر مطلق.
- **MASTER و DELIVERY:** MASTER = رندر آرشیوی (CRF پایین، 60fps)؛ DELIVERY = نسخه‌ی مشتق برای تلگرام/اینستاگرام. DELIVERY همیشه از MASTER ساخته می‌شود و هرگز MASTER را بازنویسی نمی‌کند.

## 9. Queue / Worker Strategy

- **فاز ۱:** صف مبتنی بر فایل/SQLite (بدون سرویس خارجی) + یک Worker در همان ماشین.
- **کنترل هم‌زمانی بر اساس نوع منبع:**
  - `heavy_ai` (SDXL، Whisper، سرِ سخنگو): **حداکثر ۱**
  - `render` (Chromium): حداکثر ۱ کار، که خودش تا ۴ بخش موازی اجرا می‌کند
  - `light` (QA، metadata، اعلان): حداکثر ۲
- قبل از شروع کار: بررسی RAM و دیسک آزاد؛ اگر کافی نیست، کار در صف می‌ماند (امروز دیسک ۵.۴GB آزاد است).
- هر Job **idempotent** است: کلید آن `project_id + version + stage + input_hash` است. اگر خروجی با همان کلید موجود باشد، دوباره اجرا نمی‌شود.
- Timeout و retry با backoff برای هر نوع کار؛ کار سنگین شکست‌خورده پروژه را خراب نمی‌کند (خروجی‌ها موقت نوشته و در پایان atomically جابه‌جا می‌شوند).
- فاز ۷ به بعد: همان interface صف روی Redis یا یک سرویس GPU ابری؛ کد stage تغییر نمی‌کند.

## 10. Security Model

- **Secrets فقط از متغیر محیطی / secret manager:** `TELEGRAM_BOT_TOKEN`، `META_APP_SECRET`، `IG_ACCESS_TOKEN`، `FAL_KEY`، `REPLICATE_API_TOKEN`، … — هرگز در Git، manifest، لاگ یا پیام.
- یک ماژول `config.secrets` که نبودن secret را با پیام روشن گزارش می‌دهد و مقدار آن را هرگز چاپ نمی‌کند.
- `.gitignore` برای `.env*`، کش، خروجی‌ها.
- **Authorization:** `AUTHORIZED_USERS` و `AUTHORIZED_CHAT_IDS` در config؛ Adapter تلگرام قبل از هر کار بررسی می‌کند. کاربر ناشناس هیچ پاسخی جز «دسترسی ندارید» نمی‌گیرد (بدون افشای وجود پروژه‌ها).
- **مدل دسترسی آینده‌نگر:** `User → Workspace → Project` با نقش (`owner`، `editor`، `reviewer`). Telegram ID فقط به یک `User` نگاشت می‌شود و جایگزین مدل Owner/Workspace نیست.
- فقط نقش `owner` می‌تواند منتشر کند یا تنظیمات را تغییر دهد.
- Audit log برای: approve، reject، publish، schedule، cancel، تغییر تنظیمات، رد دسترسی.

## 11. Approval Model

```
Idea → Script ──[HUMAN ✅]──► Production → Render → QA ──[HUMAN ✅]──► Publishing
```

- دو دروازه‌ی اجباری: **سناریو** و **ویدئوی نهایی**. انتشار بدون تأیید دوم ممکن نیست؛ «سیاست انتشار خودکار» فقط در صورتی اضافه می‌شود که صریحاً تعریف شود.
- تأیید به **نسخه‌ی مشخص** گره می‌خورد (`approve(REEL-0047, v03)`)؛ اگر بعد از تأیید نسخه‌ی جدیدی ساخته شود، تأیید قبلی به آن منتقل نمی‌شود.
- QA با وضعیت `FAIL` مانع رسیدن به `READY_FOR_REVIEW` می‌شود؛ `WARN` مجاز است ولی در پیش‌نمایش نشان داده می‌شود.
- پیش‌نمایش همیشه این‌ها را دارد: Project، Version، مدت، رزولوشن، FPS، نتیجه‌ی QA، **فهرست موارد نیازمند بازبینی انسانی** (کیفیت صدا، روانی حرکت، ریتم، نمایش درست سبحان).
- Revision: `revise(project, instruction, scope?)` → نسخه‌ی جدید؛ اگر scope مبهم است («نور این قسمت») سیستم سؤال می‌پرسد («منظورتان Scene 04 است؟»).

## 12. جلوگیری از رندرهای تکراری

1. **Hash محتوایی برای هر صحنه:** `scene_hash = hash(scene JSON + template version + asset hashes + brand version)`.
2. **رندر در سطح صحنه:** هر صحنه یک قطعه‌ی ویدئوی جدا (`scenes/<scene_hash>.mp4`)؛ نسخه‌ی جدید فقط صحنه‌هایی را رندر می‌کند که hash شان تغییر کرده، بعد با ffmpeg concat (بدون encode دوباره) + میکس صدا. (نیازمند پایه‌ریزی transition ها روی مرز صحنه‌ها — در Architecture V1 طراحی می‌شود.)
3. **Cache دارایی:** تصویر AI، نقشه‌ی عمق، رونوشت Whisper، ویس تمیزشده، موزیک → کلید = hash ورودی + provider + پارامترها.
4. **Job idempotent** (بخش 9).
5. تغییر فقط-صدا (مثلاً موزیک) → فقط میکس و mux دوباره، بدون رندر تصویر.
6. تغییر فقط-متن زیرنویس → فقط صحنه‌های دارای آن زیرنویس.

## 13. Versioning

```
projects/REEL-0047/
  manifest.json            ← وضعیت فعلی، current_version، history، approvals
  audit.jsonl
  versions/
    v01/  storyboard.json · script.md · render/ (MASTER, DELIVERY) · qa_report.json · changes.md
    v02/  … (parent: v01, change: "hook")
    v03/
  final → v03              ← اشاره‌گر، نه کپی
```

- هر نسخه **غیرقابل‌تغییر** است؛ تغییر = نسخه‌ی جدید با `parent` و توضیح تغییر.
- «برگرد به v02» = نسخه‌ی جدید `v04` با `parent=v02` (تاریخچه حفظ می‌شود؛ هیچ چیز پاک نمی‌شود).
- «از v02 استفاده کن و فقط موسیقی را عوض کن» = `v05` با `parent=v02`، فقط لایه‌ی صدا تغییر می‌کند → به لطف cache، صحنه‌ها دوباره رندر نمی‌شوند.
- دارایی‌های حجیم بین نسخه‌ها با hash مشترک‌اند، نه کپی.

---

## پیوست: نگاشت Intent → عملیات Core (برای Router آینده)

| نمونه‌ی پیام | Intent | عملیات |
|---|---|---|
| «یه ریلز درباره X بساز» | `CREATE_CONTENT` | `ProjectService.create(topic)` → سؤال‌های ضروری |
| «هوکش رو قوی‌تر کن» | `REVISE_SCRIPT` | `revise(scope="hook")` |
| «ویدئو رو دوباره بساز» | `REGENERATE` | `render(new_version)` |
| «آخرین پروژه رو نشون بده» | `GET_PROJECT` | `status(latest)` |
| «تأیید» | `APPROVE` | `approve(current_project, current_version)` — اگر زمینه مبهم است، سؤال |
| «فردا ساعت ۸ منتشرش کن» | `SCHEDULE_PUBLISH` | `enqueue(publish_at=…)` |
| «برگرد به v02» | `RESTORE_VERSION` | `branch_from(v02)` |

## منابع (بخش 6)
- [Instagram Reels API: Complete Developer Guide (2026) — Phyllo](https://www.getphyllo.com/post/a-complete-guide-to-the-instagram-reels-api)
- [Instagram Reels API Publishing Guide (2026) — Postproxy](https://postproxy.dev/blog/instagram-reels-api-publishing-guide/)
- [Post to Instagram via API: Guide (2026) — Postproxy](https://postproxy.dev/blog/post-to-instagram-via-api/)
- [Instagram API Rate Limits Explained (2026) — InstantDM](https://instantdm.com/blog/instagram-api-rate-limits-explained-2026-developer-guide)
- [Instagram Graph API in 2026 — Netrows](https://www.netrows.com/blog/instagram-graph-api-guide-2026)

> این‌ها منابع ثانویه هستند و درباره‌ی سقف روزانه با هم اختلاف دارند. قبل از پیاده‌سازی، مستندات رسمی Meta (developers.facebook.com) مرجع نهایی است.
