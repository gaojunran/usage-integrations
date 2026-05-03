import type { Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices } from "@usage-spec/core";

// oclif types - minimal definitions for the data we need
// These match the shape of oclif's cached command data

interface OclifFlag {
  name: string;
  type: "boolean" | "option";
  char?: string;
  charAliases?: string[];
  aliases?: string[];
  summary?: string;
  description?: string;
  hidden?: boolean;
  required?: boolean;
  env?: string;
  deprecated?: boolean | { to?: string; message?: string; version?: string | number };
  // boolean-specific
  allowNo?: boolean;
  // option-specific
  default?: unknown;
  multiple?: boolean;
  options?: readonly string[];
  helpValue?: string | string[];
}

interface OclifArg {
  name: string;
  description?: string;
  hidden?: boolean;
  required?: boolean;
  multiple?: boolean;
  options?: string[];
  default?: unknown;
}

interface OclifCommand {
  id: string;
  aliases?: string[];
  hiddenAliases?: string[];
  hidden?: boolean;
  description?: string;
  summary?: string;
  state?: "beta" | "deprecated" | string;
  usage?: string | string[];
  flags: Record<string, OclifFlag>;
  args: Record<string, OclifArg>;
}

interface OclifTopic {
  name: string;
  description?: string;
  hidden?: boolean;
}

interface OclifConfig {
  bin: string;
  version: string;
  commands: OclifCommand[];
  topics: OclifTopic[];
  binAliases?: string[];
  topicSeparator?: string;
}

function convertArg(arg: OclifArg): SpecArg {
  const result: SpecArg = {
    name: arg.name,
    help: arg.description ?? "",
    required: arg.required ?? false,
    var: arg.multiple ?? false,
    hide: arg.hidden ?? false,
    default: arg.default != null ? [String(arg.default)] : [],
    choices: null,
  };

  if (arg.options && arg.options.length > 0) {
    result.choices = { values: [...arg.options] };
  }

  return result;
}

function convertFlag(flag: OclifFlag): SpecFlag {
  const isBool = flag.type === "boolean";

  const result: SpecFlag = {
    short: flag.char ?? "",
    long: flag.name,
    help: flag.summary ?? flag.description ?? "",
    helpLong: flag.summary && flag.description ? flag.description : "",
    required: flag.required ?? false,
    hide: flag.hidden ?? false,
    global: false,
    count: false,
    var: flag.multiple ?? false,
    negate: flag.allowNo ? `--${flag.name}` : "",
    deprecated: typeof flag.deprecated === "object" && flag.deprecated.message
      ? flag.deprecated.message
      : "",
    default: [],
    defaultBool: null,
    env: flag.env ?? "",
    arg: null,
  };

  // Non-boolean options have an argument
  if (!isBool) {
    const argName = (flag.helpValue && typeof flag.helpValue === "string"
      ? flag.helpValue.replace(/[<>]/g, "")
      : flag.name).replace(/-/g, "_").toUpperCase();
    result.arg = {
      name: argName,
      help: "",
      required: flag.required ?? false,
      var: flag.multiple ?? false,
      hide: false,
      default: [],
      choices: null,
    };

    if (flag.options && flag.options.length > 0) {
      result.arg.choices = { values: [...flag.options] };
    }
  }

  // Default values
  if (flag.default != null) {
    if (isBool) {
      if (flag.default === true) {
        result.defaultBool = true;
      }
    } else {
      result.default = [String(flag.default)];
    }
  }

  return result;
}

// Build nested command tree from flat oclif command list
function buildCommandTree(
  commands: OclifCommand[],
  topics: OclifTopic[],
  separator: string,
): SpecCommand[] {
  const topicMap = new Map<string, OclifTopic>();
  for (const t of topics) {
    topicMap.set(t.name, t);
  }

  // Group commands by their top-level segment
  const rootCommands = new Map<string, OclifCommand[]>();
  const rootTopics = new Map<string, OclifTopic>();

  for (const cmd of commands) {
    const parts = cmd.id.split(separator);
    const root = parts[0];

    if (!rootCommands.has(root)) {
      rootCommands.set(root, []);
    }
    rootCommands.get(root)!.push(cmd);

    // Track topics at the root level
    const topic = topicMap.get(root);
    if (topic) {
      rootTopics.set(root, topic);
    }
  }

  const result: SpecCommand[] = [];

  for (const [rootName, cmds] of rootCommands) {
    // Check if this root has direct commands (id === rootName) or only nested
    const directCmd = cmds.find((c) => c.id === rootName);
    const nestedCmds = cmds.filter((c) => c.id !== rootName);
    const topic = rootTopics.get(rootName);

    if (directCmd) {
      // This is a leaf command at this level
      result.push(convertCommand(directCmd, topic));
    } else if (nestedCmds.length > 0) {
      // This is a topic/group with no direct command
      result.push(buildTopicNode(rootName, nestedCmds, topicMap, separator));
    }
  }

  return result;
}

function buildTopicNode(
  name: string,
  commands: OclifCommand[],
  topicMap: Map<string, OclifTopic>,
  separator: string,
): SpecCommand {
  const topic = topicMap.get(name);

  const sc: SpecCommand = {
    name: name.split(separator).pop()!,
    help: topic?.description ?? "",
    helpLong: "",
    hide: topic?.hidden ?? false,
    deprecated: "",
    aliases: [],
    subcommandRequired: true,
    flags: [],
    args: [],
    cmds: [],
  };

  // Group by next segment
  const nextLevel = new Map<string, OclifCommand[]>();

  for (const cmd of commands) {
    const prefix = name + separator;
    const rest = cmd.id.slice(prefix.length);

    if (!rest) continue; // Direct command at this level (shouldn't happen here)

    const nextSegment = rest.split(separator)[0];
    const nextFull = name + separator + nextSegment;

    if (!nextLevel.has(nextFull)) {
      nextLevel.set(nextFull, []);
    }
    nextLevel.get(nextFull)!.push(cmd);
  }

  for (const [nextName, cmds] of nextLevel) {
    const directCmd = cmds.find((c) => c.id === nextName);
    const nestedCmds = cmds.filter((c) => c.id !== nextName);
    const nextTopic = topicMap.get(nextName);

    if (directCmd) {
      sc.cmds.push(convertCommand(directCmd, nextTopic));
    } else if (nestedCmds.length > 0) {
      sc.cmds.push(buildTopicNode(nextName, nestedCmds, topicMap, separator));
    }
  }

  return sc;
}

function convertCommand(cmd: OclifCommand, topic?: OclifTopic): SpecCommand {
  const sc: SpecCommand = {
    name: cmd.id.split(":").pop()!,
    help: cmd.summary ?? cmd.description ?? "",
    helpLong: cmd.summary && cmd.description ? cmd.description : "",
    hide: cmd.hidden ?? false,
    deprecated: cmd.state === "deprecated" ? "deprecated" : "",
    aliases: (cmd.aliases ?? []).filter((a) => !a.includes(":")),
    subcommandRequired: false,
    flags: [],
    args: [],
    cmds: [],
  };

  // Convert flags - skip built-in
  for (const [name, flag] of Object.entries(cmd.flags)) {
    if (name === "help" || name === "version") continue;
    sc.flags.push(convertFlag(flag));
  }

  // Convert args
  for (const arg of Object.values(cmd.args)) {
    sc.args.push(convertArg(arg));
  }

  return sc;
}

export function convertRoot(config: OclifConfig): Spec {
  const separator = config.topicSeparator ?? ":";

  // Exclude root command (id === bin) from subcommand tree
  const subcommands = config.commands.filter((c) => c.id !== config.bin);

  const spec: Spec = {
    name: config.bin,
    bin: config.bin,
    version: config.version ?? "",
    about: "",
    long: "",
    usage: "",
    flags: [],
    args: [],
    cmds: buildCommandTree(subcommands, config.topics, separator),
  };

  // Find root-level command ($0 equivalent)
  const rootCmd = config.commands.find((c) => c.id === config.bin);
  if (rootCmd) {
    spec.about = rootCmd.summary ?? rootCmd.description ?? "";
    spec.long = rootCmd.summary && rootCmd.description ? rootCmd.description : "";
    spec.flags = Object.entries(rootCmd.flags)
      .filter(([name]) => name !== "help" && name !== "version")
      .map(([, flag]) => convertFlag(flag));
    spec.args = Object.values(rootCmd.args).map(convertArg);
  }

  return spec;
}

// Re-export types for consumers
export type { OclifConfig, OclifCommand, OclifFlag, OclifArg, OclifTopic };
