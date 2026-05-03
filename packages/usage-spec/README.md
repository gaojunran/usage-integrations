# @usage-spec/core

Core types and rendering for [usage spec](https://usage.jdx.dev).

## Install

```sh
npm install @usage-spec/core
```

## API

### Types

```ts
interface Spec {
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
```

### Functions

```ts
// Render Spec as KDL string
renderKDL(spec: Spec): string

// Render Spec as JSON string
renderJSON(spec: Spec): string

// Generate spec output with optional comment header
generate(spec: Spec, options?: { format?: "kdl" | "json"; comment?: string }): string

// Validate KDL string by parsing it back
validateKDL(kdl: string): void
```

## License

MIT
