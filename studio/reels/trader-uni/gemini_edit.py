"""Edit/pose the approved character with Google Gemini image models (key injected by the environment proxy).
usage: python3 gemini_edit.py out.png "prompt" [input.png] [model]"""
import sys, json, base64, urllib.request
out, prompt = sys.argv[1], sys.argv[2]
src = sys.argv[3] if len(sys.argv) > 3 else "char_sobhan.png"
model = sys.argv[4] if len(sys.argv) > 4 else "gemini-2.5-flash-image"
body = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/png", "data": base64.b64encode(open(src, "rb").read()).decode()}}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"], "imageConfig": {"aspectRatio": "9:16"}}}
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                             data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
try: r = json.load(urllib.request.urlopen(req, timeout=180))
except urllib.error.HTTPError as e: print("HTTP", e.code, e.read().decode()[:400]); sys.exit(1)
for p in r["candidates"][0]["content"]["parts"]:
    if "inlineData" in p: open(out, "wb").write(base64.b64decode(p["inlineData"]["data"])); print("ok", out, model); break
    if "text" in p: print("text:", p["text"][:200])
