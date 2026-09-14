# Install The Gardener As A Routine

Set up the PR Gardener on the current repo now. Assume `gh` is authenticated.
Default to every 2 hours.

Require the GitHub login whose authored PRs should be tended. If the caller did
not provide it, ask exactly that one setup question; do not infer it from the
system `gh` identity because scheduled hosts may authenticate as an app.

Create the schedule through the current host:

| Host | Scheduling feature |
|---|---|
| [Cursor](https://cursor.com/docs/cloud-agent/automations) | Run `/automate` |
| [Claude Code](https://code.claude.com/docs/en/routines) | Run `/schedule` |
| [Codex](https://developers.openai.com/codex/app/automations) | Ask Codex to create an Automation with the cadence |
| [Antigravity (`agy`)](https://antigravity.google/docs/slash-commands/) | Run `/schedule "<cron>" <prompt>` |

Schedule this prompt:

```text
Required run input: GARDENER_AUTHOR=<github-login>
npx -y skills add AdirD/agent-shell-hamelech --skill melech-pr-gardener -g -y -a '*'
Read ~/.agents/skills/melech-pr-gardener/SKILL.md and follow it exactly.
```

Replace `<github-login>` with the literal login before creating the schedule.
Confirm the author and cadence after creating it. Do not run a test pass unless
asked.
