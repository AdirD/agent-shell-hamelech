---
name: melech-tidy
description: Adaptive diff reduction — prune dead code residue, minimize architectural blast radius, shake prompt bloat, and remove cosmetic diff noise before opening a PR.
disable-model-invocation: true
---

# Tidy

You just finished coding with an AI agent. The feature works and tests might pass, but `git status` shows a messy diff: orphaned helpers from earlier prompts, dead types, changes to shared infrastructure when a local fix was enough, bloated prompt instructions, or cosmetic churn that obscures the real change.

**`melech-tidy` is the universal, adaptive diff reduction engine.**

Instead of forcing you to diagnose whether your diff suffers from dead code, architectural overreach, prompt bloat, or cosmetic noise, `melech-tidy` audits your diff, categorizes findings into **four mutually exclusive reduction lanes**, presents a concrete evidentiary table, and executes surgical cleanups with your approval.

---

## The 4 Mutually Exclusive Reduction Lanes

The agent reads the requested outcome and surrounding code, decomposes the diff into findings, and evaluates each reducible finding against one strictly delineated engine. Not every changed hunk needs a recommendation.

```text
                              Incoming Working Diff
                                        │
                         Decompose into isolated findings
                         (semantic edits absorb inseparable
                              cosmetic surroundings)
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
          Canonical artifact unchanged?              Semantic change
                    │                                       │
                    ▼                         ┌─────────────┴─────────────┐
              Diff noise                 [Code / Config]       [Prompt / Rules]
          (Cosmetic-only churn)                 │                      │
                                     ┌──────────┴──────────┐           ▼
                                     ▼                     ▼      Prompt bloat
                                 Dead code           Blast radius
```

User-facing labels (always lead with these — never "Lane 1/2/3" in reports, approval options, or summaries):

| Short label | Full name |
|---|---|
| **Dead code** | Dead Code & AI Residue |
| **Blast radius** | Architectural Seams & Blast Radius |
| **Prompt bloat** | Instruction & Prompt Bloat |
| **Diff noise** | Cosmetic Diff Noise |

Lane numbers below are internal section anchors only.

---

### Lane 1: Dead Code & AI Residue (Garbage Collection)
* **Target**: Code added or modified during AI iteration that is uncalled, orphaned, or unneeded.
* **Core Philosophy**: **Inverted Burden of Proof**. Every added symbol is assumed guilty (residue/dead code) until proven innocent.
* **The 4 Evidentiary Proofs**:
  1. **Reachability Proof**: Can runtime execution actually reach this from an active entrypoint (route, UI component, CLI command, export, or event handler)? If not → **Purge**.
  2. **Requirement Proof**: Which explicit user prompt required this? If the answer is *"in case we need it later"* → **Strip YAGNI**.
  3. **Non-Duplication Proof**: Does an existing helper or standard library utility already do this? If so → **Collapse**.
  4. **Breakage Proof**: If deleted right now, does any test or behavior break? If nothing fails and no behavior shifts → **Remove**.
* **Action**: **Subtraction only** (delete dead functions, types, props, imports, and zombie chains).
* **Deep playbook**: [`references/lane-1-dead-code.md`](references/lane-1-dead-code.md) — inverted burden of proof, the 4-tier residue classification, and call-graph/zombie-chain tracing.

---

### Lane 2: Architectural Seams & Blast Radius (Blast Radius Reduction)
* **Target**: **Live, working, necessary** implementation that touches too much surface or introduces unnecessary shared abstraction.
* **Core Philosophy**: **Contract Preservation with Minimal Semantic Exposure**. Keep the required behavioral outcome 100% fixed, but anchor the change to the narrowest, lowest-risk seam.
* **The Seam Hierarchy (prefer in order)**:
  1. Changing an existing leaf-level decision.
  2. Extending a nearby established path.
  3. Adding a small local implementation (local duplication is acceptable if a shared abstraction exposes core systems to regression).
  4. Introducing a shared abstraction *only* when multiple real consumers require it.
* **Action**: **Refactor / Re-anchor** (revert changes in central middleware, schemas, or global providers; place logic in a local leaf module).
* **Deep playbook**: [`references/lane-2-seam-radius.md`](references/lane-2-seam-radius.md) — the must-preserve contract, measuring the surface, and proving behavioral equivalence.

---

### Lane 3: Instruction & Prompt Bloat (Prompt Shake)
* **Target**: System prompts, skill files (`SKILL.md`), rule instructions (`.cursorrules`, `AGENTS.md`), and markdown prompt docs in the diff.
* **Core Philosophy**: **Minimal-that-covers beats maximal**. Every line is guilty until proven load-bearing. Subtraction, not redesign.
* **The 5 Prompt Proofs**:
  1. **Coverage**: If cut, does a real required case fall through? If not → **Cut**.
  2. **Redundancy**: Is this already stated elsewhere in the instruction? If so → **Collapse**.
  3. **Subsumption**: Is this rule a subset of a broader rule present? If so → **Fold in**.
  4. **Default Knowledge**: Would a competent model do this unprompted? If so → **Cut**.
  5. **Load-Bearing**: Does agent output actually degrade without this line? If not → **Cut**.
* **Action**: **Subtraction inside the diff window** (strip filler, redundant edge cases, and over-explanation).
* **Deep playbook**: [`references/lane-3-prompt-shake.md`](references/lane-3-prompt-shake.md) — the targets it hunts, the 5 proofs in full, and the leanness-≠-lossy guardrails.

---

### Lane 4: Cosmetic Diff Noise (Canonical-Equivalence Cleanup)
* **Target**: Standalone, cosmetic-only findings whose representation changed but whose canonical artifact and intended meaning did not.
* **Core Philosophy**: **Context first, proof or keep**. A moved line is not noise merely because it moved. Read the requirement and surrounding code, then prove canonical equivalence with repository-appropriate tools. If proof is unavailable or the change mixes with a semantic edit, keep it out of this lane.
* **The 4 Evidentiary Proofs**:
  1. **Intent Proof**: Is the change unrelated to the required behavior or instruction effect? A declaration moved to fix scope, timing, or ordering is semantic and does not qualify.
  2. **Canonical-Equivalence Proof**: Are the before/after artifacts structurally identical after only safe normalization (for example, the same parsed code structure, Markdown structure plus instruction text, or resolved dependency graph)?
  3. **Significance Proof**: Is the changed whitespace, order, line ending, or metadata inert for this language and repository? Never assume imports, indentation, file modes, comments, snapshots, or generated output are cosmetic.
  4. **Revert-Safety Proof**: Can the cosmetic delta be restored to the base representation while required formatter, generator, build, and test checks remain green?
* **Action**: **Restore representation only** (revert cosmetic hunks or regenerate with the repository's expected tool). Never rewrite semantics or hand-edit generated output under this lane.
* **Deep playbook**: [`references/lane-4-diff-noise.md`](references/lane-4-diff-noise.md) — finding decomposition, canonical proofs by artifact type, mixed-hunk ownership, and fail-closed traps.

---

## Workflow

```text
1. Resolve Scope  ──►  2. Adaptive Diagnosis  ──►  3. Present Evidence  ──►  4. Ask Approval  ──►  5. Tidy & Verify
  (Prompt or Flag)      (Route by lane name)        Unified Table             (ask_question)       (Tests green)
```

---

### Step 1: Resolve Scope

Confirm the diff boundary before auditing. Default to uncommitted changes unless specified:

* **Uncommitted working tree** (staged + unstaged git diff) — *default*
* **Branch vs base** (e.g. `origin/main...HEAD` or `main...HEAD`)
* **Last N commits** (e.g. `HEAD~2..HEAD`)
* **Specific file or path**

If the target is ambiguous, prompt the user with `ask_question`.

---

### Step 2: Adaptive Diagnosis & Lane Routing

Inspect the requested outcome, surrounding context, and diff. Route **reducible findings**, not files blindly:

1. **Decompose the diff**:
   - Use `git diff` hunks as input, then separate independent findings when safe.
   - If cosmetic lines are inseparable from a semantic edit, the semantic lane owns the whole finding.
   - Keep intentional, necessary, well-placed changes without manufacturing a tidy recommendation.
2. **Check standalone cosmetic candidates across all file types**:
   - Compare base and changed artifacts with repository-appropriate parsers, formatters, or normalized representations.
   - Route to **Diff noise** only when all 4 proofs hold. No proof means keep it out of this lane.
3. **For semantic changes in code/config files (`.ts`, `.py`, `.go`, `.rs`, etc.)**:
   - Trace the call graph upwards to find callers. Flag unreferenced symbols and zombie chains under **Dead code**.
   - Check if changes touch shared systems, global state, public contracts, or broad dependencies when a leaf change could suffice. Flag overreach under **Blast radius**.
4. **For semantic changes in prompt/instruction files (`.md`, `.prompt`, `.cursorrules`, etc.)**:
   - Audit changed lines against the 5 prompt proofs under **Prompt bloat**.

---

### Step 3: Present Unified Evidence & Diagnosis Table

Output a clean, scannable table grouped by lane before modifying any code. In the Lane column, use the short labels (**Dead code**, **Blast radius**, **Prompt bloat**, **Diff noise**) — never lane numbers.

```markdown
### 🧹 Tidy Audit Results (Scope: uncommitted diff)

| Lane | Target | Issue / Evidence | Proposed Action | Risk |
|---|---|---|---|---|
| **Dead code** | `src/utils/date.ts:L40` (`formatDateV2`) | **Reachability**: 0 callers across repo. | Delete dead helper | Low |
| **Dead code** | `src/types/user.ts:L15` (`DraftRole`) | **Breakage**: Unreferenced enum variant. | Delete variant | Low |
| **Blast radius** | `src/middleware/auth.ts` | **Blast Radius**: Modified global auth middleware for a single route's needs. | Revert middleware; check role locally in `src/routes/admin.ts`. | Medium |
| **Prompt bloat** | `skills/deploy/SKILL.md:L18` | **Default Knowledge**: Explains how git commit works to the model. | Cut line | Low |
| **Diff noise** | `src/routes/admin.ts:L20-L45` | **Canonical equivalence**: Formatter-only delta; parsed structure is unchanged and format check passes after restore. | Restore base formatting | Low |
```

---

### Step 4: Request Explicit User Approval

**Never alter files or delete code without human sign-off.**

Prompt the user using `ask_question`:
* **Question**: "How would you like to proceed with the tidy recommendations?"
* **Options**:
  1. `(Recommended) Apply all recommendations (dead code, blast radius, prompt bloat, and diff noise)`
  2. `Apply only low-risk cleanup (dead code + prompt bloat + diff noise)`
  3. `Let me select specific items from the table`
  4. `Cancel (Keep working tree unchanged)`

---

### Step 5: Surgical Tidy & Verification

Once approved:
1. **Apply diff noise**: Restore approved cosmetic-only findings to their base representation; use the expected generator/formatter instead of hand-editing generated files.
2. **Apply dead code**: Delete dead functions, types, and unreferenced imports.
3. **Apply blast radius**: Refactor to the narrowest leaf seam while preserving 100% of required behavior.
4. **Apply prompt bloat**: Strip bloat from prompt/instruction docs within the diff window.
5. **Preserve Load-Bearing Context**: Keep load-bearing comments and intent notes intact.
6. **Run Verification**:
   - Run tests (`npm test`, `pytest`, `cargo test`, `go test`).
   - Run type checks / builds (`tsc`, `mypy`, `cargo check`).
   - If tests fail, fix immediately or revert the offending change.
7. **Report Summary** (lead with lane names, not numbers):
   - What changed under **Dead code**, **Blast radius**, **Prompt bloat**, and **Diff noise**
   - Lines removed / added
   - Files cleaned or reverted to clean state
   - Verification status (e.g. `All 36 tests passing green`)

---

## Do / Don't

- **Do** treat dead-code deletion (**Dead code**), architectural narrowing (**Blast radius**), prompt shaking (**Prompt bloat**), and cosmetic restoration (**Diff noise**) as distinct, mutually exclusive disciplines.
- **Don't** rewrite a working architecture when the user only asked to delete dead residue.
- **Do** prove reachability with a concrete call graph before claiming code is dead.
- **Don't** say "this looks unneeded" without citing callers and requirements.
- **Do** preserve 100% of functional requirements when narrowing an architectural seam.
- **Don't** quietly cut behavior or call a weakened implementation "minimized".
- **Do** read why a line moved and prove canonical equivalence before calling it cosmetic.
- **Don't** classify imports, declaration moves, whitespace, generated files, or file modes as noise from appearance alone.
- **Do** fail closed: uncertain cosmetic candidates stay in the diff and out of **Diff noise**.
- **Do** require explicit human approval via `ask_question` before modifying code.
