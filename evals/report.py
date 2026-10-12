"""Write evals/results.md and results.json: per-field accuracy by engine and split, plus code-check pass rates."""
import json
from pathlib import Path
from evals.run_eval import score, FIELDS
from evals.checks import CHECKS
from locparse import parse
ROOT = Path(__file__).resolve().parent.parent
res = {}; lines = ["# Results", "", "Exact match per field. dev = cases the rules were tuned on. heldout = never looked at while writing rules.", ""]
lines += ["| engine | split | n | " + " | ".join(FIELDS) + " | all fields |", "|---" * (len(FIELDS) + 4) + "|"]
for eng in ["rules", "llm"]:
    for sp in ["dev", "heldout", "all"]:
        rows, acc, allok, n = score(eng, sp)
        res[f"{eng}/{sp}"] = {"n": n, **acc, "all_fields": allok}
        lines.append(f"| {eng} | {sp} | {n} | " + " | ".join(f"{acc[f]}/{n}" for f in FIELDS) + f" | {allok}/{n} |")
        if sp == "all":
            lines += [""] if False else []
cases = json.loads((ROOT / "data/cases.json").read_text())
llm = json.loads((ROOT / "evals/out_llm.json").read_text())
lines += ["", "## Code checks (pass / total outputs)", "", "| check | rules | llm |", "|---|---|---|"]
for ch in CHECKS:
    r = [ch(parse([s["text"] for s in c["sources"]]))[0] for c in cases]
    l = [ch(llm[c["id"]])[0] for c in cases]
    lines.append(f"| {ch.__name__} | {sum(r)}/{len(r)} | {sum(l)}/{len(l)} |")
    res[f"check/{ch.__name__}"] = {"rules": sum(r), "llm": sum(l), "n": len(r)}
lines += ["", "## Errors", ""]
for eng in ["rules", "llm"]:
    rows, *_ = score(eng, "all")
    for r in rows:
        bad = [f for f, v in r["ok"].items() if not v]
        if bad: lines.append(f"- {eng} / {r['split']} / {r['id']}: " + "; ".join(f"{f} got {r['pred'][f]} want {r['gold'][f]}" for f in bad))
(ROOT / "evals/results.md").write_text("\n".join(lines) + "\n")
(ROOT / "evals/results.json").write_text(json.dumps(res, indent=1))
print("\n".join(lines))
