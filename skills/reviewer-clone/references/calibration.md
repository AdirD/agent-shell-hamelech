# Calibration

Phase order and human-interaction timing live in `workflow.md`. This file defines
what makes a reviewer-fingerprint reflection or question worth interrupting the
human for and how answers change the model.

Calibration should make the human recognize a part of themselves that Clone
actually discovered. It is not a survey and not a way to outsource the
trainer's uncertainty.

## Two kinds of interaction

Training is interactive by default:

- A **confidence checkpoint** reflects the current understanding and asks one
  easy correction question. Its purpose is to reassure the human that training
  understands their repository, voice, attention, or judgment and to redirect
  exploration early when it does not.
- A **behavior-changing calibration** asks whether a pattern should become
  active Clone behavior. It needs stronger corroboration because the answer
  changes future reviews.

Confidence checkpoints may happen before an inference is ready for promotion.
They still require real evidence, a personal and falsifiable reflection, and an
answer that could change what the main agent explores next. They must not become
generic status questions such as “Am I on the right track?”

Use this default cadence:

- first checkpoint as soon as repository/voice analysis supports a personal
  reflection, or after the first two deep reads
- another checkpoint before more than three additional deep reads pass without
  human interaction
- ask sooner when a meaningful insight, contradiction, or likely
  misunderstanding appears
- always checkpoint before proposing publication

Each checkpoint contains one reflection and one question, never a batch.
Prioritize whichever dimension has gained meaningful evidence since the last
interaction; do not force a fixed rotation.

Keep this cadence unless the human explicitly asks for a quieter run. Do not
silently reduce confidence checkpoints merely because earlier hypotheses were
rejected.

## Learn before behavior-changing calibration

When one review creates a tempting hypothesis:

1. Keep it tentative.
2. Search for the same behavior in independent PRs.
3. Search for a near-neighbor where the human acted differently.
4. Inspect replies, re-review, and wording for the boundary.
5. Ask only if the remaining distinction is both high-leverage and not
   answerable from available evidence.

A single recording request, terse process comment, isolated code suggestion, or
domain-specific concern is usually evidence to search—not a personal policy to
calibrate. Do not ask the human to turn an anecdote into doctrine.

Direct corrections to a traced Clone comment are different: they already expose
the attempted behavior and the human's response. Apply an unambiguous correction
without asking the human to confirm it again.

## Find the reviewer fingerprint

Do not present observations one by one. Synthesize the non-obvious relationship
between them:

- what the human challenges versus deliberately tolerates
- which kinds of uncertainty trigger questions versus silence
- where their threshold changes despite similar objective risk
- what they seek proof for and what they accept on judgment
- how attention, intervention threshold, and voice combine

The useful unit is an asymmetry or trade-off, not a topic. `Cares about retries`
is generic. `Challenges unverifiable claims more readily than hypothetical
complexity` begins to describe a person.

Use matched contrasts where possible: comparable changes that received
different substantive treatment, comments that were defended versus withdrawn,
questions that escalated versus approvals that followed an explanation. A
bodyless approval or silence cannot supply the negative side of a contrast.

## Behavior-changing question gate

A candidate question should pass all of these:

1. **Corroborated:** normally supported by at least two independent PRs, a
   meaningful contradiction, or direct feedback on a traced Clone comment.
2. **Distinctive:** it would distinguish this human from a competent generic
   reviewer.
3. **Behavioral:** each plausible answer would make Clone review a meaningful
   class of future changes differently.
4. **Personal:** it combines the human's demonstrated attention, tolerance,
   threshold, or voice instead of asking for generic engineering policy.
5. **Unresolved:** another targeted GitHub search is unlikely to answer it.
6. **Timely:** resolving it matters to the current training model or an imminent
   review, not a rare hypothetical.

If any test fails, do not promote the pattern through calibration. The main
agent may still use a confidence checkpoint to show its tentative read and ask
which direction deserves more evidence. Importance-sounding subject matter does
not make a weakly supported rule safe to activate.

One earned question is better than three reasonable questions. Ask two together
only when both independently pass the gate and neither can bias the other.
Never fill a batch because the interaction cadence is due.

## Reflect before asking

Lead with the personal synthesis. The question comes second:

> Across several reviews, you let unfamiliar machinery stand when there was no
> concrete failure path, but stopped when code relied on an external fact the
> repository could not prove. My read is that you review **claims** harder than
> **complexity**: complexity can earn its place later, while an unverifiable
> assumption makes the current change untrustworthy.
>
> Is that asymmetry actually part of how you review?

Then offer concrete boundaries that change future behavior:

- `Yes—ask for provenance when correctness rests on an unproven external fact,
  but do not challenge complexity without a concrete failure path`
- `Only apply that to contracts crossing a service or trust boundary`
- `The common factor is blast radius, not whether something is a claim`
- `This is not stable enough to teach Clone yet`

The human should be able to think, “that sounds like me,” before choosing.
Historical links are optional provenance, not required reading.

A confidence checkpoint uses the same reflection-first shape but can stay
tentative:

> So far, I see event publication as an irreversible boundary you inspect
> closely, while internal retry machinery gets attention only when there is a
> concrete duplicate effect. That may be an early sample rather than a stable
> rule.
>
> Is that a useful direction for the next PRs, or should I test a different
> boundary?

For voice:

> Your comments usually open with the failure case rather than a severity label,
> and explanation appears only when the failure path is hidden.
>
> Does that sound representative, or is this sample making you look terser than
> you are?

For attention calibration, reflect a meaningful relationship rather than asking
for a repository ranking:

> Clone sees repeated deep reasoning at trust boundaries and only tentative
> evidence around interface state. That may mean you allocate attention by
> irreversible blast radius rather than by layer. Should that steer review
> depth, or is the sample still misleading?

## Avoid generic policy interviews

Do not ask:

- when Clone should request one artifact seen in one review
- how Clone should handle one terse process action
- generic best-practice questions that could be asked of any engineer
- “What should Clone do?” without first showing a personal synthesis
- questions whose answer would affect only one narrow or unlikely scenario
- questions available repository or GitHub evidence can answer
- “Why did you write this?” or anything requiring memory of an old PR
- “Does this look right?” without first showing what Clone currently understands

Do not mark a weak inference `(Recommended)`. Recommend an answer only when the
evidence is strong enough that choosing another option would teach Clone
something genuinely new.

## Learn from calibration behavior

The pattern of answers is evidence too. If the human repeatedly:

- narrows proposed rules
- requires a concrete failure path
- chooses `do not encode`
- rejects topic-level generalizations
- corrects recommendations in the same direction

learn that meta-preference. Raise the evidence threshold, search for more
contrasts, and ask fewer behavior-changing calibration questions. Keep
confidence checkpoints on cadence unless the human asks for less interaction.
Do not record only isolated rule corrections and then repeat the same synthesis
mistake in the next exploration.

If several recommendations are rejected or narrowed in the same direction,
treat that as a trainer miss. Record why, change which PR or focused exploration
the main agent selects next, and do not produce more questions from the same
reasoning pattern.

## Ask and apply

Use the structured `AskQuestion` tool when available. Use one answer per
question unless choices can truthfully coexist. The tool supplies `Other`; do
not duplicate it.

Write choices as first-person behavior, not labels such as `broad`, `narrow`, or
`wrong`. If the tool is unavailable, show the same compact choices in the
conversation.

Current explicit answers outrank historical inference. Preserve older evidence
in the completed run rather than rewriting it to appear consistent.

After an answer, immediately show only the useful effect:

```text
Clone now understands
- ...

Clone will stop assuming
- ...

Still uncertain
- ...
```

If the answer revealed a trainer miss, say so plainly and explain how the next
exploration will search differently.
