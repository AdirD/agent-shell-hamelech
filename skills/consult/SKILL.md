---
name: consult
description: >-
  Get an unbiased second opinion, peer review, sanity check, or multi-expert
  council on an architectural choice, difficult bug, code diff, plan, or naming
  dilemma. Isolates context, briefs fresh subagents without leading the witness,
  and synthesizes consensus vs divergence into actionable trade-offs. Use when
  the user asks to "consult", "second opinion", "peer review", "sanity check",
  "ask another model", or "convene a council".
disable-model-invocation: true
---

# Consult

Single conversation threads suffer from **context inertia, fatigue, and confirmation bias**:
- The agent agrees too easily with the user or with its own prior assertions.
- Chat history clutters the problem with discarded hypotheses and tangents.
- Hard trade-offs get glossed over because no one is dedicated to arguing the counter-case.

`consult` breaks out of the loop by packaging the dilemma cleanly, delegating to one or more fresh, isolated subagent consultants (or deeper model tiers), and synthesizing the delta into a clear, decisive verdict.

---

## When to Reach for Consult

- **Second Opinion / Sanity Check**: You or the agent reached a conclusion on an architecture, naming, or bug fix, but want fresh eyes before committing.
- **Peer Review**: You have a plan, diff, or RFC draft that needs an independent critique.
- **Expert Council (Triangulation)**: A complex decision with competing priorities (e.g., simplicity vs. scale, speed vs. security, DX vs. purity).
- **Devil's Advocate (Red Team)**: You want someone whose explicit job is to kill the proposal and find the hidden landmines.

---

## The 4-Step Consultation Workflow

### 1. Calibrate Mode & Roles

Detect what the user hinted to or pick the appropriate consultation format:

| Format | When to use | Agents / Roles |
|---|---|---|
| **Second Opinion** (Default) | Sanity check on a decision, hypothesis, or naming dilemma | 1 subagent (deeper model tier / fresh eyes) |
| **Peer Review** | Reviewing a diff, refactor, or RFC | 1–2 subagents (e.g., *Staff Reviewer*, *Domain Specialist*) |
| **Expert Council** | Complex multi-variable fork with competing trade-offs | 2–3 subagents with distinct lenses (e.g., *Pragmatist/80-20*, *Security/Reliability*, *API/DX*) |
| **Devil's Advocate** | Stress-testing a seemingly solid proposal | 1 subagent with an explicit adversarial mandate to find failure modes |

---

### 2. Package the Dilemma (Anti-Bias Briefing)

**Never dump the raw chat history.** Cleanly isolate and distill only what the consultant needs:

1. **Context & Objective**: What is being built and what must be true.
2. **Hard Constraints**: Codebase realities, team rules, invariants, performance limits.
3. **Options on the Table**: The candidates being evaluated.
4. **Prior Rejections & Rationale**: What was already considered and why it failed (avoids retreading old ground).
5. **Evaluation Criteria**: Specific questions the consultant must answer.

#### The Golden Rule: Do Not Lead the Witness
- **Don't say**: *"We think Option A is best because of X. Do you agree?"*
- **Do say**: *"Evaluate Option A vs Option B under constraint X. Detail the sharpest trade-off of each and pick one."*

---

### 3. Dispatch the Consultation

- **When subagent tools are available (`invoke_subagent`, background agents)**:
  - Launch subagents with distinct `Role` and appropriate `Model` (e.g., heavier reasoning tier like `pro` for subtle architectural trade-offs).
  - For an **Expert Council**, dispatch all consultants concurrently in a single invocation.
- **When running in environments without subagent tools**:
  - Formulate the clean prompt explicitly, run simulated adversarial/distinct role passes with strict isolation, and clearly label the simulated perspectives.

---

### 4. Synthesize Consensus vs. Divergence

When consultant responses arrive, **do not dump raw transcripts**. Deliver a synthesized briefing with four distinct components:

1. **Consensus (The Ground Truth)**: Points where all consultants (and the host agent) agree.
2. **Divergence & Clashes**: Where the consultants disagree, and the underlying trade-off driving the split (e.g., short-term velocity vs. long-term maintenance).
3. **Blindspots Exposed**: Surfaced risks, edge cases, or novel alternatives that neither you nor the original chat had considered.
4. **Decisive Recommendation**: The host agent's bottom-line recommendation, leaving the final choice to the user.

---

## Relationship to Sibling Skills

| Skill | How it differs |
|---|---|
| `consult` | Spins up **isolated subagents / councils** for unbiased second opinions, peer review, and triangulation across distinct roles or models. |
| `challenge` | In-thread, conversational Socratic grilling. Asks high-value questions one at a time to poke holes directly with the human. |
| `distill-need` | Intercepts the user ask to uncover the true underlying problem and non-build options before any design starts. |
| `8020` | Finds the smallest, least-invasive implementation path once the direction is decided. |

---

## Example Briefings & Syntheses

### Example 1: Naming or API Design Dilemma

```markdown
**Subagent Prompt:**
You are an API Design Consultant. Evaluate 3 candidate function signatures for our batching queue.
Constraints: Must support backpressure, zero memory allocations on hot path, backward compatible with v1.
Rejected: sync callback pattern (caused deadlocks in v1).
Task: Rank the candidates, critique the top pick's failure mode, and recommend the cleanest API.
```

### Example 2: Expert Council Triangulation

```markdown
**Council Dispatched:**
1. *Pragmatic / 80-20 Architect* (Focus: minimal diff, reuse existing Postgres tables)
2. *Distributed Systems Specialist* (Focus: horizontal scaling, idempotency, event ordering)
3. *Security / Compliance Lead* (Focus: audit trails, tenant data isolation)

**Synthesized Verdict:**
- **Consensus**: All 3 agree that introducing a separate Redis cluster is premature for current QPS.
- **Clash**: Pragmatist favors polling the existing DB; Distributed Specialist warns of row locking under peak burst.
- **Recommended Path**: DB table with optimistic locking (`SKIP LOCKED`) — hits the 80/20 simplicity while avoiding the row contention.
```

---

## Do / Don't

**Do:**
- Give consultants distinct mandates and roles so they don't echo each other.
- Use higher reasoning model tiers when consulting on subtle bugs or architectural forks.
- Present the clash cleanly: *"Expert A prioritized speed; Expert B prioritized failure recovery."*
- State the bottom-line recommendation clearly so the user can make an informed call in 5 seconds.

**Don't:**
- Dump full subagent transcripts into the user chat.
- Frame the prompt in a way that telegraphs your preferred outcome.
- Run a 3-agent council for trivial, low-stakes questions (e.g., standard CSS styling).
- Leave the user with a generic "it depends" without taking a stand.
