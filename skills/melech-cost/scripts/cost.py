#!/usr/bin/env python3
"""Estimate coding-agent spend for every worktree of the current git repository."""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

DEFAULT_CARDS = 8
TOP_SESSIONS = 3
FOCUS_SESSIONS = 10
TOPIC_MAX_CHARS = 80


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


PRICES = json.loads((skill_dir() / "references" / "prices.json").read_text(encoding="utf-8"))
REPLAY = PRICES["cursor_replay"]
CPT = float(REPLAY["chars_per_token"])


# ---------------------------------------------------------------- pricing


def price(model: Optional[str]) -> dict[str, Any]:
    m = (model or "").lower()
    for rule in PRICES["rules"]:
        if all(part in m for part in rule["match"]):
            mult = rule.get("fast_multiplier", 1) if "fast" in m else 1
            return {
                "input": rule["input"] * mult,
                "cache_write": (rule.get("cache_write") or rule["input"]) * mult,
                "cache_read": rule["cache_read"] * mult,
                "output": rule["output"] * mult,
                "pool": rule.get("pool", "third_party"),
            }
    fb = PRICES["fallback"]
    return {**fb, "cache_write": fb.get("cache_write") or fb["input"]}


def long_context_multiplier(model: Optional[str], prompt_tokens: float) -> float:
    m = (model or "").lower()
    for rule in PRICES["long_context"]:
        if all(part in m for part in rule["match"]) and prompt_tokens > rule["above_tokens"]:
            return rule["multiplier"]
    return 1.0


def family(model: Optional[str]) -> str:
    m = (model or "").lower()
    if any(k in m for k in ("claude", "opus", "sonnet", "haiku", "fable")):
        return "claude"
    for k in ("gpt", "composer", "grok"):
        if k in m:
            return k
    return "other"


# ---------------------------------------------------------------- scope


@dataclass
class Scope:
    repo: str
    main: Path
    roots: dict[Path, str]
    containers: set[Path]
    known: list[tuple[str, Path, str]] = field(default_factory=list)

    def label_for_path(self, raw: str) -> Optional[str]:
        if not raw:
            return None
        for candidate in {Path(raw), Path(os.path.realpath(raw))}:
            for root in sorted(self.roots, key=lambda p: len(str(p)), reverse=True):
                if candidate == root or root in candidate.parents:
                    return self.roots[root]
            for container in self.containers:
                if container in candidate.parents:
                    name = candidate.relative_to(container).parts[0]
                    return name if (container / name).exists() else f"{name} (removed)"
        return None

    def label_for_slug(self, slug: str) -> Optional[str]:
        best: Optional[tuple[str, Path, str]] = None
        for entry in self.known:
            s = entry[0]
            if (slug == s or slug.startswith(s + "-")) and (best is None or len(s) > len(best[0])):
                best = entry
        if best is None:
            return None
        s, path, kind = best
        if kind == "root":
            return self.roots[path]
        if kind == "container":
            rest = slug[len(s) + 1 :]
            if not rest:
                return None
            return rest if (path / rest).exists() else f"{rest} (removed)"
        return None


def path_slug(path: Path | str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", str(path)).strip("-")


def git_worktrees(cwd: Path) -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=cwd, capture_output=True, text=True, check=False,
        ).stdout
    except OSError:
        return []
    return [Path(line[len("worktree ") :]) for line in out.splitlines() if line.startswith("worktree ")]


def exclusive_container(parent: Path, roots: dict[Path, str]) -> bool:
    """A folder only counts as this repo's worktree home if it holds no other repo's checkout."""
    main = next(r for r, label in roots.items() if label == "main")
    try:
        children = [Path(os.path.realpath(c)) for c in parent.iterdir() if c.is_dir()]
    except OSError:
        return False
    for child in children:
        marker = child / ".git"
        if child in roots or not marker.exists():
            continue
        if marker.is_dir():
            return False
        try:
            gitdir = marker.read_text(encoding="utf-8").strip()
        except OSError:
            return False
        if str(main / ".git") not in os.path.realpath(gitdir.removeprefix("gitdir:").strip()):
            return False
    return True


def build_scope(cwd: Path) -> Optional[Scope]:
    paths = git_worktrees(cwd)
    if not paths:
        return None
    main = Path(os.path.realpath(paths[0]))
    repo = main.name
    roots: dict[Path, str] = {main: "main"}
    for p in paths[1:]:
        real = Path(os.path.realpath(p))
        roots[real] = real.parent.name if real.name == repo else real.name
    containers = {
        parent for parent in {r.parent for r in roots if r != main}
        if parent not in (main.parent, Path.home()) and exclusive_container(parent, roots)
    }
    known: list[tuple[str, Path, str]] = []
    for root in roots:
        known.append((path_slug(root), root, "root"))
    for c in containers:
        known.append((path_slug(c), c, "container"))
    for parent in {r.parent for r in roots} | {c.parent for c in containers}:
        try:
            siblings = [d for d in parent.iterdir() if d.is_dir()]
        except OSError:
            continue
        for d in siblings:
            real = Path(os.path.realpath(d))
            if real not in roots and real not in containers:
                known.append((path_slug(real), real, "other"))
    return Scope(repo=repo, main=main, roots=roots, containers=containers, known=known)


# ---------------------------------------------------------------- text helpers


def clean_user_text(text: str) -> str:
    queries = re.findall(r"<user_query>\s*(.*?)\s*</user_query>", text, re.DOTALL | re.I)
    if queries:
        text = " ".join(queries)
    text = re.sub(r"<(timestamp|system_reminder|system-reminder)>.*?</\1>", " ", text, flags=re.DOTALL | re.I)
    return re.sub(r"\s+", " ", text).strip()


def topic_of(messages: list[str]) -> str:
    generic = re.compile(r"^(?:hi|hello|hey|ok(?:ay)?|thanks?|yes|no|continue)\W*$", re.I)
    source = next((m for m in messages if m and not generic.fullmatch(m)), messages[0] if messages else "")
    first = re.split(r"(?<=[.!?])\s+", source, maxsplit=1)[0]
    return shorten(first, TOPIC_MAX_CHARS)


def shorten(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def chars_of(value: Any) -> int:
    if value is None:
        return 0
    return len(value) if isinstance(value, str) else len(json.dumps(value, ensure_ascii=False))


def age_label(seconds: float) -> str:
    s = max(0, int(seconds))
    if s < 3600:
        return f"{s // 60}m ago"
    if s < 48 * 3600:
        return f"{s // 3600}h ago"
    return f"{s // 86400}d ago"


def new_session(provider: str, sid: str, worktree: str, **extra: Any) -> dict[str, Any]:
    return {
        "provider": provider, "sid": sid, "worktree": worktree, "parent": None, "topic": "",
        "first": 0.0, "last": 0.0, "model": None, "cost": 0.0, "input_new": 0.0,
        "input_cached": 0.0, "output": 0.0, "calls": 0, "exact": False, **extra,
    }


# ---------------------------------------------------------------- Claude Code


def claude_sessions(home: Path, scope: Scope) -> Iterable[dict[str, Any]]:
    root = Path(os.environ.get("CLAUDE_CONFIG_DIR") or home / ".claude") / "projects"
    for path in root.glob("**/*.jsonl"):
        s: Optional[dict[str, Any]] = None
        seen: set[str] = set()
        users: list[str] = []
        models: collections.Counter[str] = collections.Counter()
        try:
            handle = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with handle:
            for line in handle:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if s is None:
                    label = scope.label_for_path(rec.get("cwd") or "")
                    if not rec.get("cwd"):
                        continue
                    if label is None:
                        break
                    s = new_session("claude", path.stem, label, exact=True)
                    if path.parent.name == "subagents":
                        s["parent"] = path.parent.parent.name
                stamp = parse_iso(rec.get("timestamp"))
                if stamp:
                    s["first"] = s["first"] or stamp
                    s["last"] = max(s["last"], stamp)
                msg = rec.get("message") or {}
                if rec.get("type") == "user" and not rec.get("isMeta"):
                    content = msg.get("content")
                    text = content if isinstance(content, str) else " ".join(
                        c.get("text", "") for c in content or [] if isinstance(c, dict) and c.get("type") == "text"
                    )
                    if text.strip():
                        users.append(clean_user_text(text))
                usage = msg.get("usage")
                if rec.get("type") != "assistant" or not usage:
                    continue
                key = msg.get("id") or rec.get("requestId") or rec.get("uuid")
                if key in seen:
                    continue
                seen.add(key)
                model = msg.get("model") or ""
                if model.startswith("<"):
                    continue
                models[model] += 1
                p = price(model)
                cc = usage.get("cache_creation") or {}
                write_1h = cc.get("ephemeral_1h_input_tokens") or 0
                write_all = usage.get("cache_creation_input_tokens") or 0
                write_5m = max(0, write_all - write_1h)
                fresh = usage.get("input_tokens") or 0
                read = usage.get("cache_read_input_tokens") or 0
                out = usage.get("output_tokens") or 0
                s["cost"] += (fresh * p["input"] + write_5m * p["cache_write"] + write_1h * p["input"] * 2
                              + read * p["cache_read"] + out * p["output"]) / 1e6
                s["input_new"] += fresh + write_all
                s["input_cached"] += read
                s["output"] += out
                s["calls"] += 1
        if s is None or not s["calls"]:
            continue
        s["model"] = models.most_common(1)[0][0] if models else None
        s["topic"] = topic_of(users)
        s["last"] = s["last"] or path.stat().st_mtime
        yield s


def parse_iso(value: Any) -> float:
    if not isinstance(value, str):
        return 0.0
    try:
        return time.mktime(time.strptime(value[:19], "%Y-%m-%dT%H:%M:%S")) - time.timezone
    except ValueError:
        return 0.0


# ---------------------------------------------------------------- Codex


def codex_sessions(home: Path, scope: Scope) -> Iterable[dict[str, Any]]:
    base = Path(os.environ.get("CODEX_HOME") or home / ".codex")
    files = list(base.glob("sessions/**/*.jsonl")) + list(base.glob("archived_sessions/**/*.jsonl"))
    for path in files:
        s: Optional[dict[str, Any]] = None
        totals: Optional[dict[str, Any]] = None
        model: Optional[str] = None
        users: list[str] = []
        try:
            handle = path.open(encoding="utf-8", errors="replace")
        except OSError:
            continue
        with handle:
            for line in handle:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                payload = rec.get("payload") or {}
                kind = rec.get("type")
                if kind == "session_meta" and s is None:
                    label = scope.label_for_path(payload.get("cwd") or "")
                    if label is None:
                        break
                    s = new_session("codex", payload.get("id") or path.stem, label, exact=True)
                if s is None:
                    continue
                stamp = parse_iso(rec.get("timestamp"))
                if stamp:
                    s["first"] = s["first"] or stamp
                    s["last"] = max(s["last"], stamp)
                if kind == "turn_context" and payload.get("model"):
                    model = payload["model"]
                if kind == "event_msg" and payload.get("type") == "user_message":
                    users.append(clean_user_text(payload.get("message") or ""))
                if kind == "response_item" and payload.get("role") == "user":
                    for part in payload.get("content") or []:
                        text = (part.get("text") or "").strip() if isinstance(part, dict) else ""
                        if text and not text.startswith(("<", "# AGENTS.md")):
                            users.append(clean_user_text(text))
                if kind == "event_msg" and payload.get("type") == "token_count":
                    totals = (payload.get("info") or {}).get("total_token_usage") or totals
        if s is None or not totals:
            continue
        p = price(model)
        inp = totals.get("input_tokens") or 0
        cached = totals.get("cached_input_tokens") or 0
        out = totals.get("output_tokens") or 0
        s.update(model=model, topic=topic_of(users), input_new=max(0, inp - cached), input_cached=cached,
                 output=out, calls=1)
        s["cost"] = (s["input_new"] * p["input"] + cached * p["cache_read"] + out * p["output"]) / 1e6
        yield s


# ---------------------------------------------------------------- Cursor


def cursor_ide_db(home: Path) -> Optional[Path]:
    for candidate in (
        home / "Library/Application Support/Cursor/User/globalStorage/state.vscdb",
        home / ".config/Cursor/User/globalStorage/state.vscdb",
        Path(os.environ.get("APPDATA", "")) / "Cursor/User/globalStorage/state.vscdb",
    ):
        if candidate.is_file():
            return candidate
    return None


def parse_cursor_transcript(path: Path) -> tuple[list[tuple[str, int, list[str]]], list[str]]:
    steps: list[tuple[str, int, list[str]]] = []
    users: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        lines = handle.readlines()
    for line in lines:
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (rec.get("message") or {}).get("content") or []
        if rec.get("role") == "user":
            text = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
            steps.append(("user", len(text), []))
            cleaned = clean_user_text(text)
            if cleaned:
                users.append(cleaned)
        elif rec.get("role") == "assistant":
            out, tools = 0, []
            for c in content:
                if not isinstance(c, dict):
                    continue
                if c.get("type") == "tool_use":
                    tools.append(c.get("name"))
                    out += chars_of(c.get("input"))
                else:
                    out += chars_of(c.get("text") or c.get("thinking"))
            steps.append(("asst", out, tools))
    return steps, users


def first_timestamp(path: Path) -> float:
    with path.open(encoding="utf-8", errors="replace") as handle:
        head = handle.read(4000)
    m = re.search(r"<timestamp>\w+, (\w{3}) (\d+), (\d{4})", head)
    if m:
        return time.mktime(time.strptime(" ".join(m.groups()), "%b %d %Y"))
    return path.stat().st_mtime


def load_cli_store(chat_dir: Path, tmp: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, tuple[str, int]]]:
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    for f in chat_dir.glob("store.db*"):
        shutil.copy(f, tmp)
    conn = sqlite3.connect(str(tmp / "store.db"))
    try:
        row = conn.execute("select value from meta where key='0'").fetchone()
        meta = json.loads(bytes.fromhex(row[0]).decode()) if row else {}
        blobs = dict(conn.execute("select id, data from blobs"))
    finally:
        conn.close()
    ordered: list[dict[str, Any]] = []
    root = blobs.get(meta.get("latestRootBlobId"))
    if isinstance(root, bytes):
        for i in range(len(root) - 31):
            ref = root[i : i + 32].hex()
            if ref in blobs:
                msg = safe_json(blobs[ref])
                if isinstance(msg, dict) and msg.get("role"):
                    ordered.append(msg)
    results: dict[str, tuple[str, int]] = {}
    for data in blobs.values():
        msg = safe_json(data)
        if isinstance(msg, dict) and msg.get("role") == "tool" and isinstance(msg.get("content"), list):
            for part in msg["content"]:
                if isinstance(part, dict) and part.get("type") == "tool-result":
                    results[part.get("toolCallId")] = (part.get("toolName"), chars_of(part.get("result")))
    return meta, ordered, results


def safe_json(data: Any) -> Any:
    try:
        return json.loads(data)
    except (TypeError, ValueError):
        return None


def load_ide_composer(db: sqlite3.Connection, sid: str) -> Optional[dict[str, Any]]:
    row = db.execute("select value from cursorDiskKV where key=?", ("composerData:" + sid,)).fetchone()
    if not row:
        return None
    cd = json.loads(row[0])
    order = [h.get("bubbleId") for h in cd.get("fullConversationHeadersOnly") or []]
    bubbles = dict(db.execute(
        "select key, value from cursorDiskKV where key >= ? and key < ?",
        (f"bubbleId:{sid}:", f"bubbleId:{sid};"),
    ).fetchall())
    results: list[int] = []
    models: collections.Counter[str] = collections.Counter()
    for bid in order:
        raw = bubbles.get(f"bubbleId:{sid}:{bid}")
        b = safe_json(raw) if raw else None
        if not isinstance(b, dict):
            continue
        name = (b.get("modelInfo") or {}).get("modelName")
        if name:
            models[name] += 1
        tool = b.get("toolFormerData") or {}
        if tool.get("name"):
            results.append(chars_of(tool.get("result")))
    cats = {c.get("id"): c.get("estimatedTokens") or 0
            for c in (cd.get("promptTokenBreakdown") or {}).get("categories") or []}
    breakdown = None
    if cats.get("conversation"):
        breakdown = {
            "prefix": sum(v for k, v in cats.items() if k not in ("conversation", "summarized_conversation")),
            "conversation": cats["conversation"],
            "summarized": bool(cats.get("summarized_conversation")),
        }
    model = models.most_common(1)[0][0] if models else (cd.get("modelConfig") or {}).get("modelName")
    return {"model": model, "results": results, "breakdown": breakdown,
            "limit": cd.get("contextTokenLimit") or REPLAY["default_context_limit"]}


def replay(events: list[tuple[str, float]], model: Optional[str], prefix: float, limit: float,
           scale: float = 1.0) -> dict[str, float]:
    """Price each model call as cached prior prompt + newly appended context + output.

    `scale` inflates context growth to match Cursor's own context counter; billed output
    stays unscaled because hidden reasoning tokens are not stored locally.
    """
    p = price(model)
    ctx, prev = prefix, 0.0
    r = {"cost": 0.0, "input_new": 0.0, "input_cached": 0.0, "output": 0.0, "calls": 0, "final_ctx": 0.0}
    for kind, chars in events:
        t = chars / CPT
        if kind == "in":
            ctx += t * scale
            continue
        prompt = ctx
        mult = long_context_multiplier(model, prompt)
        cached = min(prev, prompt)
        new = prompt - cached
        r["cost"] += ((cached * p["cache_read"] + new * p["cache_write"]) * mult + t * p["output"]) / 1e6
        r["input_new"] += new
        r["input_cached"] += cached
        r["output"] += t
        r["calls"] += 1
        ctx += t * scale
        prev = prompt
        if ctx > limit:
            r["cost"] += (ctx * p["cache_read"] + REPLAY["summary_output_tokens"] * p["output"]) / 1e6
            ctx = prefix + REPLAY["summary_tokens"]
            prev = prefix
    r["final_ctx"] = ctx
    return r


def cursor_sessions(home: Path, scope: Scope) -> Iterable[dict[str, Any]]:
    projects = home / ".cursor" / "projects"
    chat_dirs = {d.name: d for d in (home / ".cursor" / "chats").glob("*/*") if d.is_dir()}
    db_path = cursor_ide_db(home)
    db = None
    if db_path:
        try:
            db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        except sqlite3.Error:
            db = None
    tmp = Path(tempfile.mkdtemp(prefix="melech-cost-"))
    raw: list[dict[str, Any]] = []
    tool_sizes: collections.defaultdict[str, list[int]] = collections.defaultdict(list)
    try:
        for project in projects.glob("*/agent-transcripts"):
            label = scope.label_for_slug(project.parent.name)
            if label is None:
                continue
            files = list(project.glob("*/*.jsonl")) + list(project.glob("*/subagents/*.jsonl"))
            for path in files:
                sid = path.stem
                steps, users = parse_cursor_transcript(path)
                s = new_session("cursor", sid, label, topic=topic_of(users),
                                first=first_timestamp(path), last=path.stat().st_mtime)
                if path.parent.name == "subagents":
                    s["parent"] = path.parent.parent.name
                s["_steps"] = steps
                s["_limit"] = REPLAY["default_context_limit"]
                n_asst = sum(1 for k, _, _ in steps if k == "asst")
                chat = chat_dirs.get(sid)
                if chat and (chat / "store.db").exists():
                    try:
                        meta, ordered, results = load_cli_store(chat, tmp)
                    except (sqlite3.Error, OSError, ValueError):
                        meta, ordered, results = {}, [], {}
                    s["model"] = meta.get("lastUsedModel")
                    s["parent"] = s["parent"] or (meta.get("subagentInfo") or {}).get("parentAgentId")
                    for name, size in results.values():
                        tool_sizes[name].append(size)
                    root_asst = sum(1 for m in ordered if m.get("role") == "assistant")
                    if ordered and root_asst >= 0.8 * n_asst:
                        s["_mode"] = "cli"
                        s["_system"] = sum(chars_of(m.get("content")) for m in ordered if m.get("role") == "system")
                        s["_events"] = [("call" if m["role"] == "assistant" else "in", chars_of(m.get("content")))
                                        for m in ordered if m.get("role") != "system"]
                    else:
                        s["_mode"] = "cli-partial"
                        s["_by_name"] = results
                elif db is not None:
                    try:
                        ide = load_ide_composer(db, sid)
                    except sqlite3.Error:
                        ide = None
                    if ide:
                        s.update(model=ide["model"], _mode="ide", _seq=ide["results"],
                                 _breakdown=ide["breakdown"], _limit=ide["limit"])
                s.setdefault("_mode", "transcript")
                raw.append(s)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        if db is not None:
            db.close()

    by_sid = {s["sid"]: s for s in raw}
    avg = {k: sum(v) / len(v) for k, v in tool_sizes.items() if v}
    overall = statistics.mean([x for v in tool_sizes.values() for x in v]) if tool_sizes else 4000.0
    for s in raw:
        if not s["model"] and s["parent"] in by_sid:
            s["model"] = by_sid[s["parent"]]["model"]
        if s["_mode"] == "cli":
            continue
        seq = s.get("_seq") or []
        by_name: collections.defaultdict[str, list[int]] = collections.defaultdict(list)
        for name, size in (s.get("_by_name") or {}).values():
            by_name[name].append(size)
        events: list[tuple[str, float]] = []
        k = 0
        for kind, chars, tools in s["_steps"]:
            if kind == "user":
                events.append(("in", chars))
                continue
            events.append(("call", chars))
            total = 0.0
            for name in tools:
                if k < len(seq):
                    total += seq[k]
                    k += 1
                elif by_name.get(name):
                    total += sum(by_name[name]) / len(by_name[name])
                else:
                    total += avg.get(name, overall)
            if total:
                events.append(("in", total))
        s["_events"] = events

    scales = []
    for s in raw:
        b = s.get("_breakdown")
        if b and not b["summarized"]:
            probe = replay(s["_events"], s["model"], b["prefix"], 10**12)
            conv = probe["final_ctx"] - b["prefix"]
            if conv > 5000:
                s["_scale"] = min(REPLAY["max_scale"], max(1.0, b["conversation"] / conv))
                scales.append(s["_scale"])
    default_scale = statistics.median(scales) if len(scales) >= 5 else REPLAY["default_scale"]

    for s in raw:
        fam = family(s["model"])
        b = s.get("_breakdown")
        if s["_mode"] == "cli" and s.get("_system"):
            prefix = s["_system"] / CPT + REPLAY["tool_overhead_tokens"][fam]
            scale = 1.0
        elif b:
            prefix, scale = b["prefix"], s.get("_scale", default_scale)
        else:
            prefix = REPLAY["prefix_tokens"][fam]
            scale = 1.0 if s["_mode"].startswith("cli") else default_scale
        r = replay(s["_events"], s["model"], prefix, s["_limit"], scale)
        r.pop("final_ctx")
        s.update(r)
        for key in [k for k in s if k.startswith("_")]:
            s.pop(key)
        yield s


# ---------------------------------------------------------------- report


def money(x: float) -> str:
    return f"${x:,.0f}" if x >= 10 else f"${x:,.2f}"


def tokens(x: float) -> str:
    if x >= 1e9:
        return f"{x / 1e9:,.1f}B"
    if x >= 1e6:
        return f"{x / 1e6:,.1f}M"
    return f"{x / 1e3:,.0f}k"


def root_session(s: dict[str, Any], by_key: dict[tuple[str, str], dict[str, Any]]) -> dict[str, Any]:
    seen = set()
    while s.get("parent") and (s["provider"], s["parent"]) in by_key and s["sid"] not in seen:
        seen.add(s["sid"])
        s = by_key[(s["provider"], s["parent"])]
    return s


def build_report(scope: Scope, sessions: list[dict[str, Any]], cards: int, focus: Optional[str],
                 now: float) -> tuple[str, str]:
    by_key = {(s["provider"], s["sid"]): s for s in sessions}
    groups: dict[str, dict[str, Any]] = collections.defaultdict(lambda: {
        "cost": 0.0, "sessions": set(), "subs": 0, "models": collections.Counter(),
        "providers": collections.Counter(), "cached": 0.0, "new": 0.0, "out": 0.0, "last": 0.0,
        "top": collections.defaultdict(float),
    })
    months: collections.Counter[str] = collections.Counter()
    providers: collections.Counter[str] = collections.Counter()
    assumed = 0.0
    for s in sessions:
        root = root_session(s, by_key)
        g = groups[root["worktree"]]
        g["cost"] += s["cost"]
        g["cached"] += s["input_cached"]
        g["new"] += s["input_new"]
        g["out"] += s["output"]
        g["models"][s["model"] or "unknown"] += s["cost"]
        g["providers"][s["provider"]] += s["cost"]
        g["last"] = max(g["last"], s["last"])
        g["top"][(root["provider"], root["sid"])] += s["cost"]
        if s is root:
            g["sessions"].add((s["provider"], s["sid"]))
        else:
            g["subs"] += 1
        months[time.strftime("%Y-%m", time.localtime(s["first"] or s["last"]))] += s["cost"]
        providers[s["provider"]] += s["cost"]
        if price(s["model"])["pool"] == "assumed":
            assumed += s["cost"]

    total = sum(g["cost"] for g in groups.values())
    ordered = sorted(groups.items(), key=lambda kv: -kv[1]["cost"])
    if focus:
        ordered = [kv for kv in ordered if kv[0] == focus or kv[0].startswith(focus)]
    firsts = [s["first"] for s in sessions if s["first"]]
    span = (f"{time.strftime('%b %d, %Y', time.localtime(min(firsts)))} → today") if firsts else ""

    head = [f"## `{scope.repo}` agent spend · ~{money(total)}",
            f"{len(sessions):,} sessions across {len(groups)} worktrees · {span}"]
    head.append(" · ".join(f"{p} ~{money(c)}{'' if p == 'cursor' else ' (exact tokens)'}"
                           for p, c in providers.most_common()))
    head.append(" · ".join(f"{m} ~{money(c)}" for m, c in sorted(months.items())[-6:]))
    head.append("")

    def card(name: str, g: dict[str, Any], top_n: int) -> list[str]:
        model, model_cost = g["models"].most_common(1)[0]
        share = model_cost / g["cost"] * 100 if g["cost"] else 0
        read = g["cached"] + g["new"]
        cached_pct = g["cached"] / read * 100 if read else 0
        n = len(g["sessions"])
        subs = f" + {g['subs']} subagents" if g["subs"] else ""
        mix = ", ".join(p for p, _ in g["providers"].most_common())
        lines = [f"### `{name}` · ~{money(g['cost'])}",
                 f"{age_label(now - g['last'])} · {n} session{'s' if n != 1 else ''}{subs} · {mix} · "
                 f"mostly `{model}` ({share:.0f}%)",
                 f"~{tokens(read)} tokens read ({cached_pct:.0f}% cached) · ~{tokens(g['out'])} written", ""]
        for i, (key, cost) in enumerate(sorted(g["top"].items(), key=lambda kv: -kv[1])[:top_n], 1):
            s = by_key[key]
            topic = shorten(s["topic"] or "(no user message)", TOPIC_MAX_CHARS)
            lines.append(f"{i}. `{s['sid'][:8]}` · {s['provider']} · {topic} — ~{money(cost)}")
        lines.append("")
        return lines

    foot = ["_API list-price value from local history; Cursor rows are replay estimates (±30–40%), "
            "Claude Code and Codex rows use logged token counts. Plan-included usage may cover part of it._"]
    if assumed >= 0.01:
        foot.append(f"_~{money(assumed)} is from sessions with an unknown model (e.g. Auto), priced at fallback rates._")

    top_n = FOCUS_SESSIONS if focus else TOP_SESSIONS
    shown = []
    for name, g in ordered[: cards if not focus else len(ordered)]:
        shown += card(name, g, top_n)
    full = []
    for name, g in ordered:
        if g["cost"] >= 0.01:
            full += card(name, g, top_n)
    hidden = len(ordered) - (len(ordered) if focus else min(cards, len(ordered)))
    tail = [f"_{hidden} more worktrees in the full report._"] if hidden > 0 else []
    return "\n".join(head + shown + tail + foot), "\n".join(head + full + foot)


# ---------------------------------------------------------------- cli


def collect(home: Path, scope: Scope, since: float) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for source in (cursor_sessions, claude_sessions, codex_sessions):
        out.extend(s for s in source(home, scope) if s["last"] >= since and s["cost"] > 0)
    return out


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cwd", default=".", help="Any directory inside the repo")
    ap.add_argument("--home", default=None, help="Override home directory (tests)")
    ap.add_argument("--cards", type=int, default=DEFAULT_CARDS, help="Worktree cards to print")
    ap.add_argument("--worktree", default=None, help="Focus one worktree (name or prefix)")
    ap.add_argument("--since", default=None, help="Only sessions active on/after YYYY-MM-DD")
    ap.add_argument("--report", default=None, help="Where to write the full Markdown report")
    ap.add_argument("--json", action="store_true", help="Print per-session JSON instead of Markdown")
    args = ap.parse_args(argv)

    home = Path(args.home).expanduser() if args.home else Path.home()
    scope = build_scope(Path(args.cwd).resolve())
    if scope is None:
        print("melech-cost: not inside a git repository", file=sys.stderr)
        return 1
    since = time.mktime(time.strptime(args.since, "%Y-%m-%d")) if args.since else 0.0
    sessions = collect(home, scope, since)
    if args.json:
        print(json.dumps({"repo": scope.repo, "sessions": sessions}, indent=1))
        return 0
    if not sessions:
        print(f"No priced agent sessions found for `{scope.repo}` worktrees.")
        return 0
    short, full = build_report(scope, sessions, args.cards, args.worktree, time.time())
    report = Path(args.report) if args.report else Path(tempfile.gettempdir()) / f"melech-cost-{scope.repo}.md"
    report.write_text(full + "\n", encoding="utf-8")
    print(short)
    print(f"\nFull report: `{report}`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
