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
