"""Tests for KDL renderer."""

from usage_spec import Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices, render_kdl, validate_kdl


def test_simple_spec():
    spec = Spec(
        name="mycli",
        bin="mycli",
        version="1.0.0",
        about="A simple CLI",
        flags=[
            SpecFlag(short="v", long="verbose", help="Enable verbose output"),
            SpecFlag(short="c", long="config", help="Config file path", arg=SpecArg(name="PATH")),
        ],
    )
    output = render_kdl(spec)
    assert "name mycli" in output
    assert "bin mycli" in output
    assert 'version "1.0.0"' in output
    assert 'about "A simple CLI"' in output
    assert 'flag "-v --verbose"' in output
    assert 'help="Enable verbose output"' in output
    assert 'flag "-c --config"' in output
    assert 'help="Config file path"' in output


def test_required_option():
    spec = Spec(
        name="app",
        flags=[
            SpecFlag(long="env", help="Target environment", required=True, arg=SpecArg(name="ENV")),
        ],
    )
    output = render_kdl(spec)
    assert "required=#true" in output


def test_boolean_flag():
    spec = Spec(
        name="app",
        flags=[
            SpecFlag(long="force", help="Force the operation"),
        ],
    )
    output = render_kdl(spec)
    assert "flag --force" in output
    # Boolean flags should not have arg
    force_line = next(l for l in output.split("\n") if "flag --force" in l)
    assert "arg" not in force_line


def test_default_values():
    spec = Spec(
        name="app",
        flags=[
            SpecFlag(long="output", help="Output format", default=["json"], arg=SpecArg(name="FORMAT")),
            SpecFlag(long="retries", help="Number of retries", default=["3"], arg=SpecArg(name="N")),
        ],
    )
    output = render_kdl(spec)
    assert "default=json" in output
    assert 'default="3"' in output


def test_boolean_default_true():
    spec = Spec(
        name="app",
        flags=[
            SpecFlag(long="color", help="Enable color", default_bool=True),
        ],
    )
    output = render_kdl(spec)
    assert "default=#true" in output


def test_boolean_default_false_omitted():
    spec = Spec(
        name="app",
        flags=[
            SpecFlag(long="force", help="Force operation", default_bool=None),
        ],
    )
    output = render_kdl(spec)
    force_line = next(l for l in output.split("\n") if "flag --force" in l)
    assert "default" not in force_line


def test_negated_option():
    spec = Spec(
        name="app",
        flags=[
            SpecFlag(long="no-color", help="Disable color output", negate="--color"),
        ],
    )
    output = render_kdl(spec)
    assert "negate=--color" in output


def test_choices():
    spec = Spec(
        name="deploy",
        flags=[
            SpecFlag(
                long="format",
                help="Output format",
                arg=SpecArg(name="TYPE", choices=SpecChoices(values=["json", "yaml", "toml"])),
            ),
        ],
    )
    output = render_kdl(spec)
    assert "choices" in output
    assert "json" in output
    assert "yaml" in output
    assert "toml" in output


def test_positional_args():
    spec = Spec(
        name="cmd",
        args=[
            SpecArg(name="file", help="Input file", required=True),
            SpecArg(name="output", help="Output file", required=False),
        ],
    )
    output = render_kdl(spec)
    assert "arg <file>" in output
    assert 'arg "[output]"' in output
    assert "required=#false" in output


def test_variadic_arg():
    spec = Spec(
        name="cmd",
        args=[
            SpecArg(name="files", help="Multiple files", required=True, var=True),
        ],
    )
    output = render_kdl(spec)
    assert "arg <files>\u2026" in output
    assert "var=#true" in output


def test_subcommands():
    spec = Spec(
        name="app",
        cmds=[
            SpecCommand(name="start", help="Start the app"),
            SpecCommand(name="stop", help="Stop the app"),
        ],
    )
    output = render_kdl(spec)
    assert "cmd start" in output
    assert "cmd stop" in output


def test_nested_subcommands():
    spec = Spec(
        name="app",
        cmds=[
            SpecCommand(
                name="sub",
                help="A subcommand",
                cmds=[
                    SpecCommand(name="nested", help="A nested command"),
                ],
            ),
        ],
    )
    output = render_kdl(spec)
    assert "cmd sub" in output
    assert "cmd nested" in output


def test_subcommand_required():
    spec = Spec(
        name="app",
        cmds=[
            SpecCommand(
                name="config",
                help="Manage config",
                subcommand_required=True,
                cmds=[
                    SpecCommand(name="get", help="Get a value"),
                    SpecCommand(name="set", help="Set a value"),
                ],
            ),
        ],
    )
    output = render_kdl(spec)
    assert "subcommand_required=#true" in output


def test_aliases():
    spec = Spec(
        name="app",
        cmds=[
            SpecCommand(name="install", help="Install packages", aliases=["i", "add"]),
        ],
    )
    output = render_kdl(spec)
    assert "alias" in output
    assert "i" in output
    assert "add" in output


def test_long_help():
    spec = Spec(
        name="app",
        about="Short help",
        long="This is a much longer description of the app.",
    )
    output = render_kdl(spec)
    assert 'about "Short help"' in output
    assert 'long_about "This is a much longer description of the app."' in output


def test_env_variable():
    spec = Spec(
        name="app",
        flags=[
            SpecFlag(long="color", help="Color output", env="MYCLI_COLOR", arg=SpecArg(name="BOOL")),
        ],
    )
    output = render_kdl(spec)
    assert "env=MYCLI_COLOR" in output


def test_validate_kdl_valid():
    spec = Spec(
        name="app",
        version="1.0.0",
        about="A CLI",
        flags=[
            SpecFlag(short="v", long="verbose", help="Be verbose"),
            SpecFlag(short="f", long="file", help="Input file", arg=SpecArg(name="FILE")),
        ],
    )
    output = render_kdl(spec)
    validate_kdl(output)  # Should not raise


def test_special_char_escaping():
    spec = Spec(
        name="app",
        about="Short help",
        long="First line.\nSecond line.\n\nThird paragraph.",
    )
    output = render_kdl(spec)
    assert "long_about" in output
    validate_kdl(output)

def test_string_zero_default():
    spec = Spec(
        name="app",
        flags=[
            SpecFlag(long="port", help="Port number", default=["0"], arg=SpecArg(name="PORT")),
        ],
    )
    output = render_kdl(spec)
    assert 'default="0"' in output
