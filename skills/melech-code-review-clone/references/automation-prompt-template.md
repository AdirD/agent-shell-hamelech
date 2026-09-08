# Reviewer Clone automation prompt

This is a trainer-side source template, not a generated Clone artifact. During
optional automation setup, render the content below into the current agent
host's automation/task system. Never save it in `cr-clone-<login>`.

Replace every `{{...}}` value before scheduling. If the host provides native
durable memory or state, adapt the corresponding file-based paragraphs to use
that mechanism. If any placeholder remains, stop without reviewing or writing
state.

## Prompt

Use {{CLONE_INVOCATION}} to autonomously review eligible pull requests in
{{BASE_REPOSITORY}}. {{POSTING_INSTRUCTION}}

Eligibility is based on pull request author, never requested reviewers.
{{ELIGIBILITY_INSTRUCTION}} Exclude pull requests authored by
{{REVIEW_ACTOR_LOGIN}}, draft or closed pull requests, and base-repository
mismatches.

Treat each pull request head commit SHA as the unit of review. Use
`{{STATE_FILE}}` to map pull request numbers to their last successfully reviewed
head SHA. A pull request is a candidate only when its current head SHA is absent
from that pull request's state or differs from the stored SHA. Visiting or
reviewing the pull request in the past does not exclude it after its head SHA
changes. Initialize the file if it is missing and preserve unrelated entries.

Before reviewing a candidate, fetch its live reviews and inspect each review's
commit SHA. If `{{REVIEW_ACTOR_LOGIN}}` already submitted an `APPROVED`,
`CHANGES_REQUESTED`, or `COMMENTED` review for the exact current head SHA,
record the SHA in the state file if needed and skip the pull request. In
particular, never re-review a pull request already approved by
`{{REVIEW_ACTOR_LOGIN}}` at its current head SHA.

Immediately before submitting a review, re-fetch the pull request head SHA and
exact-head reviews. If the head changed, do not submit against the stale diff;
leave state unchanged so the new head can be reviewed on a later run. If another
run already submitted an exact-head review by `{{REVIEW_ACTOR_LOGIN}}`, backfill
state and skip submission.

Process at most `{{MAX_CANDIDATES}}` candidates per run, newest update first. For every candidate, follow {{CLONE_INVOCATION}} exactly. Only after successfully submitting a completed review for the exact current head SHA, or verifying an existing completed review by `{{REVIEW_ACTOR_LOGIN}}` on that exact SHA, record that SHA in the state file; otherwise leave it unchanged.

Maintain durable context in `{{MEMORY_FILE}}`, initializing it if needed; never
replace the whole file with only the latest run. Keep:

1. Durable review ledger: upsert one entry per acted-on pull request head with
   pull request number, link, head SHA, terminal verdict, product-oriented
   summary, why that verdict was chosen, non-blocking concerns or follow-up
   work, and relationships to other pull requests.
2. Latest run: replace this short section each run with the run time,
   eligibility/candidate result, and actions taken.

Before reviewing a candidate, consult the durable ledger for related work and
verify all remembered claims against the live pull request and current code.
Detect relationships from stacked base branches, pull request body links,
shared work or initiatives, dependency order, and overlapping product outcome.
When pull requests are related, explicitly record the relationship and review
them as a sequence—for example, a service-foundation pull request followed by a
catalog-migration pull request. Memory is context, not authority: current
GitHub state and current code always win. Do not edit the reviewer Clone's
`MODEL.md`, `VOICE.md`, or root training `state.json`. If the ledger grows
large, condense merged or closed entries, but preserve rationale and
relationship context for open pull requests.

Report every acted-on pull request separately with its link and terminal
verdict, immediately followed by a one- or two-line product-oriented summary.
Describe the user, customer, or business outcome rather than files or
implementation mechanics. Add one short **Related PRs** note when multiple
reviewed pull requests belong to one rollout or dependency chain.

If none are actionable, say there are no new or updated eligible pull requests.
