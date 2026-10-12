"""Bundle the rules parser and web demo into one Vercel Python function: build/vercel/api/index.py."""
import json, re
from pathlib import Path
R = Path(__file__).resolve().parent.parent
out = R / "build/vercel/api"; out.mkdir(parents=True, exist_ok=True)
rules = (R / "locparse/rules.py").read_text()
merge = (R / "locparse/merge.py").read_text()
srv = (R / "web/server.py").read_text()
cases = json.loads((R / "data/cases.json").read_text())
keep = ("matcha-fse", "matcha-ai", "searchatlas", "prairielearn", "datamint", "checkly")
presets = {c["id"]: {"company": c["company"], "sources": c["sources"], "gold": c["gold"]} for c in cases if c["id"] in keep}
head = srv.split("class H(")[0]
body = "class H(" + srv.split("class H(")[1].split('if __name__')[0]
PATHFIX = """from urllib.parse import urlsplit, parse_qs
def _p(h):
    u = urlsplit(h.path)
    if u.path.startswith("/api/index"):
        return parse_qs(u.query).get("p", ["/"])[0]
    return u.path
"""
code = "\n".join([
    rules, merge.replace('"""Merge', '"""(merge) Merge'),
    "def parse(texts):\n    return merge([parse_source(t) for t in texts])\n",
    "import json, os\nfrom http.server import BaseHTTPRequestHandler",
    f"INDEX = {(R / 'web/index.html').read_text()!r}",
    f"PRESETS = {presets!r}", f"RESULTS = {json.loads((R / 'evals/results.json').read_text())!r}",
    PATHFIX + body.replace("class H(", "class handler(").replace("self.path", "_p(self)"), "H = handler\n"])
(out / "index.py").write_text(code)
(R / "build/vercel/vercel.json").write_text('{"rewrites": [{"source": "/(.*)", "destination": "/api/index?p=/$1"}]}\n')
print(len(code))
