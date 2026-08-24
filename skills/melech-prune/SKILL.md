---
name: melech-prune
description: Audit and remove dead code, AI residue, and unnecessary complexity after iteration.
disable-model-invocation: true
---

# Prune

After 5–15 prompts of iterative coding with AI, codebases accrete **AI residue**: orphaned helpers from earlier prompts, dead types, half-migrated state, speculative config keys, and zombie workflows.

The feature works and tests might pass, but the working diff is cluttered with dead pathways and unreferenced scaffolding.

**`melech-prune` acts as an evidentiary garbage collector and architectural reconciler.**

---

## The Core Philosophy: Inverted Burden of Proof

In normal coding, developers assume: *"The AI wrote this, so it's probably needed."*

**`melech-prune` flips this assumption entirely:**
> **Every added or modified function, type, parameter, state hook, wrapper, and export is assumed GUILTY (dead code, accidental residue, or YAGNI bloat) until proven innocent with concrete evidence.**

If a symbol cannot provide proof of reachability and concrete necessity, it is queued for deletion.

---

## The 4 Evidentiary Proofs

To survive pruning, every symbol in the audited diff must satisfy these four tests:

| Proof Type | Question Asked | Evidentiary Requirement | If Proof Fails |
|---|---|---|---|
| **1. Reachability Proof** | "Can runtime execution actually reach this?" | Trace a direct call chain from an active entrypoint (route, UI component, CLI command, export, or event handler). | **Dead / Zombie Code** → Purge. |
| **2. Requirement Proof** | "Which explicit user requirement demanded this?" | Identify the exact user story or bugfix requiring this branch or parameter. If the answer is *"in case we need it later"*, it fails. | **YAGNI Bloat** → Strip. |
| **3. Non-Duplication Proof** | "Did this logic already exist in the codebase?" | Verify whether an existing helper, utility, or standard library method already handles this. | **Accidental Reinvention** → Collapse. |
| **4. Breakage Proof** | "If we delete this right now, what test or behavior breaks?" | Simulate removal or check test coverage. If nothing fails and no behavior shifts, why does it exist? | **Phantom Scaffolding** → Remove. |

If a symbol looks like a hand-rolled version of a known library or tool rather than of local code, that is an adoption question and not a deletion — note it and flag it for the user.

---

## Workflow

```text
1. Ask Scope  ──►  2. Build Call Graph  ──►  3. Present Evidence  ──►  4. Ask Approval  ──►  5. Prune & Verify
  (ask_question)     & Run 4 Proofs             Table to User             (ask_question)       (Tests green)
```

---

### Step 1: Prompt for Scope

Never assume the diff target. Immediately prompt the user using `ask_question` to choose the audit boundary:

* **Question**: "What scope would you like to prune?"
* **Options**:
  1. `(Recommended) Uncommitted working tree (staged + unstaged git diff)`
  2. `Current branch vs base (git diff origin/main...HEAD or main...HEAD)`
  3. `Last N commits (e.g. HEAD~3..HEAD)`
  4. `Specific files or directory (custom path)`

If the user passed a specific target in their initial prompt (e.g. `melech-prune HEAD~2..HEAD` or `melech-prune src/auth/`), confirm that target directly.

---

### Step 2: Audit the Diff with Evidentiary Proofs

Examine every added or modified file in the chosen scope:

1. **Extract all new / modified symbols**:
   * Functions, methods, and classes
   * Types, interfaces, DTOs, and enums
   * Imports and exported variables
   * State variables, props, hooks, and event handlers
   * Parameters, flags, and configuration keys
2. **Trace the Call Graph**:
   * Trace upwards from leaf helpers to find their callers.
   * **Catch Zombie Chains**: A helper is NOT alive just because `WorkflowA` calls it, if `WorkflowA` itself has zero callers from the application entrypoints.
3. **Classify Findings into Tiers**:
   * 🟢 **Tier 1: Undisputed Dead Residue (Zero-risk)**
     * Zero-reference local functions, unused imports, orphaned types, unreachable `if/else` branches, dead test fixtures.
   * 🟡 **Tier 2: Zombie Workflows & Abandoned Iterations (Medium-risk)**
     * Handlers or multi-step logic created in turn 2, abandoned in turn 6 when approach changed, but left wired to phantom state.
   * 🟠 **Tier 3: Speculative / YAGNI Bloat (Design-level)**
     * Unused options, defensive wrappers with only one trivial caller, over-generalized helper parameters.
   * 🔵 **Tier 4: Accidental Duplications**
     * Custom helpers written during iteration that reinvent existing codebase utilities.

---

### Step 3: Present Findings & Notification

Before touching any code, output a clear, structured **Evidence & Pruning Table**:

```markdown
### 🔍 Prune Audit Results (Scope: uncommitted diff)

| Tier | File | Symbol / Block | Failed Proof & Evidence | Proposed Action |
|---|---|---|---|---|
| 🟢 Tier 1 | `src/utils/format.ts:L42-L58` | `formatLegacyDate()` | **Reachability**: 0 call sites across repo. | Delete function |
| 🟢 Tier 1 | `src/types/user.ts:L12` | `LegacyUserRole` | **Reachability**: Unreferenced type. | Delete enum variant |
| 🟡 Tier 2 | `src/hooks/useCart.ts:L85-L102` | `syncToLocalStorage()` | **Breakage**: Added in turn 3, superseded by IndexedDB in turn 7. Only called by unused draft handler. | Delete handler & state |
| 🟠 Tier 3 | `src/services/api.ts:L30` | `options.retryDelay` | **Requirement**: YAGNI; hardcoded to default everywhere, no callers supply custom delay. | Inline & simplify |
```

---

### Step 4: Request Explicit User Approval

**Never prune without human sign-off.**

Use `ask_question` to request the user's verdict:

* **Question**: "How would you like to proceed with the pruning recommendations?"
* **Options**:
  1. `(Recommended) Prune all verified items (Tiers 1, 2, 3, and 4)`
  2. `Prune only Tier 1 (Zero-risk dead code & unreferenced symbols)`
  3. `Let me specify which items to keep or prune`
  4. `Cancel (Keep working tree unchanged)`

If the user picks **Option 3**, ask which specific items from the table they want to preserve before proceeding.

---

### Step 5: Surgical Pruning & Verification

Once approved:

1. **Delete Dead Code**: Remove the approved functions, types, branches, and parameters.
2. **Clean Up Dangling References**: Remove unused imports and unneeded variables left behind by deletions.
3. **Respect Comments**: Preserve load-bearing landmine/WHY comments, and remove comments only if the code they explain was deleted.
4. **Run Verification**:
   * Run the test suite (`npm test`, `pytest`, `cargo test`, `go test`, etc.).
   * Run type checking (`tsc`, `mypy`, `cargo check`, etc.) or build commands.
   * If any test fails, inspect whether a test was testing a deleted dead path (update test) or if an unintended dependency was touched (revert & fix).
5. **Summarize Outcome**:
   * Lines of code removed
   * Files cleaned
   * Final verification/test status (e.g. `All 42 tests passing green`)

---

## Do / Don't

**Do:** Prompt for the audit scope with `ask_question` before running the analysis.  
**Don't:** Guess the git diff target without confirming.

**Do:** Provide concrete proof (e.g. *"0 references in repo"*, *"only caller is dead function X"*) for every item flagged.  
**Don't:** Say *"this looks unnecessary"* without showing the call graph evidence.

**Do:** Require explicit user approval via `ask_question` before deleting files or code blocks.  
**Don't:** Silently delete code behind the scenes.

**Do:** Run tests and type checks immediately after pruning to prove the build remains green.  
**Don't:** Leave broken imports or failing test suites after a cleanup.
