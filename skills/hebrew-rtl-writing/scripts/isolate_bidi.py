#!/usr/bin/env python3
import pathlib
import re
import sys

LRI = "\u2066"
PDI = "\u2069"

EN_SPAN_RE = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z][A-Za-z0-9+/_.,:-]*(?: [A-Za-z0-9+/_.,:-]+)*)(?![A-Za-z0-9_])")


def split_protected(text: str):
    combined = re.compile(
        r"(`+[^`]*?`+)|"          # inline code
        r"(\[[^\]]+\]\([^)]+\))|"  # markdown link
        r"(https?://\S+)"          # url
    )
    last = 0
    for match in combined.finditer(text):
        if match.start() > last:
            yield False, text[last:match.start()]
        yield True, match.group(0)
        last = match.end()
    if last < len(text):
        yield False, text[last:]


def already_isolated(segment: str, start: int, end: int) -> bool:
    return start > 0 and end < len(segment) and segment[start - 1] == LRI and segment[end] == PDI


def isolate_segment(segment: str) -> str:
    def repl(match: re.Match[str]) -> str:
        start, end = match.span(1)
        if already_isolated(segment, start, end):
            return match.group(1)
        value = match.group(1)
        trailing = ""
        while value and value[-1] in ".,;:!?":
            trailing = value[-1] + trailing
            value = value[:-1]
        return f"{LRI}{value}{PDI}{trailing}"

    return EN_SPAN_RE.sub(repl, segment)


def process_line(line: str) -> str:
    parts = []
    for protected, chunk in split_protected(line):
        if protected:
            parts.append(chunk)
        else:
            parts.append(isolate_segment(chunk))
    return "".join(parts)


def process_text(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out = []
    in_frontmatter = False
    in_fence = False
    fence_marker = ""

    for idx, line in enumerate(lines):
        stripped = line.lstrip()

        if idx == 0 and stripped.startswith("---"):
            in_frontmatter = True
            out.append(line)
            continue

        if in_frontmatter:
            out.append(line)
            if stripped.startswith("---"):
                in_frontmatter = False
            continue

        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            out.append(line)
            continue

        if in_fence:
            out.append(line)
            continue

        out.append(process_line(line))

    return "".join(out)


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        print("usage: isolate_bidi.py <file> [<file> ...]", file=sys.stderr)
        return 0 if len(argv) >= 2 else 2

    for raw_path in argv[1:]:
        path = pathlib.Path(raw_path)
        original = path.read_text(encoding="utf-8")
        updated = process_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
