from __future__ import annotations
from dataclasses import asdict, fields, is_dataclass, MISSING
from enum import Enum

# Enum-to-value converter defined at module level: avoids re-creating a closure
# on every toDict() call (each call previously allocated 2 function objects).
def _enumSerializer(obj: object) -> object:
    """Return the enum value if obj is an Enum, otherwise return obj unchanged."""
    if isinstance(obj, Enum):
        return obj.value
    return obj


# Reusable dict factory: passed to asdict() so no lambda is built per call.
def _dictFactory(items: list) -> dict:
    """Construct a dictionary from key-value pairs, converting enum values."""
    return {k: _enumSerializer(v) for k, v in items}


# Module-level cache: maps each concrete class to its frozen tuple of Field objects.
# dataclasses.fields() rebuilds a new tuple on every call; we pay that cost once.
_FIELDS_CACHE: dict[type, tuple] = {}


class BaseEntity:

    # ruff: noqa: PLR0912, C901

    def __post_init__(self) -> None:
        """
        Perform additional initialization after dataclass instance creation.

        This method is called automatically after all dataclass fields have been
        initialized. Override in subclasses to add custom initialization logic
        or field validation.

        Returns
        -------
        None
            No value is returned.
        """

    @classmethod
    def _cachedDataclassFields(cls) -> tuple:
        """Return the cached tuple of Field objects for this class.

        Returns
        -------
        tuple
            Immutable tuple of dataclasses.Field objects for the calling class.
        """
        # Return cached result or populate the cache on first access per class.
        try:
            return _FIELDS_CACHE[cls]
        except KeyError:
            _result = fields(cls)
            _FIELDS_CACHE[cls] = _result
            return _result

    def toDict(self) -> dict:
        """
        Convert the dataclass instance to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the dataclass instance with enums
            converted to their values.
        """
        # Use module-level dict_factory to avoid per-call closure allocation.
        return asdict(self, dict_factory=_dictFactory)

    def getFields(self) -> list[dict]:  # NOSONAR
        """
        Get detailed information about each field in the dataclass instance.

        Returns
        -------
        list[dict]
            List where each element contains field information with keys:
            'name' (str), 'types' (list[str]), 'default' (Any),
            'metadata' (dict).

        Notes
        -----
        Handles complex field types including unions and generics.
        Resolves defaults from field definition, factory, or metadata.
        Normalizes dataclass and Enum values in defaults and metadata.
        """
        # Store field information dictionaries
        __fields = []

        # Iterate over the cached field tuple instead of rebuilding it each call.
        for _field in self._cachedDataclassFields():
            # Extract field name
            __name = _field.name

            # Resolve simple type name; fall back to string-parsing for unions/generics
            __type = getattr(_field.type, "__name__", None)
            type_lst: list[str] = []

            # Handle complex types (unions, generics)
            if __type is None:
                type_str = str(_field.type).split("|")
                type_lst = [itype.strip() for itype in type_str]
                __type = type_lst

            # Normalise type representation to a list for consistency
            __type = type_lst if isinstance(__type, list) else [__type]

            # Extract and process metadata
            metadata = dict(_field.metadata) if _field.metadata else {}

            # Normalise metadata default value when present
            if "default" in metadata:
                metadata_default = metadata["default"]
                if callable(metadata_default):
                    metadata_default = metadata_default()
                if is_dataclass(metadata_default):
                    metadata_default = asdict(metadata_default)
                elif isinstance(metadata_default, Enum):
                    metadata_default = metadata_default.value
                metadata["default"] = metadata_default

            __metadata = metadata

            # Resolve the field's effective default value
            __default = None

            # Branch 1: static default value
            if _field.default is not MISSING:
                __default = (_field.default() if callable(_field.default)
                             else _field.default)
                if is_dataclass(__default):
                    __default = asdict(__default)
                elif isinstance(__default, Enum):
                    __default = __default.value

            # Branch 2: default produced by a factory callable
            elif _field.default_factory is not MISSING:
                __default = (_field.default_factory()
                             if callable(_field.default_factory)
                             else _field.default_factory)
                if is_dataclass(__default):
                    __default = asdict(__default)
                elif isinstance(__default, Enum):
                    __default = __default.value

            # Branch 3: fall back to the value stored in field metadata
            else:
                __default = __metadata.get("default", None)

            # Build field information dictionary
            __fields.append({
                "name": __name,
                "types": __type,
                "default": __default,
                "metadata": __metadata,
            })

        return __fields
