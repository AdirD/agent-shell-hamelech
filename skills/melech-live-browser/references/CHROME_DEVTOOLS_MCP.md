# Chrome DevTools MCP auto-connect

Chrome 144+ can let Chrome DevTools MCP request access to the user's existing
browser session. It preserves the open tabs, profile, and logged-in apps while
keeping the user in control of every new attach request.

Official references:

- [Chrome: connect a coding agent to an active browser session](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [Chrome DevTools MCP: automatically connect to a running instance](https://github.com/ChromeDevTools/chrome-devtools-mcp#automatically-connecting-to-a-running-chrome-instance)

## Ownership

The agent host starts `chrome-devtools-mcp` from its MCP configuration. Running
the npm package in a separate shell does not add tools to an agent session that
is already running.

The official command-server entry is:

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

Use the host's normal MCP configuration flow when it has one. For JSON-based
host configs, the bundled helper can inspect or update one explicitly selected
file:

```bash
python3 <skill-dir>/scripts/setup_chrome_devtools.py --config <host-config>
python3 <skill-dir>/scripts/setup_chrome_devtools.py --config <host-config> --apply
```

The first command is read-only. `--apply` adds the official server when absent,
or appends `--autoConnect` to an existing local command server. It refuses to
rewrite remote-URL servers and never scans or changes other host configs.

After changing a config, ask the user to reload that MCP server or restart the
agent host. A skill cannot inject newly configured MCP tools into the current
live host.

## Chrome side

1. Keep the same Chrome window and profile.
2. Open `chrome://inspect/#remote-debugging`.
3. Enable **Allow remote debugging for this browser instance**.
4. When the MCP server requests access, click **Allow** in Chrome's dialog.
5. Expect the *Chrome is being controlled by automated test software* banner
   while attached.

Do not relaunch the user's daily Chrome with `--remote-debugging-port` and a
custom `--user-data-dir`; that creates the isolated-profile path and loses the
session this skill is meant to reuse.

## Failure matrix

| Symptom | Next action |
|---|---|
| MCP tools are absent | Configure only the current host, then reload it. |
| MCP starts without `--autoConnect` | Add the flag to that host's local command entry, then reload it. |
| Chrome does not offer the connection | Enable remote debugging in Chrome 144+ and retry page listing. |
| `Could not find DevToolsActivePort` | Remote debugging is off, even if the port file exists. Ask the user to enable it, then retry page listing once. |
| Chrome shows a dialog but attach fails | Click **Allow**, retry once, then report the blocker. |
| The expected tab is missing | Ask the user to bring it forward or identify it; do not open an unauthenticated replacement. |
| The host uses a remote-URL MCP server | Do not rewrite it; use that host's supported configuration path. |

## Security

While remote debugging is enabled, trusted local processes can request control
of Chrome. Chrome still prompts for each connection. Do not tunnel CDP, scrape
credentials or browser storage, persist session state, or leave an automation
process running after the task.
