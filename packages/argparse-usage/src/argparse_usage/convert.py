"""Convert argparse.ArgumentParser to usage spec."""

from __future__ import annotations

import argparse
from typing import Any

from usage_spec import Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices

# Action class names that represent boolean flags
_BOOL_ACTION_NAMES = frozenset({
    "_StoreTrueAction",
    "_StoreFalseAction",
})

# Action class names that represent count flags
_COUNT_ACTION_NAMES = frozenset({
    "_CountAction",
})

# Action class names for subparsers
_SUBPARSERS_ACTION_NAMES = frozenset({
    "_SubParsersAction",
    "SubParsersAction",
})

# Built-in flag names to skip
_BUILTIN_FLAG_NAMES = frozenset({"help", "version"})


def _is_bool_action(action: argparse.Action) -> bool:
    return type(action).__name__ in _BOOL_ACTION_NAMES


def _is_count_action(action: argparse.Action) -> bool:
    return type(action).__name__ in _COUNT_ACTION_NAMES


def _is_subparsers_action(action: argparse.Action) -> bool:
    return type(action).__name__ in _SUBPARSERS_ACTION_NAMES


def _is_optional(action: argparse.Action) -> bool:
    return bool(action.option_strings)


def _extract_short_long(option_strings: list[str]) -> tuple[str, str]:
    short = ""
    long = ""
    for opt in option_strings:
        if opt.startswith("--"):
            long = opt[2:]
        elif opt.startswith("-"):
            short = opt[1:]
    return short, long


def _convert_arg(action: argparse.Action) -> SpecArg:
    nargs = action.nargs
    # Use argparse's own 'required' attribute for positional args
    required = getattr(action, "required", True)
    # Variadic: nargs is '*' or '+' or argparse.REMAINDER
    variadic = nargs in ("*", "+", argparse.REMAINDER) if nargs else False

    result = SpecArg(
        name=action.dest or action.metavar or "",
        help=action.help if action.help != argparse.SUPPRESS else "",
        required=required,
        var=variadic,
        hide=action.help == argparse.SUPPRESS,
        default=[str(action.default)] if action.default not in (None, argparse.SUPPRESS) else [],
        choices=None,
    )

    if action.choices:
        result.choices = SpecChoices(values=[str(c) for c in action.choices])

    return result


def _convert_flag(action: argparse.Action) -> SpecFlag:
    short, long = _extract_short_long(action.option_strings)
    is_bool = _is_bool_action(action)
    is_count = _is_count_action(action)
    is_store_false = type(action).__name__ == "_StoreFalseAction"

    flag = SpecFlag(
        short=short,
        long=long,
        help=action.help if action.help != argparse.SUPPRESS else "",
        help_long="",
        required=bool(action.required) if hasattr(action, "required") else False,
        hide=action.help == argparse.SUPPRESS,
        global_=False,
        count=is_count,
        var=bool(action.nargs and action.nargs in ("*", "+")),
        negate=f"--{long}" if is_store_false else "",
        deprecated="",
        default=[],
        default_bool=None,
        env="",
        arg=None,
    )

    # Non-boolean, non-count options have an argument
    if not is_bool and not is_count:
        arg_name = (long or short).replace("-", "_").upper()
        flag.arg = SpecArg(
            name=arg_name,
            help="",
            required=flag.required,
            var=flag.var,
            hide=False,
            default=[],
            choices=None,
        )

        if action.choices:
            flag.arg.choices = SpecChoices(values=[str(c) for c in action.choices])

    # Default values
    if action.default not in (None, argparse.SUPPRESS, True, False):
        if is_bool or is_count:
            pass  # skip for booleans
        else:
            flag.default = [str(action.default)]
    elif action.default is True:
        flag.default_bool = True
    # False defaults are omitted for booleans

    return flag


def _get_subcommand_helps(parser: argparse.ArgumentParser) -> dict[str, str]:
    """Extract help texts from subparsers' _choices_actions."""
    helps: dict[str, str] = {}
    for action in parser._actions:
        if _is_subparsers_action(action) and hasattr(action, "_choices_actions"):
            for ca in action._choices_actions:
                if ca.dest and ca.help:
                    helps[ca.dest] = ca.help
    return helps


def _convert_command(parser: argparse.ArgumentParser, help_override: str = "") -> SpecCommand:
    name = parser.prog
    # Strip parent prefix from name (e.g. "app sub" -> "sub")
    if " " in name:
        name = name.rsplit(" ", 1)[-1]

    # Use help_override from _choices_actions if available, otherwise description
    cmd_help = help_override or parser.description or ""

    sc = SpecCommand(
        name=name,
        help=cmd_help,
        help_long="",
        hide=False,
        deprecated="",
        aliases=[],
        subcommand_required=False,
        flags=[],
        args=[],
        cmds=[],
    )

    sub_helps = _get_subcommand_helps(parser)

    for action in parser._actions:
        if _is_optional(action):
            action_name = _extract_short_long(action.option_strings)[1] or _extract_short_long(action.option_strings)[0]
            if action_name in _BUILTIN_FLAG_NAMES:
                continue
            sc.flags.append(_convert_flag(action))
        elif _is_subparsers_action(action):
            if hasattr(action, "choices") and action.choices:
                for sub_name, sub_parser in action.choices.items():
                    sc.cmds.append(_convert_command(sub_parser, sub_helps.get(sub_name, "")))
        else:
            sc.args.append(_convert_arg(action))

    # subcommand_required: has subcommands but no positional args
    if sc.cmds and not sc.args:
        sc.subcommand_required = True

    return sc


def convert_root(parser: argparse.ArgumentParser, bin_name: str | None = None) -> Spec:
    """Convert an argparse.ArgumentParser to a Spec object."""
    name = bin_name or parser.prog

    spec = Spec(
        name=name,
        bin=name,
        version="",
        about=parser.description or "",
        long=parser.epilog or "",
        usage=parser.usage or "",
        flags=[],
        args=[],
        cmds=[],
    )

    sub_helps = _get_subcommand_helps(parser)

    for action in parser._actions:
        if _is_optional(action):
            action_name = _extract_short_long(action.option_strings)[1] or _extract_short_long(action.option_strings)[0]
            # Extract version string before skipping
            if action_name == "version" and hasattr(action, "version"):
                spec.version = action.version or ""
                continue
            # Skip built-in flags
            if action_name in _BUILTIN_FLAG_NAMES:
                continue
            spec.flags.append(_convert_flag(action))
        elif _is_subparsers_action(action):
            if hasattr(action, "choices") and action.choices:
                for sub_name, sub_parser in action.choices.items():
                    spec.cmds.append(_convert_command(sub_parser, sub_helps.get(sub_name, "")))
        else:
            # Positional argument
            spec.args.append(_convert_arg(action))

    return spec
