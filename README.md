# agent-shell-hamelech

A small, opinionated library of **agent skills** — drop-in behaviors you can install into Cursor, Claude Code, Codex, and any other agent that speaks the [Agent Skills](https://github.com/anthropics/skills) format.

Everything in this repo is a skill. No commands, no rules, no bespoke installer. One repo, one format, one install command.

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

## Skills

| Skill | What it does | When to reach for it |
|---|---|---|
| [`8020`](#8020) | Finds the smallest useful path to a product goal before coding. | "least diff", "minimal change", "80/20", "least intrusive". |
| [`babysit`](#babysit) | Loops on an open PR — comments, conflicts, CI — until it's merge-ready. | You have a PR and don't want to poll it every 5 minutes. |
| [`challenge`](#challenge) | Pressure-tests an existing direction one high-value question at a time. | You have a plan and want holes poked before you build it. |
| [`hebrew-rtl-writing`](#hebrew-rtl-writing) | Fixes mixed RTL/LTR rendering in Hebrew Markdown with embedded English. | Hebrew prose that looks broken because of English words. |
| [`ideation`](#ideation) | Product/startup thinking partner — clarifies the real goal, researches, challenges. | Ideating on a product, service, or business — before it's a spec. |
| [`podcast-production`](#podcast-production) | Turns long recordings into a user-approved podcast story and finished video. | Raw interview/meeting/webinar → storyline, script, clips, or rendered cut. |
| [`smart-comments`](#smart-comments) | Writes intent-preserving inline comments and treats existing ones as load-bearing. | Any code edit where the agent might narrate what code does or "clean up" comments. |
| [`visualize`](#visualize) | Renders the current idea as a compact ASCII diagram. | Flow, structure, layout, comparison, or mental-model ambiguity. |

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

### `ideation`

An adaptive, circular thinking partner for new ideas and existing products. It clarifies the idea's relationship to any current product, explores only the uncertainty that matters now, researches or parallelizes proportionately, reframes as evidence changes, and keeps one evolving brief or produces a specialized artifact only when useful.

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill ideation
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
  hebrew-rtl-writing/
  ideation/
  podcast-production/
  smart-comments/
  visualize/
```

Every skill is self-contained: a `SKILL.md` with frontmatter, optional `scripts/`, and optional `references/`.

## Contributing

Add a new skill by creating `skills/<name>/SKILL.md` with proper frontmatter (`name`, `description`). Then update the catalog above — the `AGENTS.md` maintenance rule enforces this.

Before pushing, run `bash scripts/pre-push-audit.sh` (see `AGENTS.md` for commit/push safety rules and optional git hook setup).

## License

[MIT](./LICENSE)
