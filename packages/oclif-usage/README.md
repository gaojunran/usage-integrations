# @usage-spec/oclif

Generates [usage spec](https://usage.jdx.dev) for CLIs built with [oclif](https://oclif.io).

## Install

```sh
npm install @usage-spec/oclif
```

## Usage

```js
import { Config } from "@oclif/core";
import { generate } from "@usage-spec/oclif";

const config = await Config.load();
console.log(generate(config));
```

## API

### `generate(config)`

Generates a usage spec in KDL format from an oclif `Config` object.

### `generateKDL(config)`

Alias for `generate()`.

### `generateJSON(config)`

Generates a usage spec in JSON format.

### `convertRoot(config)`

Converts an oclif `Config` to the `Spec` data structure.

## Notes

The converter accepts a plain object matching the `OclifConfig` interface, so you can pass `config.commands`, `config.topics`, etc. directly from an oclif `Config` instance without depending on `@oclif/core` at compile time.

Command IDs with `:` separators are automatically organized into nested `cmd` structures. Topic descriptions are used for intermediate group nodes.

## License

MIT
