#!/usr/bin/env python3
"""Serve one plan-review page on localhost and save its comments beside it."""

import argparse
import http.server
import json
import pathlib
import webbrowser

MAX_BODY = 2_000_000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("page", help="the filled plan-review HTML page")
    parser.add_argument("--port", type=int, default=0, help="0 picks a free port")
    parser.add_argument("--no-open", action="store_true", help="do not open a browser")
    args = parser.parse_args()

    page = pathlib.Path(args.page).resolve()
    if not page.is_file():
        parser.error(f"no such page: {page}")
    review = page.with_suffix(".json")

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            path = self.path.split("?", 1)[0]
            if path in ("/", "/" + page.name):
                self.send(200, "text/html; charset=utf-8", page.read_bytes())
            elif path == "/review":
                body = review.read_bytes() if review.exists() else b"null"
                self.send(200, "application/json", body)
            else:
                self.send(404, "text/plain", b"not found")

        def do_POST(self) -> None:
            if self.path.split("?", 1)[0] != "/review":
                return self.send(404, "text/plain", b"not found")
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_BODY:
                return self.send(413, "text/plain", b"bad size")
            try:
                data = json.loads(self.rfile.read(length))
            except ValueError:
                return self.send(400, "text/plain", b"bad json")
            tmp = review.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            tmp.replace(review)
            self.send(204, "text/plain", b"")

        def send(self, code: int, kind: str, body: bytes) -> None:
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_: object) -> None:
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{server.server_port}/{page.name}"
    print(json.dumps({"url": url, "page": str(page), "review": str(review)}), flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
