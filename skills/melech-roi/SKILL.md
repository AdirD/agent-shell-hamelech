---
name: melech-roi
description: Grade whether a change's complexity and blast radius are actually worth the benefit it delivers, using an itemized ROI receipt and rankings among solutions already raised. Use on an existing PR, a local diff, or an idea still being discussed before any code exists. Trigger on "is this worth it", "ROI on this fix", "are we overengineering this bugfix", "worth the blast radius", or when a small fix seems to be touching shared systems, adding state, or expanding scope out of proportion to what it fixes.
disable-model-invocation: true
---

# ROI

## The core question

The whole thing in one story:

> Your tap drips. Fix A reroutes the pipes for the whole house so that tap
> stops dripping. Fix B replaces the washer in that one tap. Both fix the
> drip. Only one of them means every future plumber has to understand the
> whole house's new plumbing just to work on a different tap someday.

That's it. That's the entire skill. It just asks, every time:

> **Are we rerouting the house, or replacing the washer?**

- **Replacing the washer** — a local, contained fix at the exact leak.
- **Rerouting the house** — a shared boundary, new persisted state, a new
  lifecycle, or broad blast radius, paid to fix one drip.

`melech-roi` exists to catch the second disguised as the first — on code that
already exists or on an idea that hasn't been coded yet. It evaluates the
solution in front of it; it does not design a replacement.

If the plumbing picture isn't landing for whoever you're talking to, four
other everyday pictures for the same question (packing, renovation permits,
toolbox, alterations) are in
[`references/analogies.md`](references/analogies.md).

## What it judges

**Benefit** — how real and large is the drip: severity, reach (how many
users/paths), frequency, durability of the fix, strategic value.

**Burden** — how much of the house does this reroute: shared boundaries
touched, new persisted state or lifecycle, regression exposure, new concepts a
future maintainer must learn, reversibility.

**Verdict** — does the burden match the benefit, or is the house being
rerouted for one drip?

**Receipt** — where the solution earned and lost ROI: problem reach versus
solution reach, value received, cost charged, and the largest charge.

## Sources you can point it at

- an existing PR (diff + description + discussion),
- a local diff (staged/unstaged, branch vs base),
- an idea or direction still only discussed in conversation — no diff exists
  yet, so flag confidence as lower and call assumptions out as assumptions.

Resolve the source from context. Ask only if genuinely ambiguous.

## Workflow

1. **Name the drip.** State the actual benefit being pursued in one line. If
   the benefit itself is unclear or unproven, mark confidence low and name the
   missing evidence. Do not silently invent benefit.
2. **Trace the touched surface.** For code: shared modules, persisted state,
   public contracts, new dependencies, call sites, concepts. For an idea:
   what it would require touching once built.
3. **Compare reach using the same unit.** Show who experiences the problem
   beside who must carry the solution: paths, callers, users, jobs, records, or
   another grounded unit. Use `unknown` rather than fake precision.
4. **Itemize the receipt.** List concrete value received and permanent costs
   charged. Mark cost severity `LOW`, `MEDIUM`, or `HIGH`.
5. **Find the largest charge.** State the single clearest source of
   disproportionality, or explain why the broad reach is justified.
6. **Grade the current solution.** The score measures proportionality, not how
   close the developer came to an imaginary perfect implementation.
7. **Rank only existing candidates.** If the PR or discussion already contains
   multiple concrete solutions, evaluate and rank those. Never invent an
   alternative to complete a ranking.
8. **Render the receipt.** Use the visual contract and adapt the examples in
   [`references/output-examples.md`](references/output-examples.md).

## Output shape

The default output is one itemized receipt:

1. solution name;
2. ROI score and letter grade;
3. rank only when two or more solutions were already raised;
4. problem-reach and solution-reach bars in a comparable unit;
5. value received;
6. cost charged with severity;
7. the largest charge;
8. a one-sentence verdict about the current solution.

The receipt diagnoses; it does not prescribe. Do not add a replacement design,
an improvement plan, or a "do this instead" section.

Interpret grades consistently:

- **A (85–100):** burden is clearly proportionate to the benefit.
- **B (70–84):** worthwhile with real but bounded cost.
- **C (55–69):** works, but has a meaningful reach or complexity mismatch.
- **D (40–54):** burden exceeds the demonstrated benefit.
- **F (0–39):** severely disproportionate or mostly unsupported.

Use `+` or `−` only to express a position near a grade boundary. A developer
does not need to reach 100; the grade answers whether this solution is
proportionate. The itemized charges explain why.

Read [`references/output-examples.md`](references/output-examples.md) before
rendering the result. It contains examples for disproportionate, justified,
operationally costly, ranked, and low-confidence solutions.

## Boundary with other skills

- **`melech-distill-need`** — establishes whether the drip is real when the
  benefit itself is in doubt.
- **`melech-8020`** — designs a cheaper shape after `melech-roi` diagnoses a
  mismatch. `melech-roi` itself does not propose that shape.
- **`melech-tidy`** — executes the adaptive diff reduction (purging dead residue,
  narrowing seam blast radius, and shaking prompt bloat) once `melech-roi` has
  graded the existing diff. `melech-roi` evaluates; `melech-tidy` changes.
- **`melech-challenge`** — pressure-tests a whole direction with open
  questions. `melech-roi` asks one narrower question: is the touched surface
  proportionate to the benefit.

Typical chain: `melech-distill-need` → `melech-roi` → `melech-8020` /
`melech-tidy`.

## Do / Don't

**Do:** Show "one submission path" beside "47 request paths," then itemize the
shared middleware, persisted state, and cleanup lifecycle as charges.

**Don't:** Show only "ROI: 58%" with no receipt explaining where ROI was lost.

**Do:** "This bug happens at every entry point that submits data — a shared
fix genuinely matches a shared benefit here. This is not overreach; proceed."

**Don't:** Force a poor grade onto a genuinely systemic fix just because it
touches shared code.

**Do:** On a transcript idea, not yet coded: "Still a direction, not a diff —
confidence is lower. The proposal's permanent shared-service cost is better
evidenced than the number of workflows receiving its benefit."

**Don't:** Invent precise reach counts, candidate solutions, or a replacement
design when the evidence does not contain them.
