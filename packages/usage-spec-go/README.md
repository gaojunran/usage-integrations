# usage-spec-go

Core types and rendering for [usage spec](https://usage.jdx.dev) in Go.

KDL rendering uses [calico32/kdl-go](https://github.com/calico32/kdl-go).

## Install

```sh
go get github.com/gaojunran/usage-integrations/packages/usage-spec-go
```

## API

### Types

```go
type Spec struct {
    Name    string
    Bin     string
    Version string
    About   string
    Long    string
    Usage   string
    Flags   []SpecFlag
    Args    []SpecArg
    Cmds    []SpecCommand
}

type SpecFlag struct {
    Short       string
    Long        string
    Help        string
    HelpLong    string
    Required    bool
    Hide        bool
    Global      bool
    Count       bool
    Var         bool
    Negate      string
    Deprecated  string
    Default     []string
    DefaultBool *bool
    Env         string
    Arg         *SpecArg
}

type SpecArg struct {
    Name     string
    Help     string
    Required bool
    Var      bool
    Hide     bool
    Default  []string
    Choices  *SpecChoices
}

type SpecCommand struct {
    Name               string
    Help               string
    HelpLong           string
    Hide               bool
    Deprecated         string
    Aliases            []string
    SubcommandRequired bool
    Flags              []SpecFlag
    Args               []SpecArg
    Cmds               []SpecCommand
}
```

### Functions

```go
// Render Spec as KDL string
func RenderKDL(spec Spec) string

// Render Spec as JSON string
func RenderJSON(spec Spec) string

// Generate spec output with optional comment header
func Generate(spec Spec, format string, comment string) string

// Validate KDL string by parsing it
func ValidateKDL(kdl string)
```

## License

MIT
