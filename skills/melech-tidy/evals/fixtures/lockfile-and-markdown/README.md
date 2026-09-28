# Lockfile and Markdown fixture

Requirement: the upload button should retry once on a network failure. No
dependency changes and no documentation changes were requested.

Repository facts:

- The project uses npm. `package-lock.json` is tool-generated and CI runs
  `npm ci`, which installs exactly what the lockfile resolves.
- The agent ran `npm install` with a newer npm version during the session.
- The agent's editor rewraps Markdown on save.
- CI runs `eslint` and `npm test`. There is no formatter check.

Treat `change.diff` as the uncommitted working diff.
