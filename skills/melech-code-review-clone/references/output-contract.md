# What you generate

You (the trainer) write these files; the Clone (`cr-clone-<login>`) is the only thing
that reads them at review time. Write for that reader.

One private user-global skill per GitHub identity, kept outside project repos:

```text
~/.agents/skills/cr-clone-<login>/
  SKILL.md
  VOICE.md            # transferable HOW
  state.json          # machine facts: identity, revisions, sync cursors, run path
  repos/github.com/<owner>/<repo>/
    MODEL.md          # this repo's model: IF/WHAT/WHERE/WHEN/WHO/WHY, grounding inline
    runs/2026-08-22T100000Z-init/
      RUN.md          # status, coverage, per-chunk deltas, human answers, decision, source IDs
      previous-*.md   # backups, only when publish replaces active files
      scratch/        # collector JSON + comments/batch-*.json + draft MODEL.md/VOICE.md
```

At review time the Clone reads only its `SKILL.md`, `VOICE.md`, the matching
`MODEL.md`, and the live PR/code. Runs are provenance—read them on resync, not
every review. `VOICE.md` and `MODEL.md` are the only learned truth; live code and
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
How blockers, ordinary concerns, nits, and approval are communicated—including
whether approval is usually *silent* (no words) or carries a summary line.

## As author vs as reviewer
How they sound answering feedback on their own PRs (concede / defend / explain /
cite) vs how they push on others'. Note only if the two clearly differ.

## Avoid / Uncertain
What would sound unlike them; what isn't learned confidently yet.
```

Keep one voice unless evidence clearly shows they communicate differently in a context
(reviewing others' code vs replying on their own is the most common such split).

## `MODEL.md` — the repo brain the Clone acts from

This is written for the Clone to *use at review time*, so it's filed by how a review
actually happens—open the diff, and for each change decide *do I care, and what do I
do?*—not by lens. The lenses (IF/WHAT/WHERE/WHEN/WHO/WHY) are how you *learn* it;
here they collapse into reflexes and a map. Fill from real data:

```markdown
---
revision: 7
updated_at: 2026-08-22T10:00:00Z
repository: github.com/example-org/order-service
---
# Repository reviewer model

## Attention map — where I look first (WHERE)
Ranked areas by comment density + git ownership: where to spend scrutiny, where to skim.
- packages/ai-sdk/tools — 120 comments, ~70% authored → home turf, high bar
- db/migrations — 40 comments, co-owns → high, always reads rollback + backfill order
- apps/studio (studio.json) — 3 comments, heavy churn, doesn't author → skim (trusts it)

## Reflexes — when I see X, I do Y (WHAT / WHEN / WHY)
The core. Each: trigger → reaction → how hard → why → real example.
- **Un-awaited async write on a hot path** → flag → **block**; data-loss / double-
  processing risk. e.g. `packages/ai-sdk/tools/run.ts:44` (31 comments / 22 PRs).
- **Migration without rollback + backfill order** → ask for both → **block**;
  irreversible in prod. e.g. `db/migrations/0042_orders.sql`.
- **External call without retry / idempotency** → suggest a queue or stable id →
  strong push, won't always block. e.g. `run.ts:44`.
- **Naming / file structure** → note it → **suggestion only**, never blocks.

## Negative space — what I wave through (the anti-over-flag guard)
As load-bearing as the reflexes; stops the Clone from nitpicking. Don't comment on:
- Copy / UI strings, config churn in studio.json, formatting, test scaffolding.
- Style / naming inside areas I don't own.

## Default posture — when nothing above fires (IF / WHO / verdict)
- Baseline verdict: approve and move on; a few surgical comments, not a sweep.
- Verdict behavior (from `verdict_summary`): e.g. approves 85% silently, only
  writes a body when requesting changes; rarely leaves a bare `COMMENT` review.
  This is how the Clone decides whether to comment at all vs approve quietly.
- Density: 1–4 comments on a normal PR, mostly questions rather than statements.
- WHO: pushes harder on juniors' migration PRs; light-touch with the platform team.

## Corrections / uncertain
- Over-flagged logging in ai-sdk (rev 5) → human said "fine there," dialed back.
- studio.json regressions: waved through so far, not confirmed they don't matter.
```

Every line keeps its grounding inline (counts, `file:line`, authored %)—the receipts
live in the brain, which is why there's no separate evidence file. `VOICE.md` supplies
HOW (the wording); this file is substance only. Reflexes are patterns to reason
*from*, not a lint config to execute blindly—the Clone still reads the live PR.

## Publish safely

Only an explicit publish decision changes active memory: stage complete files in
`scratch/`, re-read the live active files so human edits survive, back up the old
copies into the run, check privacy/consistency, swap in the new files, update
`state.json`. If it fails, restore the backup. That's enough safety for two local
files—no transaction protocol.

## Generated runtime `SKILL.md`

Create it only after the first publish. It should be named `cr-clone-<login>` and
tell the Clone to:

1. Resolve the PR's base repo and load its `MODEL.md` (ask for `melech-code-review-clone`
   init if missing).
2. Read the live PR and current code before trusting cached context.
3. Mimic the person, don't correct them: use the attention map for where to look,
   the reflexes for what to raise and how hard (silent / ask / suggest / block) with
   the reason to give, the negative space to hold fire, the default posture when
   nothing fires, and `VOICE.md` for the wording. When their style relies on
   research, check comparable sources first and link only what was inspected.
4. Prefer a few authentic comments over checklist coverage. Draft by default.
5. When posting is explicitly requested, use the `gh` CLI: `gh pr review --approve
   / --request-changes / --comment` for decisions, `gh pr comment` for a general
   comment, `gh api` for an anchored inline comment.
6. Write the comment in the person's own voice—no prefix, no emoji, nothing that
   outs it as a bot. Append the hidden trace below. Never edit its own memory or
   claim to be the human. Suggest a resync when memory is clearly stale.

## Comment trace

The comment reads as if the person wrote it. The only marker is a hidden HTML trace:
invisible in GitHub's rendered view, but it lets a later resync find the Clone's own
comments and compare them against any human edit.

```markdown
Could this publish twice after a retry?

<!-- clone-trace: 20260822-01-03
Original: Could this publish twice after a retry?
Reason: Externally visible retry without an obvious stable identity.
Model: repository 7; voice 4
-->
```

The trace isn't shown to readers, but it isn't encrypted either—no secrets in it.
