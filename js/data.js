// ============================================================
// DATA.JS — کتاب‌های صوتی آکادمی سبحان صمدی
// ============================================================

const BOOKS = [
  {
    id: 1,
    title: "معامله‌گر منضبط",
    originalTitle: "The Disciplined Trader",
    author: "مارک داگلاس",
    translator: "تیم آکادمی سبحان صمدی",
    category: "psychology",
    duration: "۸ ساعت و ۳۰ دقیقه",
    durationSec: 30600,
    rating: 4.9,
    reviews: 342,
    cover: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&h=600&fit=crop&q=80",
    description: "این کتاب به شما یاد می‌دهد که چگونه ذهنیت یک معامله‌گر موفق را توسعه دهید. مارک داگلاس با سال‌ها تجربه در بازارهای مالی، رازهای روانشناختی معامله‌گری را آشکار می‌کند.",
    tags: ["روانشناسی", "معامله‌گری", "ذهنیت"],
    featured: true,
    chapters: [
      { title: "فصل ۱: پایه‌های ذهنیت معامله‌گر", duration: "۴۵:۲۰", src: "" },
      { title: "فصل ۲: ترس و طمع در بازار", duration: "۵۲:۱۰", src: "" },
      { title: "فصل ۳: انضباط معامله‌گری", duration: "۴۸:۳۵", src: "" },
      { title: "فصل ۴: مدیریت ریسک روانشناختی", duration: "۵۵:۴۰", src: "" }
    ]
  },
  {
    id: 2,
    title: "معامله در منطقه",
    originalTitle: "Trading in the Zone",
    author: "مارک داگلاس",
    translator: "تیم آکادمی سبحان صمدی",
    category: "psychology",
    duration: "۷ ساعت و ۱۵ دقیقه",
    durationSec: 26100,
    rating: 4.8,
    reviews: 289,
    cover: "https://images.unsplash.com/photo-1642790106117-e829e14a795f?w=400&h=600&fit=crop&q=80",
    description: "چطور می‌توان در یک محیط کاملاً احتمالی با اطمینان معامله کرد؟ این کتاب پاسخ این سؤال را با عمق و دقت می‌دهد.",
    tags: ["روانشناسی", "احتمال", "اعتماد به نفس"],
    featured: true,
    chapters: [
      { title: "فصل ۱: تغییر ذهنیت", duration: "۴۲:۰۰", src: "" },
      { title: "فصل ۲: درک احتمال‌ها", duration: "۵۰:۳۰", src: "" },
      { title: "فصل ۳: باورهای اصلی معامله‌گر", duration: "۵۸:۱۵", src: "" }
    ]
  },
  {
    id: 3,
    title: "پول هوشمند",
    originalTitle: "Smart Money",
    author: "مایکل لوئیس",
    translator: "تیم آکادمی سبحان صمدی",
    category: "finance",
    duration: "۶ ساعت و ۴۰ دقیقه",
    durationSec: 24000,
    rating: 4.7,
    reviews: 198,
    cover: "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=400&h=600&fit=crop&q=80",
    description: "رازهای سرمایه‌گذاران بزرگ و چگونگی تفکر آن‌ها درباره پول و بازارهای مالی. یک دیدگاه تازه درباره مدیریت سرمایه.",
    tags: ["سرمایه‌گذاری", "مالی", "استراتژی"],
    featured: true,
    chapters: [
      { title: "فصل ۱: اصول پول هوشمند", duration: "۳۸:۴۵", src: "" },
      { title: "فصل ۲: سرمایه‌گذاری ارزشی", duration: "۴۵:۲۰", src: "" }
    ]
  },
  {
    id: 4,
    title: "تحلیل تکنیکال بازارهای مالی",
    originalTitle: "Technical Analysis of Financial Markets",
    author: "جان مورفی",
    translator: "تیم آکادمی سبحان صمدی",
    category: "trading",
    duration: "۱۲ ساعت و ۲۰ دقیقه",
    durationSec: 44400,
    rating: 4.9,
    reviews: 456,
    cover: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&h=600&fit=crop&q=80&sat=-100",
    description: "جامع‌ترین منبع درباره تحلیل تکنیکال. از اصول پایه تا الگوهای پیشرفته — همه چیزی که برای تحلیل بازار نیاز دارید.",
    tags: ["تکنیکال", "نمودار", "الگو"],
    featured: true,
    chapters: [
      { title: "فصل ۱: فلسفه تحلیل تکنیکال", duration: "۵۵:۰۰", src: "" },
      { title: "فصل ۲: نظریه داو", duration: "۴۸:۳۰", src: "" },
      { title: "فصل ۳: ساخت نمودار", duration: "۶۲:۱۵", src: "" },
      { title: "فصل ۴: روندها", duration: "۵۳:۴۰", src: "" },
      { title: "فصل ۵: الگوهای بازگشتی", duration: "۷۰:۲۵", src: "" }
    ]
  },
  {
    id: 5,
    title: "ذهن پول‌ساز",
    originalTitle: "The Millionaire Mindset",
    author: "T. Harv Eker",
    translator: "تیم آکادمی سبحان صمدی",
    category: "success",
    duration: "۵ ساعت و ۵۰ دقیقه",
    durationSec: 21000,
    rating: 4.6,
    reviews: 175,
    cover: "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=400&h=600&fit=crop&q=80",
    description: "چه چیزی تفاوت ذهنیت افراد ثروتمند و افراد فقیر را می‌سازد؟ این کتاب ریشه‌های باورهای مالی شما را به چالش می‌کشد.",
    tags: ["ثروت", "ذهنیت", "موفقیت"],
    featured: false,
    chapters: [
      { title: "فصل ۱: فایل ذهنی پول", duration: "۴۰:۰۰", src: "" },
      { title: "فصل ۲: ۱۷ روش تفکر ثروتمندان", duration: "۶۵:۳۰", src: "" }
    ]
  },
  {
    id: 6,
    title: "کتاب مدیریت ریسک",
    originalTitle: "The Risk Book",
    author: "مایکل لوئیس",
    translator: "تیم آکادمی سبحان صمدی",
    category: "trading",
    duration: "۹ ساعت و ۱۰ دقیقه",
    durationSec: 33000,
    rating: 4.8,
    reviews: 234,
    cover: "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=400&h=600&fit=crop&q=80",
    description: "مدیریت ریسک پایه‌ای‌ترین مهارت هر معامله‌گر موفق است. این کتاب تمام جوانب مدیریت ریسک در معامله‌گری را پوشش می‌دهد.",
    tags: ["ریسک", "مدیریت سرمایه", "بقا"],
    featured: false,
    chapters: [
      { title: "فصل ۱: اصول مدیریت ریسک", duration: "۵۲:۰۰", src: "" },
      { title: "فصل ۲: محاسبه حجم معاملات", duration: "۴۷:۱۵", src: "" },
      { title: "فصل ۳: استاپ لاس و تارگت", duration: "۵۸:۳۰", src: "" }
    ]
  },
  {
    id: 7,
    title: "روانشناسی بازار",
    originalTitle: "Market Psychology",
    author: "ادوین لوفور",
    translator: "تیم آکادمی سبحان صمدی",
    category: "psychology",
    duration: "۷ ساعت و ۳۵ دقیقه",
    durationSec: 27300,
    rating: 4.7,
    reviews: 312,
    cover: "https://images.unsplash.com/photo-1516245834210-c4c142787335?w=400&h=600&fit=crop&q=80",
    description: "درک روانشناسی جمعی بازار و اینکه چگونه هیجانات عمومی قیمت‌ها را شکل می‌دهند — یکی از مهم‌ترین مهارت‌های معامله‌گری.",
    tags: ["روانشناسی", "رفتار بازار", "احساسات"],
    featured: false,
    chapters: [
      { title: "فصل ۱: چرخه هیجانات بازار", duration: "۵۰:۴۵", src: "" },
      { title: "فصل ۲: ترس و طمع جمعی", duration: "۵۵:۱۰", src: "" }
    ]
  },
  {
    id: 8,
    title: "راز ثروت",
    originalTitle: "The Richest Man in Babylon",
    author: "جرج ساموئل کلاسون",
    translator: "تیم آکادمی سبحان صمدی",
    category: "finance",
    duration: "۴ ساعت و ۲۰ دقیقه",
    durationSec: 15600,
    rating: 4.9,
    reviews: 521,
    cover: "https://images.unsplash.com/photo-1633158829585-23ba8f7c8caf?w=400&h=600&fit=crop&q=80",
    description: "داستان‌های بابل باستان که اصول جاودانه مالی را به شیوه‌ای جذاب و به‌یادماندنی آموزش می‌دهند.",
    tags: ["پول", "پس‌انداز", "سرمایه‌گذاری"],
    featured: false,
    chapters: [
      { title: "آدمی که کیسه‌هایش را پر کرد", duration: "۳۵:۰۰", src: "" },
      { title: "هفت علاج برای کیف خالی", duration:="۴۲:۳۰", src: "" }
    ]
  },
  {
    id: 9,
    title: "قدرت عادت",
    originalTitle: "The Power of Habit",
    author: "چارلز دوهیگ",
    translator: "تیم آکادمی سبحان صمدی",
    category: "success",
    duration: "۸ ساعت و ۵۵ دقیقه",
    durationSec: 32100,
    rating: 4.8,
    reviews: 401,
    cover: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=600&fit=crop&q=80",
    description: "چگونه عادت‌ها کار می‌کنند و چطور می‌توانیم آن‌ها را تغییر دهیم؟ کتابی که برای هر معامله‌گری که می‌خواهد عادات معامله‌گری خود را بهبود بخشد ضروری است.",
    tags: ["عادت", "تغییر", "موفقیت"],
    featured: false,
    chapters: [
      { title: "فصل ۱: حلقه عادت", duration: "۵۸:۰۰", src: "" },
      { title: "فصل ۲: مغز عادت‌ساز", duration: "۶۲:۱۵", src: "" }
    ]
  },
  {
    id: 10,
    title: "بیایید درباره پول صحبت کنیم",
    originalTitle: "Let's Talk About Money",
    author: "گرنت کاردون",
    translator: "تیم آکادمی سبحان صمدی",
    category: "finance",
    duration: "۶ ساعت و ۱۰ دقیقه",
    durationSec: 22200,
    rating: 4.5,
    reviews: 167,
    cover: "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=400&h=600&fit=crop&q=80",
    description: "صادقانه‌ترین کتاب درباره پول که تا به حال خوانده‌اید. گرنت کاردون تمام رازهای جمع‌آوری ثروت را با شما به اشتراک می‌گذارد.",
    tags: ["پول", "ثروت", "سرمایه‌گذاری"],
    featured: false,
    chapters: [
      { title: "فصل ۱: پول چیست؟", duration: "۳۸:۰۰", src: "" },
      { title: "فصل ۲: چرا فقیر می‌مانیم", duration: "۴۵:۲۰", src: "" }
    ]
  },
  {
    id: 11,
    title: "راهنمای کامل بازار فارکس",
    originalTitle: "Complete Forex Guide",
    author: "کتی لین",
    translator: "تیم آکادمی سبحان صمدی",
    category: "trading",
    duration: "۱۰ ساعت و ۴۵ دقیقه",
    durationSec: 38700,
    rating: 4.8,
    reviews: 378,
    cover: "https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=400&h=600&fit=crop&q=80",
    description: "همه چیز درباره بازار فارکس: از مفاهیم پایه تا استراتژی‌های پیشرفته. یک راهنمای جامع برای معامله‌گران فارکس.",
    tags: ["فارکس", "جفت ارز", "معامله‌گری"],
    featured: false,
    chapters: [
      { title: "فصل ۱: آشنایی با فارکس", duration: "۵۵:۳۰", src: "" },
      { title: "فصل ۲: جفت ارزها", duration: "۶۰:۰۰", src: "" },
      { title: "فصل ۳: تحلیل فاندامنتال", duration: "۶۸:۴۵", src: "" }
    ]
  },
  {
    id: 12,
    title: "رمزگشایی اندیکاتورها",
    originalTitle: "Cracking Indicators",
    author: "جان ایله",
    translator: "تیم آکادمی سبحان صمدی",
    category: "trading",
    duration: "۷ ساعت و ۵۵ دقیقه",
    durationSec: 28500,
    rating: 4.7,
    reviews: 256,
    cover: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&h=600&fit=crop&q=80&hue=200",
    description: "درک عمیق اندیکاتورهای تکنیکال و چگونگی استفاده صحیح از آن‌ها — بدون اشتباهاتی که اکثر معامله‌گران مرتکب می‌شوند.",
    tags: ["اندیکاتور", "تکنیکال", "سیگنال"],
    featured: false,
    chapters: [
      { title: "فصل ۱: اندیکاتورهای روندی", duration: "۴۵:۰۰", src: "" },
      { title: "فصل ۲: اسیلاتورها", duration: "۵۲:۳۰", src: "" }
    ]
  }
];

const CATEGORIES = {
  trading: { label: "معامله‌گری", icon: "fa-chart-line", color: "#1e3a5f", desc: "استراتژی‌ها و روش‌های معامله در بازارهای مالی" },
  psychology: { label: "روانشناسی", icon: "fa-brain", color: "#B8860B", desc: "ذهنیت، کنترل احساسات و روانشناسی معامله‌گری" },
  finance: { label: "مالی", icon: "fa-coins", color: "#1e3a5f", desc: "مدیریت سرمایه، سرمایه‌گذاری و برنامه‌ریزی مالی" },
  success: { label: "موفقیت", icon: "fa-trophy", color: "#B8860B", desc: "رشد شخصی، عادت‌های موفق و تفکر استراتژیک" }
};
