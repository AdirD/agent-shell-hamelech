# Secondary Research and Evidence Discipline

Use secondary research to establish plausibility, map the market, and decide what
must be tested with customers. It can disprove a hypothesis. By itself, it rarely
validates one.

## Match evidence to the claim

| Claim | Useful evidence | Common false proof |
|---|---|---|
| Customer encounters the situation | workflow descriptions, first-party usage, incident accounts | broad demographic size |
| Problem is costly and urgent | repeated consequences, escalations, cancellations, operational loss | complaints and upvotes |
| Existing demand exists | spend, hiring, agencies, internal tools, repeated workarounds | survey interest |
| Buyer and budget exist | procurement, job ownership, budget language, current contracts | user enthusiasm |
| Offer can win | switching events, failed alternatives, paid tests, concrete commitments | missing competitor feature |
| Segment is reachable | concentrated communities, lists, partners, channel response | total addressable market |

## Evidence ladder

### Tier 1 — Commercial commitment

Strongest evidence that a buyer will act:

- completed purchases, paid pilots, deposits, or preorders
- signed agreements with meaningful obligations
- procurement, security, legal, or integration effort
- switching from a paid alternative

Verify who committed, what they received, and whether the behavior matches the
active hypothesis.

### Tier 2 — Costly observed behavior

Evidence that the problem already commands resources:

- manual workflows and recurring operational labor
- internal tools, scripts, and multi-tool stitching
- agency or consultant spend
- hiring and dedicated role ownership
- escalation, churn, lost revenue, compliance exposure, or delay

Costly behavior supports demand more strongly than stated preference, but it
does not automatically prove the proposed offer will win.

### Tier 3 — First-party product and sales evidence

- usage, retention, funnel, support, and cancellation data
- sales objections, win/loss notes, and proposal history
- customer interviews and workflow observations

Treat proxy metrics carefully. Reassignment may mean incorrect routing or
workload balancing; a feature request may express a desired outcome or merely
repeat a fashionable implementation.

### Tier 4 — Public lived-experience evidence

- specialized communities and professional forums
- GitHub issues and discussions for technical users
- product reviews and public support boards
- practitioner blogs, conference talks, and workflow writeups

Use these sources to learn language, mechanisms, recurrence, and workarounds.
They are not representative prevalence estimates.

### Tier 5 — Market and intent proxies

- search trends and keyword data
- category reports and analyst estimates
- funding, traffic, app rankings, and social engagement

Use as context only. These signals can describe attention or category activity;
they do not establish demand for the active offer.

## Research the market from the job outward

Map:

1. direct competitors serving the same customer and job
2. adjacent products solving part of the job
3. bundled features and platform substitutes
4. agencies, consultants, and service providers
5. spreadsheets, internal builds, and manual workflows
6. non-consumption and reasons customers tolerate the problem

For each relevant alternative, capture:

- target customer and buyer
- triggering job and promised outcome
- workflow and delivery model
- pricing and packaging
- distribution or traction signal
- why customers choose and stay
- switching cost and trust advantage
- where it fails for the active situation

An empty competitor slate usually means the search frame is too narrow. A
feature gap is not an opportunity until customers demonstrate a reason to
switch.

## Buyer and budget research

Look for:

- who owns the affected metric or risk
- which team currently performs or funds the workaround
- job descriptions and organizational language
- procurement and security requirements
- current contract values and packaging norms
- budget cycles, approval thresholds, and buying triggers

Distinguish user, champion, buyer, approver, and blocker. In small markets one
person may fill several roles; do not assume that pattern scales.

## Market timing and reachability

Investigate only factors capable of changing the decision:

- regulation, platform policy, or procurement shifts
- newly feasible cost or technical capability
- segment concentration and reachable communities
- incumbent bundling or channel control
- data access, trust, and integration barriers
- failed prior attempts and why they failed

Do not substitute a top-down TAM for a reachable first market. Build bottom-up
logic from identifiable customers, plausible annual value, and an explicit
reachability assumption.

## Search discipline

1. Start broad enough to learn the market's language.
2. Convert claims into falsifiable research questions.
3. Search primary sources for product, pricing, law, and procurement facts.
4. Search for failed attempts and evidence designed to break the hypothesis.
5. Trace repeated statistics and quotes to their original source.
6. Record publication and retrieval dates for time-sensitive claims.
7. Deduplicate by canonical origin before counting corroboration.
8. Stop when new searches repeat known evidence or the declared cap is reached.

Useful query shapes:

- `"[problem phrase]" site:[relevant community]`
- `"[current alternative]" (frustrating OR switched OR cancelled OR workaround)`
- `"[role]" ("responsible for" OR hiring OR job description) [problem]`
- `"[category]" (pricing OR procurement OR RFP OR implementation)`
- `"[job to be done]" ("spreadsheet" OR "manual process" OR consultant)`
- `"[proposed solution]" (failed OR shutdown OR postmortem OR discontinued)`

## Evidence row

Record one row per claim:

```json
{
  "claim": "Short factual statement",
  "validation_claim": "problem | demand | buyer | offer | reachability",
  "tier": 2,
  "source_url": "https://...",
  "source_id": "canonical origin identifier",
  "date": "YYYY-MM-DD",
  "snippet": "Verbatim quote or datapoint",
  "supports": true,
  "confidence": "high | medium | low",
  "limits": "Why this does not fully establish the claim"
}
```

Mark inference explicitly. No resolvable source means the row is a lead, not
evidence.

## Depth bar for a desk audit

Before issuing the desk-research call:

- every decision-carrying claim has evidence or a named gap
- at least three claim areas have two independent origins when available
- at least one Tier 1–2 behavioral or commercial signal exists, or its absence
  is explicit
- obvious competitors and substitutes are mapped
- buyer and reachability received explicit attention
- disconfirming searches were run
- duplicate origins were collapsed
- saturation or the research cap was reached

Passing this bar means the hypothesis is ready for a better field test. It does
not mean the market is validated.
