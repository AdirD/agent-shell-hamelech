#!/usr/bin/env python3
"""Fetch the repeatable GitHub data needed before an agent deep-reads selected PRs."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PR_FIELDS = (
    "number,title,url,body,author,baseRefName,headRefName,headRefOid,state,isDraft,"
    "createdAt,updatedAt,mergedAt,closedAt,additions,deletions,changedFiles,"
    "reviewDecision,mergeCommit"
)

THREAD_QUERY = """
query(
  $owner: String!
  $name: String!
  $number: Int!
  $cursor: String
) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $cursor) {
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          originalLine
          comments(first: 100) {
            nodes {
              databaseId
              id
              url
              body
              createdAt
              updatedAt
              author { login }
              replyTo { databaseId }
            }
            pageInfo { hasNextPage endCursor }
          }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
"""


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


def rest_list(endpoint: str) -> list[dict[str, Any]]:
    pages = parse_paginated_json(
        run_gh(
            [
                "api",
                "--method",
                "GET",
                "--paginate",
                endpoint,
                "-f",
                "per_page=100",
            ]
        )
    )
    return [
        item
        for page in pages
        if isinstance(page, list)
        for item in page
        if isinstance(item, dict)
    ]


def login_of(value: Any) -> str | None:
    return value.get("login") if isinstance(value, dict) else None


def classify_body(body: str, author: str | None, reviewer: str) -> dict[str, bool]:
    return {
        "is_reviewer": bool(author and author.casefold() == reviewer.casefold()),
        "clone_marked": body.startswith("🤖 Clone:"),
    }


def compact_reviews(
    reviews: list[dict[str, Any]], reviewer: str
) -> list[dict[str, Any]]:
    result = []
    for item in reviews:
        body = item.get("body") or ""
        author = login_of(item.get("user"))
        result.append(
            {
                "id": item.get("id"),
                "node_id": item.get("node_id"),
                "author": author,
                "state": item.get("state"),
                "body": body,
                "submitted_at": item.get("submitted_at"),
                "commit_id": item.get("commit_id"),
                "html_url": item.get("html_url"),
                **classify_body(body, author, reviewer),
            }
        )
    return result


def compact_review_comments(
    comments: list[dict[str, Any]], reviewer: str
) -> list[dict[str, Any]]:
    result = []
    for item in comments:
        body = item.get("body") or ""
        author = login_of(item.get("user"))
        result.append(
            {
                "id": item.get("id"),
                "node_id": item.get("node_id"),
                "author": author,
                "body": body,
                "path": item.get("path"),
                "line": item.get("line"),
                "side": item.get("side"),
                "start_line": item.get("start_line"),
                "start_side": item.get("start_side"),
                "original_line": item.get("original_line"),
                "original_side": item.get("original_side"),
                "original_start_line": item.get("original_start_line"),
                "original_start_side": item.get("original_start_side"),
                "diff_hunk": item.get("diff_hunk"),
                "commit_id": item.get("commit_id"),
                "original_commit_id": item.get("original_commit_id"),
                "review_id": item.get("pull_request_review_id"),
                "in_reply_to_id": item.get("in_reply_to_id"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "html_url": item.get("html_url"),
                **classify_body(body, author, reviewer),
            }
        )
    return result


def compact_issue_comments(
    comments: list[dict[str, Any]], reviewer: str
) -> list[dict[str, Any]]:
    result = []
    for item in comments:
        body = item.get("body") or ""
        author = login_of(item.get("user"))
        result.append(
            {
                "id": item.get("id"),
                "node_id": item.get("node_id"),
                "author": author,
                "body": body,
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "html_url": item.get("html_url"),
                **classify_body(body, author, reviewer),
            }
        )
    return result


def compact_files(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "filename": item.get("filename"),
            "status": item.get("status"),
            "previous_filename": item.get("previous_filename"),
            "additions": item.get("additions"),
            "deletions": item.get("deletions"),
            "changes": item.get("changes"),
            "sha": item.get("sha"),
            "patch": item.get("patch"),
            "contents_url": item.get("contents_url"),
            "blob_url": item.get("blob_url"),
        }
        for item in files
    ]


def compact_commits(commits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for item in commits:
        commit = item.get("commit") or {}
        result.append(
            {
                "sha": item.get("sha"),
                "message": commit.get("message"),
                "author_date": (commit.get("author") or {}).get("date"),
                "committer_date": (commit.get("committer") or {}).get("date"),
                "author": login_of(item.get("author")),
                "committer": login_of(item.get("committer")),
                "parents": [
                    parent.get("sha")
                    for parent in item.get("parents", [])
                    if isinstance(parent, dict)
                ],
                "html_url": item.get("html_url"),
            }
        )
    return result


def fetch_threads(
    owner: str,
    name: str,
    number: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    cursor: str | None = None
    threads: list[dict[str, Any]] = []
    warnings: list[str] = []

    while True:
        command = [
            "api",
            "graphql",
            "-f",
            f"query={THREAD_QUERY}",
            "-f",
            f"owner={owner}",
            "-f",
            f"name={name}",
            "-F",
            f"number={number}",
        ]
        if cursor:
            command.extend(["-f", f"cursor={cursor}"])
        result = gh_json(command)
        errors = result.get("errors") if isinstance(result, dict) else None
        if errors:
            warnings.append(f"GraphQL review threads unavailable: {errors}")
            break
        try:
            connection = result["data"]["repository"]["pullRequest"]["reviewThreads"]
        except (KeyError, TypeError):
            warnings.append("GraphQL review threads were absent from the response.")
            break

        for thread in connection.get("nodes") or []:
            comments = thread.get("comments") or {}
            if (comments.get("pageInfo") or {}).get("hasNextPage"):
                warnings.append(
                    f"Thread {thread.get('id')} has more than 100 comments; "
                    "additional replies were not fetched."
                )
            threads.append(
                {
                    "id": thread.get("id"),
                    "is_resolved": thread.get("isResolved"),
                    "is_outdated": thread.get("isOutdated"),
                    "path": thread.get("path"),
                    "line": thread.get("line"),
                    "original_line": thread.get("originalLine"),
                    "comments": comments.get("nodes") or [],
                }
            )

        page_info = connection.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        if not cursor:
            warnings.append("Review-thread pagination ended without a cursor.")
            break

    return threads, warnings


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def collect_pr(
    repo: str,
    reviewer: str,
    number: int,
) -> dict[str, Any]:
    owner, name = repo.split("/", 1)
    metadata = gh_json(
        [
            "pr",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            PR_FIELDS,
        ]
    )
    reviews = compact_reviews(
        rest_list(f"repos/{repo}/pulls/{number}/reviews"), reviewer
    )
    review_comments = compact_review_comments(
        rest_list(f"repos/{repo}/pulls/{number}/comments"), reviewer
    )
    issue_comments = compact_issue_comments(
        rest_list(f"repos/{repo}/issues/{number}/comments"), reviewer
    )
    files = compact_files(rest_list(f"repos/{repo}/pulls/{number}/files"))
    commits = compact_commits(rest_list(f"repos/{repo}/pulls/{number}/commits"))
    threads, warnings = fetch_threads(owner, name, number)

    return {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repository": repo,
        "reviewer": reviewer,
        "pr_number": number,
        "metadata": metadata,
        "reviews": reviews,
        "review_comments": review_comments,
        "issue_comments": issue_comments,
        "files": files,
        "commits": commits,
        "review_threads": threads,
        "warnings": warnings,
        "collection_level": "review material fetched; agent deep-read still required",
        "counts": {
            "reviews": len(reviews),
            "review_comments": len(review_comments),
            "issue_comments": len(issue_comments),
            "files": len(files),
            "commits": len(commits),
            "review_threads": len(threads),
            "reviewer_reviews": sum(item["is_reviewer"] for item in reviews),
            "reviewer_review_comments": sum(
                item["is_reviewer"] and not item["clone_marked"]
                for item in review_comments
            ),
            "reviewer_issue_comments": sum(
                item["is_reviewer"] and not item["clone_marked"]
                for item in issue_comments
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch compact metadata, reviews, comments, files, commits, and review "
            "threads for selected PRs into disposable run scratch."
        )
    )
    parser.add_argument("--repo", required=True, help="Canonical owner/repository")
    parser.add_argument("--reviewer", required=True, help="GitHub reviewer login")
    parser.add_argument(
        "--prs",
        required=True,
        nargs="+",
        type=int,
        help="One or more selected PR numbers",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Private run-scratch directory; writes <number>.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if "/" not in args.repo or args.repo.startswith("/") or args.repo.endswith("/"):
        print("--repo must be owner/repository.", file=sys.stderr)
        return 2

    try:
        authenticated_login = run_gh(["api", "user", "--jq", ".login"]).strip()
        summaries = []
        for number in dict.fromkeys(args.prs):
            result = collect_pr(args.repo, args.reviewer, number)
            output = args.output_dir / f"{number}.json"
            atomic_write_json(output, result)
            summaries.append(
                {
                    "pr": number,
                    "output": str(output),
                    "counts": result["counts"],
                    "warnings": result["warnings"],
                }
            )
    except CollectionError as exc:
        print(f"collection failed: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "authenticated_login": authenticated_login,
                "repository": args.repo,
                "reviewer": args.reviewer,
                "prs": summaries,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
