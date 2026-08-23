# What you generate

One private user-global skill per GitHub identity, kept outside project repos:

```text
~/.agents/skills/cr-clone-<login>/
  SKILL.md
  VOICE.md            # transferable HOW
  state.json          # machine facts: identity, revisions, sync cursors, run path
  repos/github.com/<owner>/<repo>/
    MEMORY.md         # this repo's WHERE / WHEN / HOW
    runs/2026-08-22T100000Z-init/
      RUN.md          # status, coverage, PR IDs, human answers, learning, decision
      EVIDENCE.md     # short source-backed notes for PRs actually deep-read
      repository-system.md
      voice.md
      previous-*.md   # backups, only when publish replaces active files
      scratch/        # disposable collector JSON, diffs, staged files
```

At review time the Clone reads only its `SKILL.md`, `VOICE.md`, the matching
`MEMORY.md`, and the live PR/code. Runs are provenance—read them on resync, not
every review. `VOICE.md` and `MEMORY.md` are the only learned truth; live code and
explicit human edits outrank both.

## `VOICE.md` — transferable HOW

```markdown
---
revision: 4
updated_at: 2026-08-22T10:00:00Z
---
# HOW — transferable review style

## Posture
Curious, direct, cautious, encouraging, etc.

## Investigation
Whether they research before commenting, follow links, cite docs/code/precedent,
run checks, or give examples.

## Comment shape
Length, questions vs statements, depth, examples, patches, praise, recurring phrasing.

## Delivery
How blockers, ordinary concerns, nits, and approval are communicated.

## Avoid / Uncertain
What would sound unlike them; what isn't learned confidently yet.
```

Keep one voice unless evidence clearly shows they communicate differently in a context.

## `MEMORY.md` — this repo's model

```markdown
---
revision: 7
updated_at: 2026-08-22T10:00:00Z
repository: github.com/example-org/order-service
---
# Repository reviewer model

## WHERE — system attention
Architecture overlaid with where they show repeated interest/expertise. Include the
ranked attention tree and the evidence behind the important areas.

## WHEN — intervention threshold
What makes them comment, ask, suggest, block, praise, or approve silently.

## HOW — method here
Repo-specific investigation habits: internal precedents, docs, tests, or evidence
used before commenting. `VOICE.md` supplies the transferable style.

## Known corrections / Uncertainty
What Clone got wrong before; what the evidence hasn't settled.
```

Don't turn WHERE/WHEN/HOW into a rule matrix—let the runtime reason from the model
plus the current PR.

## Publish safely

Only an explicit publish decision changes active memory: stage complete files in
`scratch/`, re-read the live active files so human edits survive, back up the old
copies into the run, check privacy/consistency, swap in the new files, update
`state.json`. If it fails, restore the backup. That's enough safety for two local
files—no transaction protocol.

## Generated runtime `SKILL.md`

Create it only after the first publish. It should be named `cr-clone-<login>` and
tell the Clone to:

1. Resolve the PR's base repo and load its `MEMORY.md` (ask for `reviewer-clone`
   init if missing).
2. Read the live PR and current code before trusting cached context.
3. Use WHERE for depth, WHEN for whether to stay silent / ask / suggest / block,
   and HOW to investigate and write. When the style relies on research, check
   comparable sources first and link only what was actually inspected.
4. Prefer a few authentic comments over checklist coverage. Draft by default.
5. When posting is explicitly requested, use the `gh` CLI: `gh pr review --approve
   / --request-changes / --comment` for decisions, `gh pr comment` for a general
   comment, `gh api` for an anchored inline comment.
6. Mark comments `🤖 Clone:` with the trace below. Never edit its own memory or
   claim to be the human. Suggest a resync when memory is clearly stale.

## Comment trace

```markdown
🤖 Clone: Could this publish twice after a retry?

<!-- Clone note:
Trace: 20260822-01-03
Original: Could this publish twice after a retry?
Reason: Externally visible retry without an obvious stable identity.
Memory: repository 7; voice 4
-->
```

Human-readable provenance, not hidden reasoning. HTML comments aren't private—no
secrets.
