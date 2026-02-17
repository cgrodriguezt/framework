from typing import Iterable, Iterator

class Headers:

    __slots__ = ("_items",)

    def __init__(self, raw: Iterable[tuple[str, str]]) -> None:
        """
        Initialize the Headers object with an iterable of key-value pairs.

        Parameters
        ----------
        raw : Iterable[tuple[str, str]]
            Iterable containing header key-value pairs.

        Returns
        -------
        None
            This method does not return a value.
        """
        self._items = list(raw)

    def get(self, key: str, default: str | None = None) -> str | None:
        """
        Retrieve the last value for the specified header key.

        Parameters
        ----------
        key : str
            The header key to search for.
        default : str | None, optional
            Value to return if the key is not found (default is None).

        Returns
        -------
        str | None
            The value associated with the key, or the default if not found.
        """
        key_lower = key.lower()
        for k, v in reversed(self._items):
            if k.lower() == key_lower:
                return v
        return default

    def getAll(self, key: str | None = None) -> dict[str, str | list[str]]:
        """
        Retrieve all values for a given key or all keys.

        Parameters
        ----------
        key : str | None, optional
            Header key to search for. If None, returns all keys.

        Returns
        -------
        dict[str, str | list[str]]
            Dictionary mapping keys to a string or list of strings.
        """
        def smart_assign(values: list[str]) -> str | list[str]:
            # Return a single value if only one, else the list of values
            return values[0] if len(values) == 1 else values

        if key is None:
            # Collect all values for each key (case-insensitive)
            result: dict[str, list[str]] = {}
            for k, v in self._items:
                k_lower = k.lower()
                result.setdefault(k_lower, []).append(v)
            return {k: smart_assign(vs) for k, vs in result.items()}
        key_lower = key.lower()
        values = [v for k_, v in self._items if k_.lower() == key_lower]
        if not values:
            return {}
        return {key: smart_assign(values)}

    def __contains__(self, key: str) -> bool:
        """
        Check if the specified header key exists.

        Parameters
        ----------
        key : str
            The header key to check.

        Returns
        -------
        bool
            True if the key exists, False otherwise.
        """
        key_lower = key.lower()
        return any(k.lower() == key_lower for k, _ in self._items)

    def __getitem__(self, key: str) -> str:
        """
        Retrieve the last value for the specified header key.

        Parameters
        ----------
        key : str
            The header key to retrieve.

        Returns
        -------
        str
            The value associated with the key.

        Raises
        ------
        KeyError
            If the key is not found.
        """
        value = self.get(key)
        if value is None:
            error_msg = key
            raise KeyError(error_msg)
        return value

    def __iter__(self) -> Iterator[tuple[str, str]]:
        """
        Return an iterator over the header key-value pairs.

        Returns
        -------
        Iterator[tuple[str, str]]
            An iterator over the header items.
        """
        return iter(self._items)

    def items(self) -> list[tuple[str, str]]:
        """
        Return a list of all header key-value pairs.

        Returns
        -------
        list[tuple[str, str]]
            A list of all header items.
        """
        return list(self._items)

    def keys(self) -> set[str]:
        """
        Return all unique header keys.

        Returns
        -------
        set[str]
            Set of all unique header keys.
        """
        return {k for k, _ in self._items}

    def values(self) -> list[str]:
        """
        Return a list of all header values.

        Returns
        -------
        list[str]
            A list of all header values.
        """
        return [v for _, v in self._items]

    def __len__(self) -> int:
        """
        Return the number of header key-value pairs.

        Returns
        -------
        int
            The number of header items.
        """
        return len(self._items)

    def __repr__(self) -> str:
        """
        Return the string representation of the Headers object.

        Returns
        -------
        str
            The string representation of the Headers instance.
        """
        return f"Headers({self._items!r})"