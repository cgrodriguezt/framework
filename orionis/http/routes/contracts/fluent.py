from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from orionis.http.middleware import BaseMiddleware

class IFluentRoute(ABC):

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Return the unique identifier of the route.

        Returns
        -------
        str
            The unique identifier of the route.
        """

    @abstractmethod
    def action(self, controller: type, handler: str) -> Self:
        """
        Set the controller class and handler for the route.

        Parameters
        ----------
        controller : type
            Controller class to associate with the route.
        handler : str
            Name of the handler method.

        Returns
        -------
        Self
            This instance for method chaining.
        """

    @abstractmethod
    def name(self, name: str) -> Self:
        """
        Set the name for the route.

        Parameters
        ----------
        name : str
            Name to assign to the route.

        Returns
        -------
        Self
            This instance for method chaining.
        """

    @abstractmethod
    def middleware(self, *middleware: type[BaseMiddleware]) -> Self:
        """
        Add middleware to the route.

        Parameters
        ----------
        *middleware : type[BaseMiddleware]
            One or more middleware classes (not instances) to attach.

        Returns
        -------
        Self
            This instance for method chaining.
        """

    @abstractmethod
    def withOutMiddleware(self, *middleware: type[BaseMiddleware]) -> Self:
        """
        Exclude one or more middleware classes from the route.

        Parameters
        ----------
        *middleware : type[BaseMiddleware]
            One or more middleware classes to exclude from this route.

        Returns
        -------
        Self
            This instance for method chaining.
        """

    @abstractmethod
    def prefix(self, prefix: str) -> Self:
        """
        Prepend a path segment to the route's current path.

        Parameters
        ----------
        prefix : str
            The path prefix to prepend.

        Returns
        -------
        Self
            This instance for method chaining.
        """

    @abstractmethod
    def export(self) -> dict:
        """
        Export the route configuration as a plain dictionary.

        Returns
        -------
        dict
            Dictionary with keys: id, method, path, class, handler,
            callable_handler, name, middleware, and
            without_middleware.
        """
