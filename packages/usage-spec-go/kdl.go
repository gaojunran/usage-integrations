package usagespec

import (
	"strings"

	kdl "github.com/calico32/kdl-go"
)

func RenderKDL(spec Spec) string {
	doc := buildSpecDocument(spec)
	s, err := kdl.EmitToString(doc, kdl.WithIndent("    "))
	if err != nil {
		panic("usage-spec: failed to emit KDL: " + err.Error())
	}
	return s
}

func ValidateKDL(kdlStr string) {
	kdlStr = strings.TrimSpace(kdlStr)
	if kdlStr == "" {
		return
	}
	_, err := kdl.ParseString(kdlStr)
	if err != nil {
		panic("usage-spec: invalid KDL output: " + err.Error())
	}
}

func buildSpecDocument(spec Spec) *kdl.Document {
	doc := kdl.NewDocument()
	if spec.Name != "" {
		doc.AddNode(kdl.NewKV("name", spec.Name))
	}
	if spec.Bin != "" {
		doc.AddNode(kdl.NewKV("bin", spec.Bin))
	}
	if spec.Version != "" {
		doc.AddNode(kdl.NewKV("version", spec.Version))
	}
	if spec.About != "" {
		doc.AddNode(kdl.NewKV("about", spec.About))
	}
	if spec.Long != "" {
		doc.AddNode(kdl.NewKV("long_about", spec.Long))
	}
	if spec.Usage != "" {
		doc.AddNode(kdl.NewKV("usage", spec.Usage))
	}
	for _, flag := range spec.Flags {
		doc.AddNode(buildFlagNode(flag))
	}
	for _, arg := range spec.Args {
		doc.AddNode(buildArgNode(arg))
	}
	for _, cmd := range spec.Cmds {
		doc.AddNode(buildCommandNode(cmd))
	}
	return doc
}

func buildFlagNode(flag SpecFlag) *kdl.Node {
	var nameParts []string
	if flag.Short != "" {
		nameParts = append(nameParts, "-"+flag.Short)
	}
	if flag.Long != "" {
		nameParts = append(nameParts, "--"+flag.Long)
	}
	flagName := strings.Join(nameParts, " ")

	node := kdl.NewNode("flag", kdl.NewString(flagName))

	if flag.Help != "" {
		node.AddProperty("help", kdl.NewString(flag.Help))
	}
	if flag.Required {
		node.AddProperty("required", kdl.NewBool(true))
	}
	if flag.Var {
		node.AddProperty("var", kdl.NewBool(true))
	}
	if flag.Hide {
		node.AddProperty("hide", kdl.NewBool(true))
	}
	if flag.Global {
		node.AddProperty("global", kdl.NewBool(true))
	}
	if flag.Count {
		node.AddProperty("count", kdl.NewBool(true))
	}
	if flag.Negate != "" {
		node.AddProperty("negate", kdl.NewString(flag.Negate))
	}
	if flag.Deprecated != "" {
		node.AddProperty("deprecated", kdl.NewString(flag.Deprecated))
	}
	if len(flag.Default) == 1 {
		node.AddProperty("default", kdl.NewString(flag.Default[0]))
	} else if flag.DefaultBool != nil {
		node.AddProperty("default", kdl.NewBool(*flag.DefaultBool))
	}
	if flag.Env != "" {
		node.AddProperty("env", kdl.NewString(flag.Env))
	}

	if flag.HelpLong != "" {
		node.NewChild("long_help").AddArgument(kdl.NewString(flag.HelpLong))
	}
	if len(flag.Default) > 1 {
		defaultNode := kdl.NewNode("default")
		for _, d := range flag.Default {
			defaultNode.AddArgument(kdl.NewString(d))
		}
		node.AddChild(defaultNode)
	}
	if flag.Arg != nil {
		node.AddChild(buildFlagArgNode(flag.Arg))
	}

	return node
}

func buildFlagArgNode(arg *SpecArg) *kdl.Node {
	node := kdl.NewNode("arg", kdl.NewString("<"+arg.Name+">"))

	if arg.Help != "" {
		node.AddProperty("help", kdl.NewString(arg.Help))
	}
	if arg.Choices != nil {
		choicesNode := kdl.NewNode("choices")
		for _, c := range arg.Choices.Values {
			choicesNode.AddArgument(kdl.NewString(c))
		}
		node.AddChild(choicesNode)
	}

	return node
}

func buildArgNode(arg SpecArg) *kdl.Node {
	usage := ""
	if arg.Required {
		usage = "<" + arg.Name + ">"
	} else {
		usage = "[" + arg.Name + "]"
	}
	if arg.Var {
		usage += "\u2026"
	}

	node := kdl.NewNode("arg", kdl.NewString(usage))

	if arg.Help != "" {
		node.AddProperty("help", kdl.NewString(arg.Help))
	}
	if !arg.Required {
		node.AddProperty("required", kdl.NewBool(false))
	}
	if arg.Var {
		node.AddProperty("var", kdl.NewBool(true))
	}
	if arg.Hide {
		node.AddProperty("hide", kdl.NewBool(true))
	}
	if len(arg.Default) == 1 {
		node.AddProperty("default", kdl.NewString(arg.Default[0]))
	}

	if len(arg.Default) > 1 {
		defaultNode := kdl.NewNode("default")
		for _, d := range arg.Default {
			defaultNode.AddArgument(kdl.NewString(d))
		}
		node.AddChild(defaultNode)
	}
	if arg.Choices != nil {
		choicesNode := kdl.NewNode("choices")
		for _, c := range arg.Choices.Values {
			choicesNode.AddArgument(kdl.NewString(c))
		}
		node.AddChild(choicesNode)
	}

	return node
}

func buildCommandNode(cmd SpecCommand) *kdl.Node {
	node := kdl.NewNode("cmd", kdl.NewString(cmd.Name))

	if cmd.Hide {
		node.AddProperty("hide", kdl.NewBool(true))
	}
	if cmd.SubcommandRequired {
		node.AddProperty("subcommand_required", kdl.NewBool(true))
	}
	if cmd.Help != "" {
		node.AddProperty("help", kdl.NewString(cmd.Help))
	}
	if cmd.Deprecated != "" {
		node.AddProperty("deprecated", kdl.NewString(cmd.Deprecated))
	}

	if len(cmd.Aliases) > 0 {
		aliasNode := kdl.NewNode("alias")
		for _, a := range cmd.Aliases {
			aliasNode.AddArgument(kdl.NewString(a))
		}
		node.AddChild(aliasNode)
	}
	if cmd.HelpLong != "" {
		node.NewChild("long_help").AddArgument(kdl.NewString(cmd.HelpLong))
	}
	for _, flag := range cmd.Flags {
		node.AddChild(buildFlagNode(flag))
	}
	for _, arg := range cmd.Args {
		node.AddChild(buildArgNode(arg))
	}
	for _, sub := range cmd.Cmds {
		node.AddChild(buildCommandNode(sub))
	}

	return node
}
