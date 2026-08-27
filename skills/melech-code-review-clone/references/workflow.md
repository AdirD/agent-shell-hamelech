# Reviewer Clone workflow

Learn how one person reviews PRs, then save that as a Clone that reviews new PRs the
same way. Two principles:

- **Mimic, don't fix.** Clone their real themes and biases—what they obsess over,
  wave through, and push back on. Never impose your own "best practices."
- **Correlate, don't narrate.** Learn from many small comments, each checked against
  the actual code it was written on—never from re-reading whole PRs (that overfits).

## What you're learning: the lenses

You're building one thing—a model of how this person reviews—looked at through these
lenses. Use what fits; don't force a rigid matrix. This is the only place they're
defined. For every lens, the *negative space* is signal too: what they wave through
tells you as much as what they flag, so capture both sides.

- **IF** — do they weigh in at all, or wave it through
- **WHAT** — the concerns they keep flagging vs the ones they never raise
- **WHERE** — the parts of the system they dig into and own vs the parts they skim
- **WHEN** — how far they take it: a question, a suggestion, a hard block—or silence
- **WHO** — whose PRs they push on vs whose they wave through, if it recurs
- **WHY** — the reason under the comment (risk, data loss, maintainability, cost…)
- **HOW** — tone, and whether they research / link / cite. This is their voice.

Absence is a real part of the picture, but it's ambiguous—"didn't comment" can mean
"trusts it" or "those PRs just didn't need me." So paint both sides, then treat the
gaps as questions to confirm, not proof they don't care.

There's just one model file, `MODEL.md` (plus `VOICE.md` for the cross-repo voice).
You build it up as you read—draft in the run's `scratch/`—and publish it only when the
human says so. Each claim carries its own grounding inline (the comments + code + git
that back it), so there's no separate "evidence" file. `RUN.md` is the run's journal
(what each chunk added, decisions); `state.json` tracks what's been processed so a
resync resumes where you left off.

## How the run goes

```text
1. WHERE AM I   Find the repo + GitHub user from the current folder (no menu).
       │
2. SET UP       Open this person's training folder (start fresh or continue an old one).
       │
3. GATHER       Download every review comment they left here (split into chunk-files),
       │        and in parallel read the code + git to see what they wrote and own.
       │
4. LEARN  ┌───► Read the comments one chunk at a time, filling in the model above.
       │  │     When a pattern looks real, open the code they commented on to confirm.
       │  │     When a real fork appears, ask them a sharp question right there.
       │  └──── Repeat until new chunks stop teaching you anything.
       │
5. DECIDE       They pick: save it / keep going / pause.
       │
6. SAVE         Write the model to files the Clone can reuse, then report.
```

You (main agent) do all the thinking, and run the quick read-only git/code lookups
yourself. Offload to a fresh subagent (cheap fast model, full prompt, one job) only
for genuinely heavy read-only work; it never decides anything or touches saved memory.
If one fails, dispatch it again.

Surface these six as todos, one in progress at a time; while reading chunks show
which (e.g. "chunk 6 of 11"). Between routine tool calls, say nothing.

## 1 — Find the repo and user

The repo is wherever the skill runs. Don't ask.

```bash
gh api user --jq .login
git -C . remote get-url origin      # → canonical owner/repo (base, not a fork head)
```

Only if there's no remote, ask the user for `owner/repo`.

## 2 — Open the training folder

In `~/.agents/skills/cr-clone-<login>`, decide from what's already there whether
this is a first-time run, an update of an existing one, or nothing-to-do. Make a run
dir with a real UTC timestamp (`output-contract.md`). Don't wipe existing memory
just because someone said "init"—that needs explicit confirmation.

## 3 — Gather comments, scan ownership (parallel)

Run the collector yourself (don't reinvent it in shell):

```bash
python3 "$REVIEWER_CLONE_SKILL_DIR/scripts/collect-review-activity.py" \
  --repo "$OWNER/$REPO" --login "$LOGIN" \
  --output "$RUN/scratch/review-activity.json"
```

It grabs every interaction point the person left on PRs, each tagged with a
`kind` and an `as_author`/`as_reviewer` side:

- **inline** review comments (file + line) and **inline_reply** threads;
- **conversation** (non-inline) comments, including on their own PRs;
- **review_summary** verdicts—approve / request-changes / comment plus any body.

It splits the ones with words into small chunk-files
(`scratch/comments/batch-*.json`) and counts areas (`area_counts`), kinds
(`kind_counts`), and author-vs-reviewer side (`author_side_counts`). Wordless
verdicts (silent approvals) carry no text to batch, so they land in
`verdict_summary` instead—read it for the person's **default posture**:
`silent_approval_ratio`, state breakdown, how often they attach a summary body.
Read `review-activity.summary.json` first—these counts give you **WHERE**,
**WHEN**, and the IF/silence picture over everything, not a sample. Silent
approvals need one API call per reviewed PR, so they're capped to the most
recent `--reviews-cap` PRs (default 300); `verdict_summary.cap_applied` tells you
if older reviews were skipped. If it fails, fix args/auth and retry once; don't
improvise a big script.

While the collector runs, scan ownership yourself in one pass so you know which areas
this person actually *wrote*, not just commented on:

```bash
git -C . shortlog -sne --all | head            # who authors the most, overall
git -C . log --author="<login>" --oneline | wc -l   # their footprint
```

That's the ownership half of **WHERE**; `area_counts` is the attention half. You don't
need a full architecture write-up—just enough to overlay ownership on attention.

## 4 — Build the model, chunk by chunk

Read one chunk-file at a time, filling in the lenses in the draft `MODEL.md`
(`scratch/`). Never load every comment at once, and never conclude from a single
comment. For each chunk, in order:

1. Read it (~40 interaction points). Each carries a `kind` and side: inline
   review comments have a file/line; `inline_reply`/`conversation` points marked
   `as_author` are them answering feedback on their *own* code (a different voice
   from reviewing others'); `review_summary` points carry the verdict `state`.
2. Add what's new to your notes; note what just repeats what you knew. Read
   author-side replies for voice under pushback (do they concede, defend, cite?),
   not for review reflexes.
3. When a pattern looks real, open the actual file they commented on and check git:

   ```bash
   git -C . log --author="<login>" --oneline -- <path>   # do they write here?
   git -C . blame -L <line>,+1 -- <path>                  # who owns this line
   git -C . log --oneline -n 5 -- <path>                  # how often it changes
   ```

4. Jot the delta in `RUN.md` ("chunk 5: +1 recurring concern, nothing else").

**Stop early when it stops paying off:** if 2–3 chunks in a row add nothing new,
you've seen enough—move to the questions even if chunks remain (a later run resumes
from where you left off). Reading all chunks is fine too.

What to trust: the same concern across unrelated PRs, suggested fixes, links/precedent
they cite, specific praise, human corrections of a Clone comment, and areas they both
wrote and commented on. The **aggregate** verdict pattern is also trustworthy—a high
`silent_approval_ratio` over hundreds of reviews is a real default posture, and a
consistent "always writes a one-line summary when blocking" is a real delivery habit.
Weak—never a conclusion on its own: a *single* bare approval, "LGTM", or one silent
merge—an area they didn't comment on is a question to ask, not proof they don't care.
Only save something as learned when the human confirms it, the behavior repeats
independently (or shows up strongly in `verdict_summary`), or a correction to a Clone
comment makes it explicit.

While reading, draft freely by lens—that's how you think—each claim carrying its
grounding inline (this *is* the receipts):

```markdown
## WHAT — recurring themes
- "await / use a queue" — 31 comments / 22 PRs; grounded `packages/ai-sdk/tools/run.ts:44`
  (they author it) → strong WHEN gate?

## WHERE — focus + ownership
- packages/ai-sdk: 120 comments, ~70% authored → high
- apps/studio (studio.json): 3 comments, heavy churn → unknown (silence fork)
```

These are your working notes, filed by lens. At publish (step 6) you reshape them into
the brain the Clone actually reads—attention map, reflexes, negative space, default
posture—per `output-contract.md`. Lenses are how *you* learn; reflexes are how *it* acts.

### Ask when a real fork appears

This is where the skill earns its trust. A great question makes the human go **"whoa,
it gets me—I *do* review like that."** You're holding up a mirror: naming a reflex of
theirs, in their own repo, that they act on but maybe never spelled out. The best ones
name a pattern they hadn't consciously noticed—then instantly recognize as themselves.
Get this right and everything else is forgivable; get it generic and the Clone feels
like a bot.

Calibration isn't a phase after learning—it happens inside the loop. When a chunk
raises a genuine fork you can't settle from evidence, stop and ask right there, then
keep reading. `AskQuestion` titled `Calibrate Clone`, 1–3 questions, **only when a real
fork exists**. Learn the shape from the contrast (fill names from real data):

```text
❌ "You push back on abstractions. Want Clone to flag over-engineering?"
   horoscope — abstract, unnamed, true of everyone. no aha.
✅ "You author most of the ai-sdk tool-calling code and comment on it heavily —
   reading that as your home turf. Want Clone to go hard there and lower its bar?"
   - Yeah, lock it in — that's my area
   - I know it well, don't over-scrutinize it
   - Nah, that was just these PRs
```

```text
❌ "On #163 you flagged the un-awaited sandbox call — was that a big deal?"
   a memory quiz about one incident. they won't even remember it.
✅ "Across PRs you keep catching un-awaited queue writes (e.g. run.ts:44). A hard
   gate for you, or something you raise and trust the author on?"
   - Hard gate — I don't approve without it
   - I push hard but won't block
   - Case by case
```

```text
❌ "How should Clone treat studio.json? block / request-changes / suggest / ask / ignore"
   a config ladder in robot-speak; pre-answers nothing real.
✅ "Changes to studio.json mostly sail past you with no comment. Is that 'I trust it,
   skim it' or just 'those PRs didn't need me'?"
   - Trust it — Clone can go light there
   - Didn't come up — don't downgrade it
   - Actually I'd want regressions there caught
```

Zero forks in a session is fine. Ask again only when new evidence raises a real
uncertainty.

## 5 — They decide

Show them the model you built and what's still open, with honest counts (comments
downloaded / chunks read of total / codebase mapped). Suggest stopping when more
chunks keep confirming the same picture and no open question would change how reviews
go—your judgment, not a formula. They pick: publish, keep going, look harder at a
named area, or pause. Stopping is not the same as permission to publish.

## 6 — Save and report

Only an explicit "save/publish" choice changes what the Clone actually uses. Record
the accepted learning + source IDs in `RUN.md`, then reshape your lens-notes into the
finished `VOICE.md` and `MODEL.md` (the brain format in `output-contract.md`, written
for the Clone) in `scratch/`, re-read the live files so any hand-edits survive, back
up the old copies, swap in the new, update `state.json`. If it fails partway, restore
the backup and report. A paused/failed run resumes from `RUN.md` + the draft
`MODEL.md`.

Then report: status, honest coverage, why you stopped and what the human chose, what
was learned (the model + their voice) and anything dropped, and the Clone + run paths.
The Clone is a transparent, correctable stand-in—never claim it's the person.

## Resync (updating an existing Clone)

Don't start over. Only look at comments and Clone-feedback newer than the last run
(match by GitHub/trace IDs, not timestamps), read those new chunks, and fold them into
the saved model. The strongest signal is the human editing or rejecting one of the
Clone's own comments (matched by the hidden `clone-trace` marker)—compare it against
the original the Clone recorded.
Anything the human typed directly into `VOICE.md`/`MODEL.md` wins.
