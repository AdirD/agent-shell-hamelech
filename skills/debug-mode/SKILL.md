---
name: debug-mode
description: Run an evidence-first debugging loop with temporary runtime probes and a local Portless-backed JSONL collector. Use when a user can reproduce a UI, API, desktop, or integration bug but static inspection, tests, and existing logs do not reveal the failing runtime path, especially when the user asks for debug mode, dynamic request logs, instrumentation, or a reproduce-and-proceed workflow.
---

# Debug Mode

Treat the current task as an active debugging session. Diagnose from runtime
evidence before proposing a fix.

For the intended first-use, reproduction, iteration, verification, and later-use
experience, read [DEVELOPER_JOURNEY_EXAMPLE.md](references/DEVELOPER_JOURNEY_EXAMPLE.md)
and use it as the interaction model.

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

## Start A Session

1. Inspect the failing path, current logs, and relevant tests. State one to
   three concrete hypotheses and what observation would distinguish them.
2. Locate this installed skill directory and confirm both `python3` and
   `portless` are available. If Portless is missing, stop and tell the user to
   install the official Vercel Labs CLI with `npm install -g portless`. Do not
   silently substitute another tunnel or server.
3. If this machine has not used Portless before, run `portless doctor`. Follow
   its local trust/setup guidance before starting the background session.
4. Start the bundled collector:

   ```bash
   python3 <skill-dir>/scripts/debug_session.py start
   ```

   Save the returned `session_dir`, `session_id`, `log_endpoint`, `events_file`,
   and `backend_port`. The launcher copies the lean server skeleton into a new
   temporary directory. Portless assigns a different free backend port and a
   unique local route for every session.
5. Verify the returned `health_url` before editing application code.

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

## Hand Control To The User

Tell the user:

1. Debug mode is active.
2. The exact workflow to perform, including any reset or starting state.
3. Which visible outcome identifies the bug.
4. To reply exactly `proceed` after one reproduction attempt.

Then stop. Do not poll the event file or claim a reproduction before the user
replies.

## Inspect On `proceed`

Read the evidence with:

```bash
python3 <skill-dir>/scripts/debug_session.py logs <session-dir> --run run-1
```

Correlate event order and values against the stated hypotheses, then choose
one outcome:

- **Reproduced and conclusive:** explain the observed causal chain, implement
  the smallest root-cause fix, and verify it. Keep probes only if one user
  rerun is still needed to validate the fix.
- **Reproduced but inconclusive:** say what the evidence ruled out, revise the
  hypothesis, add or move only the probes needed for `run-2`, and ask for the
  precise workflow again.
- **No application events:** check session status and send one synthetic event
  to distinguish collector delivery failure from an unvisited code path. Check
  browser CSP/CORS or environment reachability when relevant, then repair the
  instrumentation and retry.
- **Workflow did not reproduce:** record that result, adjust the starting state
  or probe placement, increment the run ID, and retry without pretending the
  bug was observed.

Do not equate correlation with cause. Cite the specific probe sequence and
values that support the next action.

## Finish Or Abort

Whether the bug is fixed, the user stops, or the session fails:

1. Remove every `DEBUG_MODE:<session-id>:` probe and any debug-only imports,
   helpers, configuration, or CSP changes. Preserve the actual fix and useful
   regression tests.
2. Search the touched files for `DEBUG_MODE:` and inspect the diff to confirm
   no temporary instrumentation remains.
3. Tear down only this collector and delete its temporary directory:

   ```bash
   python3 <skill-dir>/scripts/debug_session.py stop <session-dir>
   ```

4. Confirm the command reports `removed: true`. If teardown fails, report the
   exact session directory and PID instead of using a broad kill command.

If context is interrupted, recover from the saved `session_dir`; use `status`,
`logs`, and `stop` from the bundled launcher.
