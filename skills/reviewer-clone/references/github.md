# GitHub collection

`workflow.md` owns phase order. This file defines the small supported GitHub
collection path and honest coverage labels.

Use the authenticated GitHub CLI so existing access applies. Never print or
persist tokens.

## Resolve identity and repository

Confirm the authenticated login:

```bash
gh api user --jq .login
```

Resolve PR identity from GitHub, not only local remotes. Route memory by the
canonical base repository; keep the head repository only as change provenance.

## Offer repositories cheaply

When no repository or PR was supplied, run only:

```bash
gh search prs --reviewed-by LOGIN --sort updated --limit 100 \
  --json repository,updatedAt,url

gh search prs --commenter LOGIN --sort updated --limit 100 \
  --json repository,updatedAt,url
```

The main agent groups this bounded window by repository and asks the human
directly. Label counts as recent-window matches, not total PR history. Stop
there until the human chooses. Do not inspect candidate code, full history,
Clone state, or individual PRs merely to build the menu.

## Use the bundled collectors

The main agent invokes these scripts directly. Run the documented command
without opening the source first; inspect implementation only when a failed run
indicates a script defect.

Index reviewed, commented, and authored PRs plus inline comments:

```bash
python3 "$REVIEWER_CLONE_SKILL_DIR/scripts/collect-review-activity.py" \
  --repo "$OWNER/$REPO" \
  --login "$LOGIN" \
  --output "$RUN/scratch/review-activity.json"
```

The script handles count-first searches, GitHub Search's 1,000-result cap,
creation-date partitioning, role deduplication, the repository-wide inline
comment sweep, and compact candidate selection. Read
`review-activity.summary.json` first; open detailed JSON only for a specific PR
or comment.

Fetch selected PR evidence:

```bash
python3 "$REVIEWER_CLONE_SKILL_DIR/scripts/collect-pr-evidence.py" \
  --repo "$OWNER/$REPO" \
  --reviewer "$LOGIN" \
  --prs 123 456 \
  --output-dir "$RUN/scratch/pr-evidence"
```

It writes one compact JSON file per PR containing metadata, reviews, anchored
comments, general discussion, file patches, commits, and review-thread state.
The main agent then reads the relevant diff and live code itself.

If a collector fails, verify arguments, authentication, and repository access,
then retry once. Do not replace it with a large improvised script. Use the
smallest narrow fallback necessary and record any resulting coverage gap.

## Resync boundaries

Use the saved GitHub cursor or last successful sync time to find PRs updated
since the previous run. `updatedAt` makes a PR eligible for revisiting; it does
not identify the changed event. Fetch that PR and deduplicate reviews, comments,
replies, and reactions by stable GitHub IDs.

Revisit previously open PRs when their state changed. Preserve enough source IDs
in `EVIDENCE.md` to avoid treating the same event as new learning.

## Distinguish human and Clone comments

The same GitHub login may author both:

- Clone comments start with `🤖 Clone:` and contain the compact hidden
  `Clone note` with a trace ID.
- Unmarked comments by the modeled login are human evidence.

The hidden trace is the durable origin marker; the emoji provides visible
transparency. Compare the current visible text with the trace's `Original`
field when detecting a human rewrite.

HTML comments are not private from API readers. Never put secrets or sensitive
unpublished context in a trace.

## Interpret outcomes carefully

When feedback may have affected code:

1. Anchor it to the original commit and diff location.
2. Inspect later changes only around the relevant behavior.
3. Record code movement, thread resolution, re-review, and final state.
4. Do not equate a merge or code change with proof that the comment was correct.

## Report collection levels honestly

Keep these separate:

- **PRs indexed:** metadata was found by search.
- **Authored comments collected:** comment bodies were swept.
- **Review material fetched:** specialized PR evidence was downloaded.
- **Full PR deep reads:** relevant diff, live code, discussion, and outcome were
  interpreted together by the main agent.

Never describe a broad index or comment sweep as deeply reading its PRs.
