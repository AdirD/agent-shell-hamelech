# Moved lines fixture

Requirement: fix `ReferenceError: Cannot access 'config' before initialization`
thrown when the app starts. Nothing else was requested.

Repository facts:

- `./polyfills` installs a `globalThis.fetch` implementation for older runtimes.
- `./api-client` reads `globalThis.fetch` once, at module import time.
- Both files are unchanged in this diff.

Treat `change.diff` as the uncommitted working diff.
