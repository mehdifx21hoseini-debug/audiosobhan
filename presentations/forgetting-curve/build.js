// Builds the 4-slide deck "Forgetting Curve" with pptxgenjs.
// Animations + Morph are injected afterwards by animate.py.
// Run: NODE_PATH=/home/user/tools/pptx/node_modules node build.js
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const sharp = require("sharp");
const Fi = require("react-icons/fi");

const OUT = path.join(__dirname, "deck_raw.pptx");
const A = (f) => path.join(__dirname, "assets", f);

// ---- design system -------------------------------------------------------
const C = {
  ink: "0E1A2B", ink2: "16263D", white: "FFFFFF", mist: "F3F5F9",
  slate: "5B6B82", mute: "8FA3BF", soft: "C9D3E1", line: "2E4A6B",
  teal: "16B5A6", tealDk: "0E8C80", amber: "F2A93B", amberDk: "C77D12",
};
const F = "Arial"; // ships with Office, full Persian coverage
const fa = (s) => String(s).replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[d]);
// RTL text helper - fresh options object on every call
const T = (slide, text, o) =>
  slide.addText(text, {
    fontFace: F, rtlMode: true, lang: "fa-IR", align: "right", valign: "top",
    margin: 0, isTextBox: true, ...o,
  });
async function icon(Comp, color) {
  const svg = renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: 256, strokeWidth: 2 }));
  const png = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}
const orb = (slide, x, y, s, transparency) =>
  slide.addImage({ path: A("orb.png"), x, y, w: s, h: s, transparency, objectName: "!!orb", altText: "هاله‌ی نورانی تزئینی" });
const shadow = () => ({ type: "outer", color: "0E1A2B", opacity: 0.08, blur: 12, offset: 3, angle: 90 });

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  pres.title = "منحنی فراموشی و مرور فاصله‌دار";
  pres.rtlMode = true;
  const W = 13.333;

  // ======================= SLIDE 1 - HOOK (dark) ===========================
  {
    const s = pres.addSlide();
    s.background = { path: A("bg_dark_hook.png") };
    orb(s, -1.4, 1.2, 7.4, 55);

    // hero curve: Ebbinghaus savings, no axes - just the fall
    s.addChart(pres.charts.LINE, [{
      name: "حافظه", labels: ["0", "20m", "1h", "9h", "1d", "2d", "6d", "31d"],
      values: [100, 58.2, 44.2, 35.8, 33.7, 27.8, 25.4, 21.1],
    }], {
      objectName: "hook_curve", x: 0.55, y: 1.25, w: 5.9, h: 4.9,
      chartColors: [C.amber], lineSize: 4, lineSmooth: true, lineDataSymbol: "none",
      catAxisHidden: true, valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 105,
      valGridLine: { style: "none" }, catGridLine: { style: "none" },
      showLegend: false,
    });
    T(s, "امروز", { objectName: "hook_axis_start", x: 0.6, y: 6.2, w: 1.5, h: 0.35, fontSize: 12, color: C.mute, align: "left" });
    T(s, "یک ماه بعد", { objectName: "hook_axis_end", x: 4.6, y: 6.2, w: 1.8, h: 0.35, fontSize: 12, color: C.mute });

    T(s, "علوم یادگیری  |  درس اول", { objectName: "hook_kicker", x: 6.9, y: 0.95, w: 5.73, h: 0.4, fontSize: 14, bold: true, color: C.teal });
    T(s, fa("66٪"), { objectName: "hook_stat", x: 6.9, y: 1.3, w: 5.73, h: 1.9, fontSize: 120, bold: true, color: C.amber, valign: "middle" });
    T(s, "از آنچه امروز یاد می‌گیری، تا فردا از ذهنت پاک می‌شود.", {
      objectName: "hook_line", x: 6.9, y: 3.3, w: 5.73, h: 1.0, fontSize: 24, color: C.white, lineSpacingMultiple: 1.1 });
    T(s, "منحنی فراموشی", { objectName: "hook_title", x: 6.9, y: 4.75, w: 5.73, h: 0.8, fontSize: 40, bold: true, color: C.white });
    T(s, "و چطور شکستش بدهیم", { objectName: "hook_subtitle", x: 6.9, y: 5.55, w: 5.73, h: 0.5, fontSize: 20, color: C.mute });
    T(s, fa("بر پایه‌ی پژوهش هرمان ابینگهاوس، 1885"), { objectName: "hook_source", x: 6.9, y: 6.6, w: 5.73, h: 0.35, fontSize: 11, color: "6F819B" });
    s.addNotes("قلاب: عدد ۶۶٪ را بگو و مکث کن. بعد اشاره کن که این منحنی در ۱۸۸۵ کشف شد و هنوز هم معتبر است.");
  }

  // ======================= SLIDE 2 - CORE CONCEPT (light) ==================
  {
    const s = pres.addSlide();
    s.background = { color: C.white };
    orb(s, -1.3, -1.4, 3.6, 70);
    T(s, "ذهن چطور فراموش می‌کند؟", { objectName: "c_title", x: 4.6, y: 0.6, w: 8.13, h: 0.8, fontSize: 38, bold: true, color: C.ink });
    T(s, fa("درصد مطلبِ باقی‌مانده در حافظه طی 31 روز — آزمایش کلاسیک ابینگهاوس"), {
      objectName: "c_sub", x: 4.6, y: 1.38, w: 8.13, h: 0.45, fontSize: 15, color: C.slate });

    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { objectName: "c_chart_card", x: 0.6, y: 2.05, w: 8.0, h: 4.85, fill: { color: C.mist }, rectRadius: 0.18 });
    s.addChart(pres.charts.LINE, [{
      name: "حافظه",
      labels: ["شروع", "۲۰ دقیقه", "۱ ساعت", "۹ ساعت", "۱ روز", "۲ روز", "۶ روز", "۳۱ روز"],
      values: [100, 58.2, 44.2, 35.8, 33.7, 27.8, 25.4, 21.1],
    }], {
      objectName: "c_chart", x: 0.8, y: 2.25, w: 7.6, h: 4.45,
      chartColors: [C.amber], lineSize: 3, lineSmooth: true,
      lineDataSymbol: "circle", lineDataSymbolSize: 9, lineDataSymbolLineColor: C.white, lineDataSymbolLineSize: 2,
      showValue: true, dataLabelPosition: "t", dataLabelFormatCode: '0"%"', dataLabelFontSize: 11,
      dataLabelColor: C.amberDk, dataLabelFontBold: true, dataLabelFontFace: F,
      catAxisLabelColor: C.slate, catAxisLabelFontSize: 11, catAxisLabelFontFace: F,
      catAxisLineShow: false, valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 115,
      valGridLine: { color: "E3E8EF", size: 0.75 }, catGridLine: { style: "none" },
      showLegend: false,
    });

    const cards = [
      { t: "سقوط در ساعت اول", b: "بیش از نیمی از مطلب فقط در ۶۰ دقیقه از دست می‌رود.", i: Fi.FiTrendingDown, c: C.amber },
      { t: "کُند شدن فراموشی", b: "بعد از روز اول، شیب منحنی به‌شدت ملایم می‌شود.", i: Fi.FiClock, c: C.slate },
      { t: "ردپای ماندگار", b: "حدود یک‌پنجم مطلب حتی پس از یک ماه باقی می‌ماند.", i: Fi.FiAnchor, c: C.teal },
    ];
    for (let k = 0; k < 3; k++) {
      const d = cards[k], y = 2.05 + k * 1.7, n = `c_card${k + 1}`;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { objectName: n + "_bg", x: 8.95, y, w: 3.78, h: 1.45, fill: { color: C.white }, line: { color: "E3E8EF", width: 1 }, rectRadius: 0.14, shadow: shadow() });
      s.addShape(pres.shapes.OVAL, { objectName: n + "_dot", x: 11.93, y: y + 0.25, w: 0.56, h: 0.56, fill: { color: d.c, transparency: 85 } });
      s.addImage({ data: await icon(d.i, d.c), objectName: n + "_icon", altText: "آیکون", x: 12.06, y: y + 0.38, w: 0.3, h: 0.3 });
      T(s, d.t, { objectName: n + "_title", x: 9.15, y: y + 0.24, w: 2.62, h: 0.42, fontSize: 17, bold: true, color: C.ink, valign: "middle" });
      T(s, d.b, { objectName: n + "_body", x: 9.15, y: y + 0.86, w: 3.3, h: 0.5, fontSize: 12.5, color: C.slate, lineSpacingMultiple: 1.05 });
    }
    s.addNotes("سه ویژگی منحنی را به ترتیب کارت‌ها توضیح بده. تأکید: فراموشی تصادفی نیست، الگو دارد.");
  }

  // ======================= SLIDE 3 - PRACTICAL EXAMPLE (light) =============
  let finalWith = 0, finalWithout = 0;
  {
    const s = pres.addSlide();
    s.background = { color: C.white };
    orb(s, 9.6, 3.6, 4.6, 72);
    T(s, fa("مثال: 100 لغت جدید، 30 روز بعد"), { objectName: "e_title", x: 4.6, y: 0.6, w: 8.13, h: 0.8, fontSize: 36, bold: true, color: C.ink });
    T(s, "همان مطالعه، همان آدم — فقط یک تفاوت: زمان‌بندی مرور", { objectName: "e_sub", x: 4.6, y: 1.38, w: 8.13, h: 0.45, fontSize: 15, color: C.slate });

    // illustrative model: R = F + (100-F)·e^(-(t-t0)/S), stronger after each review
    const reviews = [0, 1, 3, 7, 21], Fl = [20, 45, 60, 70, 80], St = [0.6, 1.3, 2.6, 5, 11];
    const no = (t) => 20 + 80 * Math.exp(-t / 0.6);
    const yes = (t, k) => Fl[k] + (100 - Fl[k]) * Math.exp(-(t - reviews[k]) / St[k]);
    const xs = [], y1 = [], y2 = [];
    for (let k = 0; k < reviews.length; k++) {
      const a = reviews[k], b = k + 1 < reviews.length ? reviews[k + 1] : 30;
      for (let t = a; t <= b + 1e-9; t += 0.2) { xs.push(+t.toFixed(2)); y1.push(+no(t).toFixed(1)); y2.push(+yes(t, k).toFixed(1)); }
    }
    finalWith = Math.round(y2[y2.length - 1]); finalWithout = Math.round(y1[y1.length - 1]);

    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { objectName: "e_chart_card", x: 0.6, y: 2.05, w: 8.4, h: 4.65, fill: { color: C.mist }, rectRadius: 0.18 });
    // manual legend (RTL)
    s.addShape(pres.shapes.OVAL, { objectName: "e_leg_teal", x: 8.55, y: 2.34, w: 0.16, h: 0.16, fill: { color: C.teal } });
    T(s, fa("با مرور در روزهای 1، 3، 7 و 21"), { objectName: "e_leg_teal_t", x: 4.9, y: 2.25, w: 3.5, h: 0.34, fontSize: 12, color: C.ink, valign: "middle" });
    s.addShape(pres.shapes.OVAL, { objectName: "e_leg_amber", x: 4.55, y: 2.34, w: 0.16, h: 0.16, fill: { color: C.amber } });
    T(s, "بدون مرور", { objectName: "e_leg_amber_t", x: 2.8, y: 2.25, w: 1.6, h: 0.34, fontSize: 12, color: C.ink, valign: "middle" });

    s.addChart(pres.charts.SCATTER, [
      { name: "روز", values: xs },
      { name: "بدون مرور", values: y1 },
      { name: "با مرور", values: y2 },
    ], {
      objectName: "e_chart", x: 0.75, y: 2.65, w: 8.1, h: 3.95,
      chartColors: [C.amber, C.teal], lineSize: 3, lineDataSymbol: "none",
      valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 25,
      valAxisLabelColor: C.slate, valAxisLabelFontSize: 10, valAxisLineShow: false,
      catAxisMinVal: 0, catAxisMaxVal: 30, catAxisMajorUnit: 5,
      catAxisLabelColor: C.slate, catAxisLabelFontSize: 10, catAxisLineShow: false,
      valGridLine: { color: "E0E5EC", size: 0.75 }, catGridLine: { style: "none" },
      showLegend: false,
    });
    T(s, "روز", { objectName: "e_axis_x", x: 0.7, y: 6.32, w: 0.4, h: 0.28, fontSize: 10, color: C.slate, align: "left" });
    T(s, "٪ به‌یادمانده", { objectName: "e_axis_y", x: 0.8, y: 2.25, w: 1.8, h: 0.34, fontSize: 10, color: C.slate, align: "left", valign: "middle" });
    T(s, "مدل نمایشی بر پایه‌ی منحنی ابینگهاوس؛ اعداد تقریبی‌اند.", { objectName: "e_note", x: 0.6, y: 6.85, w: 8.4, h: 0.3, fontSize: 10, color: C.mute });

    const box = [
      { n: "e_before", y: 2.05, k: "قبل: بدون مرور", v: finalWithout, c: C.amber, i: Fi.FiTrendingDown },
      { n: "e_after", y: 4.45, k: "بعد: ۴ مرورِ کوتاه", v: finalWith, c: C.teal, i: Fi.FiTrendingUp },
    ];
    for (const b of box) {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { objectName: b.n + "_bg", x: 9.35, y: b.y, w: 3.38, h: 2.25, fill: { color: C.white }, line: { color: "E3E8EF", width: 1 }, rectRadius: 0.14, shadow: shadow() });
      s.addShape(pres.shapes.OVAL, { objectName: b.n + "_dot", x: 11.95, y: b.y + 0.25, w: 0.5, h: 0.5, fill: { color: b.c, transparency: 85 } });
      s.addImage({ data: await icon(b.i, b.c), objectName: b.n + "_icon", altText: "آیکون", x: 12.07, y: b.y + 0.37, w: 0.26, h: 0.26 });
      T(s, b.k, { objectName: b.n + "_label", x: 9.55, y: b.y + 0.27, w: 2.3, h: 0.45, fontSize: 13, bold: true, color: b.c === C.teal ? C.tealDk : C.amberDk, valign: "middle" });
      T(s, fa(b.v), { objectName: b.n + "_value", x: 9.55, y: b.y + 0.72, w: 2.95, h: 0.95, fontSize: 54, bold: true, color: b.c, valign: "middle" });
      T(s, "لغت در ذهن، بعد از ۳۰ روز", { objectName: b.n + "_caption", x: 9.55, y: b.y + 1.7, w: 2.95, h: 0.35, fontSize: 12, color: C.slate });
    }
    s.addNotes(`بدون مرور حدود ${finalWithout} لغت می‌ماند؛ با چهار مرور کوتاه حدود ${finalWith} لغت. نکته: هر مرور شیب فراموشی بعدی را کم می‌کند.`);
  }

  // ======================= SLIDE 4 - KEY TAKEAWAY (dark) ===================
  {
    const s = pres.addSlide();
    s.background = { path: A("bg_dark_takeaway.png") };
    orb(s, 3.9, -0.3, 5.5, 50);
    T(s, "نکته‌ی کلیدی", { objectName: "k_kicker", x: 1, y: 0.7, w: W - 2, h: 0.4, fontSize: 14, bold: true, color: C.teal, align: "center" });
    T(s, fa("قانون 1 – 3 – 7 – 21"), { objectName: "k_title", x: 1, y: 1.08, w: W - 2, h: 0.95, fontSize: 46, bold: true, color: C.white, align: "center", valign: "middle" });

    const days = [["1", "فردا"], ["3", "سه روز بعد"], ["7", "یک هفته بعد"], ["21", "سه هفته بعد"]];
    const d = 1.3, gap = 2.3, x0 = (W - (3 * gap + d)) / 2, cy = 2.4;
    for (let k = 0; k < 4; k++) {
      const x = x0 + (3 - k) * gap; // RTL: day 1 on the right
      if (k < 3) s.addShape(pres.shapes.LINE, { objectName: `k_link${k + 1}`, x: x - gap + d + 0.12, y: cy + d / 2, w: gap - d - 0.24, h: 0, line: { color: C.line, width: 2, dashType: "dash" } });
      s.addShape(pres.shapes.OVAL, { objectName: `k_day${k + 1}`, x, y: cy, w: d, h: d, fill: { color: C.ink2 }, line: { color: C.teal, width: 2 + k * 0.75 } });
      T(s, fa(days[k][0]), { objectName: `k_day${k + 1}_n`, x, y: cy + 0.18, w: d, h: 0.7, fontSize: 32, bold: true, color: C.white, align: "center", valign: "middle" });
      T(s, "روز", { objectName: `k_day${k + 1}_u`, x, y: cy + 0.82, w: d, h: 0.3, fontSize: 11, color: C.mute, align: "center" });
      T(s, days[k][1], { objectName: `k_day${k + 1}_l`, x: x - 0.4, y: cy + d + 0.12, w: d + 0.8, h: 0.35, fontSize: 13, color: C.soft, align: "center" });
    }
    T(s, "یادگیری یک رویداد نیست؛ یک برنامه است.", { objectName: "k_quote", x: 1, y: 4.35, w: W - 2, h: 0.75, fontSize: 30, bold: true, color: C.white, align: "center", valign: "middle" });

    const tk = [
      { t: "کوتاه و زود", b: "اولین مرور را در ۲۴ ساعت اول انجام بده.", i: Fi.FiClock },
      { t: "فاصله‌ها را بلندتر کن", b: "هر مرور، فاصله‌ی بعدی را بیشتر می‌کند.", i: Fi.FiMaximize2 },
      { t: "یادآوری فعال", b: "به‌جای بازخوانی، از حافظه بنویس.", i: Fi.FiZap },
    ];
    const cw = 3.7, cg = 0.35, cx0 = (W - (3 * cw + 2 * cg)) / 2;
    for (let k = 0; k < 3; k++) {
      const x = cx0 + (2 - k) * (cw + cg), y = 5.45, n = `k_tip${k + 1}`;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { objectName: n + "_bg", x, y, w: cw, h: 1.25, fill: { color: C.ink2 }, line: { color: "22364F", width: 1 }, rectRadius: 0.14 });
      s.addShape(pres.shapes.OVAL, { objectName: n + "_dot", x: x + cw - 0.8, y: y + 0.33, w: 0.56, h: 0.56, fill: { color: C.teal, transparency: 80 } });
      s.addImage({ data: await icon(tk[k].i, C.teal), objectName: n + "_icon", altText: "آیکون", x: x + cw - 0.67, y: y + 0.46, w: 0.3, h: 0.3 });
      T(s, tk[k].t, { objectName: n + "_title", x: x + 0.2, y: y + 0.2, w: cw - 1.15, h: 0.42, fontSize: 16, bold: true, color: C.white, valign: "middle" });
      T(s, tk[k].b, { objectName: n + "_body", x: x + 0.2, y: y + 0.64, w: cw - 1.15, h: 0.45, fontSize: 12, color: "9FB0C8" });
    }
    s.addNotes("جمع‌بندی: چهار مرور کوتاه در روزهای ۱، ۳، ۷ و ۲۱. جمله‌ی پایانی را آرام و با مکث بگو.");
  }

  await pres.writeFile({ fileName: OUT });
  console.log("wrote", OUT, "final with/without:", finalWith, finalWithout);
})();
