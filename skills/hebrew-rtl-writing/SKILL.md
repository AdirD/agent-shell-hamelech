---
name: hebrew-rtl-writing
description: 'Fix mixed RTL/LTR rendering for any textual artifact that is primarily Hebrew but includes embedded English terms. Use when drafting or editing Hebrew prose, Markdown, notes, docs, essays, posts, specs, or other text-heavy files that include words like AI, thread, prompt, RBAC, billing, commits, or product names.'
---

Use this skill whenever the user is working on a textual artifact that is mostly Hebrew and contains embedded English terms that make the text hard to read.

## Goal

Keep Hebrew Markdown readable when English words appear inside Hebrew sentences.

Default strategy:

1. Preserve the text itself.
2. Add Unicode bidi isolation around English spans in prose:
   - `LRI` = `U+2066`
   - `PDI` = `U+2069`
3. Apply isolation only where it helps readability.

## Use This Skill For

- Hebrew prose of any kind
- Markdown files that are mostly Hebrew text
- notes, docs, essays, posts, specs, drafts, and internal writing
- existing Hebrew-first files that already render badly because of mixed RTL/LTR text

## Do Not Use This Skill For

- Code files
- JSON, YAML, shell scripts, or config
- Markdown sections that are mostly paths, URLs, or code
- Link targets or file references unless the user explicitly asks

## Workflow

1. Confirm the text is primarily Hebrew prose with mixed English spans.
2. Prefer the bundled script for prose-heavy text or Markdown files.
3. Avoid touching:
   - fenced code blocks
   - inline code spans
   - YAML frontmatter
   - Markdown link destinations
   - obvious URLs and filesystem paths
4. If the file is fragile or has many special Markdown constructs, edit surgically instead of bulk-running the script.
5. After editing, inspect a few representative mixed-language lines.

## Bundled Script

Use:

```bash
python3 .agents/skills/hebrew-rtl-writing/scripts/isolate_bidi.py path/to/file.md
```

Multiple files are supported:

```bash
python3 .agents/skills/hebrew-rtl-writing/scripts/isolate_bidi.py file1.md file2.md
```

The script:

- skips fenced code blocks
- skips top-level YAML frontmatter
- skips inline code
- skips Markdown link destinations
- wraps English prose spans with `LRI ... PDI`

## Notes

- Do not double-wrap spans that are already isolated.
- Do not rewrite terminology just to avoid English.
- This skill is for directionality, not content editing.
- If a renderer visibly shows the isolate marks as glyphs, offer a fallback:
  - wrap English terms in backticks
  - or use HTML spans with `dir="ltr"` if the target renderer supports them
