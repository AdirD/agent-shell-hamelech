# Install The Gardener As A Routine

Use this when the user wants the gardener to run on a schedule in the current
repo. Assume `gh` is already authenticated. Ask only for the cadence if missing.

Create the schedule through the current host:

| Host | Scheduling feature |
|---|---|
| [Cursor](https://cursor.com/docs/cloud-agent/automations) | Run `/automate` |
| [Claude Code](https://code.claude.com/docs/en/routines) | Run `/schedule` |
| [Codex](https://developers.openai.com/codex/app/automations) | Ask Codex to create an Automation with the cadence |
| [Antigravity (`agy`)](https://antigravity.google/docs/slash-commands/) | Run `/schedule "<cron>" <prompt>` |

Use this prompt:

```text
Tend the open pull requests in the current repo, one pass.

First install the latest playbook non-interactively:

  npx -y skills add AdirD/agent-shell-hamelech --skill melech-pr-gardener -g -y -a '*'

Then read ~/.agents/skills/melech-pr-gardener/SKILL.md and follow it exactly,
then stop after one pass.
```

Confirm the cadence after creating it. Do not run a test pass unless asked.
