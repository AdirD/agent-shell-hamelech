---
name: market-validation
description: >-
  Run end-to-end market validation for one concrete market hypothesis: lock the
  target customer, painful situation, buyer, current alternatives, and proposed
  value; gather first-party and public evidence; design and synthesize customer
  discovery; run the smallest behavioral or commercial test; and return an
  evidence-backed Advance / Reshape / Hold / Stop decision. Use whenever someone
  wants to validate a startup, business idea, new market, ICP, buyer, demand,
  willingness to pay, or whether a specific opportunity is worth pursuing—even
  if they ask for market research, customer discovery, demand validation, or
  "will people pay for this?" Trigger only once the customer/problem/value
  hypothesis is concrete enough to test. Use product-ideation when those pieces
  are still movable, and do not use for implementation planning after the market
  decision is already made.
---

# Market Validation

Validate one specific market hypothesis all the way from plausibility to the
strongest real-world evidence the user can obtain. Do not mistake research,
enthusiasm, interviews, or one pilot for a validated market.

The skill is complete only when it has:

1. made the hypothesis falsifiable
2. mapped evidence for and against every decision-carrying claim
3. closed the most important evidence gap with primary or behavioral evidence
   when access permits
4. separated what is known from what remains merely plausible
5. produced an explicit **Advance / Reshape / Hold / Stop** decision

Market validation may span multiple sessions because customers and experiments
exist outside the chat. Preserve one living validation brief so the work can
resume without restarting.

## Boundary first

Choose this skill based on the state of the user's thinking:

| User has | Use |
|---|---|
| A movable product premise and wants help shaping what it could become | `product-ideation` |
| A concrete requested solution that may not serve the real need | `distill-need` |
| A specific customer/problem/value hypothesis and wants to know whether reality supports it | `market-validation` |
| A market-backed direction and needs a shared build concept | `pre-plan` |

Do not force an open idea into validation. Help the user form a testable
hypothesis first, or hand back to `product-ideation`.

## Validation model

Validation is not one binary badge. Track the evidence state of each claim:

- **Unsupported** — asserted, with no meaningful evidence
- **Plausible** — supported by credible secondary or first-party signals
- **Behavior-supported** — target customers repeatedly demonstrate the problem,
  workaround, switching, or relevant action
- **Commitment-supported** — the intended buyer gives scarce commitment such as
  money, signed pilot, procurement effort, data access, or meaningful time

The claims that usually carry a market decision are:

1. **Customer and situation** — a reachable segment encounters a specific
   triggering situation.
2. **Problem** — the situation creates frequent, severe, or costly consequences.
3. **Existing demand** — people already spend money, time, risk, or political
   capital to make progress.
4. **Buyer and budget** — an identifiable decision-maker owns the outcome and
   can fund change.
5. **Offer fit** — the proposed value and delivery shape beat the current
   alternative enough to motivate action.
6. **Reachability** — there is a credible path to repeatedly find and engage the
   segment.

Not every claim needs commitment-level evidence before proceeding. The riskiest
claim that would reverse the decision does.

## End-to-end workflow

### 1. Lock the validation contract

Turn what the user gave you into one provisional sentence:

> **[Customer] in [situation] struggles with [costly problem], currently uses
> [alternative], and [buyer] will choose/pay for [proposed value] because
> [reason to switch].**

Also capture:

- geography or market boundary
- the decision this validation must inform
- time, money, access, and research constraints
- what evidence would cause **Advance**, **Reshape**, **Hold**, or **Stop**

Propose the contract from available context. Ask only about a blank that is both
unguessable and decision-changing. Let the user correct it once; do not run a
generic startup intake.

If the proposed solution is still very fluid, lock the customer/problem side and
label the offer claim as open rather than inventing false precision.

### 2. Build the claim and evidence map

For each decision-carrying claim, record:

- current evidence
- strongest counter-explanation
- evidence state
- risk if false
- cheapest method that could discriminate between explanations
- threshold that changes the decision

Prioritize by **decision impact × uncertainty**, not by whichever evidence is
easiest to collect.

Read `references/artifacts.md` before creating or updating the living validation
brief.

### 3. Mine first-party evidence

Before searching the public web, inspect evidence the user already owns when it
exists:

- support conversations and feature requests
- product usage, retention, cancellation, and workflow data
- sales calls, objections, win/loss notes, and CRM fields
- interview transcripts, surveys, emails, community conversations
- paid pilots, proposals, procurement steps, and previous experiments

Separate capability from demand. Existing code proves something can be built;
feature requests prove someone asked; neither proves repeated pain or purchase
intent.

Respect privacy and authorization. Ask for aggregated or redacted evidence when
raw customer data is unnecessary.

### 4. Run the secondary evidence audit

Research both for and against the contract:

- recurring pain and consequences
- workarounds and existing spend
- direct competitors, substitutes, services, internal builds, and non-consumption
- buyers, budgets, procurement language, and switching barriers
- market timing, regulation, concentration, and reachable communities
- failed products or attempts that expose structural risk

Read `references/research.md` and use only methods relevant to the active claims.
For parallel evidence collection, read `references/orchestration.md`.

Keep an evidence log with canonical source, date, claim covered, evidence type,
snippet or datapoint, confidence, and contradiction. Deduplicate by origin before
counting corroboration.

Stop at saturation or a declared research cap—not after the first plausible
answer.

### 5. Make the desk-research call

Synthesize what secondary and first-party evidence can establish. Use precise
language:

- **research-supported** or **plausible**, never “validated,” when evidence is
  indirect
- **insufficient evidence** when the decisive claim remains open
- confidence per claim, not one decorative confidence score

At this point, recommend **Advance to field validation**, **Reshape the
hypothesis**, **Hold**, or **Stop**. Do not produce the final market-validation
verdict yet unless strong primary and behavioral evidence already exists.

### 6. Close mechanism gaps with primary discovery

Use interviews or workflow observation to understand:

- the last real incident, trigger, sequence, and consequence
- current alternatives and why they remain tolerated
- who notices, owns, approves, pays, and can block change
- urgency, switching conditions, and adoption risk
- language customers naturally use

Read `references/fieldwork.md` and prepare:

- participant criteria and exclusions
- recruiting routes
- a behavior-first interview or observation guide
- an evidence-capture format
- sample and stop rationale

The user may conduct sessions and return with notes, or connected tools may
provide authorized evidence. Do not fabricate interviews or silently replace
them with public posts.

Synthesize patterns and disconfirming cases. Interviews validate mechanisms and
context; stated enthusiasm does not validate willingness to pay.

### 7. Close demand gaps with a behavioral or commercial test

Choose the smallest test that exposes the weakest decisive claim to reality.
Examples:

- paid or deposit-backed pilot
- concierge/manual delivery of the promised outcome
- proposal or letter of intent with concrete obligations
- pricing or packaging test with a real buying decision
- smoke test measuring qualified conversion from a reachable audience
- channel test measuring whether the target segment can be acquired
- switching test that requires data, integration, or workflow commitment

Define before launch:

- exact claim being tested
- target participant and offer
- observable behavior—not reported preference
- pass / reshape / stop threshold
- time and spend cap
- what the test cannot prove

Help execute the test when tools and authorization permit. Otherwise, produce a
run-ready protocol, pause at the human gate, and resume from returned results.
Do not treat “I would use this,” waitlist signups, or compliments as payment.

### 8. Decide without laundering uncertainty

Update every claim's evidence state, then issue:

- **Advance** — enough evidence supports the next reversible investment
- **Reshape** — the market signal exists, but customer, problem, buyer, offer,
  channel, or timing must change
- **Hold** — the evidence is still insufficient and the next test is not
  currently worth its cost
- **Stop** — strong evidence contradicts a decision-carrying claim or economics

Separate verdicts for:

- problem
- demand
- buyer/budget
- proposed offer
- reachability

One positive customer or paid pilot is evidence, not proof of a repeatable
market. State the next unvalidated risk even when the decision is Advance.

### 9. Deliver the market-validation dossier

Read `references/artifacts.md`. The final dossier must show:

- validation contract and decision
- evidence progression from desk research through fieldwork and experiment
- claim-by-claim evidence state and confidence
- strongest supporting and contradicting evidence
- customer, buyer, alternatives, and competitive reality
- experiment result against its precommitted threshold
- split verdict across problem, demand, buyer, offer, and reachability
- Advance / Reshape / Hold / Stop recommendation
- next investment and the risk it is intended to retire
- source and research-coverage appendix

If field or behavioral work could not happen, deliver an **interim validation
brief**, label it honestly, and leave a run-ready next test. Never dress a
research report as completed market validation.

## Resuming long-running validation

At the start of a resumed session:

1. read the living validation brief
2. restate the active contract and current decision in one sentence
3. identify new evidence and which claim it changes
4. continue from the first open gate

Do not restart discovery or rewrite history when the hypothesis changes. Record
what changed, why, and which earlier evidence still applies.

## Guardrails

- Never equate market size, traffic, funding, or competitors with demand.
- Never count duplicated claims as independent corroboration.
- Never use interviews to claim payment, a landing page to claim retention, or a
  pilot to claim scalable acquisition.
- Never hide contradictory or null evidence.
- Never optimize the offer before confirming the customer and costly situation.
- Never force venture-scale criteria onto a lifestyle business or internal tool.
- Never claim “market validated” without behavior or commitment from the target
  customer or buyer.
- Never continue validation after decisive negative evidence merely to produce a
  prettier report.
