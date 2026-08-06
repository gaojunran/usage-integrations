"""Convert click commands to usage spec."""

from __future__ import annotations

from typing import Any

import click
from usage_spec import Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices


def _convert_arg(arg: click.Argument) -> SpecArg:
    variadic = arg.nargs == -1
    required = arg.required

    from enum import Enum
    _has_real_default = arg.default is not None and not isinstance(arg.default, Enum)

    result = SpecArg(
        name=arg.name or arg.human_readable_name.lower(),
        help=getattr(arg, "help", "") or "",
        required=required,
        var=variadic,
        hide=getattr(arg, "hidden", False),
        default=[str(arg.default)] if _has_real_default else [],
        choices=None,
    )

    if isinstance(arg.type, click.Choice):
        result.choices = SpecChoices(values=list(arg.type.choices))

    return result


def _extract_short_long(opts: list[str]) -> tuple[str, str]:
    short = ""
    long = ""
    for opt in opts:
        if opt.startswith("--"):
            long = opt[2:]
        elif opt.startswith("-"):
            short = opt[1:]
    return short, long


def _convert_flag(opt: click.Option) -> SpecFlag:
    short, long = _extract_short_long(opt.opts)

    is_bool = opt.is_bool_flag or (opt.is_flag and not opt.multiple and not opt.count)

    # Detect negation from secondary opts (--flag/--no-flag pattern)
    negate = ""
    if opt.secondary_opts:
        for sec in opt.secondary_opts:
            if sec.startswith("--no-"):
                # negate points to the negative form itself
                negate = sec
                break

    flag = SpecFlag(
        short=short,
        long=long,
        help=opt.help or "",
        help_long="",
        required=opt.required,
        hide=opt.hidden,
        global_=False,
        count=opt.count,
        var=opt.multiple,
        negate=negate,
        deprecated=(
            str(opt.deprecated)
            if isinstance(getattr(opt, "deprecated", None), str)
            else ""
        ),
        default=[],
        default_bool=None,
        env=str(opt.envvar) if isinstance(opt.envvar, str) else (opt.envvar[0] if opt.envvar and isinstance(opt.envvar, (list, tuple)) else ""),
        arg=None,
    )

    # Non-boolean options have an argument
    if not is_bool and not opt.count:
        arg_name = (long or short).replace("-", "_").upper()
        flag.arg = SpecArg(
            name=arg_name,
            help="",
            required=opt.required,
            var=opt.multiple,
            hide=False,
            default=[],
            choices=None,
        )

        if isinstance(opt.type, click.Choice):
            flag.arg.choices = SpecChoices(values=list(opt.type.choices))

    # Default values - click uses Sentinel enum for unset defaults
    from enum import Enum
    _has_real_default = opt.default is not None and not isinstance(opt.default, Enum)

    if _has_real_default and not (is_bool and opt.default is False):
        if is_bool or opt.count:
            if opt.default is True:
                flag.default_bool = True
        else:
            flag.default = [str(opt.default)]

    return flag


def _convert_command(cmd: click.BaseCommand) -> SpecCommand:
    is_group = isinstance(cmd, click.Group)

    sc = SpecCommand(
        name=cmd.name or "",
        help=cmd.short_help or cmd.help or "",
        help_long=cmd.short_help and cmd.help and cmd.help or "",
        hide=cmd.hidden,
        deprecated=str(cmd.deprecated) if isinstance(cmd.deprecated, str) else "",
        aliases=[],
        subcommand_required=False,
        flags=[],
        args=[],
        cmds=[],
    )

    for param in cmd.params:
        if isinstance(param, click.Option):
            # Skip help and version flags
            name = param.name or ""
            if name in ("help", "version"):
                continue
            sc.flags.append(_convert_flag(param))
        elif isinstance(param, click.Argument):
            sc.args.append(_convert_arg(param))

    # Subcommands for Groups
    if is_group:
        group = cmd  # type: click.Group
        # Try eager commands dict first, then lazy loading
        if group.commands:
            for sub_name, sub_cmd in group.commands.items():
                if sub_cmd.hidden:
                    continue
                sc.cmds.append(_convert_command(sub_cmd))
        else:
            # Lazy loading via list_commands + get_command
            ctx = click.Context(cmd)
            for sub_name in group.list_commands(ctx):
                sub_cmd = group.get_command(ctx, sub_name)
                if sub_cmd and not sub_cmd.hidden:
                    sc.cmds.append(_convert_command(sub_cmd))

        # subcommand_required: group with no positional args
        if sc.cmds and not sc.args:
            sc.subcommand_required = True

    return sc


def _extract_version_from_callback(opt: click.Option) -> str:
    """Extract version string from click.version_option callback closure."""
    cb = opt.callback
    if not cb or not cb.__closure__:
        return ""
    for cell in cb.__closure__:
        val = cell.cell_contents
        if isinstance(val, str) and val and val[0].isdigit():
            return val
    return ""


def convert_root(cmd: click.BaseCommand, bin_name: str | None = None) -> Spec:
    """Convert a click Command or Group to a Spec object."""
    name = bin_name or cmd.name or ""

    spec = Spec(
        name=name,
        bin=name,
        version="",
        about=cmd.short_help or cmd.help or "",
        long=cmd.short_help and cmd.help and cmd.help or "",
        usage="",
        flags=[],
        args=[],
        cmds=[],
    )

    for param in cmd.params:
        if isinstance(param, click.Option):
            pname = param.name or ""
            # Version flag detection
            if pname == "version":
                version = _extract_version_from_callback(param)
                if version:
                    spec.version = version
                continue
            if pname == "help":
                continue
            spec.flags.append(_convert_flag(param))
        elif isinstance(param, click.Argument):
            spec.args.append(_convert_arg(param))

    # Subcommands
    is_group = isinstance(cmd, click.Group)
    if is_group:
        group = cmd  # type: click.Group
        if group.commands:
            for sub_name, sub_cmd in group.commands.items():
                if sub_cmd.hidden:
                    continue
                spec.cmds.append(_convert_command(sub_cmd))
        else:
            ctx = click.Context(cmd)
            for sub_name in group.list_commands(ctx):
                sub_cmd = group.get_command(ctx, sub_name)
                if sub_cmd and not sub_cmd.hidden:
                    spec.cmds.append(_convert_command(sub_cmd))

    return spec
