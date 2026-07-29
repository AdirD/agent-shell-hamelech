# agent-shell-hamelech

Reusable skills, commands, and later rules for working with coding agents.

This repo is a small collection of agent-facing artifacts that can be copied into your own setup and adapted to your workflow.

## Catalog

### Skills

#### `hebrew-rtl-writing`

Fix mixed RTL/LTR rendering for any textual artifact that is mostly Hebrew but includes English words.

Install this skill specifically:

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill hebrew-rtl-writing
```

Manual install fallback:

```bash
mkdir -p .agents/skills
cp -R skills/hebrew-rtl-writing .agents/skills/hebrew-rtl-writing
```

Use it when:
- the text is primarily Hebrew
- English words or technical terms make raw Markdown hard to read
- you want bidi isolation applied without touching code blocks or links

#### `8020`

Help decide on the smallest useful way to reach a product goal before writing code. Explore technical, UX, product, and strategy trade-offs, favor existing integration points over new code, and surface 80/20 alternatives.

Install this skill specifically:

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill 8020
```

Manual install fallback:

```bash
mkdir -p .agents/skills
cp -R skills/8020 .agents/skills/8020
```

Use it when:
- you want the least intrusive or smallest-diff path to a goal
- you ask for "80/20", "minimal change", or "least diff"
- you want trade-offs explained before implementation, not a ticket-style build

#### `babysit`

Keep a PR merge-ready by looping over comments, merge conflicts, and CI on a recurring cadence (default 5 min) until the PR is green and mergeable, or a real blocker needs the user. Delegates the loop to a `/loop` primitive if the agent has one, otherwise arms a background heartbeat.

Install this skill specifically:

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill babysit
```

Manual install fallback:

```bash
mkdir -p .agents/skills
cp -R skills/babysit .agents/skills/babysit
```

Use it when:
- you have an open PR and want it driven to merge without you polling every few minutes
- teammates and review bots (Bugbot, CodeRabbit, ...) keep posting new comments and CI keeps rerunning, so a one-shot check goes stale
- you want the agent to stop cleanly on real blockers instead of spinning on failures it can't fix

### Commands

#### `visualize`

Render the current idea as a compact ASCII diagram.

Install:

```bash
mkdir -p .cursor/commands
cp commands/visualize.md .cursor/commands/visualize.md
```

Use it for:
- architecture
- flows
- comparisons
- boundaries
- current mental models

#### `challenge`

Pressure-test an existing idea or direction before implementation.

Install:

```bash
mkdir -p .cursor/commands
cp commands/challenge.md .cursor/commands/challenge.md
```

Use it when:
- you already have a direction
- you want high-value questions, not a rewrite from zero
- you want assumptions, risks, and over-engineering pressure-tested

### Rules

Rules are auto-loaded instructions shared across agents (Cursor, Claude Code, Codex). Install with the bundled CLI — it auto-detects your agent config and writes to the right place.

```bash
# Install for this repo (default)
npx github:AdirD/agent-shell-hamelech install <rule-name>

# Install globally for your user
npx github:AdirD/agent-shell-hamelech install <rule-name> --global

# See what's available
npx github:AdirD/agent-shell-hamelech list
```

#### `smart-comments`

Make the agent write selective, intent-preserving inline comments, and respect existing ones.

Install:

```bash
npx github:AdirD/agent-shell-hamelech install smart-comments
```

Use it when:
- you want agents to leave landmines, WHYs, and workarounds behind, not narrate WHAT the code does
- you've been burned by an agent "cleaning up" a comment that was the only trace of a past incident
- you want one rule that covers Cursor, Claude Code, and any tool reading `AGENTS.md`

## Repo Structure

```text
skills/
commands/
rules/
```

The plan is to grow this into a broader pattern library over time, likely including:

```text
skills/
commands/
rules/
references/
```
