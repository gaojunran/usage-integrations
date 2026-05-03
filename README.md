# usage-spec

Monorepo for generating [usage spec](https://usage.jdx.dev) from CLI framework metadata.

## Packages

| Package | Description |
|---|---|
| [`@usage-spec/core`](packages/usage-spec/) | Shared Spec types, KDL/JSON rendering via `@bgotink/kdl` |
| [`@usage-spec/commander`](packages/commander-usage/) | Commander.js integration |
| [`@usage-spec/yargs`](packages/yargs-usage/) | yargs integration |
| [`@usage-spec/oclif`](packages/oclif-usage/) | oclif integration |

## Usage

Each adapter package provides the same API surface:

```ts
import { generate, generateKDL, generateJSON, convertRoot } from "@usage-spec/<adapter>";

// Generate KDL spec
const kdl = generate(frameworkInstance);

// Generate JSON spec
const json = generateJSON(frameworkInstance);

// Get Spec object for custom processing
const spec = convertRoot(frameworkInstance);
```

Pipe KDL output to the `usage` CLI for completions, docs, and man pages:

```sh
mycli --usage-spec | usage generate completion bash
```

## Development

```sh
aube install -r       # Install dependencies
aube run build -r     # Build all packages
aube run test -r      # Run all tests
```

## License

MIT
