"""KDL renderer for usage spec, aligned with @usage-spec/core kdl.ts output."""

from __future__ import annotations

from .spec import Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices


def _escape_kdl_string(value: str) -> str:
    """Escape a string for KDL format."""
    if not value:
        return '""'
    # KDL strings: if the value contains special chars, wrap in quotes
    needs_quoting = any(c in value for c in (' ', '"', '\n', '\r', '\t', '\\', '{', '}', '#', '\0'))
    if not needs_quoting and value not in ('true', 'false', 'null'):
        return value
    escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    return f'"{escaped}"'


def _format_bool(value: bool) -> str:
    return "#true" if value else "#false"


def _indent(lines: list[str], level: int) -> list[str]:
    prefix = "    " * level
    return [prefix + line for line in lines]


def _render_choices(choices: SpecChoices) -> list[str]:
    parts = " ".join(_escape_kdl_string(c) for c in choices.values)
    return [f"choices {parts}"]


def _render_arg(arg: SpecArg, *, is_flag_arg: bool = False, indent_level: int = 0) -> list[str]:
    lines: list[str] = []

    if is_flag_arg:
        usage = f"<{arg.name}>"
        line_parts = [f"arg {_escape_kdl_string(usage)}"]
    else:
        # Build usage string: <required> or [optional], with … for variadic
        if arg.required:
            usage = f"<{arg.name}>"
        else:
            usage = f"[{arg.name}]"
        if arg.var:
            usage += "\u2026"

        line_parts = [f"arg {_escape_kdl_string(usage)}"]

        if arg.help:
            line_parts.append(f"help={_escape_kdl_string(arg.help)}")
        if not arg.required:
            line_parts.append(f"required={_format_bool(False)}")
        if arg.var:
            line_parts.append(f"var={_format_bool(True)}")
        if arg.hide:
            line_parts.append(f"hide={_format_bool(True)}")
        if len(arg.default) == 1:
            line_parts.append(f"default={_escape_kdl_string(arg.default[0])}")

    # Check for children (choices, multiple defaults)
    children: list[str] = []

    if not is_flag_arg and len(arg.default) > 1:
        parts = " ".join(_escape_kdl_string(d) for d in arg.default)
        children.append(f"default {parts}")

    if arg.choices:
        children.extend(_render_choices(arg.choices))

    if is_flag_arg:
        # Flag arg: only has help and choices as children/properties
        line_parts_flag = [f"arg {_escape_kdl_string(f'<{arg.name}>')}"]
        if arg.help:
            line_parts_flag.append(f"help={_escape_kdl_string(arg.help)}")

        if arg.choices:
            children_flag = _indent(_render_choices(arg.choices), 1)
            lines.append(" ".join(line_parts_flag) + " {")
            lines.extend(children_flag)
            lines.append("}")
        else:
            lines.append(" ".join(line_parts_flag))
        return lines

    if children:
        lines.append(" ".join(line_parts) + " {")
        lines.extend(_indent(children, 1))
        lines.append("}")
    else:
        lines.append(" ".join(line_parts))

    return lines


def _render_flag(flag: SpecFlag) -> list[str]:
    # Build the flag name: "-s --long"
    name_parts: list[str] = []
    if flag.short:
        name_parts.append(f"-{flag.short}")
    if flag.long:
        name_parts.append(f"--{flag.long}")
    flag_name = " ".join(name_parts)

    line_parts = [f"flag {_escape_kdl_string(flag_name)}"]

    if flag.help:
        line_parts.append(f"help={_escape_kdl_string(flag.help)}")
    if flag.required:
        line_parts.append(f"required={_format_bool(True)}")
    if flag.var:
        line_parts.append(f"var={_format_bool(True)}")
    if flag.hide:
        line_parts.append(f"hide={_format_bool(True)}")
    if flag.global_:
        line_parts.append(f"global={_format_bool(True)}")
    if flag.count:
        line_parts.append(f"count={_format_bool(True)}")
    if flag.negate:
        line_parts.append(f"negate={flag.negate}")
    if flag.deprecated:
        line_parts.append(f"deprecated={_escape_kdl_string(flag.deprecated)}")
    if len(flag.default) == 1:
        line_parts.append(f"default={_escape_kdl_string(flag.default[0])}")
    elif flag.default_bool is not None:
        line_parts.append(f"default={_format_bool(flag.default_bool)}")
    if flag.env:
        line_parts.append(f"env={_escape_kdl_string(flag.env)}")

    # Check for children
    children: list[str] = []

    if flag.help_long:
        children.append(f"long_help {_escape_kdl_string(flag.help_long)}")

    if len(flag.default) > 1:
        parts = " ".join(_escape_kdl_string(d) for d in flag.default)
        children.append(f"default {parts}")

    if flag.arg:
        children.extend(_render_flag_arg(flag.arg))

    if children:
        return [" ".join(line_parts) + " {", *_indent(children, 1), "}"]
    else:
        return [" ".join(line_parts)]


def _render_flag_arg(arg: SpecArg) -> list[str]:
    """Render a flag's inner arg node."""
    line_parts = [f"arg {_escape_kdl_string(f'<{arg.name}>')}"]

    if arg.help:
        line_parts.append(f"help={_escape_kdl_string(arg.help)}")

    if arg.choices:
        children = _indent(_render_choices(arg.choices), 1)
        return [" ".join(line_parts) + " {", *children, "}"]
    else:
        return [" ".join(line_parts)]


def _render_command(cmd: SpecCommand) -> list[str]:
    line_parts = [f"cmd {_escape_kdl_string(cmd.name)}"]

    if cmd.hide:
        line_parts.append(f"hide={_format_bool(True)}")
    if cmd.subcommand_required:
        line_parts.append("subcommand_required=#true")
    if cmd.help:
        line_parts.append(f"help={_escape_kdl_string(cmd.help)}")
    if cmd.deprecated:
        line_parts.append(f"deprecated={_escape_kdl_string(cmd.deprecated)}")

    # Check for children
    children: list[str] = []

    if cmd.aliases:
        parts = " ".join(_escape_kdl_string(a) for a in cmd.aliases)
        children.append(f"alias {parts}")

    if cmd.help_long:
        children.append(f"long_help {_escape_kdl_string(cmd.help_long)}")

    for flag in cmd.flags:
        children.extend(_render_flag(flag))

    for arg in cmd.args:
        children.extend(_render_arg(arg))

    for sub in cmd.cmds:
        children.extend(_render_command(sub))

    if children:
        indented = _indent(children, 1)
        return [" ".join(line_parts) + " {", *indented, "}"]
    else:
        return [" ".join(line_parts)]


def render_kdl(spec: Spec) -> str:
    """Render a Spec to KDL format string."""
    lines: list[str] = []

    if spec.name:
        lines.append(f"name {_escape_kdl_string(spec.name)}")
    if spec.bin:
        lines.append(f"bin {_escape_kdl_string(spec.bin)}")
    if spec.version:
        lines.append(f"version {_escape_kdl_string(spec.version)}")
    if spec.about:
        lines.append(f"about {_escape_kdl_string(spec.about)}")
    if spec.long:
        lines.append(f"long_about {_escape_kdl_string(spec.long)}")
    if spec.usage:
        lines.append(f"usage {_escape_kdl_string(spec.usage)}")

    for flag in spec.flags:
        lines.extend(_render_flag(flag))

    for arg in spec.args:
        lines.extend(_render_arg(arg))

    for cmd in spec.cmds:
        lines.extend(_render_command(cmd))

    return "\n".join(lines) + "\n"


def validate_kdl(kdl: str) -> None:
    """Validate KDL output by attempting a basic structural parse.

    This is a simplified validator - for full validation, use the
    @bgotink/kdl parser via the TypeScript @usage-spec/core package.
    """
    if not kdl.strip():
        return
    # Basic bracket matching for child blocks
    depth = 0
    for line in kdl.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        depth += stripped.count("{") - stripped.count("}")
    if depth != 0:
        raise ValueError(f"Unbalanced braces in KDL output (depth={depth})")
