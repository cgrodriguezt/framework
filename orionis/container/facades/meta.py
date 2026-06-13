from __future__ import annotations
import inspect

# Cache for dispatcher functions to avoid recreating them on every access.
_dispatcher_cache: dict[tuple[type, str], object] = {}

class FacadeMeta(type):

    def __getattr__(cls, name: str) -> object:
        """
        Return a proxy for a facade attribute.

        Parameters
        ----------
        name : str
            Specify the requested attribute name.

        Returns
        -------
        object
            Return the pinned attribute when an instance is pinned;
            otherwise return an async dispatcher that resolves the service
            and returns an attribute value or call result.
        """
        # Use pinned instances for direct, zero-resolution access.
        if cls._pinned_instance is not None:
            return getattr(cls._pinned_instance, name)

        # Return a cached dispatcher when one already exists for this (class, attr).
        # This avoids creating a new function object and closure on every access.
        cache_key = (cls, name)
        cached = _dispatcher_cache.get(cache_key)
        if cached is not None:
            return cached

        # Build the dispatcher once and store it for subsequent calls.
        async def dispatcher(*args: object, **kwargs: object) -> object:
            """
            Resolve the service and dispatch the requested attribute.

            Parameters
            ----------
            *args : object
                Pass positional arguments to the target callable.
            **kwargs : object
                Pass keyword arguments to the target callable.

            Returns
            -------
            object
                Return the awaited value for async results, the direct
                value for sync results, or the raw attribute value.
            """
            # Resolve the backing service from the container.
            service = await cls.resolve()

            # Retrieve the target attribute from the resolved service.
            attr = getattr(service, name)

            # Invoke callables and transparently await async results.
            if callable(attr):
                result = attr(*args, **kwargs)
                if inspect.isawaitable(result):
                    return await result
                return result

            # Return plain attributes without additional processing.
            return attr

        # Cache the dispatcher for future accesses to avoid recreating it.
        _dispatcher_cache[cache_key] = dispatcher

        # Return the newly created dispatcher for this attribute access.
        return dispatcher
