import json, subprocess, numpy as np, soundfile as sf, textwrap
T = json.load(open("timeline.json")); D = json.load(open("durs.json")); L = json.load(open("lines.json"))
ev, total, src = T["events"], T["total"], T["video"]; GAP = 0.3
OUT = "/workspace/outreach/matcha-location-text-demo.mp4"
# keep-spans: drop the initial page load, and page-load dead air before navigation lines (1 and 3)
cuts = [(0, ev[0] - 0.4)] + [(ev[i - 1] + D[i - 1] + GAP, ev[i] - 0.15) for i in (1, 3) if ev[i] - 0.15 > ev[i - 1] + D[i - 1] + GAP]
keep, prev = [], 0
for a, b in cuts:
    if a > prev: keep.append((prev, a))
    prev = b
keep.append((prev, total))
def newt(t): return sum(max(0, min(t, b) - a) for a, b in keep)
starts = [round(newt(t), 3) for t in ev]; dur = round(newt(total), 3)
print("keep", keep, "\nstarts", starts, "\nduration", dur)
sr = 48000; buf = np.zeros(int((dur + 1) * sr), np.float32)
for i, s in enumerate(starts):
    a, _ = sf.read(f"l{i:02d}.wav.trim.wav", dtype="float32"); j = int(s * sr); buf[j:j + len(a)] += a
sf.write("voice.wav", buf[:int(dur * sr)], sr)
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); return f"{h}:{m:02d}:{x % 60:05.2f}"
ass = ["[Script Info]", "PlayResX: 1280", "PlayResY: 720", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV",
       "Style: C,DejaVu Sans,30,&H00FFFFFF,&H00000000,&H90000000,0,3,10,0,2,80,80,34", "", "[Events]", "Format: Layer, Start, End, Style, Text"]
for i, s in enumerate(starts):
    txt = "\\N".join(textwrap.wrap(L[i][1], 62))
    ass.append(f"Dialogue: 0,{ts(s)},{ts(s + D[i] + 0.2)},C,{txt}")
open("captions.ass", "w").write("\n".join(ass) + "\n")
fc = "".join(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{k}];" for k, (a, b) in enumerate(keep))
fc += "".join(f"[v{k}]" for k in range(len(keep))) + f"concat=n={len(keep)}:v=1:a=0,fps=30,subtitles=captions.ass[v];[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", "voice.wav", "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", str(dur), "-movflags", "+faststart", OUT], check=True)
json.dump({"starts": starts, "durs": D, "lines": [l[1] for l in L], "duration": dur}, open("script_timed.json", "w"), indent=1)
