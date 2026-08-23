# 👑 agent-shell-hamelech

A king's problem was never obedience — it was a court that only ever agreed with him.

Which is why every throne kept a wazir: one advisor close enough to speak plainly and trusted enough to be believed. This library makes your agent that wazir instead of another courtier. It questions the decree before carrying it out, prices the campaign before marching, demands evidence before naming a culprit, and burns what the last campaign left behind. It counsels. You rule.

Plain `SKILL.md` files in the [Agent Skills](https://github.com/anthropics/skills) format — drop into Cursor, Claude Code, Codex, or anything that reads `.agents/skills/`.

![A fictional Moroccan sultan on a palace terrace at sunset, overlooking an ancient medina and the Atlas mountains](assets/moroccan-sultan-cover.jpg)

---

## Install

Install any skill with a single command (needs [`skills`](https://www.npmjs.com/package/skills)):

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill <name>
```

Manual fallback (any agent that reads `.agents/skills/`):

```bash
mkdir -p .agents/skills
cp -R skills/<name> .agents/skills/<name>
```

---

## Choose a skill

Start from the outcome you need. Skills are individual capabilities; the
[workflow bundles](#workflow-bundles) below show how to combine them.

### Manage the library

| Skill | Question it answers | Reach for it when |
|---|---|---|
| [`sync-melech-skills`](#sync-melech-skills) | Are all melech skills installed globally and current? | Say `sync-melech-skills` / `melech sync` to apply, or `sync-melech-skills list` for a dry catalog. |

### Understand what you need

| Skill | Question it answers | Reach for it when |
|---|---|---|
| [`distill-need`](#distill-need) | Is the requested thing actually the right solution? | "distill this", "faster horse", "what do I actually need". |
| [`scout`](#scout) | Has someone already built this? | "does this already exist", "is there a tool for this", "don't reinvent the wheel", "what's out there for X". |
| [`market-validation`](#market-validation) | What market premise should we test, and does it survive customer and commercial evidence? | Shape or validate a startup, product opportunity, ICP, buyer, demand, willingness to pay, or paid expansion. |

### Shape work before coding

| Skill | Question it answers | Reach for it when |
|---|---|---|
| [`pre-plan`](#pre-plan) | Do we share a precise, buildable concept? | You want alignment before plan mode or code, with calibrated question depth. |
| [`consult`](#consult) | Did the AI miss a landmine, edge case, or simpler path? | The AI proposed an implementation, architecture, or idea and you say "double check", "proof this", or "are you sure". |
| [`idea-to-canvas`](#idea-to-canvas) | Can the team absorb this idea without rereading the whole input? | You have any idea, note, brief, or doc and want a standalone knowledge-transfer Canvas. |
| [`8020`](#8020) | What is the smallest useful path to the outcome? | "least diff", "minimal change", "80/20", "least intrusive". |
| [`challenge`](#challenge) | What is weak or risky about this direction? | You already have a direction and want holes poked before building. |
| [`visualize`](#visualize) | Can this structure, flow, or trade-off be easier to see? | Prose is hiding architecture, sequence, boundaries, layout, or ambiguity. |

### Implement and ship safely

| Skill | Question it answers | Reach for it when |
|---|---|---|
| [`prune`](#prune) | What dead code, zombie workflows, or YAGNI bloat accumulated during AI coding? | After multi-turn iteration with an AI, when you want to audit uncalled helpers, dead types, and speculative abstractions before opening a PR. |
| [`debug-mode`](#debug-mode) | What runtime evidence explains this reproducible bug? | A user can exercise a failing workflow but static inspection and existing logs are insufficient. Manual: they reproduce. Autopilot: the agent drives an already-open logged-in Chrome tab. |
| [`smart-comments`](#smart-comments) | Which intent and landmines must survive in the code? | An agent is writing, editing, refactoring, or reviewing commented code. |
| [`code-review-clone`](#code-review-clone) | Can an agent review PRs like me and keep learning? | Train or resync a private reviewer Clone by correlating your real review comments to the local code and git history in the repo you run it from. |
| [`babysit`](#babysit) | Can this PR be kept moving until it is merge-ready? | Comments, conflicts, and CI need recurring attention. |

---

## Which skill do I need?

| If you are saying… | Start with | Why |
|---|---|---|
| "What melech skills do I have / should I update?" | [`sync-melech-skills`](#sync-melech-skills) | Global sync of this library into `~/.agents/skills` and every agent. |
| "I have a startup/product idea." | [`market-validation`](#market-validation) | It can shape an open premise into a testable hypothesis before gathering market evidence. |
| "I have a specific startup hypothesis—is the pain real, who buys, and will they pay?" | [`market-validation`](#market-validation) | Runs desk research, customer discovery, and a behavioral/commercial test through a market decision. |
| "Should our existing product add this feature?" | [`distill-need`](#distill-need) | Treat the feature as a proposed solution, uncover the outcome, and compare better means before planning it. |
| "Build a custom RBAC engine." | [`distill-need`](#distill-need) | The named implementation may be a faster horse; first uncover the actual need. |
| "Is there already a library/tool/service that does this?" | [`scout`](#scout) | Parallel verified search of libraries, OSS, dev tools, managed services, and deps already installed. |
| "The AI just hand-rolled a queue/retry/scheduler — check that." | [`scout`](#scout) | Names the capability, then finds the incumbents instead of guessing package names from memory. |
| "What's out there for X? Any new AI tools for it?" | [`scout`](#scout) | Open-ended landscape discovery with a frontier lane for what shipped recently. |
| "We decided to add RBAC; align it before planning." | [`pre-plan`](#pre-plan) | The work is build-shaped, but the design concept still needs alignment. |
| "Double-check / proof this proposal before building." | [`consult`](#consult) | Isolates the AI's proposal and briefs fresh subagents/councils to stress-test it without grading its own homework. |
| "Are you sure? Consult another model on this architecture or idea." | [`consult`](#consult) | Unbiased second opinion or expert council to expose blindspots and failure modes. |
| "Turn this idea/doc/notes into a Canvas the team can absorb." | [`idea-to-canvas`](#idea-to-canvas) | Knowledge transfer from any idea, note, or doc into a scannable Canvas. |
| "Find the least invasive way to add role checks." | [`8020`](#8020) | The outcome is understood; now minimize the implementation. |
| "I can reproduce this bug, but the existing logs do not explain it." | [`debug-mode`](#debug-mode) | Temporary runtime probes can narrow the real failing path before a fix. |
| "Drive the Chrome tab I'm already logged into while we debug." | [`debug-mode`](#debug-mode) | Autopilot: Chrome DevTools MCP `--autoConnect`; one-time `chrome://inspect/#remote-debugging` toggle, then Allow. |
| "I've been iterating with AI and need to strip dead code and bloat." | [`prune`](#prune) | Evidentiary audit of working diff/branch against 4 proofs before PR. |
| "Learn how I review PRs and make me a reviewer Clone." | [`code-review-clone`](#code-review-clone) | Builds or resyncs one private user-global Clone with repo-specific memory. |
| "Here is the design—poke holes in it." | [`challenge`](#challenge) | A direction exists and needs pressure-testing. |
| "Research competitors to help choose our product or market direction." | [`market-validation`](#market-validation) | Competitor and substitute evidence should reshape the premise and the test that follows. |
| "Produce a sourced comparison of these competitors." | No dedicated skill yet | Competitor intelligence is the deliverable; extract a skill only if this becomes recurring work. |

## Workflow bundles

Bundles are **journey recipes**, not additional skills. Skip any step whose
question is already answered.

### Product discovery

```text
distill-need (if the ask is a proposed solution)
  → market-validation (shape an open premise, then test it)
  → consult (optional idea council)
  → pre-plan
```

Use when you are unsure what should exist. The flow may stop at
`distill-need` or `market-validation` if reuse, reshape, hold, or stop wins.

### Better engineering

```text
scout (if it might already exist) → distill-need → pre-plan → consult (optional sanity check/council) → 8020 → challenge (optional)
```

Use when someone requested a feature or change and you want to avoid building
the wrong thing, aligning it poorly, or overbuilding the solution.

### Existing-plan review

```text
challenge → 8020
```

Use when the direction already exists: pressure-test it, then find the smallest
useful implementation.

### Shipping

```text
prune (after AI iteration) → smart-comments (during implementation) → babysit
```

Use when the work is decided and the remaining job is cleaning iteration residue, preserving code intent, and driving the PR to merge-ready. `visualize` can assist any bundle when structure or flow is unclear.

---

### [`sync-melech-skills`](skills/sync-melech-skills)

Syncs this skill library globally across supported coding agents.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill sync-melech-skills -g -y -a '*'
```

Invoke it with:
- `sync-melech-skills` or `melech sync` — install new + refresh existing (global, all agents)
- `sync-melech-skills list` / `melech list` — dry catalog: remote skills plus what is installed globally

Use it when:
- you want every melech skill installed and current in `~/.agents/skills`
- the same set should show up in Cursor, Claude, Codex, Gemini, and the rest
- you want to see what is on remote before applying (`sync-melech-skills list`)
- a newly pushed skill is not showing up and you need to know whether it is a scope problem or just a stale session

---

### [`8020`](skills/8020)

Finds the smallest useful path to a product or engineering outcome.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill 8020
```

Use it when:
- you want the least intrusive or smallest-diff path to a goal
- you say "80/20", "minimal change", or "least diff"
- you want trade-offs explained before implementation, not a ticket-style build

---

### [`babysit`](skills/babysit)

Keeps a PR moving through review, conflicts, and CI until merge-ready.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill babysit
```

Use it when:
- you have an open PR and want it driven to merge without polling every few minutes
- review bots (Bugbot, CodeRabbit, …) and CI keep making a one-shot check go stale
- you want the agent to stop cleanly on real blockers instead of spinning

---

### [`debug-mode`](skills/debug-mode)

Diagnoses reproducible bugs using temporary runtime probes and captured evidence.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill debug-mode
```

Use it when:
- you can reproduce a UI, API, desktop, or integration bug but current logs are insufficient
- runtime state or control flow must be observed before choosing a fix
- you want hypothesis-driven instrumentation with an explicit user reproduction gate (**manual**)
- you want the agent to reproduce a UI end-to-end in the Chrome tab you already have open (**autopilot**)
- temporary probes and the local collector must be removed cleanly afterward
- you want a live view of running collectors, their health, and streamed logs, with the ability to kill one manually (`doctor`)

Requires Python 3.9+ and the official Vercel Labs `portless` CLI. Live-Chrome attach additionally needs Chrome 144+, Node/`npx`, and a host that can run MCP. The skill writes the official `chrome-devtools-mcp --autoConnect` config when it is missing (see [the Chrome blog](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)); the collector still works without it.

Optional: install the bundled `dm` shell command for one-keystroke access from any directory (`dm` opens the doctor TUI, `dm help` lists commands, `dm start`/`dm stop <dir>`/`dm mcp-setup`/`dm browser-check` forward to the launcher):

```bash
sh <skill-dir>/scripts/install-dm.sh
```

---

### [`challenge`](skills/challenge)

Pressure-tests an existing direction before implementation.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill challenge
```

Use it when:
- you already have a direction
- you want high-value questions, not a rewrite from zero
- you want assumptions, risks, and over-engineering pressure-tested

---

### [`pre-plan`](skills/pre-plan)

Aligns on a buildable design concept before planning or coding.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill pre-plan
```

Use it when:
- you want alignment before a plan, PRD, or implementation
- plan mode keeps inventing the wrong thing too early
- you need grilling without a 40-question tax on every bugfix
- you want scale/status architecture stripped before it hardens

---

### [`consult`](skills/consult)

Gets independent model opinions on an AI-proposed plan, fix, architecture, or idea.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill consult
```

Use it when:
- the AI proposed a plan, architecture, or fix and you say "double check", "proof this", or "are you sure"
- you want an unbiased second opinion from a fresh subagent on a different model/provider than the thread that wrote the proposal
- you want an expert council to triangulate a multi-variable trade-off (e.g., simplicity vs. scale vs. security)
- you want a devil's advocate / red team to stress-test a proposal for hidden landmines before writing code

---

### [`idea-to-canvas`](skills/idea-to-canvas)

Turns rough ideas or docs into a standalone Cursor Canvas for team understanding.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill idea-to-canvas
```

Use it when:
- you have any idea, note, brief, design doc, or RFC and want the team to absorb it fast
- you want a knowledge-transfer Canvas, not a debate space or sign-off flow
- the input is rough and needs structuring before it can be shared
- prose is hiding the mental model, ownership, flows, or decisions

---

### [`distill-need`](skills/distill-need)

Uncovers the real need behind a requested solution before building it.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill distill-need
```

Use it when:
- the request may be a faster-horse style proposed solution
- you want the agent to find the real need before implementing
- existing tools/process might already solve it
- "don't just build what I asked" is the point

---

### [`market-validation`](skills/market-validation)

Tests whether a product or market opportunity has real demand and willingness to pay.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill market-validation
```

Use it when:
- you have a vague startup, product, or market opportunity and need to discover what hypothesis is worth testing
- you have a specific startup, market, ICP, customer/problem, buyer, or offer hypothesis
- you need to establish whether the pain is real, budget exists, and customers will act or pay
- you want secondary research followed by primary discovery and the smallest decisive market test
- you already ran interviews, a smoke test, or a pilot and need rigorous synthesis against precommitted thresholds
- you want a decision-ready validation dossier that keeps counter-evidence and remaining risk visible

For a concrete feature or implementation request, use `distill-need` first. For implementation planning after the direction is chosen, use `pre-plan`.

---

### [`code-review-clone`](skills/code-review-clone)

Builds or resyncs a private reviewer that learns your GitHub code-review style.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill code-review-clone
```

Use it when:
- you want an agent to review PRs with your attention, judgment threshold, and writing voice
- you want it to mimic your themes and biases, not correct them or impose "best practices"
- you want it to just use the repo you run it from, with no repo-picker step
- you want it to learn across IF/WHAT/WHERE/WHEN/WHO/WHY plus your voice, then act from reflexes, an attention map, and negative space
- you want learning grounded by correlating your real comments to the actual local code and git history, not deep-read PR narratives
- you want a compact `Calibrate Clone` question set where every question names a real package/file/area
- you want a clean split between the trainer that learns and the generated Clone that acts
- you want fresh bounded subagents only for genuinely heavy read-only lookups (ownership is scanned inline)
- you want approvals, change requests, and comments performed through the GitHub CLI
- you want the human—not the trainer—to choose whether to publish, continue, or pause
- a week of new human and Clone review activity is ready to resync
- you want direct edits, rejected comments, missed concerns, and replies to teach the Clone what to learn or unlearn
- you need personalized review memory to stay private and out of project git

---

### [`scout`](skills/scout)

Finds and compares existing tools before building a capability from scratch.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill scout
```

Use it when:
- an agent just hand-rolled a queue, retry policy, scheduler, state machine, parser, or auth layer and you suspect a known tool already does it
- you want build-vs-buy answered with verified sources instead of a model's stale memory
- you want to know whether the capability is already covered by an installed dependency or a vendor you already pay for
- you are exploring a space open-endedly — "what's out there for X", "what are people using now", "any new AI tools for this"
- you want to seed the search with specific tools or sources and have them evaluated on the same contract
- you want the honest counter-case for when writing it yourself is genuinely the smaller total cost

---

### [`smart-comments`](skills/smart-comments)

Preserves code intent with selective comments and protects meaningful existing comments.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill smart-comments
```

Use it when:
- you want agents to leave landmines, WHYs, and workarounds behind — not narrate WHAT the code does
- you've been burned by an agent "cleaning up" a comment that was the only trace of a past incident
- you want one consistent comment policy across Cursor, Claude Code, Codex, and anything else reading `.agents/skills/`

---

### [`prune`](skills/prune)

Audits and removes dead code, AI residue, and unnecessary complexity after iteration.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill prune
```

Use it when:
- you've been iterating with an AI for multiple turns and lost track of what is actually used
- you suspect orphaned helper functions, dead types, and abandoned workflows are polluting the diff
- you want speculative generality (YAGNI) and ad-hoc duplicate helpers collapsed before opening a PR
- you want an evidentiary audit where you approve the deletions with full visibility

---

### [`visualize`](skills/visualize)

Turns an idea, flow, or structure into a compact ASCII diagram.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill visualize
```

Use it for:
- architecture
- flows
- comparisons
- boundaries
- current mental models

---

## Repo Layout

```text
skills/
  8020/
  babysit/
  challenge/
  consult/
  idea-to-canvas/
  distill-need/
  debug-mode/
  sync-melech-skills/
  market-validation/
  pre-plan/
  prune/
  code-review-clone/
  scout/
  smart-comments/
  visualize/
```

Every skill is self-contained: a `SKILL.md` with frontmatter, optional `scripts/`, and optional `references/`.

## Contributing

Add a new skill by creating `skills/<name>/SKILL.md` with proper frontmatter (`name`, `description`). Then update the catalog above — the `AGENTS.md` maintenance rule enforces this.

Before pushing, run `bash scripts/pre-push-audit.sh` (see `AGENTS.md` for commit/push safety rules and optional git hook setup).

After pushing, sync installations across all global agent dirs by running the `sync-melech-skills` skill (or `melech sync`).


## License

[MIT](./LICENSE)
