---
name: melech-babysit
description: Keep a PR moving through review, conflicts, and CI until merge-ready.
disable-model-invocation: true
---

# Babysit PR

## What The User Is Trying To Achieve

The user opened a PR and wants it merged without hand-holding every 30 seconds.
Between iterations the world moves: teammates comment, the base branch
advances, CI reruns, review bots (Bugbot, CodeRabbit, and friends) post new
findings. A one-shot check goes stale within minutes.

Your job is to keep the PR in "merge-ready" state on a recurring cadence until
it merges, the user stops you, or something genuinely needs them.

## Loop Or You're Useless

Default cadence: **every 5 minutes**. Accept overrides like
`melech-babysit every 10m` or `melech-babysit 2m`.

Arm the loop before doing anything else:

- If the user has a `/loop` primitive in their setup, invoke it:
  `/loop 5m melech-babysit <PR ref>`.
- Otherwise arm a background heartbeat with a unique sentinel and monitored
  output, then run one immediate iteration.

One iteration doesn't count as babysitting. If you can't loop, say so and
stop — don't pretend a single pass is enough.

## Per Iteration

Do these in order. Skip a step only if the previous one produced a hard
blocker.

1. **Refresh state.** `git fetch`, pull the PR branch, check whether base has
   advanced. Never trust cached PR data older than the last tick.
2. **Merge conflicts.** Resolve them intelligently, preserving intent on both
   sides. If intents genuinely conflict, abort the merge and surface the
   specific hunks to the user — do not guess.
3. **Comments.** Fetch only unresolved review threads. For each, read only the
   comment body and the minimum location needed to act. Validate before
   changing code — review bots are often wrong on intent. If you disagree,
   reply with the reasoning instead of silently ignoring. Never mass-resolve
   threads.
4. **CI.** Only fix failures caused by this PR's diff. Never edit workflow YAML
   or unrelated code just to make a check green. If a merge-blocking check
   looks unrelated, first try merging latest base — another PR may have fixed
   it. If it's still red and out of scope, stop and report.
5. **Push scoped fixes** and let the next tick verify.

## When To Stop On Your Own

- PR is mergeable, CI is green, no unresolved threads → announce ready, then
  stop the loop.
- A step needs a product / design / security decision only the user can make
  → stop the loop and hand back with a clear question.
- Same failure repeats across 3 consecutive ticks with no progress → stop and
  report; you're spinning.

Always kill the loop process when stopping. A silently-alive heartbeat is
worse than no babysit.

## Between Ticks

Keep tick reports short. On each wake, say what changed (new comments, CI
delta, new commits on base) and what you did. Don't reprint the whole PR
state.

## Do / Don't

**Do:** "Tick 3 — CI now green, one Bugbot thread left. It's asking for a null
check; the code already handles that case at line 42. Replied on the thread,
didn't change code."

**Don't:** Silently mark a review bot's request "resolved" because it's
inconvenient.

**Do:** "Base advanced by 4 commits, one of them fixed the flaky
`api-integration` job. Merged base into the branch, checks re-running."

**Don't:** Edit `.github/workflows/*.yml` to skip a failing check.

**Do:** "Two ticks in a row the `db-migration` job fails with the same
timeout. This isn't a code fix I can make from here. Stopping the loop —
can you check the migration or bump the timeout?"

**Don't:** Keep looping on a failure you clearly cannot fix.
