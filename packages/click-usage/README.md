# usage-spec-click

Generates [usage spec](https://usage.jdx.dev) for CLIs written with [click](https://click.palletsprojects.com/).

## Install

```sh
pip install usage-spec-click
```

## Usage

```python
import click
from click_usage import generate

@click.command()
@click.version_option("1.0.0")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option("-f", "--file", type=str, help="Input file")
@click.option("--color/--no-color", default=False, help="Color output")
def cli(verbose, file, color):
    pass

print(generate(cli, "mycli"))
```

## API

### `generate(cmd, bin_name=None)`

Generates a usage spec in KDL format from a click `Command` or `Group`.

### `generate_kdl(cmd, bin_name=None)`

Alias for `generate()`.

### `generate_json(cmd, bin_name=None)`

Generates a usage spec in JSON format.

### `convert_root(cmd, bin_name=None)`

Converts a click `Command` or `Group` to the `Spec` data structure.

## Supported Features

| click Feature | Usage Spec Mapping |
|---|---|
| `cmd.name` | `name` / `bin` |
| `@click.version_option()` | `version` |
| `cmd.short_help` / `cmd.help` | `about` / `long_about` |
| `@click.option()` | `flag` |
| `required=True` | `flag required=#true` |
| `is_flag=True` | Boolean flag (no arg) |
| `--flag/--no-flag` | `negate` |
| `count=True` | `count=#true` |
| `multiple=True` | `var=#true` |
| `type=click.Choice()` | `choices` |
| `default=...` | `default` |
| `hidden=True` | `hide=#true` |
| `deprecated="..."` | `deprecated` |
| `envvar="..."` | `env` |
| `@click.argument()` | `arg` |
| `@click.group()` subcommands | `cmd` (recursive) |
| Groups without positional args | `subcommand_required=#true` |
| `cmd.hidden` | Commands hidden from listing |

## License

MIT
