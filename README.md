# 👑 agent-shell-hamelech

A small, opinionated library of **agent skills** — drop-in behaviors you can install into Cursor, Claude Code, Codex, and any other agent that speaks the [Agent Skills](https://github.com/anthropics/skills) format.

Everything in this repo is a skill. No commands, no rules, no bespoke installer. One repo, one format, one install command.

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
| [`problem-discovery`](#problem-discovery) | Is this problem real, painful, and worth solving now? | Pain validation, demand/WTP checks, customer discovery, JTBD research. |
| [`product-ideation`](#product-ideation) | What product, feature, or direction is worth pursuing? | A product/company idea, feature opportunity, market question, or premise is still open. |

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

### Specialized production

| Skill | What it does | Reach for it when |
|---|---|---|
| [`podcast-production`](#podcast-production) | Turns long recordings into an approved short story and finished video. | Interview/meeting/webinar → storyline, script, clips, or rendered cut. |
| [`hebrew-rtl-writing`](#hebrew-rtl-writing) | Fixes mixed RTL/LTR rendering in Hebrew text with embedded English. | English terms make primarily Hebrew prose render incorrectly. |

---

## Which skill do I need?

| If you are saying… | Start with | Why |
|---|---|---|
| "What melech skills do I have / should I update?" | [`sync-melech-skills`](#sync-melech-skills) | Global sync of this library into `~/.agents/skills` and every agent. |
| "I have a startup/product idea." | [`product-ideation`](#product-ideation) | The product premise is still open. |
| "Is this pain real / will buyers pay?" | [`problem-discovery`](#problem-discovery) | Demand and pain need evidence before solutioning. |
| "Should our existing product add this feature?" | [`product-ideation`](#product-ideation) | Feature ideation is product ideation inside a current product. |
| "Build a custom RBAC engine." | [`distill-need`](#distill-need) | The named implementation may be a faster horse; first uncover the actual need. |
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
| "Research competitors to help choose our direction." | [`product-ideation`](#product-ideation) | Competitor research is serving a product decision. |
| "Produce a sourced comparison of these competitors." | No dedicated skill yet | Competitor intelligence is the deliverable; extract a skill only if this becomes recurring work. |

## Workflow bundles

Bundles are **journey recipes**, not additional skills. Skip any step whose
question is already answered.

### Product discovery

```text
distill-need → problem-discovery (if demand/pain unclear) → product-ideation → consult (optional idea council) → pre-plan
```

Use when you are unsure what should exist. The flow may stop at
`distill-need` or `problem-discovery` if reuse, refine, hold, or stop wins.

### Better engineering

```text
distill-need → pre-plan → consult (optional sanity check/council) → 8020 → challenge (optional)
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

### `sync-melech-skills`

Keeps this library current on the machine: every skill on GitHub is present under `~/.agents/skills` and linked into every coding agent. `sync-melech-skills` / `melech sync` applies missing installs and updates with non-interactive `npx skills` (`-g -y -a '*'`). Never writes a project/repo lock. `sync-melech-skills list` is the dry remote↔local catalog (folder SHAs, not semver). `sync-local` is the authoring-repo copy after you push this checkout. Renamed from `melech`; remove the old global skill with `npx skills remove melech -g -y`.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill sync-melech-skills -g -y -a '*'
```

Invoke it with:
- `sync-melech-skills` or `melech sync` — install missing + update stale (global, all agents)
- `sync-melech-skills list` / `melech list` — dry catalog
- `sync-melech-skills sync-local` — after pushing this repo, copy into sibling local installs

Use it when:
- you want every melech skill installed and current in `~/.agents/skills`
- the same set should show up in Cursor, Claude, Codex, Gemini, and the rest
- you want a dry remote → local comparison before applying (`sync-melech-skills list`)
- a skill's lock still points at the typo slug `AdirD/agent-shel-hamelech`

---

### `8020`

Helps decide on the smallest useful way to reach a product goal before writing code. Explores technical, UX, product, and strategy trade-offs, favors existing integration points over new code, and surfaces 80/20 alternatives.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill 8020
```

Use it when:
- you want the least intrusive or smallest-diff path to a goal
- you say "80/20", "minimal change", or "least diff"
- you want trade-offs explained before implementation, not a ticket-style build

---

### `babysit`

Keeps a PR merge-ready by looping over comments, merge conflicts, and CI on a recurring cadence (default 5 min) until the PR is green and mergeable — or a real blocker needs you. Delegates the loop to a `/loop` primitive if available, otherwise arms a background heartbeat.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill babysit
```

Use it when:
- you have an open PR and want it driven to merge without polling every few minutes
- review bots (Bugbot, CodeRabbit, …) and CI keep making a one-shot check go stale
- you want the agent to stop cleanly on real blockers instead of spinning

---

### `debug-mode`

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

### `challenge`

Pressure-tests an existing direction before implementation. Asks one high-value question at a time, revises assumptions as you answer, and flags over-engineering risk. Does not restart from zero; does not turn into a PRD.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill challenge
```

Use it when:
- you already have a direction
- you want high-value questions, not a rewrite from zero
- you want assumptions, risks, and over-engineering pressure-tested

---

### `pre-plan`

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

### `consult`

Double-checks, proofs, and stress-tests an AI-proposed implementation, architecture, plan, or product idea before committing. Isolates the proposal, briefs fresh subagents or an expert council without grading its own homework, and synthesizes consensus vs. flaws into concrete adjustments.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill consult
```

Use it when:
- the AI proposed a plan, architecture, or fix and you say "double check", "proof this", or "are you sure"
- you want an unbiased second opinion from a fresh subagent or heavier reasoning model without thread bias
- you want an expert council to triangulate a multi-variable trade-off (e.g., simplicity vs. scale vs. security)
- you want a devil's advocate / red team to stress-test a proposal for hidden landmines before writing code

---

### `idea-to-canvas`

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

### `distill-need`

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

### `hebrew-rtl-writing`

Fixes mixed RTL/LTR rendering for any textual artifact that is primarily Hebrew but includes embedded English terms. Wraps English spans with Unicode bidi isolates without touching code blocks, links, or frontmatter.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill hebrew-rtl-writing
```

Use it when:
- the text is primarily Hebrew
- English words or technical terms make raw Markdown hard to read
- you want bidi isolation applied without touching code blocks or links

---

### `problem-discovery`

Locks one falsifiable hypothesis ("users of type A doing B struggle when they hit C"), then researches real sources (Reddit, forums, G2, GitHub, job posts) for and against it and delivers a blunt, styled decision page — split verdict, sourced numbers, named rivals, one decisive next test. Proposes the hypothesis instead of interrogating you; researches by default instead of waiting to be told.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill problem-discovery
```

Use it when:
- you need to know if the problem is real and painful enough before solutioning
- you want demand / willingness-to-pay confidence, not feature brainstorming
- you want the agent to go research the pain, not interview you about it
- you want a decision-ready validation page, not a hedged report

---

### `product-ideation`

An adaptive, circular thinking partner for new ideas and existing products. It clarifies the idea's relationship to any current product, explores only the uncertainty that matters now, researches or parallelizes proportionately, reframes as evidence changes, and keeps one evolving brief or produces a specialized artifact only when useful.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill product-ideation
```

Use it when:
- you want to ideate or think through an idea before it's a spec
- you're exploring a feature, workflow, roadmap, or growth direction for a current product and repository
- you're investigating a market, mapping existing solutions, or sharpening positioning
- you're deciding what to build or preparing a pitch
- you want research, lightweight working notes, or a decision artifact without being forced through a validation pipeline

---

### `podcast-production`

Turns long interviews, meetings, webinars, panels, or recorded conversations into a short, user-approved podcast story and finished video. Two independently invokable intents: collaborative storyline development from raw media/transcripts, and source-faithful FFmpeg production from an approved script.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill podcast-production
```

Use it when:
- you have raw media or a transcript and want themes, editorial angles, a script, or the strongest clips
- you want to iterate on an interview narrative before locking a cut
- you already have an approved script and need to cut, render, assemble, or verify video
- you want end-to-end help from a long recording to a finished short

---

### `reviewer-clone`

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

### `smart-comments`

Makes the agent write selective, intent-preserving inline comments and respect existing ones as load-bearing memory. Kills "what" comments, preserves "why" comments, and refuses to silently delete comments during refactors.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill smart-comments
```

Use it when:
- you want agents to leave landmines, WHYs, and workarounds behind — not narrate WHAT the code does
- you've been burned by an agent "cleaning up" a comment that was the only trace of a past incident
- you want one consistent comment policy across Cursor, Claude Code, Codex, and anything else reading `.agents/skills/`

---

### `prune`

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

### `visualize`

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
  hebrew-rtl-writing/
  sync-melech-skills/
  podcast-production/
  pre-plan/
  problem-discovery/
  product-ideation/
  prune/
  reviewer-clone/
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
