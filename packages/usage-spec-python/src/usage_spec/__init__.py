"""Usage spec core - Python implementation aligned with @usage-spec/core."""

from .spec import Spec, SpecArg, SpecFlag, SpecCommand, SpecChoices
from .kdl import render_kdl, validate_kdl
from .json import render_json

__all__ = [
    "Spec",
    "SpecArg",
    "SpecFlag",
    "SpecCommand",
    "SpecChoices",
    "render_kdl",
    "validate_kdl",
    "render_json",
    "generate",
]


def generate(
    spec: Spec,
    *,
    format: str = "kdl",
    comment: str | None = None,
) -> str:
    """Generate usage spec output in the specified format."""
    output = render_json(spec) if format == "json" else render_kdl(spec)

    if comment:
        return f"// {comment}\n{output}"

    return output
