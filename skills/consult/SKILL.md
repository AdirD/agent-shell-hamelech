---
name: consult
description: >-
  Double-check, proof, and stress-test an AI-proposed implementation,
  architecture, plan, or product idea before committing. Isolates the proposal,
  briefs fresh subagents or an expert council without grading its own homework,
  and synthesizes consensus vs flaws into concrete adjustments. Use when the
  user asks to "double check", "proof this", "consult", "second opinion", "ask
  another model", "are you sure", or "convene an expert council" on a proposal.
disable-model-invocation: true
---

# Consult

When an AI proposes an architecture, implementation plan, or idea, asking the *same* conversation thread *"are you sure?"* fails:
- It suffers from **self-grading bias** (eagerly rationalizing its own proposal).
- It suffers from **thread fatigue** (trapped in the same assumptions and blind spots).
- It agrees too easily with whatever direction was already discussed.

`consult` is the **proof-and-verify circuit**. It takes the proposal on the table, packages it into an objective brief, hands it to fresh isolated subagents (or an expert council / deeper model tier) to stress-test and proof, and reports back the independent findings without defending the original idea.

---

## When to Reach for Consult

Reach for `consult` **after a direction, plan, or architecture has been proposed** and you want it proofed before building:

- *"Double-check this implementation plan before we start coding."*
- *"Proof this architecture with another model."*
- *"Are you sure about this fix? Get a second opinion."*
- *"Convene an expert council to poke holes in this idea."*
- *"Have a devil's advocate red-team your proposed approach."*

---

## What You Can Proof & Double-Check

`consult` proofs both **Implementation & Architecture** and **Product & Ideas**:

| Consultation Format | For **Implementation & Architecture** Proposals | For **Product & Idea** Proposals |
|---|---|---|
| **Double-Check / Second Opinion** *(Default)* | Proofs a proposed code diff, refactor, DB schema, or bug fix for subtle flaws, race conditions, or missing edge cases. | Sanity-checks a proposed feature concept, workflow, or positioning against market reality. |
| **Peer Review** | Independent staff-engineer critique of a written RFC, plan, or API design before implementation. | Independent product-manager critique of a PRD, user journey, or pitch. |
| **Expert Council** | Triangulates the proposal across 2–3 competing technical lenses (e.g. *Pragmatist / 80-20* vs. *Scale / Concurrency* vs. *Security / Blast Radius*). | Triangulates the proposal across 2–3 business lenses (e.g. *User Value & WTP* vs. *Growth & Distribution* vs. *MVP Feasibility*). |
| **Devil's Advocate (Red Team)** | Explicit mandate to break the proposed code: find why it will fail in production, deadlock, or degrade performance. | Explicit mandate to shoot down the idea: why users won't switch, why incumbents win, and flawed assumptions. |

---

## The 4-Step Proofing Workflow

### 1. Freeze the Proposal (Take off the Author Hat)

You are no longer defending your idea. Extract the current proposal into a clean, standalone brief:
- **Core Objective**: What problem this is trying to solve.
- **The Proposed Approach**: The exact mechanism, architecture, or workflow proposed.
- **Key Invariants & Constraints**: Performance limits, existing patterns, backward compatibility.
- **Alternatives Already Rejected**: What was considered and ruled out (so consultants don't waste time suggesting them).

---

### 2. Brief the Consultant (The Anti-Self-Grading Rule)

**Never lead the witness or ask for validation.**

- **DON'T SAY**: *"I proposed using a Redis queue because it's fast. Do you think that's a good idea?"*
- **DO SAY**: *"Here is a proposed implementation using a Redis queue for task batching under constraints [X, Y]. Audit this approach: identify failure modes, edge cases, operational costs, and whether a simpler in-process or DB solution was overlooked."*

---

### 3. Dispatch the Consultation

- **When subagent tools are available (`invoke_subagent`, background agents)**:
  - Launch subagents with distinct `Role` and appropriate `Model` (e.g. deeper reasoning tier like `pro` for architectural sanity checks).
  - For an **Expert Council**, dispatch all 2–3 consultant lenses concurrently in a single call.
- **When running without subagent tools**:
  - Explicitly construct the adversarial/distinct role perspectives with strict isolation, clearly labeling the independent audit.

---

### 4. Synthesize the Proofing Verdict

Do not dump raw transcripts. Deliver a clean 4-part synthesis:

1. **Verified Solid**: Parts of the proposal that held up under independent scrutiny.
2. **Flaws, Landmines & Blind Spots**: Concrete failure modes, missing edge cases, or unwarranted complexity exposed by the consultants.
3. **Consensus vs. Clashes**: Where the consultants agree vs. where trade-offs clash (e.g. simplicity vs. scale).
4. **Concrete Adjustments (The Adjusted Plan)**: Actionable changes to make to the proposal before starting implementation.

---

## Example Proofing Runs

### Example 1: Double-Checking an Implementation Proposal

```markdown
**Context**: AI proposed adding an in-memory cache with TTL for user permissions.
**User**: "Double-check this with another model before we write code."

**Consultant Prompt**:
You are a Staff Systems Engineer. Audit this proposed permission-caching design:
Proposal: In-memory cache with 60s TTL on the API gateway.
Constraints: Multi-tenant SaaS, instantaneous permission revocation required for offboarded admins.
Task: Find where this breaks, evaluate cache invalidation complexity, and recommend the soundest fix.

**Synthesized Verdict**:
- **Landmine Exposed**: 60s TTL violates the hard requirement of instantaneous revocation for security offboarding.
- **Consultant Recommendation**: Use Redis Pub/Sub invalidation events or check revocation status via Redis bitmap rather than a blind TTL.
- **Adjusted Plan**: Switch from pure TTL to a lightweight revocation check endpoint.
```

### Example 2: Expert Council on a Proposed Feature Idea

```markdown
**Context**: AI pitched building a custom automated visual diffing engine for PRs.
**User**: "Convene a council to proof this idea."

**Council Dispatched**:
1. *Pragmatist / 80-20 Lead* (Focus: build vs. buy, maintenance burden)
2. *Developer Experience Reviewer* (Focus: workflow friction, false-positive noise)
3. *Technical Architect* (Focus: headless browser rendering cost, CI latency)

**Synthesized Verdict**:
- **Consensus**: All 3 agree that building a custom diff engine from scratch has high maintenance overhead and false-positive flake.
- **Clash**: DX wants rich inline PR comments; Pragmatist recommends integrating existing GitHub Actions / Percy CLI instead of building a service.
- **Adjusted Plan**: Don't build a custom engine; write a 20-line GitHub Action wrapper around an existing open-source visual regression tool.
```

---

## Do / Don't

**Do:**
- Use `consult` whenever the user says "double check", "are you sure", or asks for a second opinion on a proposal.
- Welcome flaws and pushback from the consultants — proving the idea wrong early saves hours of wasted coding.
- Keep the briefing neutral and adversarial so the consultant actively tries to break the proposal.
- End with a concrete, adjusted proposal ready for the user to greenlight.

**Don't:**
- Defend your original proposal when a consultant points out a valid flaw.
- Ask the consultant to "confirm" or "validate" your idea.
- Dump raw subagent logs or transcripts into the chat.
- Propose changes without explaining *why* the consultation altered the plan.
