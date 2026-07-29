import * as cursor from "./cursor.js";
import * as claudeCode from "./claude-code.js";
import * as codex from "./codex.js";

export const TARGETS = {
  [cursor.id]: cursor,
  [claudeCode.id]: claudeCode,
  [codex.id]: codex,
};

export function getTarget(id) {
  const t = TARGETS[id];
  if (!t) throw new Error(`Unknown target: ${id}`);
  return t;
}
