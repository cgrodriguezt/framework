from urllib.parse import parse_qsl
from typing import Iterator

class QueryParams:

    __slots__ = ("_items",)

    def __init__(self, query_string: str) -> None:
        """
        Initialize QueryParams with a query string.

        Parameters
        ----------
        query_string : str
            The query string to parse.

        Returns
        -------
        None
            This method initializes the instance.
        """
        # Parse the query string into a list of key-value pairs.
        self._items: list[tuple[str, str]] = parse_qsl(
            query_string,
            keep_blank_values=True,
            strict_parsing=False,
        )

    def get(self, key: str, default: str | None = None) -> str | None:
        """
        Retrieve the last value for a given key.

        Parameters
        ----------
        key : str
            The key to search for.
        default : str | None, optional
            The value to return if the key is not found (default is None).

        Returns
        -------
        str | None
            The last value associated with the key, or default if not found.
        """
        # Iterate in reverse to get the last occurrence of the key.
        for k, v in reversed(self._items):
            if k == key:
                return v
        return default

    def getAll(self, key: str | None = None) -> dict[str, str | list[str]]:
        """
        Retrieve all values associated with a key or all keys.

        Parameters
        ----------
        key : str | None, optional
            The key to search for. If None, returns all keys with their values.

        Returns
        -------
        dict[str, str | list[str]]
            Dictionary mapping keys to a string (if one value) or a list of strings
            (if multiple values).
        """
        def smart_assign(values: list[str]) -> str | list[str]:
            # Return a single value if only one, else the list of values.
            return values[0] if len(values) == 1 else values

        if key is None:
            # Collect all values for each key.
            result: dict[str, list[str]] = {}
            for k, v in self._items:
                result.setdefault(k, []).append(v)
            return {k: smart_assign(vs) for k, vs in result.items()}
        # Collect all values for the specified key.
        values = [v for k_, v in self._items if k_ == key]
        if not values:
            return {}
        return {key: smart_assign(values)}

    def __contains__(self, key: str) -> bool:
        """
        Check if the key exists in the query parameters.

        Parameters
        ----------
        key : str
            The key to check for.

        Returns
        -------
        bool
            True if the key exists, False otherwise.
        """
        # Check if any key matches the provided key.
        return any(k == key for k, _ in self._items)

    def __getitem__(self, key: str) -> str:
        """
        Retrieve the last value for a given key or raise KeyError.

        Parameters
        ----------
        key : str
            The key to retrieve.

        Returns
        -------
        str
            The last value associated with the key.

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

    def items(self) -> list[tuple[str, str]]:
        """
        Return all key-value pairs as a list.

        Returns
        -------
        list[tuple[str, str]]
            List of all key-value pairs.
        """
        # Return a copy of the internal items list.
        return list(self._items)

    def keys(self) -> set[str]:
        """
        Return all keys in the query parameters.

        Returns
        -------
        set[str]
            Set of all unique keys.
        """
        # Extract all keys from the items.
        return {k for k, _ in self._items}

    def values(self) -> list[str]:
        """
        Return all values in the query parameters.

        Returns
        -------
        list[str]
            List of all values.
        """
        # Extract all values from the items.
        return [v for _, v in self._items]

    def __iter__(self) -> Iterator[tuple[str, str]]:
        """
        Return an iterator over the key-value pairs.

        Returns
        -------
        Iterator[tuple[str, str]]
            Iterator over all key-value pairs.
        """
        # Return an iterator for the items.
        return iter(self._items)

    def __len__(self) -> int:
        """
        Return the number of key-value pairs.

        Returns
        -------
        int
            The number of key-value pairs.
        """
        # Return the length of the items list.
        return len(self._items)

    def __repr__(self) -> str:
        """
        Return the string representation of the QueryParams object.

        Returns
        -------
        str
            String representation of the QueryParams instance.
        """
        # Return a formatted string showing the items.
        return f"QueryParams({self._items!r})"