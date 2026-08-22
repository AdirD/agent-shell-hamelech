# Reviewer Clone workflow

This file owns phase order, main-agent authority, parallel work, human
interaction, publication, recovery, progress, and hand-off. Other references
explain collection, evidence, calibration, attention, resync, and output format;
they do not define another workflow.

## Who does what

The main agent is the continuous trainer. Only it:

- resolves identity, offers repositories, and lets the human choose
- creates or resumes the run and invokes bundled collectors directly
- chooses every PR it will deeply read
- personally interprets selected PRs and compares behavior across them
- interacts with the human
- decides what the Clone learns, unlearns, or leaves uncertain
- decides whether another exploration is useful
- proposes stopping and publishes only after explicit approval

Use subagents only for independent bounded work:

- map the chosen repository and write `repository-system.md`
- analyze review wording and write `voice.md`
- collect a narrow missing fact or find candidate contrasting PRs

Subagents are disposable, not long-lived collaborators. Give each a complete
self-contained prompt, start it fresh, and assign at most one output. It must
rewrite that output completely rather than append, never rely on prior agent
memory, and never edit active Clone memory, interview the human, choose the next
PR, decide learning, or publish. If it fails, dispatch the same complete job
again. The main agent records useful facts once using stable GitHub IDs.

Use a fast inexpensive model for factual repository mapping and narrow searches.
Use a stronger model when wording or contextual interpretation matters. The
main agent always keeps selected-PR interpretation and final learning.

## Invocation routing

Treat every invocation as:

> Ensure this reviewer's Clone is initialized and current for this repository.

- Clone missing: initialize transferable voice and repository memory.
- Clone exists but this repository is missing: initialize repository memory and
  update voice only if new evidence materially changes it.
- Clone and repository memory exist: resync from new events.
- Resync finds no relevant new evidence: report a no-op.

Never rebuild existing memory merely because the user said `init`. A destructive
rebuild requires explicit confirmation.

## Progress

Create these todos when the todo tool is available:

```text
Offer recent repositories and let the user choose
Create or resume the private training run
Collect activity and start repository/voice analysis
Explore PRs and learn iteratively
Choose whether to continue or publish
Publish the reviewer Clone
Report the result
```

Keep one todo in progress. During PR exploration, update that todo with the
number of completed deep reads and the purpose of the next choice, for example:

```text
Explore PRs and learn iteratively — 4 deep reads; checking a threshold contrast
```

Do not create one todo per PR or duplicate the todo UI with progress bars,
dashboards, ASCII status panels, or routine narration. Between routine tool
calls, say nothing: do not announce plans, restate completed mechanics, or
explain the next tool. Let todos carry that information.

## Phase 1 — identify reviewer and choose repository

The main agent performs this entire phase directly.

1. Resolve the authenticated GitHub login using `github.md`.
2. If a PR was supplied, use its canonical base repository.
3. Otherwise run only the two bounded recent reviewed/commented PR queries in
   `github.md`.
4. Group results by repository and offer three to five useful choices.
5. Let the human choose through a structured question with `Other`.
6. Resolve and show canonical `host/owner/repo`.

Describe menu counts as matches in the bounded recent window, not total
historical PR counts.

Before the choice, do not inspect candidate repository code, enumerate full PR
history, inspect Clone state, or launch a repository subagent. This first step
is a quick menu.

## Phase 2 — create or resume the run

Locate `~/.agents/skills/cr-clone-<github-login-lowercase>`, then determine init,
repository init, resync, or no-op from its active files and `state.json`.

Create one new run directory using an actual UTC timestamp from the system
clock; never hand-type or guess it. Follow `output-contract.md`. `RUN.md` owns
run status, exact collection coverage, selected/deep-read PR IDs, human answers,
learning changes, failures, and the final decision. Do not create the generated
runtime `SKILL.md` until the human publishes the first initialization.

For resync, preserve existing active files. Collect only events newer or changed
since the saved GitHub cursors and revisit open PRs whose observable state
changed.

## Phase 3 — collect activity and start parallel analysis

In the first tool turn after creating the run:

- the main agent starts `scripts/collect-review-activity.py` directly and saves
  its detailed and compact outputs in run `scratch/`
- concurrently, dispatch **Map repository system** to inspect current code,
  configuration, and docs and write `repository-system.md` with a compact
  architecture graph, important boundaries, source paths, and gaps
- on resync, also dispatch **Collect Clone feedback** to return only observed
  traced comments, human edits/replies, missed concerns, changed outcomes, and
  direct active-file edits

Do not read the collector source before invoking its documented command. As soon
as the activity index exists, dispatch **Analyze review voice** over the shared
comment material. It writes `voice.md` with exact examples, counterexamples,
uncertainty, and a complete candidate `VOICE.md`. If later deep reads materially
change the evidence, start a fresh voice job with the full current evidence and
replace `voice.md`.

The main agent does not wait for repository or voice analysis. It builds an
initial menu of roughly 8–12 promising PRs from:

- substantive inline comments and change requests
- follow-up, withdrawal, defense, re-review, or specific praise
- varied areas, authors, change types, and time periods
- authored PRs only as supporting familiarity evidence

This is a menu, not a batch commitment.

## Phase 4 — explore PRs iteratively

For each iteration, the main agent:

1. Chooses one PR or a small matched pair that can establish, contrast, or
   challenge something material.
2. Runs `scripts/collect-pr-evidence.py` for those PR numbers.
3. Personally reads the saved evidence, relevant diff and live code, exact human
   actions, discussion, later changes, outcome, and limitations.
4. Adds concise source-backed sections to run `EVIDENCE.md`.
5. Updates candidate judgment, attention, voice implications, and uncertainty.
6. Checks whether a confidence checkpoint is due and asks before continuing
   when it is.
7. Decides whether to inspect a contrast, launch a focused exploration, choose
   another PR, or propose stopping.
8. Updates `RUN.md` and the active todo.

Use this evidence shape:

```markdown
## PR #...

### Observed
- Exact human action/comment with stable GitHub ID and anchor.

### Context
- Only what is needed to understand that action.

### Outcome
- Reply, edit, code movement, re-review, and final state.

### Supports
- Plausible interpretation, stated as inference.

### Challenges
- Contradictions, alternatives, and what this PR cannot establish.
```

Focused exploration remains available whenever the main agent sees a real gap:
find a contrasting review, check one repository behavior, or locate comparable
decisions. Give the explorer shared sources and one narrow question. It returns
facts and candidate IDs; the main agent chooses and reads any resulting PR.

Repository and voice jobs continue in parallel. Their completion should not
block the next PR choice.

## Human interaction during exploration

Training is interactive by default. Follow the two interaction types in
`calibration.md`:

- Use a confidence checkpoint to show the current repository, voice, attention,
  or judgment understanding and ask one correction question.
- Use behavior-changing calibration only when evidence is strong enough to
  consider activating the pattern.

Run the first confidence checkpoint as soon as repository/voice work supports a
personal reflection, or after the first two deep reads. After that, do not
complete more than three additional deep reads without another human
interaction. Ask sooner when an insight, contradiction, or likely
misunderstanding appears, and always checkpoint before proposing publication.

A checkpoint leads with a concrete, evidence-backed synthesis, then asks one
question whose answer can redirect exploration. Do not ask empty reassurance
questions or lower the evidence threshold for active memory merely because a
checkpoint is due.

The main agent does not wait for unrelated background work before asking.
Background jobs may continue while the human answers. Human answers affect
main-agent learning and future jobs; they do not mutate already-running prompts.

## Phase 5 — maintain the candidate model

After every deep read, the main agent:

- separates observation from interpretation using `evidence.md`
- looks for matched contrasts rather than topic counts
- updates the attention tree using `attention-map.md`
- combines repository context, voice analysis, judgment, threshold, corrections,
  and uncertainty
- applies explicit human answers and direct active-file edits as authoritative
- records only material changes in `RUN.md`

Repository and voice artifacts are inputs, not independent learned reviewers.
Only the main agent decides what enters active `VOICE.md` and `MEMORY.md`.

## Phase 6 — let the human choose depth

Before proposing publication, run a final confidence checkpoint over the
current repository model, voice, judgment, attention, and important unknowns.

Before changing active memory, show the smallest useful delta:

```text
Learned
- ...

Unlearned or narrowed
- ...

Voice adjustment
- ...

Attention movement
- ...

Still uncertain
- ...
```

The main agent may propose stopping when recent diverse deep reads mostly
reinforce the same model and no unresolved contradiction is likely to change
future reviews materially. This is judgment, not a fixed wave count or
saturation percentage.

Show exact indexed, comment-collected, review-material-fetched, and fully
deep-read counts. Let the human choose:

- publish now
- continue with another diverse exploration
- deep-dive into a named unknown area
- pause and resume later

Stopping never implies permission to publish.

## Phase 7 — publish simply and safely

Only an explicit publish choice authorizes active changes.

1. Record accepted learning, source IDs, human decision, and remaining
   uncertainty in `RUN.md`.
2. Build complete candidate `VOICE.md` and repository `MEMORY.md` in `scratch/`.
3. Re-read existing active files so direct human edits are not overwritten.
4. Check the candidates for privacy, contradictions, unsupported certainty, and
   required structure.
5. If replacing active files, preserve their prior contents in the run.
6. Replace each active file with one complete candidate, then update
   `state.json`.
7. Mark `RUN.md` published and remove only disposable scratch.

If publication fails before replacement, existing memory remains active. If it
fails midway, restore the prior copy preserved in the run and report the
failure. A paused or failed run remains resumable from `RUN.md` and
`EVIDENCE.md`.

## Communication and hand-off

Use todos for routine progress. Do not narrate tool selection, phase mechanics,
or what just completed. Send a conversational update only when:

- access or another blocker requires action
- a confidence checkpoint is due
- completed evidence earns behavior-changing calibration
- a meaningful result changes the next exploration
- the human must choose depth or publication

Finish with:

- initialized, resynced, no-op, paused, or failed status
- exact indexed/collected/fetched/deep-read coverage
- why work stopped and what the human chose
- accepted learning, unlearning, and voice changes
- attention strengths and unknowns
- active Clone path and run path

The Clone is a transparent, correctable approximation of the human, never the
human.
