The intended developer experience is a guided loop where infrastructure stays mostly invisible.

Two reproduction modes share the same collector and probes:

- **Manual** — the developer holds the wheel, then replies `proceed`.
- **Autopilot** — the agent drives the already-open Chrome tab end-to-end.
  The developer only enables remote debugging and clicks Allow.

If the bug is a UI and the developer did not pick, the agent names both
modes and waits. It does not attach and does not hand over clicks until
they answer.

## First-ever activation (manual)

The developer says something like:

> Use debug mode. Clicking “Save” sometimes does nothing.

The agent then:

1. Announces debug mode and inspects the relevant code.
2. Forms a few testable hypotheses.
3. Checks Python and Portless.
4. If Portless is missing, asks the developer to install it.
5. On first use, `portless doctor` may require a one-time local certificate trust/setup.
6. Starts a private temporary collector with a unique URL and backend port.
7. Adds a few clearly marked temporary probes.
8. Runs a syntax/type check.

The developer then sees something like:

> Debug mode is active in **manual**. You hold the wheel.  
> Open Settings, change the display name, disconnect the network, and click Save once.  
> The bug is reproduced if the spinner disappears but the name does not update.  
> Reply `proceed` when finished.

No manual log setup or URL copying should normally be required.

## First-ever activation (autopilot)

When the developer wants the agent to drive an already-open Chrome tab:

> Use debug mode. I already have Settings open and I'm logged in. Save still
> does nothing.

The agent still instruments as above, then tries live attach instead of
handing over the clicks:

1. Runs `dm mcp-setup`. If Chrome DevTools MCP is missing or has no
   `--autoConnect`, that writes the official host config. If a reload is
   required, it waits until the developer reloads MCP. The host, not the
   skill, then starts the server.
2. If this is the first attach on the machine, tells the developer to open
   `chrome://inspect/#remote-debugging` once and enable remote debugging
   (official Chrome M144 auto-connect; see
   [CHROME_DEVTOOLS_MCP.md](CHROME_DEVTOOLS_MCP.md)).
3. Lists pages through Chrome DevTools MCP and asks them to click **Allow**.

The developer then sees something like:

> Autopilot is on. I will drive the Settings tab you already have open.  
> One-time: open chrome://inspect/#remote-debugging and enable Allow remote
> debugging for this browser instance (Chrome 144+).  
> When Chrome prompts, click Allow. A “controlled by automated test software”
> banner is expected. I will not quit Chrome or close other tabs.  
> I will change the display name, drop the network, and click Save once.

If attach fails (checkbox off, Allow dismissed, Chrome too old), the agent
switches to **manual**, uses the hold-the-wheel text above, and waits for
`proceed`. The collector still runs either way.

After a successful driven run, the agent reads `dm logs` without waiting
for `proceed`, then follows the same evidence paths as below.

## After the developer replies `proceed`

The agent reads the collected events and reports evidence:

> Reproduced. The submit handler ran, but the offline error branch returned before resetting `isSaving`. That explains the stuck state.

Then it chooses one path:

- Evidence is conclusive → implement the fix.
- Evidence is incomplete → add one or two more probes and request another run.
- No events arrived → verify the collector and probe delivery, then retry.
- The bug didn’t reproduce → adjust the starting conditions and retry.

For another round:

> I moved the probes around the retry boundary. Repeat the same workflow and reply `proceed` again.

## Fix verification

After implementing a fix, the agent may ask for one final run:

> The fix is applied, but debug mode remains active for verification. Repeat the workflow once more and reply `proceed`.

After confirmation, it:

1. Removes every temporary probe and debug-only helper.
2. Verifies no `DEBUG_MODE:` markers remain.
3. Stops only that session’s collector.
4. Deletes its temporary directory and logs.
5. Reports the diagnosis, fix, and verification result.

## Later activations

Subsequent activations skip Portless installation and trust setup. Every activation still gets:

- A fresh temporary directory
- A unique Portless route
- A newly assigned backend port
- An empty event log
- Independent teardown

So the normal recurring experience becomes:

```text
Ask to debug
  → agent instruments
  → pick manual or autopilot (ask if unclear)
  → manual: developer reproduces, then "proceed"
    or autopilot: Allow once, agent drives the tab
  → agent inspects evidence
  → refine or fix
  → optionally verify
  → agent detaches (Chrome stays open), removes probes, and tears down
```

The developer should interact only at the mode pick and the reproduction
gates (Allow dialog or `proceed`); the agent owns the collector,
instrumentation, evidence analysis, and cleanup.
