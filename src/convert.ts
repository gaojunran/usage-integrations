import type { Command, Option, Argument } from "commander";

// Commander.js doesn't expose internal properties in its type definitions.
// We use an interface to safely access them at runtime.
interface CommandInternal extends Command {
  _actionHandler: unknown;
  _executableHandler: boolean;
  _hidden: boolean;
}

export interface SpecChoices {
  values: string[];
}

export interface SpecArg {
  name: string;
  help: string;
  required: boolean;
  var: boolean;
  hide: boolean;
  default: string[];
  choices: SpecChoices | null;
}

export interface SpecFlag {
  short: string;
  long: string;
  help: string;
  helpLong: string;
  required: boolean;
  hide: boolean;
  global: boolean;
  count: boolean;
  var: boolean;
  negate: string;
  deprecated: string;
  default: string[];
  defaultBool: boolean | null;
  env: string;
  arg: SpecArg | null;
}

export interface SpecCommand {
  name: string;
  help: string;
  helpLong: string;
  hide: boolean;
  deprecated: string;
  aliases: string[];
  subcommandRequired: boolean;
  flags: SpecFlag[];
  args: SpecArg[];
  cmds: SpecCommand[];
}

export interface Spec {
  name: string;
  bin: string;
  version: string;
  about: string;
  long: string;
  usage: string;
  flags: SpecFlag[];
  args: SpecArg[];
  cmds: SpecCommand[];
}

const BUILTIN_FLAG_NAMES = new Set(["help", "version"]);

function isBuiltinOption(opt: Option): boolean {
  const name = opt.name();
  return BUILTIN_FLAG_NAMES.has(name);
}

function isRunnable(cmd: Command): boolean {
  const internal = cmd as CommandInternal;
  return internal._actionHandler != null || internal._executableHandler === true;
}

function isBuiltinCommand(cmd: Command): boolean {
  const name = cmd.name();
  // Commander.js auto-generates "help" subcommand
  if (name === "help" && !isRunnable(cmd)) return true;
  return false;
}

function convertArg(arg: Argument): SpecArg {
  const result: SpecArg = {
    name: arg.name(),
    help: arg.description ?? "",
    required: arg.required,
    var: arg.variadic,
    hide: false,
    default: arg.defaultValue != null ? [String(arg.defaultValue)] : [],
    choices: null,
  };

  if (arg.argChoices && arg.argChoices.length > 0) {
    result.choices = { values: [...arg.argChoices] };
  }

  return result;
}

function convertFlag(opt: Option, global = false): SpecFlag {
  // isBoolean: no value argument, including negated options (--no-color)
  const isBoolean = !opt.required && !opt.optional;
  const flag: SpecFlag = {
    short: opt.short?.replace(/^-/, "") ?? "",
    long: opt.long?.replace(/^--/, "") ?? "",
    help: opt.description ?? "",
    helpLong: "",
    required: opt.mandatory,
    hide: opt.hidden,
    global,
    count: false,
    var: opt.variadic,
    negate: "",
    deprecated: "",
    default: [],
    defaultBool: null,
    env: opt.envVar ?? "",
    arg: null,
  };

  // Negated options: --no-color
  if (opt.negate) {
    flag.negate = opt.long!.replace(/^--no-/, "--");
  }

  // Non-boolean options have an argument
  if (!isBoolean) {
    const argName = opt.name().replace(/-/g, "_").toUpperCase();
    flag.arg = {
      name: argName,
      help: "",
      required: opt.required,
      var: opt.variadic,
      hide: false,
      default: [],
      choices: null,
    };

    if (opt.argChoices && opt.argChoices.length > 0) {
      flag.arg.choices = { values: [...opt.argChoices] };
    }
  }

  // Default values
  if (opt.defaultValue != null) {
    if (isBoolean) {
      // Boolean defaults: skip false, store true as KDL #true
      if (opt.defaultValue === true) {
        flag.defaultBool = true;
      } else if (opt.defaultValue !== false) {
        flag.default = [String(opt.defaultValue)];
      }
    } else {
      flag.default = [String(opt.defaultValue)];
    }
  }

  return flag;
}

function convertCommand(cmd: Command): SpecCommand {
  const sc: SpecCommand = {
    name: cmd.name(),
    help: cmd.summary() || cmd.description() || "",
    helpLong: cmd.summary() && cmd.description() ? cmd.description() : "",
    hide: (cmd as CommandInternal)._hidden ?? false,
    deprecated: "",
    aliases: cmd.aliases(),
    subcommandRequired: false,
    flags: [],
    args: [],
    cmds: [],
  };

  // Options
  for (const opt of cmd.options) {
    if (isBuiltinOption(opt)) continue;
    sc.flags.push(convertFlag(opt));
  }

  // Arguments
  for (const arg of cmd.registeredArguments) {
    sc.args.push(convertArg(arg));
  }

  // Subcommands
  const subcommands = cmd.commands.filter((sub) => !isBuiltinCommand(sub));
  for (const sub of subcommands) {
    sc.cmds.push(convertCommand(sub));
  }

  // subcommand_required: only when not runnable and has no positional args
  if (sc.cmds.length > 0 && sc.args.length === 0 && !isRunnable(cmd)) {
    sc.subcommandRequired = true;
  }

  return sc;
}

export function convertRoot(cmd: Command): Spec {
  const spec: Spec = {
    name: cmd.name(),
    bin: cmd.name(),
    version: cmd.version() ?? "",
    about: cmd.summary() || cmd.description() || "",
    long: cmd.summary() && cmd.description() ? cmd.description() : "",
    usage: "",
    flags: [],
    args: [],
    cmds: [],
  };

  // Build usage string from Commander's helpInformation or construct it
  if (cmd.usage && typeof cmd.usage === "function") {
    spec.usage = cmd.usage() || "";
  }

  // Options
  for (const opt of cmd.options) {
    if (isBuiltinOption(opt)) continue;
    spec.flags.push(convertFlag(opt));
  }

  // Arguments
  for (const arg of cmd.registeredArguments) {
    spec.args.push(convertArg(arg));
  }

  // Subcommands
  const subcommands = cmd.commands.filter((sub) => !isBuiltinCommand(sub));
  for (const sub of subcommands) {
    spec.cmds.push(convertCommand(sub));
  }

  return spec;
}
