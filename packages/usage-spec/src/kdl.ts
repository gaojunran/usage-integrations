import { Document, Node, format, parse } from "@bgotink/kdl";
import type { Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices } from "./spec.js";

function buildChoicesNode(choices: SpecChoices): Node {
  const node = Node.create("choices");
  for (const c of choices.values) {
    node.addArgument(c);
  }
  return node;
}

function buildArgNode(arg: SpecArg): Node {
  // Build usage string: <required> or [optional], with … for variadic
  let usage: string;
  if (arg.required) {
    usage = `<${arg.name}>`;
  } else {
    usage = `[${arg.name}]`;
  }
  if (arg.var) {
    usage += "\u2026";
  }

  const node = Node.create("arg");
  node.addArgument(usage);

  if (arg.help) node.setProperty("help", arg.help);
  if (!arg.required) node.setProperty("required", false);
  if (arg.var) node.setProperty("var", true);
  if (arg.hide) node.setProperty("hide", true);
  if (arg.default.length === 1) node.setProperty("default", arg.default[0]);

  const hasChildren = arg.choices != null || arg.default.length > 1;
  if (hasChildren) {
    const children = new Document();

    if (arg.default.length > 1) {
      const defaultNode = Node.create("default");
      for (const d of arg.default) {
        defaultNode.addArgument(d);
      }
      children.appendNode(defaultNode);
    }

    if (arg.choices) {
      children.appendNode(buildChoicesNode(arg.choices));
    }

    node.children = children;
  }

  return node;
}

function buildFlagArgNode(arg: SpecArg): Node {
  const node = Node.create("arg");
  node.addArgument(`<${arg.name}>`);

  if (arg.help) node.setProperty("help", arg.help);

  if (arg.choices) {
    const children = new Document();
    children.appendNode(buildChoicesNode(arg.choices));
    node.children = children;
  }

  return node;
}

function buildFlagNode(flag: SpecFlag): Node {
  // Build the flag name: "-s --long"
  const nameParts: string[] = [];
  if (flag.short) nameParts.push(`-${flag.short}`);
  if (flag.long) nameParts.push(`--${flag.long}`);
  const flagName = nameParts.join(" ");

  const node = Node.create("flag");
  node.addArgument(flagName);

  if (flag.help) node.setProperty("help", flag.help);
  if (flag.required) node.setProperty("required", true);
  if (flag.var) node.setProperty("var", true);
  if (flag.hide) node.setProperty("hide", true);
  if (flag.global) node.setProperty("global", true);
  if (flag.count) node.setProperty("count", true);
  if (flag.negate) node.setProperty("negate", flag.negate);
  if (flag.deprecated) node.setProperty("deprecated", flag.deprecated);
  if (flag.default.length === 1) node.setProperty("default", flag.default[0]);
  else if (flag.defaultBool != null) node.setProperty("default", flag.defaultBool);
  if (flag.env) node.setProperty("env", flag.env);

  const hasChildren =
    flag.helpLong !== "" || flag.arg != null || flag.default.length > 1;

  if (hasChildren) {
    const children = new Document();

    if (flag.helpLong) {
      const longHelpNode = Node.create("long_help");
      longHelpNode.addArgument(flag.helpLong);
      children.appendNode(longHelpNode);
    }

    if (flag.default.length > 1) {
      const defaultNode = Node.create("default");
      for (const d of flag.default) {
        defaultNode.addArgument(d);
      }
      children.appendNode(defaultNode);
    }

    if (flag.arg) {
      children.appendNode(buildFlagArgNode(flag.arg));
    }

    node.children = children;
  }

  return node;
}

function buildCommandNode(cmd: SpecCommand): Node {
  const node = Node.create("cmd");
  node.addArgument(cmd.name);

  if (cmd.hide) node.setProperty("hide", true);
  if (cmd.subcommandRequired) node.setProperty("subcommand_required", true);
  if (cmd.help) node.setProperty("help", cmd.help);
  if (cmd.deprecated) node.setProperty("deprecated", cmd.deprecated);

  const hasChildren =
    cmd.helpLong !== "" ||
    cmd.aliases.length > 0 ||
    cmd.flags.length > 0 ||
    cmd.args.length > 0 ||
    cmd.cmds.length > 0;

  if (hasChildren) {
    const children = new Document();

    if (cmd.aliases.length > 0) {
      const aliasNode = Node.create("alias");
      for (const a of cmd.aliases) {
        aliasNode.addArgument(a);
      }
      children.appendNode(aliasNode);
    }

    if (cmd.helpLong) {
      const longHelpNode = Node.create("long_help");
      longHelpNode.addArgument(cmd.helpLong);
      children.appendNode(longHelpNode);
    }

    for (const flag of cmd.flags) {
      children.appendNode(buildFlagNode(flag));
    }

    for (const arg of cmd.args) {
      children.appendNode(buildArgNode(arg));
    }

    for (const sub of cmd.cmds) {
      children.appendNode(buildCommandNode(sub));
    }

    node.children = children;
  }

  return node;
}

export function renderKDL(spec: Spec): string {
  const doc = new Document();

  if (spec.name) {
    const nameNode = Node.create("name");
    nameNode.addArgument(spec.name);
    doc.appendNode(nameNode);
  }

  if (spec.bin) {
    const binNode = Node.create("bin");
    binNode.addArgument(spec.bin);
    doc.appendNode(binNode);
  }

  if (spec.version) {
    const versionNode = Node.create("version");
    versionNode.addArgument(spec.version);
    doc.appendNode(versionNode);
  }

  if (spec.about) {
    const aboutNode = Node.create("about");
    aboutNode.addArgument(spec.about);
    doc.appendNode(aboutNode);
  }

  if (spec.long) {
    const longAboutNode = Node.create("long_about");
    longAboutNode.addArgument(spec.long);
    doc.appendNode(longAboutNode);
  }

  if (spec.usage) {
    const usageNode = Node.create("usage");
    usageNode.addArgument(spec.usage);
    doc.appendNode(usageNode);
  }

  for (const flag of spec.flags) {
    doc.appendNode(buildFlagNode(flag));
  }

  for (const arg of spec.args) {
    doc.appendNode(buildArgNode(arg));
  }

  for (const cmd of spec.cmds) {
    doc.appendNode(buildCommandNode(cmd));
  }

  return format(doc);
}

/**
 * Validates KDL output by parsing it back.
 * Throws if the KDL is invalid.
 */
export function validateKDL(kdl: string): void {
  parse(kdl);
}
