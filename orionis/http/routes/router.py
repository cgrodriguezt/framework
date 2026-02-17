from typing import Callable, Self
from orionis.http.bases.middleware import BaseMiddleware
from orionis.services.introspection.concretes.reflection import ReflectionConcrete

class Router:

    def __init__(self) -> None:
        """
        Initialize a Router instance.

        Returns
        -------
        None
            This method initializes the Router instance.
        """
        self.__routes: list[FluentRoute] = []
        self.__middleware: list[BaseMiddleware] = []
        self.__without_middleware: list[BaseMiddleware] = []
        self.__prefix: str = ""

    def addRoute(
        self,
        method: str,
        path: str,
        action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Add a new route to the router.

        Parameters
        ----------
        method : str
            HTTP method for the route.
        path : str
            Path for the route.
        action : Callable | list | None, optional
            Action to execute for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance.
        """
        route = FluentRoute(method, path, action)
        self.__routes.append(route)
        return route

    def group(self, *routes: FluentRoute) -> Self:
        """
        Group multiple FluentRoute instances together.

        Parameters
        ----------
        *routes : FluentRoute
            Variable number of FluentRoute instances to group.

        Returns
        -------
        Self
            This Router instance for method chaining.
        """
        # Add each provided FluentRoute to the router's route list
        for route in routes:
            if not isinstance(route, FluentRoute):
                error_msg = "All arguments must be instances of FluentRoute"
                raise TypeError(error_msg)
            self.__routes.append(route)
        return self

    def middleware(self, middleware: BaseMiddleware) -> Self:
        """
        Add middleware to the router.

        Parameters
        ----------
        middleware : IMiddleware
            Middleware instance to add.

        Returns
        -------
        Self
            This Router instance for method chaining.
        """
        if not isinstance(middleware, BaseMiddleware):
            error_msg = "Middleware must be an instance of IMiddleware"
            raise TypeError(error_msg)
        # Add middleware to the list of middlewares for this router
        self.__middleware.append(middleware)
        return self

    def withOutMiddleware(self, middleware: IMiddleware) -> Self:
        """
        Exclude middleware from the router.

        Parameters
        ----------
        middleware : IMiddleware
            Middleware instance to exclude.

        Returns
        -------
        Self
            This Router instance for method chaining.
        """
        if not isinstance(middleware, IMiddleware):
            error_msg = "Middleware must be an instance of IMiddleware"
            raise TypeError(error_msg)
        # Add middleware to the list of excluded middlewares for this router
        self.__without_middleware.append(middleware)
        return self

    def prefix(self, prefix: str) -> Self:
        """
        Set a prefix for all routes in the router.

        Parameters
        ----------
        prefix : str
            Prefix to set for the router.

        Returns
        -------
        Self
            This Router instance for method chaining.
        """
        if not isinstance(prefix, str):
            error_msg = "Prefix must be a string"
            raise TypeError(error_msg)
        self.__prefix = prefix
        return self

    def _loadRoutes(self) -> list[tuple[str, str, dict]]:
        """
        Load all routes defined in this router.

        Returns
        -------
        list of tuple
            A list of tuples, each containing the route path, HTTP method,
            and a dictionary with controller, handler, callable handler,
            middleware, excluded middleware, and alias.
        """
        data: list[tuple[str, str, dict]] = []
        # Iterate through all routes and build the route data
        for route in self.__routes:
            path = (self.__prefix + "/" + route.path).replace("//", "/")
            data.append(
                (
                    path,
                    route.method,
                    {
                        "controller": route.controller_class,
                        "handler": route.handler,
                        "callable_handler": route.callable_handler,
                        "middleware": self.__middleware,
                        "without_middleware": self.__without_middleware,
                        "alias": route.alias,
                    },
                )
            )
        return data

class FluentRoute:

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
            The route path.
        action : Callable | list | None, optional
            The action to be executed, either a callable or a list
            [controller, method_name].

        Returns
        -------
        None
            This method initializes the instance and returns None.
        """
        # Validate input types
        if not isinstance(method, str):
            error_msg = "HTTP method must be a string"
            raise TypeError(error_msg)
        if not isinstance(path, str):
            error_msg = "Path must be a string"
            raise TypeError(error_msg)

        # Store the method and path, and initialize other attributes
        self.__method = method.upper()
        self.__path = path
        self.__controller: IController | None = None
        self.__handler: str | None = None
        self.__callable_handler: Callable | None = None
        self.__name: str | None = None

        # Set the action if provided
        if action is not None:
            self.__setAction(action)

    def __setAction(self, action: Callable | list) -> None:
        """
        Set the action for the route.

        Parameters
        ----------
        action : Callable | list
            The action to be executed, either a callable or a list
            [controller, method_name].

        Returns
        -------
        None
            This method sets the action and returns None.
        """
        if callable(action):
            self.__callable_handler = action
        elif isinstance(action, list):
            if len(action) != 2:
                error_msg = (
                    "Action list must have exactly two elements: "
                    "[Controller, 'method_name']"
                )
                raise ValueError(error_msg)
            controller, method_name = action
            if not isinstance(controller, type) or not issubclass(controller, IController):
                error_msg = (
                    "First element of action list must be an instance of IController"
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
            self.__controller = controller
            self.__handler = method_name
        else:
            error_msg = (
                "Action must be a callable or a list [Controller, 'method_name']"
            )
            raise TypeError(error_msg)

    def controller(self, controller: IController) -> Self:
        """
        Set the controller for the route.

        Parameters
        ----------
        controller : IController
            Controller instance to associate with the route.

        Returns
        -------
        Self
            Returns this FluentRoute instance for chaining.
        """
        if not isinstance(controller, IController):
            error_msg = "Controller must be an instance of IController"
            raise TypeError(error_msg)
        self.__controller = controller
        return self

    def action(self, controller: IController, handler: str) -> Self:
        """
        Set the controller and handler for the route.

        Parameters
        ----------
        controller : IController
            Controller instance to associate with the route.
        handler : str
            Name of the handler method.

        Returns
        -------
        Self
            Returns this FluentRoute instance for chaining.
        """
        if not isinstance(controller, type) or not issubclass(controller, IController):
            error_msg = "Controller must be a concrete subclass of IController"
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
            The name to assign to the route.

        Returns
        -------
        Self
            Returns this FluentRoute instance for chaining.
        """
        if not isinstance(name, str):
            error_msg = "Route name must be a string"
            raise TypeError(error_msg)
        self.__name = name
        return self

    @property
    def method(self) -> str:
        """
        Get the HTTP method for the route.

        Returns
        -------
        str
            The HTTP method as an uppercase string.
        """
        return self.__method

    @property
    def path(self) -> str:
        """
        Get the path for the route.

        Returns
        -------
        str
            The route path.
        """
        return self.__path

    @property
    def controller_class(self) -> IController | None:
        """
        Get the controller associated with the route.

        Returns
        -------
        IController | None
            The controller instance or None if not set.
        """
        return self.__controller

    @property
    def handler(self) -> str | None:
        """
        Get the handler method name for the route.

        Returns
        -------
        str | None
            The handler method name or None if not set.
        """
        return self.__handler

    @property
    def callable_handler(self) -> Callable | None:
        """
        Get the callable handler for the route.

        Returns
        -------
        Callable | None
            The callable handler or None if not set.
        """
        return self.__callable_handler

    @property
    def alias(self) -> str | None:
        """
        Get the name of the route.

        Returns
        -------
        str | None
            The name of the route or None if not set.
        """
        return self.__name
