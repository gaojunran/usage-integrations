"""Tests for JSON renderer."""

import json

from usage_spec import Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices, render_json


def test_simple_spec():
    spec = Spec(
        name="mycli",
        bin="mycli",
        version="2.0.0",
        about="A CLI tool",
        flags=[
            SpecFlag(short="v", long="verbose", help="Be verbose"),
        ],
        cmds=[
            SpecCommand(name="run", help="Run something"),
        ],
    )
    result = json.loads(render_json(spec))
    assert result["name"] == "mycli"
    assert result["bin"] == "mycli"
    assert result["version"] == "2.0.0"
    assert result["about"] == "A CLI tool"
    assert len(result["flags"]) == 1
    assert len(result["cmds"]) == 1
    assert result["cmds"][0]["name"] == "run"


def test_choices_in_json():
    spec = Spec(
        name="deploy",
        flags=[
            SpecFlag(
                long="env",
                help="Environment",
                arg=SpecArg(name="ENV", choices=SpecChoices(values=["dev", "prod"])),
            ),
        ],
    )
    result = json.loads(render_json(spec))
    assert result["flags"][0]["arg"]["choices"] == ["dev", "prod"]


def test_flag_details():
    spec = Spec(
        name="app",
        flags=[
            SpecFlag(long="env", help="Target environment", required=True, arg=SpecArg(name="ENV")),
            SpecFlag(long="no-color", help="Disable color", negate="--color"),
        ],
    )
    result = json.loads(render_json(spec))
    assert len(result["flags"]) == 2
    env_flag = next(f for f in result["flags"] if f["name"] == "--env")
    assert env_flag["required"] is True
    assert env_flag["arg"]["name"] == "ENV"

    color_flag = next(f for f in result["flags"] if f["name"] == "--no-color")
    assert color_flag["negate"] == "--color"


def test_args_in_json():
    spec = Spec(
        name="app",
        args=[
            SpecArg(name="file", help="Input file", required=True),
            SpecArg(name="output", help="Output file", required=False),
        ],
    )
    result = json.loads(render_json(spec))
    assert len(result["args"]) == 2
    assert result["args"][0]["name"] == "file"
    # required=true is default, omitted in JSON
    assert "required" not in result["args"][0]
    assert result["args"][1]["required"] is False


def test_omits_empty_fields():
    spec = Spec(name="empty")
    result = json.loads(render_json(spec))
    assert result == {"name": "empty"}
