# usage-spec

Monorepo for generating [usage spec](https://usage.jdx.dev) from CLI framework metadata.

## Packages

### JavaScript / TypeScript

| Package | Description |
|---|---|
| [`@usage-spec/core`](packages/usage-spec/) | Shared Spec types, KDL/JSON rendering via `@bgotink/kdl` |
| [`@usage-spec/commander`](packages/commander-usage/) | Commander.js integration |
| [`@usage-spec/yargs`](packages/yargs-usage/) | yargs integration |
| [`@usage-spec/oclif`](packages/oclif-usage/) | oclif integration |

### Python

| Package | PyPI | Description |
|---|---|---|
| [`usage-spec`](packages/usage-spec-python/) | `usage-spec` | Core Spec types and KDL/JSON rendering (Python port of `@usage-spec/core`) |
| [`usage-spec-argparse`](packages/argparse-usage/) | `usage-spec-argparse` | argparse integration |
| [`usage-spec-click`](packages/click-usage/) | `usage-spec-click` | Click integration |
| [`usage-spec-typer`](packages/typer-usage/) | `usage-spec-typer` | Typer integration (built on top of `usage-spec-click`) |

## Usage

### JavaScript / TypeScript

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

### Python

Each Python adapter package provides the same API surface:

```python
from <adapter>_usage import generate, generate_kdl, generate_json, convert_root

# Generate KDL spec (default)
kdl = generate(framework_instance)

# Generate KDL spec explicitly
kdl = generate_kdl(framework_instance)

# Generate JSON spec
json_str = generate_json(framework_instance)

# Get Spec object for custom processing
spec = convert_root(framework_instance)
```

For example, with Click:

```python
import click
from click_usage import generate

@click.group()
def cli():
    pass

# Print KDL spec
print(generate(cli, bin_name="mycli"))
```

Pipe KDL output to the `usage` CLI for completions, docs, and man pages:

```sh
mycli --usage-spec | usage generate completion bash
```

## Development

### JavaScript / TypeScript

```sh
aube install -r       # Install dependencies
aube run build -r     # Build all packages
aube run test -r      # Run all tests
```

### Python

```sh
uv sync               # Install dependencies
uv run pytest         # Run all tests
```

## License

MIT
