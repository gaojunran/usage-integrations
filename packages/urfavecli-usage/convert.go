package cliusage

import (
	"strconv"
	"strings"

	cli "github.com/urfave/cli/v2"
	usagespec "github.com/gaojunran/usage-integrations/packages/usage-spec-go"
)

func convertCLIFlag(flag cli.Flag) usagespec.SpecFlag {
	names := flag.Names()
	short, long := splitFlagNames(names)

	sf := usagespec.SpecFlag{
		Short:       short,
		Long:        long,
		Help:        getUsage(flag),
		Required:    isRequired(flag),
		Hide:        !isVisible(flag),
		Global:      false,
		Count:       isCountFlag(flag),
		Var:         isSliceFlag(flag),
		Negate:      "",
		Deprecated:  "",
		Default:     nil,
		DefaultBool: nil,
		Env:         getEnv(flag),
		Arg:         nil,
	}

	isBool := !takesValue(flag)

	if isBool {
		defaultText := getDefaultText(flag)
		if defaultText == "true" {
			sf.DefaultBool = usagespec.BoolPtr(true)
		}
	} else {
		defaultText := getDefaultText(flag)
		if defaultText != "" {
			sf.Default = []string{defaultText}
		}

		argName := strings.ToUpper(strings.ReplaceAll(long, "-", "_"))
		sf.Arg = &usagespec.SpecArg{
			Name:     argName,
			Required: isRequired(flag),
			Var:      isSliceFlag(flag),
		}
	}

	return sf
}

func splitFlagNames(names []string) (short string, long string) {
	for _, name := range names {
		if len(name) == 1 {
			short = name
		} else if len(name) > 1 {
			long = name
		}
	}
	return
}

func getUsage(flag cli.Flag) string {
	if dg, ok := flag.(cli.DocGenerationFlag); ok {
		return dg.GetUsage()
	}
	return ""
}

func isRequired(flag cli.Flag) bool {
	if rf, ok := flag.(cli.RequiredFlag); ok {
		return rf.IsRequired()
	}
	return false
}

func isVisible(flag cli.Flag) bool {
	if vf, ok := flag.(cli.VisibleFlag); ok {
		return vf.IsVisible()
	}
	return true
}

func takesValue(flag cli.Flag) bool {
	if dg, ok := flag.(cli.DocGenerationFlag); ok {
		return dg.TakesValue()
	}
	return true
}

func getDefaultText(flag cli.Flag) string {
	if dg, ok := flag.(cli.DocGenerationFlag); ok {
		text := dg.GetDefaultText()
		if unquoted, err := strconv.Unquote(text); err == nil {
			return unquoted
		}
		return text
	}
	return ""
}

func getEnv(flag cli.Flag) string {
	type envFlag interface {
		GetEnvVars() []string
	}
	if ef, ok := flag.(envFlag); ok {
		envs := ef.GetEnvVars()
		if len(envs) > 0 {
			return envs[0]
		}
	}
	return ""
}

func isSliceFlag(flag cli.Flag) bool {
	switch flag.(type) {
	case *cli.StringSliceFlag, *cli.IntSliceFlag, *cli.Float64SliceFlag, *cli.Int64SliceFlag, *cli.UintSliceFlag:
		return true
	default:
		return false
	}
}

func isCountFlag(flag cli.Flag) bool {
	if bf, ok := flag.(*cli.BoolFlag); ok {
		return bf.Count != nil
	}
	return false
}

func isBuiltinFlag(flag cli.Flag) bool {
	names := flag.Names()
	long, _ := splitFlagNames(names)
	return long == "help" || long == "version"
}

func convertCommand(cmd *cli.Command) usagespec.SpecCommand {
	sc := usagespec.SpecCommand{
		Name:               cmd.Name,
		Help:               cmd.Usage,
		HelpLong:           cmd.Description,
		Hide:               cmd.Hidden,
		Deprecated:         "",
		Aliases:            cmd.Aliases,
		SubcommandRequired: false,
		Flags:              nil,
		Args:               nil,
		Cmds:               nil,
	}

	for _, f := range cmd.Flags {
		if isBuiltinFlag(f) {
			continue
		}
		sc.Flags = append(sc.Flags, convertCLIFlag(f))
	}

	if cmd.ArgsUsage != "" {
		sc.Args = parseArgsUsage(cmd.ArgsUsage)
	}

	for _, sub := range cmd.Subcommands {
		sc.Cmds = append(sc.Cmds, convertCommand(sub))
	}

	if len(sc.Cmds) > 0 && len(sc.Args) == 0 && cmd.Action == nil {
		sc.SubcommandRequired = true
	}

	return sc
}

func parseArgsUsage(usage string) []usagespec.SpecArg {
	usage = strings.TrimSpace(usage)
	if usage == "" {
		return nil
	}
	parts := strings.Fields(usage)
	var args []usagespec.SpecArg
	for _, part := range parts {
		required := !strings.HasPrefix(part, "[")
		name := strings.Trim(part, "[]<>")
		isVar := strings.HasSuffix(name, "...")
		if isVar {
			name = strings.TrimSuffix(name, "...")
		}
		if name == "" {
			continue
		}
		args = append(args, usagespec.SpecArg{
			Name:     name,
			Required: required,
			Var:      isVar,
		})
	}
	return args
}

func Convert(app *cli.App) usagespec.Spec {
	spec := usagespec.Spec{
		Name:    app.Name,
		Bin:     app.Name,
		Version: app.Version,
		About:   app.Usage,
		Long:    app.Description,
		Usage:   "",
		Flags:   nil,
		Args:    nil,
		Cmds:    nil,
	}

	for _, f := range app.Flags {
		if isBuiltinFlag(f) {
			continue
		}
		spec.Flags = append(spec.Flags, convertCLIFlag(f))
	}

	if app.ArgsUsage != "" {
		spec.Args = parseArgsUsage(app.ArgsUsage)
	}

	for _, cmd := range app.Commands {
		spec.Cmds = append(spec.Cmds, convertCommand(cmd))
	}

	return spec
}
