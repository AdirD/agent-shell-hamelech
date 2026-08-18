#!/usr/bin/env python3
"""Minimal local JSONL collector used by the debug-mode skill."""

from __future__ import annotations

import argparse
import json
import os
import signal
import threading
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

MAX_BODY_BYTES = 64 * 1024
SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "access_token",
    "authorization",
    "cookie",
    "password",
    "passwd",
    "private_key",
    "refresh_token",
    "secret",
    "set-cookie",
    "token",
}
NORMALIZED_SENSITIVE_KEYS = {item.replace("-", "_") for item in SENSITIVE_KEYS}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sensitive_path(value: Any, path: str = "payload") -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            child_path = f"{path}.{key}"
            if normalized in NORMALIZED_SENSITIVE_KEYS:
                return child_path
            found = sensitive_path(child, child_path)
            if found:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = sensitive_path(child, f"{path}[{index}]")
            if found:
                return found
    return None


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


class CollectorState:
    def __init__(self, session_dir: Path, token: str) -> None:
        self.session_dir = session_dir
        self.token = token
        self.events_file = session_dir / "events.jsonl"
        self.lock = threading.Lock()
        self.sequence = 0

    def append(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            self.sequence += 1
            event = {
                "seq": self.sequence,
                "received_at": utc_now(),
                "payload": payload,
            }
            with self.events_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, separators=(",", ":")) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            return event


class CollectorHandler(BaseHTTPRequestHandler):
    server_version = "DebugModeCollector/1"

    @property
    def state(self) -> CollectorState:
        return self.server.state  # type: ignore[attr-defined]

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path != "/health":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        self.send_json(
            HTTPStatus.OK,
            {"ok": True, "entries": self.state.sequence},
        )

    def do_POST(self) -> None:
        if self.path != f"/log/{self.state.token}":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return

        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length or "")
        except ValueError:
            self.send_json(HTTPStatus.LENGTH_REQUIRED, {"error": "content_length_required"})
            return
        if length < 1 or length > MAX_BODY_BYTES:
            self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "invalid_size"})
            return
        if "application/json" not in self.headers.get("Content-Type", "").lower():
            self.send_json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "json_required"})
            return

        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
            return
        if not isinstance(payload, dict):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "object_required"})
            return

        blocked = sensitive_path(payload)
        if blocked:
            self.send_json(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {"error": "sensitive_field_rejected", "path": blocked},
            )
            return

        event = self.state.append(payload)
        self.send_json(HTTPStatus.ACCEPTED, {"accepted": True, "seq": event["seq"]})

    def log_message(self, _format: str, *_args: Any) -> None:
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    session_dir = args.session_dir.resolve()
    token = (session_dir / "token").read_text(encoding="utf-8").strip()
    port = int(os.environ["PORT"])
    if not 1 <= port <= 65535:
        raise ValueError("PORT must be between 1 and 65535")
    host = os.environ.get("HOST", "127.0.0.1")
    public_url = os.environ.get("PORTLESS_URL", f"http://{host}:{port}").rstrip("/")

    state = CollectorState(session_dir, token)
    server = ThreadingHTTPServer((host, port), CollectorHandler)
    server.state = state  # type: ignore[attr-defined]

    metadata = {
        "collector_pid": os.getpid(),
        "backend_host": host,
        "backend_port": server.server_address[1],
        "collector_url": public_url,
        "health_url": f"{public_url}/health",
        "log_endpoint": f"{public_url}/log/{token}",
        "events_file": str(state.events_file),
        "started_at": utc_now(),
    }
    write_json_atomic(session_dir / "collector.json", metadata)

    def request_stop(_signum: int, _frame: Any) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
