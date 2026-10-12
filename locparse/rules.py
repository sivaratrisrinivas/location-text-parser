"""Rule-based location-text parser. No network, no keys."""
import re

COUNTRY = [
    ("WORLDWIDE", r"\bworld ?wide\b|\banywhere\b|around the world|\(global\)|remote \(global\)|100% remote, worldwide"),
    ("NON_US", r"\bnon[- ]US\b|outside (?:the )?US\b"),
    ("US", r"\bUS\b|\bUSA\b|United States|\bU\.S\.|North America|\bUS/"),
    ("CA", r"\bCanada\b|\bCan\)|/Can\b|North America"),
    ("UK", r"\bUK\b|United Kingdom"),
    ("EUROPE", r"\bEurope\b|\bEU\b|\bEuropean\b"),
    ("LATAM", r"\bLATAM\b|Latin America|South America"),
    ("BR", r"\bBrazil\b"), ("DE", r"\bGermany\b"), ("PL", r"\bPoland\b"), ("RO", r"\bRomania\b"),
    ("CO", r"\bColombia\b"), ("HR", r"\bCroatia\b"), ("HU", r"\bHungary\b"), ("PT", r"\bPortugal\b"),
    ("DK", r"\bDenmark\b"), ("SE", r"\bSweden\b"), ("AT", r"\bAustria\b"), ("IN", r"\bIndia\b"),
    ("APAC", r"\bAPAC\b"),
]
# A sentence must look like a statement about where someone may work from.
LOC_CUE = re.compile(r"remote|location|located|based in|must be (?:based|located|in)|anywhere|worldwide|around the world|hire|hiring (?:in|from)|work from|\bonsite\b|on-site", re.I)
# Sentences describing the team, customers or users, not the candidate.
TEAM = re.compile(r"spread across|distributed across|team of \d+|our customers|universities|engineers spread|alongside the|serving|riders|patients|countries\)|\d+ countries", re.I)
TZ_PHRASE = re.compile(r"(?:(?:US|EU|EMEA|European|Europe|CET|PST|EST|Pacific|Eastern|East Coast|West Coast|North American?)\s*(?:/|or|and|,|to|up to)?\s*)+(?:time ?zones?|hours|overlap)\b", re.I)
SALARY_US = re.compile(r"(?:salary|range|pay)[^.|]{0,30}US-based", re.I)

def _sentences(text):
    for line in text.split("\n"):
        for s in re.split(r"(?<=[.!?])\s+|\s\|\s", line):
            if s.strip():
                yield s.strip()

OFFICE = re.compile(r"\b[A-Z][a-z]+,\s+[A-Z][a-z]+\s*(?:/|\bor\b)\s*(?=remote)", re.I)

def _tokens(s):
    s2 = OFFICE.sub(" ", SALARY_US.sub(" ", TZ_PHRASE.sub(" ", s)))
    return {tok for tok, pat in COUNTRY if re.search(pat, s2, re.I if tok not in ("US", "UK", "EUROPE", "CA") else 0)}

def allowed(text):
    per = [_tokens(s) for s in _sentences(text) if LOC_CUE.search(s) and not TEAM.search(s)]
    out = set().union(*per) if per else set()
    if "WORLDWIDE" in out:
        # Keep a country list only when it sits in the same clause as "worldwide" (e.g. "Worldwide: US / Canada").
        out = set().union(*[t for t in per if "WORLDWIDE" in t])
    if "NON_US" in out:
        out.discard("US")
    return sorted(out)

def timezones(text):
    out = set()
    for s in _sentences(text):
        if not re.search(r"time ?zones?|hours|overlap|UTC|\bCET\b|\bPST\b|\bEST\b|Eastern|Pacific|West Coast|East Coast", s, re.I):
            continue
        for a, b in re.findall(r"UTC\s?([+-−]\s?\d+)\s*(?:to|-|–)\s*UTC\s?([+-−]\s?\d+)", s):
            f = lambda x: x.replace(" ", "").replace("−", "-")
            out.add(f"UTC{f(a)}..UTC{f(b)}")
        if re.search(r"(?:US )?Pacific(?: Time)?\s*(?:and|to)\s*(?:CET|Central European)", s, re.I):
            out.add("US_PACIFIC..CET"); continue
        if re.search(r"CET\s*±\s*\d", s): out.add("CET±" + re.search(r"CET\s*±\s*(\d)", s).group(1)); continue
        if re.search(r"US Eastern|East Coast|Eastern time|\bEST\b|\bET\b", s, re.I): out.add("US_EAST")
        if re.search(r"\bPST\b|Pacific|West Coast", s, re.I): out.add("US_PACIFIC")
        if re.search(r"\bUS\s*(?:/|or|and)?\s*(?:EU\s*)?time ?zones?|US time ?zones?|US\s*/\s*EU time", s, re.I): out.add("US")
        if re.search(r"\b(?:EU|European?)\b[^.]{0,12}time ?zones?|EU time|US\s*/\s*EU", s, re.I): out.add("EUROPE")
        if re.search(r"EMEA time", s, re.I): out.add("EMEA")
        if re.search(r"\bCET\b(?!\s*±)", s) and not out & {"US_PACIFIC..CET"}: out.add("CET")
    return sorted(out)

def engagement(text):
    out = set()
    if re.search(r"\bEOR\b|employer of record", text, re.I): out.add("EOR")
    if re.search(r"\bB2B (?:contract|from|rate)|with B2B|via B2B", text, re.I): out.add("B2B")
    if re.search(r"\bcontractor\b", text, re.I): out.add("CONTRACTOR")
    if re.search(r"\bfreelance\b", text, re.I): out.add("FREELANCE")
    return sorted(out)

def visa(text):
    if re.search(r"(?:not|n't|unable to|cannot|can't)\s+(?:able to\s+)?(?:offer\s+|provide\s+)?(?:visa\s+)?sponsor|no visa|without (?:visa )?sponsorship", text, re.I):
        return "no"
    if re.search(r"visa sponsorship (?:is )?(?:available|offered|provided)|we (?:can|will|do) sponsor|sponsor(?:ship)? (?:for )?visas", text, re.I):
        return "yes"
    return "unknown"

def parse_source(text):
    return {"allowed": allowed(text), "timezones": timezones(text), "engagement": engagement(text), "visa": visa(text)}
