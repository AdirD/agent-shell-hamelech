# Podcast Storyline

Turn long recorded conversations into a source-grounded storyline the user chooses. This is the editorial stage, not the video-editing stage.

## Load the supporting resources

- Read [references/editorial-method.md](../references/editorial-method.md) before analyzing themes or proposing arcs. It contains claim, host-presence, runtime, distinctness, research, and legal/privacy methods.
- Use [templates/editorial-options.md](../templates/editorial-options.md) when creating or revising `editorial-options.md`.
- Use [templates/approved-script.md](../templates/approved-script.md) only after explicit approval, when writing `approved-script.md`.

## Non-negotiable editorial rules

1. **The recording is the authority.** A transcript is an index and may contain recognition, speaker, punctuation, or timing errors.
2. **Never fabricate dialogue.** Every speaker turn in a proposed or approved script must be a phrase actually recorded by that speaker. Do not silently rewrite grammar, splice words into a new sentence, or put a paraphrase in quotation marks.
3. **Label authored material.** Mark non-recorded text as `CARD — EDITORIAL SUMMARY, NOT SPOKEN` or `NARRATION — EDITORIAL TEXT, NOT SOURCE AUDIO`. Mark production guidance as an editor's note, never as dialogue.
4. **Treat source windows as rough editorial estimates.** Format them with `~` and the note `editorial estimate; align against timestamped audio`. Do not call transcript-position estimates exact, frame-accurate, or final in/out points.
5. **Keep the user in control.** Present options, revise collaboratively, and obtain unambiguous approval of a named version before creating `approved-script.md`. Preference, praise, or revision feedback is not approval.
6. **Apply exclusions globally.** Privacy, legal, confidentiality, or employer/client restrictions cover every active option, quote bank, recommendation, note, and handoff—not only the most obvious name.
7. **Do not edit or render media in this skill.** After approval, produce the handoff and stop. The editor must re-align sentence boundaries from timestamped audio before cutting.

## Artifacts and state

Write artifacts in the user's chosen project/output directory:

| Artifact | When | Purpose |
|---|---|---|
| `editorial-options.md` | During discovery and every iteration | Source inventory, constraints, analysis, three options, complete reading-order scripts, comparison, recommendation, and decision log |
| `approved-script.md` | Only after explicit approval | Stable handoff containing the selected source-grounded sequence and approval record |

Keep rejected options in the decision log when they explain a useful choice. Preserve their premise, version, and rejection reason; do not repeat text excluded for privacy or legal reasons.

## Workflow and gates

Do not skip a gate. If evidence is insufficient, state what is missing instead of filling the gap with plausible language.

### Gate 1 — Inventory the source set

Locate and inspect the available media, transcripts, notes, and prior constraints. Record:

- stable source IDs and paths;
- media type and duration;
- speakers and roles, including uncertain identities;
- transcript path, format, timestamp granularity, and whether it is automatic or human-reviewed;
- audio/video layout, duplicate or partial sources, and obvious quality limitations;
- intended audience, target runtime, delivery format, and known privacy/legal limits.

**Pass when:** every source used later can be named unambiguously, transcript timing quality is described honestly, and missing information that could change the story is visible.

### Gate 2 — Analyze transcript and themes

Read the conversation in context, not as isolated keyword hits. Build a working theme map and claim ledger using the method reference. Identify:

- expected points versus non-obvious, consequential claims;
- tensions, reversals, mechanisms, boundary conditions, and human stakes;
- complete candidate phrases with enough setup to preserve their meaning;
- host/moderator turns that frame, challenge, synthesize, or redirect;
- sensitive material and claims that need qualification.

Use transcript positions only to create rough source windows. If wording is unclear, verify against the recording when possible or exclude it from dialogue; never repair it by invention.

**Pass when:** each candidate story beat has source evidence, a narrative function, context requirements, and a risk note.

### Gate 3 — Research only when it improves judgment

Guest or company research is optional. Use public, attributable sources when the user requests it or when it materially helps assess novelty, audience context, titles, or claim significance. Skip it for private/internal material or when the recording already supplies sufficient context.

Keep research separate from recorded speech. Cite it in editorial notes. External facts may become a clearly labeled card or narration only with appropriate sourcing and user acceptance; they may never be presented as something a speaker said.

**Pass when:** research provenance is recorded and no external wording has leaked into verbatim excerpts. If research is unnecessary, record that decision and continue.

### Gate 4 — Draft three genuinely distinct arcs

Create exactly three supported options in `editorial-options.md` before asking the user to narrow. Each option must include:

- premise and audience promise;
- central tension or question;
- why this is a different editorial thesis, not a reordered version of another option;
- a complete reading-order script from opening through ending;
- every speaker turn as verbatim text with source ID and rough source window;
- every card or narration item explicitly labeled as non-spoken;
- runtime estimate with assumptions;
- strengths, risks, omissions, and legal/privacy exposure.

Options may share an indispensable clip, but they must differ in central question, claim hierarchy, development, and destination. A new title, order, or ending alone is cosmetic. If the source cannot support three honest theses, fail the gate and explain the evidence gap rather than manufacture variants.

Recommend one option and explain the tradeoff. A recommendation informs the user's choice; it does not select on their behalf.

**Pass when:** the distinctness matrix and full scripts let the user compare three complete listening experiences, not three blurbs.

### Gate 5 — Iterate with the user

Treat `editorial-options.md` as a versioned working artifact:

1. Translate feedback into explicit changes and assumptions.
2. Apply global feedback globally. For example, an employer-specific exclusion also removes indirect identifiers, products, clients, locations, timelines, and anecdotes that can reveal the employer.
3. Revise complete scripts so a changed opening or ending is evaluated in context.
4. Remove discarded endings or beats instead of defending them after the user rejects them.
5. Update runtime, risks, comparison, and recommendation after every material revision.
6. Append a decision-log entry with version, user direction, retained/rejected choices, and reason. Summarize restricted material by category rather than quoting it.

Maintain a meaningful host presence by narrative function, not airtime quota. Keep questions, challenges, bridges, or syntheses that change how the listener understands the guest. Remove backchannels, duplicated setup, and filler. Never distort an answer by removing the host context it relies on.

**Pass when:** the latest full scripts embody the feedback, constraints are consistent across all eligible material, and rejected alternatives remain auditable without exposing excluded content.

### Gate 6 — Run the constraint and integrity pass

Before requesting approval, check every line of every active option:

- Speaker text exists in the source and keeps its original meaning.
- A complete phrase or sentence has not been assembled from disconnected fragments.
- Removed context does not turn a qualified statement into an absolute claim.
- Sensitive names and indirect identifiers are absent wherever the exclusion applies.
- Editorial summaries, cards, narration, and visual ideas are unmistakably non-verbatim.
- Runtime math includes spoken words, card holds, pauses, and transitions.
- All source windows are labeled as estimates.

Record the pass in `editorial-options.md`, including any unresolved risk.

**Pass when:** there are no silent substitutions, unlabeled authored lines, or known constraint leaks.

### Gate 7 — Obtain explicit approval

Ask the user to approve a specific arc and version. Accept any unequivocal selection that identifies the version and authorizes the next stage, such as “I approve Arc 2, revision 4,” “I pick Option 4—edit it,” or “use this exact script.” Praise, preference without a named version, or a request for another tweak is not approval.

No video editing starts at this point. Approval authorizes the editorial handoff only.

**Pass when:** the selected arc/version and approval evidence are unambiguous and any requested changes have already been incorporated.

### Gate 8 — Write the handoff

Create `approved-script.md` from the approved version using the bundled template. It must contain:

- source inventory;
- locked constraints and target runtime;
- one-sentence premise;
- ordered speaker turns with verbatim text, stable source IDs, and rough source windows;
- clearly labeled card/narration items, if any;
- explicit omissions without reproducing restricted content;
- sequence-level and overall visual notes;
- approval status, selected version, approver, date, and approval evidence.

Run the integrity and constraint pass once more while copying. Do not add a stronger line, new card, cleaner paraphrase, or different ending after approval. Any material editorial change returns to Gate 5 and requires renewed approval.

End with a handoff note: rough windows are editorial estimates; the media editor must align exact sentence boundaries against timestamped audio before constructing the cut.

**Pass when:** `approved-script.md` is complete, contains no unresolved fields, matches the approved version, and is ready for a separate editor without relying on this conversation.

## Completion boundary

The skill is complete when the user-approved `approved-script.md` exists and the handoff is internally consistent. Do not create an edit plan, transcode, crop, mix, or render media.