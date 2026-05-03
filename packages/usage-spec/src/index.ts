export type { Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices } from "./spec.js";
export { renderKDL, validateKDL } from "./kdl.js";
export { renderJSON } from "./json.js";

import { renderKDL } from "./kdl.js";
import { renderJSON } from "./json.js";
import type { Spec } from "./spec.js";

export function generate(
  spec: Spec,
  options?: { format?: "kdl" | "json"; comment?: string },
): string {
  const fmt = options?.format ?? "kdl";
  const output = fmt === "json" ? renderJSON(spec) : renderKDL(spec);

  if (options?.comment) {
    return `// ${options.comment}\n${output}`;
  }

  return output;
}
