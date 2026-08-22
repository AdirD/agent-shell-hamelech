# Resync evidence and reconciliation

Phase order, run recording, parent-led interpretation, parallel factual
collection, publication, recovery, and reporting live in
`workflow.md`. This file defines which incremental events matter and how to
interpret them against current Clone memory.

Resync is not a fresh personality analysis. It reconciles new behavior with the
current model while preserving explicit corrections and uncertainty.

## Incremental event surfaces

From the last successful cursors, collect:

- new human reviews, inline comments, replies, and review submissions
- new Clone comments identified by `🤖 Clone:` plus the hidden
  `Clone note for you` trace
- human edits, replacements, replies, or reactions to traced Clone comments
- human concerns added after Clone reviewed the same PR
- commits or diff changes following review comments
- thread resolution, approval, dismissal, merge, or close outcomes
- direct human edits to active `VOICE.md` or `MEMORY.md`

Revisit previously open PRs whose observable state changed. Use stable GitHub
event IDs and Clone trace IDs for identity; timestamps are collection
boundaries, because events may be edited after creation.

When one GitHub account authors both human and Clone comments, the durable hidden
trace determines Clone origin. An unmarked comment remains human evidence. Emoji
alone is not a machine identifier.

## Reconciliation questions

For each meaningful event, determine:

1. Did repository understanding change?
2. Did the human reveal what deserves attention?
3. Should a code area move in relative attention?
4. Did the intervention threshold change?
5. Was judgment right but voice wrong?
6. Is this a current preference replacing an older one?
7. Is the outcome too ambiguous to learn from?

Group related events into one proposed learning. A resync should not create one
memory entry per comment.

## Human review of Clone

This is the strongest resync source because the attempted behavior and its
rationale are traceable:

1. A human rewrite/replacement teaches judgment and voice.
2. A rejected comment usually narrows or removes an instinct.
3. A human-added missed concern teaches attention.
4. A reply to hidden rationale identifies which assumption failed.
5. Explicit endorsement reinforces the current model.
6. Author code movement suggests impact, not human endorsement.
7. Silence teaches nothing.

Compare a human edit with the hidden trace's original `I wrote:` text. If the
trace disappeared or the edit is ambiguous, preserve uncertainty instead of
inventing the original.

Direct, unambiguous corrections can be applied without asking the human to
confirm them again. Broader inferences still need the support described in
`evidence.md`.

## Timing and replacement

New explicit preferences outrank older inferred behavior. Preserve older
evidence in the completed run rather than rewriting it to appear consistent.

Classify whether the difference is:

- a corrected repository fact
- a narrower/broader attention boundary
- a different intervention threshold
- a voice-only correction
- a changed preference over time
- unresolved ambiguity

Treat direct human edits to active memory as authoritative input. Resync results
must surface them rather than presenting the older generated revision as truth.

## Factual feedback collection result

A focused collector may save the following observed facts:

```markdown
## Scope
- Cursor range, PRs revisited, events fetched, gaps/failures.

## Apparent direct corrections
- Trace/source IDs, original Clone text, human replacement or response.

## Human concerns after Clone
- Human concern after Clone review and anchored context.

## Explicit reinforcement
- Explicit endorsement or independent repetition.

## Observable outcomes
- Code/thread/review movement without an interpretation of preference.

## Contradictions and limits
- Existing memory challenged and what remains ambiguous.
```

Give the collector the prior cursor, relevant trace IDs, and one complete output
path. Run it fresh and deduplicate events by stable IDs.

The collector does not classify what the events teach. The main agent reads the
traced comments and surrounding PR evidence, decides whether the change concerns
repository understanding, attention, threshold, voice, timing, or nothing
learnable, and reconciles it with all completed evidence.
