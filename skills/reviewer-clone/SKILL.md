---
name: reviewer-clone
description: >-
  Create and resync a private user-global Clone skill that reviews GitHub pull
  requests like the authenticated user. Learn the user's review voice,
  repository-specific concerns, ranked code-area attention, intervention
  threshold, and corrections from their reviews of other people's PRs, authored
  code, and feedback on prior Clone comments. Use when the user asks to clone or
  learn their code-review style, build a personal CR/PR reviewer, initialize
  another repository, retrain the reviewer, or resync/update an existing
  reviewer Clone.
---

# Reviewer Clone

Build and maintain a private personal reviewer, not a generic checklist bot.

## Run one workflow

Read `references/workflow.md` first and follow it as the single source of truth.
Do not reconstruct phase order or human-question behavior elsewhere.

Open the other references only when the workflow needs their subject:

- `references/github.md` — collection and honest coverage labels
- `references/evidence.md` — what activity can and cannot establish
- `references/attention-map.md` — relative code-area attention
- `references/resync.md` — new human and Clone-feedback events
- `references/output-contract.md` — generated files and publication

Use the bundled GitHub collectors whenever `workflow.md` assigns those jobs:

- `scripts/collect-review-activity.py`: index reviewed, commented, and authored
  PRs plus inline review comments
- `scripts/collect-pr-evidence.py`: fetch the repeatable metadata, discussion,
  diff, commit, and thread data for selected PRs

The main agent runs both collectors directly. Do not delegate them, inspect
their source before the first run, or recreate them as improvised Python or
shell. The main agent personally interprets selected-PR output; never delegate
those deep reads.

## Keep the learned model compact

This skill trains and updates; the generated Clone reviews PRs.

- `VOICE.md` holds transferable communication.
- Each repository has one `MEMORY.md` for context, attention, and judgment.
- Completed runs explain the evidence but are not active policy.
- Current code and explicit human corrections outrank learned files.

Repository context is the stack as a working system—runtime, frameworks, data
stores, infrastructure, deployment, architecture, and conventions—not merely
languages. Learn a plain-language picture of what the human notices, tolerates,
blocks, praises, and how they say it. Do not build a rigid personality rule
engine.

## Essential boundaries

- Keep private evidence and memory out of project repositories; never store
  credentials.
- Treat silence and authorship as weak evidence, not proof of preference.
- Publish only after the human chooses it, and preserve completed runs.
- Only this trainer edits active memory.
- Mark Clone authorship visibly; it is a correctable approximation, not the
  human.
