---
name: distill-need
description: >-
  Distill the real need behind a user request before obeying it. Treat the
  literal ask as a proposed solution, uncover the outcome that must be true,
  check context and existing alternatives, and surface better solution
  categories — including non-build options. Use when the user asks to
  "distill-need", "distill this", "what do I actually need", "faster horse",
  or says not to just implement what they asked.
disable-model-invocation: true
---

# Distill Need

The user's request is not scripture. It is usually a **proposed solution**.

People often:

- do not know exactly what they are asking for
- do not know what they actually need
- do not know existing solutions already cover it

Naive AI bullseyes the words. Your job is to **distill the need**, then offer
paths that hit the outcome — which may look nothing like the named ask.

Classic pattern:

- Ask: "I need a faster horse."
- Distill: get to B faster.
- Better means: a car — or walk, if work is ten feet away.

## What You Are Trying To Achieve

Separate:

1. **Literal ask** — the named feature, tool, or implementation
2. **Actual need / goal** — what must be true for the user to be happy
3. **Context** — constraints that can collapse or change the problem
4. **Better means** — including reuse, process change, or don't-build

Then let the **user decide**. Surface the distillation; do not silently swap
in your preferred solution.

## Workflow

### 1. Catch the proposed solution

Restate the literal ask in one line. Mark it as a proposed solution, not the
mission.

### 2. Distill the outcome

Ask the smallest set of questions that reveal:

- what must be true when this is done
- why they want it now
- what pain happens if nothing changes

Prefer 1–3 high-leverage questions. Batch when forks are clear.
Do not run a long intake.

### 3. Check collapsing context

Look for facts that change the category of solution:

- constraints, proximity, frequency, urgency, scale
- who feels the pain
- what "done" means in their world

If context is missing and would change the answer, ask for it.
If you can infer safely from the repo/product, say the assumption.

### 4. Check existing solutions

Before inventing:

- is there already a wheel in the codebase, product, or process
- are they reinventing it
- worse: reinventing it as a rectangle
- if a known library, tool, or service may already do it, point the user at `scout`

Prefer integrate / reuse / configure over greenfield when it hits the need.

### 5. Offer solution categories

Give 1–3 meaningfully different means to the same outcome. At least consider:

- **don't build** / manual / process / existing tool
- **smallest change** to something that already exists
- **the named ask** (or a cleaned version), if it still earns its place

For each path: outcome fit, cost, what you sacrifice, and when you'd choose it.
Recommend one. User picks.

### 6. Hand off

- If the need dies or "walk" wins → stop. No plan, no code.
- If still build-shaped → hand to `pre-plan` and/or `8020`.
- If they already had a direction and only needed holes poked → `challenge`.

## Question Filter

Ask only what would change:

- the outcome definition
- the solution category
- whether building is justified
- whether something existing already solves it

Do not ask implementation trivia. Do not invent requirements theater.

## Relationship To Sibling Skills

| Skill | Relationship |
|---|---|
| `pre-plan` | After distillation, if the work is still build-shaped: align the shared concept. |
| `8020` | After the need is clear: pick the smallest useful path to that outcome. |
| `product-ideation` | Broader / earlier product premise work. Use when the idea itself is still open, not when a concrete ask needs interception. |
| `challenge` | Pressure-tests an existing direction. Does not primarily re-category the ask. |
| `scout` | Verified search for existing libraries, tools, services, or products that already deliver the outcome. |

`distill-need` is the intercept. It can end with **don't build**.

## Do / Don't

**Do:** "You asked for a faster horse. Outcome seems to be: get to work faster. You live 10 feet away — walking beats breeding. If the real constraint is weather/status/cargo, say which and we re-open."

**Don't:** Start designing a horse-optimization service.

**Do:** "You asked for a new notification microservice. Need seems to be: users notice failed billing. Existing email + in-app banner may cover it. Options: (1) reuse banners, (2) extend current notifier, (3) new service. I recommend (1)."

**Don't:** Scaffold the microservice because that was the noun in the sentence.

**Do:** "Literal ask: custom RBAC engine. Distilled need: hide admin screens from non-admins. Role check on two routes may be enough. Confirm the outcome before we invent a policy framework."

**Don't:** Treat the named architecture as sacred.

**Do:** Recommend, then wait for the user to choose.

**Don't:** Silently replace their ask with your pet solution and start coding.
