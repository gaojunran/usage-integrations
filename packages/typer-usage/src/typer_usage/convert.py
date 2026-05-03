"""Convert Typer apps to usage spec.

Typer is built on top of click, so this module reuses click conversion logic
and adds Typer-specific handling.
"""

from __future__ import annotations

from typing import Any

import click as _click
import typer
from usage_spec import Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices

from click_usage.convert import convert_root as _click_convert_root, _convert_arg, _convert_flag, _convert_command

# Typer auto-generated flags to skip
_TYPER_BUILTIN_FLAG_NAMES = frozenset({
    "install-completion",
    "show-completion",
})


def _is_typer_argument(arg: _click.Argument) -> bool:
    return hasattr(arg, "help")  # TyperArgument has help; standard click.Argument does not


def _convert_typer_arg(arg: _click.Argument) -> SpecArg:
    """Convert a TyperArgument, which has help/hidden that standard click.Argument lacks."""
    result = _convert_arg(arg)

    if _is_typer_argument(arg):
        result.help = getattr(arg, "help", "") or ""
        result.hide = getattr(arg, "hidden", False)

    return result


def _convert_typer_command(cmd: _click.BaseCommand) -> SpecCommand:
    """Convert a click command that may contain Typer-specific params."""
    sc = _convert_command(cmd)

    # Replace args with Typer-aware conversion
    sc.args = []
    for param in cmd.params:
        if isinstance(param, _click.Argument):
            sc.args.append(_convert_typer_arg(param))

    # Filter out Typer built-in flags
    sc.flags = [f for f in sc.flags if f.long not in _TYPER_BUILTIN_FLAG_NAMES]

    return sc


def _is_typer_builtin_option(opt: _click.Option) -> bool:
    name = opt.name or ""
    return name in _TYPER_BUILTIN_FLAG_NAMES or name in ("help", "version")


def convert_root(app: typer.Typer, bin_name: str | None = None) -> Spec:
    """Convert a Typer app to a Spec object."""
    name = bin_name or app.info.name or ""

    spec = Spec(
        name=name,
        bin=name,
        version="",
        about=app.info.help or "",
        long="",
        usage="",
        flags=[],
        args=[],
        cmds=[],
    )

    # Handle empty Typer apps (no commands registered)
    if not app.registered_commands and not app.registered_groups:
        return spec

    # Get the underlying click command from Typer
    try:
        click_cmd = typer.main.get_command(app)
    except RuntimeError:
        return spec

    if not name:
        name = click_cmd.name or ""
        spec.name = name
        spec.bin = name

    # If Typer has a single command, it returns a Command, not a Group.
    # We treat that single command as the root.
    is_group = isinstance(click_cmd, _click.Group)

    if is_group:
        # Multi-command app: root is the group, commands are subcommands
        spec.about = app.info.help or click_cmd.short_help or click_cmd.help or ""
        spec.long = (app.info.help and click_cmd.help and click_cmd.help) or ""

        # Root-level params from the group
        for param in click_cmd.params:
            if isinstance(param, _click.Option):
                if _is_typer_builtin_option(param):
                    if param.name == "version" and param.default is not None:
                        spec.version = str(param.default)
                    continue
                spec.flags.append(_convert_flag(param))
            elif isinstance(param, _click.Argument):
                spec.args.append(_convert_typer_arg(param))

        # Subcommands
        group = click_cmd  # type: _click.Group
        if group.commands:
            for sub_name, sub_cmd in group.commands.items():
                if sub_cmd.hidden:
                    continue
                spec.cmds.append(_convert_typer_command(sub_cmd))
        else:
            ctx = _click.Context(click_cmd)
            for sub_name in group.list_commands(ctx):
                sub_cmd = group.get_command(ctx, sub_name)
                if sub_cmd and not sub_cmd.hidden:
                    spec.cmds.append(_convert_typer_command(sub_cmd))
    else:
        # Single-command app: treat the command as root
        spec.about = app.info.help or click_cmd.short_help or click_cmd.help or ""

        for param in click_cmd.params:
            if isinstance(param, _click.Option):
                if _is_typer_builtin_option(param):
                    continue
                spec.flags.append(_convert_flag(param))
            elif isinstance(param, _click.Argument):
                spec.args.append(_convert_typer_arg(param))

    # Filter out Typer built-in flags
    spec.flags = [f for f in spec.flags if f.long not in _TYPER_BUILTIN_FLAG_NAMES]

    return spec
