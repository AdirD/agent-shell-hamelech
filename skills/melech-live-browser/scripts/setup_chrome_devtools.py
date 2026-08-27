#!/usr/bin/env python3
"""Inspect or update one JSON host config for Chrome DevTools MCP auto-connect."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

SERVER_KEYS = ("chrome-devtools", "chrome-devtools-mcp")
AUTO_CONNECT_FLAGS = ("--autoConnect", "--auto-connect")
OFFICIAL_SERVER = {
    "command": "npx",
    "args": ["chrome-devtools-mcp@latest", "--autoConnect"],
}


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("config root must be a JSON object")
    return payload


def mcp_servers(payload: dict[str, Any], *, create: bool) -> dict[str, Any]:
    if "mcpServers" in payload:
        servers = payload["mcpServers"]
        if isinstance(servers, dict):
            return servers
        raise ValueError("mcpServers must be a JSON object")

    nested = payload.get("mcp")
    if isinstance(nested, dict):
        if "mcpServers" in nested:
            servers = nested["mcpServers"]
            if isinstance(servers, dict):
                return servers
            raise ValueError("mcp.mcpServers must be a JSON object")
        if create:
            nested["mcpServers"] = {}
            return nested["mcpServers"]

    if create:
        payload["mcpServers"] = {}
        return payload["mcpServers"]
    return {}


def find_server(
    servers: dict[str, Any],
) -> tuple[str, dict[str, Any]] | None:
    for key in SERVER_KEYS:
        entry = servers.get(key)
        if isinstance(entry, dict):
            return key, entry
    return None


def has_auto_connect(entry: dict[str, Any]) -> bool:
    args = entry.get("args")
    return isinstance(args, list) and any(
        str(value) in AUTO_CONNECT_FLAGS for value in args
    )


def inspect(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    found = find_server(mcp_servers(payload, create=False))
    if found is None:
        return {
            "config": str(path),
            "present": False,
            "autoConnect": False,
        }

    key, entry = found
    if "url" in entry or not isinstance(entry.get("command"), str):
        return {
            "config": str(path),
            "present": True,
            "autoConnect": False,
            "server": key,
            "remote": True,
            "reason": "remote or non-command server; not rewritten",
        }

    return {
        "config": str(path),
        "present": True,
        "autoConnect": has_auto_connect(entry),
        "server": key,
        "remote": False,
    }


def write_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode if path.exists() else None
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary)
    try:
        if mode is not None:
            os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def apply(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    servers = mcp_servers(payload, create=True)
    found = find_server(servers)
    if found is None:
        servers["chrome-devtools"] = {
            "command": OFFICIAL_SERVER["command"],
            "args": list(OFFICIAL_SERVER["args"]),
        }
        action = "added"
    else:
        _, entry = found
        if "url" in entry or not isinstance(entry.get("command"), str):
            result = inspect(path, payload)
            result["action"] = "skipped"
            return result
        args = entry.get("args")
        if not isinstance(args, list):
            args = []
            entry["args"] = args
        if has_auto_connect(entry):
            action = "already_ok"
        else:
            args.append("--autoConnect")
            action = "updated"

    write_atomic(path, payload)
    result = inspect(path, payload)
    result["action"] = action
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect one JSON MCP config. Pass --apply to add or update the "
            "Chrome DevTools MCP --autoConnect command."
        )
    )
    parser.add_argument(
        "--config",
        required=True,
        help="exact JSON host config to inspect or update",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write the selected config; without this flag the command is read-only",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.config).expanduser()
    if path.is_symlink():
        path = path.resolve()

    try:
        payload = load_config(path)
        result = apply(path, payload) if args.apply else inspect(path, payload)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "config": str(path), "error": str(error)}, indent=2))
        return 1

    ready = bool(result.get("present") and result.get("autoConnect"))
    changed = result.get("action") in {"added", "updated"}
    output = {
        "ok": ready,
        "ready": ready,
        "reload_required": changed,
        **result,
        "next": (
            "Reload this host's chrome-devtools MCP server."
            if changed
            else (
                "Chrome DevTools MCP --autoConnect is configured."
                if ready
                else "Apply the official local command entry to this host config."
            )
        ),
    }
    print(json.dumps(output, indent=2))
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
