# @usage-spec/yargs

Generates [usage spec](https://usage.jdx.dev) for CLIs written with [yargs](https://github.com/yargs/yargs).

## Install

```sh
npm install @usage-spec/yargs
```

## Usage

```js
import yargs from "yargs";
import { generate } from "@usage-spec/yargs";

const y = yargs([])
  .scriptName("mycli")
  .version("1.0.0")
  .option("verbose", { alias: "v", type: "boolean", description: "Be verbose" })
  .option("file", { alias: "f", type: "string", description: "Input file" })
  .command("add <file>", "Add a file", () => {})
  .command("remove", "Remove files", () => {});

console.log(generate(y));
```

## API

### `generate(y, binName?)`

Generates a usage spec in KDL format from a yargs `Argv` instance.

### `generateKDL(y, binName?)`

Alias for `generate()`.

### `generateJSON(y, binName?)`

Generates a usage spec in JSON format.

### `convertRoot(y, binName?)`

Converts a yargs `Argv` to the `Spec` data structure.

## Notes

This package uses yargs internal APIs (`getOptions()`, `getInternalMethods()`) to extract command and option metadata. These APIs are not part of the stable public API and may change between yargs versions.

## License

MIT
