---
name: melech-minimize
description: Reduce an existing PR or diff to the smallest safe implementation that preserves its goal.
disable-model-invocation: true
---

# Minimize

Take an implementation that already exists and make it smaller, more local, and
safer to review without weakening what it must accomplish.

## Goal

> Preserve the PR's required behavior with the smallest safe diff and semantic
> blast radius.

Do not optimize line count blindly. A three-line change in shared infrastructure
can be riskier than thirty isolated lines in a leaf module.

Optimize in this order:

1. Preserve required behavior, compatibility, and correctness.
2. Avoid touching shared systems, public contracts, schemas, persisted data,
   dependencies, and cross-cutting state.
3. Reduce affected subsystems, files, call sites, concepts, and code paths.
4. Reduce changed lines.

Local duplication is acceptable when a shared abstraction would expose more of
the system to regression.

## Boundary With Other Skills

- **`melech-8020`** may negotiate or narrow the outcome to find a cheaper useful
  path before implementation.
- **`melech-prune`** proves and removes dead code, zombie paths, and YAGNI residue.
- **`melech-minimize`** keeps the outcome fixed and may replace a working,
  necessary implementation with a narrower one.

If the only meaningful reduction requires dropping or changing behavior, stop
and hand that product trade-off to the user or `melech-8020`. Do not call a
weaker result equivalent.

## Workflow

### 1. Establish the contract and diff

Resolve the comparison target from the user's command, PR metadata, or repository
conventions. Ask only when the target is genuinely ambiguous.

Write a short must-preserve contract from concrete evidence:

- acceptance criteria and bug reproduction,
- observable behavior and compatibility,
- tests and externally consumed interfaces,
- explicit non-goals.

PR descriptions and tests are evidence, not automatic truth; reconcile conflicts
against the user's stated goal and current code.

### 2. Measure the current surface

Inspect the whole diff and its integration points. Record the baseline:

- files and subsystems touched,
- new or changed public APIs, schemas, dependencies, and state,
- new abstractions and concepts,
- call sites and shared paths affected,
- relevant diff size.

Flag broad refactors, generalized machinery, parallel implementations, incidental
cleanup, and changes made only to accommodate the chosen design.

### 3. Find the narrowest safe seam

Look for an existing local branch, adapter, hook, helper, or boundary that can
carry the required behavior. Prefer, in order:

1. changing an existing leaf-level decision,
2. extending a nearby established path,
3. adding a small local implementation,
4. introducing a shared abstraction only when multiple real consumers require it.

Judge candidates by semantic exposure, not aesthetics or DRYness. Reject a
smaller textual patch when it moves risk into a more central path.

### 4. Rewrite the implementation

Remove incidental refactors and machinery that the narrower design no longer
needs. Keep edits inside the selected contract. Preserve load-bearing comments
and add no speculative flexibility.

When two implementations are behaviorally equivalent, choose the one with fewer
boundaries, assumptions, and future obligations.

### 5. Prove equivalence

Run the narrowest relevant verification first, then the repository's required
checks in proportion to risk. Confirm both:

- the must-preserve contract still holds,
- behavior outside that contract did not broaden or regress.

A smaller diff without equivalent behavior is a failed minimization.

### 6. Report the reduction

Summarize:

- contract preserved,
- original versus final files, concepts, and diff size,
- high-risk boundaries avoided or removed,
- checks run and their results,
- remaining unavoidable blast radius.

Do not claim lower risk from line count alone.

## Do / Don't

**Do:** Replace a new shared formatting service with a branch in the one existing
formatter that needs the behavior, when no other caller needs the abstraction.

**Don't:** Keep the service because it is "cleaner" or "more reusable" without a
second real consumer.

**Do:** Keep a slightly longer leaf-local change when the shorter alternative
modifies a global middleware path.

**Don't:** celebrate `-40 LOC` while expanding the regression surface to every
request.

**Do:** preserve the full accepted behavior and report when no material safe
reduction exists.

**Don't:** quietly turn minimization into scope cutting; that belongs to
`melech-8020` and the user.