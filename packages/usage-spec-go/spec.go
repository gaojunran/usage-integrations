package usagespec

type SpecChoices struct {
	Values []string
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

func BoolPtr(v bool) *bool {
	return &v
}
