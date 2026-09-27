// Studio renderer (GSAP scene -> headless Chrome -> ffmpeg).
// usage: node render_par.js <html> <fps> <out.mp4> [stills=t1,t2] | node render_par.js <html> <fps> <out> --part k/N
const { chromium } = require("playwright-core"); const { spawn } = require("child_process"); const path = require("path"); const fs = require("fs");
(async () => {
  const [html, fpsS, out, mode] = process.argv.slice(2); const FPS = +fpsS; const TL = JSON.parse(fs.readFileSync(path.join(path.dirname(path.resolve(html)), "tl.json"), "utf8"));
  const b = await chromium.launch({ executablePath: process.env.CHROME || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--allow-file-access-from-files", "--disable-web-security", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.addInitScript(t => { window.TL = t; }, TL);
  await p.goto("file://" + path.resolve(html)); await p.waitForFunction(() => window.ready === true); await p.evaluate(() => document.fonts.ready);
  const T = await p.evaluate(() => window.DUR); const N = Math.round(T * FPS);
  if (mode && mode.startsWith("stills=")) { for (const t of mode.slice(7).split(",")) { await p.evaluate(x => window.seek(x), +t); await p.screenshot({ path: "st_" + t + ".jpg", type: "jpeg", quality: 88 }); } await b.close(); return; }
  let a = 0, z = N; if (mode === "--part") { const [k, n] = process.argv[6].split("/").map(Number); a = Math.floor(N * k / n); z = Math.floor(N * (k + 1) / n); }
  const ff = spawn(process.env.FFMPEG || "ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out]);
  for (let i = a; i < z; i++) { await p.evaluate(x => window.seek(x), i / FPS); const buf = await p.screenshot({ type: "jpeg", quality: 94 }); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r)); }
  ff.stdin.end(); await new Promise(r => ff.on("close", r)); await b.close(); console.log("part done", a, z);
})();
