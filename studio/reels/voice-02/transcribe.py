"""Word-level Persian transcript (faster-whisper medium). -> words.json + transcript.txt"""
import json
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=4)
segs, _ = m.transcribe("raw48.wav", language="fa", beam_size=5, word_timestamps=True, vad_filter=True,
                       initial_prompt="سبحان صمدی، معامله‌گری، روانشناسی، ترس، طمع، دیسیپلین، استاپ‌لاس، ضرر، سود")
words, lines = [], []
for s in segs:
    lines.append(f"{s.start:6.2f}-{s.end:6.2f} | {s.text.strip()}")
    words += [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for w in s.words]
json.dump(words, open("words.json", "w"), ensure_ascii=False, indent=0); open("transcript.txt", "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
