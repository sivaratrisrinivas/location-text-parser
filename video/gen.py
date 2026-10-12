import json, subprocess, soundfile as sf
L = json.load(open("mloc/lines.json")); say = {"EOR": "E O R", "32": "thirty two", "11 of 16": "eleven of sixteen", "all 16": "all sixteen", "9 of 16": "nine of sixteen", "October 12": "October twelfth"}
durs = []
for i, (_, t) in enumerate(L):
    s = t
    for a, b in say.items(): s = s.replace(a, b)
    f = f"mloc/l{i:02d}.wav"
    subprocess.run(["venv/bin/python", "tts.py", "af_heart", "0.95", f, s], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse", "-ar", "48000", "-ac", "1", f + ".trim.wav"], check=True)
    a, sr = sf.read(f + ".trim.wav"); durs.append(round(len(a) / sr, 2))
json.dump(durs, open("mloc/durs.json", "w")); print(durs, sum(durs))
