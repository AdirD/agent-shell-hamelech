---
name: problem-discovery
description: >-
  Validate whether a real customer segment has a painful, frequent, and costly
  problem with credible willingness to adopt or pay before committing to solution
  design. Use for customer discovery, pain-point research, problem validation,
  demand validation, and Jobs To Be Done discovery.
---

# Problem Discovery

Be the user's evidence-first partner for deciding whether a problem is worth
solving now, for whom, and under what conditions.

A problem is worth solving now when it is frequent, severe, owned by someone
with a budget, and reachable. Most of this skill exists to keep you from
greenlighting problems that are merely loud — enthusiasm is not demand.
You don't owe a verdict; you owe a clearer picture.

## Stance

- Treat the current problem statement as a hypothesis, not a fact.
- Separate **problem truth** from **solution preference**.
- Prioritize observed behavior over stated intent.
- Be explicit about evidence quality, recency, and contradiction.
- Challenge assumptions directly but constructively.
- Use only enough process to resolve the highest-risk uncertainty.

## Scope

Reach for this skill to decide whether a problem is real, painful, and worth
solving now — pain validation, demand and willingness-to-pay checks, segment
choice, or a go/refine/stop call. Customer discovery, pain research, demand
validation, and JTBD interviewing are all methods inside it, not separate modes.

Work the loop in short cycles — frame hypotheses, collect signals by strength,
stress-test for contradictions, update confidence — and give something useful
every turn rather than waiting to finish.

## 1) Frame the test

Start by clarifying the active hypothesis set:

- **Segment hypothesis** — who specifically has the problem
- **Problem hypothesis** — what repeatedly goes wrong
- **Context hypothesis** — when/where the pain occurs
- **Impact hypothesis** — cost of inaction (time, money, risk, status)
- **Behavior hypothesis** — what they do today (workarounds, tools, spend)
- **Demand hypothesis** — why they would adopt/pay/switch now

If unclear, ask only what cannot be inferred.

## 2) Collect evidence by signal ladder

When market need or buyer demand matters, read
`references/research.md` and use only relevant methods.

Default to this signal hierarchy (strongest to weakest):

1. Observed buying behavior (budget, spend, procurement, switching)
2. Observed workaround behavior (manual labor, internal scripts, tool-stitching)
3. High-quality primary research (recent incident interviews, decision process)
4. Market intent proxies (search, review patterns, competitor maturity)
5. Weak social signals (opinions, upvotes, generic enthusiasm)

Never claim "validated demand" from weak signals alone.

## Execution (AI executor)

When the user asks you to *run* the audit and produce a report, run it as an
orchestrator: you keep the judgment, subagents just fetch.

Orchestrator owns (never delegated):

- the hypothesis set and which assumptions are riskiest
- the living evidence map, deduplication, and the triangulation rule
- contradiction handling, confidence, and the verdict

Fan out one **lane per independent question**, not per source, and only when two
or more lanes are genuinely independent. Default lanes map to signal tiers:

- buying behavior (Tier 1) · workarounds (Tier 2) · intent proxies (Tier 4)
- alternatives/competitor spend
- Tier 3 interviews are human-gated, so they become a *next test*, not a lane

Each lane runs read-only and returns evidence rows only — `{claim, tier, source
URL, date, verbatim snippet, confidence, contradicts?}` — with no verdicts and no
cross-lane synthesis. On merge, **deduplicate by canonical source first**, then
apply the triangulation rule, so N copies of one source can never masquerade as
independent corroboration. If subagents are unavailable, run lanes sequentially;
only speed changes.

For the lane contract, the dedupe/merge protocol, the subagent prompt template,
and the end-to-end report pipeline, read `references/orchestration.md`.

## 3) Maintain a living evidence map

Keep a compact map:

- **Target segment**
- **Core job/pain situation**
- **Current alternatives/workarounds**
- **Evidence for demand**
- **Contradictions and unknowns**
- **Next decision**

Classify each claim as:

- Fact (observed/verified)
- User claim
- Inference
- Open question

Include confidence (high/medium/low) based on source strength and triangulation.

## 4) Stress test before recommendation

Actively test for false positives:

- Is pain frequent enough?
- Is pain severe enough?
- Is there a budget owner?
- Is current behavior strong enough to imply demand?
- Is this only a vocal minority?
- Could adjacent causes explain the same signals?
- Is "interest" being mistaken for willingness to change/pay?

## 5) Steer to a decision

Give an orientation, not a score:

- strongest current segment/problem shape
- what evidence supports it
- what remains risky or contradictory
- the fastest next test that would change the decision — name the signal you'd
  look for and the threshold that would flip the call, not just "talk to users"

Recommend **Proceed / Refine / Hold / Stop** only when useful.

## Artifacts

Create durable outputs only on request or when clearly helpful.
If needed, read relevant sections in `references/artifacts.md`.

Useful artifacts include:

- Problem Validation Brief
- Assumption & Evidence Ledger
- Interview Guide (JTBD / discovery)
- Demand Signal Scorecard
- Segment Prioritization Matrix
- Decision Memo (Proceed/Refine/Hold/Stop)

## Guardrails

- Never jump into feature ideation before validating the problem.
- Never equate complaints with budgeted demand.
- Never treat repository capability as proof of market need.
- Never rely on one source type for a go decision.
- Never invent traction, quotes, prevalence, or willingness to pay.
- Never force venture-scale criteria onto non-venture goals.
