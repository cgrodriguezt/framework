import uuid
from typing import Self
from collections.abc import Callable
from orionis.http.bases.controller import BaseController
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.support.patterns.final.meta import Final

class FluentRoute(metaclass=Final):

    # ruff: noqa: PLR2004

    @property
    def id(self) -> str:
        """
        Get the unique identifier of the router.

        Returns
        -------
        str
            The unique identifier of the router.
        """
        return self.__id

    @property
    def data(self) -> dict:
        """
        Get the route data as a dictionary.

        Returns
        -------
        dict
            A dictionary containing route information such as id, method, path,
            controller, handler, and callable_handler.
        """
        return {
            "id": self.__id,
            "method": self.__method,
            "path": self.__path,
            "controller": self.__controller,
            "handler": self.__handler,
            "callable_handler": self.__callable_handler,
        }

    def __init__(
        self,
        method: str,
        path: str,
        action: Callable | list | None = None,
    ) -> None:
        """
        Initialize a FluentRoute instance.

        Parameters
        ----------
        method : str
            HTTP method (e.g., 'GET', 'POST').
        path : str
            Route path.
        action : Callable | list | None
            Action to execute, either a callable or a list [controller, method_name].

        Returns
        -------
        None
            The instance is initialized; no value is returned.
        """
        # Validate input types for method and path
        if not isinstance(method, str):
            error_msg = "HTTP method must be a string"
            raise TypeError(error_msg)
        if not isinstance(path, str):
            error_msg = "Path must be a string"
            raise TypeError(error_msg)

        # Initialize route attributes
        self.__id = str(uuid.uuid4())
        self.__method = method.upper()
        self.__path = path
        self.__controller: type[BaseController] | None = None
        self.__handler: str | None = None
        self.__callable_handler: Callable | None = None
        self.__name: str | None = None

        # Set action if provided
        if action is not None:
            self.__setAction(action)

    def __setAction(self, action: Callable | list) -> None:
        """
        Set the action for the route.

        Parameters
        ----------
        action : Callable | list
            Callable or a list [Controller, 'method_name'].

        Returns
        -------
        None
            The action is set; no value is returned.
        """
        # Handle callable action directly
        if callable(action):
            self.__callable_handler = action
        # Handle list action format [Controller, 'method_name']
        elif isinstance(action, list):
            # Validate list format and contents
            if len(action) != 2:
                error_msg = (
                    "Action list must have exactly two elements: "
                    "[Controller, 'method_name']"
                )
                raise ValueError(error_msg)
            controller, method_name = action
            # Validate controller and method name types
            if (
                not isinstance(controller, type)
                or not issubclass(controller, BaseController)
            ):
                error_msg = (
                    "First element of action list must be a concrete "
                    "subclass of BaseController"
                )
                raise TypeError(error_msg)
            if not isinstance(method_name, str):
                error_msg = "Second element of action list must be a string"
                raise TypeError(error_msg)
            if not ReflectionConcrete(controller).hasMethod(method_name):
                error_msg = (
                    f"Controller {controller} does not have method {method_name}"
                )
                raise ValueError(error_msg)
            # Set controller and handler
            self.__controller = controller
            self.__handler = method_name
        # Invalid action type
        else:
            error_msg = (
                "Action must be a callable or a list [Controller, 'method_name']"
            )
            raise TypeError(error_msg)

    def controller(self, controller: type[BaseController]) -> Self:
        """
        Set the controller class for the route.

        Parameters
        ----------
        controller : type[BaseController]
            Controller class to associate with the route.

        Returns
        -------
        Self
            Returns this FluentRoute instance for chaining.
        """
        # Validate controller type: must be a subclass of BaseController.
        if (
            not isinstance(controller, type)
            or not issubclass(controller, BaseController)
        ):
            error_msg = "Controller must be a concrete subclass of BaseController"
            raise TypeError(error_msg)
        self.__controller = controller
        return self

    def action(self, controller: type[BaseController], handler: str) -> Self:
        """
        Set the controller class and handler for the route.

        Parameters
        ----------
        controller : type[BaseController]
            Controller class to associate with the route.
        handler : str
            Name of the handler method.

        Returns
        -------
        Self
            Returns this FluentRoute instance for chaining.
        """
        # Validate controller class and handler method
        if (
            not isinstance(controller, type)
            or not issubclass(controller, BaseController)
        ):
            error_msg = "Controller must be a concrete subclass of BaseController"
            raise TypeError(error_msg)
        if not isinstance(handler, str):
            error_msg = "Handler must be a string"
            raise TypeError(error_msg)
        if not ReflectionConcrete(controller).hasMethod(handler):
            error_msg = f"Controller {controller} does not have method {handler}"
            raise ValueError(error_msg)
        self.__controller = controller
        self.__handler = handler
        return self

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
            Returns this FluentRoute instance for chaining.
        """
        # Validate route name type
        if not isinstance(name, str):
            error_msg = "Route name must be a string"
            raise TypeError(error_msg)
        self.__name = name.strip()
        return self
