import uuid
from typing import Self
from orionis.http.bases.middleware import BaseMiddleware
from orionis.http.routes.fluent import FluentRoute
from orionis.support.patterns.final.meta import Final

class Router(metaclass=Final):

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
    def data(self) -> list[dict]:
        """
        Return route data as a list of dictionaries.

        Returns
        -------
        list of dict
            Each dictionary contains route information, including id, method, path,
            controller, handler, callable_handler, prefix, middleware, and
            without_middleware.
        """
        data = []
        # Collect route data from all FluentRoute instances, updating with router info
        for router in self.__fluent_routes.values():
            route_data = router.data
            new_path: str = (
                f"{self.__prefix}/{route_data["path"]}"
                if self.__prefix else route_data["path"]
            )
            route_data.update({
                "path": new_path.replace("//", "/"),
                "middleware": self.__middleware,
                "without_middleware": self.__without_middleware,
            })
            data.append(route_data)
        return data

    def __init__(self) -> None:
        """
        Initialize a Router instance.

        Initializes internal attributes for routes, middleware, and prefix.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__id = str(uuid.uuid4())
        self.__fluent_routes: dict[str, FluentRoute] = {}
        self.__prefix: str = ""
        self.__middleware: list[type[BaseMiddleware]] = []
        self.__without_middleware: list[type[BaseMiddleware]] = []

    def group(self, *routes: FluentRoute) -> Self:
        """
        Group FluentRoute instances into the router.

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
            self.__fluent_routes[route.id] = route
        return self

    def middleware(
        self,
        middleware: list[type[BaseMiddleware]] | type[BaseMiddleware],
    ) -> Self:
        """
        Add middleware classes to the router.

        Parameters
        ----------
        middleware : type[BaseMiddleware] or list[type[BaseMiddleware]]
            Middleware class or list of middleware classes to add.

        Returns
        -------
        Self
            This Router instance for method chaining.
        """
        # Add middleware(s) to the router's middleware list
        if isinstance(middleware, list):
            for mw in middleware:
                if not isinstance(mw, type) or not issubclass(mw, BaseMiddleware):
                    error_msg = (
                        "Each middleware must be a concrete subclass of BaseMiddleware"
                    )
                    raise TypeError(error_msg)
                self.__middleware.append(mw)
        elif isinstance(middleware, type) and issubclass(middleware, BaseMiddleware):
            self.__middleware.append(middleware)
        else:
            error_msg = (
                "Middleware must be a concrete subclass of "
                "BaseMiddleware or a list of them"
            )
            raise TypeError(error_msg)
        return self

    def withOutMiddleware(
        self,
        middleware: list[type[BaseMiddleware]] | type[BaseMiddleware],
    ) -> Self:
        """
        Exclude middleware classes from the router.

        Parameters
        ----------
        middleware : type[BaseMiddleware] or list[type[BaseMiddleware]]
            Middleware class or list of middleware classes to exclude.

        Returns
        -------
        Self
            This Router instance for method chaining.
        """
        # Add middleware(s) to the exclusion list
        if isinstance(middleware, list):
            for mw in middleware:
                if not isinstance(mw, type) or not issubclass(mw, BaseMiddleware):
                    error_msg = (
                        "Each middleware must be a concrete subclass of BaseMiddleware"
                    )
                    raise TypeError(error_msg)
                self.__without_middleware.append(mw)
        elif isinstance(middleware, type) and issubclass(middleware, BaseMiddleware):
            self.__without_middleware.append(middleware)
        else:
            error_msg = (
                "Middleware must be a concrete subclass of "
                "BaseMiddleware or a list of them"
            )
            raise TypeError(error_msg)
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
        # Set the prefix for all routes
        if not isinstance(prefix, str):
            error_msg = "Prefix must be a string"
            raise TypeError(error_msg)
        self.__prefix = prefix.strip()
        return self
