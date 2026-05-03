# @usage-spec/commander

Generates [usage spec](https://usage.jdx.dev) for CLIs written with [Commander.js](https://github.com/tj/commander.js).

## Install

```sh
npm install @usage-spec/commander
```

## Usage

```js
import { Command } from "commander";
import { generate } from "@usage-spec/commander";

const program = new Command("mycli")
  .version("1.0.0")
  .description("My CLI tool")
  .option("-v, --verbose", "Enable verbose output")
  .option("-f, --file <FILE>", "Input file")
  .option("--no-color", "Disable colored output");

console.log(generate(program));
```

## Integration with `usage` CLI

```js
import { generateToStdout } from "@usage-spec/commander";

if (process.argv.includes("--usage-spec")) {
  generateToStdout(program);
  process.exit(0);
}
```

```sh
mycli --usage-spec | usage generate completion bash
mycli --usage-spec | usage generate md -f -
mycli --usage-spec | usage generate man -f -
```

## API

### `generate(cmd, binName?)`

Generates a usage spec in KDL format from a Commander.js `Command`.

### `generateKDL(cmd, binName?)`

Alias for `generate()`.

### `generateJSON(cmd, binName?)`

Generates a usage spec in JSON format.

### `generateToStdout(cmd, binName?)`

Writes the KDL spec to stdout.

### `convertRoot(cmd)`

Converts a Commander.js `Command` to the `Spec` data structure.

## Supported Features

| Commander.js Feature | Usage Spec Mapping |
|---|---|
| `cmd.name()` | `name` / `bin` |
| `cmd.version()` | `version` |
| `cmd.description()` / `cmd.summary()` | `about` / `long_about` |
| `cmd.option()` | `flag` |
| `cmd.requiredOption()` | `flag required=#true` |
| `cmd.argument()` | `arg` |
| `cmd.alias()` | `alias` |
| `cmd._hidden` | `hide=#true` |
| `opt.hideHelp()` | `hide=#true` |
| `opt.env()` | `env` |
| `opt.choices()` | `choices` |
| `opt.defaultValue` | `default` |
| `--no-*` options | `negate` |
| Subcommands | `cmd` (recursive) |
| Non-runnable subcommand groups | `subcommand_required=#true` |
| `arg.choices()` | `choices` |
| `arg.defaultValue` | `default` |
| Variadic arguments | `var=#true` + ellipsis |

## License

MIT
