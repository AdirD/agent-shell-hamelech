#!/usr/bin/env python3
"""Start, inspect, and stop an isolated debug-mode collector session."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.request import urlopen

SESSION_PREFIX = "debug-mode-"
START_TIMEOUT_SECONDS = 20.0
STOP_TIMEOUT_SECONDS = 5.0


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def assert_session_process(pid: int, session_dir: Path) -> None:
    """Refuse to signal a reused or unrelated PID on POSIX systems."""
    if not process_alive(pid) or os.name == "nt":
        return
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or str(session_dir) not in result.stdout:
        raise RuntimeError(f"PID {pid} does not belong to session {session_dir}")


def stop_process_group(pid: int) -> None:
    if not process_alive(pid):
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True,
            check=False,
        )
        return
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + STOP_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if not process_alive(pid):
            return
        time.sleep(0.1)
    if process_alive(pid):
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def stop_session_processes(session_dir: Path, launcher_pid: int) -> None:
    assert_session_process(launcher_pid, session_dir)
    stop_process_group(launcher_pid)

    metadata_path = session_dir / "collector.json"
    if not metadata_path.is_file():
        return
    collector_pid = int(read_json(metadata_path)["collector_pid"])
    if process_alive(collector_pid):
        assert_session_process(collector_pid, session_dir)
        stop_process_group(collector_pid)


def validated_session_dir(raw_path: str) -> Path:
    path = Path(raw_path).expanduser().resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if path.parent != temp_root or not path.name.startswith(SESSION_PREFIX):
        raise ValueError(f"refusing non-session path: {path}")
    if not (path / "launcher.json").is_file():
        raise ValueError(f"missing launcher metadata: {path}")
    return path


def start_session(args: argparse.Namespace) -> int:
    portless = shutil.which(args.portless_bin)
    if not portless:
        raise RuntimeError(
            "portless was not found; install the official CLI with "
            "`npm install -g portless`, then run `portless doctor`"
        )

    session_id = secrets.token_hex(5)
    session_dir = Path(tempfile.mkdtemp(prefix=SESSION_PREFIX)).resolve()
    route_name = f"debug-mode-{session_id}"
    token = secrets.token_urlsafe(24)
    token_file = session_dir / "token"
    token_file.write_text(token + "\n", encoding="utf-8")
    token_file.chmod(0o600)

    source = Path(__file__).resolve().parents[1] / "assets" / "collector.py"
    collector = session_dir / "collector.py"
    shutil.copy2(source, collector)
    runtime_log = session_dir / "runtime.log"
    command = [
        portless,
        route_name,
        sys.executable,
        str(collector),
        "--session-dir",
        str(session_dir),
    ]

    with runtime_log.open("ab") as output:
        process = subprocess.Popen(
            command,
            cwd=session_dir,
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=os.name != "nt",
            creationflags=(
                subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
                if os.name == "nt"
                else 0
            ),
        )

    launcher = {
        "session_id": session_id,
        "session_dir": str(session_dir),
        "route_name": route_name,
        "launcher_pid": process.pid,
        "runtime_log": str(runtime_log),
    }
    write_json(session_dir / "launcher.json", launcher)

    metadata_path = session_dir / "collector.json"
    deadline = time.monotonic() + args.timeout
    try:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                detail = runtime_log.read_text(encoding="utf-8", errors="replace")[-4000:]
                raise RuntimeError(f"collector exited during startup:\n{detail}")
            if metadata_path.is_file():
                metadata = read_json(metadata_path)
                backend_health = (
                    f"http://{metadata['backend_host']}:{metadata['backend_port']}/health"
                )
                try:
                    with urlopen(backend_health, timeout=1.0) as response:
                        if response.status == 200:
                            result = {**launcher, **metadata, "status": "running"}
                            print(json.dumps(result, indent=2))
                            return 0
                except OSError:
                    pass
            time.sleep(0.1)
        raise RuntimeError(f"collector did not become healthy within {args.timeout:g}s")
    except Exception:
        stop_session_processes(session_dir, process.pid)
        try:
            process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            pass
        detail = runtime_log.read_text(encoding="utf-8", errors="replace")[-4000:]
        shutil.rmtree(session_dir, ignore_errors=True)
        if detail:
            print(detail, file=sys.stderr)
        raise


def status_session(args: argparse.Namespace) -> int:
    session_dir = validated_session_dir(args.session_dir)
    launcher = read_json(session_dir / "launcher.json")
    metadata_path = session_dir / "collector.json"
    payload: dict[str, Any] = {
        **launcher,
        "status": "running" if process_alive(int(launcher["launcher_pid"])) else "stopped",
    }
    if metadata_path.is_file():
        payload.update(read_json(metadata_path))
    print(json.dumps(payload, indent=2))
    return 0


def logs_session(args: argparse.Namespace) -> int:
    session_dir = validated_session_dir(args.session_dir)
    events_file = session_dir / "events.jsonl"
    if not events_file.exists():
        return 0

    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(events_file.read_text(encoding="utf-8").splitlines(), 1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"invalid JSONL at line {line_number}: {error}") from error
        if args.run is not None and event.get("payload", {}).get("run") != args.run:
            continue
        if event.get("seq", 0) <= args.after_seq:
            continue
        events.append(event)

    for event in events[-args.tail :]:
        print(json.dumps(event, indent=2, sort_keys=True))
    return 0


def stop_session(args: argparse.Namespace) -> int:
    session_dir = validated_session_dir(args.session_dir)
    launcher = read_json(session_dir / "launcher.json")
    pid = int(launcher["launcher_pid"])
    stop_session_processes(session_dir, pid)
    collector_pid = int(read_json(session_dir / "collector.json")["collector_pid"])
    remaining = [candidate for candidate in {pid, collector_pid} if process_alive(candidate)]
    if remaining:
        raise RuntimeError(f"session processes are still alive: {remaining}")

    removed = False
    if not args.keep:
        shutil.rmtree(session_dir)
        removed = not session_dir.exists()
    print(json.dumps({"stopped": True, "removed": removed, "session_dir": str(session_dir)}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="start a new temporary collector")
    start.add_argument("--portless-bin", default="portless")
    start.add_argument("--timeout", type=float, default=START_TIMEOUT_SECONDS)
    start.set_defaults(func=start_session)

    status = subparsers.add_parser("status", help="show collector session status")
    status.add_argument("session_dir")
    status.set_defaults(func=status_session)

    logs = subparsers.add_parser("logs", help="print collected JSON events")
    logs.add_argument("session_dir")
    logs.add_argument("--run")
    logs.add_argument("--after-seq", type=int, default=0)
    logs.add_argument("--tail", type=int, default=200)
    logs.set_defaults(func=logs_session)

    stop = subparsers.add_parser("stop", help="stop and remove one collector session")
    stop.add_argument("session_dir")
    stop.add_argument("--keep", action="store_true", help="keep the session directory")
    stop.set_defaults(func=stop_session)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
