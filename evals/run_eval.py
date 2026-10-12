"""Score a parser against data/cases.json. Usage: python -m evals.run_eval [rules|llm] [dev|heldout|all]"""
import json, sys
from pathlib import Path
from locparse import parse
FIELDS = ["allowed", "timezones", "engagement", "visa", "india", "conflict"]
ROOT = Path(__file__).resolve().parent.parent

def score(engine="rules", split="all", cache=True):
    cases = [c for c in json.loads((ROOT / "data/cases.json").read_text()) if split == "all" or c["split"] == split]
    cpath = ROOT / f"evals/out_{engine}.json"
    prev = json.loads(cpath.read_text()) if (cache and engine == "llm" and cpath.exists()) else {}
    rows = []
    for c in cases:
        pred = prev.get(c["id"]) or parse([s["text"] for s in c["sources"]], engine)
        prev[c["id"]] = pred
        ok = {f: pred[f] == c["gold"][f] for f in FIELDS}
        rows.append({"id": c["id"], "split": c["split"], "ok": ok, "pred": {f: pred[f] for f in FIELDS}, "gold": c["gold"]})
    if engine == "llm": cpath.write_text(json.dumps(prev, indent=1))
    acc = {f: sum(r["ok"][f] for r in rows) for f in FIELDS}
    allok = sum(all(r["ok"].values()) for r in rows)
    return rows, acc, allok, len(rows)

if __name__ == "__main__":
    eng = sys.argv[1] if len(sys.argv) > 1 else "rules"; sp = sys.argv[2] if len(sys.argv) > 2 else "dev"
    rows, acc, allok, n = score(eng, sp)
    for r in rows:
        bad = [f for f, v in r["ok"].items() if not v]
        if bad: print(r["id"], {f: (r["pred"][f], r["gold"][f]) for f in bad})
    print(f"{eng} {sp} n={n}", {f: f"{v}/{n}" for f, v in acc.items()}, f"all-fields {allok}/{n}")
