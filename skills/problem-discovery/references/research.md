# Research Methods for Problem Discovery

Use only the methods needed for the current uncertainty.
Favor fast, falsifiable learning.

## A) Buyer Demand Signal Ladder (where to look online)

Use this order by default.

### Tier 1 — Observed buying behavior (strongest)

Look for direct evidence that money or budget is already moving.

Sources:
- G2, Capterra, GetApp (paid tool usage, replacement discussions)
- Cloud marketplaces (AWS/Azure/GCP) where relevant
- Public procurement portals / RFP databases (market dependent)
- Job postings (LinkedIn Jobs, Indeed): companies hiring to handle the pain
- Competitor pricing/packaging pages (commercial maturity, contract signals)

What counts:
- Existing spend in adjacent/direct alternatives
- Switching events and migration pain
- Budget-owner involvement
- Procurement language and buying criteria

### Tier 2 — Observed workaround behavior

Look for costly non-product behavior indicating unresolved demand.

Sources:
- Community threads with concrete process descriptions
- Public engineering/blog writeups of internal tooling
- GitHub issues/discussions for tooling-heavy markets
- Support/forum posts showing repeated workaround steps

What counts:
- Repeated manual workflows
- Multi-tool stitching
- Internal scripts replacing missing product capability
- Time and reliability tradeoffs accepted due to no better option

### Tier 3 — Primary research (high quality)

Use interviews to validate mechanism, context, and decision process.

Methods:
- Customer Discovery (Steve Blank style)
- JTBD discovery interviews
- Recent-incident interviews ("last time this happened")
- Buyer-process interviews (approval, risk, procurement)

What counts:
- Specific incidents, not hypotheticals
- Current behavior and costs
- Trigger events and urgency
- Adoption constraints and switching barriers

### Tier 4 — Intent and market proxies

Use as directional support, never sole proof.

Sources:
- Google Trends
- Search keyword tools (problem-intent terms)
- Review-site complaint clusters
- YouTube/tutorial query patterns

What counts:
- Growth/consistency of intent signals
- Segment-specific language patterns
- Converging evidence across multiple proxies

### Tier 5 — Weak signals (supporting only)

Sources:
- Generic social posts
- Upvotes/likes
- Broad "sounds useful" reactions
- Launch-platform applause without behavior follow-through

Rule:
- Do not conclude demand from Tier 5 alone.

---

## B) Triangulation Rule (minimum bar)

Before claiming meaningful demand, require at least:

1. One behavioral/commercial signal (Tier 1 or Tier 2), and
2. One narrative/context signal (Tier 3 or strong Tier 4), and
3. No unresolved contradiction that could reverse the decision.

If one of these is missing, output "insufficient evidence" and propose the fastest next test.

---

## C) Interview Protocol (JTBD + Discovery)

Goal: understand real behavior, not collect feature requests.

Interview prompts:
1. "Tell me about the last time this problem happened."
2. "What did you do first, then what?"
3. "What made it hard/expensive/risky?"
4. "What tools or people were involved?"
5. "What did this cost (time, money, delay, risk)?"
6. "What have you already tried?"
7. "If this were solved, what measurable outcome improves?"
8. "Who decides to buy/change process here?"
9. "What would block switching/adoption?"

Avoid:
- hypothetical future opinions
- leading questions
- pitching your solution during discovery

---

## D) Scoring framework (lightweight)

Score each segment/problem hypothesis on:

- Frequency (how often pain occurs)
- Severity (impact when it occurs)
- Cost of inaction (time/money/risk)
- Budget proximity (is there a buyer and budget path)
- Switching readiness (ability to adopt/change now)
- Evidence quality (source strength + triangulation)

Use High/Medium/Low or 1–5, but keep rationale explicit.
No false precision.

---

## E) Contradiction handling

When signals conflict:

1. Keep both claims visible.
2. Weight by signal strength and recency.
3. Identify the minimal test to resolve conflict.
4. Do not smooth contradictions into fake certainty.

---

## F) Output templates (short form)

## Problem Validation Snapshot
- Segment:
- Problem situation:
- Current behavior/workaround:
- Strongest demand signals:
- Weak/ambiguous signals:
- Key contradictions:
- Confidence:
- Recommendation: Proceed / Refine / Hold / Stop
- Next test:

## Demand Evidence Ledger
- Claim
- Evidence type (Tier 1–5)
- Source
- Date/recency
- Confidence
- Contradictions
