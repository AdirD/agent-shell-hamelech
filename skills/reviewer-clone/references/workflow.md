# Reviewer Clone workflow

This is the flow. It's a guide, not a script—use judgment. The goal is to learn
how this person reviews (WHERE they focus, WHEN they speak, HOW they work), check
it with them, and save it as a Clone that reviews like them.

## Who does what

You (the main agent) run the whole thing: pick the repo with the human, run the
collectors, choose and deeply read PRs, talk to the human, decide what's learned,
and publish. Deep reads and learning are always yours.

Hand off only bounded, independent work to subagents:

- map the chosen repository → `repository-system.md`
- study how the person writes and investigates → `voice.md`
- go fetch one missing fact or find candidate contrasting PRs

Give a subagent a complete prompt, one output, and let it run fresh. It doesn't
touch active memory, interview the human, or decide anything. If it fails, run it
again. Use a cheap fast model for mechanical mapping/search, a stronger one when
wording and interpretation matter.

## Progress

Track progress with todos, not narration:

```text
Offer recent repositories and let the user choose
Create or resume the training run
Collect activity and start repository/voice analysis
Explore PRs and learn iteratively
Choose whether to continue or publish
Publish the reviewer Clone
Report the result
```

Keep one in progress; on the exploration step, append the deep-read count and what
you're checking next. Between routine tool calls, say nothing—let the todos talk.

## 1 — Pick the repo

Usually already done from `SKILL.md`'s quick-start—if so, skip to step 2 and don't
re-run the queries. If not: resolve the login, run the two `jq`-aggregated queries
in `github.md`, offer the top few, let the human choose. Keep it cheap—just the
menu, no code inspection or history crawl.

## 2 — Create or resume the run

Find `~/.agents/skills/cr-clone-<login>`. Decide from its state whether this is a
fresh init, a new repo, a resync, or a no-op. Make a run directory with a real UTC
timestamp (see `output-contract.md`). Don't rebuild existing memory just because
someone said "init"—that needs explicit confirmation.

## 3 — Collect and start parallel analysis

Kick these off together:

- run `collect-review-activity.py` yourself, save output to the run's `scratch/`
- dispatch **Map repository system** → `repository-system.md`
- once the activity index exists, dispatch **Analyze review method and voice** →
  `voice.md` (studies both wording and how they back up claims—links, research,
  in-repo precedent, tests, examples)
- on resync, also dispatch **Collect Clone feedback** to gather traced comments,
  human edits/replies, and missed concerns

Don't wait on those. Build a menu of ~8–12 promising PRs from the activity: real
inline comments, change requests, follow-ups, praise, comments backed by research
or links, and repeated activity in one area. Spread across areas, authors, and
time. It's a menu, not a commitment.

## 4 — Explore PRs and learn

Loop, one PR (or a matched pair) at a time:

1. Pick something that can establish, contrast, or challenge a pattern.
2. Run `collect-pr-evidence.py` for it.
3. Read it yourself—diff, live code, what the human actually did, the thread,
   later changes, outcome.
4. Jot a short source-backed note in `EVIDENCE.md` (see shape below).
5. Update your picture of WHERE / WHEN / HOW and what's still unclear.
6. Ask the human when their answer would actually change the model or your next move.
7. Decide: contrast it, explore further, pick another, or propose stopping.

Evidence note shape:

```markdown
## PR #...
- Observed: exact action/comment + GitHub ID.
- Context: only what's needed to understand it.
- Outcome: reply, edit, code movement, final state.
- Read: what it suggests (as inference) and what it can't prove.
```

Repository and voice jobs keep running in the background—don't block on them.

## Calibrate with the human

Calibration is an interview with a senior engineer about how they review. Use
`AskQuestion` with title `Calibrate Clone`, one to three questions, only when a
real fork exists. Every good question follows the same shape:

**[a concrete thing you actually saw them do, named] → [your read of it] → lock it
in / correct me.**

The "aha" comes from naming the real thing—the actual package, file, framework, or
area from the collector data (`ai-sdk`, `studio.json`, migrations, the retry code),
not a generic reviewer trait. "You push back on abstractions" is a horoscope that
fits everyone; "you're all over the `ai-sdk` tool-calling code" is personal.

Rules for a golden question:

- **Name a real artifact** from their activity. No generic archetype questions.
- **It's a pattern across PRs**, never "on #163." Named area ≠ single incident.
- **One-line premise, then the fork.** Don't write a setup that already answers it.
- **2–4 clean, non-overlapping options**—each a different reviewer, recognizable
  instantly. Not a `block / suggestion / ask / don't encode` config ladder.
- **Only ask a genuine fork.** If you already know the answer, it's a reflection
  for the summary, not a question. Don't recommend an option on a real fork.

The golden set (fill the names from real data):

```text
WHERE — home turf (high, well-evidenced → confirm the bar):
You're all over anything touching the ai-sdk tool-calling code — deep comments,
follow-ups, you defend your takes. Reading that as your home turf. Want Clone to
go hard there and lower its bar to speak up?
- Yeah, lock it in — that's my area
- I know it well but don't over-scrutinize it
- Nah, that was just these PRs
```

```text
WHERE — silence fork (an area they DON'T comment on is ambiguous → ask):
Changes to studio.json / generated config mostly sail past you with no comment.
Is that "I trust it, skim it" or just "those PRs didn't need me"?
- Trust it — Clone can go light there
- Didn't come up — don't downgrade it
- Actually I'd want regressions there caught
```

```text
WHEN — grounded in a real area:
On DB migrations you always dig into rollback + backfill order. Is that a hard
gate for you, or you raise it and trust the author?
- Hard gate — I don't approve migrations without it
- I push hard but won't block on it
- Case by case
```

```text
HOW — grounded in a real habit:
When you flag retry/idempotency stuff you link the queue docs or a past incident.
Want Clone to dig up that kind of proof before commenting, or just raise it?
- Dig it up — don't make that claim bare
- Only for the non-obvious ones
- Just raise it, I'll get the proof myself
```

Some sessions produce zero real forks—that's fine. Ask again later only when new
evidence raises a genuine uncertainty. Always show the current model before
publishing and ask anything still open that could change it.

## 5 — Keep the model compact

After each deep read: separate what you saw from what you infer (`evidence.md`),
prefer matched contrasts over topic counts, overlay demonstrated interest/expertise
onto the repo architecture, and update WHERE / WHEN / HOW / uncertainty. Explicit
human answers and direct edits win. Record only material changes in `RUN.md`. The
repo and voice artifacts are inputs—you decide what enters active memory.

## 6 — Let the human choose depth

Before proposing to publish, show the current model and the important unknowns:

```text
WHERE — where they focus: ...
WHEN — when they intervene: ...
HOW — how they investigate and write: ...
Narrowed / unlearned: ...
Still uncertain: ...
```

Propose stopping when recent diverse reads keep reinforcing the same picture and no
open contradiction seems likely to change reviews. That's judgment, not a formula.
Show honest counts (indexed / comments swept / evidence fetched / deep-read) and
let the human publish, keep exploring, deep-dive a named area, or pause. Stopping
is not permission to publish.

## 7 — Publish

Only an explicit publish choice changes active memory. Then: record the accepted
learning and source IDs in `RUN.md`, stage complete `VOICE.md` and `MEMORY.md` in
`scratch/`, re-read the live active files so human edits aren't clobbered, check for
privacy and contradictions, back up the old copies into the run, swap in the new
files, and update `state.json`. If it fails mid-way, restore the backup and report
it. A paused or failed run resumes from `RUN.md` and `EVIDENCE.md`.

## Wrap up

Report: status (initialized / resynced / no-op / paused / failed), honest coverage
counts, why you stopped and what the human chose, the accepted WHERE/WHEN/HOW and
anything unlearned, and the Clone + run paths. The Clone is a transparent,
correctable stand-in—never claim it's the person.
