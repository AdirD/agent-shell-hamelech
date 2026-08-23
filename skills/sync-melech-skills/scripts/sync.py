#!/usr/bin/env python3
"""Install and update every remote melech skill into the global skills lock.

Always user-global, never project/repo. Fans out to every agent the Skills
CLI supports (`-a '*'`). Non-interactive (`-y`).

Does not touch non-melech skills. Does not remove skills that left remote.

Usage:
  python3 scripts/sync.py           # apply
  python3 scripts/sync.py --check   # plan only
  python3 scripts/sync.py --json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

STATUS_PY = Path(__file__).resolve().parent / "status.py"
AGENTS_SKILLS = Path.home() / ".agents" / "skills"
CANONICAL_SOURCE = "AdirD/agent-shell-hamelech"
APPLY_STATUSES = {"new", "outdated", "untracked", "broken-source"}


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def skills_argv(*parts: str) -> list[str]:
    return ["npm", "exec", "--yes", "--package=skills", "--", "skills", *parts]


def load_catalog(ref: str) -> dict[str, Any]:
    cmd = [sys.executable, str(STATUS_PY), "--json", "--ref", ref]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(err or f"status.py exited {result.returncode}")
    data = json.loads(result.stdout)
    if not isinstance(data, dict):
        raise RuntimeError("status.py --json did not return an object")
    return data


def missing_agents_copy(name: str) -> bool:
    return not (AGENTS_SKILLS / name / "SKILL.md").is_file()


def planned_rows(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in catalog.get("skills") or []:
        if not row.get("on_remote"):
            continue
        name = str(row["name"])
        reason = None
        if row.get("status") in APPLY_STATUSES:
            reason = str(row["status"])
        elif missing_agents_copy(name):
            reason = "missing-agents-copy"
        if reason is None:
            continue
        action = "update" if reason == "outdated" else "add"
        rows.append(
            {
                "name": name,
                "status": row.get("status"),
                "reason": reason,
                "action": action,
                "local_version": row.get("local_version"),
                "remote_version": row.get("remote_version"),
            }
        )
    return rows


def run_skills(args: list[str], timeout: float) -> dict[str, Any]:
    cmd = skills_argv(*args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            cwd=str(Path.home()),
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "cmd": cmd, "error": f"timed out after {timeout}s"}
    except FileNotFoundError:
        return {"ok": False, "cmd": cmd, "error": "npm not found on PATH"}
    ok = result.returncode == 0
    return {
        "ok": ok,
        "cmd": cmd,
        "exit_code": result.returncode,
        "stdout": (result.stdout or "").strip(),
        "stderr": (result.stderr or "").strip(),
    }


def apply_row(plan: dict[str, Any], timeout: float) -> dict[str, Any]:
    name = plan["name"]
    steps: list[dict[str, Any]] = []
    if plan["action"] == "update":
        steps.append(run_skills(["update", name, "-g", "-y"], timeout))
    steps.append(
        run_skills(
            [
                "add",
                CANONICAL_SOURCE,
                "--skill",
                name,
                "-g",
                "-y",
                "-a",
                "*",
            ],
            timeout,
        )
    )
    ok = all(step.get("ok") for step in steps)
    return {**plan, "ok": ok, "steps": steps}


def print_human(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    print(
        f"sync-melech-skills  remote={payload['remote']}  "
        f"planned={summary['planned']}  applied={summary['applied']}  "
        f"failed={summary['failed']}"
    )
    if payload.get("check"):
        print("check only — no installs")
    for item in payload.get("results") or []:
        mark = "ok" if item.get("ok", True) else "FAIL"
        print(
            f"  [{mark}] {item['action']} {item['name']}  "
            f"({item['reason']})"
        )
    if summary.get("failed"):
        print("some skills failed; see results")
    elif summary["planned"] == 0:
        print("global ~/.agents/skills already has every remote melech skill")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Globally install/update all remote melech skills"
    )
    parser.add_argument("--check", action="store_true", help="plan only")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--ref", default="main")
    parser.add_argument(
        "--timeout",
        type=float,
        default=180.0,
        help="seconds per skills CLI call",
    )
    args = parser.parse_args()

    if shutil.which("npm") is None:
        eprint("npm not found on PATH; install Node.js to run the skills CLI")
        return 2

    catalog = load_catalog(args.ref)
    plan = planned_rows(catalog)
    results: list[dict[str, Any]]
    if args.check:
        results = [{**item, "ok": True} for item in plan]
    else:
        results = [apply_row(item, args.timeout) for item in plan]

    failed = sum(1 for item in results if not item.get("ok"))
    payload = {
        "ok": failed == 0,
        "check": args.check,
        "remote": catalog.get("remote"),
        "ref": args.ref,
        "scope": "global",
        "agents": "*",
        "lock": str(Path.home() / ".agents" / ".skill-lock.json"),
        "agents_skills": str(AGENTS_SKILLS),
        "summary": {
            "remote_skills": (catalog.get("summary") or {}).get("remote_skills"),
            "planned": len(plan),
            "applied": 0 if args.check else len(results) - failed,
            "failed": 0 if args.check else failed,
        },
        "results": results,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_human(payload)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
