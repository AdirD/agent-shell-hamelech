const MARKER_NS = "agent-shell-hamelech";

export function makeMarkers(name) {
  return {
    start: `<!-- ${MARKER_NS}:${name} start -->`,
    end: `<!-- ${MARKER_NS}:${name} end -->`,
  };
}

export function upsertBlock(existing, name, body) {
  const { start, end } = makeMarkers(name);
  const block = `${start}\n${body.trim()}\n${end}`;

  if (!existing) return { content: `${block}\n`, status: "created" };

  const startIdx = existing.indexOf(start);
  const endIdx = existing.indexOf(end);

  if (startIdx === -1 || endIdx === -1 || endIdx < startIdx) {
    const sep = existing.endsWith("\n") ? "\n" : "\n\n";
    return { content: `${existing}${sep}${block}\n`, status: "appended" };
  }

  const before = existing.slice(0, startIdx);
  const after = existing.slice(endIdx + end.length);
  return { content: `${before}${block}${after}`, status: "replaced" };
}

export function hasBlock(existing, name) {
  const { start, end } = makeMarkers(name);
  return existing.includes(start) && existing.includes(end);
}
