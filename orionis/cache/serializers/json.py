from __future__ import annotations
from typing import Any
import msgspec.json as _msgjson
from aiocache.serializers import BaseSerializer

class MsgspecSerializer(BaseSerializer):

    # ruff: noqa: ANN401

    DEFAULT_ENCODING = None  # raw bytes — no UTF-8 decoding overhead

    def dumps(self, value: Any) -> bytes:
        """
        Serialize *value* to UTF-8 encoded JSON bytes.

        Parameters
        ----------
        value : Any
            A JSON-serializable Python object.

        Returns
        -------
        bytes
            msgspec-encoded JSON payload.
        """
        return _msgjson.encode(value)

    def loads(self, data: bytes | str | None) -> Any:
        """
        Deserialize JSON *data* back to a Python object.

        Parameters
        ----------
        data : bytes | str | None
            Raw bytes or string returned by the backend. Returns None
            when *data* is None (key not found).

        Returns
        -------
        Any
            Decoded Python object, or None when *data* is None.
        """
        if data is None:
            return None
        if isinstance(data, str):
            data = data.encode()
        return _msgjson.decode(data)
