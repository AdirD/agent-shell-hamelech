The intended developer experience is a guided loop where infrastructure stays mostly invisible.

## First-ever activation

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

> Debug mode is active.  
> Open Settings, change the display name, disconnect the network, and click Save once.  
> The bug is reproduced if the spinner disappears but the name does not update.  
> Reply `proceed` when finished.

No manual log setup or URL copying should normally be required.

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
  → developer reproduces
  → developer says "proceed"
  → agent inspects evidence
  → refine or fix
  → optionally verify
  → agent removes probes and tears down
```

The developer should interact only at the reproduction gates; the agent owns the collector, instrumentation, evidence analysis, and cleanup.
