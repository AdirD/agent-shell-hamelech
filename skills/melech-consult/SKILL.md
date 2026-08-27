---
name: melech-consult
description: Convene Beit Hillel and Beit Shammai to expose the real disagreement inside an AI-proposed plan, fix, architecture, or idea, using fresh independent models when available, then preserve both arguments while recommending what to do now. Use for "double check", "proof this", "are you sure", "argue both sides", second opinions, or an expert council before implementation.
disable-model-invocation: true
---

# Consult

When an AI proposes an architecture, implementation plan, or idea, asking the *same* conversation thread *"are you sure?"* fails:
- It suffers from **self-grading bias** (eagerly rationalizing its own proposal).
- It suffers from **thread fatigue** (trapped in the same assumptions and blind spots).
- It agrees too easily with whatever direction was already discussed.

`melech-consult` is a **machloket l'shem shamayim**: a disagreement in service of finding what is true and useful, not winning.

Take the proposal off the author's desk and into the beit midrash. Find the consequential tension inside it, then constitute **Beit Hillel** and **Beit Shammai** around the two strongest coherent readings. At standard and deep effort, give each house a fresh isolated model from a different provider when available. The houses argue the question, not the user. Neither is a disposable devil's advocate.

The result is not flattened consensus. Deliver a **psak for now** while preserving the minority opinion and the conditions that should reopen the decision.

---

## When to Reach for Consult

Reach for `melech-consult` **after a direction, plan, or architecture has been proposed** and you want it proofed before building:

- *"Double-check this implementation plan before we start coding."*
- *"Proof this architecture with another model."*
- *"Are you sure about this fix? Get a second opinion."*
- *"I can see two valid sides. Argue both before we choose."*
- *"Convene Beit Hillel and Beit Shammai on this idea."*

Do not use it for loose ideation with no proposal yet. Do not use it when the user wants one conversational partner or a sequence of clarifying questions. Consult begins when there is something concrete enough to disagree about.

---

## The Core Distinction

This is not generic "pros and cons."

- **Pros and cons** produce a bag of points.
- **Red teaming** appoints one side to attack.
- **An expert council** often collects unrelated lenses and averages them.
- **Machloket** identifies the decision's governing tension and develops both positions as complete, defensible approaches.

Beit Hillel and Beit Shammai are not fixed personality presets. Do not caricature Hillel as always permissive or Shammai as always strict. Derive the houses from the actual fork:

| One house protects | The other protects |
|---|---|
| Simplicity and reversibility now | Guarantees and future failure cost |
| Developer autonomy | Organizational consistency |
| Speed to market | Operational resilience |
| User delight | Commercial viability |
| Adopting a mature capability | Owning a strategic capability |

The names create a structure for principled disagreement; they do not predetermine which principle wins.

---

## Effort

Calibrate the consultation to the stakes:

| Level | Use when | Dispatch |
|---|---|---|
| **Light** | A narrow fix or direct "get a second opinion" request | One fresh model develops both readings. Label it a single-model machloket, not independent corroboration. |
| **Standard** *(default)* | A meaningful technical or product fork | Two houses, two fresh models from different providers, dispatched independently. |
| **Deep** | The decision is expensive, hard to reverse, or genuinely balanced | Standard, followed by one steelman-and-response round. Add a specialist only for an orthogonal factual invariant. |

Never add agents merely to make the court look impressive. A security, legal, data, or concurrency invariant may need a specialist; it is not automatically a third "opinion."

---

## Workflow

### 1. Freeze the Proposal

You are no longer defending your idea. Extract the current proposal into a clean, standalone brief:
- **Core Objective**: What problem this is trying to solve.
- **The Proposed Approach**: The exact mechanism, architecture, or workflow proposed.
- **Key Invariants & Constraints**: Performance limits, existing patterns, backward compatibility.
- **Alternatives Already Rejected**: What was considered and ruled out (so consultants don't waste time suggesting them).

### 2. Find the Live Machloket

State the real fork in one sentence:

> Should we optimize for **A**, accepting **its cost**, or for **B**, accepting **its cost**?

A live machloket requires two approaches that can both plausibly satisfy the objective while protecting different values or assumptions.

Do not manufacture symmetry:
- If one side already violates a hard requirement, stop before constituting houses and use the **No Live Machloket** output below.
- If the disagreement is factual, stop and use the **No Live Machloket** output with the evidence or measurement needed next. Do not turn missing data into a philosophical dispute.
- If both houses later converge, use the **No Live Machloket** output rather than inventing conflict or a minority opinion.

### 3. Constitute the Houses

Give both houses the same frozen brief, then assign each a positive mandate:

- **Beit Hillel**: develop the strongest workable case for one side. State what it protects, what it sacrifices, its failure modes, and the conditions under which the other house would be right.
- **Beit Shammai**: do the same for the competing side.

Each house must argue an implementable position, not merely criticize the other. The assignment should follow the actual tension, not stereotypes attached to the house names.

Brief neutrally. Never lead the witness or ask for validation.

- **DON'T SAY**: *"I proposed using a Redis queue because it's fast. Do you think that's a good idea?"*
- **DO SAY**: *"We need durable task execution under constraints [X, Y]. The live fork is Postgres-backed simplicity now versus Redis-backed operational capability. Argue the assigned side as the strongest complete approach; name its costs, failure modes, and when the other side should win."*

### 4. Dispatch Independently

- **Light**:
  - Give one fresh eligible model the neutral brief and ask it to develop both houses.
  - Exclude the model that authored the proposal when its identity is known.
  - Label the result **single-model machloket / second opinion**, not independent corroboration.
- **Standard or deep**:
  - Give each house a deliberately distinct model from a different provider.
  - Exclude the model that authored the proposal when its identity is known. Never use `inherit`.
  - Dispatch both houses concurrently in one call and keep first-round arguments isolated.
  - If two eligible providers are unavailable, prefer two distinct models and disclose the limitation. If only one fresh eligible model is available, downgrade to light rather than manufacturing diverse corroboration.
- **Without subagent tools**:
  - Construct both positions explicitly in the main thread.
  - Label the result **thread-local single-model machloket** and disclose that it does not solve self-grading bias.

If subagent tools exist but no fresh model is eligible because only the author model or `inherit` is available, use the same disclosed thread-local fallback. A weaker honest consultation is better than a fake independent one.

Shared models create shared blind spots. Report the actual dispatch honestly, including when the author model is unknown; never imply provider or model independence you did not achieve.

### 5. Let the Houses Answer Each Other (Deep Only)

Give each house the other's exact argument. Ask it to:

1. steelman the strongest point before disagreeing,
2. identify genuine common ground,
3. answer the central objection,
4. state what evidence would change its position.

Run one exchange, not an endless role-play. The purpose is to sharpen the hinge, not produce theater.

### 6. Pasken Without Erasing

Do not dump raw transcripts or count votes. Synthesize the reasoning:

1. **Common Ground (Davar Muskam)**: Facts, constraints, and parts of the proposal both houses accept.
2. **Beit Hillel**: Its complete case, what it protects, and the price it accepts.
3. **Beit Shammai**: Its complete case, what it protects, and the price it accepts.
4. **The Machloket**: The precise assumption, value, or trade-off separating them.
5. **Psak for Now**: The recommended direction for the present constraints and the concrete adjusted proposal.
6. **Minority Opinion Preserved**: What the chosen direction risks missing; do not erase the losing house's strongest warning.
7. **Reopen When**: Observable evidence, thresholds, or changed conditions that should return the minority view to the table.

The user still rules. A psak is a clear recommendation, not permission to implement without approval.

If a hard invariant decides the case or both houses converge, do not force the seven-part structure. Use:

1. **Verified Common Ground**: What scrutiny established.
2. **No Live Machloket**: Why the apparent fork collapsed.
3. **Decisive Constraint or Evidence**: The requirement, fact, or shared finding that settles it.
4. **Adjusted Proposal / Next Measurement**: What to do now, or what evidence is still needed.

There is no minority opinion when no defensible minority position remains.

---

## Example

```markdown
**Question**: Use the existing Postgres database for durable background jobs, or introduce Redis and a queue runtime?

## Common Ground (Davar Muskam)
Both houses agree jobs must survive process restarts and need bounded retries. Current volume is under 1,000 jobs/day; Redis is not otherwise provisioned.

## Beit Hillel — Postgres-backed simplicity
Use the infrastructure already operated. The current scale does not justify another datastore and operational surface. Accept lower throughput and fewer queue-native tools.

## Beit Shammai — Redis-backed queue capability
Use a mature queue runtime with explicit concurrency, retry, scheduling, and observability semantics. Accept new infrastructure now to avoid a risky migration after volume grows.

## The Machloket
Whether expected growth is credible enough to pay the operational cost before the limit is measured.

## Psak for Now
Use the Postgres-backed option behind a narrow queue interface. Do not provision Redis yet.

## Minority Opinion Preserved
The Postgres design must not spread queue semantics through business code; otherwise later migration cost validates Beit Shammai's warning.

## Reopen When
Reconsider Redis when measured queue latency breaches the product SLO, sustained volume exceeds the declared threshold, or required scheduling semantics outgrow the Postgres library.
```

---

## Do / Don't

**Do:**
- Derive the houses from the decision's real governing tension.
- Make both sides coherent enough that an intelligent person could choose either under different conditions.
- Keep first-round reasoning independent at standard/deep effort and always disclose the actual dispatch.
- Recommend what to do now and preserve what would make the other house right.
- Say when there is no legitimate machloket.

**Don't:**
- Turn Beit Hillel and Beit Shammai into lenient/strict mascots.
- Assign one house to advocate an obviously broken strawman.
- Manufacture disagreement when evidence converges or a hard invariant decides the case.
- Let the original author pose as an independent house or defend its proposal without disclosing the thread-local fallback.
- Reuse the main thread's model or duplicate models and call the result independent corroboration.
- Dump raw subagent logs or transcripts into the chat.
- Average the houses into a vague compromise that protects neither principle.
- Erase the minority opinion after issuing the psak.
