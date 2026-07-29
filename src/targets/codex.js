import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { upsertBlock } from "../util/markers.js";

export const id = "codex";
export const label = "Codex / AGENTS.md";

function resolvePath(scope) {
  if (scope.kind === "global") {
    const codexHome = process.env.CODEX_HOME || join(scope.root, ".codex");
    return join(codexHome, "AGENTS.md");
  }
  return join(scope.root, "AGENTS.md");
}

export function plan({ scope, artifact }) {
  const path = resolvePath(scope);
  return { kind: "marker", path, summary: `Codex — upsert marker block in ${path}` };
}

export async function write({ scope, artifact, body }) {
  const target = resolvePath(scope);
  let existing = "";
  try {
    existing = await readFile(target, "utf8");
  } catch {
    existing = "";
  }
  const { content, status } = upsertBlock(existing, artifact.name, body);
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, content, "utf8");
  return { status, path: target };
}
