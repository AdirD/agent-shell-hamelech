import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";

export const id = "claude-code";
export const label = "Claude Code";

function resolvePath(scope, artifact) {
  const base = scope.kind === "global" ? join(scope.root, ".claude") : join(scope.root, ".claude");
  return join(base, "rules", `${artifact.name}.md`);
}

export function plan({ scope, artifact }) {
  const path = resolvePath(scope, artifact);
  return { kind: "file", path, summary: `Claude Code — write ${path}` };
}

export async function write({ scope, artifact, body }) {
  const target = resolvePath(scope, artifact);
  let existed = true;
  try {
    await readFile(target, "utf8");
  } catch {
    existed = false;
  }
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, body.trim() + "\n", "utf8");
  return { status: existed ? "overwritten" : "created", path: target };
}
