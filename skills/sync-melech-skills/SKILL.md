---
name: sync-melech-skills
description: >-
  Sync every AdirD/agent-shell-hamelech skill into the user-global
  ~/.agents/skills lock and fan it out to every coding agent. Use when the
  user says sync-melech-skills, sync melech skills, melech sync, keep my
  melech skills up to date, or asks whether hamelech skills are installed.
  sync-melech-skills list is dry catalog only.
---

# Sync Melech Skills — global library sync

You are the meta-skill for
[`AdirD/agent-shell-hamelech`](https://github.com/AdirD/agent-shell-hamelech).

Canonical source (double `l` in `shell`):

```text
AdirD/agent-shell-hamelech
```

Managed with Vercel's Skills CLI
([`vercel-labs/skills`](https://github.com/vercel-labs/skills)).

The old skill name was `melech`. This skill is `sync-melech-skills`. If the
global lock still has `melech`, remove it after this one is installed:
`npx skills remove melech -g -y`.

## How the user invokes this

| They say | You do |
|---|---|
| `sync-melech-skills`, `sync melech skills`, `melech sync`, keep skills up to date | **Apply.** Install missing skills and update stale ones. |
| `sync-melech-skills list`, `melech list`, `melech status` | **Dry catalog** only. Do not install. |


## Hard rules

1. **Global only.** Every `npx skills` / `npm exec` call uses `-g`. Never
   install into a repo, `./.agents`, `./.cursor`, or any project lock.
2. **Every agent.** Adds use `-a '*'`. Do not target Cursor-only or
   Claude-only unless the user names one agent.
3. **Non-interactive.** Always `-y`. Never run a promptable skills command.
4. **Never run `npx skills check`.** It aliases `update` and can mutate
   non-melech skills. Status = bundled `status.py`. Apply = bundled `sync.py`.
5. **Melech skills only.** Do not `skills update -g` with no names — that
   upgrades unrelated global skills.
6. Run CLI calls with `cwd` = the user's home (the script already does this)
   so a random git repo cannot flip scope to project.

## Apply (`sync-melech-skills` / `melech sync`)

Resolve this skill directory, then:

```bash
python3 <skill-dir>/scripts/sync.py
```

That script:

1. Reads the remote catalog via `status.py --json`.
2. Plans work for remote skills that are `new`, `outdated`, `untracked`,
   `broken-source`, or missing `~/.agents/skills/<name>/SKILL.md`.
3. For each: `skills update <name> -g -y` when outdated, then
   `skills add AdirD/agent-shell-hamelech --skill <name> -g -y -a '*'`.
4. Leaves `remote-gone` skills installed. Does not uninstall.

If `npm` is missing, stop and tell the user to install Node.js.

After apply, print the sync summary (planned / applied / failed). If anything
failed, show that skill and the CLI error. Do not pretend the library is
current.

Re-run `python3 <skill-dir>/scripts/status.py` only if they also want the
full catalog cards.

## Dry catalog (`sync-melech-skills list`)

```bash
python3 <skill-dir>/scripts/status.py
python3 <skill-dir>/scripts/status.py --json
```

Repo checkout:

```bash
python3 skills/sync-melech-skills/scripts/status.py
```

Needs `gh` auth (preferred) or `GITHUB_TOKEN` / `GH_TOKEN`.

Remote-first. Every skill on GitHub is a row. Versions are skill-folder tree
SHAs in `~/.agents/.skill-lock.json`, not semver.

| Status | Meaning | Apply does |
|---|---|---|
| `new` | on remote, not in the global lock | `add -g -y -a '*'` |
| `outdated` | lock SHA differs from remote | `update -g -y`, then `add -g -y -a '*'` |
| `current` | lock matches remote and `~/.agents/skills/<name>` exists | skip |
| `broken-source` | lock uses typo `AdirD/agent-shel-hamelech` | re-`add` with the canonical slug |
| `untracked` | installed, no local hash | re-`add` |
| `remote-gone` | local only, deleted upstream | skip (do not remove) |

## Voice


Sharp and short. Verdict first (N installed, M updated, K failed), then
names. Do not dump the full catalog after a clean sync unless they asked
for `list`.
