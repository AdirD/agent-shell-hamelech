# 👑 agent-shell-hamelech

A small, opinionated library of **agent skills** — drop-in behaviors you can install into Cursor, Claude Code, Codex, and any other agent that speaks the [Agent Skills](https://github.com/anthropics/skills) format.

Everything in this repo is a skill. No commands, no rules, no bespoke installer. One repo, one format, one install command.

![A fictional Moroccan sultan in a palace courtyard at sunset](assets/moroccan-sultan-cover.png)

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
| [`melech`](#melech) | What melech skills exist remote vs local, and should I update? | Say `melech list` / `melech list skills`, or ask about catalog sync / updates. |

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
| [`design-to-canvas`](#design-to-canvas) | Can the team absorb this design without rereading the whole doc? | You have a design doc / RFC and want a standalone knowledge-transfer Canvas. |
| [`8020`](#8020) | What is the smallest useful path to the outcome? | "least diff", "minimal change", "80/20", "least intrusive". |
| [`challenge`](#challenge) | What is weak or risky about this direction? | You already have a direction and want holes poked before building. |
| [`visualize`](#visualize) | Can this structure, flow, or trade-off be easier to see? | Prose is hiding architecture, sequence, boundaries, layout, or ambiguity. |

### Implement and ship safely

| Skill | Question it answers | Reach for it when |
|---|---|---|
| [`debug-mode`](#debug-mode) | What runtime evidence explains this reproducible bug? | A user can exercise a failing workflow but static inspection and existing logs are insufficient, including driving an already-open logged-in Chrome tab. |
| [`smart-comments`](#smart-comments) | Which intent and landmines must survive in the code? | An agent is writing, editing, refactoring, or reviewing commented code. |
| [`reviewer-clone`](#reviewer-clone) | Can an agent review PRs like me and keep learning? | Train or resync a private reviewer Clone through parent-led PR exploration, parallel repository/voice analysis, and calibration. |
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
| "What melech skills do I have / should I update?" | [`melech`](#melech) | Dry remote↔local sync status for this library. |
| "I have a startup/product idea." | [`product-ideation`](#product-ideation) | The product premise is still open. |
| "Is this pain real / will buyers pay?" | [`problem-discovery`](#problem-discovery) | Demand and pain need evidence before solutioning. |
| "Should our existing product add this feature?" | [`product-ideation`](#product-ideation) | Feature ideation is product ideation inside a current product. |
| "Build a custom RBAC engine." | [`distill-need`](#distill-need) | The named implementation may be a faster horse; first uncover the actual need. |
| "We decided to add RBAC; align it before planning." | [`pre-plan`](#pre-plan) | The work is build-shaped, but the design concept still needs alignment. |
| "Turn this design doc into a Canvas the team can absorb." | [`design-to-canvas`](#design-to-canvas) | Knowledge transfer from a design doc into a scannable Canvas. |
| "Find the least invasive way to add role checks." | [`8020`](#8020) | The outcome is understood; now minimize the implementation. |
| "I can reproduce this bug, but the existing logs do not explain it." | [`debug-mode`](#debug-mode) | Temporary runtime probes can narrow the real failing path before a fix. |
| "Drive the Chrome tab I'm already logged into while we debug." | [`debug-mode`](#debug-mode) | Optional `agent-browser --auto-connect` attach; one-time `chrome://inspect/#remote-debugging` toggle. |
| "Learn how I review PRs and make me a reviewer Clone." | [`reviewer-clone`](#reviewer-clone) | Builds or resyncs one private user-global Clone with repo-specific memory. |
| "Here is the design—poke holes in it." | [`challenge`](#challenge) | A direction exists and needs pressure-testing. |
| "Research competitors to help choose our direction." | [`product-ideation`](#product-ideation) | Competitor research is serving a product decision. |
| "Produce a sourced comparison of these competitors." | No dedicated skill yet | Competitor intelligence is the deliverable; extract a skill only if this becomes recurring work. |

## Workflow bundles

Bundles are **journey recipes**, not additional skills. Skip any step whose
question is already answered.

### Product discovery

```text
distill-need → problem-discovery (if demand/pain unclear) → product-ideation → pre-plan
```

Use when you are unsure what should exist. The flow may stop at
`distill-need` or `problem-discovery` if reuse, refine, hold, or stop wins.

### Better engineering

```text
distill-need → pre-plan → 8020 → challenge (optional)
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
smart-comments (during implementation) → babysit
```

Use when the work is decided and the remaining job is preserving code intent
and driving the PR to merge-ready. `visualize` can assist any bundle when
structure or flow is unclear.

---

### `melech`

Remote-first catalog for this library. For every skill on GitHub it shows name, description, installed y/n, where (global/project/workspace → which agents), local/remote version (folder SHA), update available y/n, and the exact install/update command. Also lists the [workflow bundles](#workflow-bundles) (journey recipes) with which steps you already have. Leverages [`vercel-labs/skills`](https://github.com/vercel-labs/skills); dry-run only (`npx skills check` aliases `update` and applies changes).

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech
```

Invoke it with:
- `melech list` or `melech list skills` (easiest to remember)
- `melech`, `melech status`, or "should I update my melech skills?"
- `melech sync-local` or `python3 scripts/sync-local-skills.py` (local zero-deviation sync)

Use it when:
- you want remote → local comparison per skill (including brand-new remote skills)
- you ask "should I update?" before running `npx skills update`
- you pushed skill changes and want all usages across sibling repos & global agent dirs synced
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

Runs an evidence-first debugging loop for bugs that require a real user workflow. It starts a lean, isolated JSONL collector through Portless on a newly assigned backend port, guides the agent to add minimal temporary POST probes, then either attaches to the user's already-open Chrome via Vercel Labs `agent-browser --auto-connect` (same tabs and logins; Chrome 144+ one-time toggle at `chrome://inspect/#remote-debugging`, then Allow) or waits for the user to reproduce and reply `proceed`. It inspects evidence, iterates or fixes, removes every probe, detaches without quitting Chrome, and tears down only that session. A bundled developer-journey example defines the intended first-use and repeat-use experience. A built-in `doctor` TUI (`debug_session.py doctor`) shows every live session with per-session health (running/degraded/dead from process state plus the collector `/health` endpoint), a real-time event tail, surfaced collector errors, and a hotkey to kill a session. `dm browser-check` lists open tabs or prints the inspect-page / Allow setup hints.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill debug-mode
```

Use it when:
- you can reproduce a UI, API, desktop, or integration bug but current logs are insufficient
- runtime state or control flow must be observed before choosing a fix
- you want hypothesis-driven instrumentation with an explicit user reproduction gate
- temporary probes and the local collector must be removed cleanly afterward
- you want a live view of running collectors, their health, and streamed logs, with the ability to kill one manually (`doctor`)
- you want the agent to drive a UI you already have open and logged into, without a second browser or extension

Requires Python 3.9+ and the official Vercel Labs `portless` CLI. Live-Chrome attach additionally needs the official Vercel Labs `agent-browser` CLI (`npm i -g agent-browser && agent-browser install`); the collector still works without it.

Optional: install the bundled `dm` shell command for one-keystroke access from any directory (`dm` opens the doctor TUI, `dm help` lists commands, `dm start`/`dm stop <dir>`/`dm browser-check` forward to the launcher):

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

### `design-to-canvas`

Turns a design doc into a standalone Cursor Canvas for team knowledge transfer — not an approval workflow or a prettier copy of the document. Surfaces mental model, system shape, decisions, constraints, and rollout with strong hierarchy and progressive disclosure.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill design-to-canvas
```

Use it when:
- you have a design doc / RFC / tech design and want the team to absorb it fast
- you want a knowledge-transfer Canvas, not a debate space or sign-off flow
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

Creates and resyncs a private user-global `cr-clone-<name>` reviewer from the authenticated user's real GitHub behavior. The main agent directly runs a cheap recent-activity query and asks which repository to use before inspecting code or history. After selection it invokes the bundled activity collector while a fresh subagent maps the repository; voice analysis starts when comments are available. The main agent alone chooses and deeply reads PRs, talks with the human, decides learning, and publishes. Built-in todos replace routine narration. Evidence-backed confidence checkpoints redirect exploration, while stricter corroboration controls behavior-changing calibration. Durable run records retain exact coverage, decisions, and source IDs; compact active files retain voice and repository judgment. The human always chooses whether to publish, continue, deep-dive, or pause. Later corrections to traced `🤖 Clone` comments teach it what to learn or unlearn.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill reviewer-clone
```

Use it when:
- you want an agent to review PRs with your attention, judgment threshold, and writing voice
- you want to initialize another repository inside the same personal Clone
- you want activity collection and repository mapping to begin together while the main agent iteratively reasons through selected PRs with you
- you want the parent to own repository choice, collectors, deep reads, questions, learning, and publication
- you want fresh bounded subagents only for repository mapping, voice, and narrow factual searches
- you want regular evidence-backed confidence checkpoints plus stricter behavior-changing calibration
- you want code areas ranked by relative review importance without treating missing evidence as low importance
- you want the human—not the trainer—to choose whether to publish, continue broadly, or deep dive
- you want each run's evidence, decisions, and learning delta retained without separate log systems
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
  design-to-canvas/
  distill-need/
  debug-mode/
  hebrew-rtl-writing/
  melech/
  podcast-production/
  pre-plan/
  problem-discovery/
  product-ideation/
  reviewer-clone/
  smart-comments/
  visualize/
```

Every skill is self-contained: a `SKILL.md` with frontmatter, optional `scripts/`, and optional `references/`.

## Contributing

Add a new skill by creating `skills/<name>/SKILL.md` with proper frontmatter (`name`, `description`). Then update the catalog above — the `AGENTS.md` maintenance rule enforces this.

Before pushing, run `bash scripts/pre-push-audit.sh` (see `AGENTS.md` for commit/push safety rules and optional git hook setup).

After pushing, sync local installations across sibling repos and global agent dirs:
```bash
python3 scripts/sync-local-skills.py --apply
```

## License

[MIT](./LICENSE)
