# Lane 3 — Instruction & Prompt Bloat / Prompt Shake (deep playbook)

> The full handcrafted playbook behind Tidy's **Lane 3** (originally the
> standalone `melech-prompt-shake` skill). Tidy's [`SKILL.md`](../SKILL.md)
> owns the shared workflow — scope, the unified evidence table, approval, and
> verification. This file holds the lane-specific targets, proofs, and
> guardrails for tree-shaking prompts. Pull it in when Lane 3 fires and you
> need more than the 5-proof list in the router.

Tree-shaking for prompts. Every line is **guilty until proven load-bearing**. The goal is the leanest prompt that still covers 100% of needed cases — minimal-that-covers beats maximal.

## Purpose

- Strip bloat from system prompts, skill files, and instruction docs so they cover 100% of needed cases in the fewest lines.
- Subtraction, not redesign.

## Targets it hunts

- Over-explanation the model already knows by default
- Duplicate instructions (same rule stated N ways/places)
- Subset/mutually-inclusive rules (one rule already implies another)
- Redundant never-fires branches / dead edge cases
- Vague filler that adds tokens but not behavior

## The proofs

- **Coverage** — cut it: does a real required case now fall through? If not → cut.
- **Redundancy** — is this already said elsewhere? → collapse to one.
- **Subsumption** — is this a subset of a broader rule present? → fold in.
- **Default-knowledge** — would a competent model do this unprompted? → cut.
- **Load-bearing** — does output actually change with vs. without this line? If not → cut.

## Lane-specific method

*(Scope, approval, and verification are handled by the Tidy workflow.)*

- Audit the changed/added lines. Read the whole file to catch cross-file issues (a new line duplicating an untouched one), but keep recommendations **inside the diff window** — target the new line, not the old.
- Audit line-by-line, tag each survivor with the proof that keeps it alive.
- Report findings so the human can decide (line/block → failed proof + evidence → recommended action: cut/collapse/fold/keep). Recommend only; apply only within the diff window after approval.

## Guardrails

- Preserve intent and load-bearing constraints — leanness ≠ lossy.
- Behavioral over vibes: justify a cut by showing output is unchanged, not just that it "feels" redundant.
- Never invent new rules or "improve" the prompt — this is subtraction, not redesign.
