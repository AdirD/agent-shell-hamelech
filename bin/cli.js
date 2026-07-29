#!/usr/bin/env node
import { install } from "../src/commands/install.js";
import { list } from "../src/commands/list.js";

const USAGE = `agent-shell-hamelech — install reusable agent rules.

Usage:
  agent-shell-hamelech install <name> [--local | --global]
                                     [--agents cursor,claude-code,codex]
                                     [--yes]
  agent-shell-hamelech list

Flags:
  --local         Install into the current repo (default).
  --global        Install into user-level config (~/.claude, ~/.codex, ...).
  --agents <csv>  Comma-separated targets; skips the interactive multi-select.
  --yes           Non-interactive: accept detected targets at the chosen scope.
  -h, --help      Show this help.
`;

function parseArgs(argv) {
  const args = { positional: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--help" || a === "-h") args.flags.help = true;
    else if (a === "--local") args.flags.local = true;
    else if (a === "--global") args.flags.global = true;
    else if (a === "--yes" || a === "-y") args.flags.yes = true;
    else if (a === "--agents") args.flags.agents = argv[++i];
    else if (a.startsWith("--agents=")) args.flags.agents = a.slice("--agents=".length);
    else args.positional.push(a);
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const [cmd, ...rest] = args.positional;

  if (args.flags.help) {
    process.stdout.write(USAGE);
    process.exit(0);
  }
  if (!cmd) {
    process.stdout.write(USAGE);
    process.exit(1);
  }

  if (cmd === "install") {
    await install({ name: rest[0], flags: args.flags });
    return;
  }
  if (cmd === "list") {
    await list();
    return;
  }

  process.stderr.write(`Unknown command: ${cmd}\n\n${USAGE}`);
  process.exit(1);
}

main().catch((err) => {
  process.stderr.write(`\n${err?.stack || err}\n`);
  process.exit(1);
});
