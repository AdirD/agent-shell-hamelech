# Lane 4 — Cosmetic Diff Noise (deep playbook)

> The full playbook behind Tidy's **Diff noise** lane (internal anchor:
> Lane 4). Tidy's [`SKILL.md`](../SKILL.md) owns scope resolution, the unified
> evidence table, approval, and verification. This file owns finding
> decomposition, canonical-equivalence proofs, and fail-closed guardrails.
>
> User-facing short label in the evidence table / approval / summary:
> **Diff noise** — never print "Lane 4".

## Goal

> Remove standalone cosmetic churn from the review without changing behavior,
> instruction effect, dependency resolution, or any other intended meaning.

This is not a blind line-movement detector. The agent reads the requested
outcome and surrounding artifact before deciding why a line moved. A declaration
moved to fix scope, initialization order, or timing is semantic and must stay.

## Boundary with the semantic lanes

The lanes classify **recommended reductions**, not every changed line:

- **Diff noise**: the canonical artifact is unchanged; restore representation.
- **Dead code**: a semantic code construct exists but is unnecessary; delete it.
- **Blast radius**: required semantic behavior exists but is implemented across
  too much surface; re-anchor it.
- **Prompt bloat**: semantic instruction content exists but is redundant or
  non-load-bearing; cut or collapse it.

A behavior-preserving refactor is still semantic: renames, helper extraction,
condition rewrites, and reordered logic change the parsed structure and belong
under **Blast radius** when they unnecessarily broaden the diff.

## Core rule: proof or keep

Assign **Diff noise** only when all four proofs hold:

| Proof | Question | Required evidence |
|---|---|---|
| **Intent** | Why did this line move or change? | The requirement and surrounding context show no intended behavior, instruction, dependency, or contract change. |
| **Canonical equivalence** | Is the artifact structurally the same? | A repository-appropriate parser, normalizer, formatter, or semantic comparison produces the same canonical artifact before and after. |
| **Significance** | Could this representation carry meaning here? | Language- and repository-specific checks rule out meaningful whitespace, ordering, comments, line endings, modes, snapshots, or generator output. |
| **Revert safety** | Can the representation return to base safely? | Required format, generation, build, and test checks remain green after restoration. |

If any proof is missing, do not report the finding as **Diff noise**.

## Unit of routing: an isolated finding

`git diff` hunks are input, not automatic findings. One hunk can contain several
changes, and one logical change can span several hunks.

1. Read the requirement and the full surrounding block.
2. Split independent cosmetic and semantic changes only when they can be
   restored separately.
3. If cosmetic lines are inseparable from a semantic edit, the semantic lane
   owns the whole finding.
4. Do not emit a second Diff noise row for whitespace that disappears when an
   approved Dead code, Blast radius, or Prompt bloat action is applied.

Example:

```diff
-const result=calculate(a,b)
+const result = calculate(a, c)
```

Formatting changed, but so did the argument. This is a semantic finding, not
Diff noise. Do not split a single line to manufacture a cosmetic recommendation.

## Canonical evidence by artifact type

Use the repository's own tools and conventions where available.

| Artifact | Possible evidence | Common significance traps |
|---|---|---|
| Source code | Same parsed structure or token stream after safe formatting normalization | Python/YAML indentation, string or template contents, heredocs, macros, comment directives |
| Imports | Same import structure and relative order, or a language/tool guarantee that the changed order is inert | Module side effects, initialization order, CSS cascade |
| Markdown prompts/rules | Same instruction text and same parsed Markdown structure after rewrapping | Hard line breaks, lists, code fences, indentation, YAML frontmatter |
| Structured data | Equal parsed value under the repository's canonical serializer | Consumers that preserve order, duplicate keys, comments in JSON-like formats |
| Lockfiles | Identical resolved dependency graph, versions, integrity data, and package-manager semantics | Resolver or package-manager version changes, integrity/hash changes |
| Generated artifacts | Identical canonical generated content backed by unchanged source inputs | Stale output, generator-version drift, manual edits |
| Line endings | Repository attributes and file type prove the EOL change inert | Shell scripts, batch files, Makefiles, byte-sensitive fixtures |
| File mode | No shebang, direct execution, hook, CI invocation, or deployment dependency | `100644` ↔ `100755`, symlinks, executable entrypoints |
| Snapshots/fixtures | Consumer compares a normalized representation rather than bytes | Exact byte/text assertions, visual snapshots |

These are candidate proof methods, not permission to assume equivalence. A
formatter touching a file or a generator writing output does not itself prove
that the delta is cosmetic.

## Lane-specific method

*(Scope, approval, and final verification are handled by the Tidy workflow.)*

### 1. Find suspicious cosmetic churn

Look for formatter sweeps, whitespace-only hunks, line-ending changes, harmless
paragraph wrapping, metadata flips, and serializer churn that obscure the
requested change.

### 2. Establish intent

Trace each candidate back to the requested outcome and its local context. If
the movement fixes execution order, scope, control flow, rendering, instruction
structure, dependency resolution, or another observable contract, keep it.

### 3. Prove canonical equivalence

Compare base and changed versions with the narrowest trustworthy mechanism
available. Prefer repository-enforced parsers and formatters over visual
inspection. Record the exact comparison used.

### 4. Check revert safety

Restore the candidate representation in a temporary or working comparison and
run the relevant formatter/generator check plus focused build or tests. If the
repository requires the new representation, it is not removable noise.

### 5. Recommend restoration

Report the finding with its proof and propose restoring the base representation
or regenerating with the expected pinned tool. Never hand-edit lockfiles or
generated artifacts merely to make the diff smaller.

## Evidence-table examples

```markdown
| Lane | Target | Issue / Evidence | Proposed Action | Risk |
|---|---|---|---|---|
| **Diff noise** | `src/view.ts:L20-L80` | **Canonical equivalence**: parsed structure is identical; the delta disappears under the repo formatter and checks pass after restore. | Restore base formatting outside the functional edit | Low |
| **Diff noise** | `skills/review/SKILL.md:L12-L18` | **Canonical equivalence**: paragraph text and Markdown structure are identical; only wrapping changed. | Restore base wrapping | Low |
```

Bad evidence: "looks cosmetic," "only moved two lines," "Prettier did it," or
"this file is generated." Name the context and comparison that proved it.

## Do / Don't

**Do:** recognize that moving `const x` before its use may be the bug fix.
**Don't:** classify movement by line count alone.

**Do:** fail closed when import order or whitespace might carry meaning.
**Don't:** assume compilation success proves identical runtime behavior.

**Do:** let a semantic lane absorb inseparable surrounding cosmetics.
**Don't:** double-report the same hunk under Diff noise and another lane.

**Do:** restore representation only after explicit approval.
**Don't:** turn Diff noise into a general refactor or scope-cutting lane.
