# Lane 1 — Dead Code & AI Residue (deep playbook)

> The full handcrafted playbook behind Tidy's **Lane 1** (originally the
> standalone `melech-prune` skill). Tidy's [`SKILL.md`](../SKILL.md) owns the
> shared workflow — scope resolution, the unified evidence table, approval via
> `ask_question`, and verification. This file holds the lane-specific
> philosophy, proofs, and tier classification. Pull it in when Lane 1 fires and
> you need the depth behind the compact proof list in the router.

After 5–15 prompts of iterative coding with AI, codebases accrete **AI residue**: orphaned helpers from earlier prompts, dead types, half-migrated state, speculative config keys, and zombie workflows.

The feature works and tests might pass, but the working diff is cluttered with dead pathways and unreferenced scaffolding.

**Lane 1 acts as an evidentiary garbage collector and architectural reconciler.**

---

## The Core Philosophy: Inverted Burden of Proof

In normal coding, developers assume: *"The AI wrote this, so it's probably needed."*

**Lane 1 flips this assumption entirely:**
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

## Auditing depth

*(Scope, approval, and verification are handled by the Tidy workflow. This is the lane-specific "how" for the diagnosis step.)*

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

Example findings table (feeds the unified Tidy evidence table):

```markdown
| Tier | File | Symbol / Block | Failed Proof & Evidence | Proposed Action |
|---|---|---|---|---|
| 🟢 Tier 1 | `src/utils/format.ts:L42-L58` | `formatLegacyDate()` | **Reachability**: 0 call sites across repo. | Delete function |
| 🟢 Tier 1 | `src/types/user.ts:L12` | `LegacyUserRole` | **Reachability**: Unreferenced type. | Delete enum variant |
| 🟡 Tier 2 | `src/hooks/useCart.ts:L85-L102` | `syncToLocalStorage()` | **Breakage**: Added in turn 3, superseded by IndexedDB in turn 7. Only called by unused draft handler. | Delete handler & state |
| 🟠 Tier 3 | `src/services/api.ts:L30` | `options.retryDelay` | **Requirement**: YAGNI; hardcoded to default everywhere, no callers supply custom delay. | Inline & simplify |
```

When applying: delete approved dead code, clean up dangling references (unused imports/variables left behind), and **preserve load-bearing landmine/WHY comments** — remove a comment only if the code it explained was deleted.

---

## Do / Don't

**Do:** Provide concrete proof (e.g. *"0 references in repo"*, *"only caller is dead function X"*) for every item flagged.
**Don't:** Say *"this looks unnecessary"* without showing the call graph evidence.

**Do:** Require explicit user approval before deleting files or code blocks.
**Don't:** Silently delete code behind the scenes.

**Do:** Run tests and type checks immediately after pruning to prove the build remains green.
**Don't:** Leave broken imports or failing test suites after a cleanup.
