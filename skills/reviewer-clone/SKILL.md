---
name: reviewer-clone
description: >-
  Create and resync a private user-global Clone skill that reviews GitHub pull
  requests like the authenticated user. Learn their review voice,
  repository-specific concerns, where they focus, when they intervene, and how
  they investigate—from their real reviews, authored code, and feedback on prior
  Clone comments. Use when the user asks to clone or learn their code-review
  style, build a personal CR/PR reviewer, add a repository, retrain, or resync an
  existing reviewer Clone.
---

# Reviewer Clone

Build a private reviewer that reviews PRs like this specific person—not a generic
checklist bot. You train it; the generated `cr-clone-<login>` skill does the
reviews.

Learn a compact model of the person:

- **WHERE** they focus—the parts of the system they know deeply or care about.
- **WHEN** they speak up—what makes them stay silent, ask, suggest, praise, or block.
- **HOW** they work—how they investigate, what evidence they cite, how they phrase things.

The whole job is to watch how they actually behave on real PRs, form a picture,
check that picture with them, and save it. Trust your judgment over rigid rules.

## Start here — pick the repo first (cheap)

Do this before reading any other reference. Picking the repo needs almost nothing,
so don't front-load the whole workflow just to show a menu.

1. Resolve the login: `gh api user --jq .login`
2. If a PR was given, use its base repo. Otherwise run both and merge the results:

```bash
gh search prs --reviewed-by LOGIN --sort updated --limit 100 --json repository \
  --jq 'group_by(.repository.nameWithOwner)|map({repo:.[0].repository.nameWithOwner,recent:length})|sort_by(-.recent)'
gh search prs --commenter LOGIN --sort updated --limit 100 --json repository \
  --jq 'group_by(.repository.nameWithOwner)|map({repo:.[0].repository.nameWithOwner,recent:length})|sort_by(-.recent)'
```

3. Offer the top few and let the human pick (counts = recent window, not lifetime).
   No code inspection, history crawl, or per-PR fetches here.

## After they pick — run the workflow

Now read `references/workflow.md`—it's the source of truth for the rest of the
flow. Pull in the others only when you need them:

- `references/github.md` — the CLI commands and bundled collector scripts
- `references/evidence.md` — how to read behavior into WHERE/WHEN/HOW, and resync
- `references/output-contract.md` — the files you generate and how to publish

## Ground rules

- Keep private evidence and memory out of project repos. Never store credentials.
- Silence and authorship are weak hints, not proof.
- Only publish when the human says so. Only this trainer edits active memory.
- Mark Clone comments visibly (`🤖 Clone:`). It's a correctable stand-in, not the person.
