# Official Chrome auto-connect (M144+)

This is the attach path autopilot uses.

- [Let your Coding Agent debug your browser session with Chrome DevTools MCP](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [Chrome DevTools MCP README: automatically connecting](https://github.com/ChromeDevTools/chrome-devtools-mcp#automatically-connecting-to-a-running-chrome-instance)

## Who starts the server

The **agent host** (Cursor, Claude, Gemini, …) spawns `chrome-devtools-mcp`
from its MCP config. A skill cannot attach MCP tools to a live session by
`npx`-ing the server in the background.

This skill **does** the official setup step for people who do not already
have it:

```bash
dm mcp-setup          # check + write official --autoConnect
dm mcp-setup --check  # inspect only
```

`dm mcp-setup` looks at known user-level configs (`~/.cursor/mcp.json`,
Claude / Gemini / Codex files when present). If `chrome-devtools` is
missing, it adds the official entry. If the server exists without
`--autoConnect`, it appends that flag and leaves the rest of the file
alone. If no config exists but `~/.cursor` does, it creates
`~/.cursor/mcp.json`. Then it prefetches `chrome-devtools-mcp@latest` so
the host can start quickly after reload.

After a write, ask the user to reload the `chrome-devtools` MCP server.
Do not continue against a default MCP-owned empty Chrome profile.

## Chrome side

Same window, same profile, same logins. Do not restart Chrome or launch a second empty profile.

1. Chrome >= 144.
2. Open `chrome://inspect/#remote-debugging` and enable remote debugging for this browser instance.
3. When the MCP server requests a session, Chrome shows a permission dialog. Click **Allow**.
4. Expect the banner: *Chrome is being controlled by automated test software*.

Remote debugging stays off until the user enables it. Every new attach request gets a new Allow prompt.

## Official MCP config

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest", "--autoConnect"]
    }
  }
}
```

`--channel=beta` was only needed while 144 was in Beta. Stable Chrome 144+ is enough.

## What the agent does after Allow

Use Chrome DevTools MCP tools against the already-open tab:

1. List pages. Select the existing app tab. Do not open a new URL unless the repro needs a fresh navigation.
2. Snapshot the page. If the user already selected a node in the Elements panel, that selection is marked — start there.
3. Drive the repro (click, fill, type). Prefer one form fill over many single-field calls.
4. After the repro, read `dm logs`. Optionally also read console messages, the network list, or the request currently selected in the Network panel (no request id needed).
5. Do not close the last tab. Do not quit Chrome. Do not close tabs you did not open.

Snapshots, selected Elements/Network data, and console lines are extra evidence. They do not replace `dm logs`.

## Fallback only

If `dm mcp-setup` cannot make a host config ready, show its official snippet
and only then try `dm browser-check` (`agent-browser --auto-connect`). If
that is also missing or fails, switch to manual `proceed`. Do not use
Playwright, Puppeteer, a cloud browser, or a custom extension.

## What we do not do

- Do not default to launching Chrome with `--remote-debugging-port` and a custom `--user-data-dir`. That is the isolated-profile path and drops the user's logged-in session.
- Do not tunnel CDP through Portless or any remote exposure.
- Do not skip the Allow dialog or attach silently.
- Do not collect credentials, cookies, authorization headers, or full unrelated bodies.
- Do not rewrite a remote-URL `chrome-devtools` server.
