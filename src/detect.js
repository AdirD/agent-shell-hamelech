import { stat } from "node:fs/promises";
import { join } from "node:path";

async function exists(path) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

export async function detectTargets(scope) {
  const detected = new Set();

  if (scope.kind === "local") {
    if (await exists(join(scope.root, ".cursor"))) detected.add("cursor");
    if (
      (await exists(join(scope.root, ".claude"))) ||
      (await exists(join(scope.root, "CLAUDE.md")))
    ) {
      detected.add("claude-code");
    }
    if (await exists(join(scope.root, "AGENTS.md"))) detected.add("codex");
    return detected;
  }

  // global
  if (
    (await exists(join(scope.root, ".claude"))) ||
    (await exists(join(scope.root, ".claude", "CLAUDE.md")))
  ) {
    detected.add("claude-code");
  }
  const codexHome = process.env.CODEX_HOME || join(scope.root, ".codex");
  if (await exists(codexHome)) detected.add("codex");
  // Cursor has no file-based global store; never auto-detected at global scope.
  return detected;
}
