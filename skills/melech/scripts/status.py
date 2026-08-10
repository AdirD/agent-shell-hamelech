#!/usr/bin/env python3
"""Remote-first catalog for AdirD/agent-shell-hamelech vs local installs.

For every skill on GitHub main (plus any orphan local lock entries), shows:
  name, description, installed, where (global/project + agents), local/remote
  version, update available, and the install/update command.

Also lists workflow bundles from the remote README (journey recipes that
chain skills), with per-step install readiness.

Versions are the skill-folder tree SHAs the Skills CLI stores in
~/.agents/.skill-lock.json. Install locations come from `npx skills list`
(global + project). Dry-run only — never installs or updates.

Requires: Python 3.9+, and either `gh` (preferred) or network via urllib.
Optional: `npx` / skills CLI for where/agents (falls back to path probes).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

CANONICAL_SOURCE = "AdirD/agent-shell-hamelech"
CANONICAL_URL = f"https://github.com/{CANONICAL_SOURCE}.git"
TYPO_SOURCE = "AdirD/agent-shel-hamelech"
DEFAULT_REF = "main"
DEFAULT_LOCK = Path.home() / ".agents" / ".skill-lock.json"
MELECH_SOURCE_RE = re.compile(
    r"(?i)(?:^|/)AdirD/agent-shel+l?-hamelech(?:\.git)?$"
)


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def run_json(cmd: list[str]) -> Any | None:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def parse_leading_json(raw: str) -> Any | None:
    """Decode the first JSON value; ignore trailing CLI junk."""
    start = -1
    for i, ch in enumerate(raw):
        if ch in "[{":
            start = i
            break
    if start < 0:
        return None
    try:
        data, _ = json.JSONDecoder().raw_decode(raw, start)
        return data
    except json.JSONDecodeError:
        return None


AGENT_DIR_MARKERS = (
    "/.agents/skills/",
    "/.cursor/skills/",
    "/.claude/skills/",
    "/.codex/skills/",
    "/.config/agents/skills/",
    "/.gemini/skills/",
    "/.copilot/skills/",
    "/.factory/skills/",
    "/.windsurf/skills/",
    "/.codeium/windsurf/skills/",
    "/.continue/skills/",
    "/.goose/skills/",
)


def classify_install_scope(scope: str | None, path: str) -> str:
    """Map CLI scope + path to: global | project | workspace."""
    norm = path.replace("\\", "/")
    if scope == "global":
        return "global"
    # Real project installs live under an agent skills dir
    if any(marker in norm for marker in AGENT_DIR_MARKERS):
        return "project" if scope == "project" else (scope or "project")
    # Bare skills/<name> under a repo checkout — discovery, not npx install
    if re.search(r"/skills/[^/]+/?$", norm) and "/.agents/" not in norm:
        return "workspace"
    return scope or "project"


def shorten_path(path: str) -> str:
    home = str(Path.home())
    if path.startswith(home + "/"):
        return "~/" + path[len(home) + 1 :]
    cwd = str(Path.cwd())
    if path.startswith(cwd + "/"):
        return "./" + path[len(cwd) + 1 :]
    return path


def skills_cli_list(global_scope: bool, cwd: Path | None = None) -> list[dict[str, Any]]:
    args = [
        "npm",
        "exec",
        "--yes",
        "--package=skills",
        "--",
        "skills",
        "list",
        *(["-g"] if global_scope else []),
        "--json",
    ]
    try:
        out = subprocess.check_output(
            args,
            stderr=subprocess.DEVNULL,
            text=True,
            cwd=str(cwd) if cwd else None,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    data = parse_leading_json(out)
    return data if isinstance(data, list) else []


def probe_install_paths(name: str, cwd: Path) -> list[dict[str, Any]]:
    """Filesystem fallback when skills CLI list is unavailable."""
    candidates: list[tuple[str, Path]] = [
        ("global", Path.home() / ".agents" / "skills" / name),
        ("global", Path.home() / ".cursor" / "skills" / name),
        ("global", Path.home() / ".claude" / "skills" / name),
        ("global", Path.home() / ".codex" / "skills" / name),
        ("project", cwd / ".agents" / "skills" / name),
        ("project", cwd / ".cursor" / "skills" / name),
        ("project", cwd / ".claude" / "skills" / name),
        ("workspace", cwd / "skills" / name),
    ]
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for scope, path in candidates:
        if not (path / "SKILL.md").is_file():
            continue
        resolved = str(path.resolve())
        if resolved in seen:
            continue
        seen.add(resolved)
        home_agent = path.parent.parent.name if path.parent.name == "skills" else ""
        agent_map = {
            ".agents": "shared (.agents)",
            ".cursor": "Cursor",
            ".claude": "Claude Code",
            ".codex": "Codex",
        }
        if scope == "workspace":
            agents = ["workspace checkout"]
        elif home_agent in agent_map:
            agents = [agent_map[home_agent]]
        else:
            agents = []
        found.append(
            {
                "scope": scope,
                "path": resolved,
                "agents": agents,
                "source": None,
            }
        )
    return found


def load_installs(cwd: Path) -> dict[str, list[dict[str, Any]]]:
    """name -> list of install locations (global / project / workspace)."""
    by_name: dict[str, list[dict[str, Any]]] = {}

    def add(entry: dict[str, Any]) -> None:
        name = entry.get("name")
        path = entry.get("path") or ""
        if not name or not path:
            return
        scope = classify_install_scope(entry.get("scope"), path)
        loc = {
            "scope": scope,
            "path": str(Path(path).expanduser().resolve()) if path else path,
            "agents": list(entry.get("agents") or []),
            "source": entry.get("source"),
        }
        bucket = by_name.setdefault(name, [])
        # dedupe by scope+path
        key = (loc["scope"], loc["path"])
        if any((b["scope"], b["path"]) == key for b in bucket):
            # merge agents
            for b in bucket:
                if (b["scope"], b["path"]) == key:
                    for a in loc["agents"]:
                        if a not in b["agents"]:
                            b["agents"].append(a)
                    if not b.get("source") and loc.get("source"):
                        b["source"] = loc["source"]
            return
        bucket.append(loc)

    for entry in skills_cli_list(True, cwd):
        add(entry)
    for entry in skills_cli_list(False, cwd):
        add(entry)
    return by_name


def format_where(installs: list[dict[str, Any]]) -> str:
    if not installs:
        return "—"
    parts: list[str] = []
    for loc in installs:
        agents = ", ".join(loc.get("agents") or []) or "unknown agents"
        parts.append(f"{loc['scope']} → {agents} @ {shorten_path(loc['path'])}")
    return "; ".join(parts)


def attach_installs(
    rows: list[dict[str, Any]],
    installs_by_name: dict[str, list[dict[str, Any]]],
    cwd: Path,
) -> None:
    for r in rows:
        name = r["name"]
        locs = list(installs_by_name.get(name) or [])
        if not locs:
            locs = probe_install_paths(name, cwd)
        order = {"global": 0, "project": 1, "workspace": 2}
        locs.sort(key=lambda x: (order.get(x["scope"], 9), x["path"]))
        r["installs"] = locs
        r["where"] = format_where(locs)
        r["installed_global"] = any(x["scope"] == "global" for x in locs)
        r["installed_project"] = any(x["scope"] == "project" for x in locs)
        r["visible_somewhere"] = bool(locs)


def http_get_text(url: str) -> str | None:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github.raw+json, text/plain",
            "User-Agent": "melech-status",
        },
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None


def fetch_repo_tree(owner_repo: str, ref: str) -> dict[str, Any] | None:
    api = f"repos/{owner_repo}/git/trees/{ref}?recursive=1"
    data = run_json(["gh", "api", api])
    if data and isinstance(data, dict) and "tree" in data:
        return data

    url = f"https://api.github.com/repos/{owner_repo}/git/trees/{ref}?recursive=1"
    text = http_get_text(url)
    if not text:
        eprint(f"failed to fetch remote tree for {owner_repo}@{ref}")
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as err:
        eprint(f"failed to parse remote tree for {owner_repo}@{ref}: {err}")
        return None


def parse_frontmatter(text: str) -> dict[str, str]:
    """Minimal YAML-ish frontmatter reader for name/description only."""
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    block = parts[1]
    out: dict[str, str] = {}
    key: str | None = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal key, buf
        if key is None:
            return
        raw = "\n".join(buf).strip()
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
            raw = raw[1:-1]
        out[key] = " ".join(raw.split())
        key = None
        buf = []

    for line in block.splitlines():
        if key and (line.startswith("  ") or line.startswith("\t")):
            buf.append(line.strip())
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            if key:
                buf.append(line.strip())
            continue
        flush()
        key = m.group(1)
        val = m.group(2).strip()
        if val in (">", ">-", "|", "|-"):
            buf = []
        else:
            buf = [val] if val else []
    flush()
    return out


def fetch_repo_file(owner_repo: str, ref: str, path: str) -> str | None:
    try:
        out = subprocess.check_output(
            [
                "gh",
                "api",
                f"repos/{owner_repo}/contents/{path}?ref={ref}",
                "-H",
                "Accept: application/vnd.github.raw",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if out:
            return out
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return http_get_text(
        f"https://raw.githubusercontent.com/{owner_repo}/{ref}/{path}"
    )


def fetch_skill_md(owner_repo: str, ref: str, name: str) -> str | None:
    return fetch_repo_file(owner_repo, ref, f"skills/{name}/SKILL.md")


def parse_workflow_bundles(readme: str) -> tuple[str, list[dict[str, Any]]]:
    """Extract ## Workflow bundles from README → (intro, bundles)."""
    if not readme:
        return "", []
    m = re.search(r"(?m)^## Workflow bundles\s*$", readme)
    if not m:
        return "", []
    rest = readme[m.end() :]
    # Stop at next top-level ##, a --- rule, or the per-skill ### `name` catalog
    end = re.search(r"(?m)^(?:## |---\s*$|### `)", rest)
    section = rest[: end.start()] if end else rest

    intro_lines: list[str] = []
    bundles: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    in_flow = False
    flow_buf: list[str] = []
    use_buf: list[str] = []

    def flush() -> None:
        nonlocal current, in_flow, flow_buf, use_buf
        if not current:
            return
        current["flow"] = " ".join(" ".join(flow_buf).split())
        current["use_when"] = " ".join(" ".join(use_buf).split())
        bundles.append(current)
        current = None
        in_flow = False
        flow_buf = []
        use_buf = []

    for line in section.splitlines():
        if re.match(r"^### ", line):
            flush()
            current = {"name": line[4:].strip(), "flow": "", "use_when": ""}
            continue
        if current is None:
            if line.strip():
                intro_lines.append(line.strip())
            continue
        if line.strip().startswith("```"):
            in_flow = not in_flow
            continue
        if in_flow:
            if line.strip():
                flow_buf.append(line.strip())
            continue
        if line.strip().lower().startswith("use when"):
            use_buf.append(re.sub(r"(?i)^use when\s*", "", line.strip()))
            continue
        if line.strip() and not line.startswith("#"):
            use_buf.append(line.strip())

    flush()
    return " ".join(intro_lines), bundles


def skills_in_flow(flow: str, known: set[str]) -> list[str]:
    """Return known skill names in flow order."""
    hits: list[tuple[int, str]] = []
    for name in known:
        for match in re.finditer(
            rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])", flow
        ):
            hits.append((match.start(), name))
            break
    hits.sort()
    return [name for _, name in hits]


def annotate_bundles(
    bundles: list[dict[str, Any]], rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_name = {r["name"]: r for r in rows}
    known = set(by_name)
    out: list[dict[str, Any]] = []
    for b in bundles:
        skills = skills_in_flow(b.get("flow") or "", known)
        steps = []
        for name in skills:
            row = by_name[name]
            steps.append(
                {
                    "name": name,
                    "installed": bool(row.get("installed")),
                    "status": row.get("status"),
                    "command": row.get("command"),
                }
            )
        missing = [s["name"] for s in steps if not s["installed"]]
        out.append(
            {
                "name": b["name"],
                "flow": b.get("flow") or "",
                "use_when": b.get("use_when") or "",
                "skills": skills,
                "steps": steps,
                "ready": len(missing) == 0 and bool(steps),
                "missing": missing,
            }
        )
    return out


def remote_skills(tree: dict[str, Any]) -> dict[str, dict[str, str]]:
    folders: dict[str, str] = {}
    skill_md_paths: set[str] = set()
    for entry in tree.get("tree") or []:
        path = entry.get("path") or ""
        etype = entry.get("type")
        if etype == "tree" and re.fullmatch(r"skills/[^/]+", path):
            folders[path.split("/", 1)[1]] = entry.get("sha") or ""
        elif etype == "blob" and re.fullmatch(r"skills/[^/]+/SKILL\.md", path):
            skill_md_paths.add(path.split("/")[1])

    out: dict[str, dict[str, str]] = {}
    for name, sha in sorted(folders.items()):
        if name not in skill_md_paths:
            continue
        out[name] = {
            "folder_sha": sha,
            "skill_path": f"skills/{name}/SKILL.md",
        }
    return out


def enrich_descriptions(
    owner_repo: str, ref: str, remote: dict[str, dict[str, str]]
) -> None:
    names = list(remote)

    def one(name: str) -> tuple[str, str]:
        text = fetch_skill_md(owner_repo, ref, name)
        if not text:
            return name, ""
        meta = parse_frontmatter(text)
        return name, meta.get("description") or ""

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for name, desc in pool.map(one, names):
            remote[name]["description"] = desc


def is_melech_source(source: str | None, source_url: str | None) -> bool:
    for candidate in (source or "", source_url or ""):
        cleaned = candidate.strip()
        if not cleaned:
            continue
        cleaned = re.sub(r"^https?://github\.com/", "", cleaned)
        cleaned = re.sub(r"^git@github\.com:", "", cleaned)
        cleaned = cleaned.removesuffix(".git")
        if MELECH_SOURCE_RE.search(cleaned) or cleaned.endswith(
            "agent-shell-hamelech"
        ) or cleaned.endswith("agent-shel-hamelech"):
            return True
        if "hamelech" in cleaned.lower() and "adird" in cleaned.lower():
            return True
    return False


def source_is_typo(source: str | None, source_url: str | None) -> bool:
    blob = f"{source or ''} {source_url or ''}".lower()
    return "agent-shel-hamelech" in blob and "agent-shell-hamelech" not in blob


def load_lock(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"version": 0, "skills": {}}
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as err:
        eprint(f"failed to read lock {path}: {err}")
        return {"version": 0, "skills": {}}


def local_melech(lock: dict[str, Any]) -> dict[str, dict[str, Any]]:
    skills = lock.get("skills") or {}
    out: dict[str, dict[str, Any]] = {}
    for name, entry in skills.items():
        if not isinstance(entry, dict):
            continue
        if is_melech_source(entry.get("source"), entry.get("sourceUrl")):
            out[name] = entry
    return out


def classify(
    name: str,
    remote: dict[str, dict[str, str]],
    local: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    rem = remote.get(name)
    loc = local.get(name)
    description = (rem or {}).get("description") or ""

    # Remote-only = new skill the user does not have yet
    if rem and not loc:
        return {
            "name": name,
            "description": description,
            "on_remote": True,
            "installed": False,
            "update_available": False,
            "status": "new",
            "local_version": None,
            "remote_version": rem["folder_sha"],
            "source": None,
            "skill_path": rem["skill_path"],
            "action": f"npx skills add {CANONICAL_SOURCE} --skill {name} -g -y",
            "note": "on remote, not installed locally",
        }

    # Local orphan — was installed, gone from remote catalog
    if loc and not rem:
        return {
            "name": name,
            "description": description or "(not on remote)",
            "on_remote": False,
            "installed": True,
            "update_available": False,
            "status": "remote-gone",
            "local_version": loc.get("skillFolderHash"),
            "remote_version": None,
            "source": loc.get("source"),
            "skill_path": loc.get("skillPath"),
            "action": f"npx skills remove {name} -g -y",
            "note": "installed locally, not on remote main",
        }

    assert rem is not None and loc is not None
    typo = source_is_typo(loc.get("source"), loc.get("sourceUrl"))
    local_sha = loc.get("skillFolderHash") or ""
    remote_sha = rem["folder_sha"]
    content_matches = bool(local_sha) and local_sha == remote_sha

    base = {
        "name": name,
        "description": description,
        "on_remote": True,
        "installed": True,
        "local_version": local_sha or None,
        "remote_version": remote_sha,
        "source": loc.get("source"),
        "skill_path": loc.get("skillPath") or rem["skill_path"],
    }

    if typo:
        return {
            **base,
            "update_available": not content_matches,
            "status": "broken-source",
            "action": f"npx skills add {CANONICAL_SOURCE} --skill {name} -g -y",
            "note": (
                f"lock source is typo {TYPO_SOURCE!r}; reinstall with "
                f"{CANONICAL_SOURCE!r}"
            ),
            "content_matches": content_matches,
        }

    if not local_sha:
        return {
            **base,
            "update_available": True,
            "status": "untracked",
            "action": f"npx skills add {CANONICAL_SOURCE} --skill {name} -g -y",
            "note": "no local version hash — reinstall to track updates",
        }

    if content_matches:
        return {
            **base,
            "update_available": False,
            "status": "current",
            "action": None,
            "note": "local matches remote",
        }

    return {
        **base,
        "update_available": True,
        "status": "outdated",
        "action": f"npx skills update {name} -g -y",
        "note": "remote version differs from local",
    }


def short(sha: str | None) -> str:
    if not sha:
        return "-"
    return sha[:10]


def yn(flag: bool) -> str:
    return "Y" if flag else "N"


def command_for(row: dict[str, Any]) -> str:
    """Always-present install/update/noop command for agents to execute on request."""
    if row.get("action"):
        return str(row["action"])
    name = row["name"]
    if row.get("on_remote"):
        # current — still give a reinstall path if the user asks to reinstall
        return f"npx skills add {CANONICAL_SOURCE} --skill {name} -g -y"
    return f"npx skills remove {name} -g -y"


def print_bundles(
    intro: str, bundles: list[dict[str, Any]], rows: list[dict[str, Any]]
) -> None:
    if not bundles:
        return
    print()
    print("workflow bundles (journey recipes, not extra skills):")
    if intro:
        print(f"  {intro}")
    print()
    by_name = {r["name"]: r for r in rows}
    for b in bundles:
        ready_tag = "READY" if b.get("ready") else "MISSING STEPS"
        print(f"• {b['name']}  [{ready_tag}]")
        print(f"  {b.get('flow') or '(no flow)'}")
        if b.get("use_when"):
            print(f"  use when: {b['use_when']}")
        step_bits = []
        for step in b.get("steps") or []:
            mark = "✓" if step.get("installed") else "✗"
            step_bits.append(f"{step['name']} {mark}")
        if step_bits:
            print(f"  steps: {' | '.join(step_bits)}")
        missing = b.get("missing") or []
        if missing:
            cmds = []
            for name in missing:
                cmd = (by_name.get(name) or {}).get("command")
                if cmd:
                    cmds.append(cmd)
            if cmds:
                print("  install missing:")
                for cmd in cmds:
                    print(f"    {cmd}")
        print()


def print_human(
    rows: list[dict[str, Any]],
    *,
    ref: str,
    source: str,
    bundle_intro: str = "",
    bundles: list[dict[str, Any]] | None = None,
) -> None:
    # Remote-first: all on_remote skills A–Z, then orphans
    remote_rows = [r for r in rows if r.get("on_remote")]
    orphan_rows = [r for r in rows if not r.get("on_remote")]
    remote_rows.sort(key=lambda r: r["name"])
    orphan_rows.sort(key=lambda r: r["name"])

    new_count = sum(1 for r in remote_rows if r["status"] == "new")
    outdated_count = sum(1 for r in remote_rows if r["update_available"])
    installed_count = sum(1 for r in remote_rows if r["installed"])
    broken = sum(1 for r in remote_rows if r["status"] == "broken-source")

    print(f"melech catalog — remote {source}@{ref}  →  local lock")
    print(
        f"remote skills: {len(remote_rows)}  |  installed: {installed_count}  |  "
        f"new on remote: {new_count}  |  updates available: {outdated_count}"
        + (f"  |  broken-source: {broken}" if broken else "")
    )
    if orphan_rows:
        print(f"local-only (not on remote): {len(orphan_rows)}")
    print()

    for r in remote_rows:
        flag = []
        if r["status"] == "new":
            flag.append("NEW")
        if r["update_available"]:
            flag.append("UPDATE")
        if r["status"] == "broken-source":
            flag.append("BROKEN-SOURCE")
        badge = f"  [{', '.join(flag)}]" if flag else ""
        cmd = command_for(r)
        print(f"• {r['name']}{badge}")
        print(f"  {r.get('description') or '(no description)'}")
        print(
            f"  installed: {yn(r['installed'])}   "
            f"update: {yn(bool(r['update_available']))}   "
            f"local: {short(r.get('local_version'))}   "
            f"remote: {short(r.get('remote_version'))}"
        )
        print(f"  where: {r.get('where') or '—'}")
        print(f"  command: {cmd}")
        if r.get("note") and r["status"] != "current":
            print(f"  note: {r['note']}")
        print()

    if orphan_rows:
        print("local-only (not on remote):")
        for r in orphan_rows:
            print(
                f"• {r['name']}  installed: Y  local: {short(r.get('local_version'))}"
            )
            print(f"  where: {r.get('where') or '—'}")
            print(f"  command: {command_for(r)}")
            if r.get("note"):
                print(f"  note: {r['note']}")
        print()

    print("matrix:")
    print(
        f"{'NAME':<20} {'INST':<5} {'UPD':<4} {'LOCAL':<11} {'REMOTE':<11} WHERE"
    )
    print("-" * 120)
    for r in remote_rows + orphan_rows:
        where = r.get("where") or "—"
        # keep matrix readable — agents only, paths are in the cards
        short_where = where
        if " @ " in where:
            short_where = "; ".join(
                part.split(" @ ", 1)[0] for part in where.split("; ")
            )
        print(
            f"{r['name']:<20} {yn(r['installed']):<5} "
            f"{yn(bool(r['update_available'])):<4} "
            f"{short(r.get('local_version')):<11} "
            f"{short(r.get('remote_version')):<11} "
            f"{short_where}"
        )

    print_bundles(bundle_intro, bundles or [], rows)

    print("notes:")
    print(
        "  - versions are skill-folder git tree SHAs (same as the skills CLI lock),"
        " not semver"
    )
    print(
        "  - where: `global` = user-level npx install; `project` = this repo's"
        " agent dirs; `workspace` = bare skills/ checkout discovery (not an install)"
    )
    print(
        "  - each card's `command` is what to run when the user asks to"
        " install/update that skill; do not run until asked"
    )
    print(
        "  - workflow bundles come from the remote README; they chain skills,"
        " they are not installable packages"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remote-first catalog: melech skills vs local installs"
    )
    parser.add_argument(
        "--ref",
        default=DEFAULT_REF,
        help=f"git ref to compare against (default: {DEFAULT_REF})",
    )
    parser.add_argument(
        "--lock",
        type=Path,
        default=DEFAULT_LOCK,
        help=f"path to skills lock (default: {DEFAULT_LOCK})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="machine-readable JSON output",
    )
    parser.add_argument(
        "--source",
        default=CANONICAL_SOURCE,
        help=f"GitHub owner/repo (default: {CANONICAL_SOURCE})",
    )
    parser.add_argument(
        "--no-descriptions",
        action="store_true",
        help="skip fetching SKILL.md descriptions (faster)",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        default=Path.cwd(),
        help="project directory for project-level skills list (default: cwd)",
    )
    args = parser.parse_args()
    cwd = args.cwd.expanduser().resolve()

    tree = fetch_repo_tree(args.source, args.ref)
    if not tree:
        eprint("could not load remote skill tree")
        return 2

    remote = remote_skills(tree)
    if not args.no_descriptions:
        enrich_descriptions(args.source, args.ref, remote)

    readme = fetch_repo_file(args.source, args.ref, "README.md") or ""
    # Prefer local README when running inside this checkout (unpushed edits)
    local_readme = cwd / "README.md"
    if local_readme.is_file() and (cwd / "skills" / "melech").is_dir():
        try:
            readme = local_readme.read_text()
        except OSError:
            pass
    bundle_intro, raw_bundles = parse_workflow_bundles(readme)

    lock = load_lock(args.lock)
    local = local_melech(lock)
    installs_by_name = load_installs(cwd)
    # Remote-first ordering for classify list, then orphans
    names = sorted(remote) + sorted(set(local) - set(remote))
    rows = [classify(name, remote, local) for name in names]
    attach_installs(rows, installs_by_name, cwd)
    for r in rows:
        r["command"] = command_for(r)
    bundles = annotate_bundles(raw_bundles, rows)

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    payload = {
        "remote": args.source,
        "ref": args.ref,
        "canonical_url": CANONICAL_URL,
        "lock": str(args.lock),
        "cwd": str(cwd),
        "summary": {
            "remote_skills": sum(1 for r in rows if r["on_remote"]),
            "installed": sum(1 for r in rows if r["installed"] and r["on_remote"]),
            "installed_global": sum(
                1 for r in rows if r.get("installed_global") and r["on_remote"]
            ),
            "installed_project": sum(
                1 for r in rows if r.get("installed_project") and r["on_remote"]
            ),
            "new_on_remote": sum(1 for r in rows if r["status"] == "new"),
            "updates_available": sum(
                1 for r in rows if r["update_available"] and r["on_remote"]
            ),
            "broken_source": sum(1 for r in rows if r["status"] == "broken-source"),
            "workflow_bundles": len(bundles),
            "workflow_bundles_ready": sum(1 for b in bundles if b.get("ready")),
        },
        "skills": rows,
        "workflow_bundles_intro": bundle_intro,
        "workflow_bundles": bundles,
        "counts": counts,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_human(
            rows,
            ref=args.ref,
            source=args.source,
            bundle_intro=bundle_intro,
            bundles=bundles,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
