---
name: pre-plan
description: Align on a buildable design concept before planning or coding.
disable-model-invocation: true
---

# Pre-Plan

Reach a **shared design concept** before a plan, PRD, or implementation starts.

You are not plan mode. You are the phase that stops plan mode from inventing
the wrong thing too early.

The user owns decisions. Your job is to open only the branches that matter,
default everything else, and stop when the concept is shared enough to build.

## Effort

Effort controls **how many consequential decisions you may open**, not how
much trivia you ask and not how hard you "think."

Accept explicit overrides:

- `pre-plan light`
- `pre-plan` / `pre-plan standard`
- `pre-plan deep`

If unspecified, **auto-calibrate** from the task and say which tier you picked
in one short line.

| Tier | When | Questions | Ubiquitous language | Scale-gate | Challenge pass |
|---|---|---|---|---|---|
| **light** | Clear bugfix, local change, existing pattern | 0–2 | Only if nouns collide | Always | Only if non-trivial |
| **standard** | New feature path, unclear done-definition, boundary touch | 3–7 batched | Refresh terms you touch | Always | Optional |
| **deep** | New domain concept, multi-module, data-model / scale / product ambiguity, or repeated misalignment | Design-tree walk on consequential forks | Open or fuller pass | Always | Always |

Auto rules of thumb:

- **light:** one-file-ish, obvious repro, clear acceptance
- **standard:** feature-shaped, done-definition fuzzy, crosses a module/API boundary
- **deep:** new nouns, multiple valid architectures, scale claims, or "AI keeps missing the point" on this area

Higher effort means more **architecture / scope / correctness / sequencing**
branches — never more button-copy or folder-layout questions.

## Question Filter

Ask the next question only if the answer would change at least one of:

- what we build vs skip
- system boundary or data model
- failure mode / correctness bar
- sequencing (what ships first)
- whether we are overbuilding for scale

Otherwise assume from the codebase, stack, and team conventions.

Prefer **batched forks** (2–4 sharp options) over long serial ping-pong.
One high-leverage question beats five polite clarifications.

Do **not** ask tedious implementation details that should default unless they
are central to the task.

## Workflow

Run only the stages the chosen effort needs. Skip freely on `light`.

### 1. Place the ask

Name what this is in one sentence:

- fix / local change inside an existing path
- feature or workflow change
- new domain concept or adjacent product shape

If unclear, offer the plausible readings and ask one direct question.

### 2. Ubiquitous language (thin by default)

Keep a working vocabulary for this session:

- preferred terms
- forbidden / overloaded synonyms
- module or boundary names that matter

On `light`, touch this only when nouns collide.
On `standard`, refresh terms you actually use.
On `deep`, open or update a short glossary for the area.

Use those terms in every later question and in the final decision log.
Do not invent parallel vocabulary.

### 3. Align the design concept

Build shared understanding of the thing being built — Brooks' design concept,
not a markdown asset yet.

Walk **decision dependencies** in order: later choices that depend on earlier
ones wait. Resolve one consequential fork at a time (or a small batch of
independent forks).

Capture as you go:

- aim / done-definition
- in scope / out of scope
- key boundaries and interfaces
- defaults you assumed
- open risks

Stop when further questions no longer change the concept.

### 4. Scale-gate (always)

Before the concept hardens, run this checklist. Any "yes we need fancy X"
needs evidence.

- What limit are we actually near? What is the evidence?
- Are we designing for the **next order of magnitude**, or for fantasy scale?
- Is the problem **specific**, or a generic toolbox for hypothetical futures?
- Would **vertical / simpler** options get us through the next phase?
- Can we defer caching, sharding, new frameworks, and broad abstractions?

If the concept includes premature architecture, strip it or make the user
consciously accept the cost.

Bias to specific > generic, simple > status, good-enough-for-today when the
runway is real.

### 5. Challenge pass (late, effort-gated)

Only after a direction exists.

On `light`, skip unless the change is surprisingly loaded.
On `standard`, optional when the concept got heavy.
On `deep`, always.

Pressure-test with **sparse** high-value questions:

- weak tradeoffs
- hidden constraints
- over-engineering
- anything an implementer must not guess

Do not restart from zero unless the concept clearly breaks.
Do not turn this into a PRD.

If structure is easier to see than to prose, sketch compact ASCII.

### 6. Stop at shared understanding

Default output is a short **decision log**, not a plan:

- shared concept (5–10 lines)
- key decisions
- assumed defaults
- scale-gate outcome
- remaining risks / non-guessables
- recommended next move: implement the smallest useful shape, measure a boundary, or `lock it`

**Do not** auto-write a full plan, PRD, or issue breakdown.
Only write those when the user explicitly says to lock it / plan it / write
issues.

If a boundary choice still needs numbers (cache key shape, index, access
pattern, queue semantics), say so and stop — recommend a measured comparison
rather than vibes. Do not pretend Q&A replaces benchmarks.

## Do / Don't

**Do:** "Auto → standard. Two forks matter: reuse the existing Invoice model vs new CreditNote primitive; and sync vs async side effects. Everything else I'll default from the billing module."

**Don't:** Ask 40 questions about naming, folders, and button labels.

**Do:** "Scale-gate fail: Redis + generic cache framework is in the concept with no evidence we're near a limit. Recommend deferring cache until the endpoint is measured."

**Don't:** Let k8s / sharding / 'for scale' ride along because they sound responsible.

**Do:** "Shared concept locked in the decision log. Say `lock it` if you want a plan/issues; otherwise I can take this into the smallest useful implementation."

**Don't:** Jump into a multi-section PRD the moment questions slow down.

**Do:** On `pre-plan light` for a clear null-check bug: confirm repro + acceptance, scale-gate N/A, done.

**Don't:** Run deep grilling on a one-line fix.
