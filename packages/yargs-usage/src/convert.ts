import type { Argv } from "yargs";
import type { Spec, SpecArg, SpecFlag, SpecCommand } from "@usage-spec/core";

// yargs internal types - not exposed in public API
interface YargsOptions {
  local: string[];
  boolean: string[];
  string: string[];
  number: string[];
  count: string[];
  array: string[];
  hiddenOptions: string[];
  alias: Record<string, string[]>;
  default: Record<string, unknown>;
  choices: Record<string, (string | number)[]>;
  demandedOptions: Record<string, string | true>;
  deprecatedOptions: Record<string, string | boolean>;
  envPrefix: string | undefined;
  key: Record<string, boolean>;
  narg: Record<string, number>;
  demandedCommands: Record<string, { min: number; max: number; minMsg?: string; maxMsg?: string }>;
}

interface Positional {
  cmd: string[];
  variadic: boolean;
}

interface CommandHandler {
  original: string;
  description: string | false;
  handler: (...args: unknown[]) => void;
  builder: ((y: Argv) => Argv | void) | Record<string, unknown>;
  middlewares: unknown[];
  demanded: Positional[];
  optional: Positional[];
  deprecated: boolean | string | undefined;
}

interface CommandInstance {
  handlers: Record<string, CommandHandler>;
  aliasMap: Record<string, string>;
  defaultCommand: CommandHandler | undefined;
  getCommandHandlers(): Record<string, CommandHandler>;
  getCommands(): string[];
}

interface UsageInstance {
  getDescriptions(): Record<string, string>;
  showVersion(fn: (v: string) => void): void;
  getUsage(): [string, string][];
}

interface YargsInternal extends Argv {
  getOptions(): YargsOptions;
  getInternalMethods(): {
    getCommandInstance(): CommandInstance;
    getUsageInstance(): UsageInstance;
    reset(aliases: Record<string, string[]>): Argv;
  };
  $0: string;
}

function extractOptions(y: Argv): {
  opts: YargsOptions;
  descriptions: Record<string, string>;
} {
  const internal = y as unknown as YargsInternal;
  return {
    opts: internal.getOptions(),
    descriptions: internal.getInternalMethods().getUsageInstance().getDescriptions(),
  };
}

function isShortFlag(name: string): boolean {
  return name.length === 1;
}

function convertPositional(pos: Positional, descriptions: Record<string, string>): SpecArg {
  const name = pos.cmd[0];
  const result: SpecArg = {
    name,
    help: descriptions[name] ?? "",
    required: true, // will be overridden by caller for optional positionals
    var: pos.variadic,
    hide: false,
    default: [],
    choices: null,
  };
  return result;
}

function convertOptions(
  y: Argv,
): SpecFlag[] {
  const { opts, descriptions } = extractOptions(y);
  const flags: SpecFlag[] = [];

  // Build the set of all alias values (non-canonical names)
  const aliasValues = new Set<string>();
  for (const aliases of Object.values(opts.alias)) {
    for (const a of aliases) aliasValues.add(a);
  }

  // Canonical names: keys in opts.alias + keys in opts.key that aren't alias values or built-in
  const canonicalNames = new Set<string>();
  for (const name of Object.keys(opts.alias)) {
    canonicalNames.add(name);
  }
  for (const name of Object.keys(opts.key)) {
    if (!aliasValues.has(name)) {
      canonicalNames.add(name);
    }
  }

  for (const name of canonicalNames) {
    // Skip built-in flags
    if (name === "help" || name === "version" || name === "show-hidden" || name === "_") continue;

    // Skip if this is an alias (not canonical) - aliases appear in boolean/string arrays too
    // Canonical names are the keys in opts.alias; their values are the aliases

    const aliases = opts.alias[name] ?? [];
    const shortAliases = aliases.filter(isShortFlag);
    const longAliases = aliases.filter((a) => !isShortFlag(a));

    const isBool = opts.boolean.includes(name);
    const isCount = opts.count.includes(name);
    const isArray = opts.array.includes(name);
    const isNumber = opts.number.includes(name);
    const isString = opts.string.includes(name);
    const isRequired = name in opts.demandedOptions;
    const isHidden = opts.hiddenOptions.includes(name);

    // Determine the canonical short/long
    let short = isShortFlag(name) ? name : (shortAliases[0] ?? "");
    let long = isShortFlag(name) ? (longAliases[0] ?? "") : name;

    // If name is short and there's no long alias, check if name itself should be long
    if (isShortFlag(name) && !long) {
      short = name;
      long = "";
    }

    const desc = descriptions[name] ?? "";

    const flag: SpecFlag = {
      short,
      long,
      help: desc,
      helpLong: "",
      required: isRequired,
      hide: isHidden,
      global: false,
      count: isCount,
      var: isArray,
      negate: "",
      deprecated: typeof opts.deprecatedOptions[name] === "string"
        ? (opts.deprecatedOptions[name] as string)
        : "",
      default: [],
      defaultBool: null,
      env: opts.envPrefix ? `${opts.envPrefix}_${name.replace(/-/g, "_").toUpperCase()}` : "",
      arg: null,
    };

    // Non-boolean options have an argument
    if (!isBool && !isCount) {
      const argName = name.replace(/-/g, "_").toUpperCase();
      flag.arg = {
        name: argName,
        help: "",
        required: isRequired || name in opts.narg,
        var: isArray,
        hide: false,
        default: [],
        choices: null,
      };

      if (name in opts.choices && opts.choices[name]) {
        flag.arg.choices = { values: opts.choices[name].map(String) };
      }
    }

    // Default values
    if (name in opts.default && opts.default[name] !== undefined) {
      const def = opts.default[name];
      if (isBool || isCount) {
        if (def === true) {
          flag.defaultBool = true;
        }
        // Skip false defaults for booleans
      } else {
        flag.default = [String(def)];
      }
    }

    // Choices on the flag itself (for non-boolean)
    if (name in opts.choices && opts.choices[name] && (isBool || isCount)) {
      // Boolean/count flags shouldn't have choices; skip
    } else if (name in opts.choices && opts.choices[name] && !flag.arg) {
      // Flag doesn't have arg but has choices - unusual, skip
    }

    flags.push(flag);
  }

  return flags;
}

function convertCommand(
  name: string,
  handler: CommandHandler,
  parentYargs: Argv,
): SpecCommand {
  const sc: SpecCommand = {
    name,
    help: handler.description === false ? "" : (handler.description ?? ""),
    helpLong: "",
    hide: handler.description === false,
    deprecated: typeof handler.deprecated === "string" ? handler.deprecated : "",
    aliases: [],
    subcommandRequired: false,
    flags: [],
    args: [],
    cmds: [],
  };

  // Get command aliases from aliasMap
  const cmd = (parentYargs as unknown as YargsInternal)
    .getInternalMethods()
    .getCommandInstance();
  for (const [alias, canonical] of Object.entries(cmd.aliasMap)) {
    if (canonical === name && alias !== name) {
      sc.aliases.push(alias);
    }
  }

  // Positional arguments
  const innerYargs = getBuilderYargs(handler, parentYargs);
  const innerDescriptions = innerYargs
    ? (innerYargs as unknown as YargsInternal).getInternalMethods().getUsageInstance().getDescriptions()
    : {};

  for (const pos of handler.demanded) {
    const arg = convertPositional(pos, innerDescriptions);
    arg.required = true;
    sc.args.push(arg);
  }

  for (const pos of handler.optional) {
    const arg = convertPositional(pos, innerDescriptions);
    arg.required = false;
    sc.args.push(arg);
  }

  // Options from builder
  if (innerYargs) {
    sc.flags = convertOptions(innerYargs);

    // Recurse into subcommands
    const innerCmd = (innerYargs as unknown as YargsInternal)
      .getInternalMethods()
      .getCommandInstance();
    const innerHandlers = innerCmd.getCommandHandlers();

    for (const [cmdName, cmdHandler] of Object.entries(innerHandlers)) {
      sc.cmds.push(convertCommand(cmdName, cmdHandler, innerYargs));
    }

    // subcommand_required
    const innerOpts = (innerYargs as unknown as YargsInternal).getOptions();
    if (sc.cmds.length > 0 && sc.args.length === 0) {
      const demanded = innerOpts.demandedCommands?._;
      if (demanded && (demanded as { min: number }).min > 0) {
        sc.subcommandRequired = true;
      }
    }
  }

  return sc;
}

function getBuilderYargs(handler: CommandHandler, parentYargs: Argv): Argv | null {
  if (!handler.builder) return null;

  // Object builder - create a yargs instance from it
  if (typeof handler.builder === "object") {
    // Builder is an options object, apply it to a reset yargs
    const reset = (parentYargs as unknown as YargsInternal)
      .getInternalMethods()
      .reset({});
    return (reset as unknown as Argv).options(handler.builder as Record<string, never>);
  }

  // Function builder - call it
  if (typeof handler.builder === "function") {
    try {
      const reset = (parentYargs as unknown as YargsInternal)
        .getInternalMethods()
        .reset({});
      const result = (handler.builder as (y: Argv) => Argv | void)(reset as unknown as Argv);
      return result && typeof (result as YargsInternal).getOptions === "function"
        ? result as unknown as Argv
        : reset as unknown as Argv;
    } catch {
      return null;
    }
  }

  return null;
}

export function convertRoot(y: Argv, binName?: string): Spec {
  const internal = y as unknown as YargsInternal;
  const opts = internal.getOptions();
  const usage = internal.getInternalMethods().getUsageInstance();
  const cmd = internal.getInternalMethods().getCommandInstance();

  const descriptions = usage.getDescriptions();

  // Extract version string
  let version = "";
  usage.showVersion((v: string) => { version = v; });

  // Get the description from the usage
  // yargs stores description via .usage('description') or .usage('$0 ...', 'description')
  const usageData = usage.getUsage();
  const about = usageData.length > 0 ? usageData[0][0] : (descriptions._ ?? "");

  const spec: Spec = {
    name: binName ?? internal.$0.replace(/^.*\//, ""),
    bin: binName ?? internal.$0.replace(/^.*\//, ""),
    version,
    about: typeof about === "string" ? about : "",
    long: "",
    usage: "",
    flags: convertOptions(y),
    args: [],
    cmds: [],
  };

  // Process commands
  const handlers = cmd.getCommandHandlers();

  for (const [cmdName, handler] of Object.entries(handlers)) {
    // Skip the default command ($0) as a named subcommand
    if (cmdName === "$0") continue;

    spec.cmds.push(convertCommand(cmdName, handler, y));

    // If default command has positionals, they become root args
    if (cmd.defaultCommand && cmdName === "$0") {
      const dh = cmd.defaultCommand;
      for (const pos of dh.demanded) {
        spec.args.push({ ...convertPositional(pos, descriptions), required: true });
      }
      for (const pos of dh.optional) {
        spec.args.push({ ...convertPositional(pos, descriptions), required: false });
      }
    }
  }

  // Handle default command positionals as root args
  if (cmd.defaultCommand) {
    const dh = cmd.defaultCommand;
    for (const pos of dh.demanded) {
      spec.args.push({ ...convertPositional(pos, descriptions), required: true });
    }
    for (const pos of dh.optional) {
      spec.args.push({ ...convertPositional(pos, descriptions), required: false });
    }

    // Get flags from default command builder
    const builderYargs = getBuilderYargs(dh, y);
    if (builderYargs) {
      spec.flags.push(...convertOptions(builderYargs));
    }
  }

  // subcommand_required for root
  if (spec.cmds.length > 0 && spec.args.length === 0) {
    const demanded = opts.demandedCommands?._;
    if (demanded && (demanded as { min: number }).min > 0) {
      // Root has required subcommands
    }
  }

  return spec;
}
