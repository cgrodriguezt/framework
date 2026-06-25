from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from orionis.http.middleware import BaseMiddleware
    from orionis.http.routes.fluent import FluentRoute


class IRouter(ABC):

    @abstractmethod
    def post(
        self,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute:
        """
        Register a POST route.

        Parameters
        ----------
        path : str
            URL path for the route.
        action : Callable | list | type | None, optional
            Callable, invokable controller class (defining ``__call__``),
            or ``[ControllerClass, 'method_name']`` list.

        Returns
        -------
        FluentRoute
            The registered FluentRoute instance.
        """

    @abstractmethod
    def query(
        self,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute:
        """
        Register a QUERY route.

        Parameters
        ----------
        path : str
            URL path for the route.
        action : Callable | list | type | None, optional
            Callable, invokable controller class (defining ``__call__``),
            or ``[ControllerClass, 'method_name']`` list.

        Returns
        -------
        FluentRoute
            The registered FluentRoute instance.
        """

    @abstractmethod
    def get(
        self,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute:
        """
        Register a GET route.

        Parameters
        ----------
        path : str
            URL path for the route.
        action : Callable | list | type | None, optional
            Callable, invokable controller class (defining ``__call__``),
            or ``[ControllerClass, 'method_name']`` list.

        Returns
        -------
        FluentRoute
            The registered FluentRoute instance.
        """

    @abstractmethod
    def put(
        self,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute:
        """
        Register a PUT route.

        Parameters
        ----------
        path : str
            URL path for the route.
        action : Callable | list | type | None, optional
            Callable, invokable controller class (defining ``__call__``),
            or ``[ControllerClass, 'method_name']`` list.

        Returns
        -------
        FluentRoute
            The registered FluentRoute instance.
        """

    @abstractmethod
    def delete(
        self,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute:
        """
        Register a DELETE route.

        Parameters
        ----------
        path : str
            URL path for the route.
        action : Callable | list | type | None, optional
            Callable, invokable controller class (defining ``__call__``),
            or ``[ControllerClass, 'method_name']`` list.

        Returns
        -------
        FluentRoute
            The registered FluentRoute instance.
        """

    @abstractmethod
    def patch(
        self,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute:
        """
        Register a PATCH route.

        Parameters
        ----------
        path : str
            URL path for the route.
        action : Callable | list | type | None, optional
            Callable, invokable controller class (defining ``__call__``),
            or ``[ControllerClass, 'method_name']`` list.

        Returns
        -------
        FluentRoute
            The registered FluentRoute instance.
        """

    @abstractmethod
    def fallback(
        self,
        action: Callable | list | type | None = None,
    ) -> None:
        """
        Register the fallback handler for unmatched routes (HTTP 404/405).

        Only one fallback may be registered; a second call raises
        ``FallbackRouteAlreadyRegisteredException``.

        Parameters
        ----------
        action : Callable | list | type | None, optional
            Callable, invokable controller class (defining ``__call__``),
            or ``[ControllerClass, 'method_name']`` list.

        Returns
        -------
        None
            The fallback is stored on the instance; no value is returned.

        Raises
        ------
        FallbackRouteAlreadyRegisteredException
            If a fallback handler has already been registered.
        """

    @abstractmethod
    def group(
        self,
        *,
        prefix: str | None = None,
        middleware: list[type[BaseMiddleware]] | None = None,
        routes: list[FluentRoute] | None = None,
    ) -> None:
        """
        Register a group of routes with a shared prefix and middleware.

        Parameters
        ----------
        prefix : str | None, optional
            URL prefix prepended to every route path in the group.
        middleware : list[type[BaseMiddleware]] | None, optional
            Middleware classes to attach to every route in the group.
        routes : list[FluentRoute] | None, optional
            FluentRoute instances to include in the group.

        Returns
        -------
        None
            Routes are mutated and registered; no value is returned.

        Raises
        ------
        ValueError
            If *routes* is empty or ``None``.
        ValueError
            If *prefix* is not a ``str``.
        ValueError
            If any entry in *middleware* is not a ``BaseMiddleware``
            subclass.
        TypeError
            If any entry in *routes* is not a ``FluentRoute`` instance.
        """

    @abstractmethod
    def export(self) -> dict:
        """
        Export all registered routes and the fallback handler.

        Returns
        -------
        dict
            A dictionary with two keys:

            - ``'routes'``: list of all registered routes as dicts.
            - ``'fallback'``: tuple
              ``(class_or_None, handler_or_callable)``.
        """
