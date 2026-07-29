import * as p from "@clack/prompts";
import { findArtifact, loadRuleBody } from "../registry.js";
import { resolveScope } from "../scope.js";
import { detectTargets } from "../detect.js";
import { getTarget, TARGETS } from "../targets/index.js";

export async function install({ name, flags }) {
  if (!name) {
    throw new Error("install requires an artifact name. Try: agent-shell-hamelech list");
  }

  const artifact = await findArtifact(name);
  if (!artifact) {
    throw new Error(`Artifact not found: ${name}. Try: agent-shell-hamelech list`);
  }

  p.intro(`Installing ${artifact.name}`);

  const scope = await resolveScope({ flags });
  const detected = await detectTargets(scope);

  const candidateIds = artifact.targets.filter((id) => TARGETS[id]);
  let selected = await pickTargets({
    scope,
    candidates: candidateIds,
    detected,
    flags,
  });

  if (selected.length === 0) {
    p.cancel("No targets selected. Nothing to do.");
    return;
  }

  const body = await loadRuleBody(artifact);
  const plans = selected.map((id) => ({ id, ...getTarget(id).plan({ scope, artifact }) }));

  p.note(renderPlan(plans, scope), "Planned writes");

  if (!flags.yes && process.stdin.isTTY) {
    const ok = await p.confirm({ message: "Proceed?", initialValue: true });
    if (p.isCancel(ok) || !ok) {
      p.cancel("Install cancelled.");
      return;
    }
  }

  const results = [];
  for (const id of selected) {
    const t = getTarget(id);
    const result = await t.write({ scope, artifact, body });
    results.push({ id, label: t.label, ...result });
  }

  p.outro("Done.");
  printSummary(results);
}

async function pickTargets({ scope, candidates, detected, flags }) {
  if (flags.agents) {
    const requested = flags.agents.split(",").map((s) => s.trim()).filter(Boolean);
    const unknown = requested.filter((id) => !candidates.includes(id));
    if (unknown.length) throw new Error(`Unknown target(s): ${unknown.join(", ")}`);
    return requested;
  }

  if (flags.yes || !process.stdin.isTTY) {
    return candidates.filter((id) => detected.has(id));
  }

  const options = candidates.map((id) => {
    const t = getTarget(id);
    const isDetected = detected.has(id);
    const hints = [];
    if (isDetected) hints.push("detected");
    if (id === "cursor" && scope.kind === "global") hints.push("manual paste");
    return {
      value: id,
      label: t.label,
      hint: hints.join(", ") || undefined,
    };
  });

  const initialValues = candidates.filter((id) => detected.has(id));
  const chosen = await p.multiselect({
    message: `Which agents? (scope: ${scope.kind})`,
    options,
    initialValues,
    required: false,
  });
  if (p.isCancel(chosen)) {
    p.cancel("Install cancelled.");
    process.exit(1);
  }
  return chosen;
}

function renderPlan(plans, scope) {
  const lines = [`scope: ${scope.kind}  root: ${scope.root}`, ""];
  for (const plan of plans) {
    lines.push(`• ${plan.summary}`);
  }
  return lines.join("\n");
}

function printSummary(results) {
  const lines = ["", "Results:"];
  for (const r of results) {
    if (r.status === "manual") {
      lines.push(`  ${r.label}: manual paste required (see below)`);
    } else {
      lines.push(`  ${r.label}: ${r.status} → ${r.path}`);
    }
  }
  process.stdout.write(lines.join("\n") + "\n");
  for (const r of results) {
    if (r.status === "manual" && r.message) process.stdout.write(r.message);
  }
}
