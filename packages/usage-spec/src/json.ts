import type { Spec, SpecArg, SpecFlag, SpecCommand } from "./spec.js";

function argToJSON(arg: SpecArg): Record<string, unknown> {
  const result: Record<string, unknown> = { name: arg.name };

  if (arg.help) result.help = arg.help;
  if (!arg.required) result.required = false;
  if (arg.var) result.var = true;
  if (arg.hide) result.hide = true;
  if (arg.default.length === 1) result.default = arg.default[0];
  if (arg.default.length > 1) result.default = arg.default;
  if (arg.choices) result.choices = arg.choices.values;

  return result;
}

function flagToJSON(flag: SpecFlag): Record<string, unknown> {
  const result: Record<string, unknown> = {};

  const nameParts: string[] = [];
  if (flag.short) nameParts.push(`-${flag.short}`);
  if (flag.long) nameParts.push(`--${flag.long}`);
  result.name = nameParts.join(" ");

  if (flag.help) result.help = flag.help;
  if (flag.helpLong) result.help_long = flag.helpLong;
  if (flag.required) result.required = true;
  if (flag.hide) result.hide = true;
  if (flag.global) result.global = true;
  if (flag.count) result.count = true;
  if (flag.var) result.var = true;
  if (flag.negate) result.negate = flag.negate;
  if (flag.deprecated) result.deprecated = flag.deprecated;
  if (flag.env) result.env = flag.env;
  if (flag.default.length === 1) result.default = flag.default[0];
  if (flag.default.length > 1) result.default = flag.default;

  if (flag.arg) {
    result.arg = argToJSON(flag.arg);
  }

  return result;
}

function cmdToJSON(cmd: SpecCommand): Record<string, unknown> {
  const result: Record<string, unknown> = { name: cmd.name };

  if (cmd.help) result.help = cmd.help;
  if (cmd.helpLong) result.help_long = cmd.helpLong;
  if (cmd.hide) result.hide = true;
  if (cmd.deprecated) result.deprecated = cmd.deprecated;
  if (cmd.aliases.length > 0) result.aliases = cmd.aliases;
  if (cmd.subcommandRequired) result.subcommand_required = true;

  if (cmd.flags.length > 0) {
    result.flags = cmd.flags.map(flagToJSON);
  }

  if (cmd.args.length > 0) {
    result.args = cmd.args.map(argToJSON);
  }

  if (cmd.cmds.length > 0) {
    result.cmds = cmd.cmds.map(cmdToJSON);
  }

  return result;
}

export function renderJSON(spec: Spec): string {
  const result: Record<string, unknown> = {};

  if (spec.name) result.name = spec.name;
  if (spec.bin) result.bin = spec.bin;
  if (spec.version) result.version = spec.version;
  if (spec.about) result.about = spec.about;
  if (spec.long) result.long_about = spec.long;
  if (spec.usage) result.usage = spec.usage;

  if (spec.flags.length > 0) {
    result.flags = spec.flags.map(flagToJSON);
  }

  if (spec.args.length > 0) {
    result.args = spec.args.map(argToJSON);
  }

  if (spec.cmds.length > 0) {
    result.cmds = spec.cmds.map(cmdToJSON);
  }

  return JSON.stringify(result, null, 2) + "\n";
}
