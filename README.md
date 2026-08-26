# 👑 agent-shell-hamelech

A king's problem was never obedience — it was a court that only ever agreed with him.

Which is why every throne kept a wazir: one advisor close enough to speak plainly and trusted enough to be believed. This library makes your agent that wazir instead of another courtier. It questions the decree before carrying it out, prices the campaign before marching, demands evidence before naming a culprit, and burns what the last campaign left behind. It counsels. You rule.

Plain `SKILL.md` files in the [Agent Skills](https://github.com/anthropics/skills) format — drop into Cursor, Claude Code, Codex, or anything that reads `.agents/skills/`.

## Quick start

**On the run?** Click your editor — the prompt is prefilled; review it and press Enter. The agent reads every skill, installs them globally, and gives you a first-day wizard tour: when to reach for each skill, how the workflow bundles connect, and what to try first for *your* task.

[![Open in Cursor](https://img.shields.io/badge/Open_in-Cursor-000000?style=for-the-badge&logo=cursor&logoColor=white)](https://cursor.com/link/prompt?text=You+are+onboarding+me+to+the+agent-shell-hamelech+skill+library+%28https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%29.%0A%0ADo+this+in+order%3A%0A1.+Read+the+repo+README+and+every+skill+under+skills%2F%2A%2FSKILL.md.%0A2.+Run+melech-sync-skills+%28or%3A+npx+skills+add+https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech+--skill+melech-sync-skills+-g+-y+-a+%22%2A%22+then+invoke+melech+sync%29+to+install+all+skills+globally.%0A3.+Give+me+a+first-day+tour+%E2%80%94+like+a+product+wizard+%E2%80%94+not+a+wall+of+docs%3A%0A+++-+One+sentence+on+what+this+library+is+for+%28agent+as+wazir%2C+not+courtier%29.%0A+++-+The+4+workflow+bundles+%28product+discovery%2C+better+engineering%2C+existing-plan+review%2C+shipping%29+as+journeys+with+when+to+start+each.%0A+++-+For+each+skill%3A+name%2C+one-line+purpose%2C+and+a+concrete+trigger+phrase+%28%22say+X+when...%22%29.%0A+++-+A+%22if+you+only+remember+5+things%22+cheat+sheet+for+day-to-day+use.%0A+++-+Ask+what+I+am+working+on+right+now+and+recommend+the+first+skill+%2B+bundle+to+try.%0A%0AKeep+it+scannable.+Use+tables+or+short+bullets.+No+lore+dumps.)
[![Open in Claude Code](https://img.shields.io/badge/Open_in-Claude_Code-D97757?style=for-the-badge&logo=anthropic&logoColor=white)](https://claude.ai/code/new?q=You+are+onboarding+me+to+the+agent-shell-hamelech+skill+library+%28https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%29.%0A%0ADo+this+in+order%3A%0A1.+Read+the+repo+README+and+every+skill+under+skills%2F%2A%2FSKILL.md.%0A2.+Run+melech-sync-skills+%28or%3A+npx+skills+add+https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech+--skill+melech-sync-skills+-g+-y+-a+%22%2A%22+then+invoke+melech+sync%29+to+install+all+skills+globally.%0A3.+Give+me+a+first-day+tour+%E2%80%94+like+a+product+wizard+%E2%80%94+not+a+wall+of+docs%3A%0A+++-+One+sentence+on+what+this+library+is+for+%28agent+as+wazir%2C+not+courtier%29.%0A+++-+The+4+workflow+bundles+%28product+discovery%2C+better+engineering%2C+existing-plan+review%2C+shipping%29+as+journeys+with+when+to+start+each.%0A+++-+For+each+skill%3A+name%2C+one-line+purpose%2C+and+a+concrete+trigger+phrase+%28%22say+X+when...%22%29.%0A+++-+A+%22if+you+only+remember+5+things%22+cheat+sheet+for+day-to-day+use.%0A+++-+Ask+what+I+am+working+on+right+now+and+recommend+the+first+skill+%2B+bundle+to+try.%0A%0AKeep+it+scannable.+Use+tables+or+short+bullets.+No+lore+dumps.&repo=AdirD%2Fagent-shell-hamelech)
[![Open in Codex](https://img.shields.io/badge/Open_in-Codex-10A37F?style=for-the-badge&logo=openai&logoColor=white)](https://open-in-agent.anaskhaaan-28.workers.dev/open/codex?prompt=You%20are%20onboarding%20me%20to%20the%20agent-shell-hamelech%20skill%20library%20%28https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%29.%0A%0ADo%20this%20in%20order%3A%0A1.%20Read%20the%20repo%20README%20and%20every%20skill%20under%20skills%2F%2A%2FSKILL.md.%0A2.%20Run%20melech-sync-skills%20%28or%3A%20npx%20skills%20add%20https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%20--skill%20melech-sync-skills%20-g%20-y%20-a%20%22%2A%22%20then%20invoke%20melech%20sync%29%20to%20install%20all%20skills%20globally.%0A3.%20Give%20me%20a%20first-day%20tour%20%E2%80%94%20like%20a%20product%20wizard%20%E2%80%94%20not%20a%20wall%20of%20docs%3A%0A%20%20%20-%20One%20sentence%20on%20what%20this%20library%20is%20for%20%28agent%20as%20wazir%2C%20not%20courtier%29.%0A%20%20%20-%20The%204%20workflow%20bundles%20%28product%20discovery%2C%20better%20engineering%2C%20existing-plan%20review%2C%20shipping%29%20as%20journeys%20with%20when%20to%20start%20each.%0A%20%20%20-%20For%20each%20skill%3A%20name%2C%20one-line%20purpose%2C%20and%20a%20concrete%20trigger%20phrase%20%28%22say%20X%20when...%22%29.%0A%20%20%20-%20A%20%22if%20you%20only%20remember%205%20things%22%20cheat%20sheet%20for%20day-to-day%20use.%0A%20%20%20-%20Ask%20what%20I%20am%20working%20on%20right%20now%20and%20recommend%20the%20first%20skill%20%2B%20bundle%20to%20try.%0A%0AKeep%20it%20scannable.%20Use%20tables%20or%20short%20bullets.%20No%20lore%20dumps.)
[![Open in Windsurf](https://img.shields.io/badge/Open_in-Windsurf-0084FF?style=for-the-badge&logo=wind&logoColor=white)](https://open-in-agent.anaskhaaan-28.workers.dev/open/windsurf?prompt=You%20are%20onboarding%20me%20to%20the%20agent-shell-hamelech%20skill%20library%20%28https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%29.%0A%0ADo%20this%20in%20order%3A%0A1.%20Read%20the%20repo%20README%20and%20every%20skill%20under%20skills%2F%2A%2FSKILL.md.%0A2.%20Run%20melech-sync-skills%20%28or%3A%20npx%20skills%20add%20https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%20--skill%20melech-sync-skills%20-g%20-y%20-a%20%22%2A%22%20then%20invoke%20melech%20sync%29%20to%20install%20all%20skills%20globally.%0A3.%20Give%20me%20a%20first-day%20tour%20%E2%80%94%20like%20a%20product%20wizard%20%E2%80%94%20not%20a%20wall%20of%20docs%3A%0A%20%20%20-%20One%20sentence%20on%20what%20this%20library%20is%20for%20%28agent%20as%20wazir%2C%20not%20courtier%29.%0A%20%20%20-%20The%204%20workflow%20bundles%20%28product%20discovery%2C%20better%20engineering%2C%20existing-plan%20review%2C%20shipping%29%20as%20journeys%20with%20when%20to%20start%20each.%0A%20%20%20-%20For%20each%20skill%3A%20name%2C%20one-line%20purpose%2C%20and%20a%20concrete%20trigger%20phrase%20%28%22say%20X%20when...%22%29.%0A%20%20%20-%20A%20%22if%20you%20only%20remember%205%20things%22%20cheat%20sheet%20for%20day-to-day%20use.%0A%20%20%20-%20Ask%20what%20I%20am%20working%20on%20right%20now%20and%20recommend%20the%20first%20skill%20%2B%20bundle%20to%20try.%0A%0AKeep%20it%20scannable.%20Use%20tables%20or%20short%20bullets.%20No%20lore%20dumps.)
[![Open in Bolt](https://img.shields.io/badge/Open_in-Bolt-000000?style=for-the-badge&logo=stackblitz&logoColor=white)](https://bolt.new/?prompt=You+are+onboarding+me+to+the+agent-shell-hamelech+skill+library+%28https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%29.%0A%0ADo+this+in+order%3A%0A1.+Read+the+repo+README+and+every+skill+under+skills%2F%2A%2FSKILL.md.%0A2.+Run+melech-sync-skills+%28or%3A+npx+skills+add+https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech+--skill+melech-sync-skills+-g+-y+-a+%22%2A%22+then+invoke+melech+sync%29+to+install+all+skills+globally.%0A3.+Give+me+a+first-day+tour+%E2%80%94+like+a+product+wizard+%E2%80%94+not+a+wall+of+docs%3A%0A+++-+One+sentence+on+what+this+library+is+for+%28agent+as+wazir%2C+not+courtier%29.%0A+++-+The+4+workflow+bundles+%28product+discovery%2C+better+engineering%2C+existing-plan+review%2C+shipping%29+as+journeys+with+when+to+start+each.%0A+++-+For+each+skill%3A+name%2C+one-line+purpose%2C+and+a+concrete+trigger+phrase+%28%22say+X+when...%22%29.%0A+++-+A+%22if+you+only+remember+5+things%22+cheat+sheet+for+day-to-day+use.%0A+++-+Ask+what+I+am+working+on+right+now+and+recommend+the+first+skill+%2B+bundle+to+try.%0A%0AKeep+it+scannable.+Use+tables+or+short+bullets.+No+lore+dumps.)

Codex and Windsurf badges route through [open-in-agent](https://github.com/anxkhn/open-in-agent) because GitHub strips custom URL schemes from markdown links. Cursor, Claude Code, and Bolt use each product's official HTTPS deeplink.

Or **copy-paste** into any agent chat:

```text
You are onboarding me to the agent-shell-hamelech skill library (https://github.com/AdirD/agent-shell-hamelech).

Do this in order:
1. Read the repo README and every skill under skills/*/SKILL.md.
2. Run melech-sync-skills (or: npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-sync-skills -g -y -a "*" then invoke melech sync) to install all skills globally.
3. Give me a first-day tour — like a product wizard — not a wall of docs:
   - One sentence on what this library is for (agent as wazir, not courtier).
   - The 4 workflow bundles (product discovery, better engineering, existing-plan review, shipping) as journeys with when to start each.
   - For each skill: name, one-line purpose, and a concrete trigger phrase ("say X when...").
   - A "if you only remember 5 things" cheat sheet for day-to-day use.
   - Ask what I am working on right now and recommend the first skill + bundle to try.

Keep it scannable. Use tables or short bullets. No lore dumps.
```

<details>
<summary>Direct deeplinks (copy; run <code>open "…"</code> on macOS)</summary>

GitHub cannot link custom URL schemes directly. Paste one of these in your terminal or browser address bar:

**Claude Code CLI**

```text
claude-cli://open?repo=AdirD%2Fagent-shell-hamelech&q=You+are+onboarding+me+to+the+agent-shell-hamelech+skill+library+%28https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%29.%0A%0ADo+this+in+order%3A%0A1.+Read+the+repo+README+and+every+skill+under+skills%2F%2A%2FSKILL.md.%0A2.+Run+melech-sync-skills+%28or%3A+npx+skills+add+https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech+--skill+melech-sync-skills+-g+-y+-a+%22%2A%22+then+invoke+melech+sync%29+to+install+all+skills+globally.%0A3.+Give+me+a+first-day+tour+%E2%80%94+like+a+product+wizard+%E2%80%94+not+a+wall+of+docs%3A%0A+++-+One+sentence+on+what+this+library+is+for+%28agent+as+wazir%2C+not+courtier%29.%0A+++-+The+4+workflow+bundles+%28product+discovery%2C+better+engineering%2C+existing-plan+review%2C+shipping%29+as+journeys+with+when+to+start+each.%0A+++-+For+each+skill%3A+name%2C+one-line+purpose%2C+and+a+concrete+trigger+phrase+%28%22say+X+when...%22%29.%0A+++-+A+%22if+you+only+remember+5+things%22+cheat+sheet+for+day-to-day+use.%0A+++-+Ask+what+I+am+working+on+right+now+and+recommend+the+first+skill+%2B+bundle+to+try.%0A%0AKeep+it+scannable.+Use+tables+or+short+bullets.+No+lore+dumps.
```

**Codex Desktop** (`originUrl` picks the repo if you have it cloned)

```text
codex://new?prompt=You+are+onboarding+me+to+the+agent-shell-hamelech+skill+library+%28https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%29.%0A%0ADo+this+in+order%3A%0A1.+Read+the+repo+README+and+every+skill+under+skills%2F%2A%2FSKILL.md.%0A2.+Run+melech-sync-skills+%28or%3A+npx+skills+add+https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech+--skill+melech-sync-skills+-g+-y+-a+%22%2A%22+then+invoke+melech+sync%29+to+install+all+skills+globally.%0A3.+Give+me+a+first-day+tour+%E2%80%94+like+a+product+wizard+%E2%80%94+not+a+wall+of+docs%3A%0A+++-+One+sentence+on+what+this+library+is+for+%28agent+as+wazir%2C+not+courtier%29.%0A+++-+The+4+workflow+bundles+%28product+discovery%2C+better+engineering%2C+existing-plan+review%2C+shipping%29+as+journeys+with+when+to+start+each.%0A+++-+For+each+skill%3A+name%2C+one-line+purpose%2C+and+a+concrete+trigger+phrase+%28%22say+X+when...%22%29.%0A+++-+A+%22if+you+only+remember+5+things%22+cheat+sheet+for+day-to-day+use.%0A+++-+Ask+what+I+am+working+on+right+now+and+recommend+the+first+skill+%2B+bundle+to+try.%0A%0AKeep+it+scannable.+Use+tables+or+short+bullets.+No+lore+dumps.&originUrl=https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech
```

**Windsurf Cascade**

```text
windsurf://cascade/newChat?prompt=You+are+onboarding+me+to+the+agent-shell-hamelech+skill+library+%28https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech%29.%0A%0ADo+this+in+order%3A%0A1.+Read+the+repo+README+and+every+skill+under+skills%2F%2A%2FSKILL.md.%0A2.+Run+melech-sync-skills+%28or%3A+npx+skills+add+https%3A%2F%2Fgithub.com%2FAdirD%2Fagent-shell-hamelech+--skill+melech-sync-skills+-g+-y+-a+%22%2A%22+then+invoke+melech+sync%29+to+install+all+skills+globally.%0A3.+Give+me+a+first-day+tour+%E2%80%94+like+a+product+wizard+%E2%80%94+not+a+wall+of+docs%3A%0A+++-+One+sentence+on+what+this+library+is+for+%28agent+as+wazir%2C+not+courtier%29.%0A+++-+The+4+workflow+bundles+%28product+discovery%2C+better+engineering%2C+existing-plan+review%2C+shipping%29+as+journeys+with+when+to+start+each.%0A+++-+For+each+skill%3A+name%2C+one-line+purpose%2C+and+a+concrete+trigger+phrase+%28%22say+X+when...%22%29.%0A+++-+A+%22if+you+only+remember+5+things%22+cheat+sheet+for+day-to-day+use.%0A+++-+Ask+what+I+am+working+on+right+now+and+recommend+the+first+skill+%2B+bundle+to+try.%0A%0AKeep+it+scannable.+Use+tables+or+short+bullets.+No+lore+dumps.
```

</details>

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
| [`melech-sync-skills`](#melech-sync-skills) | Are all melech skills installed globally and current? | Say `melech-sync-skills` / `melech sync` to apply, or `melech-sync-skills list` for a dry catalog. |

### Understand what you need

| Skill | Question it answers | Reach for it when |
|---|---|---|
| [`melech-distill-need`](#melech-distill-need) | Is the requested thing actually the right solution? | "distill this", "faster horse", "what do I actually need". |
| [`melech-scout`](#melech-scout) | Has someone already built this? | "does this already exist", "is there a tool for this", "don't reinvent the wheel", "what's out there for X". |
| [`melech-market-validation`](#melech-market-validation) | What market premise should we test, and does it survive customer and commercial evidence? | Shape or validate a startup, product opportunity, ICP, buyer, demand, willingness to pay, or paid expansion. |

### Shape work before coding

| Skill | Question it answers | Reach for it when |
|---|---|---|
| [`melech-pre-plan`](#melech-pre-plan) | Do we share a precise, buildable concept? | You want alignment before plan mode or code, with calibrated question depth. |
| [`melech-consult`](#melech-consult) | Did the AI miss a landmine, edge case, or simpler path? | The AI proposed an implementation, architecture, or idea and you say "double check", "proof this", or "are you sure". |
| [`melech-idea-to-canvas`](#melech-idea-to-canvas) | Can the team absorb this idea without rereading the whole input? | You have any idea, note, brief, or doc and want a standalone knowledge-transfer Canvas. |
| [`melech-8020`](#melech-8020) | What is the smallest useful path to the outcome? | "least diff", "minimal change", "80/20", "least intrusive". |
| [`melech-challenge`](#melech-challenge) | What is weak or risky about this direction? | You already have a direction and want holes poked before building. |
| [`melech-visualize`](#melech-visualize) | Can this structure, flow, or trade-off be easier to see? | Prose is hiding architecture, sequence, boundaries, layout, or ambiguity. |

### Implement and ship safely

| Skill | Question it answers | Reach for it when |
|---|---|---|
| [`melech-prune`](#melech-prune) | What dead code, zombie workflows, or YAGNI bloat accumulated during AI coding? | After multi-turn iteration with an AI, when you want to audit uncalled helpers, dead types, and speculative abstractions before opening a PR. |
| [`melech-debug-mode`](#melech-debug-mode) | What runtime evidence explains this reproducible bug? | A user can exercise a failing workflow but static inspection and existing logs are insufficient. Manual: they reproduce. Autopilot: the agent drives an already-open logged-in Chrome tab. |
| [`melech-smart-comments`](#melech-smart-comments) | Which intent and landmines must survive in the code? | An agent is writing, editing, refactoring, or reviewing commented code. |
| [`melech-code-review-clone`](#melech-code-review-clone) | Can an agent review PRs like me and keep learning? | Train or resync a private reviewer Clone by correlating your real review comments to the local code and git history in the repo you run it from. |
| [`melech-babysit`](#melech-babysit) | Can this PR be kept moving until it is merge-ready? | Comments, conflicts, and CI need recurring attention. |

---

## Which skill do I need?

| If you are saying… | Start with | Why |
|---|---|---|
| "What melech skills do I have / should I update?" | [`melech-sync-skills`](#melech-sync-skills) | Global sync of this library into `~/.agents/skills` and every agent. |
| "I have a startup/product idea." | [`melech-market-validation`](#melech-market-validation) | It can shape an open premise into a testable hypothesis before gathering market evidence. |
| "I have a specific startup hypothesis—is the pain real, who buys, and will they pay?" | [`melech-market-validation`](#melech-market-validation) | Runs desk research, customer discovery, and a behavioral/commercial test through a market decision. |
| "Should our existing product add this feature?" | [`melech-distill-need`](#melech-distill-need) | Treat the feature as a proposed solution, uncover the outcome, and compare better means before planning it. |
| "Build a custom RBAC engine." | [`melech-distill-need`](#melech-distill-need) | The named implementation may be a faster horse; first uncover the actual need. |
| "Is there already a library/tool/service that does this?" | [`melech-scout`](#melech-scout) | Parallel verified search of libraries, OSS, dev tools, managed services, and deps already installed. |
| "The AI just hand-rolled a queue/retry/scheduler — check that." | [`melech-scout`](#melech-scout) | Names the capability, then finds the incumbents instead of guessing package names from memory. |
| "What's out there for X? Any new AI tools for it?" | [`melech-scout`](#melech-scout) | Open-ended landscape discovery with a frontier lane for what shipped recently. |
| "We decided to add RBAC; align it before planning." | [`melech-pre-plan`](#melech-pre-plan) | The work is build-shaped, but the design concept still needs alignment. |
| "Double-check / proof this proposal before building." | [`melech-consult`](#melech-consult) | Isolates the AI's proposal and briefs fresh subagents/councils to stress-test it without grading its own homework. |
| "Are you sure? Consult another model on this architecture or idea." | [`melech-consult`](#melech-consult) | Unbiased second opinion or expert council to expose blindspots and failure modes. |
| "Turn this idea/doc/notes into a Canvas the team can absorb." | [`melech-idea-to-canvas`](#melech-idea-to-canvas) | Knowledge transfer from any idea, note, or doc into a scannable Canvas. |
| "Find the least invasive way to add role checks." | [`melech-8020`](#melech-8020) | The outcome is understood; now minimize the implementation. |
| "I can reproduce this bug, but the existing logs do not explain it." | [`melech-debug-mode`](#melech-debug-mode) | Temporary runtime probes can narrow the real failing path before a fix. |
| "Drive the Chrome tab I'm already logged into while we debug." | [`melech-debug-mode`](#melech-debug-mode) | Autopilot: Chrome DevTools MCP `--autoConnect`; one-time `chrome://inspect/#remote-debugging` toggle, then Allow. |
| "I've been iterating with AI and need to strip dead code and bloat." | [`melech-prune`](#melech-prune) | Evidentiary audit of working diff/branch against 4 proofs before PR. |
| "Learn how I review PRs and make me a reviewer Clone." | [`melech-code-review-clone`](#melech-code-review-clone) | Builds or resyncs one private user-global Clone with repo-specific memory. |
| "Here is the design—poke holes in it." | [`melech-challenge`](#melech-challenge) | A direction exists and needs pressure-testing. |
| "Research competitors to help choose our product or market direction." | [`melech-market-validation`](#melech-market-validation) | Competitor and substitute evidence should reshape the premise and the test that follows. |
| "Produce a sourced comparison of these competitors." | No dedicated skill yet | Competitor intelligence is the deliverable; extract a skill only if this becomes recurring work. |

## Workflow bundles

Bundles are **journey recipes**, not additional skills. Skip any step whose
question is already answered.

### Product discovery

```text
melech-distill-need (if the ask is a proposed solution)
  → melech-market-validation (shape an open premise, then test it)
  → melech-consult (optional idea council)
  → melech-pre-plan
```

Use when you are unsure what should exist. The flow may stop at
`melech-distill-need` or `melech-market-validation` if reuse, reshape, hold, or stop wins.

### Better engineering

```text
melech-scout (if it might already exist) → melech-distill-need → melech-pre-plan → melech-consult (optional sanity check/council) → melech-8020 → melech-challenge (optional)
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

Requires Python 3.9+ and the official Vercel Labs `portless` CLI. Live-Chrome attach additionally needs Chrome 144+, Node/`npx`, and a host that can run MCP. The skill writes the official `chrome-devtools-mcp --autoConnect` config when it is missing (see [the Chrome blog](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)); the collector still works without it.

Optional: install the bundled `dm` shell command for one-keystroke access from any directory (`dm` opens the doctor TUI, `dm help` lists commands, `dm start`/`dm stop <dir>`/`dm mcp-setup`/`dm browser-check` forward to the launcher):

```bash
sh <skill-dir>/scripts/install-dm.sh
```

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

Gets independent model opinions on an AI-proposed plan, fix, architecture, or idea.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-consult
```

Use it when:
- the AI proposed a plan, architecture, or fix and you say "double check", "proof this", or "are you sure"
- you want an unbiased second opinion from a fresh subagent on a different model/provider than the thread that wrote the proposal
- you want an expert council to triangulate a multi-variable trade-off (e.g., simplicity vs. scale vs. security)
- you want a devil's advocate / red team to stress-test a proposal for hidden landmines before writing code

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

### [`melech-scout`](skills/melech-scout)

Finds and compares existing tools before building a capability from scratch.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-scout
```

Use it when:
- an agent just hand-rolled a queue, retry policy, scheduler, state machine, parser, or auth layer and you suspect a known tool already does it
- you want build-vs-buy answered with verified sources instead of a model's stale memory
- you want to know whether the capability is already covered by an installed dependency or a vendor you already pay for
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
  melech-8020/
  melech-babysit/
  melech-challenge/
  melech-consult/
  melech-idea-to-canvas/
  melech-distill-need/
  melech-debug-mode/
  melech-sync-skills/
  melech-market-validation/
  melech-pre-plan/
  melech-prune/
  melech-code-review-clone/
  melech-scout/
  melech-smart-comments/
  melech-visualize/
```

Every skill is self-contained: a `SKILL.md` with frontmatter, optional `scripts/`, and optional `references/`.

## Contributing

Add a new skill by creating `skills/<name>/SKILL.md` with proper frontmatter (`name`, `description`). Then update the catalog above — the `AGENTS.md` maintenance rule enforces this.

Before pushing, run `bash scripts/pre-push-audit.sh` (see `AGENTS.md` for commit/push safety rules and optional git hook setup).

After pushing, sync installations across all global agent dirs by running the `melech-sync-skills` skill (or `melech sync`).


## License

[MIT](./LICENSE)
