import { readdir, readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PACKAGE_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

export async function loadRegistry() {
  const rulesDir = join(PACKAGE_ROOT, "rules");
  const entries = await readdir(rulesDir, { withFileTypes: true }).catch(() => []);
  const artifacts = [];
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    const metaPath = join(rulesDir, e.name, "rule.json");
    try {
      const raw = await readFile(metaPath, "utf8");
      const meta = JSON.parse(raw);
      artifacts.push({
        ...meta,
        _dir: join(rulesDir, e.name),
        _sourcePath: join(rulesDir, e.name, meta.source),
      });
    } catch {
      // rules/<dir> without rule.json is ignored silently
    }
  }
  return artifacts;
}

export async function findArtifact(name) {
  const all = await loadRegistry();
  return all.find((a) => a.name === name);
}

export async function loadRuleBody(artifact) {
  return readFile(artifact._sourcePath, "utf8");
}
