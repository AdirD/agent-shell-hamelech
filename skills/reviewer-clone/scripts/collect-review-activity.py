#!/usr/bin/env python3
"""Collect a reviewer's PR activity without making the agent rebuild the query logic."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SEARCH_FIELDS = "number,title,author,createdAt,updatedAt,state,url"
LINK_RE = re.compile(r"https?://[^\s<>\")\]]+")
ROLE_FLAGS = {
    "reviewed": "--reviewed-by",
    "commented": "--commenter",
    "authored": "--author",
}
ROLE_QUALIFIERS = {
    "reviewed": "reviewed-by",
    "commented": "commenter",
    "authored": "author",
}


class CollectionError(RuntimeError):
    """A GitHub collection command failed."""


def run_gh(args: list[str]) -> str:
    command = ["gh", *args]
    try:
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except FileNotFoundError as exc:
        raise CollectionError("GitHub CLI (`gh`) is not installed.") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or "unknown gh error"
        raise CollectionError(f"`{' '.join(command)}` failed: {detail}") from exc


def gh_json(args: list[str]) -> Any:
    output = run_gh(args)
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise CollectionError(f"GitHub CLI returned invalid JSON: {exc}") from exc


def parse_paginated_json(output: str) -> list[Any]:
    """Parse concatenated JSON values emitted by `gh api --paginate`."""
    decoder = json.JSONDecoder()
    values: list[Any] = []
    remaining = output
    while remaining.strip():
        remaining = remaining.lstrip()
        try:
            value, consumed = decoder.raw_decode(remaining)
        except json.JSONDecodeError as exc:
            raise CollectionError(
                f"Could not parse paginated GitHub response: {exc}"
            ) from exc
        values.append(value)
        remaining = remaining[consumed:]
    return values


def search_count(
    repo: str,
    login: str,
    role: str,
    created: tuple[dt.date, dt.date] | None = None,
) -> int:
    qualifier = f"{ROLE_QUALIFIERS[role]}:{login}"
    parts = [f"repo:{repo}", "is:pr", qualifier]
    if created:
        parts.append(f"created:{created[0].isoformat()}..{created[1].isoformat()}")
    result = gh_json(
        [
            "api",
            "--method",
            "GET",
            "search/issues",
            "-f",
            f"q={' '.join(parts)}",
            "-F",
            "per_page=1",
        ]
    )
    return int(result["total_count"])


def search_prs(
    repo: str,
    login: str,
    role: str,
    created: tuple[dt.date, dt.date] | None = None,
) -> list[dict[str, Any]]:
    args = [
        "search",
        "prs",
        "--repo",
        repo,
        ROLE_FLAGS[role],
        login,
        "--limit",
        "1000",
        "--json",
        SEARCH_FIELDS,
    ]
    if created:
        args.extend(
            ["--created", f"{created[0].isoformat()}..{created[1].isoformat()}"]
        )
    result = gh_json(args)
    if not isinstance(result, list):
        raise CollectionError(f"Expected a PR list for role `{role}`.")
    return result


def partitioned_search(
    repo: str,
    login: str,
    role: str,
    repo_created: dt.date,
    today: dt.date,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    total = search_count(repo, login, role)
    if total < 1000:
        return search_prs(repo, login, role), [
            {"created": None, "reported_count": total, "complete": True}
        ]

    pending = [(repo_created, today)]
    ranges: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    while pending:
        start, end = pending.pop()
        count = search_count(repo, login, role, (start, end))
        if count < 1000:
            results.extend(search_prs(repo, login, role, (start, end)))
            ranges.append(
                {
                    "created": f"{start.isoformat()}..{end.isoformat()}",
                    "reported_count": count,
                    "complete": True,
                }
            )
            continue
        if start == end:
            ranges.append(
                {
                    "created": start.isoformat(),
                    "reported_count": count,
                    "complete": False,
                    "gap": "GitHub Search has at least 1,000 matching PRs on one day.",
                }
            )
            continue
        midpoint = start + (end - start) // 2
        pending.append((midpoint + dt.timedelta(days=1), end))
        pending.append((start, midpoint))

    by_number = {int(pr["number"]): pr for pr in results}
    return list(by_number.values()), sorted(
        ranges, key=lambda item: item["created"] or ""
    )


def counter_rows(values: list[Any], key: str) -> list[dict[str, Any]]:
    counts = collections.Counter(values)
    return [
        {key: value, "count": count}
        for value, count in sorted(
            counts.items(), key=lambda item: (-item[1], str(item[0]))
        )
    ]


def value_range(values: list[str]) -> dict[str, str] | None:
    return {"earliest": min(values), "latest": max(values)} if values else None


def area_of(path: str | None) -> str:
    """Group a comment's file path into a coarse system area."""
    if not path:
        return "(no path)"
    parts = [part for part in path.split("/") if part]
    return "/".join(parts[:2]) if len(parts) >= 2 else (parts[0] if parts else "(no path)")


def write_comment_batches(
    comments: list[dict[str, Any]],
    comments_dir: Path,
    batch_size: int,
) -> list[dict[str, Any]]:
    """Shard human comments into ordered batch files the agent crunches one by one."""
    ordered = sorted(
        comments, key=lambda comment: (comment.get("created_at") or "", comment["id"])
    )
    batches: list[dict[str, Any]] = []
    for start in range(0, len(ordered), batch_size):
        chunk = ordered[start : start + batch_size]
        index = start // batch_size
        path = comments_dir / f"batch-{index:03d}.json"
        atomic_write_json(path, chunk)
        batches.append(
            {
                "index": index,
                "file": str(path),
                "count": len(chunk),
                "pr_numbers": sorted({comment["pr_number"] for comment in chunk}),
                "areas": counter_rows(
                    [area_of(comment["path"]) for comment in chunk], "area"
                ),
                "created_range": value_range(
                    [comment["created_at"] for comment in chunk if comment.get("created_at")]
                ),
            }
        )
    return batches


def compact_comment(
    comment: dict[str, Any],
    repo: str,
    prs: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    number = int(comment["pull_request_url"].rsplit("/", 1)[1])
    pr = prs.get(number, {})
    body = comment.get("body") or ""
    return {
        "id": comment["id"],
        "node_id": comment.get("node_id"),
        "html_url": comment.get("html_url"),
        "pr_number": number,
        "pr_url": pr.get("url", f"https://github.com/{repo}/pull/{number}"),
        "pr_title": pr.get("title"),
        "pr_author": pr.get("author"),
        "pr_state": pr.get("state"),
        "roles": sorted(pr.get("roles", [])),
        "path": comment.get("path"),
        "line": comment.get("line"),
        "original_line": comment.get("original_line"),
        "review_id": comment.get("pull_request_review_id"),
        "in_reply_to_id": comment.get("in_reply_to_id"),
        "created_at": comment.get("created_at"),
        "updated_at": comment.get("updated_at"),
        "body": body,
        "body_chars": len(body),
        "links": LINK_RE.findall(body),
        "clone_marked": "<!-- clone-trace:" in body,
    }


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def build_summary(result: dict[str, Any], detail_output: Path) -> dict[str, Any]:
    candidates = []
    for candidate in result["candidate_selection"]["candidates"]:
        body = candidate["body"]
        compact = {
            key: value
            for key, value in candidate.items()
            if key not in {"body", "clone_marked"}
        }
        compact["body_preview"] = body[:500] + ("…" if len(body) > 500 else "")
        candidates.append(compact)
    return {
        "schema_version": result["schema_version"],
        "generated_at": result["generated_at"],
        "repository": result["repository"],
        "requested_reviewer": result["requested_reviewer"],
        "authenticated_login": result["authenticated_login"],
        "coverage_complete": result["coverage_complete"],
        "query_ranges": result["query_ranges"],
        "counts": result["counts"],
        "created_range": result["created_range"],
        "updated_range": result["updated_range"],
        "states": result["states"],
        "top_authors": result["authors"][:25],
        "role_combinations": result["role_combinations"],
        "area_counts": result["area_counts"],
        "comment_batches": result["comment_batches"],
        "candidate_selection": {
            "method": result["candidate_selection"]["method"],
            "limit": result["candidate_selection"]["limit"],
            "candidates": candidates,
        },
        "collection_levels": result["collection_levels"],
        "detail_output": str(detail_output),
    }


def collect(args: argparse.Namespace) -> dict[str, Any]:
    authenticated_login = run_gh(["api", "user", "--jq", ".login"]).strip()
    repo_info = gh_json(["api", f"repos/{args.repo}"])
    repo_created = dt.date.fromisoformat(repo_info["created_at"][:10])
    today = dt.datetime.now(dt.timezone.utc).date()

    indexed: dict[str, list[dict[str, Any]]] = {}
    query_ranges: dict[str, list[dict[str, Any]]] = {}
    for role in ROLE_FLAGS:
        indexed[role], query_ranges[role] = partitioned_search(
            args.repo,
            args.login,
            role,
            repo_created,
            today,
        )

    pr_by_number: dict[int, dict[str, Any]] = {}
    for role, role_prs in indexed.items():
        for source in role_prs:
            number = int(source["number"])
            author = source.get("author")
            entry = pr_by_number.setdefault(
                number,
                {
                    "number": number,
                    "title": source["title"],
                    "author": author.get("login") if isinstance(author, dict) else None,
                    "createdAt": source["createdAt"],
                    "updatedAt": source["updatedAt"],
                    "state": source["state"],
                    "url": source["url"],
                    "roles": set(),
                },
            )
            entry["roles"].add(role)

    prs = sorted(
        ({**entry, "roles": sorted(entry["roles"])} for entry in pr_by_number.values()),
        key=lambda entry: entry["number"],
    )
    normalized_prs = {entry["number"]: entry for entry in prs}

    raw_pages = parse_paginated_json(
        run_gh(
            [
                "api",
                "--method",
                "GET",
                "--paginate",
                f"repos/{args.repo}/pulls/comments",
                "-f",
                "per_page=100",
            ]
        )
    )
    raw_comments = [
        item
        for page in raw_pages
        if isinstance(page, list)
        for item in page
        if isinstance(item, dict)
    ]
    attributed = [
        item
        for item in raw_comments
        if isinstance(item.get("user"), dict)
        and item["user"].get("login", "").casefold() == args.login.casefold()
    ]
    comments = [
        compact_comment(item, args.repo, normalized_prs)
        for item in {item["id"]: item for item in attributed}.values()
    ]

    strongest_by_pr: dict[int, dict[str, Any]] = {}
    for comment in comments:
        if (
            not comment["path"]
            or not comment["body"].strip()
            or comment["clone_marked"]
        ):
            continue
        current = strongest_by_pr.get(comment["pr_number"])
        if current is None or comment["body_chars"] > current["body_chars"]:
            strongest_by_pr[comment["pr_number"]] = comment
    candidates = sorted(
        strongest_by_pr.values(),
        key=lambda comment: (-comment["body_chars"], comment["id"]),
    )[: args.candidate_limit]

    human_comments = [
        comment
        for comment in comments
        if not comment["clone_marked"] and comment["body"].strip()
    ]
    comments_dir = args.comments_dir or args.output.parent / "comments"
    comment_batches = write_comment_batches(
        human_comments, comments_dir, args.batch_size
    )
    area_counts = counter_rows(
        [area_of(comment["path"]) for comment in human_comments], "area"
    )

    coverage_complete = all(
        interval["complete"]
        for intervals in query_ranges.values()
        for interval in intervals
    )
    return {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repository": args.repo,
        "requested_reviewer": args.login,
        "authenticated_login": authenticated_login,
        "coverage_complete": coverage_complete,
        "query_ranges": query_ranges,
        "counts": {
            "reviewed": len(indexed["reviewed"]),
            "commented": len(indexed["commented"]),
            "authored": len(indexed["authored"]),
            "unique_prs": len(prs),
            "inline_review_comments": len(comments),
            "prs_with_inline_review_comments": len(
                {comment["pr_number"] for comment in comments}
            ),
            "clone_marked_comments": sum(
                comment["clone_marked"] for comment in comments
            ),
            "comments_with_links": sum(bool(comment["links"]) for comment in comments),
        },
        "created_range": value_range([entry["createdAt"] for entry in prs]),
        "updated_range": value_range([entry["updatedAt"] for entry in prs]),
        "states": counter_rows([entry["state"] for entry in prs], "state"),
        "authors": counter_rows([entry["author"] for entry in prs], "author"),
        "role_combinations": counter_rows(
            ["+".join(entry["roles"]) for entry in prs], "roles"
        ),
        "prs": prs,
        "inline_review_comments": comments,
        "area_counts": area_counts,
        "comment_batches": {
            "dir": str(comments_dir),
            "batch_size": args.batch_size,
            "human_comment_count": len(human_comments),
            "batch_count": len(comment_batches),
            "batches": comment_batches,
        },
        "candidate_selection": {
            "method": (
                "Longest non-Clone, non-empty, path-anchored inline comment per PR; "
                "a starting sample the main agent correlates to local code and git."
            ),
            "limit": args.candidate_limit,
            "candidates": candidates,
        },
        "collection_levels": {
            "pr_metadata_indexed": len(prs),
            "inline_comments_collected": len(comments),
            "human_comments_batched": len(human_comments),
            "comment_batches_written": len(comment_batches),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Index reviewed, commented, and authored PRs plus the reviewer's inline "
            "comments. Handles GitHub Search's 1,000-result cap automatically."
        )
    )
    parser.add_argument("--repo", required=True, help="Canonical owner/repository")
    parser.add_argument("--login", required=True, help="GitHub reviewer login")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Private run-scratch JSON output path",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        help=(
            "Compact JSON for the agent to read; defaults to "
            "<output-stem>.summary.json"
        ),
    )
    parser.add_argument(
        "--candidate-limit",
        type=int,
        default=30,
        help="Maximum deterministic candidate comments to include (default: 30)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=40,
        help="Human comments per batch file for iterative crunching (default: 40)",
    )
    parser.add_argument(
        "--comments-dir",
        type=Path,
        help="Directory for comment batch files (default: <output-dir>/comments)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.candidate_limit < 1:
        print("--candidate-limit must be positive.", file=sys.stderr)
        return 2
    if args.batch_size < 1:
        print("--batch-size must be positive.", file=sys.stderr)
        return 2
    try:
        result = collect(args)
        summary_output = args.summary_output or args.output.with_name(
            f"{args.output.stem}.summary.json"
        )
        summary = build_summary(result, args.output)
        atomic_write_json(args.output, result)
        atomic_write_json(summary_output, summary)
    except CollectionError as exc:
        print(f"collection failed: {exc}", file=sys.stderr)
        return 1

    counts = result["counts"]
    print(
        json.dumps(
            {
                "output": str(args.output),
                "summary_output": str(summary_output),
                "coverage_complete": result["coverage_complete"],
                "reviewed": counts["reviewed"],
                "commented": counts["commented"],
                "authored": counts["authored"],
                "unique_prs": counts["unique_prs"],
                "inline_review_comments": counts["inline_review_comments"],
                "comments_with_links": counts["comments_with_links"],
                "comment_batches": result["comment_batches"]["batch_count"],
                "batch_dir": result["comment_batches"]["dir"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
