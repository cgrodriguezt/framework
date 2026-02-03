from __future__ import annotations
from dataclasses import asdict, fields, is_dataclass, MISSING
from enum import Enum

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

    def toDict(self) -> dict:
        """
        Convert the dataclass instance to a dictionary.

        Returns
        -------
        dict
            Dictionary representation of the dataclass instance with enums
            converted to their values.
        """
        # Helper function to serialize enums
        def enum_serializer(obj: object) -> object:
            """Convert enums to their values for serialization."""
            if isinstance(obj, Enum):
                return obj.value
            return obj

        # Convert dataclass to dict with enum serialization
        return asdict(
            self, dict_factory=lambda x: {k: enum_serializer(v) for k, v in x},
        )

    def getFields(self) -> list[dict]: # NOSONAR
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

        # Process each field defined in the dataclass
        for field in fields(self):
            # Extract field name
            __name = field.name

            # Get type name for simple types
            __type = getattr(field.type, "__name__", None)

            # Handle complex types (unions, generics)
            if __type is None:
                type_lst = []
                type_str = str(field.type).split("|")
                type_lst = [itype.strip() for itype in type_str]
                __type = type_lst

            # Ensure type is always a list for consistency
            __type = type_lst if isinstance(__type, list) else [__type]

            # Extract and process metadata
            metadata = dict(field.metadata) if field.metadata else {}

            # Normalize metadata default if present
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

            # Initialize default value
            __default = None

            # Process field default value
            if field.default is not MISSING:
                __default = (field.default() if callable(field.default)
                           else field.default)
                if is_dataclass(__default):
                    __default = asdict(__default)
                elif isinstance(__default, Enum):
                    __default = __default.value

            # Process field default factory
            elif field.default_factory is not MISSING:
                __default = (field.default_factory()
                           if callable(field.default_factory)
                           else field.default_factory)
                if is_dataclass(__default):
                    __default = asdict(__default)
                elif isinstance(__default, Enum):
                    __default = __default.value

            # Use metadata default as fallback
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
