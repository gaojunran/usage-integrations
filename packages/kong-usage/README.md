# kong-usage

Generates [usage spec](https://usage.jdx.dev) for CLIs written with [Kong](https://github.com/alecthomas/kong).

## Install

```sh
go get github.com/gaojunran/usage-integrations/packages/kong-usage
```

## Usage

```go
package main

import (
    "fmt"
    "github.com/alecthomas/kong"
    kongusage "github.com/gaojunran/usage-integrations/packages/kong-usage"
)

var cli struct {
    Verbose bool   `short:"v" help:"Enable verbose output"`
    File    string `short:"f" help:"Input file"`
}

func main() {
    k, _ := kong.New(&cli, kong.Name("mycli"), kong.Version("1.0.0"))
    fmt.Println(kongusage.GenerateKDL(k))
}
```

## API

### `GenerateKDL(k *kong.Kong, bin ...string) string`

Generates a usage spec in KDL format from a Kong application.

### `GenerateJSON(k *kong.Kong, bin ...string) string`

Generates a usage spec in JSON format.

### `Generate(k *kong.Kong, format string, comment string) string`

Generates a usage spec in the given format (`"kdl"` or `"json"`) with an optional comment header.

### `ConvertRoot(k *kong.Kong) Spec`

Converts a Kong application to the `Spec` data structure.

## Supported Features

| Kong Feature | Usage Spec Mapping |
|---|---|
| `kong.Name` | `name` / `bin` |
| `kong.Version` | `version` |
| `kong.Description` / `kong.Help` | `about` / `long_about` |
| Flag with `short:` tag | short + long name |
| `required:""` tag | `required=#true` |
| `default:"value"` tag | `default` |
| `enum:"a,b,c"` tag | `choices` + `required=#true` |
| `negatable:"_"` tag | `negate` |
| `env:"VAR"` tag | `env` |
| `hidden:""` tag | `hide=#true` |
| `deprecated:""` tag | `deprecated` |
| Cumulative flags (`IsCumulative()`) | `var=#true` |
| `help:` tag | `help` |
| Positional arguments | `arg` |
| Subcommands | `cmd` (recursive) |
| Branch nodes without Run | `subcommand_required=#true` |

## License

MIT
