# GitHub collection

Use the authenticated `gh` CLI so existing access applies. Never print or store
tokens. `workflow.md` owns the flow; this is just the commands and the collectors.

## Identity and repository

```bash
gh api user --jq .login
```

Route memory by the canonical base repository (resolve from GitHub, not just local
remotes). Keep the head repo only as change provenance.

## Offer repositories cheaply

When no repo/PR was given, let `jq` do the grouping so you get a short repo→count
list instead of hundreds of PR objects:

```bash
gh search prs --reviewed-by LOGIN --sort updated --limit 100 --json repository \
  --jq 'group_by(.repository.nameWithOwner)
        | map({repo: .[0].repository.nameWithOwner, recent: length})
        | sort_by(-.recent)'

gh search prs --commenter LOGIN --sort updated --limit 100 --json repository \
  --jq 'group_by(.repository.nameWithOwner)
        | map({repo: .[0].repository.nameWithOwner, recent: length})
        | sort_by(-.recent)'
```

Merge the two, offer the top repos, ask. Don't fetch `url`/`updatedAt` or read the
raw unaggregated list—that's what makes it slow. Counts are recent-window matches,
not total history.

## Bundled collectors

Run these directly—don't read the source first or reinvent them in shell. Inspect
implementation only if a run genuinely fails.

Index reviewed/commented/authored PRs plus inline comments:

```bash
python3 "$REVIEWER_CLONE_SKILL_DIR/scripts/collect-review-activity.py" \
  --repo "$OWNER/$REPO" --login "$LOGIN" \
  --output "$RUN/scratch/review-activity.json"
```

It handles the Search API's result cap, date partitioning, dedup, the repo-wide
comment sweep, and link extraction. Read `review-activity.summary.json` first; open
detailed JSON only for a specific PR.

Fetch evidence for selected PRs:

```bash
python3 "$REVIEWER_CLONE_SKILL_DIR/scripts/collect-pr-evidence.py" \
  --repo "$OWNER/$REPO" --reviewer "$LOGIN" \
  --prs 123 456 --output-dir "$RUN/scratch/pr-evidence"
```

One compact JSON per PR: metadata, reviews, anchored comments, discussion, patches,
commits, thread state. Then read the diff and live code yourself.

If a collector fails, check args/auth/access and retry once. Use the smallest
fallback needed and note any coverage gap—don't write a big improvised script.

## Human vs Clone comments

The same login can author both. Clone comments start with `🤖 Clone:` and carry the
hidden `Clone note` trace with an ID; unmarked comments are human evidence. The
hidden trace is the durable marker—compare current text against its `Original` to
spot a human rewrite. HTML comments aren't private to API readers, so keep secrets
out of traces.

## Honest coverage labels

Keep these distinct and never call an index or comment sweep a deep read:

- **indexed:** metadata found by search
- **comments collected:** bodies swept
- **evidence fetched:** per-PR evidence downloaded
- **deep read:** diff, live code, discussion, and outcome interpreted together by you
