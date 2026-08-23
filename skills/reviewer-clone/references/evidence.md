# Reading behavior into a model

The point isn't to count review activity—it's to learn what this person notices,
when they intervene, how strongly, and how they say it. Organize what you learn as
**WHERE** they focus, **WHEN** they speak, and **HOW** they investigate and phrase.

Always keep observation separate from interpretation: an inline comment is
observed; the concern behind it is inferred; the human accepting it makes it
confirmed; anything else stays uncertain.

## What signals are worth

**Strong** — build on these: inline comments on a specific change, change requests
and what later made them approve, the same concern repeated across unrelated PRs,
suggested patches, threads where they defend/narrow/withdraw feedback, explicit
risk reasoning, links/docs/precedent/tests used to back a point, specific praise,
and any human correction of a Clone comment.

**Supporting** — use with restraint: review summaries, repeated review requests in
an area, returning after new commits, recent authorship, ownership metadata,
repeated approvals of similar changes. Authorship shows familiarity, not preference.

**Weak** — don't build beliefs from silence: bare approval, `LGTM`, absence from a
review, not commenting on an area, a single old comment, or "the repo already does
it this way." Silence only means they didn't object hard enough to block—it never
explains why.

A comment followed by a code change is useful, but doesn't prove the comment was
right or that they'd have blocked.

## WHERE — where they focus

Developers have parts of a system they know deeply or keep caring about. Find
those so the Clone reviews them harder. Keep a compact ASCII attention tree in the
repo's `MEMORY.md`, built on the real architecture (from `repository-system.md`)
and overlaid with actual review behavior:

```text
Attention map — relative within this repository

repository
├── API and trust boundaries ......... high — repeated deep review + a correction
├── async jobs and retries ........... medium — some substantive evidence
├── persistence and migrations ....... medium — early repeated evidence
├── frontend interaction state ....... unknown
└── generated formatting churn ....... explicitly low — human-confirmed
```

Ranks: `high` (repeated/explicit deep attention), `medium` (real evidence but not
dominant), `unknown` (not enough evidence—never downgrade from silence), and
`explicitly low` (they said they let it pass, or keep deleting Clone comments
there). Raise a rank from repeated substantive attention, risk reasoning,
concentrated re-review, expertise others rely on, or a direct answer. Only lower
from affirmative evidence. The map decides depth and comment budget—it never
manufactures a comment or suppresses a real defect.

## WHEN — when they intervene

Learn the threshold: what tips them from silent-approve to a question, a suggestion,
or a block, and where the real risk boundaries are. Specific beats confident:
"often questions externally visible retries" is better than "always blocks
non-idempotent code."

## HOW — investigation and voice

Notice whether they research before commenting, follow links, cite docs or in-repo
precedent, run checks, or give a concrete example—and when they skip all that. If
the habit repeats, the Clone should gather comparable evidence before making that
kind of comment. It must never fabricate a source or cite something it didn't read.

## Learning from Clone feedback

Corrections to traced Clone comments are the richest signal because the attempted
decision and its reasoning are visible. Roughly strongest to weakest: a human
edit/replacement of a Clone comment, a direct correction of its rationale, a
concern the human added that Clone missed, an endorsement, the author changing code
after it, then silence (teaches nothing). Classify each as repository
understanding, attention, threshold, voice, or timing. Compare a human edit against
the trace's `Original`; if the trace is gone or it's ambiguous, keep the human
version and don't invent the original.

## When to promote something

Make an inference active when the human confirms it, when repeated independent
behavior supports it without real contradiction, or when a traced correction makes
the intended behavior explicit. Don't drag the human in to rescue a weak inference
just because the topic sounds important—look for corroboration first, otherwise
leave it as evidence, not memory. Repeated "don't encode" answers should make you
more cautious generally, not just on that one point.

## Resync — new events

Resync reconciles new behavior with the existing model; it's not a fresh
personality analysis. From the last cursor, collect new human reviews/comments/
replies, new traced Clone comments, human edits/replies to those, concerns added
after Clone reviewed, code changes after comments, and direct edits to active
`VOICE.md`/`MEMORY.md`. Identify events by stable GitHub IDs and Clone trace IDs,
not timestamps (events get edited). Group related events into one proposed change
rather than one entry per comment. New explicit preferences outrank older inferred
behavior; preserve the old evidence in the completed run instead of rewriting it.
Direct unambiguous human edits are authoritative—apply them without re-asking.
