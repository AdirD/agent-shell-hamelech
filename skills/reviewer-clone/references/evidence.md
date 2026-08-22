# Evidence model

Phase order, main-agent PR exploration, and parallel repository/voice work live
in `workflow.md`. This file defines what counts as evidence and when an
inference is supportable.

The goal is not to count review activity. It is to learn what this human notices,
why they intervene, how strongly, and how they communicate.

Keep observation separate from interpretation:

- **Observed:** an inline comment, review state, reply, edit, reaction, code
  change, authorship, or repository fact.
- **Inferred:** the concern or preference that may explain it.
- **Confirmed:** the human accepted or supplied the interpretation.
- **Uncertain:** plausible, but not safe to make active yet.

## Strong signals

Prioritize:

- inline comments anchored to a specific changed region
- change requests and the later conditions under which approval appeared
- repeated comments about the same concern across unrelated PRs
- concrete replacement suggestions or suggested patches
- thread follow-ups where the human defends, narrows, or withdraws feedback
- explicit risk explanations
- specific praise for an implementation choice
- human correction, rewrite, rejection, or addition to a Clone review

A comment followed by a code change is useful outcome evidence, but does not
alone prove the comment was correct or that the reviewer considered it blocking.

## Supporting signals

Use with restraint:

- review summaries
- repeated review requests in the same repository area
- returning after new commits
- recent substantial authorship or maintenance in affected code
- repository ownership metadata
- repeated approval of comparable changes

Authorship indicates familiarity more reliably than preference. `CODEOWNERS`
indicates expected attention more reliably than personal concern.

## Weak or ambiguous signals

Do not build beliefs from:

- approval without comments
- `LGTM`
- absence from a review
- not commenting on a changed area
- a single old comment without context
- repository prevalence alone

Silent approval establishes only that the human did not object strongly enough
to block that snapshot. It does not explain disinterest, expertise, perceived
risk, or why they approved.

## Code-area importance

Read `references/attention-map.md` before ranking repository areas. Repeated
substantive attention, detailed risk reasoning, follow-up, and direct human
calibration can raise an area's relative priority. Authorship and ownership are
supporting familiarity signals only.

Never lower an area because the human left no comments there. Use `unknown` until
affirmative evidence shows a lighter review preference.

## Learn from Clone feedback

Clone feedback is especially valuable because the attempted decision and its
rationale are traceable.

Rank it roughly as:

1. Human edits, rejects, or replaces a proposed Clone comment.
2. Human directly corrects the hidden rationale or replies in the thread.
3. Human adds a concern Clone missed on the same PR.
4. Human endorses a Clone comment or repeats its concern independently.
5. The author changes code after Clone feedback.
6. No response.

Classify the correction before updating:

- **Repository understanding:** Clone misunderstood the stack, architecture,
  behavior, convention, or surrounding code.
- **Attention:** Clone cared about something the human would ignore, or missed
  something they would inspect.
- **Threshold:** the concern was real but should have been silent, a question,
  a suggestion, or a blocker.
- **Voice:** the judgment was right but the wording, length, directness, or tone
  was wrong.
- **Timing:** the comment was reasonable historically but the human's current
  preference changed.

If a human edits a Clone comment, compare the visible text with `I wrote:` in the
hidden note. Preserve the human version as current evidence. If the marker was
removed or the edit is ambiguous, do not invent the original.

## Repository context

Read the repository as a system:

- runtimes and major frameworks
- services, packages, and architectural boundaries
- persistence, queues, caches, and external integrations
- deployment and operational shape
- tests, CI, linting, and explicit conventions
- ownership and high-risk areas

Prefer explicit docs/configuration and current live code. Treat repeated existing
patterns as descriptive until human review behavior shows they are endorsed.

Do not turn context into repetitive per-observation qualifiers. Summarize the
repository once in `MEMORY.md`; let the LLM reason from that context.

## Pattern threshold

Promote an inference into active memory when at least one is true:

- the human confirms it directly
- repeated independent review behavior supports it without material
  contradiction
- a traced Clone correction makes the intended behavior explicit

Do not ask the human to rescue a weak inference merely because its topic sounds
important. Search for corroboration and contrast first. If the observation
remains isolated, preserve it as evidence without turning it into either active
memory or a calibration question.

Specificity beats false confidence: "often questions externally visible
retries" is better than "always blocks non-idempotent code."

Calibration choices are also evidence about the trainer's generalization
threshold. Repeated narrowing, concrete-risk requirements, or `do not encode`
answers should make later promotion and question gates stricter across topics,
not only update the individual observations that prompted those answers.
