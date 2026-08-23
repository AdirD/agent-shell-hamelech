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
| [`reviewer-clone`](#reviewer-clone) | Can an agent review PRs like me and keep learning? | Train or resync a private reviewer Clone by correlating your real review comments to the local code and git history in the repo you run it from. |
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
| "Learn how I review PRs and make me a reviewer Clone." | [`reviewer-clone`](#reviewer-clone) | Builds or resyncs one private user-global Clone with repo-specific memory. |
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

Keeps this library current on the machine: every skill on GitHub is present under `~/.agents/skills` and reachable from every coding agent. Ships no scripts — it teaches the agent to drive the Skills CLI correctly, which is one command: `cd ~ && npx skills add AdirD/agent-shell-hamelech --all -g`. Naming the repo is what keeps the sync melech-only, so unrelated global skills are never upgraded behind your back. Also documents the two outputs that look like failures and are not (Eve and PromptScript cannot do global installs; Cursor and Codex read `~/.agents/skills` directly instead of getting a symlink). Renamed from `melech`; remove the old global skill with `npx skills remove melech -g -y`.

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

Helps decide on the smallest useful way to reach a product goal before writing code. Explores technical, UX, product, and strategy trade-offs, favors existing integration points over new code, and surfaces 80/20 alternatives.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill 8020
```

Use it when:
- you want the least intrusive or smallest-diff path to a goal
- you say "80/20", "minimal change", or "least diff"
- you want trade-offs explained before implementation, not a ticket-style build

---

### [`babysit`](skills/babysit)

Keeps a PR merge-ready by looping over comments, merge conflicts, and CI on a recurring cadence (default 5 min) until the PR is green and mergeable — or a real blocker needs you. Delegates the loop to a `/loop` primitive if available, otherwise arms a background heartbeat.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill babysit
```

Use it when:
- you have an open PR and want it driven to merge without polling every few minutes
- review bots (Bugbot, CodeRabbit, …) and CI keep making a one-shot check go stale
- you want the agent to stop cleanly on real blockers instead of spinning

---

### [`debug-mode`](skills/debug-mode)

Runs an evidence-first debugging loop for bugs that require a real user workflow. It starts a lean, isolated JSONL collector through Portless on a newly assigned backend port and adds minimal temporary POST probes. Reproduction is one of two modes: **manual** (you hold the wheel, then reply `proceed`) or **autopilot** (the agent drives your already-open Chrome via Chrome DevTools MCP `--autoConnect` — same tabs and logins; Chrome 144+ one-time toggle at `chrome://inspect/#remote-debugging`, then Allow). If the host has no `chrome-devtools` MCP, `dm mcp-setup` writes the official `--autoConnect` config and asks for a reload so the host can start the server. If you do not pick, the agent names both modes and waits. It inspects evidence, iterates or fixes, removes every probe, detaches without quitting Chrome, and tears down only that session. A bundled developer-journey example defines the intended first-use and repeat-use experience. A built-in `doctor` TUI (`debug_session.py doctor`) shows every live session with per-session health (running/degraded/dead from process state plus the collector `/health` endpoint), a real-time event tail, surfaced collector errors, and a hotkey to kill a session. `dm browser-check` is a CLI fallback only.

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

Pressure-tests an existing direction before implementation. Asks one high-value question at a time, revises assumptions as you answer, and flags over-engineering risk. Does not restart from zero; does not turn into a PRD.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill challenge
```

Use it when:
- you already have a direction
- you want high-value questions, not a rewrite from zero
- you want assumptions, risks, and over-engineering pressure-tested

---

### [`pre-plan`](skills/pre-plan)

Reaches a shared buildable design concept before plan mode or code. Auto-calibrates question density (`light` / `standard` / `deep`), keeps domain nouns aligned, kills premature scale/architecture, and optionally pressure-tests the concept. Stops at a short decision log unless you explicitly lock a plan.

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

Double-checks, proofs, and stress-tests an AI-proposed implementation, architecture, plan, or product idea before committing. Isolates the proposal, briefs fresh subagents or an expert council without grading its own homework, and synthesizes consensus vs. flaws into concrete adjustments. Every consultant runs a different model from a different provider — never the main thread's model, never two on the same one — so agreement means corroboration, not an echo.

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

Turns any starting point — a rough idea, meeting notes, product brief, RFC, design doc, or bullet list — into a standalone Cursor Canvas for team knowledge transfer. Not an approval workflow or a prettier copy of the input. Shapes the idea if unstructured, then surfaces mental model, system shape, decisions, constraints, and rollout with strong hierarchy and progressive disclosure.

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

Treats the literal ask as a proposed solution, not scripture. Distills the outcome that must be true, checks context and existing alternatives, and surfaces better solution categories — including reuse or don't-build. Hands off to `pre-plan` / `8020` only when the work is still build-shaped.

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

Shapes an open product or business opportunity into a testable market hypothesis, then runs validation end to end. It can clarify the aim, relationship to a current product, customer, problem, product shape, and value mechanism without forcing an early verdict. Once the premise is testable, it locks the customer, costly situation, buyer, current alternative, proposed value, market boundary, and decision thresholds; mines first-party evidence; audits public evidence for and against the claims; closes mechanism gaps with customer discovery; and closes demand gaps with a behavioral or commercial test. It preserves one living validation brief across human gates and finishes full validation with an evidence-backed **Advance / Reshape / Hold / Stop** dossier. Desk research is labeled plausible or research-supported—not “validated.”

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

### [`reviewer-clone`](skills/reviewer-clone)

Creates and resyncs a private user-global `cr-clone-<name>` reviewer from the authenticated user's real GitHub behavior. Every reviewer has their own themes and biases—this mimics them, it doesn't correct them. It trains on the repository you run it from—no menu—and learns a compact model across six lenses: **IF** they weigh in at all, **WHAT** they flag, **WHERE** they focus and own, **WHEN** they escalate (ask / suggest / block), **WHO** they push on, and **WHY** they care—plus **HOW** they say it (their voice). Instead of deep-reading whole PRs (which overfits), it **correlates over the whole comment corpus**: the bundled collector sweeps every review comment with its file+line anchor and splits them into ordered chunk-files, and the main agent reads the chunks one by one—building a running model and grounding real patterns against the actual local code and read-only git (`log`, `blame`, `shortlog`)—until new chunks stop teaching it anything. The lenses are how the *trainer* learns; what it publishes is the *Clone's* brain, filed the way a review actually happens: an attention map (where to look), reflexes (trigger → reaction → how hard → why), negative space (what to wave through), and default posture. Once a real pattern exists, a compact `Calibrate Clone` question set—each question naming a real package/file/area—settles the few choices that would change behavior. Built-in todos replace narration. Reviews stay draft-first; approvals, change requests, and comments post through the authenticated `gh` CLI. The human always chooses whether to publish, continue, or pause. Its comments read in the person's own voice (no bot prefix) and carry only a hidden HTML trace, so later human corrections to them teach it what to learn or unlearn.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill reviewer-clone
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

Finds the prior art before you pay to rebuild it: whether the capability already ships as a library, OSS project, dev tool, managed service, cloud primitive, or a dependency already installed and already billed. Its first move is translating the implementation into the capability's canonical name (a `tasks` table plus a polling worker is a **job queue**), because searching the local vocabulary is why this research usually fails. It then fans out parallel research lanes — canon, ecosystem, commercial, already-in-your-stack, practitioner verdicts, counter-case, and a frontier lane for what shipped in the last 6–12 months — each subagent running several live web searches down its own path. Always searches; memory only generates hypotheses, and no candidate reaches the shortlist without a URL seen in this run and a liveness signal, so it cannot invent a plausible package that does not exist. Dead and unverified entries are killed, rebrands and forks deduplicated, options clustered by approach, and the result is a 3–6 row shortlist with cost, what you give up, what no option covers, and an honest case for when rolling your own still wins. Reports and recommends via `ask_question` — it never rips out working code on its own.

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

Makes the agent write selective, intent-preserving inline comments and respect existing ones as load-bearing memory. Kills "what" comments, preserves "why" comments, and refuses to silently delete comments during refactors.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill smart-comments
```

Use it when:
- you want agents to leave landmines, WHYs, and workarounds behind — not narrate WHAT the code does
- you've been burned by an agent "cleaning up" a comment that was the only trace of a past incident
- you want one consistent comment policy across Cursor, Claude Code, Codex, and anything else reading `.agents/skills/`

---

### [`prune`](skills/prune)

Audits and strips AI residue, dead code, zombie workflows, and YAGNI bloat after heavy multi-turn iteration. Operates on an **inverted burden of proof**: every added or modified symbol is assumed unneeded until proven necessary with concrete evidence (reachability, explicit requirement, non-duplication, and breakage tests). Prompts for diff scope via `ask_question`, presents a clear evidence table, and requires explicit user approval before safely pruning and verifying the test suite.

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

Renders the current idea as a compact ASCII diagram — architecture, flows, screens, sequences, boundaries, comparisons, or current mental models. Marks assumptions, separates confirmed from inferred, and calls out anything the drawing exposes.

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
  reviewer-clone/
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
