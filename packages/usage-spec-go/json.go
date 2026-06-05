package usagespec

import (
	"encoding/json"
)

func argToJSON(arg SpecArg) map[string]interface{} {
	result := map[string]interface{}{"name": arg.Name}
	if arg.Help != "" {
		result["help"] = arg.Help
	}
	if !arg.Required {
		result["required"] = false
	}
	if arg.Var {
		result["var"] = true
	}
	if arg.Hide {
		result["hide"] = true
	}
	if len(arg.Default) == 1 {
		result["default"] = arg.Default[0]
	}
	if len(arg.Default) > 1 {
		result["default"] = arg.Default
	}
	if arg.Choices != nil {
		result["choices"] = arg.Choices.Values
	}
	return result
}

func flagToJSON(flag SpecFlag) map[string]interface{} {
	result := map[string]interface{}{}

	var nameParts []string
	if flag.Short != "" {
		nameParts = append(nameParts, "-"+flag.Short)
	}
	if flag.Long != "" {
		nameParts = append(nameParts, "--"+flag.Long)
	}
	result["name"] = joinNonEmpty(nameParts, " ")

	if flag.Help != "" {
		result["help"] = flag.Help
	}
	if flag.HelpLong != "" {
		result["help_long"] = flag.HelpLong
	}
	if flag.Required {
		result["required"] = true
	}
	if flag.Hide {
		result["hide"] = true
	}
	if flag.Global {
		result["global"] = true
	}
	if flag.Count {
		result["count"] = true
	}
	if flag.Var {
		result["var"] = true
	}
	if flag.Negate != "" {
		result["negate"] = flag.Negate
	}
	if flag.Deprecated != "" {
		result["deprecated"] = flag.Deprecated
	}
	if flag.Env != "" {
		result["env"] = flag.Env
	}
	if len(flag.Default) == 1 {
		result["default"] = flag.Default[0]
	}
	if len(flag.Default) > 1 {
		result["default"] = flag.Default
	}

	if flag.Arg != nil {
		result["arg"] = argToJSON(*flag.Arg)
	}

	return result
}

func cmdToJSON(cmd SpecCommand) map[string]interface{} {
	result := map[string]interface{}{"name": cmd.Name}
	if cmd.Help != "" {
		result["help"] = cmd.Help
	}
	if cmd.HelpLong != "" {
		result["help_long"] = cmd.HelpLong
	}
	if cmd.Hide {
		result["hide"] = true
	}
	if cmd.Deprecated != "" {
		result["deprecated"] = cmd.Deprecated
	}
	if len(cmd.Aliases) > 0 {
		result["aliases"] = cmd.Aliases
	}
	if cmd.SubcommandRequired {
		result["subcommand_required"] = true
	}
	if len(cmd.Flags) > 0 {
		flags := make([]map[string]interface{}, len(cmd.Flags))
		for i, f := range cmd.Flags {
			flags[i] = flagToJSON(f)
		}
		result["flags"] = flags
	}
	if len(cmd.Args) > 0 {
		args := make([]map[string]interface{}, len(cmd.Args))
		for i, a := range cmd.Args {
			args[i] = argToJSON(a)
		}
		result["args"] = args
	}
	if len(cmd.Cmds) > 0 {
		cmds := make([]map[string]interface{}, len(cmd.Cmds))
		for i, c := range cmd.Cmds {
			cmds[i] = cmdToJSON(c)
		}
		result["cmds"] = cmds
	}
	return result
}

func RenderJSON(spec Spec) string {
	result := map[string]interface{}{}
	if spec.Name != "" {
		result["name"] = spec.Name
	}
	if spec.Bin != "" {
		result["bin"] = spec.Bin
	}
	if spec.Version != "" {
		result["version"] = spec.Version
	}
	if spec.About != "" {
		result["about"] = spec.About
	}
	if spec.Long != "" {
		result["long_about"] = spec.Long
	}
	if spec.Usage != "" {
		result["usage"] = spec.Usage
	}
	if len(spec.Flags) > 0 {
		flags := make([]map[string]interface{}, len(spec.Flags))
		for i, f := range spec.Flags {
			flags[i] = flagToJSON(f)
		}
		result["flags"] = flags
	}
	if len(spec.Args) > 0 {
		args := make([]map[string]interface{}, len(spec.Args))
		for i, a := range spec.Args {
			args[i] = argToJSON(a)
		}
		result["args"] = args
	}
	if len(spec.Cmds) > 0 {
		cmds := make([]map[string]interface{}, len(spec.Cmds))
		for i, c := range spec.Cmds {
			cmds[i] = cmdToJSON(c)
		}
		result["cmds"] = cmds
	}

	data, _ := json.MarshalIndent(result, "", "  ")
	return string(data) + "\n"
}

func joinNonEmpty(parts []string, sep string) string {
	return join(parts, sep)
}

func join(parts []string, sep string) string {
	result := ""
	for i, p := range parts {
		if i > 0 {
			result += sep
		}
		result += p
	}
	return result
}
