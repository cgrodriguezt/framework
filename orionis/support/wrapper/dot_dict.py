from __future__ import annotations
from typing import Any

class DotDict(dict):

    __slots__ = ()

    def __getattr__(self, key: str) -> object | None:
        """
        Retrieve a value using attribute-style access.

        Parameters
        ----------
        key : str
            Attribute name to retrieve.

        Returns
        -------
        Any or None
            Value associated with the key, converted to DotDict if it is a dict.
            Returns None if the key does not exist.

        Notes
        -----
        Enables attribute-style access for dictionary keys. Converts plain dicts
        to DotDict for consistency.
        """
        try:
            value = self[key]
            # Convert plain dicts to DotDict for attribute access
            if isinstance(value, dict) and not isinstance(value, DotDict):
                value = DotDict(value)
                self[key] = value
            return value
        except KeyError:
            # Return None if the key does not exist
            return None

    def __setattr__(self, key: str, value: object) -> None:
        """
        Set an attribute on the DotDict instance.

        Parameters
        ----------
        key : str
            Attribute name to set.
        value : Any
            Value to assign. If a dict (not DotDict), it is converted to DotDict.

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Enables attribute-style assignment for dictionary keys. Converts plain
        dicts to DotDict for recursive attribute access.
        """
        # Convert plain dicts to DotDict for recursive attribute access
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
        # Store the value in the underlying dictionary
        self[key] = value

    def __delattr__(self, key: str) -> None:
        """
        Delete an attribute from the DotDict instance.

        Parameters
        ----------
        key : str
            Name of the attribute to delete.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        AttributeError
            If the attribute does not exist in the DotDict.

        Notes
        -----
        Supports attribute-style deletion for dictionary keys.
        """
        try:
            # Attempt to delete the key from the dictionary
            del self[key]
        except KeyError as e:
            error_msg = (
                f"'{self.__class__.__name__}' has no attribute '{key}'"
            )
            raise AttributeError(error_msg) from e

    def get(self, key: str, default: object | None = None) -> object | None:
        """
        Get the value for a key, returning default if the key is not found.

        Parameters
        ----------
        key : str
            The key to look up in the dictionary.
        default : object or None, optional
            The value to return if the key is not found. Defaults to None.

        Returns
        -------
        object or None
            The value associated with the key, converted to DotDict if it is a
            dict. Returns the specified default value if the key is not present.
        """
        # Retrieve the value using the base dict's get method
        value = super().get(key, default)
        # Convert plain dicts to DotDict for consistency
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
            self[key] = value
        return value

    def export(self) -> dict[str, Any]:
        """
        Export the DotDict as a standard dictionary recursively.

        Returns
        -------
        dict
            A dictionary where all nested DotDict instances are converted to
            standard dictionaries. Non-DotDict values are returned unchanged.
        """
        result: dict[str, Any] = {}
        # Recursively convert DotDicts to dicts for all key-value pairs
        for k, v in self.items():
            if isinstance(v, DotDict):
                result[k] = v.export()
            else:
                result[k] = v
        return result

    def copy(self) -> DotDict:
        """
        Create a deep copy of the DotDict.

        Returns
        -------
        DotDict
            A new DotDict instance with recursively copied contents.
        """
        copied = {}
        # Recursively copy all nested DotDict and dict objects
        for k, v in self.items():
            if isinstance(v, DotDict):
                copied[k] = v.copy()
            elif isinstance(v, dict):
                copied[k] = DotDict(v).copy()
            else:
                copied[k] = v
        return DotDict(copied)

    def __repr__(self) -> str:
        """
        Return the string representation of the DotDict.

        Returns
        -------
        str
            String representation of the DotDict in the format 'DotDict({...})'.
        """
        # Use the base dict's __repr__ for the contents, but keep DotDict class name
        return super().__repr__()
