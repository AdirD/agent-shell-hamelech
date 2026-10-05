# Lane 4 — Edge-Case Trades (deep playbook)

> The playbook behind Tidy's **Edge-case trade** lane (internal anchor:
> Lane 4). Tidy's [`SKILL.md`](../SKILL.md) owns the shared workflow — scope,
> the unified evidence table, approval, and verification. This file holds the
> lane-specific targets, proofs, and guardrails for trading rare-case handling
> for a smaller diff. Pull it in when **Edge-case trade** fires.
>
> User-facing short label in the evidence table / approval / summary:
> **Edge-case trade** — never print "Lane 4".

The 80/20 lane. A large share of an AI-written diff often exists for cases
that almost never happen: a retry for a rare race, a special message for one
status code, a try/catch around a step that rarely fails, a guard stricter
than anything else in the repo. Each one costs code, tests, constants, and
reviewer attention.

## Goal

> Find code that can go if we accept losing a rare case, so the diff and its
> complexity shrink where they buy the least.

The other tidy lanes keep behavior identical. This lane deliberately does not:
every finding gives up a specific case, says exactly what is lost, and lets
the user decide item by item.

## Boundary with adjacent lanes

Route by what the proposed action changes:

- **Dead code** deletes or collapses code and nothing observable changes. If
  deleting it changes anything observable, even in a case nobody asked for, it
  belongs here.
- **Prompt bloat** keeps owning prompt and instruction files; its Coverage
  proof already handles never-fires cases in prompts.
- **`melech-8020`** negotiates the outcome before implementation. This lane
  trims rare-case handling inside an implemented diff and never changes the
  main path.

When the same lines allow two actions (replacing hand-written code with a
sibling helper that differs in one rare case), report one finding under the
lane of the recommended action and name the alternative in its evidence.

## Targets it hunts

- Retries, backoff, and delays for rare races or transient errors
- Special-case error messages or status branches that the generic path
  already handles acceptably
- Defensive try/catch around steps whose failure the user can recover from
  by retrying
- Guards stricter than the repo's precedent for the same risk
- Diagnostic detail carried only for rare debugging, such as extra error
  fields or bespoke error classes, unless a repo rule requires it

A fallback for a shape that is proven never produced is **Dead code**. A
fallback for a shape that is merely unlikely belongs here.

## The 5 proofs

Every finding must show all five. A missing proof means keep the handling.

| Proof | Question | Evidence |
|---|---|---|
| **1. Frequency** | How rare is the case? | The trigger condition (two users connecting the same site in the same second, one specific status code), plus logs or metrics when available. If frequency is unknown, say so and raise the risk. |
| **2. Consequence** | What does the user see without the handling? | A visible, recoverable error is tradable. A silent wrong result, data loss, corrupted state, duplicate charge, or leaked data is not. |
| **3. Recovery** | Is there a cheap way out? | Retrying, pasting again, an outer handler, or an idempotent rerun. No recovery path means not tradable. |
| **4. Precedent** | How does the repo handle the same case elsewhere? | Search sibling features by purpose. Handling above precedent is tradable; going below it is not. Handling required by a repo rule or explicit requirement stays. |
| **5. Savings** | What disappears? | Lines, tests, constants, helpers, imports, and concepts. Small savings with a real loss is not worth recommending. |

## Never trade below precedent

Security and auth boundaries, tenant or user isolation, data integrity,
money, privacy and secrets, and anything an explicit requirement or repo rule
mandates. In these areas the lane may only bring handling down to the repo's
established precedent, and the finding must say a security reviewer should
confirm it.

## Lane-specific method

*(Scope, approval, and verification are handled by the Tidy workflow.)*

1. **List the cases the diff handles.** For every branch, catch, retry,
   fallback, special message, and extra check, name the case it exists for.
2. **Run the 5 proofs** for each case. Read sibling features and dependency
   source when frequency or precedent depends on them.
3. **Write what is lost** in one plain sentence from the user's side, such as
   "if two people connect the same site at once, one must paste again."
4. **Report the trade** in the unified table with its risk and its
   **What we lose** cell. Recommend only.
5. **When applying an approved trade**, delete the handling and everything
   that only served it (constants, helpers, imports, tests), keep a test that
   the main path still works, and update docs and comments that describe the
   dropped case.

Example rows for the unified table:

```markdown
| Lane | Target | Issue / Evidence | Proposed Action | What we lose | Risk |
|---|---|---|---|---|---|
| **Edge-case trade** | `src/connect/service.ts:L120-L134` (retry on 400) | **Frequency**: only when two users connect the same site within a second. **Recovery**: connecting again succeeds. **Precedent**: no other connector retries. | Drop the retry, `RETRY_DELAY_MS`, `delay()`, and its test (−14 lines) | One of two simultaneous connects fails and must be retried | Low |
| **Edge-case trade** | `src/connect/site-url.ts:L40-L52` (second DNS lookup) | **Precedent**: the sibling URL validator does one lookup and documents rebinding as out of scope, because a third party makes the request. | Keep a single lookup (−9 lines, 1 test) | Catches only the most naive alternating-DNS attacker, which the third party re-resolves anyway. Security reviewer should confirm. | Low |
```

## Do / Don't

**Do:** state the loss from the user's side, in one sentence, for every trade.

**Don't:** call a trade "equivalent", "safe cleanup", or "dead code".

**Do:** use the repo's own precedent as the bar for how much handling a case
deserves.

**Don't:** trade security, isolation, data integrity, money, or privacy below
that precedent.

**Do:** report "no trade worth making" when the savings are small or the
losses are real.
