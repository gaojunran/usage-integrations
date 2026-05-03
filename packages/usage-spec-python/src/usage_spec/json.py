"""JSON renderer for usage spec, aligned with @usage-spec/core json.ts output."""

from __future__ import annotations

import json
from typing import Any

from .spec import Spec, SpecArg, SpecFlag, SpecCommand


def _arg_to_json(arg: SpecArg) -> dict[str, Any]:
    result: dict[str, Any] = {"name": arg.name}

    if arg.help:
        result["help"] = arg.help
    if not arg.required:
        result["required"] = False
    if arg.var:
        result["var"] = True
    if arg.hide:
        result["hide"] = True
    if len(arg.default) == 1:
        result["default"] = arg.default[0]
    if len(arg.default) > 1:
        result["default"] = arg.default
    if arg.choices:
        result["choices"] = arg.choices.values

    return result


def _flag_to_json(flag: SpecFlag) -> dict[str, Any]:
    result: dict[str, Any] = {}

    name_parts: list[str] = []
    if flag.short:
        name_parts.append(f"-{flag.short}")
    if flag.long:
        name_parts.append(f"--{flag.long}")
    result["name"] = " ".join(name_parts)

    if flag.help:
        result["help"] = flag.help
    if flag.help_long:
        result["help_long"] = flag.help_long
    if flag.required:
        result["required"] = True
    if flag.hide:
        result["hide"] = True
    if flag.global_:
        result["global"] = True
    if flag.count:
        result["count"] = True
    if flag.var:
        result["var"] = True
    if flag.negate:
        result["negate"] = flag.negate
    if flag.deprecated:
        result["deprecated"] = flag.deprecated
    if flag.env:
        result["env"] = flag.env
    if len(flag.default) == 1:
        result["default"] = flag.default[0]
    if len(flag.default) > 1:
        result["default"] = flag.default

    if flag.arg:
        result["arg"] = _arg_to_json(flag.arg)

    return result


def _cmd_to_json(cmd: SpecCommand) -> dict[str, Any]:
    result: dict[str, Any] = {"name": cmd.name}

    if cmd.help:
        result["help"] = cmd.help
    if cmd.help_long:
        result["help_long"] = cmd.help_long
    if cmd.hide:
        result["hide"] = True
    if cmd.deprecated:
        result["deprecated"] = cmd.deprecated
    if cmd.aliases:
        result["aliases"] = cmd.aliases
    if cmd.subcommand_required:
        result["subcommand_required"] = True

    if cmd.flags:
        result["flags"] = [_flag_to_json(f) for f in cmd.flags]
    if cmd.args:
        result["args"] = [_arg_to_json(a) for a in cmd.args]
    if cmd.cmds:
        result["cmds"] = [_cmd_to_json(c) for c in cmd.cmds]

    return result


def render_json(spec: Spec) -> str:
    """Render a Spec to JSON format string."""
    result: dict[str, Any] = {}

    if spec.name:
        result["name"] = spec.name
    if spec.bin:
        result["bin"] = spec.bin
    if spec.version:
        result["version"] = spec.version
    if spec.about:
        result["about"] = spec.about
    if spec.long:
        result["long_about"] = spec.long
    if spec.usage:
        result["usage"] = spec.usage

    if spec.flags:
        result["flags"] = [_flag_to_json(f) for f in spec.flags]
    if spec.args:
        result["args"] = [_arg_to_json(a) for a in spec.args]
    if spec.cmds:
        result["cmds"] = [_cmd_to_json(c) for c in spec.cmds]

    return json.dumps(result, indent=2) + "\n"
