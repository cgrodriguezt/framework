from abc import ABC, abstractmethod
from collections.abc import Callable
from orionis.http.bases.middleware import BaseMiddleware
from orionis.http.routes.fluent import FluentRoute
from orionis.http.routes.router import Router

class IRoute(ABC):

    @abstractmethod
    def post(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a POST route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the POST route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the POST route.
        """

    @abstractmethod
    def get(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a GET route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the GET route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the GET route.
        """

    @abstractmethod
    def put(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a PUT route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the PUT route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the PUT route.
        """

    @abstractmethod
    def delete(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a DELETE route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the DELETE route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the DELETE route.
        """

    @abstractmethod
    def patch(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a PATCH route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the PATCH route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the PATCH route.
        """

    @abstractmethod
    def head(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a HEAD route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the HEAD route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the HEAD route.
        """

    @abstractmethod
    def options(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register an OPTIONS route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the OPTIONS route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the OPTIONS route.
        """

    @abstractmethod
    def trace(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a TRACE route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the TRACE route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the TRACE route.
        """

    @abstractmethod
    def copy(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a COPY route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the COPY route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the COPY route.
        """

    @abstractmethod
    def link(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a LINK route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the LINK route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the LINK route.
        """

    @abstractmethod
    def unlink(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register an UNLINK route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the UNLINK route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the UNLINK route.
        """

    @abstractmethod
    def purge(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a PURGE route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the PURGE route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the PURGE route.
        """

    @abstractmethod
    def lock(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a LOCK route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the LOCK route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the LOCK route.
        """

    @abstractmethod
    def unlock(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register an UNLOCK route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the UNLOCK route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the UNLOCK route.
        """

    @abstractmethod
    def propfind(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a PROPFIND route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the PROPFIND route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the PROPFIND route.
        """

    @abstractmethod
    def view(
        self, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Register a VIEW route for the given path and action.

        Parameters
        ----------
        path : str
            The path for the VIEW route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the VIEW route.
        """

    @abstractmethod
    def group(self, *routes: FluentRoute) -> Router:
        """
        Create a group of routes.

        Parameters
        ----------
        *routes : FluentRoute
            Variable number of FluentRoute instances to group.

        Returns
        -------
        Router
            The created Router instance containing the group.
        """

    @abstractmethod
    def middleware(
        self,
        middleware: list[type[BaseMiddleware]] | type[BaseMiddleware],
    ) -> Router:
        """
        Apply middleware to a group of routes.

        Parameters
        ----------
        middleware : list[type[BaseMiddleware]] or type[BaseMiddleware]
            Middleware to apply to the group.

        Returns
        -------
        Router
            The Router instance with applied middleware.
        """

    @abstractmethod
    def withOutMiddleware(
        self,
        middleware: type[BaseMiddleware],
    ) -> Router:
        """
        Exclude middleware from a group of routes.

        Parameters
        ----------
        middleware : type[BaseMiddleware]
            Middleware to exclude from the group.

        Returns
        -------
        Router
            The Router instance with excluded middleware.
        """

    @abstractmethod
    def prefix(self, prefix: str) -> Router:
        """
        Set a prefix for a group of routes.

        Parameters
        ----------
        prefix : str
            The prefix to apply to the group.

        Returns
        -------
        Router
            The Router instance with the set prefix.
        """

    @abstractmethod
    def fallback(
        self, action: Callable | list | None = None,
    ) -> None:
        """
        Register a fallback action for unmatched routes.

        Parameters
        ----------
        action : Callable | list | None
            The handler function or list of handlers for the fallback route.

        Returns
        -------
        None
            This method sets the fallback action for the route instance.
        """