# usage-spec-typer

Generates [usage spec](https://usage.jdx.dev) for CLIs written with [Typer](https://typer.tiangolo.com/).

## Install

```sh
pip install usage-spec-typer
```

## Usage

```python
import typer
from typer_usage import generate

app = typer.Typer(help="My CLI tool")

@app.command()
def hello(name: str = typer.Argument(help="Your name")):
    """Say hello"""

@app.command()
def build(
    output: str = typer.Option("dist", help="Output directory"),
    verbose: bool = typer.Option(False, help="Enable verbose output"),
):
    """Build the project"""

print(generate(app, "mycli"))
```

## API

### `generate(app, bin_name=None)`

Generates a usage spec in KDL format from a Typer `Typer` app.

### `generate_kdl(app, bin_name=None)`

Alias for `generate()`.

### `generate_json(app, bin_name=None)`

Generates a usage spec in JSON format.

### `convert_root(app, bin_name=None)`

Converts a Typer `Typer` app to the `Spec` data structure.

## Supported Features

| Typer Feature | Usage Spec Mapping |
|---|---|
| `app.info.name` / `bin_name` | `name` / `bin` |
| `app.info.help` | `about` |
| `typer.Option()` | `flag` |
| `typer.Argument()` | `arg` |
| `typer.Option(..., help=)` | Flag `help` |
| `typer.Argument(..., help=)` | Arg `help` |
| `typer.Option(...)` (ellipsis) | `flag required=#true` |
| `bool` type options | Boolean flag (no arg) |
| `--flag/--no-flag` | `negate` |
| `count=True` | `count=#true` |
| `type=click.Choice()` | `choices` |
| `default=...` | `default` |
| `hidden=True` | `hide=#true` |
| `envvar="..."` | `env` |
| `app.add_typer()` | `cmd` (recursive) |
| Subcommand groups | `subcommand_required=#true` |
| Single command app | Treated as root-level |
| `--install-completion` / `--show-completion` | Filtered out |

## License

MIT
