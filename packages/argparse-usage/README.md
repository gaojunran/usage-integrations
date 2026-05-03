# usage-spec-argparse

Generates [usage spec](https://usage.jdx.dev) for CLIs written with [argparse](https://docs.python.org/3/library/argparse.html).

## Install

```sh
pip install usage-spec-argparse
```

## Usage

```python
import argparse
from argparse_usage import generate

parser = argparse.ArgumentParser(prog="mycli", description="My CLI tool")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("-f", "--file", help="Input file")
parser.add_argument("--no-color", action="store_false", help="Disable colored output")

print(generate(parser))
```

## API

### `generate(parser, bin_name=None)`

Generates a usage spec in KDL format from an `argparse.ArgumentParser`.

### `generate_kdl(parser, bin_name=None)`

Alias for `generate()`.

### `generate_json(parser, bin_name=None)`

Generates a usage spec in JSON format.

### `convert_root(parser, bin_name=None)`

Converts an `argparse.ArgumentParser` to the `Spec` data structure.

## Supported Features

| argparse Feature | Usage Spec Mapping |
|---|---|
| `prog` | `name` / `bin` |
| `--version` action | `version` |
| `description` | `about` |
| `epilog` | `long_about` |
| `add_argument()` (optional) | `flag` |
| `add_argument()` (positional) | `arg` |
| `required=True` | `flag required=#true` |
| `action="store_true"/"store_false"` | Boolean flag (no arg) |
| `action="store_false"` | `negate` |
| `action="count"` | `count=#true` |
| `nargs="?"` | `required=#false` |
| `nargs="*"/"+"` | `var=#true` |
| `choices=[...]` | `choices` |
| `default=...` | `default` |
| `help=SUPPRESS` | `hide=#true` |
| `add_subparsers()` | `cmd` (recursive) |
| Non-runnable subcommand groups | `subcommand_required=#true` |

## License

MIT
