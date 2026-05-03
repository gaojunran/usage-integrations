"""Usage spec type definitions, aligned with @usage-spec/core TypeScript types."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SpecChoices:
    values: list[str] = field(default_factory=list)


@dataclass
class SpecArg:
    name: str = ""
    help: str = ""
    required: bool = True
    var: bool = False
    hide: bool = False
    default: list[str] = field(default_factory=list)
    choices: SpecChoices | None = None


@dataclass
class SpecFlag:
    short: str = ""
    long: str = ""
    help: str = ""
    help_long: str = ""
    required: bool = False
    hide: bool = False
    global_: bool = False
    count: bool = False
    var: bool = False
    negate: str = ""
    deprecated: str = ""
    default: list[str] = field(default_factory=list)
    default_bool: bool | None = None
    env: str = ""
    arg: SpecArg | None = None


@dataclass
class SpecCommand:
    name: str = ""
    help: str = ""
    help_long: str = ""
    hide: bool = False
    deprecated: str = ""
    aliases: list[str] = field(default_factory=list)
    subcommand_required: bool = False
    flags: list[SpecFlag] = field(default_factory=list)
    args: list[SpecArg] = field(default_factory=list)
    cmds: list[SpecCommand] = field(default_factory=list)


@dataclass
class Spec:
    name: str = ""
    bin: str = ""
    version: str = ""
    about: str = ""
    long: str = ""
    usage: str = ""
    flags: list[SpecFlag] = field(default_factory=list)
    args: list[SpecArg] = field(default_factory=list)
    cmds: list[SpecCommand] = field(default_factory=list)
