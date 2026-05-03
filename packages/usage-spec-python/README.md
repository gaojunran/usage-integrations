# usage-spec

Core types and rendering for [usage spec](https://usage.jdx.dev).

## Install

```sh
pip install usage-spec
```

## API

### Types

```python
@dataclass
class Spec:
    name: str
    bin: str
    version: str
    about: str
    long: str
    usage: str
    flags: list[SpecFlag]
    args: list[SpecArg]
    cmds: list[SpecCommand]
```

### Functions

```python
from usage_spec import generate, render_kdl, render_json, validate_kdl

# Render Spec as KDL string
render_kdl(spec: Spec) -> str

# Render Spec as JSON string
render_json(spec: Spec) -> str

# Generate spec output with optional format and comment
generate(spec: Spec, format: str = "kdl", comment: str | None = None) -> str

# Validate KDL string by basic structural check
validate_kdl(kdl: str) -> None
```

## License

MIT
