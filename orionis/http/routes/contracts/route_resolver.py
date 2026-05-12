from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.http.routes.contracts.resolved_route import ResolvedRoute

class IRouteResolver(ABC):

    @abstractmethod
    def resolve(
        self,
        method: str,
        path: str,
    ) -> ResolvedRoute:
        """
        Resolve an HTTP method and path to a compiled route.

        Parameters
        ----------
        method : str
            HTTP verb (case-insensitive, e.g. ``'GET'``, ``'post'``).
            ``HEAD`` is treated as ``GET``; raises ``MethodNotAllowed``
            when no matching ``GET`` route exists.
        path : str
            Raw request path; normalised internally (leading slash
            enforced, trailing slash stripped).

        Returns
        -------
        ResolvedRoute
            Matched ``CompiledRoute`` together with a ``dict`` of path
            parameters converted to their declared types (empty dict
            for static routes).

        Raises
        ------
        RouteNotFound
            If ``path`` does not match any registered route under any
            HTTP method.
        MethodNotAllowed
            If ``path`` matches a route registered under a different
            HTTP method, or if the method is ``HEAD`` and no ``GET``
            route exists.
        """

    @abstractmethod
    def options(self, path: str) -> list[str]:
        """
        Return all HTTP methods registered for the given path.

        Parameters
        ----------
        path : str
            Raw request URL path; normalised internally.

        Returns
        -------
        list[str]
            Sorted list of uppercase HTTP method strings that have a
            route matching *path*.  Empty when the path is not
            registered under any method.
        """

    @abstractmethod
    def fallback(self) -> tuple | None:
        """
        Return the registered fallback handler, if any.

        Returns
        -------
        tuple | None
            ``(None, callable)`` for function-based fallbacks,
            ``(class, method_name)`` for controller-based fallbacks,
            or ``None`` when no fallback has been registered.
        """
