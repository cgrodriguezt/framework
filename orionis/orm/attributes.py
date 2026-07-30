from __future__ import annotations
import json
import uuid
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Any
from orionis.orm.exceptions import MassAssignmentException, OrmException
from orionis.orm.schema.types import ColumnType

if TYPE_CHECKING:
    from collections.abc import Callable

    from orionis.orm.metaclass import ModelMetadata

# Strings interpreted as truthy when casting to bool.
_TRUTHY_STRINGS: frozenset[str] = frozenset({"1", "true", "yes", "on"})


def _castInt(value: Any) -> int:  # noqa: ANN401
    """
    Cast a raw value to ``int``.

    Parameters
    ----------
    value : Any
        Raw attribute value.

    Returns
    -------
    int
        Integer representation of the value.
    """
    return int(value)


def _castFloat(value: Any) -> float:  # noqa: ANN401
    """
    Cast a raw value to ``float``.

    Parameters
    ----------
    value : Any
        Raw attribute value.

    Returns
    -------
    float
        Float representation of the value.
    """
    return float(value)


def _castBool(value: Any) -> bool:  # noqa: ANN401
    """
    Cast a raw value to ``bool`` handling common textual forms.

    Parameters
    ----------
    value : Any
        Raw attribute value.

    Returns
    -------
    bool
        Boolean representation of the value.
    """
    if isinstance(value, str):
        return value.strip().lower() in _TRUTHY_STRINGS
    return bool(value)


def _castDatetime(value: Any) -> datetime:  # noqa: ANN401
    """
    Cast a raw value to ``datetime``.

    Parameters
    ----------
    value : Any
        Datetime instance, ISO-8601 string, or POSIX timestamp.

    Returns
    -------
    datetime
        Datetime representation of the value.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=UTC)
    return datetime.fromisoformat(str(value))


def _castDate(value: Any) -> date:  # noqa: ANN401
    """
    Cast a raw value to ``date``.

    Parameters
    ----------
    value : Any
        Date, datetime, or ISO-8601 string.

    Returns
    -------
    date
        Date representation of the value.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _castJson(value: Any) -> Any:  # noqa: ANN401
    """
    Cast a raw value to a JSON-decoded Python structure.

    Parameters
    ----------
    value : Any
        JSON string, or an already decoded structure.

    Returns
    -------
    Any
        Decoded Python structure.
    """
    if isinstance(value, (bytes, bytearray, str)):
        return json.loads(value)
    return value


def _castUuid(value: Any) -> uuid.UUID:  # noqa: ANN401
    """
    Cast a raw value to :class:`uuid.UUID`.

    Parameters
    ----------
    value : Any
        UUID instance or its string form.

    Returns
    -------
    uuid.UUID
        UUID representation of the value.
    """
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(str(value))


# Registry of supported cast names.
_CAST_HANDLERS: dict[str, Callable[[Any], Any]] = {
    "int": _castInt,
    "float": _castFloat,
    "bool": _castBool,
    "datetime": _castDatetime,
    "date": _castDate,
    "json": _castJson,
    "uuid": _castUuid,
}


def getCastHandler(cast: str) -> Callable[[Any], Any]:
    """
    Return the cast handler registered under the given name.

    Parameters
    ----------
    cast : str
        Cast name declared in a model ``casts`` mapping.

    Returns
    -------
    Callable
        Function converting raw values into the cast type.

    Raises
    ------
    OrmException
        If the cast name is not supported.
    """
    handler = _CAST_HANDLERS.get(str(cast).strip().lower())
    if handler is None:
        supported = ", ".join(sorted(_CAST_HANDLERS))
        error_msg = (
            f"Unsupported cast '{cast}'. Supported casts: {supported}."
        )
        raise OrmException(error_msg)
    return handler


def serializeForStorage(meta: ModelMetadata, values: dict[str, Any]) -> dict[str, Any]:
    """
    Convert attribute values into driver-friendly storage values.

    JSON-cast structures stored in non-JSON columns are serialized to
    strings, and UUID objects targeting non-UUID columns are stringified;
    every other value passes through unchanged.

    Parameters
    ----------
    meta : ModelMetadata
        Metadata of the model owning the attributes.
    values : dict
        Attribute values to serialize.

    Returns
    -------
    dict
        Values ready to be bound into an SQL statement.
    """
    serialized: dict[str, Any] = {}
    for key, value in values.items():
        column = meta.columns.get(key)
        if column is None or value is None:
            serialized[key] = value
            continue

        # JSON structures need explicit encoding outside JSON columns.
        is_structure = isinstance(value, (dict, list))
        if is_structure and column.column_type is not ColumnType.JSON:
            serialized[key] = json.dumps(value)
            continue

        # UUID objects need their string form outside UUID columns.
        is_uuid = isinstance(value, uuid.UUID)
        if is_uuid and column.column_type is not ColumnType.UUID:
            serialized[key] = str(value)
            continue

        serialized[key] = value
    return serialized


class AttributesMixin:
    """
    Attribute handling behavior shared by every model.

    Provides mass assignment with fillable/guarded enforcement, cast
    application, and serialization helpers. The mixin operates on the
    ``_attributes`` mapping owned by the model instance.
    """

    __slots__ = ()

    def fill(self, attributes: dict[str, Any]) -> Any:  # noqa: ANN401
        """
        Mass assign the given attributes honoring the assignment rules.

        Parameters
        ----------
        attributes : dict
            Attribute values keyed by column name.

        Returns
        -------
        Model
            The same instance, enabling fluent chaining.

        Raises
        ------
        MassAssignmentException
            If a key is not a column or is guarded from mass assignment.
        """
        meta = self.__meta__
        for key, value in attributes.items():
            if key not in meta.columns:
                error_msg = (
                    f"Attribute '{key}' is not a column of model "
                    f"[{type(self).__name__}]."
                )
                raise MassAssignmentException(error_msg)
            if not meta.isFillable(key):
                error_msg = (
                    f"Attribute '{key}' is not mass assignable on model "
                    f"[{type(self).__name__}]."
                )
                raise MassAssignmentException(error_msg)
            self.setAttribute(key, value)
        return self

    def setAttribute(self, key: str, value: Any) -> None:  # noqa: ANN401
        """
        Assign a single attribute applying its cast when declared.

        Parameters
        ----------
        key : str
            Attribute name.
        value : Any
            Raw value to assign.

        Returns
        -------
        None
            This method does not return a value.
        """
        handler = self.__meta__.castLookup.get(key)
        if handler is not None and value is not None:
            value = handler(value)
        self._attributes[key] = value

    def getAttribute(self, key: str, default: Any = None) -> Any:  # noqa: ANN401
        """
        Return a single attribute value.

        Parameters
        ----------
        key : str
            Attribute name.
        default : Any, optional
            Value returned when the attribute is absent.

        Returns
        -------
        Any
            Attribute value, or the default when absent.
        """
        return self._attributes.get(key, default)

    # ── Serialization ───────────────────────────────────────────────────────

    def toDict(self) -> dict[str, Any]:
        """
        Serialize the visible attributes into a dictionary.

        Attributes listed in ``hidden`` are omitted.

        Returns
        -------
        dict
            Visible attribute values keyed by name.
        """
        hidden = self.__meta__.hidden
        if not hidden:
            return dict(self._attributes)
        return {
            key: value
            for key, value in self._attributes.items()
            if key not in hidden
        }

    def serialize(self) -> dict[str, Any]:
        """
        Serialize the model for collection-level serialization.

        Returns
        -------
        dict
            Visible attribute values keyed by name.
        """
        return self.toDict()

    def toJson(self, **kwargs: Any) -> str:  # noqa: ANN401
        """
        Serialize the visible attributes into a JSON string.

        Parameters
        ----------
        **kwargs : Any
            Additional keyword arguments forwarded to ``json.dumps``.

        Returns
        -------
        str
            JSON representation of the visible attributes.
        """
        kwargs.setdefault("default", str)
        return json.dumps(self.toDict(), **kwargs)

    def only(self, *keys: str) -> dict[str, Any]:
        """
        Return a subset of attributes limited to the given keys.

        Parameters
        ----------
        *keys : str
            Attribute names to include.

        Returns
        -------
        dict
            Attribute values for the requested keys that exist.
        """
        return {
            key: self._attributes[key]
            for key in keys
            if key in self._attributes
        }

    def except_(self, *keys: str) -> dict[str, Any]:
        """
        Return every attribute except the given keys.

        Parameters
        ----------
        *keys : str
            Attribute names to exclude.

        Returns
        -------
        dict
            Attribute values without the excluded keys.
        """
        excluded = frozenset(keys)
        return {
            key: value
            for key, value in self._attributes.items()
            if key not in excluded
        }

    def exclude(self, *keys: str) -> dict[str, Any]:
        """
        Return every attribute except the given keys.

        Alias of :meth:`except_` with a keyword-safe name.

        Parameters
        ----------
        *keys : str
            Attribute names to exclude.

        Returns
        -------
        dict
            Attribute values without the excluded keys.
        """
        return self.except_(*keys)
