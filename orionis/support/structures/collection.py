from __future__ import annotations
import contextlib
import json
import operator
import random
import secrets
from functools import reduce
from itertools import groupby
from typing import TYPE_CHECKING, Any

from dotty_dict import Dotty, dotty

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

class Collection:

    def __hash__(self) -> int:
        """Return hash of the collection."""
        return hash(tuple(self._items))

    def __init__(self, items: list[Any] | None = None) -> None:
        """
        Initialize a new Collection instance.

        Parameters
        ----------
        items : list[Any] or None, optional
            Initial items for the collection (default is None).

        Returns
        -------
        None
            This method does not return a value.
        """
        self._items = items or []
        self.__appends__ = []

    def take(self, number: int) -> Collection:
        """
        Take a specific number of items from the collection.

        Parameters
        ----------
        number : int
            The number of items to take. If negative, takes from the end.

        Returns
        -------
        Collection
            A new Collection containing the specified number of items.
        """
        # Take items from the end if number is negative, otherwise from the start
        if number < 0:
            return self[number:]
        return self[:number]

    def first(self, callback: Callable | None = None) -> object:
        """
        Return the first item in the collection, optionally filtered by a callback.

        Parameters
        ----------
        callback : Callable | None, optional
            A function to filter items before returning the first one,
            by default None.

        Returns
        -------
        object
            The first item in the filtered collection, or None if empty.
        """
        filtered = self
        # Filter the collection using the provided callback
        if callback:
            filtered = self.filter(callback)
        response = None
        # Return the first item if the collection is not empty
        if filtered:
            response = filtered[0]
        return response

    def last(self, callback: Callable | None = None) -> object:
        """
        Return the last item in the collection, optionally filtered by a callback.

        Parameters
        ----------
        callback : Callable | None, optional
            Function to filter items before returning the last one, by default None.

        Returns
        -------
        object
            The last item in the filtered collection, or raises IndexError if empty.
        """
        filtered = self
        # Filter the collection using the provided callback
        if callback:
            filtered = self.filter(callback)
        return filtered[-1]

    def all(self) -> list[Any]:
        """
        Return all items in the collection.

        Returns
        -------
        list of Any
            All items contained in the collection.
        """
        return self._items

    def avg(self, key: str | None = None) -> float:
        """
        Compute the average of the items.

        Parameters
        ----------
        key : str | None, optional
            The key to use for calculating the average of values.
            If None, use all items.

        Returns
        -------
        float
            The average value of the items. Returns 0 if calculation fails.
        """
        result = 0
        # Get values using the key or use all items if key is None
        items = self.__getValue(key) or self._items
        with contextlib.suppress(TypeError):
            result = sum(items) / len(items)
        return result

    def max(self, key: str | None = None) -> object:
        """
        Return the maximum value from the items.

        Parameters
        ----------
        key : str | None, optional
            The key to use for finding the maximum value. If None, use all items.

        Returns
        -------
        object
            The maximum value found, or 0 if not found or on error.
        """
        # Get values using the key or use all items if key is None
        result = 0
        items = self.__getValue(key) or self._items
        try:
            return max(items)
        except (TypeError, ValueError):
            pass
        return result

    def min(self, key: str | None = None) -> object:
        """
        Return the minimum value from the items.

        Parameters
        ----------
        key : str | None, optional
            The key to use for finding the minimum value. If None, use all items.

        Returns
        -------
        object
            The minimum value found, or 0 if not found or on error.
        """
        result = 0
        items = self.__getValue(key) or self._items
        try:
            return min(items)
        except (TypeError, ValueError):
            pass
        return result

    def chunk(self, size: int) -> Collection:
        """
        Divide the collection into smaller collections of a specified size.

        Parameters
        ----------
        size : int
            Number of items in each chunk.

        Returns
        -------
        Collection
            A new Collection containing sub-collections (chunks) of the specified size.
        """
        # Create chunks using list comprehension
        items = [self[i : i + size] for i in range(0, self.count(), size)]
        return self.__class__(items)

    def collapse(self) -> Collection:
        """
        Collapse the collection of arrays into a single, flat collection.

        Returns
        -------
        Collection
            A new Collection containing all items from nested arrays, flattened.
        """
        items = []
        # Flatten all nested arrays into a single list
        for item in self:
            items += self.__getItems(item)
        return self.__class__(items)

    def contains(
        self, key: str | Callable, value: object = None,
    ) -> bool:
        """
        Check if the collection contains a given item.

        Parameters
        ----------
        key : str or Callable
            The key to check for, or a callback function.
        value : Any, optional
            The value to match when key is a string, by default None.

        Returns
        -------
        bool
            True if the item is found, False otherwise.
        """
        # If a value is provided, check for the key-value pair using a lambda.
        if value is not None:
            return self.contains(lambda x: self.__dataGet(x, key) == value)

        # If key is callable, check if any item matches the callback.
        if self.__checkIsCallable(key, raise_exception=False):
            return self.first(key) is not None

        # Otherwise, check if key is in the collection.
        return key in self

    def count(self) -> int:
        """
        Return the number of items in the collection.

        Returns
        -------
        int
            The number of items in the collection.
        """
        # Return the length of the internal _items list
        return len(self._items)

    def diff(self, items: list[Any] | Collection) -> Collection:
        """
        Return items not present in the given collection.

        Parameters
        ----------
        items : list[Any] | Collection
            The items to compare against.

        Returns
        -------
        Collection
            A new collection containing items not found in the provided collection.
        """
        # Extract items from Collection if necessary
        items = self.__getItems(items)
        # Build a new collection with items not in the provided collection
        return self.__class__([x for x in self if x not in items])

    def each(self, callback: Callable) -> Collection:
        """
        Iterate over items and apply the callback to each.

        Parameters
        ----------
        callback : Callable
            The callback function to apply to each item.

        Returns
        -------
        Collection
            The current collection instance.
        """
        self.__checkIsCallable(callback)
        # Apply the callback to each item; break if callback returns falsy.
        for k, v in enumerate(self):
            result = callback(v)
            if not result:
                break
            self[k] = result
        return self

    def every(self, callback: Callable) -> bool:
        """
        Determine whether all items satisfy the given callback condition.

        Parameters
        ----------
        callback : Callable
            The callback function to test each item.

        Returns
        -------
        bool
            True if all items pass the test, otherwise False.
        """
        self.__checkIsCallable(callback)
        # Use all() to check if every item satisfies the callback condition
        return all(callback(x) for x in self)

    def filter(self, callback: Callable) -> Collection:
        """
        Filter items in the collection using a callback.

        Parameters
        ----------
        callback : Callable
            Function to determine if an item should be included.

        Returns
        -------
        Collection
            A new Collection containing items for which the callback returns True.
        """
        # Ensure the callback is callable before filtering
        self.__checkIsCallable(callback)
        return self.__class__(list(filter(callback, self)))

    def flatten(self) -> Collection:
        """
        Flatten the collection into a single dimension.

        Returns
        -------
        Collection
            A new Collection containing all items, flattened to a single dimension.
        """
        def _flatten(items: object) -> Iterator[Any]:
            if isinstance(items, dict):
                for v in items.values():
                    yield from _flatten(v)
            elif isinstance(items, list):
                for i in items:
                    yield from _flatten(i)
            else:
                yield items

        return self.__class__(list(_flatten(self._items)))

    def forget(self, *keys: int | str) -> Collection:
        """
        Remove items from the collection by their keys.

        Parameters
        ----------
        *keys : Any
            The keys of the items to remove from the collection.

        Returns
        -------
        Collection
            The current collection instance after removal.
        """
        # Sort keys in reverse order to avoid index shifting issues during deletion
        keys = sorted(keys, reverse=True)
        for key in keys:
            del self[key]
        return self

    def forPage(self, page: int, number: int) -> Collection:
        """
        Slice the collection for pagination.

        Parameters
        ----------
        page : int
            The page number to retrieve.
        number : int
            The number of items per page.

        Returns
        -------
        Collection
            A new Collection containing the paginated items.
        """
        # Calculate start and end indices for the requested page
        start = (page - 1) * number
        end = start + number
        return self.__class__(self[start:end])

    def get(self, key: int | str, default: object = None) -> object:
        """
        Retrieve an item from the collection by key.

        Parameters
        ----------
        key : Any
            The key or index to retrieve from the collection.
        default : Any, optional
            The value to return if the key is not found. Defaults to None.

        Returns
        -------
        Any
            The item at the specified key, or the default value if not found.
        """
        try:
            return self[key]
        except IndexError:
            pass
        return self.__value(default)

    def implode(self, glue: str = ",", key: str | None = None) -> str:
        """
        Join all items in the collection into a single string.

        Parameters
        ----------
        glue : str, optional
            String used to join the items. Default is ",".
        key : str | None, optional
            Key to extract from each item before joining. Default is None.

        Returns
        -------
        str
            A string with all items joined by the specified glue.
        """
        first = self.first()
        # If items are not strings and a key is provided, pluck the key values
        if not isinstance(first, str) and key:
            return glue.join(self.pluck(key))
        # Otherwise, join string representations of all items
        return glue.join([str(x) for x in self])

    def isEmpty(self) -> bool:
        """
        Check if the collection is empty.

        Returns
        -------
        bool
            True if the collection is empty, otherwise False.
        """
        # Return True if the collection has no items
        return not self

    def map(self, callback: Callable) -> Collection:
        """
        Apply a function to each item in the collection.

        Parameters
        ----------
        callback : Callable
            Function to apply to each item.

        Returns
        -------
        Collection
            A new Collection containing the mapped items.
        """
        # Ensure the callback is callable before mapping
        self.__checkIsCallable(callback)
        items = [callback(x) for x in self]
        return self.__class__(items)

    def mapInto(
        self, cls: type, method: str | None = None, **kwargs: object,
    ) -> Collection:
        """
        Map items into instances of the given class.

        Parameters
        ----------
        cls : type
            The class to map items into.
        method : str | None, optional
            The method to call on the class, by default None.
        **kwargs : Any
            Additional keyword arguments to pass to the constructor or method.

        Returns
        -------
        Collection
            A new collection with the mapped instances.
        """
        results = []
        # Iterate through each item and map into the class or its method
        for item in self:
            if method:
                results.append(getattr(cls, method)(item, **kwargs))
            else:
                results.append(cls(item))
        return self.__class__(results)

    def merge(self, items: list[Any] | Collection) -> Collection:
        """
        Merge the collection with the given items.

        Parameters
        ----------
        items : list[Any] | Collection
            The items to merge into the collection.

        Returns
        -------
        Collection
            The current collection instance with merged items.

        Raises
        ------
        TypeError
            If items cannot be merged due to incompatible types.
        """
        # Ensure items is a list or Collection before merging
        if not isinstance(items, list):
            error_msg = "Unable to merge incompatible types"
            raise TypeError(error_msg)

        items = self.__getItems(items)
        self._items += items
        return self

    def pluck( # NOSONAR
        self, value: str, key: str | None = None,
    ) -> Collection:
        """
        Extract values for a given key from all items.

        Parameters
        ----------
        value : str
            The key to extract from each item.
        key : str | None, optional
            The key to use as the result key, by default None.

        Returns
        -------
        Collection
            A new collection containing the plucked values.
        """
        # Use a dictionary if a result key is provided, otherwise use a list
        if key:
            attributes: dict[Any, Any] = {}
        else:
            attributes: list[Any] = []

        # Handle the case where the collection's items are a dictionary
        if isinstance(self._items, dict):
            return Collection([self._items.get(value)])

        # Iterate through each item and pluck the desired value
        for item in self:
            if isinstance(item, dict):
                iterable = item.items()
            elif hasattr(item, "serialize"):
                iterable = item.serialize().items()
            else:
                iterable = self.all().items()

            for k, v in iterable:
                if k == value:
                    if key:
                        attributes[self.__dataGet(item, key)] = self.__dataGet(
                            item, value,
                        )
                    else:
                        attributes.append(v)

        return Collection(attributes)

    def pop(self) -> object:
        """
        Remove and return the last item from the collection.

        Returns
        -------
        Any
            The last item from the collection.
        """
        # Remove and return the last item in the internal _items list
        return self._items.pop()

    def prepend(self, value: object) -> Collection:
        """
        Prepend an item to the beginning of the collection.

        Parameters
        ----------
        value : Any
            The value to prepend to the collection.

        Returns
        -------
        Collection
            The current collection instance with the new item prepended.
        """
        # Insert the value at the start of the internal _items list
        self._items.insert(0, value)
        return self

    def pull(self, key: int | str) -> object:
        """
        Remove and return an item from the collection by key.

        Parameters
        ----------
        key : Any
            The key of the item to remove.

        Returns
        -------
        Any
            The removed item, or None if not found.
        """
        # Retrieve the value at the specified key, then remove it from the collection
        value = self.get(key)
        self.forget(key)
        return value

    def push(self, value: object) -> Collection:
        """
        Add an item to the end of the collection.

        Parameters
        ----------
        value : Any
            The value to add to the collection.

        Returns
        -------
        Collection
            The current collection instance with the new item appended.
        """
        # Append the value to the internal _items list
        self._items.append(value)
        return self

    def put(self, key: int | str, value: object) -> Collection:
        """
        Insert or update an item in the collection at the specified key.

        Parameters
        ----------
        key : Any
            The key or index at which to set the value.
        value : Any
            The value to assign at the specified key.

        Returns
        -------
        Collection
            The current collection instance with the updated item.
        """
        # Set the value at the specified key in the collection
        self[key] = value
        return self

    def random(self, count: int | None = None) -> object | Collection | None:
        """
        Return one or more random items from the collection.

        Parameters
        ----------
        count : int | None, optional
            The number of items to return. If None, returns a single item.

        Returns
        -------
        Any | Collection | None
            A single random item if count is None, a Collection if count is given,
            or None if the collection is empty.

        Raises
        ------
        ValueError
            If count is greater than the number of items in the collection.
        """
        collection_count = self.count()
        if collection_count == 0:
            return None
        if count and count > collection_count:
            error_msg = "count argument must be inferior to collection length."
            raise ValueError(error_msg)
        if count:
            # Select 'count' random items and update the collection
            self._items = random.sample(self._items, k=count)
            return self
        # Return a single random item
        return secrets.choice(self._items)

    def reduce(self, callback: Callable, initial: object = 0) -> object:
        """
        Reduce the collection to a single value using a callback.

        Parameters
        ----------
        callback : Callable
            The function to apply cumulatively to the items.
        initial : Any, optional
            The initial value to start the reduction, by default 0.

        Returns
        -------
        Any
            The reduced value after applying the callback.
        """
        # Use functools.reduce to accumulate values in the collection
        return reduce(callback, self, initial)

    def reject(self, callback: Callable) -> Collection:
        """
        Reject items that pass a given truth test.

        Parameters
        ----------
        callback : Callable
            The callback function to test items.

        Returns
        -------
        Collection
            The current collection instance with items not passing the test.
        """
        # Ensure the callback is callable before filtering
        self.__checkIsCallable(callback)
        # Filter items that do not satisfy the callback
        items = self.__getValue(callback) or self._items
        self._items = items
        return self

    def reverse(self) -> Collection:
        """
        Reverse the order of items in the collection.

        Returns
        -------
        Collection
            The current collection instance with items in reversed order.
        """
        # Reverse the items using slicing
        self._items = self[::-1]
        return self

    def serialize(self) -> list[Any]:
        """
        Serialize the collection items as a list.

        Returns
        -------
        list of Any
            The serialized items in the collection.
        """
        def _serialize(item: object) -> object:
            # Set appends if present for each item
            if self.__appends__:
                item.set_appends(self.__appends__)
            # Prefer serialize method, then to_dict, else return as is
            if hasattr(item, "serialize"):
                return item.serialize()
            if hasattr(item, "to_dict"):
                return item.to_dict()
            return item

        return list(map(_serialize, self))

    def shift(self) -> object:
        """
        Remove and return the first item from the collection.

        Returns
        -------
        Any
            The first item from the collection, or None if the collection is empty.
        """
        # Remove and return the first item using pull(0)
        return self.pull(0)

    def sort(self, key: str | None = None) -> Collection:
        """
        Sort the items in the collection.

        Parameters
        ----------
        key : str | None, optional
            The key to sort by. If None, sort items directly.

        Returns
        -------
        Collection
            The current collection instance with sorted items.
        """
        # Sort by key if provided, otherwise sort items directly
        if key:
            self._items.sort(key=lambda x: x[key], reverse=False)
            return self

        self._items = sorted(self)
        return self

    def sum(self, key: str | None = None) -> float:
        """
        Compute the sum of the given values.

        Parameters
        ----------
        key : str | None, optional
            The key to sum by. If None, sum all items.

        Returns
        -------
        float
            The sum of the values. Returns 0 if calculation fails.
        """
        result = 0
        # Get values using the key or use all items if key is None
        items = self.__getValue(key) or self._items
        with contextlib.suppress(TypeError):
            result = sum(items)
        return result

    def toJson(self, **kwargs: object) -> str:
        """
        Return the collection items as a JSON string.

        Parameters
        ----------
        **kwargs : Any
            Additional arguments to pass to json.dumps.

        Returns
        -------
        str
            JSON representation of the serialized collection items.
        """
        # Serialize the collection and convert to JSON string
        return json.dumps(self.serialize(), **kwargs)

    def groupBy(self, key: str) -> Collection:
        """
        Group items in the collection by a specified key.

        Parameters
        ----------
        key : str
            The key to group items by.

        Returns
        -------
        Collection
            A new Collection instance containing a dictionary where each key is a
            unique value from the specified key, and each value is a list of items
            sharing that key.
        """
        # Sort items by the specified key to prepare for grouping
        self.sort(key)

        new_dict: dict[Any, list[Any]] = {}

        # Group items and collect them into the dictionary
        for k, v in groupby(self._items, key=lambda x: x[key]):
            new_dict[k] = list(v)

        return Collection(new_dict)

    def transform(self, callback: Callable) -> Collection:
        """
        Transform each item in the collection using a callback.

        Parameters
        ----------
        callback : Callable
            The callback function to transform items.

        Returns
        -------
        Collection
            The current collection instance with transformed items.
        """
        # Ensure the callback is callable before transforming items
        self.__checkIsCallable(callback)
        self._items = self.__getValue(callback)
        return self

    def unique(self, key: str | None = None) -> Collection:
        """
        Return unique items from the collection.

        Parameters
        ----------
        key : str | None, optional
            The key to use for uniqueness comparison. If None, use items directly.

        Returns
        -------
        Collection
            A new Collection containing only unique items.
        """
        # If no key is provided, use set to get unique items directly
        if not key:
            items = list(set(self._items))
            return self.__class__(items)

        keys: set[Any] = set()
        items: list[Any] = []
        # If the collection is a dict, return as is (no uniqueness logic)
        if isinstance(self.all(), dict):
            return self

        # Iterate and collect unique items based on the key
        for item in self:
            if isinstance(item, dict):
                comparison = item.get(key)
            elif isinstance(item, str):
                comparison = item
            else:
                comparison = getattr(item, key)
            if comparison not in keys:
                items.append(item)
                keys.add(comparison)

        return self.__class__(items)

    def where(self, key: str, *args: object) -> Collection:
        """
        Filter items by a given key-value pair or comparison.

        Parameters
        ----------
        key : str
            The key to filter by.
        *args : Any
            The operator and value, or just the value.

        Returns
        -------
        Collection
            A new Collection instance containing filtered items.
        """
        op: str = "=="
        value: Any = args[0]
        min_args_for_operator = 2

        # If an operator is provided, use it and the next argument as value
        if len(args) >= min_args_for_operator:
            op = args[0]
            value = args[1]

        attributes: list[Any] = []

        # Iterate and filter items based on the key and comparison
        for item in self._items:
            comparison = item.get(key) if isinstance(item, dict) else getattr(item, key)
            if self.__makeComparison(comparison, value, op):
                attributes.append(item)

        return self.__class__(attributes)

    def whereIn(
        self, key: str, values: list[Any] | Collection,
    ) -> Collection:
        """
        Filter items where a given key's value is in a list of values.

        Parameters
        ----------
        key : str
            The key to filter by.
        values : list[Any] | Collection
            The list of values to check against.

        Returns
        -------
        Collection
            A new collection containing items where the key's value is in values.
        """
        # Extract values from Collection if necessary
        values = self.__getItems(values)
        attributes: list[Any] = []

        # Iterate and collect items where the key's value is in the provided values
        for item in self._items:
            if isinstance(item, dict):
                comparison = item.get(key)
            else:
                comparison = getattr(item, key, None)

            # Support string comparison for numeric values
            if comparison in values or str(comparison) in [str(v) for v in values]:
                attributes.append(item)

        return self.__class__(attributes)

    def whereNotIn(
        self, key: str, values: list[Any] | Collection,
    ) -> Collection:
        """
        Filter items where a given key's value is not in a list of values.

        Parameters
        ----------
        key : str
            The key to filter by.
        values : list[Any] | Collection
            The list of values to check against.

        Returns
        -------
        Collection
            A new Collection containing items where the key's value is not in values.
        """
        # Extract values from Collection if necessary
        values = self.__getItems(values)
        attributes: list[Any] = []

        # Iterate and collect items where the key's value is not in the provided values
        for item in self._items:
            if isinstance(item, dict):
                comparison = item.get(key)
            else:
                comparison = getattr(item, key, None)

            # Support string comparison for numeric values
            if comparison not in values and str(comparison) not in [
                str(v) for v in values
            ]:
                attributes.append(item)

        return self.__class__(attributes)

    def zip(self, items: list[Any] | Collection) -> Collection:
        """
        Zip the collection with the given items by index.

        Parameters
        ----------
        items : list[Any] | Collection
            The items to zip with.

        Returns
        -------
        Collection
            A new Collection containing pairs of items from both collections.

        Raises
        ------
        ValueError
            If the 'items' parameter is not a list or Collection.
        """
        # Extract items from Collection if necessary
        items = self.__getItems(items)
        if not isinstance(items, list):
            error_msg = "The 'items' parameter must be a list or a Collection"
            raise TypeError(error_msg)

        # Pair items from both collections by index
        _items: list[list[Any]] = []
        for x, y in zip(self, items, strict=False):
            _items.append([x, y])
        return self.__class__(_items)

    def setAppends(self, appends: list[str]) -> Collection:
        """
        Set the attributes to append to the Collection.

        Parameters
        ----------
        appends : list[str]
            The attributes to append.

        Returns
        -------
        Collection
            The current collection instance.
        """
        # Extend the __appends__ list with the provided attributes
        self.__appends__ += appends
        return self

    def __getValue(
        self, key: str | Callable | None,
    ) -> list[Any] | None:
        """
        Retrieve values from items using a key or callback.

        Parameters
        ----------
        key : str | Callable | None
            The key to extract or callback to apply.

        Returns
        -------
        list[Any] | None
            List of extracted values, or None if key is not provided.
        """
        if not key:
            return None

        items: list[Any] = []
        # Iterate through each item and extract value by key or callback
        for item in self:
            if isinstance(key, str):
                # Support both attribute and dict key access
                if hasattr(item, key):
                    items.append(getattr(item, key))
                elif isinstance(item, dict) and key in item:
                    items.append(item[key])
            elif callable(key):
                result = key(item)
                if result:
                    items.append(result)
        return items

    def __dataGet(
        self, item: object, key: str, default: object = None,
    ) -> object:
        """
        Retrieve a value from an item using a nested key notation.

        Parameters
        ----------
        item : Any
            The item to extract data from.
        key : str
            The key to look for, supports nested notation.
        default : Any, optional
            The value to return if the key is not found. Defaults to None.

        Returns
        -------
        Any
            The extracted value if found, otherwise the default value.
        """
        try:
            # Handle list or tuple by index
            if isinstance(item, (list, tuple)):
                item = item[key]
            # Handle dict or Dotty for nested key access
            elif isinstance(item, (dict, Dotty)):
                dotty_key = key.replace("*", ":")
                dotty_item = dotty(item)
                item = dotty_item.get(dotty_key, default)
            # Handle object attribute access
            elif isinstance(item, object):
                item = getattr(item, key)
        except (IndexError, AttributeError, KeyError, TypeError):
            return self.__value(default)
        return item

    def __value(self, value: object) -> object:
        """
        Return the evaluated value if callable, otherwise return the value itself.

        Parameters
        ----------
        value : Any
            The value or callable to evaluate.

        Returns
        -------
        Any
            The result of calling the value if it is callable, otherwise the value
            itself.
        """
        # Evaluate the value if it is callable, otherwise return as is
        if callable(value):
            return value() # NOSONAR
        return value

    def __checkIsCallable(
        self, callback: object, *, raise_exception: bool = True,
    ) -> bool:
        """
        Check if the given callback is callable.

        Parameters
        ----------
        callback : Any
            The callback to check.
        raise_exception : bool, optional
            Whether to raise an exception if not callable. Default is True.

        Returns
        -------
        bool
            True if the callback is callable, otherwise False.

        Raises
        ------
        ValueError
            If callback is not callable and raise_exception is True.
        """
        # Return False or raise an error if callback is not callable
        if not callable(callback):
            if not raise_exception:
                return False
            error_msg = "The 'callback' should be a function"
            raise ValueError(error_msg)
        return True

    def __makeComparison(self, a: object, b: object, op: str) -> bool:
        """
        Compare two values using the specified operator.

        Parameters
        ----------
        a : Any
            The first value to compare.
        b : Any
            The second value to compare.
        op : str
            The comparison operator as a string.

        Returns
        -------
        bool
            True if the comparison is valid, otherwise False.
        """
        # Map string operators to their corresponding functions
        operators = {
            "<": operator.lt,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
            ">": operator.gt,
            ">=": operator.ge,
        }
        return operators[op](a, b)

    def __iter__(self) -> Iterator[Any]:
        """
        Iterate over the items in the collection.

        Yields
        ------
        Any
            Each item in the collection.
        """
        # Yield each item in the internal _items list
        yield from self._items

    def __eq__(self, other: object) -> bool:
        """
        Compare the collection with another object for equality.

        Parameters
        ----------
        other : object
            The object to compare with the current collection.

        Returns
        -------
        bool
            True if the collections are equal, False otherwise.
        """
        # Compare items if other is a Collection, else compare directly
        if isinstance(other, Collection):
            return other.all() == self._items
        return other == self._items

    def __getitem__(
        self, item: int | slice,
    ) -> object | Collection:
        """
        Retrieve an item or a slice from the collection.

        Parameters
        ----------
        item : int or slice
            The index or slice to retrieve.

        Returns
        -------
        Any or Collection
            The item at the given index, or a new Collection for a slice.
        """
        # Return a new Collection if a slice is provided, else return the item.
        if isinstance(item, slice):
            return self.__class__(self._items[item])
        return self._items[item]

    def __setitem__(self, key: int | str, value: object) -> None:
        """
        Set the value at the specified key in the collection.

        Parameters
        ----------
        key : Any
            The index or key at which to set the value.
        value : Any
            The value to assign at the specified key.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Assign the value to the specified key in the internal _items list
        self._items[key] = value

    def __delitem__(self, key: int | str) -> None:
        """
        Delete an item from the collection at the specified key.

        Parameters
        ----------
        key : Any
            The index or key of the item to remove.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Remove the item at the specified key from the internal _items list
        del self._items[key]

    def __ne__(self, other: object) -> bool:
        """
        Determine if the collection is not equal to another object.

        Parameters
        ----------
        other : object
            The object to compare with the current collection.

        Returns
        -------
        bool
            True if the collections are not equal, otherwise False.
        """
        # Extract items from the other object if it is a Collection
        other = self.__getItems(other)
        # Return True if the items are not equal, otherwise False
        return other != self._items

    def __len__(self) -> int:
        """
        Return the number of items in the collection.

        Returns
        -------
        int
            The total number of items in the collection.
        """
        # Return the length of the internal _items list
        return len(self._items)

    def __le__(self, other: object) -> bool:
        """
        Compare if the current collection is less than or equal to another object.

        Parameters
        ----------
        other : object
            The object to compare with the current collection.

        Returns
        -------
        bool
            True if the current collection is less than or equal to the other object,
            False otherwise.
        """
        # Extract items from the other object if it is a Collection
        other = self.__getItems(other)
        # Return True if the items are less than or equal, False otherwise
        return self._items <= other

    def __lt__(self, other: object) -> bool:
        """
        Compare if the current collection is less than another object.

        Parameters
        ----------
        other : object
            Object to compare with the current collection.

        Returns
        -------
        bool
            True if the current collection is less than the other object,
            otherwise False.
        """
        # Extract items from the other object if it is a Collection
        other = self.__getItems(other)
        # Return True if the items are less than, otherwise False
        return self._items < other

    def __ge__(self, other: object) -> bool:
        """
        Compare if the current collection is greater than or equal to another object.

        Parameters
        ----------
        other : object
            Object to compare with the current collection.

        Returns
        -------
        bool
            True if the current collection is greater than or equal to the other
            object, otherwise False.
        """
        # Extract items from the other object if it is a Collection
        other = self.__getItems(other)
        # Return True if the items are greater than or equal, otherwise False
        return self._items >= other

    def __gt__(self, other: object) -> bool:
        """
        Compare if the current collection is greater than another object.

        Parameters
        ----------
        other : object
            The object to compare with the current collection.

        Returns
        -------
        bool
            True if the current collection is greater than the other object,
            otherwise False.
        """
        # Extract items from the other object if it is a Collection
        other = self.__getItems(other)
        # Return True if the items are greater than, otherwise False
        return self._items > other

    @classmethod
    def __getItems(cls, items: list[Any] | Collection | object) -> list[Any] | object:
        """
        Extract the underlying items from a Collection or return the input as-is.

        Parameters
        ----------
        items : list[Any] | Collection | object
            The input to extract items from. If a Collection, its items are
            returned; otherwise, the input is returned unchanged.

        Returns
        -------
        list[Any] | object
            The extracted items if `items` is a Collection, otherwise the
            original input.
        """
        # If the input is a Collection, extract its items using the all() method
        if isinstance(items, Collection):
            items = items.all()
        return items


