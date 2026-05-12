import inspect
from typing import TYPE_CHECKING
from orionis.http.bases.middleware import BaseMiddleware
from orionis.http.default.responses import DefaultResponses
from orionis.http.routes.contracts.router import IRouter
from orionis.http.routes.fluent import FluentRoute
from orionis.http.routes.functions import normalize_path, parse_action

if TYPE_CHECKING:
    from collections.abc import Callable
class FallbackRouteAlreadyRegisteredException(Exception):
    """Raised when a second fallback route is registered."""

class Router(IRouter):

    _DEFAULT_PATHS = (
        "/favicon.ico",
        "/robots.txt",
        "/sitemap.xml",
    )

    def __init__(
        self,
    ) -> None:
        """
        Initialise the Router and register default system routes.

        Parameters
        ----------
        default_responses : DefaultResponses
            Handler that provides responses for favicon, robots.txt,
            and sitemap.xml.

        Returns
        -------
        None
            State is stored on the instance; no value is returned.
        """
        self.__fallback: tuple[Callable | None, Callable | None] = (
            None,
            None,
        )
        self.__routes: dict[str, dict] = {}
        self.__map_routes: dict[str, dict[str, str]] = {
            "GET": {},
            "POST": {},
            "PUT": {},
            "DELETE": {},
            "PATCH": {},
        }
        self.__defaultRoutes()

    def __defaultRoutes(self) -> None:
        """
        Register default routes for common static paths.

        Registers GET handlers for favicon, robots.txt, and sitemap.xml
        using the DefaultResponses class.

        Parameters
        ----------
        None

        Returns
        -------
        None
            Default routes are registered on the instance;
            no value is returned.
        """
        self.get("/favicon.ico", [DefaultResponses, "favicon"])
        self.get("/robots.txt", [DefaultResponses, "robotsTxt"])
        self.get("/sitemap.xml", [DefaultResponses, "sitemapXml"])

    def __addsingleRoute(
        self,
        method: str,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute:
        """
        Create and register a single HTTP route.

        Parameters
        ----------
        method : str
            HTTP method (e.g. ``'GET'``, ``'POST'``).
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
        # Normalise path before any duplicate check so that '/users' and
        # '/users/' are treated as the same route.
        normalized_path = normalize_path(path)
        method_upper = method.upper()

        # Validate duplicate routes
        previously_registered_id = (
            self.__map_routes.get(method_upper, {}).get(normalized_path)
        )
        if previously_registered_id:
            if normalized_path in self._DEFAULT_PATHS:
                del self.__routes[previously_registered_id]
                del self.__map_routes[method_upper][normalized_path]
            else:
                error_msg = (
                    f"Route already registered for "
                    f"{method_upper} {normalized_path}."
                )
                raise ValueError(error_msg)

        # Create and store the new route
        fluent_router = FluentRoute(method, path, action)
        self.__routes[fluent_router.id] = fluent_router
        self.__map_routes[method_upper][normalized_path] = fluent_router.id
        return self.__routes[fluent_router.id]

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
        return self.__addsingleRoute("POST", path, action)

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
        return self.__addsingleRoute("GET", path, action)

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
        return self.__addsingleRoute("PUT", path, action)

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
        return self.__addsingleRoute("DELETE", path, action)

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
        return self.__addsingleRoute("PATCH", path, action)

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
        if self.__fallback != (None, None):
            error_msg = (
                "Fallback route already registered. "
                "Only one fallback is allowed."
            )
            raise FallbackRouteAlreadyRegisteredException(error_msg)

        _callable, _handler = parse_action(action)
        if _callable and _handler is None:
            self.__fallback = (None, _callable)
        else:
            self.__fallback = (_callable, _handler)

    def __applyGroupToRoute(
        self,
        route: FluentRoute,
        prefix: str | None,
        middleware: list[type[BaseMiddleware]] | None,
    ) -> None:
        """
        Apply a group prefix and middleware to a single route in place.

        Parameters
        ----------
        route : FluentRoute
            The route to modify.
        prefix : str | None
            URL prefix to prepend to the route path.
        middleware : list[type[BaseMiddleware]] | None
            Middleware classes to add, skipping any already on the route.

        Returns
        -------
        None
            The route is mutated in place; no value is returned.
        """
        if prefix:
            route.prefix(prefix)

        if middleware:
            existing = set(route.export().get("middleware", []))
            new_middleware = [
                mw for mw in middleware if mw not in existing
            ]
            if new_middleware:
                route.middleware(*new_middleware)

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
        if not routes:
            error_msg = (
                "Group routes must be provided as a list of "
                "FluentRoute instances."
            )
            raise ValueError(error_msg)

        if prefix and not isinstance(prefix, str):
            error_msg = "Group prefix must be a string if provided."
            raise ValueError(error_msg)

        if middleware and not all(
            inspect.isclass(mw) and issubclass(mw, BaseMiddleware)
            for mw in middleware
        ):
            error_msg = (
                "Group middleware must be a list of "
                "BaseMiddleware subclasses if provided."
            )
            raise ValueError(error_msg)

        for route in routes:
            if not isinstance(route, FluentRoute):
                error_msg = (
                    "All group routes must be instances of FluentRoute."
                )
                raise TypeError(error_msg)

            self.__applyGroupToRoute(route, prefix, middleware)
            self.__routes[route.id] = route.export()

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
        routes = [
            r.export() if isinstance(r, FluentRoute) else r
            for r in self.__routes.values()
        ]
        return {
            "routes": routes,
            "fallback": self.__fallback,
        }
