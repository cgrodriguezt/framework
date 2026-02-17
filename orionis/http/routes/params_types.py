from datetime import datetime
import uuid

# ruff: noqa: DTZ007, E501

PARAM_TYPES = {
    "str": {
        "pattern": r"[^/]+",
        "converter": str,
    },
    "slug": {
        "pattern": r"[a-z0-9-]+",
        "converter": str,
    },
    "int": {
        "pattern": r"-?\d+",
        "converter": int,
    },
    "float": {
        "pattern": r"-?\d+\.?\d*",
        "converter": float,
    },
    "uuid": {
        "pattern": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        "converter": uuid.UUID,
    },
    "date": {
        "pattern": r"\d{4}-\d{2}-\d{2}",
        "converter": lambda x: datetime.strptime(x, "%Y-%m-%d").date(),
    },
    "datetime": {
        "pattern": r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
        "converter": lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"),
    },
    "bool": {
        "pattern": r"(?:true|false|0|1)",
        "converter": lambda x: x.lower() in ("true", "1"),
    },
    "alpha": {
        "pattern": r"[a-zA-Z]+",
        "converter": str,
    },
    "alnum": {
        "pattern": r"[a-zA-Z0-9]+",
        "converter": str,
    },
    "path": {
        "pattern": r".+",
        "converter": str,
    },
}
