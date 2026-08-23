---
name: debug-mode
description: Run an evidence-first debugging loop with temporary runtime probes and a local Portless-backed JSONL collector. Two reproduction modes: manual (user holds the wheel, then replies proceed) and autopilot (agent drives the user's already-open Chrome via Chrome DevTools MCP --autoConnect). Use when a user can reproduce a UI, API, desktop, or integration bug but static inspection, tests, and existing logs do not reveal the failing runtime path, especially when the user asks for debug mode, autopilot, live browser control, dynamic request logs, instrumentation, or a reproduce-and-proceed workflow.
---

# Debug Mode

Treat the current task as an active debugging session. Diagnose from runtime
evidence before proposing a fix.

For the intended first-use, reproduction, iteration, verification, and later-use
experience, read [DEVELOPER_JOURNEY_EXAMPLE.md](references/DEVELOPER_JOURNEY_EXAMPLE.md)
and use it as the interaction model. For autopilot attach, read
[LIVE_BROWSER.md](references/LIVE_BROWSER.md) when that mode starts. Chrome
setup is the official M144 auto-connect flow in
[CHROME_DEVTOOLS_MCP.md](references/CHROME_DEVTOOLS_MCP.md).

## Guardrails

- Keep the collector local. Do not enable Portless `--tailscale`, `--funnel`,
  `--ngrok`, LAN mode, or any other remote exposure.
- Never collect credentials, tokens, cookies, authorization headers, personal
  data, full request bodies, or unrelated application state. Prefer booleans,
  counts, IDs already safe for development, enum values, and narrow summaries.
- Add the fewest probes that distinguish the current hypotheses. Start with at
  most five unless the control flow genuinely requires more.
- Make probes non-blocking and failure-isolated so collector failure cannot
  alter product behavior.
- Mark every temporary edit with `DEBUG_MODE:<session-id>:<probe-id>` and keep a
  list of touched files for cleanup.
- Do not fix the bug before the evidence identifies a cause, unless the user
  explicitly asks to skip diagnosis.
- Stop only this session. Never run `portless proxy stop`, `portless clean`, or
  broad process-kill commands.
- When driving Chrome, attach only. Never `state save` cookies or tokens, never
  collect credentials from the page, never quit the user's Chrome, and never
  close tabs you did not open. Do not tunnel CDP through Portless or any remote
  exposure.

## Start A Session

1. Inspect the failing path, current logs, and relevant tests. State one to
   three concrete hypotheses and what observation would distinguish them.
2. Locate this installed skill directory and confirm both `python3` and
   `portless` are available. If Portless is missing, stop and tell the user to
   install the official Vercel Labs CLI with `npm install -g portless`. Do not
   silently substitute another tunnel or server.
3. Source the bundled command once so the short `dm` verb is available for the
   rest of this session (the shell keeps it across later calls):

   ```bash
   source <skill-dir>/scripts/dm.sh
   ```

   Every launcher call below uses `dm`, which is identical to
   `python3 <skill-dir>/scripts/debug_session.py`. If `dm` is ever undefined in a
   later step (fresh shell), re-source `dm.sh` or fall back to the full path.
4. If this machine has not used Portless before, run `portless doctor`. Follow
   its local trust/setup guidance before starting the background session.
5. Start the bundled collector:

   ```bash
   dm start
   ```

   Save the returned `session_dir`, `session_id`, `log_endpoint`, `events_file`,
   and `backend_port`. The launcher copies the lean server skeleton into a new
   temporary directory. Portless assigns a different free backend port and a
   unique local route for every session.
6. Verify the returned `health_url` before editing application code.

## Add Dynamic Request Probes

Place probes only where they can confirm or eliminate a hypothesis: branch
entries, values immediately before a transformation, boundary inputs/outputs,
and error paths. Give each a stable descriptive ID.

POST a small JSON object to the session's `log_endpoint`:

```json
{
  "run": "run-1",
  "probe": "checkout-before-submit",
  "hypothesis": "disabled state is stale",
  "data": {
    "isDisabled": true,
    "itemCount": 2
  }
}
```

For browser JavaScript, use a fire-and-forget request and swallow collector
errors locally:

```js
// DEBUG_MODE:<session-id>:checkout-before-submit
void fetch("<log-endpoint>", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    run: "run-1",
    probe: "checkout-before-submit",
    hypothesis: "disabled state is stale",
    data: { isDisabled, itemCount: items.length },
  }),
}).catch(() => {});
```

Adapt the request idiom to the target language. Preserve the same payload
shape, marker, narrow data selection, and failure isolation. Do not log whole
objects when a few fields answer the question.

Run the cheapest compile, type, or syntax check needed to ensure the temporary
instrumentation itself did not break the workflow.

## Pick A Reproduction Mode

Same collector and probes either way. Only who drives the repro changes.

- **Manual** — the user holds the wheel. You instrument, tell them the exact
  clicks, then stop until they reply `proceed`.
- **Autopilot** — you drive their already-open Chrome end-to-end with
  Chrome DevTools MCP `--autoConnect` (same tabs, same logins). They only
  enable remote debugging and click Allow. If this host is missing that
  MCP, you write the official config with `dm mcp-setup` and wait for a
  reload so the host can start the server.

Choose once, then announce it in the user-facing message:

1. User said they will reproduce, hold the wheel, or reply `proceed` →
   **manual**.
2. User said autopilot, drive my browser, already logged in, or do it for me →
   **autopilot**.
3. UI bug and they did not pick → announce both modes in one short message
   and wait. Do not attach and do not hand them a `proceed` script until they
   answer.
4. Not a UI bug, or the tab looks like production you should not touch →
   **manual**.

Never silently attach. Before any Chrome DevTools MCP call, tell the user
they are in autopilot and what they must do in Chrome.

## Autopilot

Keep probes in place. Snapshots are extra evidence, not a substitute for
`dm logs`. Read [LIVE_BROWSER.md](references/LIVE_BROWSER.md) and
[CHROME_DEVTOOLS_MCP.md](references/CHROME_DEVTOOLS_MCP.md).

1. Check whether Chrome DevTools MCP tools are already available in this
   session. Then run the bundled setup (idempotent):

   ```bash
   dm mcp-setup
   ```

   That inspects known host MCP configs, writes the official
   `chrome-devtools-mcp@latest --autoConnect` entry when it is missing, and
   prefetches the npm package. It does not inject tools into a live host;
   the host still has to spawn the server.

   - Tools already present and `ready: true` → continue.
   - `reload_required: true` → tell the user to reload the `chrome-devtools`
     MCP server (or restart the host), then wait. Do not attach to a
     profile that is missing `--autoConnect`.
   - `ready: false` → show the official snippet from the command output and
     switch to [Manual](#manual) unless they want the `dm browser-check`
     fallback.

   Do not silently switch to Playwright, Puppeteer, a fresh empty Chrome, a
   cloud browser, or a custom extension.
2. Before the first MCP call, tell the user verbatim:

   > Autopilot is on. I will drive the tab you already have open.  
   > One-time: open chrome://inspect/#remote-debugging and enable Allow
   > remote debugging for this browser instance (Chrome 144+).  
   > When Chrome prompts, click Allow. A “controlled by automated test
   > software” banner is expected. I will not quit Chrome or close other tabs.

   Then wait only if they have not confirmed they can click Allow. If they
   already said to go, list pages and keep those steps visible.
3. Discover pages through Chrome DevTools MCP. Select the existing app tab.
   Do not open a new URL unless the repro needs a fresh navigation. Do not
   close Chrome or other tabs. Do not close the last tab.
4. Snapshot, then drive the workflow with click / fill / type on snapshot
   uids. If they already selected a node in the Elements panel or a request
   in the Network panel, start there.
5. If attach fails, print the inspect-page + Allow steps and switch to
   [Manual](#manual). Use `dm browser-check` only when this host has no
   Chrome DevTools MCP at all.
6. After one reproduction attempt, read `dm logs` the same as on `proceed`.
   Do not claim a reproduction from a snapshot alone.

## Manual

Use this path when the user holds the wheel, autopilot is unavailable or
denied, or you should not touch the open tabs. Tell the user:

1. Debug mode is active in **manual**. They hold the wheel.
2. The exact workflow to perform, including any reset or starting state.
3. Which visible outcome identifies the bug.
4. To reply exactly `proceed` after one reproduction attempt.

Then stop. Do not poll the event file or claim a reproduction before the user
replies.

## Inspect On `proceed`

After an autopilot reproduction, use this same command and the same
outcomes without waiting for `proceed`.

Read the evidence with:

```bash
dm logs <session-dir> --run run-1
```

Correlate event order and values against the stated hypotheses, then choose
one outcome:

- **Reproduced and conclusive:** explain the observed causal chain, implement
  the smallest root-cause fix, and verify it. Keep probes only if one user
  rerun is still needed to validate the fix.
- **Reproduced but inconclusive:** say what the evidence ruled out, revise the
  hypothesis, add or move only the probes needed for `run-2`, and ask for the
  precise workflow again.
- **No application events:** check session status (`dm status <session-dir>`) and send one synthetic event
  to distinguish collector delivery failure from an unvisited code path. Check
  browser CSP/CORS or environment reachability when relevant, then repair the
  instrumentation and retry.
- **Workflow did not reproduce:** record that result, adjust the starting state
  or probe placement, increment the run ID, and retry without pretending the
  bug was observed.

Do not equate correlation with cause. Cite the specific probe sequence and
values that support the next action.

## Doctor: Monitor Live Sessions

To inspect every debug-mode collector on the machine at once, run the live TUI:

```bash
dm doctor    # or bare `dm`
```

It scans the temp root for all `debug-mode-*` sessions and shows, per session, a
health status derived from the process state plus the collector's `/health`
endpoint:

- **running** (green): launcher and collector processes are alive and `/health`
  returns 200.
- **degraded** (yellow): processes are alive but `/health` is unreachable or
  non-200 (hung or wedged port). `starting` means the collector metadata has not
  been written yet.
- **dead** (red): the launcher or collector process is gone.

The detail pane live-tails the selected session's `events.jsonl`, auto-scrolling
to the newest event, shows the live entry count, and surfaces the last error
line from `runtime.log` when the collector crashed or is throwing.

Keys: `↑`/`↓` or `j`/`k` to move, `x` to kill the selected session (stops its
processes and deletes its temp directory, same as `stop`; asks `y`/`n` first),
`r` to force a refresh, `q` to quit. Killing only ever targets a validated
`debug-mode-*` session directory; it never issues a broad process kill.

For scripting or when no TTY is available, use `dm doctor --once` to print a
one-shot JSON snapshot of all sessions instead of launching the TUI.

### Installing `dm` persistently for the user

The skill sources `dm.sh` for its own session, but the user gets `dm` in their
own terminals only after a one-time install. Offer it once per machine:

```bash
sh <skill-dir>/scripts/install-dm.sh
```

This appends a single `source <skill-dir>/scripts/dm.sh` line to the user's
shell rc (`~/.zshrc` or `~/.bashrc`, auto-detected; pass a path to override) and
is idempotent. After reloading the shell:

- `dm` — open the doctor TUI
- `dm help` — list every command
- `dm start`, `dm status <dir>`, `dm logs <dir>`, `dm stop <dir>`,
  `dm mcp-setup`, `dm browser-check` — launcher subcommands

`dm.sh` resolves its own location, so it keeps working wherever the skill is
installed. Users who prefer not to touch their rc can call
`python3 <skill-dir>/scripts/debug_session.py doctor` directly.

## Finish Or Abort

Whether the bug is fixed, the user stops, or the session fails:

1. Remove every `DEBUG_MODE:<session-id>:` probe and any debug-only imports,
   helpers, configuration, or CSP changes. Preserve the actual fix and useful
   regression tests.
2. Search the touched files for `DEBUG_MODE:` and inspect the diff to confirm
   no temporary instrumentation remains.
3. Stop issuing Chrome DevTools MCP commands. Do not close tabs you did not
   open, quit Chrome, or close the last tab. Remind them they can disable
   remote debugging at `chrome://inspect/#remote-debugging` if they no longer
   want local processes to attach.
4. Tear down only this collector and delete its temporary directory:

   ```bash
   dm stop <session-dir>
   ```

5. Confirm the command reports `removed: true`. If teardown fails, report the
   exact session directory and PID instead of using a broad kill command.

If context is interrupted, recover from the saved `session_dir`; re-source
`dm.sh` if needed, then use `dm status`, `dm logs`, and `dm stop`, or run
`dm doctor` to see and manage every live session at once.
