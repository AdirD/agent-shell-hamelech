# 👑 agent-shell-hamelech

A king's problem was never obedience — it was a court that only ever agreed with him.

![A fictional Moroccan sultan on a palace terrace at sunset, overlooking an ancient medina and the Atlas mountains](assets/moroccan-sultan-cover.jpg)

Which is why every throne kept a wazir: one advisor close enough to speak plainly and trusted enough to be believed. This library makes your agent that wazir instead of another courtier. It questions the decree before carrying it out, prices the campaign before marching, demands evidence before naming a culprit, and burns what the last campaign left behind. It counsels. You rule.

Plain `SKILL.md` files in the [Agent Skills](https://github.com/anthropics/skills) format — drop into Cursor, Claude Code, Codex, or anything that reads `.agents/skills/`.

## Quick start

**On the run?** Click your editor — the prompt is prefilled; review it and press Enter. The agent installs the skills and walks you through what each one is for and when to reach for it on your repo.

[![Open in Cursor](https://img.shields.io/badge/Open_in-Cursor-000000?style=for-the-badge&logo=cursor&logoColor=white)](https://cursor.com/link/prompt?text=Install+this%2C+then+onboard+me+to+agent-shell-hamelech%3A%0Ahttps%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%0A%0AShow+me+around+the+skills+and+how+I+can+leverage+them+on+this+repo.)
[![Open in Claude Code](https://img.shields.io/badge/Open_in-Claude_Code-D97757?style=for-the-badge&logo=anthropic&logoColor=white)](https://claude.ai/code/new?q=Install+this%2C+then+onboard+me+to+agent-shell-hamelech%3A%0Ahttps%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%0A%0AShow+me+around+the+skills+and+how+I+can+leverage+them+on+this+repo.&repo=AdirD%2Fagent-shell-hamelech)
[![Open in Codex](https://img.shields.io/badge/Open_in-Codex-10A37F?style=for-the-badge&logo=openai&logoColor=white)](https://open-in-agent.anaskhaaan-28.workers.dev/open/codex?prompt=Install%20this%2C%20then%20onboard%20me%20to%20agent-shell-hamelech%3A%0Ahttps%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%0A%0AShow%20me%20around%20the%20skills%20and%20how%20I%20can%20leverage%20them%20on%20this%20repo.)
[![Open in Windsurf](https://img.shields.io/badge/Open_in-Windsurf-0084FF?style=for-the-badge&logo=wind&logoColor=white)](https://open-in-agent.anaskhaaan-28.workers.dev/open/windsurf?prompt=Install%20this%2C%20then%20onboard%20me%20to%20agent-shell-hamelech%3A%0Ahttps%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%0A%0AShow%20me%20around%20the%20skills%20and%20how%20I%20can%20leverage%20them%20on%20this%20repo.)
[![Open in Bolt](https://img.shields.io/badge/Open_in-Bolt-000000?style=for-the-badge&logo=stackblitz&logoColor=white)](https://bolt.new/?prompt=Install+this%2C+then+onboard+me+to+agent-shell-hamelech%3A%0Ahttps%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%0A%0AShow+me+around+the+skills+and+how+I+can+leverage+them+on+this+repo.)

Codex and Windsurf badges route through [open-in-agent](https://github.com/anxkhn/open-in-agent) because GitHub strips custom URL schemes from markdown links. Cursor, Claude Code, and Bolt use each product's official HTTPS deeplink.

Or **copy-paste** into any agent chat:

```text
Install this, then onboard me to agent-shell-hamelech:
https://github.com/AdirD/agent-shell-hamelech

Show me around the skills and how I can leverage them on this repo.
```

<details>
<summary>Direct deeplinks (copy; run <code>open "…"</code> on macOS)</summary>

GitHub cannot link custom URL schemes directly. Paste one of these in your terminal or browser address bar:

**Claude Code CLI**

```text
claude-cli://open?repo=AdirD%2Fagent-shell-hamelech&q=Install+this%2C+then+onboard+me+to+agent-shell-hamelech%3A%0Ahttps%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%0A%0AShow+me+around+the+skills+and+how+I+can+leverage+them+on+this+repo.
```

**Codex Desktop** (`originUrl` picks the repo if you have it cloned)

```text
codex://new?prompt=Install+this%2C+then+onboard+me+to+agent-shell-hamelech%3A%0Ahttps%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%0A%0AShow+me+around+the+skills+and+how+I+can+leverage+them+on+this+repo.&originUrl=https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech
```

**Windsurf Cascade**

```text
windsurf://cascade/newChat?prompt=Install+this%2C+then+onboard+me+to+agent-shell-hamelech%3A%0Ahttps%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%0A%0AShow+me+around+the+skills+and+how+I+can+leverage+them+on+this+repo.
```

</details>

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
| [`melech-sync-skills`](#melech-sync-skills) | Are all melech skills installed globally and current? | Say `melech-sync-skills` / `melech sync` to apply, or `melech-sync-skills list` for a dry catalog. |

### Understand what you need

| Skill | Question it answers | Reach for it when |
|---|---|---|
| [`melech-think-with-me`](#melech-think-with-me) | Can a sharp engineer peer expand this half-formed thought with real prior art? | "think with me", "let me think out loud", "just ideating", "what does this remind you of". |
| [`melech-distill-need`](#melech-distill-need) | Is the requested thing actually the right solution? | "distill this", "faster horse", "what do I actually need". |
| [`melech-buy-vs-build`](#melech-buy-vs-build) | Should we adopt an existing tool or build this ourselves? | "build vs buy", "does this already exist", "is there a tool for this", "don't reinvent the wheel", "what's out there for X". |
| [`melech-market-validation`](#melech-market-validation) | What market premise should we test, and does it survive customer and commercial evidence? | Shape or validate a startup, product opportunity, ICP, buyer, demand, willingness to pay, or paid expansion. |

### Shape work before coding

| Skill | Question it answers | Reach for it when |
|---|---|---|
| [`melech-pre-plan`](#melech-pre-plan) | Do we share a precise, buildable concept? | You want alignment before plan mode or code, with calibrated question depth. |
| [`melech-consult`](#melech-consult) | What do independent models conclude once the premises are verified? | The AI proposed an implementation, architecture, or idea and you want to "double check", "proof this", "are you sure", a second opinion, or "am I right or is he right". |
| [`melech-idea-to-canvas`](#melech-idea-to-canvas) | Can the team absorb this idea without rereading the whole input? | You have any idea, note, brief, or doc and want a standalone knowledge-transfer Canvas. |
| [`melech-8020`](#melech-8020) | What is the smallest useful path to the outcome? | "least diff", "minimal change", "80/20", "least intrusive". |
| [`melech-challenge`](#melech-challenge) | What is weak or risky about this direction? | You already have a direction and want holes poked before building. |
| [`melech-visualize`](#melech-visualize) | Can this structure, flow, or trade-off be easier to see? | Prose is hiding architecture, sequence, boundaries, layout, or ambiguity. |

### Implement and ship safely

| Skill | Question it answers | Reach for it when |
|---|---|---|
| [`melech-verify`](#melech-verify) | Does this claim, conclusion, or approach hold up against the source of truth? | Say "verify" mid-thread when you want an independent second opinion that understands the discussion but does not defend its earlier conclusion. |
| [`melech-prune`](#melech-prune) | What dead code, zombie workflows, or YAGNI bloat accumulated during AI coding? | After multi-turn iteration with an AI, when you want to audit uncalled helpers, dead types, and speculative abstractions before opening a PR. |
| [`melech-prompt-shake`](#melech-prompt-shake) | What prompt bloat crept into these prompts, skills, or instructions? | After editing a prompt/skill/instruction file, when you want to strip over-explanation, duplicate/subset rules, and never-fires branches down to the leanest version that still covers 100%. |
| [`melech-debug-mode`](#melech-debug-mode) | What runtime evidence explains this reproducible bug? | A user can exercise a failing workflow but static inspection and existing logs are insufficient. Manual: they reproduce. Autopilot: the agent drives an already-open logged-in Chrome tab. |
| [`melech-live-browser`](#melech-live-browser) | Can the agent continue work in the Chrome tab I already have open? | Fill forms, draft or post comments and replies, update signed-in web apps, or inspect an existing tab without launching a separate browser profile. |
| [`melech-smart-comments`](#melech-smart-comments) | Which intent and landmines must survive in the code? | An agent is writing, editing, refactoring, or reviewing commented code. |
| [`melech-code-review-clone`](#melech-code-review-clone) | Can an agent review PRs like me and keep learning? | Train or resync a private reviewer Clone from your real PR interaction points—inline comments, replies on your own PRs, conversation comments, and review verdicts including silent approvals—correlated to local code and git history. |
| [`melech-babysit`](#melech-babysit) | Can this PR be kept moving until it is merge-ready? | Comments, conflicts, and CI need recurring attention. |

---

## Which skill do I need?

| If you are saying… | Start with | Why |
|---|---|---|
| "What melech skills do I have / should I update?" | [`melech-sync-skills`](#melech-sync-skills) | Global sync of this library into `~/.agents/skills` and every agent. |
| "I'm just thinking out loud—riff with me on this." | [`melech-think-with-me`](#melech-think-with-me) | A single engineer-peer voice that expands each musing with prior art, patterns, and mechanisms, holds it loose, and never converges into a spec. |
| "I have a startup/product idea." | [`melech-market-validation`](#melech-market-validation) | It can shape an open premise into a testable hypothesis before gathering market evidence. |
| "I have a specific startup hypothesis—is the pain real, who buys, and will they pay?" | [`melech-market-validation`](#melech-market-validation) | Runs desk research, customer discovery, and a behavioral/commercial test through a market decision. |
| "Should our existing product add this feature?" | [`melech-distill-need`](#melech-distill-need) | Treat the feature as a proposed solution, uncover the outcome, and compare better means before planning it. |
| "Build a custom RBAC engine." | [`melech-distill-need`](#melech-distill-need) | The named implementation may be a faster horse; first uncover the actual need. |
| "Should we adopt a library/tool/service or build this ourselves?" | [`melech-buy-vs-build`](#melech-buy-vs-build) | Runs the adopt-vs-rebuild check (already-owned deps/vendors), then a parallel verified search of OSS, dev tools, and managed services before the call. |
| "The AI just hand-rolled a queue/retry/scheduler — check that." | [`melech-buy-vs-build`](#melech-buy-vs-build) | Names the capability, then finds the incumbents instead of guessing package names from memory. |
| "What's out there for X? Any new AI tools for it?" | [`melech-buy-vs-build`](#melech-buy-vs-build) | Open-ended landscape discovery with a frontier lane for what shipped recently. |
| "We decided to add RBAC; align it before planning." | [`melech-pre-plan`](#melech-pre-plan) | The work is build-shaped, but the design concept still needs alignment. |
| "Double-check / proof this proposal before building." | [`melech-consult`](#melech-consult) | Verifies the load-bearing premises against the real artifact, then gets independent reads from fresh models on different providers. |
| "Is that actually right? Verify it." | [`melech-verify`](#melech-verify) | Understands what was discussed, checks it against the source of truth, and returns a concise second opinion. |
| "It's still not working / I don't trust this thread anymore." | [`melech-consult`](#melech-consult) | Checks whether the premise itself is false before anyone argues about the fix, and may end right there. |
| "Am I right or is he right?" | [`melech-consult`](#melech-consult) | Records both positions in their own words and returns a psak with what it costs and the one next step. |
| "Turn this idea/doc/notes into a Canvas the team can absorb." | [`melech-idea-to-canvas`](#melech-idea-to-canvas) | Knowledge transfer from any idea, note, or doc into an infographic-first Canvas. |
| "Find the least invasive way to add role checks." | [`melech-8020`](#melech-8020) | The outcome is understood; now minimize the implementation. |
| "I can reproduce this bug, but the existing logs do not explain it." | [`melech-debug-mode`](#melech-debug-mode) | Temporary runtime probes can narrow the real failing path before a fix. |
| "Jump into the Confluence tab I already have open and reply to this comment." | [`melech-live-browser`](#melech-live-browser) | Operates the existing logged-in Chrome tab and applies an explicit draft-versus-submit boundary. |
| "Drive the Chrome tab I'm already logged into while we debug." | [`melech-debug-mode`](#melech-debug-mode) + [`melech-live-browser`](#melech-live-browser) | Debug mode owns evidence and diagnosis; live browser owns safe attach and interaction. |
| "I've been iterating with AI and need to strip dead code and bloat." | [`melech-prune`](#melech-prune) | Evidentiary audit of working diff/branch against 4 proofs before PR. |
| "My prompt/skill/instructions got bloated — tighten them." | [`melech-prompt-shake`](#melech-prompt-shake) | Tree-shaking for prose: audits the diff against 5 prompt proofs and recommends cuts, keeping edits inside the diff window. |
| "Learn how I review PRs and make me a reviewer Clone." | [`melech-code-review-clone`](#melech-code-review-clone) | Builds or resyncs one private user-global Clone with repo-specific memory. |
| "Here is the design—poke holes in it." | [`melech-challenge`](#melech-challenge) | A direction exists and needs pressure-testing. |
| "Research competitors to help choose our product or market direction." | [`melech-market-validation`](#melech-market-validation) | Competitor and substitute evidence should reshape the premise and the test that follows. |
| "Produce a sourced comparison of these competitors." | No dedicated skill yet | Competitor intelligence is the deliverable; extract a skill only if this becomes recurring work. |

## Workflow bundles

Bundles are **journey recipes**, not additional skills. Skip any step whose
question is already answered.

### Product discovery

```text
melech-think-with-me (optional: think out loud before there's even an ask)
  → melech-distill-need (if the ask is a proposed solution)
  → melech-market-validation (shape an open premise, then test it)
  → melech-consult (optional independent check)
  → melech-pre-plan
```

Use when you are unsure what should exist. Start at `melech-think-with-me` when
the idea is still a musing and you want it expanded, not decided. The flow may
stop at `melech-distill-need` or `melech-market-validation` if reuse, reshape,
hold, or stop wins.

### Better engineering

```text
melech-buy-vs-build (adopt vs build?) → melech-distill-need → melech-pre-plan → melech-consult (optional independent check) → melech-8020 → melech-challenge (optional)
```

Use when someone requested a feature or change and you want to avoid building
the wrong thing, aligning it poorly, or overbuilding the solution.

### Existing-plan review

```text
melech-challenge → melech-8020
```

Use when the direction already exists: pressure-test it, then find the smallest
useful implementation.

### Shipping

```text
melech-prune (after AI iteration) → melech-smart-comments (during implementation) → melech-babysit
```

Use when the work is decided and the remaining job is cleaning iteration residue, preserving code intent, and driving the PR to merge-ready. `melech-visualize` can assist any bundle when structure or flow is unclear.

---

### [`melech-sync-skills`](skills/melech-sync-skills)

Syncs this skill library globally across supported coding agents.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-sync-skills -g -y -a '*'
```

Invoke it with:
- `melech-sync-skills` or `melech sync` — install new + refresh existing (global, all agents)
- `melech-sync-skills list` / `melech list` — dry catalog: remote skills plus what is installed globally

Use it when:
- you want every melech skill installed and current in `~/.agents/skills`
- the same set should show up in Cursor, Claude, Codex, Gemini, and the rest
- you want to see what is on remote before applying (`melech-sync-skills list`)
- a newly pushed skill is not showing up and you need to know whether it is a scope problem or just a stale session

---

### [`melech-think-with-me`](skills/melech-think-with-me)

Think out loud with a sharp, well-read engineer peer that expands half-formed ideas with real prior art, patterns, and mechanisms.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-think-with-me
```

Use it when:
- you're thinking out loud and nothing is set in stone yet — you want ideation, not a plan
- you want a single engineer-friend voice that catches a thought and adds one substantive brick (a name, a parallel, a mechanism), then gets out of the way
- you want musings grounded in the landscape ("that's basically the ___ pattern", "that's what ___ does, where they ___") instead of interrogated or converged
- you explicitly do **not** want questions (`melech-challenge`/`melech-pre-plan`), an independent panel and a verdict (`melech-consult`), or a decision procedure (`melech-buy-vs-build`)
- you want it to hand off to a convergent skill only once the thought firms into something buildable

---

### [`melech-8020`](skills/melech-8020)

Finds the smallest useful path to a product or engineering outcome.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-8020
```

Use it when:
- you want the least intrusive or smallest-diff path to a goal
- you say "80/20", "minimal change", or "least diff"
- you want trade-offs explained before implementation, not a ticket-style build

---

### [`melech-babysit`](skills/melech-babysit)

Keeps a PR moving through review, conflicts, and CI until merge-ready.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-babysit
```

Use it when:
- you have an open PR and want it driven to merge without polling every few minutes
- review bots (Bugbot, CodeRabbit, …) and CI keep making a one-shot check go stale
- you want the agent to stop cleanly on real blockers instead of spinning

---

### [`melech-live-browser`](skills/melech-live-browser)

Operates the user's already-open, logged-in Chrome tabs through Chrome DevTools
MCP without turning ordinary browser work into a debugging session.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-live-browser
```

Use it when:
- you want the agent to continue in a Chrome tab you already have open
- you want a form filled, a comment or reply drafted or posted, or a signed-in web page updated
- preserving the current browser profile, tabs, and login matters
- you want explicit language to control whether the agent drafts or commits an action

Requires Chrome 144+, Node/`npx`, and an agent host that can run Chrome DevTools
MCP with `--autoConnect`. The bundled setup helper changes only the one host
config explicitly passed to it; it never scans and rewrites every agent config
on the machine.

---

### [`melech-debug-mode`](skills/melech-debug-mode)

Diagnoses reproducible bugs using temporary runtime probes and captured evidence.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-debug-mode
```

Use it when:
- you can reproduce a UI, API, desktop, or integration bug but current logs are insufficient
- runtime state or control flow must be observed before choosing a fix
- you want hypothesis-driven instrumentation with an explicit user reproduction gate (**manual**)
- you want the agent to reproduce a UI end-to-end in the Chrome tab you already have open (**autopilot**)
- temporary probes and the local collector must be removed cleanly afterward
- you want a live view of running collectors, their health, and streamed logs, with the ability to kill one manually (`doctor`)

Requires Python 3.9+ and the official Vercel Labs `portless` CLI. Manual
reproduction is self-contained. Autopilot additionally requires
`melech-live-browser`, which owns Chrome DevTools MCP setup, attach consent, and
browser interaction:

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-live-browser
```

If the companion is missing during autopilot, debug mode shows this exact
command and asks whether to install it or switch to manual reproduction. For
initial reproduction, revised-probe reruns, and fix verification, live browser
drives one bounded attempt and then returns immediately to debug mode for
collector evidence; autopilot never waits for a `proceed` reply.

Optional: install the bundled `dm` shell command for one-keystroke access from any directory (`dm` opens the doctor TUI, `dm help` lists commands, and `dm start`/`dm status <dir>`/`dm logs <dir>`/`dm stop <dir>` manage collectors):

```bash
sh <skill-dir>/scripts/install-dm.sh
```

The installer guards the line it adds, so an uninstalled or renamed skill never
breaks shell startup. If the skill directory moves, re-run the same command to
repoint it — re-running rewrites the block in place instead of duplicating it.

---

### [`melech-challenge`](skills/melech-challenge)

Pressure-tests an existing direction before implementation.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-challenge
```

Use it when:
- you already have a direction
- you want high-value questions, not a rewrite from zero
- you want assumptions, risks, and over-engineering pressure-tested

---

### [`melech-pre-plan`](skills/melech-pre-plan)

Aligns on a buildable design concept before planning or coding.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-pre-plan
```

Use it when:
- you want alignment before a plan, PRD, or implementation
- plan mode keeps inventing the wrong thing too early
- you need grilling without a 40-question tax on every bugfix
- you want scale/status architecture stripped before it hardens

---

### [`melech-consult`](skills/melech-consult)

Verifies an AI-proposed plan, fix, architecture, or claim against the real artifact, then dispatches a panel of fresh models from different providers that answer independently — no assigned sides.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-consult
```

Use it when:
- the AI proposed a plan, architecture, or fix and you say "double check", "proof this", or "are you sure"
- you have stopped trusting the thread and want a fact or a verdict, not more deliberation
- you want the load-bearing premises checked against code, data, or logs before anyone argues about the fix
- you want independent reads from different providers, with calibrated confidence and the real dispatch disclosed
- you and someone else disagree and you want both positions recorded before a psak
- you want a clear answer with one next step, and a genuine tradeoff laid out only when there actually is one

The design rationale and the research it is built on are documented in
[`skills/melech-consult/README.md`](skills/melech-consult/README.md).

---

### [`melech-idea-to-canvas`](skills/melech-idea-to-canvas)

Turns rough ideas or docs into a standalone Cursor Canvas for team understanding.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-idea-to-canvas
```

Use it when:
- you have any idea, note, brief, design doc, or RFC and want the team to absorb it fast
- you want a knowledge-transfer Canvas, not a debate space or sign-off flow
- the input is rough and needs structuring before it can be shared
- prose is hiding the mental model, ownership, flows, or decisions
- you want infographics rather than a document with pictures — crowded text is treated as a missing visual, not a formatting problem

---

### [`melech-distill-need`](skills/melech-distill-need)

Uncovers the real need behind a requested solution before building it.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-distill-need
```

Use it when:
- the request may be a faster-horse style proposed solution
- you want the agent to find the real need before implementing
- existing tools/process might already solve it
- "don't just build what I asked" is the point

---

### [`melech-market-validation`](skills/melech-market-validation)

Tests whether a product or market opportunity has real demand and willingness to pay.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-market-validation
```

Use it when:
- you have a vague startup, product, or market opportunity and need to discover what hypothesis is worth testing
- you have a specific startup, market, ICP, customer/problem, buyer, or offer hypothesis
- you need to establish whether the pain is real, budget exists, and customers will act or pay
- you want secondary research followed by primary discovery and the smallest decisive market test
- you already ran interviews, a smoke test, or a pilot and need rigorous synthesis against precommitted thresholds
- you want a decision-ready validation dossier that keeps counter-evidence and remaining risk visible

For a concrete feature or implementation request, use `melech-distill-need` first. For implementation planning after the direction is chosen, use `melech-pre-plan`.

---

### [`melech-code-review-clone`](skills/melech-code-review-clone)

Builds or resyncs a private reviewer that learns your GitHub code-review style.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-code-review-clone
```

Use it when:
- you want an agent to review PRs with your attention, judgment threshold, and writing voice
- you want it to mimic your themes and biases, not correct them or impose "best practices"
- you want it to just use the repo you run it from, with no repo-picker step
- you want it to learn across IF/WHAT/WHERE/WHEN/WHO/WHY plus your voice, then act from reflexes, an attention map, and negative space
- you want learning grounded by correlating your real comments, author-side replies, and review verdicts (including silent approvals) to the actual local code and git history, not deep-read PR narratives
- you want a compact `Calibrate Clone` question set where every question names a real package/file/area
- you want a clean split between the trainer that learns and the generated Clone that acts
- you want fresh bounded subagents only for genuinely heavy read-only lookups (ownership is scanned inline)
- you want approvals, change requests, and comments performed through the GitHub CLI
- you want the human—not the trainer—to choose whether to publish, continue, or pause
- a week of new human and Clone review activity is ready to resync
- you want direct edits, rejected comments, missed concerns, and replies to teach the Clone what to learn or unlearn
- you need personalized review memory to stay private and out of project git

---

### [`melech-buy-vs-build`](skills/melech-buy-vs-build)

Decides whether to adopt an existing tool or build a capability yourself, grounded in verified research.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-buy-vs-build
```

Use it when:
- an agent just hand-rolled a queue, retry policy, scheduler, state machine, parser, or auth layer and you suspect a known tool already does it
- you want the build-vs-buy call answered with verified sources instead of a model's stale memory
- you want the inward adopt-vs-rebuild check first — is the capability already covered by an installed dependency or a vendor you already pay for
- you are exploring a space open-endedly — "what's out there for X", "what are people using now", "any new AI tools for this"
- you want to seed the search with specific tools or sources and have them evaluated on the same contract
- you want the honest counter-case for when writing it yourself is genuinely the smaller total cost

---

### [`melech-smart-comments`](skills/melech-smart-comments)

Preserves code intent with selective comments and protects meaningful existing comments.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-smart-comments
```

Use it when:
- you want agents to leave landmines, WHYs, and workarounds behind — not narrate WHAT the code does
- you've been burned by an agent "cleaning up" a comment that was the only trace of a past incident
- you want one consistent comment policy across Cursor, Claude Code, Codex, and anything else reading `.agents/skills/`

---

### [`melech-verify`](skills/melech-verify)

Gives the caller a genuine second opinion on a claim, conclusion, or approach already discussed.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-verify
```

Use it when:
- you say "verify" or ask for a second opinion on something already discussed
- you want the discussion used as context, not as evidence for its own conclusion

For multiple independent opinions or a judgment among competing paths, use `melech-consult`.

---

### [`melech-prune`](skills/melech-prune)

Audits and removes dead code, AI residue, and unnecessary complexity after iteration.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-prune
```

Use it when:
- you've been iterating with an AI for multiple turns and lost track of what is actually used
- you suspect orphaned helper functions, dead types, and abandoned workflows are polluting the diff
- you want speculative generality (YAGNI) and ad-hoc duplicate helpers collapsed before opening a PR
- you want an evidentiary audit where you approve the deletions with full visibility

---

### [`melech-prompt-shake`](skills/melech-prompt-shake)

Tree-shaking for prompts — strips bloat from prompts, skills, and instruction docs down to the leanest version that still covers 100% of needed cases.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-prompt-shake
```

Use it when:
- you just edited a prompt, skill file, or instruction doc and want the bloat shaken out
- prompts written by an AI are over-explained, duplicated, or full of never-fires edge cases
- you want minimal-that-covers-100% over maximal — leaner prompt, same coverage
- you want a diff-driven audit that reads the whole file but keeps recommendations inside the diff window
- you want a scannable findings table with a named proof per cut, not a silent rewrite

---

### [`melech-visualize`](skills/melech-visualize)

Turns an idea, flow, or structure into a compact ASCII diagram.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-visualize
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
  melech-think-with-me/
  melech-8020/
  melech-babysit/
  melech-challenge/
  melech-consult/
  melech-idea-to-canvas/
  melech-distill-need/
  melech-debug-mode/
  melech-live-browser/
  melech-sync-skills/
  melech-market-validation/
  melech-pre-plan/
  melech-prune/
  melech-prompt-shake/
  melech-verify/
  melech-code-review-clone/
  melech-buy-vs-build/
  melech-smart-comments/
  melech-visualize/
```

Every skill has its own `SKILL.md` with frontmatter plus optional `scripts/` and
`references/`. Skills can explicitly compose: debug mode remains independent
for manual reproduction and uses `melech-live-browser` only for autopilot.

## Contributing

Add a new skill by creating `skills/<name>/SKILL.md` with proper frontmatter (`name`, `description`). Then update the catalog above — the `AGENTS.md` maintenance rule enforces this.

Before pushing, run `bash scripts/pre-push-audit.sh` (see `AGENTS.md` for commit/push safety rules and optional git hook setup).

After pushing, sync installations across all global agent dirs by running the `melech-sync-skills` skill (or `melech sync`).


## License

[MIT](./LICENSE)
