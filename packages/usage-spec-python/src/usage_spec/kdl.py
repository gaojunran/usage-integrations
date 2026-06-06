"""KDL renderer for usage spec, aligned with @usage-spec/core kdl.ts output."""

from __future__ import annotations

import ckdl

from .spec import Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices


def _node(name: str, args: list[str] | None = None, properties: dict | None = None, children: list[ckdl.Node] | None = None) -> ckdl.Node:
    n = ckdl.Node(name)
    if args:
        n.args = args
    if properties:
        n.properties = properties
    if children:
        n.children = children
    return n


def _build_choices_node(choices: SpecChoices) -> ckdl.Node:
    return _node("choices", args=choices.values)


def _build_arg_node(arg: SpecArg) -> ckdl.Node:
    usage = f"<{arg.name}>" if arg.required else f"[{arg.name}]"
    if arg.var:
        usage += "\u2026"

    properties: dict = {}
    if arg.help:
        properties["help"] = arg.help
    if not arg.required:
        properties["required"] = False
    if arg.var:
        properties["var"] = True
    if arg.hide:
        properties["hide"] = True
    if len(arg.default) == 1:
        properties["default"] = arg.default[0]

    children: list[ckdl.Node] = []
    if len(arg.default) > 1:
        children.append(_node("default", args=arg.default))
    if arg.choices:
        children.append(_build_choices_node(arg.choices))

    return _node("arg", args=[usage], properties=properties or None, children=children or None)


def _build_flag_arg_node(arg: SpecArg) -> ckdl.Node:
    properties: dict = {}
    if arg.help:
        properties["help"] = arg.help

    children: list[ckdl.Node] = []
    if arg.choices:
        children.append(_build_choices_node(arg.choices))

    return _node("arg", args=[f"<{arg.name}>"], properties=properties or None, children=children or None)


def _build_flag_node(flag: SpecFlag) -> ckdl.Node:
    name_parts: list[str] = []
    if flag.short:
        name_parts.append(f"-{flag.short}")
    if flag.long:
        name_parts.append(f"--{flag.long}")
    flag_name = " ".join(name_parts)

    properties: dict = {}
    if flag.help:
        properties["help"] = flag.help
    if flag.required:
        properties["required"] = True
    if flag.var:
        properties["var"] = True
    if flag.hide:
        properties["hide"] = True
    if flag.global_:
        properties["global"] = True
    if flag.count:
        properties["count"] = True
    if flag.negate:
        properties["negate"] = flag.negate
    if flag.deprecated:
        properties["deprecated"] = flag.deprecated
    if len(flag.default) == 1:
        properties["default"] = flag.default[0]
    elif flag.default_bool is not None:
        properties["default"] = flag.default_bool
    if flag.env:
        properties["env"] = flag.env

    children: list[ckdl.Node] = []
    if flag.help_long:
        children.append(_node("long_help", args=[flag.help_long]))
    if len(flag.default) > 1:
        children.append(_node("default", args=flag.default))
    if flag.arg:
        children.append(_build_flag_arg_node(flag.arg))

    return _node("flag", args=[flag_name], properties=properties or None, children=children or None)


def _build_command_node(cmd: SpecCommand) -> ckdl.Node:
    properties: dict = {}
    if cmd.hide:
        properties["hide"] = True
    if cmd.subcommand_required:
        properties["subcommand_required"] = True
    if cmd.help:
        properties["help"] = cmd.help
    if cmd.deprecated:
        properties["deprecated"] = cmd.deprecated

    children: list[ckdl.Node] = []
    if cmd.aliases:
        children.append(_node("alias", args=cmd.aliases))
    if cmd.help_long:
        children.append(_node("long_help", args=[cmd.help_long]))
    for flag in cmd.flags:
        children.append(_build_flag_node(flag))
    for arg in cmd.args:
        children.append(_build_arg_node(arg))
    for sub in cmd.cmds:
        children.append(_build_command_node(sub))

    return _node("cmd", args=[cmd.name], properties=properties or None, children=children or None)


def render_kdl(spec: Spec) -> str:
    nodes: list[ckdl.Node] = []

    if spec.name:
        nodes.append(_node("name", args=[spec.name]))
    if spec.bin:
        nodes.append(_node("bin", args=[spec.bin]))
    if spec.version:
        nodes.append(_node("version", args=[spec.version]))
    if spec.about:
        nodes.append(_node("about", args=[spec.about]))
    if spec.long:
        nodes.append(_node("long_about", args=[spec.long]))
    if spec.usage:
        nodes.append(_node("usage", args=[spec.usage]))

    for flag in spec.flags:
        nodes.append(_build_flag_node(flag))
    for arg in spec.args:
        nodes.append(_build_arg_node(arg))
    for cmd in spec.cmds:
        nodes.append(_build_command_node(cmd))

    doc = ckdl.Document(*nodes)
    return str(doc)


def validate_kdl(kdl: str) -> None:
    """Validate KDL output by parsing it back. Throws if invalid."""
    if not kdl.strip():
        return
    ckdl.parse(kdl)
