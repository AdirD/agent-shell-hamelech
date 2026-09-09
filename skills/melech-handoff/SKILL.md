---
name: melech-handoff
description: List and continue coding-agent transcripts across Cursor, Claude Code, Codex, Gemini, and other local agents. Use when finding a recent transcript, resuming prior work, or invoking `/melech-handoff`.
---

# Melech Handoff

Find and resume coding-agent sessions without putting handoff files in the
repository or making the user copy transcript paths between chats.

Two modes only: **list** and **cont**. The script only discovers, lists, and
looks up transcripts. The agent does the intelligent retrieval.

```text
/melech-handoff
/melech-handoff list
/melech-handoff cont [session-id-prefix | objective]
```

Resolve the mode from the invocation. Do not ask which mode they want.

- Bare `/melech-handoff` or `/melech-handoff list` → **list**
- `/melech-handoff` plus a session id / unique id prefix → **cont**
- `/melech-handoff cont …` → **cont**

Set `HANDOFF_SCRIPT` to `scripts/handoff.py` beside this file. Run it with
Python 3.9 or newer. Treat its JSON output as the source of truth; do not
recreate transcript discovery with an unbounded home-directory search.

## List

Run:

```bash
python3 "$HANDOFF_SCRIPT" list --cwd "$PWD" --limit 12
```

Show the rows newest first as compact Markdown cards. Do not use a table: CLI
table renderers crush the metadata columns and cannot display multiline
glimpses. Use the script fields; do not invent dates, agents, worktrees, or
counts.

```text
### `<short_id>` · <topic>
<provider> · <age>
`<worktree>` · <stats.user_messages> user msgs · ~<stats.approx_tokens> tokens

1. <third-to-last user message>
2. <second-to-last user message>
3. <latest user message>
```

`age` is the compact time since the transcript was last written, such as `8m
ago`, `3h ago`, or `2d ago`; this is the only timestamp shown because the list
is ordered by recent activity. Exact `created` and `modified` values remain in
the script output for lookup or debugging. `worktree` is `main` for the
repository's main worktree and otherwise the worktree directory name.
`stats.approx_tokens` is a cheap `chars / 4` estimate, not a tokenizer result.
`topic` is a short hint derived from the first meaningful human request.
`glimpse` contains up to the three latest human user messages as real numbered
lines. Preserve the newlines when rendering the card; do not duplicate messages
when fewer than three exist. Each message may use up to 160 characters. Do not
remove the cap because individual transcript turns can be thousands of
characters. Tool results and metadata-only user records are ignored.

`list` is read-only. Show enough information for the user to invoke
`/melech-handoff cont <id>`, then stop. Do not start working or read full
transcripts.

## Continue

If the argument begins with a session ID or unique ID prefix, run:

```bash
python3 "$HANDOFF_SCRIPT" lookup --cwd "$PWD" --id "<id-prefix>"
```

Any remaining text is the continuation objective.

If there is no ID, run `list` without a query. The script does not pretend to
understand the objective. Choose distinctive terms from the objective and
search only the returned `primary_transcript_path` files with `rg`.

- One clear transcript match: run `lookup` on its id, then continue.
- Several plausible matches: use one combined AskQuestion picker with the
  matching candidates. After the pick, run `lookup`.
- No argument: show the five newest rows in one combined AskQuestion picker.
  Each option starts with
  `<age> · <provider> · <topic> · <short_id>`, followed by worktree, stats, and
  the three-line glimpse. If undisplayed rows remain, append an
  `Older sessions…` option that opens the next five rows using the same layout.
  Do not add multiple questions to one picker because that requires one answer
  per question.
- If the user selects the picker's automatic `Other` option and enters text,
  treat that text as the continuation objective and relevance query. Search
  the returned `primary_transcript_path` candidates for distinctive terms,
  independent of recency. Continue a single clear match; otherwise show one
  refreshed picker containing only the strongest relevant candidates.
- After a session is picked, run `lookup`.
- No match among the listed candidates: say so. Do not broaden into an
  unbounded home-directory scan.

`lookup` returns `primary_transcript_path`, the text file to consult. If
anything about the task or current state is unclear, search that transcript for
relevant keywords such as task names, filenames, IDs, errors, and tool names.
Then read a small window around matching lines to reconstruct intent and state.
Avoid reading linearly end-to-end: JSONL transcripts can be large and individual
lines can contain large payloads.

Use the continuation objective to decide what context is relevant. The agent,
not the Python script, makes that judgment.

Do not write a card and do not invent a long recap. Follow retrieval
constraints in the objective, such as “don’t read all.”

Continue the work directly once the target is clear. Do not ask whether the
user wants you to proceed.

## Boundaries

- Do not write files under `~/.melech/handoffs/`. List and continue from
  transcripts only.
- Scope defaults to the current worktree root, not sibling worktrees.
- Provider locations come only from `references/providers.json`.
- Database, encrypted, protobuf-only, and compressed-only histories are
  recorded but unsupported.
- Transcript and handoff contents are private local history. Never publish,
  upload, or paste them externally without explicit user instruction.
