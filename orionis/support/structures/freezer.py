from types import MappingProxyType
from collections import deque
from typing import Any

class FreezeThaw:

    # ruff: noqa: PLR0912, C901

    @staticmethod
    def _is_container(obj: object) -> bool:
        """
        Determine if the object is a supported container type.

        Parameters
        ----------
        obj : object
            The object to check.

        Returns
        -------
        bool
            True if the object is a MappingProxyType, dict, list, or tuple;
            otherwise, False.
        """
        return isinstance(obj, (MappingProxyType, dict, list, tuple))

    @staticmethod
    def thaw(obj: object) -> object: # NOSONAR
        """
        Recursively convert frozen containers to mutable equivalents.

        Parameters
        ----------
        obj : object
            The object to thaw. Can be a MappingProxyType, dict, list, or tuple.

        Returns
        -------
        object
            A fully mutable object with preserved references. Non-container
            objects are returned unchanged.
        """
        if not FreezeThaw._is_container(obj):
            return obj

        stack = deque([obj])
        cache: dict[int, Any] = {}

        # Traverse and copy containers, preserving references
        while stack:
            current = stack.pop()
            obj_id = id(current)
            if obj_id in cache:
                continue

            if isinstance(current, (MappingProxyType, dict)):
                new_dict: dict[Any, Any] = {}
                cache[obj_id] = new_dict
                for k, v in current.items():
                    # Add containers to stack for recursive thawing
                    if FreezeThaw._is_container(v) and id(v) not in cache:
                        stack.append(v)
                    new_dict[k] = v

            elif isinstance(current, (list, tuple)):
                new_list: list[Any] = [None] * len(current)
                cache[obj_id] = new_list
                for i, v in enumerate(current):
                    # Add containers to stack for recursive thawing
                    if FreezeThaw._is_container(v) and id(v) not in cache:
                        stack.append(v)
                    new_list[i] = v

        # Replace references with thawed objects
        for val in cache.values():
            if isinstance(val, dict):
                for k, v in val.items():
                    if id(v) in cache:
                        val[k] = cache[id(v)]
            elif isinstance(val, list):
                for i, v in enumerate(val):
                    if id(v) in cache:
                        val[i] = cache[id(v)]

        # Convert lists and MappingProxyType to mutable types
        root = cache.get(id(obj), obj)
        if isinstance(root, list):
            return list(root)
        if isinstance(root, dict):
            return dict(root)
        return root

    @staticmethod
    def freeze(obj: object) -> object:  # NOSONAR
        """
        Convert mutable containers to immutable equivalents recursively.

        Parameters
        ----------
        obj : object
            The object to freeze. Can be a dict, list, or tuple.

        Returns
        -------
        object
            A fully immutable object with preserved references. Non-container
            objects or MappingProxyType are returned unchanged.
        """
        if isinstance(obj, MappingProxyType) or not FreezeThaw._is_container(obj):
            return obj

        stack: deque[object] = deque([obj])
        cache: dict[int, object] = {}

        # Traverse and copy containers, preserving references
        while stack:
            current = stack.pop()
            obj_id = id(current)
            if obj_id in cache:
                continue

            if isinstance(current, dict):
                new_dict: dict[Any, Any] = {}
                cache[obj_id] = new_dict
                for k, v in current.items():
                    # Add containers to stack for recursive freezing
                    if FreezeThaw._is_container(v) and id(v) not in cache:
                        stack.append(v)
                    new_dict[k] = v

            elif isinstance(current, (list, tuple)):
                new_tuple: list[Any] = [None] * len(current)
                cache[obj_id] = new_tuple
                for i, v in enumerate(current):
                    # Add containers to stack for recursive freezing
                    if FreezeThaw._is_container(v) and id(v) not in cache:
                        stack.append(v)
                    new_tuple[i] = v

        # Replace references with frozen objects
        cache_items = list(cache.items())
        for obj_id, val in cache_items:
            if isinstance(val, dict):
                for k, v in val.items():
                    if id(v) in cache:
                        val[k] = cache[id(v)]
                cache[obj_id] = MappingProxyType(val)
            elif isinstance(val, list):
                for i, v in enumerate(val):
                    if id(v) in cache:
                        val[i] = cache[id(v)]
                cache[obj_id] = tuple(val)

        return cache.get(id(obj), obj)
