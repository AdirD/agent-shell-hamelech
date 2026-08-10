---
name: melech
description: >-
  Remote-first catalog of AdirD/agent-shell-hamelech ("melech") skills: for
  each remote skill show name, description, installed y/n, where (global /
  project / workspace → agents), local version, remote version, update
  available y/n, and the install/update command — including skills that are new
  on GitHub and not installed locally. Use when the user says "melech",
  "melech list", "melech list skills", "list melech skills", or asks what
  hamelech skills exist remote vs local, whether to update, or how to install
  via `npx skills`.
disable-model-invocation: true
---

# Melech — remote ↔ local skill catalog

## How the user invokes this

Treat these as the same request — run the catalog:

- `melech`
- `melech list`
- `melech list skills`
- `list melech skills`
- `melech status` / `melech sync`

You are the meta-skill for
[`AdirD/agent-shell-hamelech`](https://github.com/AdirD/agent-shell-hamelech).

Job: **show the remote catalog, diff it to local, recommend commands**.
Do not silently install or update.

Canonical source (double `l` in `shell`):

```text
AdirD/agent-shell-hamelech
```

Managed with Vercel's Skills CLI
([`vercel-labs/skills`](https://github.com/vercel-labs/skills)).

## Hard rules

1. **Never run `npx skills check`.** It aliases `update` and applies changes.
   Dry status = bundled script only.
2. **Never install/update unless the user explicitly asks.** Show the catalog,
   then wait.
3. Prefer `scripts/status.py` over hand-rolled scraping.
4. Scope to melech skills only unless the user asks for a full inventory.

## Workflow

```text
Melech catalog:
- [ ] 1. Run scripts/status.py
- [ ] 2. Lead with summary (remote count, installed, new, updates)
- [ ] 3. Show per-skill cards (name, description, installed, where, versions, update, command)
- [ ] 4. Call out NEW skills and UPDATE rows first
- [ ] 5. Show workflow bundles (recipes) with step readiness ✓/✗
- [ ] 6. Mutate only on approval, using each row's command
```

### Run the script

Resolve the skill root that contains this `SKILL.md`, then:

```bash
python3 scripts/status.py
python3 scripts/status.py --json
```

Repo checkout:

```bash
python3 skills/melech/scripts/status.py
```

Needs `gh` auth (preferred) or `GITHUB_TOKEN` / `GH_TOKEN`.

### What to present

Remote-first. Every skill on GitHub is a row, even if not installed.

Per skill, surface:

| Field | Meaning |
|---|---|
| name | skill id |
| description | from remote `SKILL.md` frontmatter |
| installed | Y / N (tracked in global skills lock) |
| where | install locations: `global` / `project` / `workspace` → agents @ path |
| local version | short folder SHA from lock, or `-` |
| remote version | short folder SHA on `main` |
| update available | Y / N |
| status | `new` / `current` / `outdated` / `broken-source` / … |
| command | exact `npx skills …` to install/update/reinstall that skill |

`where` scopes:
- `global` — user-level install (`npx skills add -g`), shared across projects
- `project` — installed into this project's agent skill dirs
- `workspace` — bare `skills/<name>` checkout discovery (authoring tree, not an install)

Statuses:

| Status | Meaning | `command` does |
|---|---|---|
| `new` | on remote, not installed | `add` |
| `outdated` | installed, remote SHA differs | `update` |
| `current` | installed and matches remote | `add` (reinstall if asked) |
| `broken-source` | lock uses typo `AdirD/agent-shel-hamelech` | `add` with correct slug |
| `untracked` | installed, no local hash | `add` |
| `remote-gone` | local only, deleted upstream | `remove` |

Lead with: remote count, installed, **new**, **updates available**. Then the
per-skill list (include each row's `command`). Versions are folder tree SHAs
(Skills CLI lock), not semver — say that once, briefly.

### Workflow bundles

Always include the **workflow bundles** section from the script output.
Bundles are journey recipes from the README (not installable skills):

- Product discovery
- Better engineering
- Existing-plan review
- Shipping

For each bundle show the flow, when to use it, and which steps are installed
(✓/✗). If steps are missing, the script already prints their install commands.

When the user says e.g. "install podcast" / "update the outdated ones" /
"install the missing steps for product discovery", run the matching
`command`s from the catalog. Do not invent different install lines. Prefer
named commands over blind `npx skills update -g`. After any mutation, re-run
the script and show the new summary.

## Voice

Sharp and short. Verdict first (N new, M updates), then the catalog, then
commands.
