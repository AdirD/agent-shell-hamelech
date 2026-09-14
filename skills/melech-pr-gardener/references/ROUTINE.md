# Install The Gardener As A Routine

Set up the PR Gardener on the current repo now. Assume `gh` is authenticated.
Do not ask setup questions; default to every 2 hours.

Create the schedule through the current host:

| Host | Scheduling feature |
|---|---|
| [Cursor](https://cursor.com/docs/cloud-agent/automations) | Run `/automate` |
| [Claude Code](https://code.claude.com/docs/en/routines) | Run `/schedule` |
| [Codex](https://developers.openai.com/codex/app/automations) | Ask Codex to create an Automation with the cadence |
| [Antigravity (`agy`)](https://antigravity.google/docs/slash-commands/) | Run `/schedule "<cron>" <prompt>` |

Schedule this prompt:

```text
npx -y skills add AdirD/agent-shell-hamelech --skill melech-pr-gardener -g -y -a '*'
Read ~/.agents/skills/melech-pr-gardener/SKILL.md and follow it exactly.
```

Confirm the cadence after creating it. Do not run a test pass unless asked.
