"""Convert Typer apps to usage spec.

Typer is built on top of click, so this module reuses click conversion logic
and adds Typer-specific handling.

Since typer 0.26.0 vendors click (as ``typer._click``), params and commands are
no longer ``click.Option`` / ``click.Argument`` / ``click.Group`` subclasses.
They are classified via the ``typer.core`` classes (``TyperOption`` /
``TyperArgument`` / ``TyperGroup``), which are stable across typer versions.
"""

from __future__ import annotations

from typing import Any

import typer
from usage_spec import Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices

from click_usage.convert import _convert_arg, _convert_flag

# Typer auto-generated flags to skip
_TYPER_BUILTIN_FLAG_NAMES = frozenset({
    "install-completion",
    "show-completion",
    "install_completion",
    "show_completion",
})


def _is_typer_option(param: Any) -> bool:
    return isinstance(param, typer.core.TyperOption)


def _is_typer_argument(param: Any) -> bool:
    return isinstance(param, typer.core.TyperArgument)


def _is_typer_group(cmd: Any) -> bool:
    return isinstance(cmd, typer.core.TyperGroup)


def _is_typer_argument_like(arg: Any) -> bool:
    # TyperArgument has help; standard click.Argument does not
    return hasattr(arg, "help")


def _command_context(cmd: Any) -> Any:
    """Create the Context a command expects.

    typer >= 0.26 uses its vendored click (``typer._click``); older versions
    use the real ``click`` package.
    """
    click_module = getattr(typer, "_click", None)
    if click_module is None:
        import click as click_module
    return click_module.Context(cmd)


def _param_choices(param: Any) -> list[str] | None:
    """Choice values for a param across typer versions.

    typer < 0.26 exposes ``click.Choice`` (``TyperChoice`` subclasses it).
    typer >= 0.26 uses a vendored ``TyperChoice``, and a ``click_type=``
    ``Choice`` is wrapped in a ``FuncParamType`` whose ``.func`` is the Choice
    instance.
    """
    param_type = param.type
    choices = getattr(param_type, "choices", None)
    if choices is None:
        choices = getattr(getattr(param_type, "func", None), "choices", None)
    if choices is None:
        return None
    return [str(choice) for choice in choices]


def _convert_typer_flag(opt: Any) -> SpecFlag:
    """Convert a TyperOption, patching choice detection for typer >= 0.26."""
    result = _convert_flag(opt)

    if result.arg is not None and result.arg.choices is None:
        choices = _param_choices(opt)
        if choices is not None:
            result.arg.choices = SpecChoices(values=choices)

    return result


def _convert_typer_arg(arg: Any) -> SpecArg:
    """Convert a TyperArgument, which has help/hidden that click.Argument lacks."""
    result = _convert_arg(arg)

    if _is_typer_argument_like(arg):
        result.help = getattr(arg, "help", "") or ""
        result.hide = getattr(arg, "hidden", False)

    if result.choices is None:
        choices = _param_choices(arg)
        if choices is not None:
            result.choices = SpecChoices(values=choices)

    return result


def _convert_typer_command(cmd: Any) -> SpecCommand:
    """Convert a Typer command (leaf or group) into a SpecCommand."""
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
        if _is_typer_option(param):
            if _is_typer_builtin_option(param):
                continue
            sc.flags.append(_convert_typer_flag(param))
        elif _is_typer_argument(param):
            sc.args.append(_convert_typer_arg(param))

    # Filter out Typer built-in flags
    sc.flags = [f for f in sc.flags if f.long not in _TYPER_BUILTIN_FLAG_NAMES]

    if _is_typer_group(cmd):
        if cmd.commands:
            for sub_cmd in cmd.commands.values():
                if sub_cmd.hidden:
                    continue
                sc.cmds.append(_convert_typer_command(sub_cmd))
        else:
            ctx = _command_context(cmd)
            for sub_name in cmd.list_commands(ctx):
                sub_cmd = cmd.get_command(ctx, sub_name)
                if sub_cmd and not sub_cmd.hidden:
                    sc.cmds.append(_convert_typer_command(sub_cmd))

        # subcommand_required: group with no positional args
        if sc.cmds and not sc.args:
            sc.subcommand_required = True

    return sc


def _is_typer_builtin_option(opt: Any) -> bool:
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

    # Get the underlying command from Typer
    try:
        cmd = typer.main.get_command(app)
    except RuntimeError:
        return spec

    if not name:
        name = cmd.name or ""
        spec.name = name
        spec.bin = name

    # If Typer has a single command, it returns a Command, not a Group.
    # We treat that single command as the root.
    is_group = _is_typer_group(cmd)

    if is_group:
        # Multi-command app: root is the group, commands are subcommands
        spec.about = app.info.help or cmd.short_help or cmd.help or ""
        spec.long = (app.info.help and cmd.help and cmd.help) or ""

        # Root-level params from the group
        for param in cmd.params:
            if _is_typer_option(param):
                if _is_typer_builtin_option(param):
                    if param.name == "version" and param.default is not None:
                        spec.version = str(param.default)
                    continue
                spec.flags.append(_convert_typer_flag(param))
            elif _is_typer_argument(param):
                spec.args.append(_convert_typer_arg(param))

        # Subcommands
        if cmd.commands:
            for sub_cmd in cmd.commands.values():
                if sub_cmd.hidden:
                    continue
                spec.cmds.append(_convert_typer_command(sub_cmd))
        else:
            ctx = _command_context(cmd)
            for sub_name in cmd.list_commands(ctx):
                sub_cmd = cmd.get_command(ctx, sub_name)
                if sub_cmd and not sub_cmd.hidden:
                    spec.cmds.append(_convert_typer_command(sub_cmd))
    else:
        # Single-command app: treat the command as root
        spec.about = app.info.help or cmd.short_help or cmd.help or ""

        for param in cmd.params:
            if _is_typer_option(param):
                if _is_typer_builtin_option(param):
                    continue
                spec.flags.append(_convert_typer_flag(param))
            elif _is_typer_argument(param):
                spec.args.append(_convert_typer_arg(param))

    # Filter out Typer built-in flags
    spec.flags = [f for f in spec.flags if f.long not in _TYPER_BUILTIN_FLAG_NAMES]

    return spec
