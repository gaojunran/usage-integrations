# urfavecli-usage

Generates [usage spec](https://usage.jdx.dev) for CLIs written with [urfave/cli v2](https://github.com/urfave/cli).

## Install

```sh
go get github.com/gaojunran/usage-integrations/packages/urfavecli-usage
```

## Usage

```go
package main

import (
    "fmt"
    cli "github.com/urfave/cli/v2"
    cliusage "github.com/gaojunran/usage-integrations/packages/urfavecli-usage"
)

func main() {
    app := &cli.App{
        Name:    "mycli",
        Version: "1.0.0",
        Usage:   "My CLI tool",
        Flags: []cli.Flag{
            &cli.BoolFlag{Name: "verbose", Aliases: []string{"v"}, Usage: "Enable verbose output"},
            &cli.StringFlag{Name: "file", Aliases: []string{"f"}, Usage: "Input file"},
        },
    }

    fmt.Println(cliusage.GenerateKDL(app))
}
```

## API

### `GenerateKDL(app *cli.App, bin ...string) string`

Generates a usage spec in KDL format from a urfave/cli app.

### `GenerateJSON(app *cli.App, bin ...string) string`

Generates a usage spec in JSON format.

### `Generate(app *cli.App, format string, comment string) string`

Generates a usage spec in the given format (`"kdl"` or `"json"`) with an optional comment header.

### `ConvertRoot(app *cli.App) Spec`

Converts a urfave/cli app to the `Spec` data structure.

## Supported Features

| urfave/cli Feature | Usage Spec Mapping |
|---|---|
| `app.Name` | `name` / `bin` |
| `app.Version` | `version` |
| `app.Usage` / `app.Description` | `about` / `long_about` |
| Flag with `Aliases` | short + long name |
| `Required: true` | `required=#true` |
| `Value` (default) | `default` |
| `EnvVars` | `env` |
| `Hidden: true` | `hide=#true` |
| `BoolFlag.Count` | `count=#true` |
| Slice flags (`StringSliceFlag`, etc.) | `var=#true` |
| `ArgsUsage` | `arg` |
| Command `Aliases` | `alias` |
| Command `Hidden` | `hide=#true` |
| Subcommands | `cmd` (recursive) |
| Commands without `Action` | `subcommand_required=#true` |

## License

MIT
