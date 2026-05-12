from __future__ import annotations
from abc import ABC, abstractmethod

class IRouteLoader(ABC):

    @abstractmethod
    def load(self) -> dict[str, dict]:
        """
        Load, compile, and return all routes.

        Imports route files if not already done, compiles every
        registered route into a runtime-ready ``CompiledRoute``, and
        returns the internal routes dictionary organised by HTTP method
        with ``'static'`` and ``'dynamic'`` buckets.

        Returns
        -------
        dict[str, dict]
            Mapping of HTTP method to
            ``{'static': {path: CompiledRoute},
            'dynamic': [CompiledRoute, ...]}``.
        """

    @property
    @abstractmethod
    def fallback(self) -> tuple | None:
        """
        Return the registered fallback handler, if any.

        Returns
        -------
        tuple | None
            ``(class, method_name)`` for controller-based fallbacks,
            ``(None, callable)`` for callable-based fallbacks,
            or ``None`` if no fallback has been registered.
        """
