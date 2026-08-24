# Autopilot (live browser attach)

Autopilot mode: the agent drives the user's already-open Chrome (same tabs,
same cookies, same logged-in apps) through Chrome DevTools MCP `--autoConnect`.
Manual mode is the opposite — the user holds the wheel and replies `proceed`.
This repo does not ship a Chrome extension.

Follow [CHROME_DEVTOOLS_MCP.md](CHROME_DEVTOOLS_MCP.md) for the official
setup. The agent must announce autopilot and the Chrome steps before the
first MCP call. Do not attach silently.

## What the user does

Keep the same Chrome window. Do not log in again, restart Chrome, or install
an extension.

**One-time (Chrome 144+):**

1. Open `chrome://inspect/#remote-debugging`
2. Enable **Allow remote debugging for this browser instance**
3. If this host is missing Chrome DevTools MCP, the agent runs `dm mcp-setup`
   and asks you to reload that MCP server once

**Every attach:**

1. The agent lists pages through Chrome DevTools MCP.
2. Chrome shows a permission dialog. Click **Allow**.
3. A banner appears: *Chrome is being controlled by automated test software*.
4. After the session, Chrome stays open. Disable remote debugging on that same
   inspect page if local processes should not be able to attach later.

## Attach sequence

First call must be discovery, not a navigation:

1. List open pages.
2. Select the existing app tab (bring it to front only if needed).
3. Take a snapshot. If a node is selected in the Elements panel, use that.
4. Drive the workflow with click / fill / type on snapshot uids.
5. After one reproduction attempt, read `dm logs`. Optionally list console
   messages and network requests, or read the request selected in the Network
   panel.

Do not open a new page unless the repro needs a fresh navigation. Do not
close Chrome or other tabs. Do not close the last tab.

## Failure matrix

| Symptom | What to tell the user | Next step |
|---|---|---|
| No `chrome-devtools` MCP on this host | Agent runs `dm mcp-setup`, then you reload that MCP server. | If setup cannot write a config, human `proceed` (optional `dm browser-check`). |
| MCP present but started without `--autoConnect` | `dm mcp-setup` appends `--autoConnect`. Reload the MCP server. | Do not keep going against a fresh empty profile. |
| No running Chrome / connect failed | Open `chrome://inspect/#remote-debugging` and enable **Allow remote debugging for this browser instance**. Chrome 144+ required. | Retry list-pages. If it still fails, human `proceed`. |
| Dialog appeared, then attach failed | Click **Allow** on the Chrome permission dialog. Dismissing it denies the session. | Retry once. Then human `proceed`. |
| Pages listed but the app tab is missing | Bring the logged-in app tab to the front, or say which tab to use. | List again. Do not open a new unauthenticated window. |
| Chrome older than 144 | Attach without restart is unavailable. | Human `proceed`. Do not relaunch their daily Chrome with `--remote-debugging-port` unless they ask. |

`dm browser-check` is a CLI fallback only (`agent-browser --auto-connect`).
It prints the same inspect-page / Allow hints when that attach fails.

## Security

While remote debugging is enabled, any local process can drive that Chrome
over localhost CDP. Use this only on a trusted machine. Do not enable
Portless `--tailscale`, `--funnel`, `--ngrok`, LAN mode, or any other remote
exposure of the collector **or** of CDP.

Never save cookies, tokens, or storage into the repo or a shared path. Never
scrape credentials, cookies, or authorization headers from the page. Prefer
accessibility snapshots and the same narrow probe payloads as the rest of
debug mode.

On teardown: stop issuing Chrome DevTools MCP commands. Do not close tabs you
did not open, quit Chrome, or close the last tab. Remind the user they can
turn remote debugging off.

## Non-goals

- No Chrome extension or native-messaging host in this skill
- No Portless (or other) tunnel of CDP
- No cloud / hosted browser
- No Playwright, Puppeteer, or empty automation profile as a silent fallback
- No default relaunch of Chrome with `--remote-debugging-port` and a custom
  `--user-data-dir` (that is the isolated-profile path, not the live session)
