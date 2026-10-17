"""The fake world: a pretend payment service and a pretend calendar.

Runs as a tiny web server. The assistant presses its buttons by POSTing here.
Every press is written to ledger.jsonl so the checker can see what was DONE,
not just what was said. In the box, this runs inside each clone; nothing real.

Run:  python world/services.py [port]
"""
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

LEDGER = "ledger.jsonl"

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        kind = self.path.strip("/")                       # "book" or "payment_link"
        entry = {"type": kind, "guest": self.headers.get("X-Guest", "?"), **body}
        if kind == "payment_link":
            entry["url"] = f"https://pay.fake/{entry['guest']}/{body.get('amount')}"
        with open(LEDGER, "a") as f:
            f.write(json.dumps(entry) + "\n")
        out = json.dumps(entry).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)

    def log_message(self, *a): pass                        # keep the terminal quiet

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
