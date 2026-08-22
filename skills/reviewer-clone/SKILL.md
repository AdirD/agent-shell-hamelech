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

## Trainer and reviewer

This skill runs training and updates. The generated Clone reviews pull requests.

- `VOICE.md` holds the person's transferable tone and communication.
- Each repository is a drawer with its own `MEMORY.md`.
- Current PR/repository context always outranks cached memory.
- Evidence and completed runs explain how active memory was learned.

Only this training skill turns evidence into learned updates. Direct human
edits to active voice or memory remain authoritative.

## Follow one workflow

Read `references/workflow.md` first. It is the single source of truth for:

- init, repo-init, resync, and no-op routing
- lightweight repository choice before repository-specific work
- main-agent authority over iterative PR selection, deep reads, and learning
- fresh bounded repository/voice jobs and focused exploration
- phase order, run recording, resume, and simple recovery
- choosing which PRs to learn from and when to read more
- work/human concurrency
- recurring confidence checkpoints and behavior-changing calibration
- built-in todo progress and concise human updates
- calibration and plateau decision points
- staging, publication, and hand-off

Do not reconstruct or duplicate phase order from the other references. Read
them only when `workflow.md` calls for their subject:

- `references/github.md`: GitHub collection, pagination, and coverage semantics
- `references/evidence.md`: signal strength, uncertainty, and promotion
- `references/calibration.md`: distinctive fingerprint/question gate
- `references/attention-map.md`: relative code-area attention
- `references/resync.md`: incremental Clone-feedback evidence and reconciliation
- `references/output-contract.md`: generated files, state, provenance, comment
  trace, and publication

Use the bundled GitHub collectors whenever `workflow.md` assigns those jobs:

- `scripts/collect-review-activity.py`: index reviewed, commented, and authored
  PRs plus inline review comments
- `scripts/collect-pr-evidence.py`: fetch the repeatable metadata, discussion,
  diff, commit, and thread data for selected PRs

The main agent runs both collectors directly. Do not delegate them, inspect
their source before the first run, or recreate them as improvised Python or
shell. The main agent personally interprets selected-PR output; never delegate
those deep reads.

Every subagent starts fresh with a complete prompt, owns at most one output, and
rewrites that output rather than appending. It never edits active memory or
decides what the Clone learns. If it fails, run the complete job again.

The main agent keeps training interactive. It reflects current understanding and
asks one correction question early, after no more than three further deep reads,
when a material insight or contradiction appears, and before publication.
These confidence checkpoints redirect exploration; stricter corroboration still
controls what becomes active memory.

## Model the human compactly

Do not reduce the human to rigid per-rule objects. Infer a concise,
plain-language picture:

- what they notice and why
- what makes them comment, block, praise, or stay silent
- where repository structure or stack changes their judgment
- what they intentionally let pass
- how they phrase feedback
- what remains uncertain or contradicted

Repository context is the stack as a working system—runtime, frameworks, data
stores, infrastructure, deployment, architecture, and conventions—not merely
programming languages. Existing code proves what exists, not what the reviewer
endorses.

Maintain a compact ASCII attention tree in repository memory. Rank areas and
system boundaries as high, medium, unknown, or explicitly low. Leave unsupported
areas unknown. The map allocates review depth; it never suppresses clear defects.

`VOICE.md` and each repository's `MEMORY.md` are the only active truth. Runs and
evidence are provenance, not competing policy. Current explicit human answers
and direct active-file edits outrank historical inference.

## Guardrails

- Never publish personalized memory, private code evidence, tokens, or account
  details into a project repository.
- Never store credentials in the generated skill.
- Never infer disinterest, lack of expertise, or approval rationale from silence.
- Never promote one comment into doctrine without corroboration or confirmation.
- Never turn trainer uncertainty or a question allowance into a human survey.
- Never make authored code alone prove endorsement.
- Never describe a comment-body sweep as fully deep-reading its PRs.
- Never assign low importance from silence or missing review activity.
- Never declare plateau or publish without explicit human choice.
- Never delete completed runs; remove only disposable scratch after publication
  or recorded abandonment.
- Never let the generated Clone rewrite its own active memory.
- Never hide Clone authorship from PR participants.
- Never claim the Clone is the human; it is a transparent, correctable
  approximation.
