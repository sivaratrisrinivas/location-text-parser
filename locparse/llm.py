"""Optional LLM parser on Groq free tier. Same output schema as rules.parse_source."""
import json, os, time, urllib.request
VOCAB = "WORLDWIDE, NON_US, US, CA, UK, EUROPE, LATAM, APAC, or ISO-3166 alpha-2 codes (BR, DE, PL, IN, ...)"
PROMPT = f"""Extract where a candidate may work from, using only this job text. Return JSON only:
{{"allowed": [...], "timezones": [...], "engagement": [...], "visa": "yes|no|unknown"}}
allowed: tokens from {VOCAB}. Use WORLDWIDE for anywhere/worldwide/global. Map North America to US and CA, South America to LATAM, EU/European to EUROPE. Only include places the candidate may live in, not where the team, customers or offices are, and not countries named only as part of a time-zone phrase. Empty list if not stated.
timezones: tokens US, US_EAST, US_PACIFIC, EUROPE, CET, EMEA, ranges like "UTC-3..UTC+3", "US_PACIFIC..CET", or "CET±3". Empty if not stated.
engagement: subset of EOR, B2B, CONTRACTOR, FREELANCE, only if explicitly stated.
visa: "no" if the text says no sponsorship, "yes" if it offers sponsorship, else "unknown".
JOB TEXT:
"""
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

def parse_source(text):
    body = json.dumps({"model": MODEL, "temperature": 0, "response_format": {"type": "json_object"},
                       "messages": [{"role": "user", "content": PROMPT + text[:6000]}]}).encode()
    for attempt in range(5):
        req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=body, headers={
            "Authorization": "Bearer " + os.environ["GROQ_API_KEY"], "Content-Type": "application/json", "User-Agent": "locparse/0.1"})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=60))
            d = json.loads(r["choices"][0]["message"]["content"])
            return {"allowed": sorted(set(map(str.upper, d.get("allowed") or []))),
                    "timezones": sorted(set(d.get("timezones") or [])),
                    "engagement": sorted(set(map(str.upper, d.get("engagement") or []))),
                    "visa": d.get("visa") if d.get("visa") in ("yes", "no") else "unknown"}
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(10 * (attempt + 1)); continue
            raise
    raise RuntimeError("groq rate limited")
