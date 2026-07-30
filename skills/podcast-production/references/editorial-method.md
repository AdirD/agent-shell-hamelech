# Editorial method

Use this reference to turn transcript evidence into defensible story options. It supports the workflow in `../SKILL.md`; it does not replace the gates there.

## 1. Establish the evidence model

Use this source-of-truth order:

1. Recorded audio for wording, speaker identity, cadence, and sentence boundaries.
2. Timestamped transcript for navigation and rough windows.
3. Untimestamped transcript or notes for discovery only.
4. Public research for context only, never for dialogue.

An automatic transcript can be wrong even when it looks fluent. Preserve recorded wording, including imperfect but intelligible grammar. Punctuation and capitalization may be normalized for readability without changing the words. Do not silently “correct” a name, number, negation, or technical term. Verify it in audio or omit the excerpt.

### Evidence labels

Use the following labels consistently:

| Label | Meaning | Required provenance |
|---|---|---|
| `SPEAKER TURN — VERBATIM` | Recorded words in their original order and meaning | Speaker, source ID, rough source window |
| `CARD — EDITORIAL SUMMARY, NOT SPOKEN` | On-screen text authored by the editorial team | Editorial rationale and, for factual claims, source/citation |
| `NARRATION — EDITORIAL TEXT, NOT SOURCE AUDIO` | Proposed new voiceover | Author/source note and explicit user acceptance |
| `EDITOR'S NOTE — NOT AUDIENCE-FACING` | Production or context guidance | None, but never place it in quotation marks |

Do not use “clean verbatim” as permission to paraphrase. Removing filler inside a sentence can change cadence or meaning and creates discontinuous audio; leave that work to the media editor after word-level alignment.

## 2. Inventory efficiently

Assign stable IDs such as `SRC-01`, `SRC-02`, and `TR-01` rather than relying on ambiguous basenames. For each media source capture:

- original path and whether it is primary, duplicate, proxy, or excerpt;
- duration and usable audio tracks;
- participant layout and speaker/camera mapping if video exists;
- recording discontinuities, dropouts, crosstalk, or music;
- corresponding transcript and its timestamp resolution;
- uncertainty about speaker labels or source synchronization.

Record the target runtime as both a goal and an acceptable range when the user gives one. Record whether cards, narration, cold opens, and reordering are allowed. Do not assume these permissions.

## 3. Build a theme map, then a claim ledger

First map the conversation at section level. For each major stretch record topic, speakers, emotional energy, new information, and dependencies on earlier context. This prevents keyword search from stripping a good quote of the question or qualification that makes it honest.

Then build a compact claim ledger:

| Field | What to record |
|---|---|
| Claim ID | Stable identifier |
| Speaker and role | Who makes or challenges the point |
| Exact candidate phrase | Recorded wording, not a paraphrase |
| Rough source window | Approximate location with timing-quality note |
| Plain-language claim | Editorial summary, labeled as such |
| Why it matters | Audience consequence or stakes |
| Expected or non-obvious | Editorial judgment and rationale |
| Mechanism/evidence | Explanation, example, or firsthand basis in the recording |
| Required setup | Question, definition, qualification, or prior clip needed for fair meaning |
| Host function | Frame, challenge, bridge, synthesis, or none |
| Risk | Privacy, legal, reputational, ambiguity, unsupported inference, or audio issue |
| Confidence | High, medium, or low with reason |

### Find non-obvious claims

A non-obvious claim is not merely a dramatic sentence. Prefer claims that pass several of these tests:

- **Contradiction:** It pushes against the audience's likely default belief.
- **Mechanism:** It explains why or how, rather than only asserting a result.
- **Consequence:** If true, it changes a decision, strategy, or human outcome.
- **Specificity:** It contains a boundary, example, tradeoff, or observable detail.
- **Earned authority:** The speaker grounds it in direct experience or clearly stated expertise.
- **Productive tension:** Another turn questions, qualifies, or reframes it.
- **Human stakes:** It affects agency, craft, identity, relationships, opportunity, or responsibility.

Watch for phrases such as “the surprising part,” “most people think,” “the opposite happened,” “only when,” “what changed my mind,” and “the real constraint.” Treat these as search leads, not proof. A polished slogan without support is usually weaker than a less polished claim with a mechanism.

Separate novelty from sensationalism. Preserve hedges such as “sometimes,” “in our case,” or “I think.” Never promote a limited observation into a universal claim.

## 4. Keep the host meaningfully present

Do not optimize for equal seconds. Optimize for conversational causality: the listener should understand why the guest says what follows and feel that a real exchange shaped the insight.

A host/moderator turn earns its place when it performs one of these functions:

- frames the premise or defines the audience's question;
- asks the question required to understand the answer;
- challenges an assumption or requests evidence;
- reveals a contradiction or raises the stakes;
- bridges two ideas that would otherwise feel spliced together;
- synthesizes a point in a way the guest accepts, refines, or rejects;
- closes on a genuinely shared or productively unresolved insight.

A host turn is expendable when it is only a greeting, backchannel, repeated question, self-contained monologue, or summary the next guest line already supplies. Remove it only if the remaining answer is still truthful and intelligible.

A short cut may contain much less host airtime than guest airtime and still feel hosted. Conversely, several short “right” or “interesting” interjections do not create meaningful presence. Evaluate function, not count or ratio.

For panels and meetings, apply the same test to the facilitator and to participant-to-participant challenges. Do not force every participant into the cut if they do not advance the selected premise, but disclose material speaker omissions.

## 5. Generate three different editorial theses

Generate candidates from different organizing questions, not from different clip orders. Useful arc families include:

- **Belief reversal:** expected view → surprising claim → mechanism → new implication.
- **Problem and mechanism:** concrete pain → failed default → causal insight → practical consequence.
- **Human stakes:** technical or organizational change → effect on agency/craft → responsibility or opportunity.
- **Debate:** host challenge → guest claim → qualification/evidence → unresolved or shared conclusion.
- **Journey:** prior belief/practice → turning point → current view → boundary or next question.

Arc families are prompts, not mandatory formulas. Pick only theses the source supports.

### Distinctness test

Before presenting options, complete a comparison matrix with these rows:

- central audience question;
- one-sentence answer/premise;
- primary non-obvious claim;
- source of tension;
- host's narrative role;
- emotional/intellectual destination;
- opening function;
- ending claim;
- clips unique to the option;
- principal risk/tradeoff.

Two arcs are cosmetic variants if their matrix entries are substantially the same and the main difference is title, ordering, or card wording. Rebuild one around a different thesis. Sharing one unusually strong clip is acceptable when that clip performs a different function in each argument, but explain the reuse.

### Construct the complete reading-order script

For every option, write the entire audience-facing order. Include the opening, setup, transitions, speaker turns, cards or narration, and ending. A synopsis alone hides whether an arc actually listens well.

For each item include:

- sequence number and item type;
- speaker and role when spoken;
- exact recorded text for a speaker turn;
- source ID and rough source window;
- story function;
- context or continuity note;
- card hold or pause estimate when relevant.

Prefer complete recorded phrases. Ellipses must represent a removable pause or omitted complete material, not an unverified word splice. If two non-contiguous excerpts from one speaker are needed, make them separate sequence items so the editor can treat the join honestly.

Choose endings that resolve or productively sharpen the premise. A strong ending often widens from a surprising claim to its human consequence, but only when the recording supports that move. If the user rejects an ending, remove it from active scripts; preserve the decision in the log rather than repeatedly re-proposing it.

## 6. Estimate runtime without false precision

Estimate each option from its full sequence:

$$
\text{runtime} \approx \sum \frac{\text{spoken words}}{\text{speaker words per minute}} + \text{card holds} + \text{intentional pauses/transitions}
$$

Use an observed speaker rate when the source provides a reliable timed passage. Otherwise report a range using a reasonable conversational band such as 130–170 words per minute. Do not claim a single-second result from transcript word count.

Practical method:

1. Count spoken words by speaker.
2. Divide by observed rates, or calculate low/high estimates from the fallback range.
3. Add card reading time. Estimate roughly 2–4 seconds for a short title and longer for dense text; shorten the card rather than forcing an unreadable hold.
4. Add room for breaths, reactions, and transitions. Do not assume jump cuts can remove every pause naturally.
5. Report the spoken subtotal, cards/pauses allowance, estimated range, and target delta.

Runtime is still editorial until exact audio boundaries are aligned. Say “estimated 3:35–3:55,” not “final duration 3:42.”

## 7. Apply privacy, legal, and factual constraints

Translate each user restriction into a scope test. An exclusion such as “remove material about a former employer” can cover:

- employer and subsidiary names;
- product, project, client, partner, or executive names;
- unique job titles, locations, dates, team sizes, milestones, or incidents;
- descriptions that let an informed listener infer the employer;
- judgments, comparisons, or anecdotes whose substance is employer-specific even after names are removed;
- host questions and editorial cards that reintroduce the excluded context.

Apply the test to all options, unused quote banks, recommendations, visual notes, and final handoff. Redaction is not enough when the remaining details identify the subject or preserve the prohibited claim.

Maintain an exclusion register by category, scope, reason, and last audit. Do not copy the restricted phrase into the decision log. When legal/privacy feedback arrives after options exist, invalidate the prior constraint pass and re-audit every eligible item.

Check factual integrity separately:

- keep qualifications and uncertainty;
- do not imply a chronology unsupported by the conversation;
- do not use reaction shots or cards to imply agreement that did not occur;
- do not combine clauses from different moments into a new assertion;
- do not use public research to “complete” what a speaker almost said.

## 8. Iterate without losing decisions

Use a version identifier for each presented state. On feedback, record:

- date/version;
- user direction;
- interpretation applied;
- options or beats retained, revised, or rejected;
- reason and resulting constraint changes;
- whether approval is still pending.

Keep rejected alternatives when they prevent circular discussion or document a meaningful tradeoff. Summarize them at premise level rather than retaining a second full script indefinitely. Retain a full prior script only when the exact sequence is likely to be reconsidered and it contains no restricted material.

Distinguish these user signals:

| Signal | Action |
|---|---|
| “Explore more like option two” | Revise options; approval remains pending |
| “Use this direction but change the ending” | Revise the full script; approval remains pending |
| “This is the one” | Confirm the named version and request explicit approval |
| “I approve Arc B revision 3” | Lock that exact version and prepare the handoff |
| Material change after approval | Reopen iteration and obtain renewed approval |

## 9. Prepare for sentence-level editing

The storyline handoff gives the editor rough neighborhoods, not cut points. A downstream editor should:

- re-transcribe candidate source windows with word timestamps when necessary;
- listen for exact complete-sentence boundaries, breaths, overlap, and room tone;
- match spoken words to the approved verbatim text;
- flag any mismatch that would require an editorial change;
- return for approval rather than silently substituting a nearby cleaner phrase.

This separation prevents a frequent failure: treating a transcript-position estimate as an exact timecode and cutting a sentence too early or too late.