import type { Spec, SpecArg, SpecCommand, SpecFlag, SpecChoices } from "./convert.js";

const KDL_RESERVED = new Set(["true", "false", "null", "inf", "-inf", "nan"]);

function needsQuoting(s: string): boolean {
  if (s.length === 0) return true;
  if (KDL_RESERVED.has(s)) return true;
  if (s[0] >= "0" && s[0] <= "9") return true;
  for (const c of s) {
    switch (c) {
      case " ":
      case "\t":
      case "\n":
      case "\r":
      case '"':
      case "\\":
      case "/":
      case "(":
      case ")":
      case "{":
      case "}":
      case ";":
      case "=":
      case "#":
      case ".":
      case ",":
      case ":":
        return true;
    }
  }
  return false;
}

function kdlQuoteAlways(s: string): string {
  s = s.replace(/\\/g, "\\\\");
  s = s.replace(/"/g, '\\"');
  s = s.replace(/\n/g, "\\n");
  s = s.replace(/\t/g, "\\t");
  s = s.replace(/\r/g, "\\r");
  return `"${s}"`;
}

function kdlQuote(s: string): string {
  if (s === "") return `""`;
  if (needsQuoting(s)) return kdlQuoteAlways(s);
  return s;
}

function indent(depth: number): string {
  return "    ".repeat(depth);
}

function renderChoices(choices: SpecChoices, depth: number): string {
  const lines: string[] = [];
  const ci = indent(depth);
  const ii = indent(depth + 1);
  lines.push(`${ci}choices {`);
  for (const c of choices.values) {
    lines.push(`${ii}${kdlQuoteAlways(c)}`);
  }
  lines.push(`${ci}}`);
  return lines.join("\n");
}

function renderArg(arg: SpecArg, depth: number): string {
  const parts: string[] = [];
  const i = indent(depth);

  // Build usage string: <required> or [optional], with … for variadic
  let usage: string;
  if (arg.required) {
    usage = `<${arg.name}>`;
  } else {
    usage = `[${arg.name}]`;
  }
  if (arg.var) {
    usage += "\u2026"; // unicode ellipsis
  }

  // [brackets] must be quoted in KDL
  if (usage.startsWith("[")) {
    parts.push(`${i}arg ${kdlQuoteAlways(usage)}`);
  } else {
    parts.push(`${i}arg ${usage}`);
  }

  if (arg.help) {
    parts.push(`help=${kdlQuote(arg.help)}`);
  }
  if (!arg.required) {
    parts.push("required=#false");
  }
  if (arg.var) {
    parts.push("var=#true");
  }
  if (arg.hide) {
    parts.push("hide=#true");
  }
  if (arg.default.length === 1) {
    parts.push(`default=${kdlQuote(arg.default[0])}`);
  }

  const hasChildren = arg.choices != null || arg.default.length > 1;
  if (!hasChildren) {
    return parts.join(" ") + "\n";
  }

  const lines: string[] = [parts.join(" ") + " {"];
  const ci = indent(depth + 1);

  if (arg.default.length > 1) {
    lines.push(`${ci}default {`);
    const ii = indent(depth + 2);
    for (const d of arg.default) {
      lines.push(`${ii}${kdlQuoteAlways(d)}`);
    }
    lines.push(`${ci}}`);
  }

  if (arg.choices) {
    lines.push(renderChoices(arg.choices, depth + 1));
  }

  lines.push(`${i}}`);
  return lines.join("\n") + "\n";
}

function renderFlag(flag: SpecFlag, depth: number): string {
  const parts: string[] = [];
  const i = indent(depth);

  // Build the flag name: "-s --long"
  const nameParts: string[] = [];
  if (flag.short) nameParts.push(`-${flag.short}`);
  if (flag.long) nameParts.push(`--${flag.long}`);
  const flagName = nameParts.join(" ");

  parts.push(`${i}flag ${kdlQuote(flagName)}`);

  if (flag.help) {
    parts.push(`help=${kdlQuote(flag.help)}`);
  }
  if (flag.required) {
    parts.push("required=#true");
  }
  if (flag.var) {
    parts.push("var=#true");
  }
  if (flag.hide) {
    parts.push("hide=#true");
  }
  if (flag.global) {
    parts.push("global=#true");
  }
  if (flag.count) {
    parts.push("count=#true");
  }
  if (flag.negate) {
    parts.push(`negate=${kdlQuote(flag.negate)}`);
  }
  if (flag.deprecated) {
    parts.push(`deprecated=${kdlQuote(flag.deprecated)}`);
  }
  if (flag.default.length === 1) {
    parts.push(`default=${kdlQuote(flag.default[0])}`);
  } else if (flag.defaultBool != null) {
    parts.push(`default=#${flag.defaultBool}`);
  }
  if (flag.env) {
    parts.push(`env=${kdlQuote(flag.env)}`);
  }

  const hasChildren =
    flag.helpLong !== "" || flag.arg != null || flag.default.length > 1;

  if (!hasChildren) {
    return parts.join(" ") + "\n";
  }

  const lines: string[] = [parts.join(" ") + " {"];
  const ci = indent(depth + 1);

  if (flag.helpLong) {
    lines.push(`${ci}long_help ${kdlQuoteAlways(flag.helpLong)}`);
  }

  if (flag.default.length > 1) {
    lines.push(`${ci}default {`);
    const ii = indent(depth + 2);
    for (const d of flag.default) {
      lines.push(`${ii}${kdlQuoteAlways(d)}`);
    }
    lines.push(`${ci}}`);
  }

  if (flag.arg) {
    const argParts: string[] = [`${ci}arg <${flag.arg.name}>`];
    if (flag.arg.help) {
      argParts.push(`help=${kdlQuote(flag.arg.help)}`);
    }

    const argHasChildren = flag.arg.choices != null;
    if (!argHasChildren) {
      lines.push(argParts.join(" "));
    } else {
      lines.push(argParts.join(" ") + " {");
      if (flag.arg.choices) {
        lines.push(renderChoices(flag.arg.choices, depth + 2));
      }
      lines.push(`${ci}}`);
    }
  }

  lines.push(`${i}}`);
  return lines.join("\n") + "\n";
}

function renderCommand(cmd: SpecCommand, depth: number): string {
  const parts: string[] = [];
  const i = indent(depth);

  parts.push(`${i}cmd ${kdlQuote(cmd.name)}`);

  if (cmd.hide) parts.push("hide=#true");
  if (cmd.subcommandRequired) parts.push("subcommand_required=#true");
  if (cmd.help) parts.push(`help=${kdlQuote(cmd.help)}`);
  if (cmd.deprecated) parts.push(`deprecated=${kdlQuote(cmd.deprecated)}`);

  const hasChildren =
    cmd.helpLong !== "" ||
    cmd.aliases.length > 0 ||
    cmd.flags.length > 0 ||
    cmd.args.length > 0 ||
    cmd.cmds.length > 0;

  if (!hasChildren) {
    return parts.join(" ") + "\n";
  }

  const lines: string[] = [parts.join(" ") + " {"];
  const ci = indent(depth + 1);

  if (cmd.aliases.length > 0) {
    const aliasParts = cmd.aliases.map((a) => kdlQuote(a)).join(" ");
    lines.push(`${ci}alias ${aliasParts}`);
  }

  if (cmd.helpLong) {
    lines.push(`${ci}long_help ${kdlQuoteAlways(cmd.helpLong)}`);
  }

  for (const flag of cmd.flags) {
    lines.push(renderFlag(flag, depth + 1));
  }

  for (const arg of cmd.args) {
    lines.push(renderArg(arg, depth + 1));
  }

  for (const sub of cmd.cmds) {
    lines.push(renderCommand(sub, depth + 1));
  }

  lines.push(`${i}}`);
  return lines.join("\n") + "\n";
}

export function renderKDL(spec: Spec): string {
  const lines: string[] = [];

  if (spec.name) lines.push(`name ${kdlQuote(spec.name)}`);
  if (spec.bin) lines.push(`bin ${kdlQuote(spec.bin)}`);
  if (spec.version) lines.push(`version ${kdlQuote(spec.version)}`);
  if (spec.about) lines.push(`about ${kdlQuote(spec.about)}`);
  if (spec.long) lines.push(`long_about ${kdlQuoteAlways(spec.long)}`);
  if (spec.usage) lines.push(`usage ${kdlQuote(spec.usage)}`);

  for (const flag of spec.flags) {
    lines.push(renderFlag(flag, 0));
  }

  for (const arg of spec.args) {
    lines.push(renderArg(arg, 0));
  }

  for (const cmd of spec.cmds) {
    lines.push(renderCommand(cmd, 0));
  }

  return lines.join("\n") + "\n";
}

export { kdlQuote, kdlQuoteAlways, needsQuoting };
