---
name: consult
description: >-
  Get an unbiased second opinion, peer review, sanity check, or multi-expert
  council on an idea, product direction, architectural choice, difficult bug,
  code diff, plan, or naming dilemma. Isolates context, briefs fresh subagents
  without leading the witness, and synthesizes consensus vs divergence into
  actionable trade-offs. Use when the user asks to "consult", "second opinion",
  "peer review", "sanity check", "ask another model", or "convene a council".
disable-model-invocation: true
---

# Consult

Single conversation threads suffer from **context inertia, fatigue, and confirmation bias**:
- The agent agrees too easily with the user or with its own prior assertions.
- Chat history clutters the problem with discarded hypotheses and tangents.
- Hard trade-offs get glossed over because no one is dedicated to arguing the counter-case.

`consult` breaks out of the loop by packaging the dilemma cleanly, delegating to one or more fresh, isolated subagent consultants (or deeper model tiers), and synthesizing the delta into a clear, decisive verdict.

---

## What You Can Consult On

`consult` works identically across **Ideas & Strategy** and **Code & Architecture**:

| Consultation Mode | When Consulting on **Ideas & Strategy** | When Consulting on **Code & Architecture** |
|---|---|---|
| **Second Opinion** (Default) | Sanity-checking a new startup/feature premise, positioning, or value prop. | Sanity-checking a bug root cause, naming dilemma, or technical design choice. |
| **Peer Review** | Independent product critique on an idea brief, pitch, user journey, or PRD draft. | Independent code review on a diff, refactor plan, or RFC. |
| **Expert Council** | Triangulating across *Customer Value/WTP* vs. *Distribution/Moat* vs. *Execution/Feasibility*. | Triangulating across *Pragmatist (80/20)* vs. *Scale/Performance* vs. *Security/Reliability*. |
| **Devil's Advocate** | Red-teaming the idea: why users won't switch, why incumbents will win, and hidden flaws in user behavior assumptions. | Hunting race conditions, edge-case regressions, blast-radius risks, and security landmines. |

---

## The 4-Step Consultation Workflow

### 1. Calibrate Mode & Roles

Detect what the user hinted to or pick the appropriate consultation format:

- **Second Opinion** (1 subagent / deeper model tier): Fast, high-clarity gut check from fresh eyes.
- **Peer Review** (1–2 subagents): Structured critique on a draft, brief, or diff.
- **Expert Council** (2–3 concurrent subagents): Multi-perspective triangulation when facing a thorny fork with competing priorities.
- **Devil's Advocate** (1 subagent): Explicit adversarial mandate to poke holes and stress-test the leading proposal.

---

### 2. Package the Dilemma (Anti-Bias Briefing)

**Never dump the raw chat history.** Cleanly isolate and distill only what the consultant needs:

1. **Context & Objective**: What is being evaluated and what outcome must be true.
2. **Hard Constraints**: Market realities, codebase limits, team constraints, or non-negotiables.
3. **Options on the Table**: The candidates or directions being weighed.
4. **Prior Rejections & Rationale**: What was already ruled out and why (avoids retreading old ground).
5. **Evaluation Criteria**: Specific questions or dimensions the consultant must evaluate.

#### The Golden Rule: Do Not Lead the Witness
- **Don't say**: *"We think Option A / this idea is great because of X. Do you agree?"*
- **Do say**: *"Evaluate Idea A vs Idea B under market constraint X. Detail the sharpest trade-off and failure mode of each, then pick one."*

---

### 3. Dispatch the Consultation

- **When subagent tools are available (`invoke_subagent`, background agents)**:
  - Launch subagents with distinct `Role` and appropriate `Model` (e.g., heavier reasoning tier like `pro` for subtle trade-offs).
  - For an **Expert Council**, dispatch all consultants concurrently in a single invocation.
- **When running in environments without subagent tools**:
  - Formulate the clean prompt explicitly, run simulated adversarial/distinct role passes with strict isolation, and clearly label the simulated perspectives.

---

### 4. Synthesize Consensus vs. Divergence

When consultant responses arrive, **do not dump raw transcripts**. Deliver a synthesized briefing with four distinct components:

1. **Consensus (The Ground Truth)**: Points where all consultants (and the host agent) agree.
2. **Divergence & Clashes**: Where the consultants disagree, and the underlying trade-off driving the split (e.g., short-term growth vs. high retention; speed vs. technical debt).
3. **Blindspots Exposed**: Surfaced risks, overlooked customer behaviors, or novel alternatives that neither you nor the original chat had considered.
4. **Decisive Recommendation**: The host agent's bottom-line recommendation, leaving the final choice to the user.

---

## Relationship to Sibling Skills

| Skill | How it differs |
|---|---|
| `consult` | Spins up **isolated subagents / councils** for unbiased second opinions, peer review, and triangulation across distinct roles or models on ideas or code. |
| `challenge` | In-thread, conversational Socratic grilling. Asks high-value questions one at a time to poke holes directly with the human. |
| `product-ideation` | Circular, adaptive thinking partner that broadens, reframes, and drafts working briefs for open-ended product ideas. |
| `distill-need` | Intercepts a user ask to uncover the true underlying outcome and non-build options before any design starts. |
| `8020` | Finds the smallest, least-invasive implementation path once the direction is decided. |

---

## Example Briefings & Syntheses

### Example 1: Product Idea Expert Council

```markdown
**Council Dispatched:**
1. *B2B Buyer / Willingness-to-Pay Lens* (Focus: budget holder, ROI proof, switching friction)
2. *Growth & Distribution Specialist* (Focus: customer acquisition, viral loops, time-to-value)
3. *Technical Feasibility / 80-20 Lead* (Focus: MVP scope, third-party API dependencies)

**Synthesized Verdict:**
- **Consensus**: All 3 agree the core pain is real and manual spreadsheets are the primary competitor today.
- **Clash**: Growth Specialist wants a self-serve freemium product; Buyer Lens warns enterprise security reviews will stall adoption unless SOC2 is built first.
- **Recommended Path**: Start with an un-gated single-user utility that exports CSVs (zero enterprise friction) to seed bottom-up adoption before building team collaboration.
```

### Example 2: Architecture & Code Triangulation

```markdown
**Council Dispatched:**
1. *Pragmatic / 80-20 Architect* (Focus: minimal diff, reuse existing Postgres tables)
2. *Distributed Systems Specialist* (Focus: horizontal scaling, idempotency, event ordering)
3. *Security / Compliance Lead* (Focus: audit trails, tenant data isolation)

**Synthesized Verdict:**
- **Consensus**: All 3 agree that introducing a separate Redis cluster is premature for current QPS.
- **Clash**: Pragmatist favors polling the existing DB; Distributed Specialist warns of row locking under peak burst.
- **Recommended Path**: DB table with optimistic locking (`SKIP LOCKED`) — hits the 80/20 simplicity while avoiding row contention.
```

---

## Do / Don't

**Do:**
- Use `consult` for ideas, product positioning, and strategy forks just as often as for code and architecture.
- Give consultants distinct mandates and roles so they don't echo each other.
- Use higher reasoning model tiers when consulting on subtle strategy trade-offs or complex bugs.
- Present the clash cleanly: *"Lens A prioritized viral acquisition; Lens B prioritized defensibility."*
- State the bottom-line recommendation clearly so the user can make an informed call in 5 seconds.

**Don't:**
- Dump full subagent transcripts into the user chat.
- Frame the prompt in a way that telegraphs your preferred outcome.
- Run a 3-agent council for trivial, low-stakes questions.
- Leave the user with a generic "it depends" without taking a stand.
