# Generated Clone contract

`workflow.md` defines when work happens. This file defines the private generated
Clone and the minimum durable record needed to review, resync, and recover.

Create one user-global skill per GitHub identity:

```text
~/.agents/skills/cr-clone-<github-login-lowercase>/
  SKILL.md
  VOICE.md
  state.json

  repos/
    github.com/<owner>/<repo>/
      MEMORY.md

      runs/
        2026-08-22T100000Z-init/
          RUN.md
          EVIDENCE.md
          repository-system.md
          voice.md
          previous-VOICE.md
          previous-MEMORY.md
          scratch/
```

`previous-VOICE.md` and `previous-MEMORY.md` exist only when publication replaces
active files. Keep the canonical Clone outside project repositories. If a
particular agent runtime cannot discover `~/.agents/skills`, expose the canonical
directory there when that need actually occurs; do not maintain default mirror
machinery.

Use the canonical base repository for routing. Normalize host, owner, and
repository casing consistently. Keep renamed-repository aliases in state rather
than duplicating memory.

## Active review context

During an ordinary review, the generated Clone reads only:

1. its `SKILL.md`
2. `VOICE.md`
3. the matching repository `MEMORY.md`
4. the live PR and relevant repository code

Training runs are provenance, not additional active policy. Read them during
resync or to resolve a specific uncertainty, not on every review.

`VOICE.md` and repository `MEMORY.md` are the only learned truth. Current live
code and explicit human edits outrank both.

## `VOICE.md`

Keep the transferable **HOW** here:

```markdown
---
revision: 4
updated_at: 2026-08-22T10:00:00Z
---

# HOW — transferable review style

## Default posture
Curious, direct, cautious, encouraging, etc.

## Investigation and evidence
Whether the human researches before commenting, follows links, cites official
docs or code, points to in-repo precedent, runs checks, or provides examples.

## Comment shape
Typical length, questions versus statements, explanation depth, examples,
patches, praise, humor, and recurring phrasing.

## Delivery
How blockers, ordinary concerns, nits, and approval are communicated.

## Avoid
Phrasing or behavior that would sound unlike the human.

## Uncertainty
What has not been learned confidently.
```

Keep one voice unless repeated evidence shows the human genuinely communicates
differently in a particular context.

## Repository `MEMORY.md`

Keep the repository-specific **WHERE, WHEN, and HOW** compact enough to load on
every review:

```markdown
---
revision: 7
updated_at: 2026-08-22T10:00:00Z
repository: github.com/example-org/order-service
---

# Repository reviewer model

## WHERE — system attention
A compact architecture view overlaid with where the human demonstrates repeated
interest, familiarity, or expertise. Include the ranked attention tree and the
evidence behind important areas.

## WHEN — intervention threshold
What makes the human comment, ask, suggest, block, praise, or approve silently.
Capture meaningful risk boundaries and demonstrated tolerance.

## HOW — review method in this repository
Repo-specific investigation habits: preferred internal precedents, docs,
research, links, tests, demonstrations, or evidence used before commenting.
`VOICE.md` supplies the transferable communication style.

## Known corrections
What Clone previously misunderstood.

## Uncertainty
What the evidence has not settled.
```

Do not turn WHERE, WHEN, and HOW into a rule matrix. Let the runtime reason from
the compact model and current PR.

## `state.json`

Use one small root state file for machine-readable facts:

- schema version and canonical reviewer identity
- active voice revision
- repository aliases and active memory revisions
- last successful sync per repository
- incremental GitHub cursors and previously open PRs to revisit
- latest coverage summary and run path

Do not copy personality, PR evidence, or run narration into state.

## Durable runs

Every initialization and resync gets one unique run directory. Never reuse a
completed run.

`RUN.md` contains:

- status: in progress, paused, published, failed, or abandoned
- reviewer, repository, start/end times
- indexed, comment-collected, fetched, and deep-read counts
- selected and deep-read PR IDs
- model reflections, calibration questions, and human answers
- material WHERE, WHEN, and HOW learning, narrowing, and unlearning
- remaining uncertainty
- system-attention movement
- why work stopped and the human decision
- publication result or failure

`EVIDENCE.md` contains concise sections for the PRs actually deeply read, using
stable PR/comment/review IDs. This is the minimum source trace needed to avoid
relearning the same event and to verify future corrections. Do not create a
large folder hierarchy or retain entire private diffs.

`repository-system.md` and `voice.md` are complete outputs from the repository
mapping and review-method jobs. `scratch/` holds disposable collector JSON,
diffs, and staged active files. Everything except `scratch/` remains useful run
provenance.

## Publication

Before replacing active memory:

- record accepted learning and source IDs in `RUN.md`
- stage complete active files under `scratch/`
- re-read active files so direct human edits remain authoritative
- preserve replaced active contents in the run
- check privacy, uncertainty, and internal consistency
- replace complete files, then update `state.json`

If replacement fails, restore the prior copy. This is enough safety for a local
two-file publication; do not build a transaction protocol around it.

## Generated runtime `SKILL.md`

Generate it only after the first explicit publish decision. Its instructions
must:

1. Use name `cr-clone-<github-login-lowercase>`.
2. Resolve the PR's canonical base repository and load matching `MEMORY.md`.
3. Ask for initialization through `reviewer-clone` when memory is missing.
4. Read the live PR and relevant current code before trusting cached context.
5. Use WHERE to allocate review depth, while reporting clear defects anywhere.
6. Use WHEN to decide whether a finding deserves silence, a question, a
   suggestion, or a block.
7. Use HOW to investigate and communicate. When the learned style relies on
   research or citations, check comparable sources before commenting and link
   only evidence actually inspected.
8. Prefer a few authentic comments over generic checklist coverage.
9. Draft unless the user explicitly requested posting.
10. When posting is explicitly requested, use the authenticated `gh` CLI:
    `gh pr review --approve`, `--request-changes`, or `--comment` for review
    decisions; `gh pr comment` for a general PR comment; and `gh api` when an
    anchored inline comment is required.
11. Mark Clone-authored comments visibly as `🤖 Clone:`.
12. Add the compact trace below to posted or pending comments.
13. Never edit its own active memory or claim to be the human.
14. Recommend trainer resync when memory is stale without blocking urgent review.

## Compact comment trace

Keep enough hidden context to recognize the original Clone decision after a
human edit:

```markdown
🤖 Clone: Could this publish twice after a retry?

<!-- Clone note:
Trace: 20260822-01-03
Original: Could this publish twice after a retry?
Reason: Externally visible retry without an obvious stable identity.
Memory: repository 7; voice 4
-->
```

The note is human-readable provenance, not hidden reasoning. HTML comments are
not private from API readers. Never include secrets or sensitive unpublished
context.
