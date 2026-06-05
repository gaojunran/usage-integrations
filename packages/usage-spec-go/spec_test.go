package usagespec

import (
	"encoding/json"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestRenderKDL_EmptySpec(t *testing.T) {
	spec := Spec{Name: "app", Bin: "app"}
	output := RenderKDL(spec)
	assert.Contains(t, output, "name app")
	assert.Contains(t, output, "bin app")
	assert.NotContains(t, output, "version")
	assert.NotContains(t, output, "flag")
	assert.NotContains(t, output, "arg ")
	assert.NotContains(t, output, "cmd ")
}

func TestRenderKDL_FullSpec(t *testing.T) {
	spec := Spec{
		Name:    "example",
		Bin:     "example",
		Version: "1.0.0",
		About:   "An example CLI",
		Flags: []SpecFlag{
			{Short: "f", Long: "file", Help: "Some input file", Arg: &SpecArg{Name: "FILE"}},
			{Long: "verbose", Help: "Enable verbose output"},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "name example")
	assert.Contains(t, output, "bin example")
	assert.Contains(t, output, `version "1.0.0"`)
	assert.Contains(t, output, `about "An example CLI"`)
	assert.Contains(t, output, `flag "-f --file"`)
	assert.Contains(t, output, `flag --verbose`)
}

func TestRenderKDL_FlagWithShortAndLong(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Short: "v", Long: "verbose", Help: "Be verbose"},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, `flag "-v --verbose"`)
}

func TestRenderKDL_FlagShortOnly(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Short: "v", Help: "Be verbose"},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, `flag -v`)
}

func TestRenderKDL_FlagLongOnly(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "verbose", Help: "Be verbose"},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, `flag --verbose`)
}

func TestRenderKDL_RequiredFlag(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "env", Help: "Target environment", Required: true},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "required=#true")
}

func TestRenderKDL_DefaultString(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "format", Help: "Format", Default: []string{"json"}},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, `default=json`)
}

func TestRenderKDL_DefaultBoolTrue(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "color", Help: "Enable color", DefaultBool: BoolPtr(true)},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "default=#true")
}

func TestRenderKDL_Choices(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{
				Long: "format", Help: "Format",
				Arg: &SpecArg{
					Name:    "FORMAT",
					Choices: &SpecChoices{Values: []string{"json", "yaml", "toml"}},
				},
			},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "choices")
	assert.Contains(t, output, "json")
	assert.Contains(t, output, "yaml")
	assert.Contains(t, output, "toml")
}

func TestRenderKDL_ArgRequired(t *testing.T) {
	spec := Spec{
		Name: "app",
		Args: []SpecArg{
			{Name: "file", Required: true},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "arg <file>")
}

func TestRenderKDL_ArgOptional(t *testing.T) {
	spec := Spec{
		Name: "app",
		Args: []SpecArg{
			{Name: "name", Required: false},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, `arg "[name]"`)
	assert.Contains(t, output, "required=#false")
}

func TestRenderKDL_ArgVariadic(t *testing.T) {
	spec := Spec{
		Name: "app",
		Args: []SpecArg{
			{Name: "files", Required: true, Var: true},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "arg <files>\u2026")
	assert.Contains(t, output, "var=#true")
}

func TestRenderKDL_CommandWithSubcommands(t *testing.T) {
	spec := Spec{
		Name: "app",
		Cmds: []SpecCommand{
			{
				Name: "db", Help: "Database ops",
				Cmds: []SpecCommand{
					{Name: "migrate", Help: "Run migrations"},
				},
				SubcommandRequired: true,
			},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "cmd db")
	assert.Contains(t, output, `help="Database ops"`)
	assert.Contains(t, output, "subcommand_required=#true")
	assert.Contains(t, output, "cmd migrate")
}

func TestRenderKDL_CommandAliases(t *testing.T) {
	spec := Spec{
		Name: "app",
		Cmds: []SpecCommand{
			{Name: "install", Help: "Install", Aliases: []string{"i", "add"}},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "alias i add")
}

func TestRenderKDL_CommandDeprecated(t *testing.T) {
	spec := Spec{
		Name: "app",
		Cmds: []SpecCommand{
			{Name: "old-cmd", Deprecated: "Use new-cmd instead"},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, `deprecated="Use new-cmd instead"`)
}

func TestRenderKDL_FlagEnv(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "token", Help: "Auth token", Env: "MYCLI_TOKEN"},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "env=MYCLI_TOKEN")
}

func TestRenderKDL_FlagNegate(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "no-color", Help: "Disable color", Negate: "--color"},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "negate=--color")
}

func TestRenderKDL_FlagCount(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Short: "v", Long: "verbose", Help: "Verbosity", Count: true},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "count=#true")
}

func TestRenderKDL_FlagDeprecated(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "old-flag", Help: "Old", Deprecated: "Use --new-flag instead"},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, `deprecated="Use --new-flag instead"`)
}

func TestRenderKDL_GlobalFlag(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "debug", Help: "Debug mode", Global: true},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "global=#true")
}

func TestRenderKDL_SpecialCharsInHelp(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "format", Help: "Output format:\n  json\n  yaml"},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "help=")
	assert.NotPanics(t, func() { ValidateKDL(output) })
}

func TestRenderKDL_LongAbout(t *testing.T) {
	spec := Spec{
		Name:  "app",
		About: "Short help",
		Long:  "This is a much longer description of the app.",
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, `about "Short help"`)
	assert.Contains(t, output, `long_about "This is a much longer description of the app."`)
}

func TestRenderKDL_HiddenFlag(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "secret", Help: "Secret flag", Hide: true},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "hide=#true")
}

func TestRenderKDL_VariadicFlag(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "include", Help: "Include patterns", Var: true, Arg: &SpecArg{Name: "PATTERNS", Var: true}},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, "var=#true")
}

func TestRenderKDL_DefaultStringZero(t *testing.T) {
	spec := Spec{
		Name: "app",
		Flags: []SpecFlag{
			{Long: "port", Help: "Port", Default: []string{"0"}},
		},
	}
	output := RenderKDL(spec)
	assert.Contains(t, output, `default="0"`)
}

func TestValidateKDL_Valid(t *testing.T) {
	kdl := `name app
bin app
flag --verbose help="Be verbose"
cmd db help="Database" {
    cmd migrate help="Migrate"
}`
	assert.NotPanics(t, func() { ValidateKDL(kdl) })
}

func TestValidateKDL_Empty(t *testing.T) {
	assert.NotPanics(t, func() { ValidateKDL("") })
}

func TestRenderJSON_FullSpec(t *testing.T) {
	spec := Spec{
		Name:    "mycli",
		Bin:     "mycli",
		Version: "2.0.0",
		About:   "A CLI tool",
		Flags:   []SpecFlag{{Long: "verbose", Help: "Be verbose"}},
		Cmds:    []SpecCommand{{Name: "run", Help: "Run something"}},
	}
	output := RenderJSON(spec)
	var parsed map[string]interface{}
	err := json.Unmarshal([]byte(output), &parsed)
	assert.NoError(t, err)
	assert.Equal(t, "mycli", parsed["name"])
	assert.Equal(t, "mycli", parsed["bin"])
	assert.Equal(t, "2.0.0", parsed["version"])
	assert.Equal(t, "A CLI tool", parsed["about"])
	assert.Equal(t, "Be verbose", parsed["flags"].([]interface{})[0].(map[string]interface{})["help"])
	assert.Equal(t, "run", parsed["cmds"].([]interface{})[0].(map[string]interface{})["name"])
}

func TestRenderJSON_ChoicesInFlag(t *testing.T) {
	spec := Spec{
		Name: "deploy",
		Flags: []SpecFlag{
			{
				Long: "env", Help: "Environment",
				Arg:  &SpecArg{Name: "ENV", Choices: &SpecChoices{Values: []string{"dev", "prod"}}},
			},
		},
	}
	output := RenderJSON(spec)
	var parsed map[string]interface{}
	json.Unmarshal([]byte(output), &parsed)
	flag := parsed["flags"].([]interface{})[0].(map[string]interface{})
	arg := flag["arg"].(map[string]interface{})
	assert.Equal(t, []interface{}{"dev", "prod"}, arg["choices"])
}

func TestRenderJSON_OmitZeroValues(t *testing.T) {
	spec := Spec{Name: "app", Bin: "app"}
	output := RenderJSON(spec)
	var parsed map[string]interface{}
	json.Unmarshal([]byte(output), &parsed)
	_, hasVersion := parsed["version"]
	_, hasFlags := parsed["flags"]
	assert.False(t, hasVersion)
	assert.False(t, hasFlags)
}

func TestGenerate_KDL(t *testing.T) {
	spec := Spec{Name: "app", Bin: "app"}
	output := Generate(spec, "kdl", "test comment")
	assert.Contains(t, output, "// test comment")
	assert.Contains(t, output, "name app")
}

func TestGenerate_JSON(t *testing.T) {
	spec := Spec{Name: "app", Bin: "app"}
	output := Generate(spec, "json", "")
	var parsed map[string]interface{}
	json.Unmarshal([]byte(output), &parsed)
	assert.Equal(t, "app", parsed["name"])
}

func TestGenerate_NoComment(t *testing.T) {
	spec := Spec{Name: "app"}
	output := Generate(spec, "kdl", "")
	assert.NotContains(t, output, "// @generated")
}
