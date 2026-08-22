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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

SESSION_PREFIX = "debug-mode-"
START_TIMEOUT_SECONDS = 20.0
STOP_TIMEOUT_SECONDS = 5.0
BROWSER_CHECK_TIMEOUT_SECONDS = 30.0
BROWSER_SETUP_HINT = {
    "install": "npm i -g agent-browser && agent-browser install",
    "enable_remote_debugging": (
        "Open chrome://inspect/#remote-debugging and enable "
        "Allow remote debugging for this browser instance (Chrome 144+)."
    ),
    "allow_dialog": (
        "When Chrome prompts, click Allow. Dismissing the dialog denies attach."
    ),
    "fallback": (
        "If attach still fails, keep the collector running and use the human "
        "proceed reproduction path."
    ),
}


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


HEALTH_TIMEOUT_SECONDS = 0.4
ERROR_MARKERS = ("Traceback", "Error", "Exception", "CRITICAL", "Fatal", "refused")


def discover_sessions() -> list[Path]:
    """Return every debug-mode session directory in the temp root."""
    temp_root = Path(tempfile.gettempdir()).resolve()
    sessions: list[Path] = []
    try:
        children = list(temp_root.iterdir())
    except OSError:
        return sessions
    for child in children:
        if (
            child.is_dir()
            and child.name.startswith(SESSION_PREFIX)
            and (child / "launcher.json").is_file()
        ):
            sessions.append(child.resolve())
    return sorted(sessions, key=lambda path: path.name)


def probe_health(metadata: dict[str, Any]) -> tuple[str, int | None]:
    """Ping the collector's /health endpoint and classify the result."""
    host = metadata.get("backend_host")
    port = metadata.get("backend_port")
    if not host or not port:
        return "unknown", None
    url = f"http://{host}:{port}/health"
    try:
        with urlopen(url, timeout=HEALTH_TIMEOUT_SECONDS) as response:
            if response.status != 200:
                return "unhealthy", None
            data = json.loads(response.read().decode("utf-8"))
    except (URLError, OSError, ValueError):
        return "unreachable", None
    entries = data.get("entries")
    return "healthy", entries if isinstance(entries, int) else None


def last_error_line(runtime_log: Path) -> str | None:
    """Return the most recent runtime.log line that looks like an error."""
    try:
        lines = runtime_log.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        stripped = line.strip()
        if stripped and any(marker in stripped for marker in ERROR_MARKERS):
            return stripped
    return None


def format_age(started_at: str | None) -> str:
    if not started_at:
        return "-"
    try:
        started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    except ValueError:
        return "-"
    seconds = int((datetime.now(timezone.utc) - started).total_seconds())
    if seconds < 0:
        return "0s"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m{seconds % 60:02d}s"
    return f"{seconds // 3600}h{(seconds % 3600) // 60:02d}m"


def session_snapshot(session_dir: Path) -> dict[str, Any]:
    """Collect status, health, and diagnostics for one session directory."""
    snapshot: dict[str, Any] = {
        "session_dir": session_dir,
        "session_id": session_dir.name.replace(SESSION_PREFIX, "", 1),
        "route_name": None,
        "status": "unknown",
        "health": "unknown",
        "entries": None,
        "backend_port": None,
        "backend_host": None,
        "collector_url": None,
        "launcher_pid": None,
        "collector_pid": None,
        "launcher_alive": False,
        "collector_alive": False,
        "started_at": None,
        "age": "-",
        "last_error": None,
    }
    try:
        launcher = read_json(session_dir / "launcher.json")
    except (OSError, json.JSONDecodeError):
        return snapshot

    snapshot["session_id"] = launcher.get("session_id", snapshot["session_id"])
    snapshot["route_name"] = launcher.get("route_name")
    launcher_pid = int(launcher.get("launcher_pid", 0) or 0)
    snapshot["launcher_pid"] = launcher_pid or None
    snapshot["launcher_alive"] = launcher_pid > 0 and process_alive(launcher_pid)

    metadata_path = session_dir / "collector.json"
    has_metadata = metadata_path.is_file()
    if has_metadata:
        try:
            metadata = read_json(metadata_path)
            collector_pid = int(metadata.get("collector_pid", 0) or 0)
            snapshot["collector_pid"] = collector_pid or None
            snapshot["collector_alive"] = collector_pid > 0 and process_alive(collector_pid)
            snapshot["backend_host"] = metadata.get("backend_host")
            snapshot["backend_port"] = metadata.get("backend_port")
            snapshot["collector_url"] = metadata.get("collector_url")
            snapshot["started_at"] = metadata.get("started_at")
            if snapshot["launcher_alive"] and snapshot["collector_alive"]:
                snapshot["health"], snapshot["entries"] = probe_health(metadata)
        except (OSError, json.JSONDecodeError, KeyError, ValueError):
            pass

    if not snapshot["launcher_alive"] or (has_metadata and not snapshot["collector_alive"]):
        snapshot["status"] = "dead"
    elif not has_metadata:
        snapshot["status"] = "starting"
    elif snapshot["health"] == "healthy":
        snapshot["status"] = "running"
    else:
        snapshot["status"] = "degraded"

    snapshot["age"] = format_age(snapshot["started_at"])

    runtime_log = launcher.get("runtime_log")
    if runtime_log:
        snapshot["last_error"] = last_error_line(Path(runtime_log))
    return snapshot


def kill_session_dir(session_dir: Path) -> None:
    """Stop a session's processes and delete its temp directory (same as `stop`)."""
    session_dir = validated_session_dir(str(session_dir))
    launcher = read_json(session_dir / "launcher.json")
    stop_session_processes(session_dir, int(launcher["launcher_pid"]))
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)


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


def _browser_setup_failure(error: str, **extra: Any) -> int:
    payload: dict[str, Any] = {
        "ok": False,
        "error": error,
        "hint": BROWSER_SETUP_HINT,
    }
    payload.update(extra)
    print(json.dumps(payload, indent=2))
    return 1


def _tab_record(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None
    title = item.get("title") or item.get("name")
    url = item.get("url") or item.get("targetUrl")
    if title is None and url is None:
        return None
    record: dict[str, Any] = {}
    if title is not None:
        record["title"] = title
    if url is not None:
        record["url"] = url
    for key in ("id", "index", "targetId", "type"):
        if key in item:
            record[key] = item[key]
    return record


def _extract_tabs(parsed: Any) -> list[dict[str, Any]] | None:
    if isinstance(parsed, list):
        records = [record for item in parsed if (record := _tab_record(item))]
        return records or None
    if not isinstance(parsed, dict):
        return None
    for key in ("tabs", "data", "result", "targets"):
        value = parsed.get(key)
        if isinstance(value, list):
            records = [record for item in value if (record := _tab_record(item))]
            if records:
                return records
        if isinstance(value, dict):
            nested = _extract_tabs(value)
            if nested:
                return nested
    record = _tab_record(parsed)
    return [record] if record else None


def browser_check_session(args: argparse.Namespace) -> int:
    binary = shutil.which("agent-browser")
    if binary is None:
        return _browser_setup_failure(
            "agent-browser not found on PATH",
        )

    command = [binary, "--auto-connect", "--json"]
    if args.session:
        command.extend(["--session", args.session])
    command.extend(["tab", "list"])

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _browser_setup_failure(
            f"agent-browser timed out after {args.timeout}s waiting to attach",
            command=command[1:],
        )

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    parsed: Any = None
    if stdout:
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            parsed = None

    tabs = _extract_tabs(parsed) if parsed is not None else None
    if result.returncode == 0 and tabs is not None:
        print(json.dumps({"ok": True, "tabs": tabs}, indent=2))
        return 0

    if result.returncode == 0 and parsed is not None:
        print(json.dumps({"ok": True, "tabs": parsed}, indent=2))
        return 0

    error = stderr or stdout or f"agent-browser exited with {result.returncode}"
    return _browser_setup_failure(
        error,
        command=command[1:],
        exit_code=result.returncode,
    )


STATUS_GLYPHS = {
    "running": "\u25cf",
    "degraded": "\u25d0",
    "starting": "\u25cc",
    "dead": "\u25cb",
    "unknown": "\u25cb",
}
SCAN_INTERVAL_SECONDS = 0.8


def _status_color(status: str) -> int:
    if status == "running":
        return 1
    if status in ("degraded", "starting"):
        return 2
    return 3


def _compact(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, separators=(",", ":"))
    return text if len(text) <= 40 else text[:37] + "..."


def _event_line(event: dict[str, Any]) -> str:
    payload = event.get("payload", {}) if isinstance(event, dict) else {}
    seq = event.get("seq", "?") if isinstance(event, dict) else "?"
    run = payload.get("run", "-")
    probe = payload.get("probe", "-")
    data = payload.get("data", {})
    if isinstance(data, dict):
        body = ", ".join(f"{key}={_compact(val)}" for key, val in data.items())
    else:
        body = _compact(data)
    return f"#{seq} [{run}] {probe}  {body}".rstrip()


def _read_events_tail(session_dir: Path, limit: int) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    try:
        lines = (session_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    events: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _safe_addstr(win: Any, y: int, x: int, text: str, attr: int = 0) -> None:
    curses = sys.modules["curses"]
    height, width = win.getmaxyx()
    if y < 0 or y >= height or x < 0 or x >= width:
        return
    clipped = text[: max(0, width - x - 1)]
    if not clipped:
        return
    try:
        win.addstr(y, x, clipped, attr)
    except curses.error:
        pass


def _draw_doctor(
    stdscr: Any,
    sessions: list[dict[str, Any]],
    selected: int,
    message: str,
    confirm: Path | None,
) -> None:
    curses = sys.modules["curses"]
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    running = sum(1 for snap in sessions if snap["status"] == "running")
    accent = curses.color_pair(4) | curses.A_BOLD

    title = f" debug-mode doctor \u2014 {len(sessions)} session(s), {running} running"
    _safe_addstr(stdscr, 0, 0, title.ljust(width - 1), accent)
    _safe_addstr(
        stdscr,
        1,
        1,
        f"{'':2}{'STATUS':<10}{'SESSION':<14}{'PORT':<7}{'EV':<6}{'AGE':<8}HEALTH",
        curses.A_DIM,
    )

    list_capacity = max(1, (height - 5) // 3)
    visible = min(len(sessions), list_capacity)
    list_top = 2
    for index in range(visible):
        snap = sessions[index]
        row = list_top + index
        selected_row = index == selected
        base = curses.A_REVERSE if selected_row else 0
        _safe_addstr(stdscr, row, 1, ">" if selected_row else " ", base | curses.A_BOLD)
        glyph = STATUS_GLYPHS.get(snap["status"], "?")
        _safe_addstr(stdscr, row, 2, f" {glyph} ", curses.color_pair(_status_color(snap["status"])) | curses.A_BOLD)
        port = str(snap.get("backend_port") or "-")
        entries = snap.get("entries")
        entries_text = str(entries) if entries is not None else "-"
        line = (
            f"{snap['status']:<10}{snap['session_id'][:13]:<14}"
            f"{port:<7}{entries_text:<6}{snap['age']:<8}{snap['health']}"
        )
        _safe_addstr(stdscr, row, 5, line, base)

    if len(sessions) > visible:
        _safe_addstr(stdscr, list_top + visible, 5, f"... {len(sessions) - visible} more", curses.A_DIM)

    divider_row = list_top + max(visible, 1) + (1 if len(sessions) > visible else 0)
    _safe_addstr(stdscr, divider_row, 0, "\u2500" * (width - 1), curses.A_DIM)

    detail_top = divider_row + 1
    footer_row = height - 1
    if sessions and 0 <= selected < len(sessions):
        snap = sessions[selected]
        health_attr = curses.color_pair(_status_color(snap["status"])) | curses.A_BOLD
        _safe_addstr(stdscr, detail_top, 1, f"SESSION {snap['session_id']}", accent)
        _safe_addstr(
            stdscr,
            detail_top,
            max(1, width - 30),
            f"route {snap.get('route_name') or '-'}",
            curses.A_DIM,
        )
        _safe_addstr(stdscr, detail_top + 1, 1, "status ", curses.A_DIM)
        _safe_addstr(stdscr, detail_top + 1, 8, snap["status"], health_attr)
        _safe_addstr(
            stdscr,
            detail_top + 1,
            22,
            f"health {snap['health']}   entries {snap.get('entries') if snap.get('entries') is not None else '-'}   age {snap['age']}",
        )
        launcher_state = "alive" if snap["launcher_alive"] else "dead"
        collector_state = "alive" if snap["collector_alive"] else "dead"
        _safe_addstr(
            stdscr,
            detail_top + 2,
            1,
            f"launcher pid {snap.get('launcher_pid') or '-'} ({launcher_state})   "
            f"collector pid {snap.get('collector_pid') or '-'} ({collector_state})   "
            f"port {snap.get('backend_port') or '-'}",
            curses.A_DIM,
        )
        if snap.get("last_error"):
            _safe_addstr(
                stdscr,
                detail_top + 3,
                1,
                f"last error: {snap['last_error']}",
                curses.color_pair(3) | curses.A_BOLD,
            )
        events_label_row = detail_top + 4
        _safe_addstr(stdscr, events_label_row, 1, "events (live tail):", curses.A_DIM)
        tail_top = events_label_row + 1
        tail_capacity = max(0, footer_row - tail_top)
        events = _read_events_tail(snap["session_dir"], tail_capacity)
        if not events:
            _safe_addstr(stdscr, tail_top, 2, "(no events yet)", curses.A_DIM)
        else:
            start = tail_top + max(0, tail_capacity - len(events))
            for offset, event in enumerate(events[-tail_capacity:]):
                _safe_addstr(stdscr, start + offset, 2, _event_line(event))
    else:
        _safe_addstr(stdscr, detail_top, 1, "No active debug-mode sessions.", curses.A_DIM)

    if confirm is not None:
        prompt = f" kill {confirm.name.replace(SESSION_PREFIX, '', 1)}? y = confirm, n = cancel "
        _safe_addstr(stdscr, footer_row, 0, prompt.ljust(width - 1), curses.color_pair(3) | curses.A_BOLD | curses.A_REVERSE)
    else:
        keys = " \u2191/\u2193 j/k move   x kill+delete   r refresh   q quit "
        _safe_addstr(stdscr, footer_row, 0, keys, curses.A_REVERSE)
        if message:
            _safe_addstr(stdscr, footer_row, max(0, width - len(message) - 2), message, curses.color_pair(4))
    stdscr.noutrefresh()
    curses.doupdate()


def _doctor_main(stdscr: Any, _args: argparse.Namespace) -> None:
    curses = sys.modules["curses"]
    curses.curs_set(0)
    stdscr.timeout(200)
    if curses.has_colors():
        curses.start_color()
        try:
            curses.use_default_colors()
            background = -1
        except curses.error:
            background = curses.COLOR_BLACK
        curses.init_pair(1, curses.COLOR_GREEN, background)
        curses.init_pair(2, curses.COLOR_YELLOW, background)
        curses.init_pair(3, curses.COLOR_RED, background)
        curses.init_pair(4, curses.COLOR_CYAN, background)

    selected = 0
    sessions: list[dict[str, Any]] = []
    message = ""
    confirm: Path | None = None
    last_scan = 0.0

    while True:
        now = time.monotonic()
        if now - last_scan >= SCAN_INTERVAL_SECONDS:
            sessions = [session_snapshot(path) for path in discover_sessions()]
            last_scan = now
            if selected >= len(sessions):
                selected = max(0, len(sessions) - 1)

        _draw_doctor(stdscr, sessions, selected, message, confirm)

        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            return
        if key == -1:
            continue

        if confirm is not None:
            if key in (ord("y"), ord("Y")):
                target = confirm
                confirm = None
                try:
                    kill_session_dir(target)
                    message = f"killed {target.name.replace(SESSION_PREFIX, '', 1)}"
                except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as error:
                    message = f"kill failed: {error}"
                last_scan = 0.0
            elif key in (ord("n"), ord("N"), 27):
                confirm = None
                message = "kill cancelled"
            continue

        if key in (ord("q"), ord("Q")):
            return
        if key in (curses.KEY_UP, ord("k")):
            selected = max(0, selected - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected = min(max(0, len(sessions) - 1), selected + 1)
        elif key in (ord("r"), ord("R")):
            last_scan = 0.0
            message = "refreshed"
        elif key in (ord("x"), ord("X")):
            if sessions and 0 <= selected < len(sessions):
                confirm = sessions[selected]["session_dir"]
        elif key == curses.KEY_RESIZE:
            continue


def doctor_session(args: argparse.Namespace) -> int:
    try:
        import curses
    except ImportError as error:
        raise RuntimeError(
            "doctor requires the curses module, which is unavailable on this platform"
        ) from error
    if args.once:
        sessions = [session_snapshot(path) for path in discover_sessions()]
        print(json.dumps(sessions, indent=2, default=str))
        return 0
    curses.wrapper(_doctor_main, args)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Manage isolated debug-mode collector sessions. "
            "Run `doctor` for a live TUI of every session (health, log tail, kill)."
        ),
        epilog=(
            "examples:\n"
            "  debug_session.py doctor            live TUI: sessions, health, logs, kill\n"
            "  debug_session.py doctor --once     one-shot JSON snapshot (no TTY needed)\n"
            "  debug_session.py start             start a new collector session\n"
            "  debug_session.py status <dir>      status of one session\n"
            "  debug_session.py logs <dir> --run run-1\n"
            "  debug_session.py stop <dir>        stop and remove one session\n"
            "  debug_session.py browser-check     attach via agent-browser --auto-connect\n"
            "\n"
            "With the `dm` shell command installed (scripts/install-dm.sh):\n"
            "  dm            open the doctor TUI\n"
            "  dm help       show this help\n"
            "  dm start / dm stop <dir> / ...     same subcommands\n"
            "  dm browser-check [--session name]  list open Chrome tabs or print setup hints\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="command")

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

    doctor = subparsers.add_parser(
        "doctor",
        help="live TUI of all debug-mode sessions with health, log tail, and kill",
    )
    doctor.add_argument(
        "--once",
        action="store_true",
        help="print a one-shot JSON snapshot instead of launching the TUI",
    )
    doctor.set_defaults(func=doctor_session)

    browser_check = subparsers.add_parser(
        "browser-check",
        help="attach to the user's Chrome via agent-browser --auto-connect and list tabs",
    )
    browser_check.add_argument(
        "--session",
        help="agent-browser session name (use dm-<debug-mode session_id>)",
    )
    browser_check.add_argument(
        "--timeout",
        type=float,
        default=BROWSER_CHECK_TIMEOUT_SECONDS,
        help="seconds to wait for Chrome Allow / auto-connect",
    )
    browser_check.set_defaults(func=browser_check_session)
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
