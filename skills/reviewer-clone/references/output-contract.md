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

Keep transferable human communication here:

```markdown
---
revision: 4
updated_at: 2026-08-22T10:00:00Z
---

# Voice

## Default posture
Curious, direct, cautious, encouraging, etc.

## Comment shape
Typical length, questions versus statements, explanation depth, examples,
patches, praise, humor, and recurring phrasing.

## Severity language
How blockers, ordinary concerns, nits, and approval are communicated.

## Avoid
Phrasing or behavior that would sound unlike the human.

## Uncertainty
What has not been learned confidently.
```

Keep one voice unless repeated evidence shows the human genuinely communicates
differently in a particular context.

## Repository `MEMORY.md`

Keep repo-specific judgment compact enough to load on every review:

```markdown
---
revision: 7
updated_at: 2026-08-22T10:00:00Z
repository: github.com/example-org/order-service
---

# Repository memory

## How this repository works
Runtime, frameworks, services, persistence, deployment, major boundaries, and
anything needed to reason about changes.

## What deserves extra attention
Concise concerns and the concrete risks behind them.

## What usually does not deserve a comment
Demonstrated tolerance, accepted conventions, and prior Clone overreach.

## Attention map
A ranked tree using `high`, `medium`, `unknown`, and `explicitly low`.

## Review instincts
Patterns in when the human questions, blocks, praises, or intentionally lets
something pass.

## Known corrections
What Clone previously misunderstood.

## Uncertainty
What the evidence has not settled.
```

Do not repeat stack qualifiers on every instinct or encode personality as a
large rule engine. Let the runtime reason from the whole memory and current PR.

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
- material learning, narrowing, unlearning, and uncertainty
- attention movement
- why work stopped and the human decision
- publication result or failure

`EVIDENCE.md` contains concise sections for the PRs actually deeply read, using
stable PR/comment/review IDs. This is the minimum source trace needed to avoid
relearning the same event and to verify future corrections. Do not create a
large folder hierarchy or retain entire private diffs.

`repository-system.md` and `voice.md` are complete outputs from their bounded
parallel jobs. `scratch/` holds disposable collector JSON, diffs, and staged
active files. Everything except `scratch/` remains useful run provenance.

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
5. Use the attention tree to allocate depth, while reporting clear defects
   anywhere.
6. Review at this human's likely intervention threshold and in their voice.
7. Prefer a few authentic comments over generic checklist coverage.
8. Draft unless the user explicitly requested posting.
9. Mark Clone-authored comments visibly as `🤖 Clone:`.
10. Add the compact trace below to posted or pending comments.
11. Never edit its own active memory or claim to be the human.
12. Recommend trainer resync when memory is stale without blocking urgent review.

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
