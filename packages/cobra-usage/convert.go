package cobrausage

import (
	"regexp"
	"strings"

	"github.com/spf13/cobra"
	"github.com/spf13/pflag"
	usagespec "github.com/gaojunran/usage-integrations/packages/usage-spec-go"
)

var builtinFlagNames = map[string]bool{
	"help": true,
}

var argPattern = regexp.MustCompile(`\[([^\]]+)\]|<([^>]+)>`)

var requiredFlagAnnotation = "cobra_annotation_bash_completion_one_required_flag"

func extractArgsFromUse(use string) []usagespec.SpecArg {
	parts := strings.Fields(use)
	if len(parts) <= 1 {
		return nil
	}
	var args []usagespec.SpecArg
	for _, part := range parts[1:] {
		matches := argPattern.FindStringSubmatch(part)
		if matches == nil {
			continue
		}
		name := ""
		required := false
		isVar := false

		if matches[1] != "" {
			name = matches[1]
			required = false
		} else if matches[2] != "" {
			name = matches[2]
			required = true
		}

		if strings.HasSuffix(name, "...") {
			name = strings.TrimSuffix(name, "...")
			isVar = true
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

func isBooleanFlag(flag *pflag.Flag) bool {
	return flag.Value.Type() == "bool"
}

func isRequiredFlag(flag *pflag.Flag) bool {
	if flag.Annotations == nil {
		return false
	}
	vals, ok := flag.Annotations[requiredFlagAnnotation]
	if !ok {
		return false
	}
	for _, v := range vals {
		if v == "true" {
			return true
		}
	}
	return false
}

func isBuiltinFlag(flag *pflag.Flag) bool {
	return builtinFlagNames[flag.Name]
}

func isBuiltinCommand(cmd *cobra.Command) bool {
	name := cmd.Name()
	if name == "help" && !cmd.Runnable() {
		return true
	}
	if name == "completion" && !cmd.Runnable() {
		return true
	}
	return false
}

func convertFlag(flag *pflag.Flag, global bool) usagespec.SpecFlag {
	sf := usagespec.SpecFlag{
		Short:       flag.Shorthand,
		Long:        flag.Name,
		Help:        flag.Usage,
		Required:    isRequiredFlag(flag),
		Hide:        flag.Hidden,
		Global:      global,
		Count:       false,
		Var:         flag.Value.Type() == "stringArray" || flag.Value.Type() == "stringSlice",
		Negate:      "",
		Deprecated:  flag.Deprecated,
		Default:     nil,
		DefaultBool: nil,
		Env:         "",
		Arg:         nil,
	}

	if isBooleanFlag(flag) {
		if flag.DefValue == "true" {
			sf.DefaultBool = usagespec.BoolPtr(true)
		}
	} else {
		if flag.DefValue != "" {
			sf.Default = []string{flag.DefValue}
		}

		argName := strings.ToUpper(strings.ReplaceAll(flag.Name, "-", "_"))
		sf.Arg = &usagespec.SpecArg{
			Name:     argName,
			Required: isRequiredFlag(flag),
		}
	}

	return sf
}

func collectFlags(cmd *cobra.Command) []usagespec.SpecFlag {
	var flags []usagespec.SpecFlag
	seen := map[string]bool{}

	if cmd.Flags() != nil {
		cmd.Flags().VisitAll(func(f *pflag.Flag) {
			if isBuiltinFlag(f) {
				return
			}
			if seen[f.Name] {
				return
			}
			seen[f.Name] = true
			flags = append(flags, convertFlag(f, false))
		})
	}
	if cmd.PersistentFlags() != nil {
		cmd.PersistentFlags().VisitAll(func(f *pflag.Flag) {
			if isBuiltinFlag(f) {
				return
			}
			if seen[f.Name] {
				return
			}
			seen[f.Name] = true
			flags = append(flags, convertFlag(f, true))
		})
	}

	return flags
}

func convertCommand(cmd *cobra.Command) usagespec.SpecCommand {
	sc := usagespec.SpecCommand{
		Name:               cmd.Name(),
		Help:               cmd.Short,
		HelpLong:           "",
		Hide:               cmd.Hidden,
		Deprecated:         cmd.Deprecated,
		Aliases:            cmd.Aliases,
		SubcommandRequired: false,
		Flags:              nil,
		Args:               nil,
		Cmds:               nil,
	}

	if cmd.Short != "" && cmd.Long != "" {
		sc.HelpLong = cmd.Long
	} else if cmd.Long != "" && cmd.Short == "" {
		sc.Help = cmd.Long
		sc.HelpLong = ""
	}

	sc.Flags = collectFlags(cmd)
	sc.Args = extractArgsFromUse(cmd.Use)

	for _, sub := range cmd.Commands() {
		if isBuiltinCommand(sub) {
			continue
		}
		if sub.Deprecated != "" && sub.Hidden {
			continue
		}
		sc.Cmds = append(sc.Cmds, convertCommand(sub))
	}

	if len(sc.Cmds) > 0 && len(sc.Args) == 0 && !cmd.Runnable() {
		sc.SubcommandRequired = true
	}

	return sc
}

func Convert(cmd *cobra.Command) usagespec.Spec {
	spec := usagespec.Spec{
		Name:    cmd.Name(),
		Bin:     cmd.Name(),
		Version: cmd.Version,
		About:   cmd.Short,
		Long:    "",
		Usage:   "",
		Flags:   nil,
		Args:    nil,
		Cmds:    nil,
	}

	if cmd.Short != "" && cmd.Long != "" {
		spec.Long = cmd.Long
	} else if cmd.Long != "" && cmd.Short == "" {
		spec.About = cmd.Long
		spec.Long = ""
	}

	spec.Flags = collectFlags(cmd)
	spec.Args = extractArgsFromUse(cmd.Use)

	for _, sub := range cmd.Commands() {
		if isBuiltinCommand(sub) {
			continue
		}
		if sub.Deprecated != "" && sub.Hidden {
			continue
		}
		spec.Cmds = append(spec.Cmds, convertCommand(sub))
	}

	return spec
}
