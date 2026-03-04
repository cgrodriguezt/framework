from __future__ import annotations
import base64
import datetime
import decimal
import json
import uuid
from pathlib import Path
from typing import Any

class Serializer:

    # ruff: noqa: ANN401, PLR0912, PLR0911, C901

    __TYPE_KEY = "__type__"
    __VALUE_KEY = "__value__"

    @classmethod
    def dumps(cls, data: Any, indent: int | None = None) -> str:
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
        # First, encode the object into a JSON-serializable structure
        encoded = cls.__encode(data)

        # Serialize the encoded object to a JSON string
        return json.dumps(encoded, indent=indent, separators=(",", ":"))

    @classmethod
    def loads(cls, raw: str) -> Any:
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
        parsed = json.loads(raw)
        return cls.__decode(parsed)

    @classmethod
    def dumpToFile(cls, data: Any, file_path: Path) -> None:
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
        # Write to a temporary file first to ensure atomicity
        tmp_file = file_path.with_suffix(".tmp")
        encoded = cls.__encode(data)

        # Serialize the encoded object to a JSON
        # string and write it to the temporary file
        with tmp_file.open("w", encoding="utf-8") as f:
            json.dump(encoded, f, separators=(",", ":"), ensure_ascii=False)

        # Atomically replace the original file with the temporary file
        tmp_file.replace(file_path)

    @classmethod
    def loadFromFile(cls, file_path: Path) -> Any:
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
        # Return None if file does not exist or is empty
        if not file_path.exists() or file_path.stat().st_size == 0:
            return None

        # Read and parse JSON content from file
        with file_path.open("r", encoding="utf-8") as f:
            parsed = json.load(f)

        # Decode the parsed object and return
        return cls.__decode(parsed)

    @classmethod
    def __encode(cls, obj: Any) -> Any:
        """
        Encode an object into a JSON-serializable structure.

        Parameters
        ----------
        obj : Any
            The object to encode.

        Returns
        -------
        Any
            The JSON-serializable representation of the object.

        Raises
        ------
        TypeError
            If the object type is not supported for serialization.
        """
        # Return primitive types and None as-is
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj

        # Encode Path objects as strings with type metadata
        if isinstance(obj, Path):
            return {
                cls.__TYPE_KEY: "path",
                cls.__VALUE_KEY: str(obj),
            }

        # Encode bytes as base64 strings with type metadata
        if isinstance(obj, bytes):
            return {
                cls.__TYPE_KEY: "bytes",
                cls.__VALUE_KEY: base64.b64encode(obj).decode(),
            }

        # Encode datetime objects as ISO format strings
        if isinstance(obj, datetime.datetime):
            return {
                cls.__TYPE_KEY: "datetime",
                cls.__VALUE_KEY: obj.isoformat(),
            }

        # Encode date objects as ISO format strings
        if isinstance(obj, datetime.date):
            return {
                cls.__TYPE_KEY: "date",
                cls.__VALUE_KEY: obj.isoformat(),
            }

        # Encode time objects as ISO format strings
        if isinstance(obj, datetime.time):
            return {
                cls.__TYPE_KEY: "time",
                cls.__VALUE_KEY: obj.isoformat(),
            }

        # Encode timedelta objects as dicts with days, seconds, microseconds
        if isinstance(obj, datetime.timedelta):
            return {
                cls.__TYPE_KEY: "timedelta",
                cls.__VALUE_KEY: {
                    "days": obj.days,
                    "seconds": obj.seconds,
                    "microseconds": obj.microseconds,
                },
            }

        # Encode Decimal objects as strings
        if isinstance(obj, decimal.Decimal):
            return {
                cls.__TYPE_KEY: "decimal",
                cls.__VALUE_KEY: str(obj),
            }

        # Encode UUID objects as strings
        if isinstance(obj, uuid.UUID):
            return {
                cls.__TYPE_KEY: "uuid",
                cls.__VALUE_KEY: str(obj),
            }

        # Encode tuple as list with type metadata
        if isinstance(obj, tuple):
            return {
                cls.__TYPE_KEY: "tuple",
                cls.__VALUE_KEY: [cls.__encode(v) for v in obj],
            }

        # Encode set as list with type metadata
        if isinstance(obj, set):
            return {
                cls.__TYPE_KEY: "set",
                cls.__VALUE_KEY: [cls.__encode(v) for v in obj],
            }

        # Encode frozenset as list with type metadata
        if isinstance(obj, frozenset):
            return {
                cls.__TYPE_KEY: "frozenset",
                cls.__VALUE_KEY: [cls.__encode(v) for v in obj],
            }

        # Encode complex numbers as dicts with real and imag parts
        if isinstance(obj, complex):
            return {
                cls.__TYPE_KEY: "complex",
                cls.__VALUE_KEY: {"real": obj.real, "imag": obj.imag},
            }

        # Recursively encode dictionaries
        if isinstance(obj, dict):
            return {k: cls.__encode(v) for k, v in obj.items()}

        # Recursively encode lists
        if isinstance(obj, list):
            return [cls.__encode(v) for v in obj]

        # Raise error for unsupported types
        error_msg = (
            f"Unsupported type for serialization: {type(obj)}"
        )
        raise TypeError(error_msg)

    @classmethod
    def __decode(cls, obj: Any) -> Any:
        """
        Decode a JSON-deserialized structure into a Python object.

        Parameters
        ----------
        obj : Any
            The JSON-deserialized structure to decode.

        Returns
        -------
        Any
            The decoded Python object.
        """
        # Recursively decode lists
        if isinstance(obj, list):
            return [cls.__decode(v) for v in obj]

        # Recursively decode dictionaries and handle special types
        if isinstance(obj, dict):
            if cls.__TYPE_KEY in obj:
                t = obj[cls.__TYPE_KEY]
                value = obj[cls.__VALUE_KEY]

                if t == "path":
                    return Path(value)
                if t == "bytes":
                    return base64.b64decode(value)
                if t == "datetime":
                    return datetime.datetime.fromisoformat(value)
                if t == "date":
                    return datetime.date.fromisoformat(value)
                if t == "time":
                    return datetime.time.fromisoformat(value)
                if t == "timedelta":
                    return datetime.timedelta(**value)
                if t == "decimal":
                    return decimal.Decimal(value)
                if t == "uuid":
                    return uuid.UUID(value)
                if t == "tuple":
                    return tuple(cls.__decode(v) for v in value)
                if t == "set":
                    return {cls.__decode(v) for v in value}
                if t == "frozenset":
                    return frozenset(cls.__decode(v) for v in value)
                if t == "complex":
                    return complex(value["real"], value["imag"])

                error_msg = f"Unknown serialized type: {t}"
                raise ValueError(error_msg)

            # Recursively decode dictionary values
            return {k: cls.__decode(v) for k, v in obj.items()}

        # Return primitive types as-is
        return obj
