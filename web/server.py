"""Tiny stdlib web demo. Rules engine only, so it needs no keys."""
import json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from locparse import parse
ROOT = Path(__file__).resolve().parent.parent
INDEX = (ROOT / "web/index.html").read_text()
CASES = json.loads((ROOT / "data/cases.json").read_text())
PRESETS = {c["id"]: {"company": c["company"], "sources": [{"name": s["name"], "url": s["url"], "text": s["text"]} for s in c["sources"]], "gold": c["gold"]}
           for c in CASES if c["id"] in ("matcha-fse", "matcha-ai", "searchatlas", "prairielearn", "datamint", "checkly")}
RESULTS = json.loads((ROOT / "evals/results.json").read_text())

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/", "/index.html"): return self._send(200, INDEX, "text/html; charset=utf-8")
        if self.path == "/health": return self._send(200, '{"ok":true}')
        if self.path == "/api/presets": return self._send(200, json.dumps(PRESETS))
        if self.path == "/api/results": return self._send(200, json.dumps(RESULTS))
        self._send(404, '{"error":"not found"}')
    def do_POST(self):
        if self.path != "/api/parse": return self._send(404, '{"error":"not found"}')
        n = min(int(self.headers.get("Content-Length", 0)), 200_000)
        try:
            texts = [t for t in json.loads(self.rfile.read(n)).get("texts", []) if t.strip()][:5]
        except Exception:
            return self._send(400, '{"error":"bad json"}')
        if not texts: return self._send(400, '{"error":"no text"}')
        self._send(200, json.dumps(parse(texts)))
    def log_message(self, *a): pass

if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8000))), H).serve_forever()
