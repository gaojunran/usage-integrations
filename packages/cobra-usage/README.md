# cobra-usage

Generates [usage spec](https://usage.jdx.dev) for CLIs written with [Cobra](https://github.com/spf13/cobra).

## Install

```sh
go get github.com/gaojunran/usage-integrations/packages/cobra-usage
```

## Usage

```go
package main

import (
    "fmt"
    "github.com/spf13/cobra"
    cobrausage "github.com/gaojunran/usage-integrations/packages/cobra-usage"
)

func main() {
    root := &cobra.Command{
        Use:     "mycli",
        Version: "1.0.0",
        Short:   "My CLI tool",
    }
    root.Flags().BoolP("verbose", "v", false, "Enable verbose output")
    root.Flags().StringP("file", "f", "", "Input file")

    fmt.Println(cobrausage.GenerateKDL(root))
}
```

## API

### `GenerateKDL(cmd *cobra.Command, bin ...string) string`

Generates a usage spec in KDL format from a Cobra command.

### `GenerateJSON(cmd *cobra.Command, bin ...string) string`

Generates a usage spec in JSON format.

### `Generate(cmd *cobra.Command, format string, comment string) string`

Generates a usage spec in the given format (`"kdl"` or `"json"`) with an optional comment header.

### `ConvertRoot(cmd *cobra.Command) Spec`

Converts a Cobra command to the `Spec` data structure.

## Supported Features

| Cobra Feature | Usage Spec Mapping |
|---|---|
| `cmd.Use` | `name` / `bin` |
| `cmd.Version` | `version` |
| `cmd.Short` / `cmd.Long` | `about` / `long_about` |
| `cmd.Flags()` | `flag` (local, `global=#false`) |
| `cmd.PersistentFlags()` | `flag` (persistent, `global=#true`) |
| `cmd.Annotations[bashCompOneRequiredFlag]` | `required=#true` |
| `cmd.Args` (from `Use` string) | `arg` |
| `cmd.Aliases` | `alias` |
| `cmd.Hidden` | `hide=#true` |
| `flag.Hidden` | `hide=#true` |
| `flag.DefValue` | `default` |
| `flag.Shorthand` | short name |
| Subcommands | `cmd` (recursive) |
| Non-runnable subcommand groups | `subcommand_required=#true` |

## License

MIT
