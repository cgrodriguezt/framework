import re
from collections.abc import Callable
from orionis.http.bases.middleware import BaseMiddleware
from orionis.http.contracts.route import IRoute
from orionis.http.default.resources import DefaultResources
from orionis.http.enums.route_types import RouteTypes
from orionis.http.routes.fluent import FluentRoute
from orionis.http.routes.params_types import PARAM_TYPES
from orionis.http.routes.router import Router

class Route(IRoute):

    def __init__(self) -> None:
        """
        Initialize the Route singleton instance.

        Initializes the internal dictionaries for group routers, single routers,
        and routes.

        Returns
        -------
        None
            This method initializes the routers and routes attributes.
        """
        # Initialize the dictionaries for group routers, single routers, and routes
        self.__group_routers: dict[str, Router] = {}
        self.__single_routers: dict[str, FluentRoute] = {}
        self.__routes: dict = {}

    def __addsingleRoute(
        self, method: str, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        """
        Add a single route for a specific HTTP method and path.

        Parameters
        ----------
        method : str
            The HTTP method for the route (e.g., 'get', 'post').
        path : str
            The path for the route.
        action : Callable | list | None, optional
            The handler function or list of handlers for the route.

        Returns
        -------
        FluentRoute
            The created FluentRoute instance for the single route.
        """
        # Create a FluentRoute and store it in the single routers dictionary
        fluent_router = FluentRoute(method, path, action)
        self.__single_routers[fluent_router.id] = fluent_router
        return self.__single_routers[fluent_router.id]

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
        return self.__addsingleRoute("post", path, action)

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
        return self.__addsingleRoute("get", path, action)

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
        return self.__addsingleRoute("put", path, action)

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
        return self.__addsingleRoute("delete", path, action)

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
        return self.__addsingleRoute("patch", path, action)

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
        return self.__addsingleRoute("head", path, action)

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
        return self.__addsingleRoute("options", path, action)

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
        return self.__addsingleRoute("trace", path, action)

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
        return self.__addsingleRoute("copy", path, action)

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
        return self.__addsingleRoute("link", path, action)

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
        return self.__addsingleRoute("unlink", path, action)

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
        return self.__addsingleRoute("purge", path, action)

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
        return self.__addsingleRoute("lock", path, action)

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
        return self.__addsingleRoute("unlock", path, action)

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
        return self.__addsingleRoute("propfind", path, action)

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
        return self.__addsingleRoute("view", path, action)

    def fallback(
        self, action: Callable | list | None = None,
    ) -> None:
        """
        Register a fallback action for unmatched routes.

        Parameters
        ----------
        action : Callable | list | None
            Handler function or list of handlers for the fallback route.

        Returns
        -------
        None
            This method sets the fallback action for the route instance.
        """
        # Register a fallback route for unmatched requests.
        fluent_router = FluentRoute("ANY", "/", action)
        self.__single_routers[fluent_router.id] = fluent_router
        self.__single_routers[fluent_router.id]

    def __addGroupRoute(
        self,
        *,
        prefix: str | None = None,
        middleware: (
            list[type[BaseMiddleware]]
            | type[BaseMiddleware]
            | None
        ) = None,
        without_middleware: (
            list[type[BaseMiddleware]]
            | type[BaseMiddleware]
            | None
        ) = None,
        routes: list[FluentRoute] | None = None,
    ) -> FluentRoute:
        """
        Add a group route with optional prefix and middleware.

        Parameters
        ----------
        prefix : str, optional
            The prefix to apply to the group of routes.
        middleware : list[type[BaseMiddleware]] or type[BaseMiddleware], optional
            Middleware to apply to the group.
        without_middleware: list[type[BaseMiddleware]] or type[BaseMiddleware], optional
            Middleware to exclude from the group.
        routes : list[FluentRoute], optional
            List of routes to include in the group.

        Returns
        -------
        FluentRoute
            The created group router instance.
        """
        router = Router()
        if prefix:
            router.prefix(prefix)
        if middleware:
            router.middleware(middleware)
        if without_middleware:
            router.withOutMiddleware(without_middleware)
        if routes:
            router.group(*routes)
        # Store the group router by its unique ID
        self.__group_routers[router.id] = router
        return self.__group_routers[router.id]

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
        return self.__addGroupRoute(routes=list(routes))

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
        return self.__addGroupRoute(middleware=middleware)

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
        return self.__addGroupRoute(without_middleware=middleware)

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
        return self.__addGroupRoute(prefix=prefix)

    def loadRoutes(self, prefix: str = "") -> None:
        """
        Load routes from registered routers into the internal routes dictionary.

        Parameters
        ----------
        prefix : str, optional
            Prefix to prepend to each route path.

        Returns
        -------
        None
            Updates the internal __routes attribute in place.

        Notes
        -----
        Clears previous routes and loads new ones from group and single routers.
        """
        # Clear the routes dictionary before loading new routes
        self.__routes.clear()

        # Process group routers and their routes
        for router in self.__group_routers.values():
            # Build the route data structure for each route in the group
            for route in router.data:
                self.__buildRouteData(route, prefix)
                # Remove single route if already included in a group
                if route["id"] in self.__single_routers:
                    del self.__single_routers[route["id"]]

        # Process remaining individual routes
        for route in self.__single_routers.values():
            self.__buildRouteData(route.data, prefix)

        # Clear the group routers after loading their routes
        self.__group_routers.clear()

        # Clear the single routers after loading their routes
        self.__single_routers.clear()

    def __buildRouteData(self, route: dict, prefix: str) -> None:
        """
        Build and store route data in the internal routes dictionary.

        Parameters
        ----------
        route : dict
            Route dictionary to be processed and added.
        prefix : str
            Prefix to prepend to the route path.

        Returns
        -------
        None
            Updates the internal __routes attribute in place.
        """
        # Construct the full path with prefix, avoiding double slashes
        path: str = (
            f"{prefix}/{route['path']}".replace("//", "/") if prefix else route["path"]
        )
        method: str = route["method"].upper()

        # Prepare the base route data structure
        route_data = {
            "id": route.get("id"),
            "kind": prefix.replace("/", "").upper() if prefix else None,
            "method": method,
            "path": path,
        }

        controller = route.get("controller")
        handler = route.get("handler")
        callable_handler = route.get("callable_handler")

        # Determine the route type and action details
        if controller and handler:
            route_data.update({
                "type": RouteTypes.CONTROLLER_METHOD.value,
                "action": {
                    "class": controller.__name__,
                    "module": controller.__module__,
                    "method": handler,
                },
            })
        elif controller and not handler:
            route_data.update({
                "type": RouteTypes.CONTROLLER_CALL.value,
                "action": {
                    "class": controller.__name__,
                    "module": controller.__module__,
                    "method": "__call__",
                },
            })
        elif callable_handler:
            route_data.update({
                "type": RouteTypes.FUNCTION.value,
                "action": {
                    "callable": callable_handler.__name__,
                    "module": callable_handler.__module__,
                },
            })

        # Collect middleware information for caching
        middleware = route.get("middleware", [])
        cachable_middleware = []
        for middleware_class in middleware:
            cachable_middleware.append({
                "class": middleware_class.__name__,
                "module": middleware_class.__module__,
                "method": "handle",
            })
        route_data["middleware"] = cachable_middleware

        # Collect excluded middleware information for caching
        without_middleware = route.get("without_middleware", [])
        cachable_without_middleware = []
        for middleware_class in without_middleware:
            cachable_without_middleware.append({
                "class": middleware_class.__name__,
                "module": middleware_class.__module__,
                "method": "handle",
            })

        # Compile the route path to regex and extract converters
        regex, converters = self.__compileRoute(path)
        route_data["regex"] = regex.pattern
        route_data["converters"] = {
            name: converter.__name__ for name, converter in converters.items()
        }

        # Ensure the method and path exist in the routes dictionary
        if method not in self.__routes:
            self.__routes[method] = {}
        if path not in self.__routes[method]:
            self.__routes[method][path] = {}

        # Store the route data
        self.__routes[method][path] = route_data

    def getRoutes(self, prefix: str = "") -> dict:
        """
        Retrieve all registered routes.

        Parameters
        ----------
        prefix : str, optional
            Prefix to apply when loading routes.

        Returns
        -------
        dict
            Dictionary containing all loaded routes, organized by method and path.
        """
        # Load routes if not already loaded
        if not self.__routes:
            self.loadRoutes(prefix)
        return self.__routes

    def __compileRoute(self, path: str) -> tuple[re.Pattern, dict[str, Callable]]:
        """
        Compile a route path with placeholders into a regex and converters.

        Parameters
        ----------
        path : str
            The route path containing placeholders, e.g., '/user/{id:int}'.

        Returns
        -------
        tuple[re.Pattern, dict[str, Callable]]
            A tuple containing the compiled regex pattern and a dictionary
            mapping parameter names to their converter functions.

        Raises
        ------
        ValueError
            If an unknown parameter type is encountered in the path.
        """
        param_types = PARAM_TYPES
        converters: dict[str, Callable] = {}

        # Replace placeholders with regex named groups and collect converters
        pattern = path
        for match in re.finditer(r"\{(\w+)(?::(\w+))?\}", path):
            name, type_name = match.groups()
            if type_name is None:
                type_name = "str"
            if type_name not in param_types:
                error_msg = f"Unknown type: {type_name}"
                raise ValueError(error_msg)
            type_info = param_types[type_name]
            pattern = pattern.replace(
                match.group(0),
                f"(?P<{name}>{type_info['pattern']})",
            )
            converters[name] = type_info["converter"]

        # Compile the final regex pattern for the route
        regex = re.compile(f"^{pattern}$")
        return regex, converters

    def clearRoutes(self) -> None:
        """
        Clear all registered routes from internal storage.

        Returns
        -------
        None
            This method clears the internal __routes attribute in place.
        """
        # Remove all routes from the internal dictionary.
        self.__routes.clear()
