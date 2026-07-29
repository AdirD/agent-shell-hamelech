import { loadRegistry } from "../registry.js";

export async function list() {
  const artifacts = await loadRegistry();
  if (artifacts.length === 0) {
    process.stdout.write("No artifacts registered.\n");
    return;
  }
  const namePad = Math.max(...artifacts.map((a) => a.name.length));
  for (const a of artifacts) {
    process.stdout.write(`${a.kind.padEnd(8)}  ${a.name.padEnd(namePad)}  ${a.description}\n`);
  }
}
