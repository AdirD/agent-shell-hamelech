# Autopilot (live browser attach)

Autopilot mode: the agent drives the user's already-open Chrome (same tabs,
same cookies, same logged-in apps) through Vercel Labs `agent-browser`. Manual
mode is the opposite — the user holds the wheel and replies `proceed`. This
repo does not ship a Chrome extension.

The agent must announce autopilot and the Chrome steps before the first
`browser-check`. Do not attach silently.

## What the user does

Keep the same Chrome window. Do not log in again, restart Chrome, or install
an extension.

**One-time (Chrome 144+):**

1. Open `chrome://inspect/#remote-debugging`
2. Enable **Allow remote debugging for this browser instance**

**Every attach:**

1. The agent runs `dm browser-check` (or `agent-browser --auto-connect`).
2. Chrome shows a permission dialog. Click **Allow**.
3. A banner appears: *Chrome is being controlled by automated test software*.
4. After the session, Chrome stays open. Disable remote debugging on that same
   inspect page if local processes should not be able to attach later.

## Attach flags

Always pass the same flags after `dm start` so the session stays pinned to one
tab:

```bash
agent-browser --auto-connect --pin-tab --session dm-<session-id> <command>
```

`--auto-connect` reads Chrome's `DevToolsActivePort` (or probes 9222 / 9229).
`--pin-tab` binds this debug session to one tab so a Slack or mail tab cannot
steal later clicks.

First command must be a discovery call, not a navigation:

```bash
dm browser-check --session dm-<session-id>
# same as:
agent-browser --auto-connect --json --session dm-<session-id> tab list
```

Then bind the existing app tab (switch by index from the list). Do not `open`
a URL unless the repro needs a fresh navigation. Do not close Chrome or other
tabs.

## Commands after attach

```bash
agent-browser --auto-connect --pin-tab --session dm-<session-id> snapshot
agent-browser --auto-connect --pin-tab --session dm-<session-id> click @eN
agent-browser --auto-connect --pin-tab --session dm-<session-id> type @eN "text"
agent-browser --auto-connect --pin-tab --session dm-<session-id> get url
agent-browser --auto-connect --pin-tab --session dm-<session-id> get title
```

Load `agent-browser skills get core` for the full command set. After one
driven reproduction, read `dm logs` the same as on human `proceed`. Snapshots
are extra evidence, not a replacement for probes.

## Failure matrix

| Symptom | What to tell the user | Next step |
|---|---|---|
| `agent-browser` not on PATH | `npm i -g agent-browser && agent-browser install` | Stay on human `proceed` until installed. Do not substitute Playwright or a fresh Chrome. |
| No running Chrome / auto-connect failed | Open `chrome://inspect/#remote-debugging` and enable **Allow remote debugging for this browser instance**. Chrome 144+ required for attach without a restart. | Retry `dm browser-check`. If it still fails, human `proceed`. |
| Dialog appeared, then attach failed | Click **Allow** on the Chrome permission dialog. Dismissing it denies the session. | Retry once. Then human `proceed`. |
| Tabs listed but the app tab is missing | Bring the logged-in app tab to the front, or say which tab to use. | List again. Do not open a new unauthenticated window. |
| Chrome older than 144 | Attach without restart is unavailable. | Human `proceed`. Do not relaunch their daily Chrome with `--remote-debugging-port` unless they ask. |

`dm browser-check` prints this setup hint JSON when attach fails so the agent
can paste the steps instead of inventing them.

## Security

While remote debugging is enabled, any local process can drive that Chrome
over localhost CDP. Use this only on a trusted machine. Do not enable
Portless `--tailscale`, `--funnel`, `--ngrok`, LAN mode, or any other remote
exposure of the collector **or** of CDP.

Never `state save` cookies, tokens, or storage into the repo or a shared
path. Never scrape credentials, cookies, or authorization headers from the
page. Prefer accessibility snapshots and the same narrow probe payloads as
the rest of debug mode.

On teardown: stop issuing `agent-browser` commands. Do not run
`agent-browser close`, quit Chrome, or close tabs you did not open. Remind
the user they can turn remote debugging off.

## Non-goals

- No Chrome extension or native-messaging host in this skill
- No Portless (or other) tunnel of CDP
- No cloud / hosted browser
- No Playwright, Puppeteer, or empty automation profile as a silent fallback
- Cursor `chrome-devtools` MCP can attach the same way, but this skill stays
  CLI-first (`agent-browser`) so every agent host gets the same flow
