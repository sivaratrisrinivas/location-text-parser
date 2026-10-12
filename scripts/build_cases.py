"""Build data/cases.json from saved public sources in sources/. Gold labels are hand-written below."""
import json, re, html, random
from pathlib import Path
S = Path(__file__).resolve().parent.parent / "sources"
def page(f, start=None, n=2500):
    t = (S / f).read_text(errors="ignore")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()
    i = t.find(start) if start else 0
    return t[max(i, 0):max(i, 0) + n]
hn = {str(c["id"]): c["text"] for c in json.loads((S / "hn_oct2026_selected.json").read_text())}
d = json.loads((S / "hn_50056667.json").read_text())
fico = html.unescape(re.sub(r"<[^>]+>", "", d["text"].replace("<p>", "\n")))
HNURL = "https://news.ycombinator.com/item?id="
def H(i): return {"name": f"HN Who is hiring Oct 2026, item {i}", "url": HNURL + str(i), "text": hn[str(i)]}
U = "unknown"
def C(cid, company, sources, allowed, tz=(), eng=(), visa=U, india=None, conflict=False):
    a = sorted(set(allowed))
    if india is None:
        india = "yes" if {"WORLDWIDE", "NON_US", "IN"} & set(a) else ("no" if a else U)
    return {"id": cid, "company": company, "sources": sources,
            "gold": {"allowed": a, "timezones": sorted(set(tz)), "engagement": sorted(set(eng)),
                     "visa": visa, "india": india, "conflict": conflict}}
fse = {"name": "Matcha job page /apply/fse", "url": "https://matcha.fm/apply/fse", "text": page("matcha_fse.html", "Founding Full-stack", 3000)}
ai = {"name": "Matcha job page /apply/ai", "url": "https://matcha.fm/apply/ai", "text": page("matcha_ai.html", "Founding AI Engineer", 3000)}
fico_src = {"name": "Founder HN post (fiiico, 2026-10-12)", "url": HNURL + "50056667", "text": fico}
cases = [
 C("matcha-fse", "Matcha (Founding SWE)", [fse, fico_src], ["US","CA","EUROPE","UK","BR","LATAM","WORLDWIDE"], ["US","EUROPE"], ["B2B","EOR"], india="conflict", conflict=True),
 C("matcha-ai", "Matcha (Founding AI Eng)", [ai, fico_src], ["US","CA","EUROPE","UK","BR","LATAM","WORLDWIDE"], ["US","EUROPE"], [], india="conflict", conflict=True),
 C("searchatlas", "Search Atlas", [H(49931746), {"name": "Search Atlas careers page", "url": "https://careers.searchatlas.com/jobs/599248-product-engineer-pm", "text": page("searchatlas_599248.html", "Department Product", 400)}],
   ["WORLDWIDE","BR","CA","CO","HR","HU","PT"], ["US_EAST"], ["CONTRACTOR"], india="conflict", conflict=True),
 C("tether", "Tether", [H(49924581), {"name": "Tether careers page", "url": "https://careers.tether.io/o/ai-harness-engineer-100-remote-worldwide", "text": page("tether_ai_harness.html", "AI Harness Engineer (100% Remote, Worldwide) Remote", 1500)}], ["WORLDWIDE"]),
 C("flexibits", "Flexibits", [H(49922803), {"name": "Matcha company page", "url": "https://matcha.fm/company/flexibits", "text": page("matcha_company_flexibits.html", "Flexibits careers", 1800)}], ["WORLDWIDE"], ["US_PACIFIC..CET"]),
 C("sourcegraph", "Sourcegraph", [H(49927984), {"name": "Matcha company page", "url": "https://matcha.fm/company/sourcegraph", "text": page("matcha_company_sourcegraph.html", "Where does Sourcegraph", 800)}], ["WORLDWIDE","US","EUROPE","CA"], ["US_EAST","US_PACIFIC"], ["EOR"]),
 C("prairielearn", "PrairieLearn", [H(49922584)], ["US"], visa="no"),
 C("sidekick", "Sidekick Labs", [H(49922609)], [], ["US"]),
 C("pagnos", "PAGNOS", [H(49922616)], ["DE"], visa="no"),
 C("checkly", "Checkly", [H(49922769)], ["EUROPE","US"], ["UTC-3..UTC+3","UTC+1..UTC+2","US_EAST"]),
 C("mainmatter", "Mainmatter", [H(49922899)], ["EUROPE"]),
 C("opensanctions", "OpenSanctions", [H(49922910)], [], ["CET±3"], ["FREELANCE"]),
 C("river", "River", [H(49923010)], ["US","EUROPE","LATAM"]),
 C("spade", "Spade", [H(49923320)], ["US","CA"]),
 C("brilliant", "Brilliant.org", [H(49923870)], ["US","CA"]),
 C("relevant", "Relevant Healthcare", [H(49923964)], ["US","CA"]),
 C("solace", "Solace Health", [H(49924327)], ["US"], visa="no"),
 C("curai", "Curai", [H(49924974)], ["US"]),
 C("discord", "Discord", [H(49925063)], ["US"], ["US_PACIFIC"]),
 C("enveritas", "Enveritas", [H(49925489)], ["WORLDWIDE"]),
 C("studyturtle", "StudyTurtle", [H(49927291)], ["NON_US"], ["US_PACIFIC"]),
 C("rinse", "RINSE", [H(49927692)], ["US","CA"]),
 C("allgravy", "All Gravy", [H(49928066)], [], ["EUROPE"]),
 C("qualcomm", "Qualcomm (QEMU team)", [H(49928358)], ["CA"]),
 C("datamint", "Datamint", [H(49928677)], ["WORLDWIDE"]),
 C("seeq", "Seeq", [H(49929522)], [], ["US_PACIFIC"]),
 C("vistulo", "Vistulo", [H(49930656)], ["PL","RO"], [], ["B2B"]),
 C("modash", "Modash.io", [H(49930681)], ["EUROPE"]),
 C("hospitable", "Hospitable", [H(49930868)], ["EUROPE","US"], ["EUROPE","US_EAST","US","EMEA"]),
 C("eventfirst", "eventfirst", [H(49930919)], [], ["CET"]),
 C("plantingspace", "PlantingSpace", [H(49931033)], [], ["EUROPE"]),
 C("lokker", "Lokker", [H(49931740)], ["US","CA","EUROPE"], ["UTC-8..UTC+2"]),
]
# Split: case 1 (Matcha FSE) is dev by design; the rest are shuffled with a fixed seed, before any rules were written.
rest = cases[1:]; random.Random(13).shuffle(rest)
half = len(cases) // 2
for i, c in enumerate([cases[0]] + rest):
    c["split"] = "dev" if i < half else "heldout"
out = Path(__file__).resolve().parent.parent / "data" / "cases.json"
out.write_text(json.dumps(cases, indent=1, ensure_ascii=False))
print(len(cases), "cases;", sum(c["split"] == "dev" for c in cases), "dev")
for c in cases: print(c["split"], c["id"])
