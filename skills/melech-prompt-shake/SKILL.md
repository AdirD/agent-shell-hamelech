---
name: melech-prompt-shake
description: Tree-shaking for prompts — strip bloat from system prompts, skill files, and instruction docs so they cover 100% of needed cases in the fewest lines.
disable-model-invocation: true
---

# Prompt Shake

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

## Workflow

- Auto-start on the working diff; audit the changed/added lines (no scope question).
- Read the whole file to catch cross-file issues (a new line duplicating an untouched one), but keep recommendations inside the diff window — target the new line, not the old.
- Audit line-by-line, tag each survivor with the proof that keeps it alive.
- Report the audit in a scannable way so the human can understand it and decide next actions — a findings table (line/block → failed proof + evidence → recommended action: cut/collapse/fold/keep). Recommend only; do NOT edit files yet.
- Apply only if the human approves, and only within the diff window.

## Guardrails

- Preserve intent and load-bearing constraints — leanness ≠ lossy.
- Behavioral over vibes: justify a cut by showing output is unchanged, not just that it "feels" redundant.
- Never invent new rules or "improve" the prompt — this is subtraction, not redesign.
