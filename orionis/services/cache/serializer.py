from __future__ import annotations
import base64
import datetime
import decimal
import enum
import importlib
import json
import sys
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

import msgspec.json as _msgjson

from orionis.support.types.sentinel import _MISSING_TYPE, MISSING

if TYPE_CHECKING:
    from collections.abc import Callable


# ---------------------------------------------------------------------------
# Module-level constants — faster than name-mangled class-attribute lookups
# ---------------------------------------------------------------------------

_TK: str = "__type__"
_VK: str = "__value__"


# ---------------------------------------------------------------------------
# Decode helpers for importlib-backed types (avoid re-importing cached modules)
# ---------------------------------------------------------------------------


def _dec_type(val: str) -> Any:
    module_name, _, class_name = val.rpartition(".")
    mod = sys.modules.get(module_name) or importlib.import_module(module_name)
    return getattr(mod, class_name)


def _dec_enum(val: dict) -> Any:
    module_name, _, class_name = val["class"].rpartition(".")
    mod = sys.modules.get(module_name) or importlib.import_module(module_name)
    return getattr(mod, class_name)(val["value"])


# ---------------------------------------------------------------------------
# _encode — O(1) exact-type dispatch, recursive fallback for subclasses
# ---------------------------------------------------------------------------


def _encode_subclass(obj: Any, t: type) -> Any:  # NOSONAR
    """Fallback encoder for subclasses not covered by the exact-type dispatch table."""
    # Path subclasses (WindowsPath, PosixPath, etc.)
    if isinstance(obj, Path):
        return {_TK: "path", _VK: str(obj)}
    # datetime.datetime must be checked before datetime.date (it is a subclass)
    if isinstance(obj, datetime.datetime):
        return {_TK: "datetime", _VK: obj.isoformat()}
    if isinstance(obj, datetime.date):
        return {_TK: "date", _VK: obj.isoformat()}
    if isinstance(obj, datetime.time):
        return {_TK: "time", _VK: obj.isoformat()}
    # dict/list subclasses: OrderedDict, defaultdict, UserList, etc.
    if isinstance(obj, dict):
        return {k: _encode(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_encode(v) for v in obj]
    # Remaining subclasses and special singletons
    if isinstance(obj, type):
        return {_TK: "type", _VK: f"{obj.__module__}.{obj.__qualname__}"}
    if obj is MISSING or isinstance(obj, _MISSING_TYPE):
        return {_TK: "missing", _VK: None}
    if isinstance(obj, tuple):
        return {_TK: "tuple", _VK: [_encode(v) for v in obj]}
    if isinstance(obj, frozenset):
        return {_TK: "frozenset", _VK: [_encode(v) for v in obj]}
    if isinstance(obj, set):
        return {_TK: "set", _VK: [_encode(v) for v in obj]}
    if isinstance(obj, enum.Enum):
        et = type(obj)
        class_path = f"{et.__module__}.{et.__qualname__}"
        return {_TK: "enum", _VK: {"class": class_path, "value": obj.value}}
    error_msg = f"Unsupported type for serialization: {t}"
    raise TypeError(error_msg)


def _encode(obj: Any) -> Any:
    t = type(obj)
    handler = _ENCODE_EXACT.get(t)
    if handler is not None:
        return handler(obj)
    # Fast-path for the two dominant exact collection types
    if t is dict:
        return {k: _encode(v) for k, v in obj.items()}
    if t is list:
        return [_encode(v) for v in obj]
    # Delegate all subclass/singleton cases to keep cognitive complexity low
    return _encode_subclass(obj, t)


# Non-recursive handlers — built once at import time; O(1) dispatch via hash lookup
_ENCODE_EXACT: dict[type, Callable[[Any], Any]] = {
    str:               lambda o: o,
    int:               lambda o: o,
    float:             lambda o: o,
    bool:              lambda o: o,
    type(None):        lambda o: o,
    Path:              lambda o: {_TK: "path",      _VK: str(o)},
    bytes:             lambda o: {_TK: "bytes",     _VK: base64.b64encode(o).decode()},
    datetime.datetime: lambda o: {_TK: "datetime",  _VK: o.isoformat()},
    datetime.date:     lambda o: {_TK: "date",      _VK: o.isoformat()},
    datetime.time:     lambda o: {_TK: "time",      _VK: o.isoformat()},
    datetime.timedelta: lambda o: {
        _TK: "timedelta",
        _VK: {"days": o.days, "seconds": o.seconds, "microseconds": o.microseconds},
    },
    decimal.Decimal:   lambda o: {_TK: "decimal",   _VK: str(o)},
    uuid.UUID:         lambda o: {_TK: "uuid",      _VK: str(o)},
    complex: lambda o: {_TK: "complex", _VK: {"real": o.real, "imag": o.imag}},
}


# ---------------------------------------------------------------------------
# _decode — O(1) dispatch on the serialized type-key string
# ---------------------------------------------------------------------------


def _decode(obj: Any) -> Any:
    if type(obj) is list:
        return [_decode(v) for v in obj]
    if type(obj) is dict:
        if _TK in obj:
            handler = _DECODE_DISPATCH.get(obj[_TK])
            if handler is None:
                error_msg = f"Unknown serialized type: {obj[_TK]}"
                raise ValueError(error_msg)
            return handler(obj[_VK])
        return {k: _decode(v) for k, v in obj.items()}
    return obj


# Built once at import time; string key lookup is O(1) via hash
def _dec_missing(_: Any) -> Any:
    return MISSING


def _dec_timedelta(v: Any) -> datetime.timedelta:
    return datetime.timedelta(**v)


def _dec_tuple(v: Any) -> tuple:
    return tuple(_decode(x) for x in v)


def _dec_set(v: Any) -> set:
    return {_decode(x) for x in v}


def _dec_frozenset(v: Any) -> frozenset:
    return frozenset(_decode(x) for x in v)


def _dec_complex(v: Any) -> complex:
    return complex(v["real"], v["imag"])


_DECODE_DISPATCH: dict[str, Callable[[Any], Any]] = {
    "missing":   _dec_missing,
    "path":      Path,
    "bytes":     base64.b64decode,
    "datetime":  datetime.datetime.fromisoformat,
    "date":      datetime.date.fromisoformat,
    "time":      datetime.time.fromisoformat,
    "timedelta": _dec_timedelta,
    "decimal":   decimal.Decimal,
    "uuid":      uuid.UUID,
    "tuple":     _dec_tuple,
    "set":       _dec_set,
    "frozenset": _dec_frozenset,
    "complex":   _dec_complex,
    "type":      _dec_type,
    "enum":      _dec_enum,
}


# ---------------------------------------------------------------------------
# Public API — thin wrapper over the module-level encode/decode functions
# ---------------------------------------------------------------------------


class Serializer:

    # ruff: noqa: ANN401, PLR0911, C901

    @staticmethod
    def dumps(data: Any, indent: int | None = None) -> str:
        """
        Serialize an object to a JSON-formatted string.

        Parameters
        ----------
        data : Any
            The object to serialize.
        indent : int or None, optional
            Number of spaces for indentation in the output JSON string.

        Returns
        -------
        str
            The JSON-formatted string representing the serialized object.
        """
        encoded = _encode(data)
        if indent is not None:
            return json.dumps(encoded, indent=indent, separators=(",", ":"))
        return _msgjson.encode(encoded).decode()

    @staticmethod
    def loads(raw: str | bytes) -> Any:
        """
        Deserialize a JSON-formatted string to a Python object.

        Parameters
        ----------
        raw : str
            JSON-formatted string to deserialize.

        Returns
        -------
        Any
            The deserialized Python object.
        """
        return _decode(_msgjson.decode(raw))

    @staticmethod
    def dumpToFile(data: Any, file_path: Path) -> None:
        """
        Write serialized data to a file atomically.

        Parameters
        ----------
        data : Any
            The object to serialize and write.
        file_path : Path
            The file path where the serialized data will be written.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Encode to bytes and write atomically via a temporary file
        tmp_file = file_path.with_suffix(".tmp")
        tmp_file.write_bytes(_msgjson.encode(_encode(data)))
        tmp_file.replace(file_path)

    @staticmethod
    def loadFromFile(file_path: Path) -> Any:
        """
        Load and deserialize data from a file.

        Parameters
        ----------
        file_path : Path
            Path to the file from which to load and deserialize data.

        Returns
        -------
        Any
            The deserialized Python object, or None if the file does not exist or is
            empty.
        """
        # EAFP: one syscall instead of exists() + stat() + open()
        try:
            content = file_path.read_bytes()
        except OSError:
            return None
        if not content:
            return None
        return _decode(_msgjson.decode(content))
