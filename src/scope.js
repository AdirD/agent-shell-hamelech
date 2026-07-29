import { stat } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import * as p from "@clack/prompts";

async function isDir(path) {
  try {
    const s = await stat(path);
    return s.isDirectory();
  } catch {
    return false;
  }
}

export async function resolveRepoRoot(cwd = process.cwd()) {
  let dir = resolve(cwd);
  while (true) {
    if (await isDir(join(dir, ".git"))) return dir;
    const parent = dirname(dir);
    if (parent === dir) return cwd;
    dir = parent;
  }
}

export async function resolveScope({ flags }) {
  if (flags.local && flags.global) {
    throw new Error("Cannot pass both --local and --global.");
  }
  if (flags.global) return makeScope("global");
  if (flags.local) return makeScope("local");

  if (!process.stdin.isTTY) {
    throw new Error("No --local or --global flag, and stdin is not a TTY. Pass one of --local or --global.");
  }

  const choice = await p.select({
    message: "Where do you want to install?",
    options: [
      { value: "local", label: "This repo (./)", hint: "default" },
      { value: "global", label: "Your user home (~/)" },
    ],
    initialValue: "local",
  });
  if (p.isCancel(choice)) {
    p.cancel("Install cancelled.");
    process.exit(1);
  }
  return makeScope(choice);
}

async function makeScope(kind) {
  if (kind === "local") {
    const root = await resolveRepoRoot();
    return { kind, root };
  }
  return { kind: "global", root: homedir() };
}
