#!/usr/bin/env python3
"""Discover and identify local coding-agent transcripts."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Optional

DEFAULT_LIMIT = 7
LIST_MAX_AGE_S = 14 * 24 * 60 * 60
GLIMPSE_READ_BYTES = 64 * 1024
GLIMPSE_MAX_CHARS = 96
INNER_ENV = re.compile(r"\$\{([A-Z0-9_]+)(?::-([^{}]*))?\}")
GENERIC_NAMES = {
    "events",
    "event",
    "chat",
    "messages",
    "message",
    "transcript",
    "session",
    "session_context",
    "updates",
    "wire",
    "history",
    "store",
}


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def load_registry() -> dict[str, Any]:
    path = skill_dir() / "references" / "providers.json"
    return json.loads(path.read_text(encoding="utf-8"))


def emit(payload: dict[str, Any], code: int = 0) -> int:
    print(json.dumps(payload, indent=2, sort_keys=False))
    return code


def fail(message: str, code: int = 1) -> int:
    return emit({"ok": False, "error": message}, code)


def slug_path(path: Path) -> str:
    resolved = path.resolve()
    text = str(resolved)
    if text.startswith("/"):
        text = text[1:]
    return text.replace("/", "-")


def worktree_root(cwd: Path) -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return cwd.resolve()
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()
    return cwd.resolve()


def main_worktree_root(cwd: Path) -> Optional[Path]:
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    first = next(
        (line.removeprefix("worktree ") for line in result.stdout.splitlines() if line.startswith("worktree ")),
        "",
    )
    return Path(first).resolve() if first else None


def worktree_label(cwd: Path, worktree: Path) -> str:
    main = main_worktree_root(cwd)
    return "main" if main == worktree.resolve() else worktree.name


def expand_template(template: str, env: dict[str, str], home: Path) -> str:
    text = template
    for _ in range(8):
        updated = INNER_ENV.sub(
            lambda match: env.get(match.group(1)) or (match.group(2) or ""),
            text,
        )
        if updated == text:
            break
        text = updated
    if text == "~":
        return str(home)
    if text.startswith("~/"):
        return str(home / text[2:])
    return text


def iter_glob(root: Path, pattern: str) -> Iterable[Path]:
    if not root.exists():
        return
    if pattern in ("", ".", "*") and root.is_dir():
        yield from (child for child in root.iterdir())
        return
    yield from root.glob(pattern)


def session_id_from_path(path: Path) -> str:
    stem = path.stem
    if stem.lower() not in GENERIC_NAMES and stem not in {".", ""}:
        if stem.startswith("rollout-") and "-" in stem:
            tail = stem.rsplit("-", 5)
            if len(tail) >= 6:
                return "-".join(tail[-5:])
        return stem
    parent = path.parent.name
    if parent and parent.lower() not in GENERIC_NAMES:
        if parent.startswith("session-"):
            return parent[len("session-") :]
        return parent
    return path.parent.parent.name or stem


def mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def file_times(path: Path) -> tuple[float, float]:
    try:
        info = path.stat()
    except OSError:
        return 0.0, 0.0
    modified = float(info.st_mtime)
    created = float(getattr(info, "st_birthtime", None) or info.st_ctime or modified)
    return created, modified


def format_when(stamp: float) -> str:
    if not stamp:
        return "unknown"
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(stamp))


def attach_dates(
    row: dict[str, Any],
    path: Optional[Path],
    now: float,
    fallback: float = 0.0,
) -> dict[str, Any]:
    created, modified = (0.0, 0.0)
    if path is not None:
        created, modified = file_times(path)
    if not modified:
        modified = fallback
    if not created:
        created = fallback or modified
    row["created_at"] = created
    row["modified_at"] = modified
    row["created"] = format_when(created)
    row["modified"] = format_when(modified)
    row["mtime"] = modified
    row["age"] = age_label(now - modified) if modified else "unknown"
    return row


def age_label(seconds_ago: float) -> str:
    seconds = max(0, int(seconds_ago))
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 48:
        return f"{hours}h"
    days = hours // 24
    return f"{days}d"


def claude_slug(worktree: Path) -> str:
    return "-" + str(worktree.resolve()).replace("/", "-").replace(".", "-")


def matches_worktree(path: Path, worktree: Path) -> bool:
    text = str(path)
    root = str(worktree.resolve())
    if root in text:
        return True
    cursor_slug = slug_path(worktree)
    cursor_dotless_slug = (
        str(worktree.resolve()).lstrip("/").replace("/.", "/").replace("/", "-")
    )
    if cursor_slug in text or cursor_dotless_slug in text:
        return True
    encoded = claude_slug(worktree)
    return encoded in text or encoded.lstrip("-") in text


def primary_transcript_file(path: Path) -> Optional[Path]:
    if path.is_file():
        return path
    if not path.is_dir():
        return None
    for name in (
        "events.jsonl",
        "chat.jsonl",
        "messages.jsonl",
        "transcript.jsonl",
        "session_context.json",
        "api_conversation_history.json",
    ):
        candidate = path / name
        if candidate.is_file():
            return candidate
    files = sorted(
        (child for child in path.iterdir() if child.is_file()),
        key=mtime,
        reverse=True,
    )
    return files[0] if files else None


def message_roles(value: Any) -> list[str]:
    if isinstance(value, dict):
        role = value.get("role")
        if isinstance(role, str) and role.lower() in {"user", "assistant", "system", "developer"}:
            return [role.lower()]
        event_type = value.get("type")
        if isinstance(event_type, str) and event_type.lower() in {
            "user",
            "assistant",
            "system",
            "developer",
        }:
            return [event_type.lower()]
        for key in ("message", "payload", "data", "event"):
            roles = message_roles(value.get(key))
            if roles:
                return roles
        roles: list[str] = []
        for key in ("messages", "events", "history", "conversation", "items"):
            roles.extend(message_roles(value.get(key)))
        return roles
    if isinstance(value, list):
        roles: list[str] = []
        for item in value:
            roles.extend(message_roles(item))
        return roles
    return []


def transcript_stats(path: Path) -> dict[str, Any]:
    target = primary_transcript_file(path)
    if target is None:
        return {
            "ok": False,
            "bytes": 0,
            "chars": 0,
            "approx_tokens": 0,
            "messages": 0,
            "user_messages": 0,
        }
    try:
        info = target.stat()
    except OSError:
        return {
            "ok": False,
            "bytes": 0,
            "chars": 0,
            "approx_tokens": 0,
            "messages": 0,
            "user_messages": 0,
        }
    chars = 0
    roles: list[str] = []
    try:
        with target.open("rb") as handle:
            for raw in handle:
                text = raw.decode("utf-8", errors="replace")
                chars += len(text)
                try:
                    roles.extend(message_roles(json.loads(text)))
                except json.JSONDecodeError:
                    continue
    except OSError:
        return {
            "ok": False,
            "bytes": int(info.st_size),
            "chars": chars,
            "approx_tokens": chars // 4,
            "messages": len(roles),
            "user_messages": roles.count("user"),
        }

    if not roles and target.suffix.lower() == ".json":
        try:
            roles = message_roles(json.loads(target.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass

    return {
        "ok": True,
        "path": str(target.resolve()),
        "bytes": int(info.st_size),
        "chars": chars,
        "approx_tokens": chars // 4 if chars else 0,
        "messages": len(roles),
        "user_messages": roles.count("user"),
    }


def extract_glimpse(path: Path) -> str:
    target = primary_transcript_file(path)
    if target is None:
        return ""
    try:
        data = target.read_bytes()[:GLIMPSE_READ_BYTES]
    except OSError:
        return ""
    text = data.decode("utf-8", errors="replace")
    strings = re.findall(r'"((?:\\.|[^"\\]){12,400})"', text)
    if not strings:
        for line in text.splitlines():
            stripped = line.strip()
            if len(stripped) >= 12 and not stripped.startswith("{"):
                strings.append(stripped)
    skip = re.compile(
        r"^(https?://|file://|/|~|[\w.-]+/)|^(system|assistant|user|tool)$",
        re.I,
    )
    for raw in strings:
        value = bytes(raw, "utf-8").decode("unicode_escape", errors="replace")
        value = re.sub(r"\s+", " ", value).strip()
        if len(value) < 12 or skip.match(value):
            continue
        if value.startswith("<") and value.endswith(">"):
            continue
        return value[:GLIMPSE_MAX_CHARS]
    return ""


def discover_sessions(
    *,
    home: Path,
    env: dict[str, str],
    max_age_s: float,
    now: float,
) -> list[dict[str, Any]]:
    registry = load_registry()
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for provider in registry["providers"]:
        if provider.get("support") != "full":
            continue
        locations = list(provider.get("locations") or [])
        if provider["id"] == "cursor" and env.get("AGENT_TRANSCRIPTS"):
            locations.insert(
                0,
                {
                    "root": env["AGENT_TRANSCRIPTS"],
                    "session_glob": "*/*.jsonl",
                },
            )
        for location in locations:
            root = Path(
                expand_template(location.get("root") or "", env, home)
            ).expanduser()
            pattern = location.get("session_glob") or "*"
            for match in iter_glob(root, pattern):
                if not match.exists():
                    continue
                if match.suffix in {".db", ".sqlite", ".sqlite3", ".zst", ".zstd"}:
                    continue
                if match.name.endswith(".jsonl.zst"):
                    continue
                unit = provider.get("unit") or "file"
                path = match
                if unit == "directory" and match.is_file():
                    path = match.parent
                key = str(path.resolve()) if path.exists() else str(path)
                if key in seen:
                    continue
                created, modified = file_times(path)
                stamp = modified or created
                if stamp and now - stamp > max_age_s:
                    continue
                seen.add(key)
                session_id = session_id_from_path(match if match.is_file() else path)
                primary = primary_transcript_file(path)
                found.append(
                    attach_dates(
                        {
                            "provider": provider["id"],
                            "provider_name": provider["name"],
                            "session_id": session_id,
                            "short_id": session_id[:8],
                            "transcript_path": key,
                            "primary_transcript_path": (
                                str(primary.resolve()) if primary else ""
                            ),
                            "transcript_kind": "directory" if path.is_dir() else "file",
                            "glimpse": extract_glimpse(path),
                        },
                        path,
                        now,
                    )
                )
    return found


def merge_rows(
    sessions: list[dict[str, Any]],
    *,
    worktree: Path,
    exclude_current: Optional[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current_id = (exclude_current or {}).get("session_id")
    current_path = (exclude_current or {}).get("transcript_path")

    for session in sessions:
        if current_id and session["session_id"] == current_id:
            continue
        if current_path and session["transcript_path"] == current_path:
            continue
        if not matches_worktree(Path(session["transcript_path"]), worktree):
            if worktree.name not in session["transcript_path"]:
                continue
        rows.append(session)

    rows.sort(key=lambda row: (-row["mtime"], row["provider"], row["session_id"]))
    return rows


def resolve_exact_cursor(env: dict[str, str]) -> Optional[dict[str, Any]]:
    session_id = env.get("CURSOR_CONVERSATION_ID", "").strip()
    transcripts = env.get("AGENT_TRANSCRIPTS", "").strip()
    if not session_id or not transcripts:
        return None
    path = Path(transcripts) / session_id / f"{session_id}.jsonl"
    if not path.is_file():
        return None
    return attach_dates(
        {
            "provider": "cursor",
            "provider_name": "Cursor",
            "session_id": session_id,
            "short_id": session_id[:8],
            "transcript_path": str(path),
            "primary_transcript_path": str(path),
            "transcript_kind": "file",
            "glimpse": extract_glimpse(path),
        },
        path,
        time.time(),
    )


def resolve_exact_claude(
    env: dict[str, str], home: Path, worktree: Path
) -> Optional[dict[str, Any]]:
    session_id = env.get("CLAUDE_SESSION_ID", "").strip()
    if not session_id:
        return None
    root = Path(expand_template("${CLAUDE_CONFIG_DIR:-~/.claude}/projects", env, home))
    matches = list(root.glob(f"**/{session_id}.jsonl"))
    if not matches:
        encoded = claude_slug(worktree)
        candidate = root / encoded / f"{session_id}.jsonl"
        if candidate.is_file():
            matches = [candidate]
    if len(matches) != 1:
        return None
    path = matches[0]
    return attach_dates(
        {
            "provider": "claude_code",
            "provider_name": "Claude Code",
            "session_id": session_id,
            "short_id": session_id[:8],
            "transcript_path": str(path),
            "primary_transcript_path": str(path),
            "transcript_kind": "file",
            "glimpse": extract_glimpse(path),
        },
        path,
        time.time(),
    )


def list_rows(
    *,
    cwd: Path,
    home: Path,
    env: dict[str, str],
    limit: int,
    hide_current: bool = True,
    include_stats: bool = True,
) -> dict[str, Any]:
    worktree = worktree_root(cwd)
    label = worktree_label(cwd, worktree)
    now = time.time()
    current = None
    if hide_current:
        current = resolve_exact_cursor(env) or resolve_exact_claude(env, home, worktree)
    sessions = discover_sessions(home=home, env=env, max_age_s=LIST_MAX_AGE_S, now=now)
    rows = merge_rows(
        sessions,
        worktree=worktree,
        exclude_current=current,
    )
    selected = rows[:limit]
    for row in selected:
        row["worktree"] = label
        if include_stats:
            row["stats"] = transcript_stats(Path(row["transcript_path"]))
    return {
        "ok": True,
        "worktree": str(worktree),
        "worktree_name": label,
        "slug": slug_path(worktree),
        "count": len(selected),
        "rows": selected,
    }


def lookup_row(*, cwd: Path, home: Path, env: dict[str, str], session_id: str) -> dict[str, Any]:
    payload = list_rows(
        cwd=cwd,
        home=home,
        env=env,
        limit=200,
        hide_current=False,
        include_stats=False,
    )
    prefix = session_id.lower()
    matches = []
    for row in payload["rows"]:
        if not (
            str(row.get("session_id") or "").lower().startswith(prefix)
            or str(row.get("short_id") or "").lower() == prefix
        ):
            continue
        matched = dict(row)
        primary = primary_transcript_file(Path(row["transcript_path"]))
        matched["primary_transcript_path"] = str(primary.resolve()) if primary else ""
        matches.append(matched)
    if len(matches) == 1:
        return {"ok": True, "status": "exact", "row": matches[0], "rows": matches}
    if matches:
        return {"ok": True, "status": "ambiguous", "rows": matches}
    return {"ok": True, "status": "not_found", "rows": []}


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--cwd", default=".", help="Working directory used to derive the worktree")
    common.add_argument("--home", default=None, help="Override home directory (tests)")
    parser = argparse.ArgumentParser(
        description="Discover and identify local coding-agent transcripts.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    listed = sub.add_parser("list", parents=[common], help="List recent transcripts")
    listed.add_argument("--limit", type=int, default=DEFAULT_LIMIT)

    lookup = sub.add_parser("lookup", parents=[common], help="Look up a session by id prefix")
    lookup.add_argument("--id", required=True)

    sub.add_parser("providers", parents=[common], help="Print the provider registry")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cwd = Path(args.cwd).resolve()
    home = Path(args.home).expanduser().resolve() if args.home else Path.home()
    env = {key: value for key, value in os.environ.items() if value}
    if args.home:
        env.setdefault("HOME", str(home))

    if args.command == "providers":
        registry = load_registry()
        return emit(
            {
                "ok": True,
                "schema_version": registry.get("schema_version"),
                "count": len(registry.get("providers") or []),
                "full": sum(1 for row in registry["providers"] if row.get("support") == "full"),
                "excluded": sum(
                    1 for row in registry["providers"] if row.get("support") == "excluded"
                ),
                "providers": registry["providers"],
            }
        )
    if args.command == "list":
        return emit(list_rows(cwd=cwd, home=home, env=env, limit=args.limit))
    if args.command == "lookup":
        return emit(lookup_row(cwd=cwd, home=home, env=env, session_id=args.id))
    return fail("unknown command")


if __name__ == "__main__":
    sys.exit(main())
