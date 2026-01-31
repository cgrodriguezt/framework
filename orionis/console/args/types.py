from pathlib import Path
from collections.abc import Callable

TYPE_CONVERTERS: dict[str, Callable] = {
    "builtins.str": str,
    "builtins.int": int,
    "builtins.float": float,
    "builtins.bool": bool,
    "pathlib.Path": Path,
}

ALLOWED_TYPES: set[Callable] = set(TYPE_CONVERTERS.values())
