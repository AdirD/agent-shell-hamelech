---
name: melech-sync-skills
description: Sync this skill library globally across supported coding agents.
---

# Sync Melech Skills — global library sync

You are the meta-skill for
[`AdirD/agent-shell-hamelech`](https://github.com/AdirD/agent-shell-hamelech).

Canonical source (double `l` in `shell`):

```text
AdirD/agent-shell-hamelech
```

Managed with Vercel's Skills CLI
([`vercel-labs/skills`](https://github.com/vercel-labs/skills)). This skill
ships no scripts — the CLI does the work, you just run it correctly.

The old skill names were `melech` and `sync-melech-skills`. This skill is
`melech-sync-skills`. If the global lock still has either old name, remove it
after this one is installed: `npx skills remove melech -g -y` and/or
`npx skills remove sync-melech-skills -g -y`.

## How the user invokes this

| They say | You do |
|---|---|
| `melech-sync-skills`, `sync melech skills`, `melech sync`, keep skills up to date | **Apply.** Run the sync command below. |
| `melech-sync-skills list`, `melech list`, `melech status` | **Dry catalog** only. Do not install. |

## Apply

One command. Run it from the user's home so the CLI cannot flip to project
scope:

```bash
cd ~ && npx skills add AdirD/agent-shell-hamelech --all -g
```

`--all` expands to `--skill '*' --agent '*' -y`, scoped to the named repo. It
installs new skills, refreshes existing ones, and needs no confirmation. It
does not touch global skills from other sources.

Takes roughly 30 seconds — it refreshes every skill, not just stale ones.
There is no cheaper "only what changed" mode worth maintaining.

If `npm` is missing, stop and tell the user to install Node.js.

### Reading the output

Two things look like failures and are not:

- `✗ <skill> → Eve` and `✗ <skill> → PromptScript` on every skill. Those two
  agents do not support global installs at all. The command still exits 0 and
  prints `Done!`. Never report these as a failed sync.
- No `~/.cursor/skills` or `~/.codex/skills` entries appear. Cursor, Codex,
  Amp, Zed, Warp, OpenCode, and friends are *universal* agents in the CLI
  registry: they read `~/.agents/skills` directly, so a global install writes
  the canonical dir and skips the per-agent symlink. Agents with their own
  dir (Claude Code, Droid, Continue, Goose, Roo, ~40 more) get real symlinks.

A newly installed skill will not show up in an already-open Cursor session —
the skill list is snapshotted at session start. Tell the user to open a new
session, do not re-run the sync.

Nothing is ever uninstalled. A skill deleted from remote stays installed and
keeps its lock entry until it is removed by name:
`npx skills remove <name> -g -y`.

## Dry catalog (`melech-sync-skills list`)

What is on remote, with descriptions:

```bash
cd ~ && npx skills add AdirD/agent-shell-hamelech -l
```

What is installed globally (`--json` for machine-readable):

```bash
cd ~ && npx skills list -g
```

Diff the two by name to answer "what am I missing". There is no
remote-versus-lock version comparison — the lock stores skill-folder git tree
SHAs, not semver, and re-running apply is cheaper than computing the diff.

## Hard rules

1. **Global only.** Every call passes `-g`. Without it the CLI auto-detects
   and picks project scope whenever the cwd is a project, writing a repo lock.
2. **Home cwd.** Run from `~`, never from a repo checkout.
3. **Name the repo.** Never run bare `npx skills update -g` or
   `npx skills check` — both mutate unrelated global skills from other
   sources. Naming the repo in `add --all` is what keeps this melech-only.
4. **Never `npx skills list` without `-g` from inside a repo.** One registry
   agent (OpenClaw) declares a bare `skills` directory, so a project-scope
   list reports this repo's own authoring folders as installs. It looks like
   the sync went into the repo. It did not.
5. **Every agent.** `--all` covers this. Do not narrow to one agent unless
   the user names one.

## Voice

Sharp and short. Verdict first (installed / refreshed / genuinely failed),
then names. Do not dump the catalog after a clean sync unless they asked for
`list`. Do not recite the Eve and PromptScript noise.
