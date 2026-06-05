package kongusage

import (
	"strings"

	"github.com/alecthomas/kong"
	usagespec "github.com/gaojunran/usage-integrations/packages/usage-spec-go"
)

func convertKongFlag(flag *kong.Flag) usagespec.SpecFlag {
	sf := usagespec.SpecFlag{
		Short:       shortName(flag),
		Long:        flag.Name,
		Help:        flag.Help,
		Required:    flag.Required,
		Hide:        flag.Hidden,
		Global:      false,
		Count:       flag.IsCounter(),
		Var:         flag.Value.IsCumulative(),
		Negate:      "",
		Deprecated:  "",
		Default:     nil,
		DefaultBool: nil,
		Env:         "",
		Arg:         nil,
	}

	if flag.Tag != nil && flag.Tag.Negatable != "" {
		if flag.Tag.Negatable == "_" {
			sf.Negate = "--no-" + flag.Name
		} else {
			sf.Negate = "--" + flag.Tag.Negatable
		}
	}

	if flag.HasDefault {
		if flag.Value.IsBool() {
			if flag.Default == "true" {
				sf.DefaultBool = usagespec.BoolPtr(true)
			}
		} else {
			sf.Default = []string{flag.Default}
		}
	}

	if len(flag.Envs) > 0 {
		sf.Env = flag.Envs[0]
	}

	if !flag.Value.IsBool() && !flag.IsCounter() {
		argName := strings.ToUpper(strings.ReplaceAll(flag.Name, "-", "_"))
		arg := usagespec.SpecArg{
			Name:     argName,
			Required: flag.Required,
			Var:      flag.Value.IsSlice(),
		}
		if flag.Value.Enum != "" {
			choices := flag.Value.EnumSlice()
			arg.Choices = &usagespec.SpecChoices{Values: choices}
		}
		sf.Arg = &arg
	}

	return sf
}

func shortName(flag *kong.Flag) string {
	if flag.Short != 0 {
		return string(flag.Short)
	}
	return ""
}

func convertPositional(pos *kong.Positional) usagespec.SpecArg {
	arg := usagespec.SpecArg{
		Name:     pos.Name,
		Help:     pos.Help,
		Required: pos.Required,
		Var:      pos.IsCumulative(),
		Hide:     pos.Tag != nil && pos.Tag.Hidden,
		Default:  nil,
		Choices:  nil,
	}

	if pos.HasDefault {
		arg.Default = []string{pos.Default}
	}

	if pos.Enum != "" {
		choices := pos.EnumSlice()
		arg.Choices = &usagespec.SpecChoices{Values: choices}
	}

	return arg
}

func convertNode(node *kong.Node) usagespec.SpecCommand {
	sc := usagespec.SpecCommand{
		Name:               node.Name,
		Help:               node.Help,
		HelpLong:           "",
		Hide:               node.Hidden,
		Deprecated:         "",
		Aliases:            node.Aliases,
		SubcommandRequired: false,
		Flags:              nil,
		Args:               nil,
		Cmds:               nil,
	}

	if node.Detail != "" {
		sc.HelpLong = node.Detail
	}

	for _, flag := range node.Flags {
		if isBuiltinFlag(flag) {
			continue
		}
		sc.Flags = append(sc.Flags, convertKongFlag(flag))
	}

	for _, pos := range node.Positional {
		sc.Args = append(sc.Args, convertPositional(pos))
	}

	for _, child := range node.Children {
		sc.Cmds = append(sc.Cmds, convertNode(child))
	}

	if len(sc.Cmds) > 0 && len(sc.Args) == 0 && node.Leaf() {
		sc.SubcommandRequired = true
	}

	return sc
}

func isBuiltinFlag(flag *kong.Flag) bool {
	return flag.Name == "help"
}

func Convert(k *kong.Kong) usagespec.Spec {
	app := k.Model
	spec := usagespec.Spec{
		Name:    app.Name,
		Bin:     app.Name,
		Version: "",
		About:   app.Help,
		Long:    "",
		Usage:   "",
		Flags:   nil,
		Args:    nil,
		Cmds:    nil,
	}

	if app.Detail != "" {
		spec.Long = app.Detail
	}

	for _, flag := range app.Flags {
		if isBuiltinFlag(flag) {
			continue
		}
		spec.Flags = append(spec.Flags, convertKongFlag(flag))
	}

	for _, pos := range app.Positional {
		spec.Args = append(spec.Args, convertPositional(pos))
	}

	for _, child := range app.Children {
		spec.Cmds = append(spec.Cmds, convertNode(child))
	}

	return spec
}
