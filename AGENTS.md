# Repo Rules

## Maintenance Rule

Whenever adding, removing, or renaming anything under `skills/`, you must also update `README.md`.

At minimum, keep the matching README section accurate:

- skill name
- short description
- install command
- when-to-use notes if behavior changed

Do not leave the repo in a state where the catalog in `README.md` is stale.

## Before You Commit

- Do not stage gitignored local agent state: `.claude/`, `.codex/`, `.cursor/`, `.entire/`, `.gemini/`, `.serena/`, `.superset/`, `.ops/`.
- Do not put secrets, tokens, private keys, or personal/work emails in tracked files.
- Skill examples and diagrams must use generic names. No real employer stack, internal service names, or production endpoint paths that could fingerprint a workplace.

## Before You Push

Run the repo audit script and fix anything it reports:

```bash
bash scripts/pre-push-audit.sh
```

Do not push until it passes.

The script checks:

- staged paths are not under gitignored agent/ops dirs
- tracked files do not match common secret patterns
- unpushed commits do not use work/internal author emails
- `origin` has only `main` (no stray side branches from agent tooling)
- `entire` auto-push hooks are not installed

Optional local extensions live in `.ops/pre-push-audit.local` (gitignored). Copy from `scripts/pre-push-audit.local.example` if you maintain extra patterns such as employer domains.

Optional git hook (runs the same audit on every push):

```bash
chmod +x scripts/pre-push-audit.sh
ln -sf ../../scripts/pre-push-audit.sh .git/hooks/pre-push
```

## Before Making the Repo Public

Day-to-day pushes use `scripts/pre-push-audit.sh`. The full public-release runbook (history, GitHub settings, incident notes) lives locally under `.ops/` and is gitignored.

If `.ops/release-public.sh` exists locally, run the audit first, then:

```bash
bash .ops/release-public.sh
```
