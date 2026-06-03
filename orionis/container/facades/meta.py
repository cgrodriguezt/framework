from __future__ import annotations
import inspect
from typing import Any, Awaitable, Callable

class FacadeMeta(type):

    def __getattr__(cls, name: str) -> Any:
        """
        Return a proxy for a facade attribute.

        Parameters
        ----------
        name : str
            Specify the requested attribute name.

        Returns
        -------
        Any
            Return the pinned attribute when an instance is pinned;
            otherwise return an async dispatcher that resolves the service
            and returns an attribute value or call result.
        """

        # Use pinned instances for direct, zero-resolution access.
        if cls._pinned_instance is not None:
            return getattr(cls._pinned_instance, name)

        # Lazily resolve the service for unpinned facade access.
        async def dispatcher(*args: Any, **kwargs: Any) -> Any:
            """
            Resolve the service and dispatch the requested attribute.

            Parameters
            ----------
            *args : Any
                Pass positional arguments to the target callable.
            **kwargs : Any
                Pass keyword arguments to the target callable.

            Returns
            -------
            Any
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

        # Return the async dispatcher for deferred service access.
        return dispatcher
