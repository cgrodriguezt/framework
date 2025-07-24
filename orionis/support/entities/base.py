from dataclasses import asdict, fields, is_dataclass, MISSING
from enum import Enum

class BaseEntity:

    def toDict(self) -> dict:
        """
        Converts the current instance into a dictionary representation.

        Returns
        -------
        dict
            Dictionary representation of the current instance.
        """
        return asdict(self)

    def getFields(self):
        """
        Retrieves a list of field information for the current dataclass instance.

        Returns
        -------
        list
            A list of dictionaries, each containing details about a field:
            - name (str): The name of the field.
            - type (type): The type of the field.
            - default: The default value of the field, if specified; otherwise, the value from metadata or None.
            - metadata (mapping): The metadata associated with the field.
        """
        # Dictionary to hold field information
        __fields = []

        # Iterate over the fields of the dataclass and extract relevant information
        for field in fields(self):

            # Get the field name
            __name = field.name

            # Get the field type with better handling for complex types
            __type = getattr(field.type, '__name__', None)

            # If the type is None, handle it
            if __type is None:

                # Handle Union types or other complex types
                type_lst = []
                type_str = str(field.type).split('|')
                for itype in type_str:
                    type_lst.append(itype.strip())
                __type = type_lst

            # Ensure __type is a list for consistency
            __type = type_lst if isinstance(__type, list) else [__type]

            # Extract metadata, default value, and type
            metadata = dict(field.metadata) if field.metadata else {}

            # If metadata contains a default value, normalize it
            if 'default' in metadata:
                metadata_default = metadata['default']
                if callable(metadata_default):
                    metadata_default = metadata_default()
                if is_dataclass(metadata_default):
                    metadata_default = asdict(metadata_default)
                elif isinstance(metadata_default, Enum):
                    metadata_default = metadata_default.value
                metadata['default'] = metadata_default

            # Add the field information to the list
            __metadata = metadata

            # Extract the default value, if specified
            __default = None

            # Field has a direct default value
            if field.default is not MISSING:
                __default = field.default() if callable(field.default) else field.default
                if is_dataclass(__default):
                    __default = asdict(__default)
                elif isinstance(__default, Enum):
                    __default = __default.value

            # Field has a default factory (like list, dict, etc.)
            elif field.default_factory is not MISSING:
                __default = field.default_factory() if callable(field.default_factory) else field.default_factory
                if is_dataclass(__default):
                    __default = asdict(__default)
                elif isinstance(__default, Enum):
                    __default = __default.value

            # No default found, check metadata for custom default
            else:
                __default = __metadata.get('default', None)

            # Append the field information to the list
            __fields.append({
                "name": __name,
                "types": __type,
                "default": __default,
                "metadata": __metadata
            })

        # Return the list of field information
        return __fields