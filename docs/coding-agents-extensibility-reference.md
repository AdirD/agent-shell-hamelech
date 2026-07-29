# Extensibility in Claude Code, Cursor, and Codex CLI

A reference covering the primitives each agent exposes for customization — instruction files, slash commands, skills, subagents, hooks, and plugins — and how they compare. Accurate as of April 2026.

---

## TL;DR matrix

| Primitive | Claude Code | Cursor | Codex CLI |
|---|---|---|---|
| **Instruction files** | `CLAUDE.md` (+ `.local`, enterprise) | `.cursor/rules/*.mdc`, User Rules, `AGENTS.md` | `AGENTS.md` (+ `AGENTS.override.md`, fallback filenames) |
| **Modular rules** | `.claude/rules/*.md` (path-scoped via frontmatter) | `.cursor/rules/*.mdc` (glob-scoped) | Directory-nested `AGENTS.md` |
| **Slash commands** | `.claude/commands/*.md` (deprecated, → Skills) | `.cursor/commands/*.md` | `~/.codex/prompts/*.md` (deprecated, → Skills) |
| **Skills** | `.claude/skills/<n>/SKILL.md` (progressive disclosure) | `.cursor/skills/<n>/SKILL.md` (added Jan 2026) | `.agents/skills/<n>/SKILL.md` (shared spec) |
| **Subagents** | Task tool + `.claude/agents/` | Native (added Jan 2026) | Native (opt-in, explicit invocation) |
| **Hooks** | 12–21 lifecycle events, 4 handler types | 6 events (beta, v1.7+) | Experimental engine (v0.114+), catching up |
| **Plugins** | Marketplace + `.claude-plugin/` (official since Oct 2025) | Marketplace + `.cursor-plugin/plugin.json` | `.codex-plugin/plugin.json` + marketplaces |
| **MCP** | Full support | Full support | Full support |
| **Config** | `settings.json`, `~/.claude/` | Settings UI + `.cursor/*.json` | `~/.codex/config.toml` |

**One-line summary of each agent's extensibility philosophy:**
- **Claude Code** — most mature and composable stack (skills + hooks + subagents + plugins). Progressive disclosure is the organizing principle.
- **Cursor** — rules-and-commands-first, with skills/subagents/hooks added later to catch up. Settings UI is the primary surface.
- **Codex** — heaviest TOML-driven configuration, strong hierarchy on `AGENTS.md`, skills/plugins adopted from the Claude-originated spec.

---

## Claude Code

### Memory & instruction files

Four-tier hierarchy, loaded in order of increasing specificity:

1. **Enterprise policy** — `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS), `/etc/claude-code/CLAUDE.md` (Linux), `C:\ProgramData\ClaudeCode\CLAUDE.md` (Windows). Managed by IT.
2. **Project memory** — `./CLAUDE.md` or `./.claude/CLAUDE.md`. Committed; team-shared.
3. **User memory** — `~/.claude/CLAUDE.md`. Personal preferences across all projects.
4. **Local project** — `CLAUDE.local.md`. Personal, auto-gitignored, additive (loaded alongside `CLAUDE.md`).

Files are loaded in full regardless of length, but shorter files produce better adherence. Use `@path/to/file` to import external files without bloating the top-level doc.

### Modular rules

`.claude/rules/*.md` — topic-specific files kept separate from the main `CLAUDE.md`. Supports a `paths` frontmatter key for path-scoped activation:

```markdown
---
paths:
  - "**/*.test.ts"
  - "tests/**"
---

# Testing conventions
- Use Vitest, not Jest
- Tests must mock database calls
```

This is Claude Code's closest analogue to Cursor's auto-attached glob rules.

### Auto-memory (newer system)

`~/.claude/projects/<project>/memory/` contains:
- `MEMORY.md` — index, loaded every session (capped for size).
- Topic files (e.g., `debugging.md`) — loaded on-demand via Claude's file tools.

Claude writes to these during sessions when it decides something is worth remembering. Run `/memory` in-session to browse.

### Slash commands (legacy)

Markdown files in:
- `.claude/commands/` — project-scoped.
- `~/.claude/commands/` — user-global.

Filename becomes the command name. Subdirectories create namespaces (`commands/frontend/build.md` → `/frontend:build`). Supports `argument-hint` and `allowed-tools` frontmatter for usage guidance and tool restrictions.

**Status:** deprecated in favor of Skills, but CLI still supports both. Skills are recommended because they support autonomous invocation in addition to explicit `/` triggering.

### Skills (current format)

`.claude/skills/<n>/SKILL.md` with the structure:

```
my-skill/
├── SKILL.md          # required, with YAML frontmatter
├── scripts/          # optional, executable Python/Bash
├── references/       # optional, loaded on-demand
└── assets/           # optional, templates/fonts/icons
```

`SKILL.md` frontmatter:
```yaml
---
name: pdf-processing
description: Extract text and tables from PDFs, fill forms, merge documents.
---
```

**Progressive disclosure** is the core design principle — three layers:
1. **Metadata** (~100 tokens): Always in system prompt so Claude knows a skill exists.
2. **SKILL.md body** (<500 lines recommended): Loaded when Claude decides the skill applies.
3. **Bundled resources**: Read only when explicitly needed.

This lets an agent have hundreds of skills without exhausting context. Skills can be invoked explicitly (`/skill-name`) or implicitly (Claude picks one matching the task).

### Subagents

Invoked via the Task tool. Each subagent runs in its own isolated context with its own tool permissions, returns a summary to the main conversation. Defined in `.claude/agents/` with frontmatter specifying allowed tools and model.

Key property: subagents don't pollute the parent context — a 20-step codebase scan subagent returns a clean 3-bullet summary, not the full transcript.

### Hooks

Defined in `settings.json` under `hooks`. Four handler types:
- `command` — shell command (most common).
- `prompt` — LLM-based semantic evaluation.
- `agent` — spawns a subagent for deep analysis.
- `http` — POST to an endpoint.

Key events (12 core, up to 21 with extensions):
- `SessionStart`, `SessionEnd`, `Setup`
- `PreToolUse`, `PostToolUse`, `PostToolUseFailure` — can approve/deny/modify tool invocations.
- `PermissionRequest` — auto-approve safe commands.
- `UserPromptSubmit` — inject context, scan for secrets.
- `Stop`, `SubagentStop`, `PreCompact`, `Notification`, `FileChanged`, `WorktreeCreate`, `TeammateIdle`, `TaskCompleted`, `ConfigChange`.

Matchers are regex evaluated against `tool_name` (or relevant field) in the JSON stdin payload.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "npx prettier --write \"$TOOL_INPUT_FILE_PATH\"" }]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": ".claude/scripts/guard.sh" }]
      }
    ]
  }
}
```

Hooks return exit codes or JSON to control flow — `PreToolUse` can approve/deny, `Stop` can block completion, `SessionStart`'s stdout injects into model context.

Async hooks (non-blocking) were added in early 2026 for long-running background checks.

> **Advisory — authoring tooling:** [`cc-hooks-ts`](https://github.com/sushichan044/cc-hooks-ts) is a community TypeScript library that provides type-safe Claude Code hooks. Uses Valibot for runtime schema validation, offers full TS inference on payloads/responses, and supports custom tool definitions via interface merging. Pairs well with Bun's `Bun.stdin.json()` for clean stdin handling. The closest thing to first-party DX for hook authoring.

### Plugins

Launched Oct 2025 public beta, now GA. Plugins bundle skills, subagents, hooks, commands, and MCP servers into one installable unit.

Structure: `.claude-plugin/plugin.json` manifest, deployed to `~/.claude/plugins/` once installed.

Commands:
```bash
/plugin marketplace add owner/repo
/plugin install my-plugin@marketplace-name
```

The official marketplace (`claude-plugins-official`) ships ~101 plugins as of early 2026 — Anthropic-internal ones (language servers, feature-dev, security-guidance, frontend-design) plus partner plugins (Playwright, Supabase, Figma, Vercel, Linear, Sentry, Stripe, Firebase). Enterprises can distribute vetted marketplaces via `enabledPlugins` in managed settings.

### MCP

Configured via `mcp_servers` in settings. Plugins can bundle MCP configs. Nothing Claude Code-specific beyond standard MCP.

---

## Cursor

### Rules

Four rule types with clear scoping:

1. **User Rules** — Cursor Settings → Rules. Plain text, always applied across all projects. No file, no metadata.
2. **Team Rules** — Enforced at the organization level. Plain text, applied across all team projects. No globs or metadata.
3. **Project Rules** — `.cursor/rules/*.mdc`. Committed, team-shared, metadata-rich.
4. **Legacy `.cursorrules`** — Single-file format, deprecated. Prefer `AGENTS.md` or `.cursor/rules/`.

**Precedence:** Team → Project → User (earlier sources take precedence on conflict). All applicable rules merge into context.

**`AGENTS.md` support** — Cursor reads `AGENTS.md` at the project root and in subdirectories (closest-wins). You can skip `.cursor/rules/` entirely and just use `AGENTS.md` if you want a cross-tool config.

### MDC frontmatter

The `.mdc` format has a specific YAML frontmatter (not strict YAML — strings shouldn't be quoted):

```markdown
---
description: Internal RPC pattern guidance
globs: src/**/*.ts,src/**/*.tsx
alwaysApply: false
---

- Use our internal RPC pattern when defining services
- Use snake_case for service names
```

Four activation modes based on field combinations:

| Config | Behavior |
|---|---|
| `alwaysApply: true` | Always in context (globs ignored even if set). |
| `globs: pattern`, `alwaysApply: false` | Auto-attached only when user references a matching file. |
| `description: "..."`, `alwaysApply: false` | Agent-decided — Claude reads description, fetches full rule if relevant. |
| All fields empty | Manual only — must `@rule-name` to invoke. |

Caveat: a rule that matches the glob *can still be omitted* by the agent if content seems irrelevant to the query.

Since Cursor 2.2, new rules are folders in `.cursor/rules/`; `.mdc` files still work. Cursor can also import rules from other tools (including Claude skills/plugins — imported as agent-decided rules).

### Custom slash commands

`.cursor/commands/*.md` — Markdown files with reusable prompts. Filename is the command name. Typing `/` in the chat input surfaces them.

```markdown
# Generate API Documentation

Create comprehensive API documentation for the current code.
Include:
- Endpoint descriptions and HTTP methods
- Request/response schemas with examples
- Authentication requirements

Format as OpenAPI/Swagger specification.
```

**Known gap:** no personal global commands — `~/.cursor/commands/` is a requested feature but not supported. Personal commands need the project-level directory.

### Skills (added Cursor 2.4, Jan 2026)

Same `SKILL.md` structure as Claude Code. Located in:
- `.cursor/skills/` — personal.
- Project-local directories — shared.

Invoked via `/` menu or implicitly by the agent. Explicitly positioned as dynamic/procedural "how-to" instructions, contrasted with always-on declarative Rules.

### Subagents (added Cursor 2.4, Jan 2026)

Parallel specialized agents with their own context, prompts, tool access, and models. Default built-in subagents cover codebase research, terminal commands, parallel work streams. Configurable custom subagents through the settings.

### Hooks (added Cursor 1.7, Oct 2025 — beta)

Configured in `.cursor/hooks.json` with three-tier precedence:
- `~/.cursor/hooks.json` (user)
- `/etc/cursor/hooks.json` (enterprise)
- `.cursor/hooks.json` (project)

**Six core lifecycle events:**
- `beforeSubmitPrompt` — validate/block prompts.
- `beforeShellExecution` — allow/deny/ask for shell commands (returns JSON).
- `beforeMCPExecution` — same but for MCP tool calls.
- `beforeReadFile` — can rewrite file content before it reaches the model (redaction).
- `afterFileEdit` — fires on edits with old/new content (notification-only, can't block).
- `stop` — end of session (commit snapshots, conventional commits).

Newer events added: `preToolUse`, `postToolUse`, `postToolUseFailure`, `subagentStart`, `subagentStop`, `afterAgentResponse`, `afterAgentThought`, `afterShellExecution`, `afterMCPExecution`, `beforeTabFileRead`, `afterTabFileEdit` (Tab/inline completions have separate hooks from Agent).

Cloud agents also honor project hooks from `.cursor/hooks.json`.

Example blocking dangerous git:
```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      { "command": ".cursor/hooks/block-dangerous-git.sh", "matcher": "git" }
    ]
  }
}
```

Hooks receive structured JSON on stdin, return JSON on stdout. Only command hooks supported (no prompt/agent handler types like Claude).

> **Advisory — authoring tooling:** [`cursor-hooks`](https://www.npmjs.com/package/cursor-hooks) is a community npm package by John Lindquist that ships full TypeScript definitions for every hook payload and response, plus a JSON schema for `.cursor/hooks.json` validation and autocomplete in your editor. Install with `bun install cursor-hooks`, point your settings.json `json.schemas` at the bundled schema, and write hooks with full inference and compile-time checks. The de facto standard for typed Cursor hook authoring.

### Plugins

Native plugin system shipped alongside skills/subagents. Plugins bundle rules, skills, subagents, commands, hooks, and MCP servers into one installable unit.

**Manifest:** `.cursor-plugin/plugin.json` at the plugin root.
- Required: `name` (lowercase kebab-case).
- Optional metadata: `version`, `displayName`, `description`, `author`, `license`, `homepage`, `repository`, `keywords`.
- Optional component path overrides: `rules`, `skills`, `agents`, `commands`, `hooks`, `mcpServers` — each points at the directory holding that primitive if you don't use the default layout.

**Standard layout:**
```
my-plugin/
├── .cursor-plugin/plugin.json   # required manifest
├── rules/*.mdc
├── skills/<name>/SKILL.md
├── agents/
├── commands/
├── hooks/hooks.json
├── mcp.json
└── assets/                      # logos, static files
```

**Installation surfaces:**
1. **Official marketplace** — browse/install from the Cursor marketplace panel inside the IDE. Submit your own at `cursor.com/marketplace/publish` by providing the repo link.
2. **Team marketplaces** (Teams/Enterprise) — admins import repos through dashboard settings; members install from the team marketplace panel.
3. **Community directory** — `cursor.directory` lists community plugins and MCPs.
4. **Local / dev install** — drop the plugin folder into `~/.cursor/plugins/local/<name>/` (with `.cursor-plugin/plugin.json` at the root) and run **Developer: Reload Window**. There is **no `cursor plugins install <repo>` CLI command** — GitHub-repo installs go through a marketplace, or you clone manually into the local path.

**Relation to primitives:** a plugin's skills/rules/hooks behave exactly like their loose equivalents described above — the manifest just packages them together with a version and identity.

### MCP

Full support. Team-level MCP servers can be distributed. Subagents and tab completions use separate hook namespaces, so permissions can differ.

---

## Codex CLI

### AGENTS.md hierarchy

Codex walks from project root to current working directory, concatenating `AGENTS.md` files. Files closer to the cwd appear later in the prompt, so they override earlier guidance.

**Discovery order at each level:**
1. `AGENTS.override.md` — replaces all parent instructions at that level.
2. `AGENTS.md` — the standard file.
3. Fallback filenames declared in `project_doc_fallback_filenames` (e.g., `TEAM_GUIDE.md`, `.agents.md`).

Global defaults: `~/.codex/AGENTS.md`. Always loaded, every repo inherits.

Combined size limit: 32 KiB default (`project_doc_max_bytes`), raisable.

**Project root discovery** — default is the nearest `.git`. Override with `project_root_markers = [".git", ".hg", ".sl"]` in `~/.codex/config.toml`.

### Custom prompts (deprecated → Skills)

`~/.codex/prompts/*.md` — reusable prompts invoked via `/prompts:<n>`. Example:

```markdown
---
description: Prep a branch, commit, and open a draft PR
argument-hint: [FILES=<paths>] [PR_TITLE="<title>"]
---

Create a branch named `dev/<feature_name>` for this work.
If files are specified, stage them first: $FILES.
```

**Status:** deprecated. Codex recommends migrating to Skills, which support implicit invocation and bundled resources.

### Slash commands

Built-in: `/model`, `/status`, `/compact`, `/fast`, `/personality`, `/plan`, `/review`, `/fork`, `/approvals`, `/apps`, `/mention`, `/feedback`, `/logout`, `/quit`.

Custom commands come from custom prompts (legacy) or skills (current).

### Skills

Same open Agent Skills framework as Claude Code. Structure:

```
.agents/skills/my-skill/
├── SKILL.md
├── scripts/
└── references/
```

Scope locations (Codex detects by folder):
- `$CWD/.agents/skills/` — project/repo.
- `$REPO_ROOT/.agents/skills/` — repo root.
- Personal: via `$skill-creator`.

SKILL.md frontmatter same as Claude:
```yaml
---
name: my-skill
description: Strict scope description.
allow_implicit_invocation: true
---
```

Skills can declare MCP dependencies in `agents/openai.yaml` so Codex auto-wires them.

### Subagents

Native support since early 2026. Each subagent has its own model and tool config. Codex spawns them only on explicit request — `[agents]` table in `config.toml` defines roles. Consumes more tokens than single-agent runs, but isolates context pollution.

### Hooks (experimental, v0.114+)

Configured in `config.toml` under `[hooks]`. Three handler types (command, prompt, agent — same as Claude). Events:
- `SessionStart` — stdout feeds into model context.
- `UserPromptSubmit`
- `PreToolUse`, `PostToolUse`
- `PermissionRequest`
- `Stop` — can block until validation passes (useful for "keep working until tests green" loops).

Async hooks supported (command handlers only, `async = true`). Default timeouts: command none, prompt 30s, agent 60s.

```toml
[[hooks]]
event = "AfterToolUse"
command = "echo 'Tool completed' >> /tmp/codex-log.txt"

[[hooks]]
event = "SessionStart"
command = "echo 'Current date: $(date +%Y-%m-%d)'"
```

Hooks are **disabled during Guardian review sessions** (v0.121+) so pre/post-tool hooks don't interfere with the review subagent.

**Windows:** hooks currently not supported. Third-party bridges like `codex-hooks` can reuse Claude Code hook configs via session JSONL monitoring.

### Plugins

Launched as a native feature. Manifest: `.codex-plugin/plugin.json`. Plugins can bundle skills, MCP servers, slash commands, hooks.

```bash
# Via built-in skill
$plugin-creator
```

Marketplaces are JSON catalogs — users can add multiple marketplaces (enterprise, team, public). Codex plugin system is explicitly designed to work across CLI, IDE extension, and web surfaces.

### config.toml — the master switchboard

Unlike Claude (settings.json) and Cursor (settings UI + many JSON files), Codex concentrates almost all config in TOML files:

**Precedence (highest to lowest):**
1. Cloud-managed requirements.
2. MDM `requirements_toml_base64`.
3. System `/etc/codex/requirements.toml`.
4. User `~/.codex/config.toml`.
5. Project `.codex/config.toml` (requires project trust).
6. CLI `--config` overrides.

Project configs require explicit trust:
```toml
[projects."/absolute/path/to/project"]
trust_level = "trusted"
```

Sandbox modes: `read-only`, `workspace-write`, `danger-full-access`. Approval policies: `untrusted`, `on-request`, `never`, or `{ granular = {...} }` for per-category rules.

---

## Cross-tool cheat sheet

### What maps to what

| If you want... | Claude Code | Cursor | Codex |
|---|---|---|---|
| Team-committed instructions | `CLAUDE.md` | `.cursor/rules/*.mdc` or `AGENTS.md` | `AGENTS.md` |
| Personal global defaults | `~/.claude/CLAUDE.md` | User Rules (Settings) | `~/.codex/AGENTS.md` |
| Personal per-project (uncommitted) | `CLAUDE.local.md` | `.cursor/rules/personal.mdc` + gitignore (DIY) | `AGENTS.override.md` (replaces parents, semantics differ) |
| Subdirectory-specific rules | `.claude/rules/*.md` with `paths:` frontmatter | `.cursor/rules/*.mdc` with `globs:` | Nested `AGENTS.md` in subdirectories |
| Reusable workflow (explicit `/` trigger) | Skill or legacy `.claude/commands/` | `.cursor/commands/*.md` | Skill or legacy `~/.codex/prompts/` |
| Reusable workflow (auto-discovered) | Skill | Skill | Skill |
| Deterministic pre/post-tool enforcement | Hook (`PreToolUse`/`PostToolUse`) | Hook (`beforeShellExecution`, `afterFileEdit`) | Hook (`PreToolUse`/`PostToolUse`) |
| LLM-based semantic check at runtime | Prompt/agent hook | Not supported (command only) | Prompt/agent hook |
| Bundled reusable package | Plugin | Plugin (`.cursor-plugin/plugin.json`) | Plugin |
| Isolated parallel work | Subagent | Subagent | Subagent |

### Source-of-truth strategies for multi-tool repos

**Pattern 1: `AGENTS.md` as canonical, tool-specific thin wrappers**
```
./AGENTS.md                    # canonical, read by Cursor and Codex natively
./CLAUDE.md                    # contains: @AGENTS.md
./CLAUDE.local.md              # personal, gitignored
```

Works well because Cursor and Codex both read `AGENTS.md` natively; Claude just needs a one-line import.

**Pattern 2: Skill-first**

Since Claude, Cursor (2.4+), and Codex all use `SKILL.md` with compatible (not identical) frontmatter, authoring a skill once and symlinking into each tool's expected directory lets all three pick it up:

```
./skills/<skill-name>/SKILL.md
# Symlinks:
./.claude/skills/<skill-name>  -> ../../skills/<skill-name>
./.cursor/skills/<skill-name>  -> ../../skills/<skill-name>
./.agents/skills/<skill-name>  -> ../../skills/<skill-name>
```

Watch for frontmatter differences: Codex uses `allow_implicit_invocation`, Claude uses metadata only. Test each one.

**Pattern 3: Cross-tool hook reuse**

`codex-hooks` (third-party) reuses `~/.claude/settings.json` hook definitions by monitoring Codex's session JSONL and mapping events. Not a general solution but shows the appetite for this convergence.

### Philosophical differences

| Axis | Claude Code | Cursor | Codex |
|---|---|---|---|
| Config locus | JSON settings, markdown files | Settings UI, project dirs | TOML, strong file hierarchy |
| Hook handler richness | Command + HTTP + Prompt + Agent | Command only | Command + Prompt + Agent |
| Package management | Full marketplace + plugins | Marketplace + plugins (also community directory) | Marketplace + plugins |
| Override semantics | Additive layers (local + committed) | Layered + merged by precedence | Override files *replace* parents |
| Skill spec maturity | Originator, most polished | Adopted Jan 2026, matches spec | Adopted, same spec, auto-install of MCP deps |
| Sandbox depth | Permission system | Cursor runs in editor | macOS seatbelt, Linux bubblewrap |

### Where each tool shines for platform builders

- **Claude Code** — if you want deterministic CI/CD-grade quality gates, the four hook handler types + async hooks are the most expressive. Progressive disclosure makes it scalable to hundreds of skills without context blow-up.
- **Cursor** — if you want the best UX layer for humans reading/writing rules (Settings UI, MDC format is readable, `/` palette). Best for "team consistency" use cases since Team Rules are enforced.
- **Codex** — if you want strong machine-readable configuration with enterprise deployment (MDM policies, requirements layers, sandbox policies). The `AGENTS.md` hierarchy + `AGENTS.override.md` handles monorepo edge cases most cleanly.

---

## Gotchas & sharp edges

1. **Cursor `.mdc` frontmatter is not real YAML** — strings without quotes, or your rules will parse weird. Quoting strings gets you literal `"foo"` back.
2. **Cursor glob rules don't trigger on agent edits** — only when the user explicitly attaches or mentions a matching file. This surprised a lot of people in 2025.
3. **Claude Code `CLAUDE.md` loads in full, always** — no truncation, so long files bloat every session. Keep it short and use `@import` or `.claude/rules/` for modular depth.
4. **Codex `AGENTS.override.md` is replace, not merge** — if you're migrating from `CLAUDE.local.md` expecting additive behavior, you'll lose parent instructions.
5. **Codex hooks disabled on Windows** and during Guardian review.
6. **Deprecated paths still work** — `.cursorrules`, `.claude/commands/`, `~/.codex/prompts/` all still function. But the newer skill-based replacements get better treatment from the agent (implicit invocation, progressive disclosure).
7. **Skill descriptions are load-bearing** — all three tools use the description field to decide whether to load a skill. Vague descriptions = unused skills. Be specific about scope and trigger conditions.
8. **Hook ordering across sources**:
   - Claude: plugin hooks can be force-enabled via managed settings.
   - Cursor: user + enterprise + project merge (all run).
   - Codex: identical handlers dedup automatically; concurrent command hooks can't block each other.
9. **Subagent semantics vary** — Claude's subagents are invoked autonomously via the Task tool; Codex requires explicit user request; Cursor's are more tightly integrated with the main agent loop.
10. **No Cursor personal slash commands** — `.cursor/commands/` is project-only. Personal shortcuts need the workaround of a shared rules file.

---

## References

- **Claude Code docs:** https://docs.claude.com/en/docs/claude-code/overview
- **Claude Code memory:** https://code.claude.com/docs/en/memory
- **Claude hooks reference:** https://code.claude.com/docs/en/hooks
- **Claude skills:** https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- **Claude plugins:** https://code.claude.com/docs/en/discover-plugins
- **Cursor rules:** https://cursor.com/docs/context/rules
- **Cursor hooks:** https://cursor.com/docs/hooks.md
- **Cursor 2.4 (skills + subagents):** https://cursor.com/changelog/2-4
- **Cursor plugins reference:** https://cursor.com/docs/reference/plugins
- **Cursor marketplace overview:** https://cursor.com/blog/marketplace
- **Cursor skills:** https://cursor.com/docs/skills
- **Codex AGENTS.md:** https://developers.openai.com/codex/guides/agents-md
- **Codex hooks:** https://developers.openai.com/codex/hooks
- **Codex skills:** https://developers.openai.com/codex/skills
- **Codex plugins:** https://developers.openai.com/codex/plugins/build
- **Codex config reference:** https://developers.openai.com/codex/config-reference
- **AGENTS.md spec:** https://agents.md
