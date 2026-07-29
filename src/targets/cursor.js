import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { wrapAsMdc } from "../util/mdc.js";

export const id = "cursor";
export const label = "Cursor";

export function plan({ scope, artifact }) {
  if (scope.kind === "global") {
    return {
      kind: "manual",
      summary:
        "Cursor — global rules are not file-based. Content will be printed for you to paste into Cursor Settings → Rules.",
    };
  }
  const path = join(scope.root, ".cursor", "rules", `${artifact.name}.mdc`);
  return { kind: "file", path, summary: `Cursor — write ${path}` };
}

export async function write({ scope, artifact, body }) {
  if (scope.kind === "global") {
    const mdc = wrapAsMdc({ description: artifact.description, body });
    return {
      status: "manual",
      message: [
        "",
        "Cursor global install — paste the block below into Cursor Settings → Rules → User Rules:",
        "",
        "----- BEGIN cursor user rule -----",
        mdc,
        "----- END cursor user rule -----",
        "",
      ].join("\n"),
    };
  }

  const target = join(scope.root, ".cursor", "rules", `${artifact.name}.mdc`);
  const mdc = wrapAsMdc({ description: artifact.description, body });

  let existed = true;
  try {
    await readFile(target, "utf8");
  } catch {
    existed = false;
  }
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, mdc, "utf8");
  return { status: existed ? "overwritten" : "created", path: target };
}
