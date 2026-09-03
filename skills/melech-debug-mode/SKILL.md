---
name: melech-debug-mode
description: Run an evidence-gated end-to-end session with temporary runtime probes and optional control of the user's existing Chrome tab.
---

# Debug Mode

Follow this protocol for the user's requested workflow:

```text
choose driver → attach if autopilot → define one complete attempt
→ start collector → add probes → run E2E → read evidence
→ act on evidence → rerun E2E if code changed → clean up
```

A unit test, direct call, ad hoc script, synthetic request, or isolated endpoint
never counts as the initial E2E attempt or post-change verification.

## 1. Choose The Driver

- Browser workflow → **autopilot** by default.
- User explicitly says they will drive, hold the wheel, or use `proceed` →
  **manual**.
- The user denies attach, the target tab is ambiguous or unsafe, or the target
  appears to be production → **manual**.
- Non-browser workflow → use its real external entry point.

Do not ask the user to choose for an ordinary local browser workflow.

For autopilot, read the installed `melech-live-browser/SKILL.md`, show its
Chrome consent notice, and begin its attach flow before any diagnostic
shortcut. If it is missing, offer:

```bash
npx skills add https://github.com/AdirD/agent-shell-hamelech --skill melech-live-browser
```

Ask whether to install it or switch to manual. Never substitute another browser
or profile.

Autopilot always starts by asking the user to enable remote debugging at
`chrome://inspect/#remote-debugging` and click **Allow** when Chrome prompts.
If attach fails, repeat that request and retry once. Manual is a fallback only
after that retry fails.

## 2. Define One Attempt

State:

- the reset and starting state
- the exact actions
- the observable outcomes that decide the user's request
- at most five probes needed to distinguish those outcomes

## 3. Start The Collector

Locate this installed skill directory and confirm `python3` and `portless`
exist. If Portless is missing, stop and request:

```bash
npm install -g portless
```

Run `portless doctor` when first-use setup is needed, then:

```bash
source <skill-dir>/scripts/dm.sh
dm start
```

`dm` is the sourced shell function for
`python3 <skill-dir>/scripts/debug_session.py`. If a later step reports `dm`
undefined, re-source `dm.sh` or call that path directly.

| Command | Use |
|---|---|
| `dm start` | start one temporary collector |
| `dm status <session-dir>` | that session's metadata and process liveness |
| `dm logs <session-dir> [--run ID] [--after-seq N] [--tail N]` | read events |
| `dm stop <session-dir>` | tear down that session |
| `dm doctor --once` | JSON snapshot of every live session |

Always pass `--once` to `doctor`: bare `dm doctor` (and bare `dm`) opens a curses
TUI for the user's own terminal and will hang or crash a non-interactive shell.

`dm start` prints the facts every later step needs: `session_id`, `session_dir`,
`log_endpoint`, `health_url`, `events_file`, and `backend_host`/`backend_port`.
Save them, then confirm the collector answers before editing application code:

```bash
curl -s "<health_url>"    # {"ok":true,"entries":0}
```

`health_url` and `log_endpoint` route through Portless. If that route is
unreachable, the same collector answers on
`http://<backend_host>:<backend_port>`; swap only the origin and keep the
`/log/<token>` path from `log_endpoint`.

Keep the collector local; never enable LAN mode, tunnels, Tailscale, Funnel,
ngrok, or other remote exposure.

## 4. Add Probes

Derive placement from the deciding outcomes: the branch that should or should not
run, the value immediately before a transformation, the boundary input and
output, and the error path. Instrument whichever layer owns the question — for a
browser workflow that means page or component state for rendering and
interaction, and server handlers for persistence, validation, and integration.

POST one small JSON object per observation to `log_endpoint` exactly as returned
(it embeds the session token):

```json
{
  "run": "run-1",
  "probe": "checkout-before-submit",
  "hypothesis": "save commits exactly once",
  "data": { "isDisabled": true, "itemCount": 2 }
}
```

Fire and forget, so a collector failure cannot change product behavior:

```js
// DEBUG_MODE:<session-id>:checkout-before-submit
void fetch("<log-endpoint>", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    run: "run-1",
    probe: "checkout-before-submit",
    hypothesis: "save commits exactly once",
    data: { isDisabled, itemCount: items.length },
  }),
}).catch(() => {});
```

Adapt the idiom to the target language while keeping the payload shape, the
marker comment, the narrow field selection, and the swallowed failure. Send
booleans, counts, enum values, IDs already safe in development, and short
summaries — never credentials, tokens, cookies, authorization headers, personal
data, full bodies, or unrelated state.

Because a fire-and-forget probe cannot see a refusal, prove delivery once with
the real payload shape before the attempt:

```bash
curl -s -X POST "<log_endpoint>" -H 'content-type: application/json' \
  -d '{"run":"run-0","probe":"delivery-check","data":{"ok":true}}'
# {"accepted":true,"seq":1}
```

Any other response means the collector refused the event rather than the code
path never running: a missing `content-type`, a non-object or malformed body, a
payload over 64 KB, a wrong URL or token, or `sensitive_field_rejected`. That
last one drops an event whose key — at any nesting depth, ignoring case and
hyphens — exactly matches a credential name such as `token`, `secret`,
`password`, `cookie`, `authorization`, `api_key`, or `access_token`. Rename the
field descriptively (`hasSessionToken`) instead of removing the observation.

Mark every temporary edit `DEBUG_MODE:<session-id>:<probe-id>` and track touched
files. Run only the cheapest compile, type, or syntax check needed to prove the
instrumentation is valid; probe events from that check are not E2E evidence.

## 5. Run The Attempt

Use `run-1` initially and increment the run ID for every retry, supplemental
diagnostic, and post-change verification. After each complete attempt, read:

```bash
dm logs <session-dir> --run <run-id>
```

Every line is an envelope: your object under `payload`, plus `seq` and
`received_at`. Read `--after-seq` to see only what the newest attempt added, and
`--tail` when a run is noisy.

### Autopilot

Use `melech-live-browser` to select the existing app tab, snapshot it, and drive
exactly one complete attempt, then read that run. Correlate console or network
evidence through live browser only when a stated outcome needs it, and never
conclude from a snapshot alone. Do not ask for `proceed`. If attach or tab
selection fails, switch to manual.

### Manual

Tell the user manual mode is active, give the defined reset, actions, and
deciding outcomes, and ask them to reply exactly `proceed` after one attempt.
Then stop. Read that run only after `proceed`.

### Non-browser

Execute the defined workflow through its real external entry point, then read
that run. Do not substitute an isolated function, tool, controller, or ad hoc
diagnostic script.

## 6. Act On Evidence

Cite the event sequence and values that support the result. Do not infer cause
from correlation.

- Use the evidence to carry out the user's requested next action without
  broadening it.
- Evidence is incomplete → revise the minimum probes and repeat with a new run
  ID through the same E2E driver.
- No events → confirm the collector is actually serving with the `health_url`
  curl or `dm doctor --once` (`dm status` only reports process liveness), then
  repeat the delivery check, since a refused event looks identical to an
  unvisited code path. The collector
  already allows cross-origin posts, so for page-side probes suspect the app's
  CSP `connect-src` or an unreachable route; repair, then repeat E2E.
- Code changed → keep relevant probes and repeat the same E2E workflow before
  cleanup.

## Supplemental Diagnostics

Only after the first E2E attempt, focused tests, direct calls, ad hoc diagnostic
scripts, endpoint requests, or synthetic requests may isolate a narrower
question. For browser workflows, use them only after successful attach. Label
them supplemental with separate run IDs; they never satisfy an E2E gate.

## 7. Clean Up

After a conclusive E2E result with no code change, successful post-change E2E
verification, or abort:

1. Remove every `DEBUG_MODE:<session-id>:` probe and debug-only change.
2. Search touched files for `DEBUG_MODE:` and inspect the diff.
3. Stop browser operations without closing user-owned tabs.
4. Run `dm stop <session-dir>` and confirm `removed: true`.

If teardown fails, report the session directory and PID; never broad-kill or
run broad Portless cleanup. If interrupted, recover the saved `session_dir` with
`dm status`, `dm logs`, or `dm doctor --once`, then finish or abort through this
cleanup.
