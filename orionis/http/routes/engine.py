import importlib
import re
from pathlib import Path
from orionis.foundation.contracts.application import IApplication
from orionis.http.contracts.resources import IDefaultResources
from orionis.http.contracts.route import IRoute
from orionis.http.default.resources import DefaultResources
from orionis.http.routes.action_resolve import RouteAction
from orionis.http.routes.params_types import PARAM_TYPES
from orionis.services.cache.contracts.file_based_cache import IFileBasedCache
from orionis.services.cache.file_based_cache import FileBasedCache

class RoutingEngine:

    def __init__(
        self,
        app: IApplication,
        defaults: DefaultResources,
        router: IRoute,
        action_resolve: RouteAction,
    ) -> None:
        """
        Initialize RoutingEngine instance.

        Parameters
        ----------
        app : IApplication
            Application instance.
        defaults : DefaultResources
            Default resources handler.
        router : IRoute
            Router instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.__app: IApplication = app
        self.__cache: dict = {}
        self.__default_resources: IDefaultResources = defaults
        self.__action_resolve: RouteAction = action_resolve
        self.__defaults = {
            "/favicon.ico",
            "/robots.txt",
            "/sitemap.xml",
            self.__app.routeHealthCheck
        }
        self.__fallback: str | None = None
        self.__use_cache: bool = False
        self.__persistence: IFileBasedCache | None = self.__getCachePersistence()
        self.__regex_compiled_routes: dict = {}
        self.__router: IRoute = router
        self.__routes: dict = {}
        self.__routes_indexed: dict = {}

    def __getCachePersistence(self) -> IFileBasedCache | None:
        """
        Get the persistence mechanism for command caching.

        Returns
        -------
        FileBasedCache | None
            FileBasedCache instance for command caching, or None if no cache
            configuration is available.
        """
        # Extract cache configuration from application
        cache_config_app = self.__app.cacheConfiguration

        # Return None if no cache configuration is available
        if not cache_config_app:
            return None

        # Extract cache settings from configuration
        path = cache_config_app.get("folder")
        monitored_dirs = cache_config_app.get("monitored_dirs", [])
        monitored_files = cache_config_app.get("monitored_files", [])

        # Enable caching
        self.__use_cache = True

        # Create and return FileBasedCache instance
        return FileBasedCache(
            path=path,
            filename="routes",
            monitored_dirs=monitored_dirs,
            monitored_files=monitored_files,
        )

    def __importFluentRoutes(
        self,
        kind: str
    ) -> None:
        """
        Import API fluent route modules.

        Parameters
        ----------
        kind : str
            The type of routes to import (e.g., 'web', 'api').

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Imports API route files specified in application configuration to register
        fluent commands.
        """
        # Retrieve the routes file paths from application configuration
        routes_path: list[Path] | Path = self.__app.routingPaths(kind)

        # Return early if no routes path is configured
        if not routes_path:
            return

        routes_path = routes_path if isinstance(routes_path, list) else [routes_path]

        # Get the application root directory
        app_root: Path = self.__app.path("root")

        # Iterate through each route file path and import as module
        for route_file in routes_path:

            # Convert file path to relative path from application root
            relative_path = route_file.relative_to(app_root)

            # Convert relative path to module name format
            full_module_name = ".".join(relative_path.with_suffix("").parts)

            # Import the module to register fluent commands
            importlib.import_module(full_module_name)

    def __load(self) -> None:
        """
        Load routes from cache or by importing route files.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return a value.

        Notes
        -----
        Loads routes from cache if available, otherwise imports web and API routes
        and updates the internal routes dictionary. Saves routes to cache if enabled.
        """
        # Return early if routes are already loaded
        if self.__routes:
            return

        # Attempt to load routes from cache if enabled
        if self.__use_cache and self.__persistence:
            self.__routes = self.__persistence.get() or {}

        # If routes are not loaded, import web and API routes
        if not self.__routes:

            # Load web routes
            self.__router.clearRoutes()
            self.__importFluentRoutes("web")
            routes = self.__router.getRoutes()
            self.__mergeRoutes(routes)

            # Load API routes
            self.__router.clearRoutes()
            self.__importFluentRoutes("api")
            routes = self.__router.getRoutes(prefix="/api")
            self.__mergeRoutes(routes)

            # Save routes to cache if persistence is available
            if self.__use_cache and self.__persistence:
                self.__persistence.save(self.__routes)

    def __mergeRoutes(
        self,
        new_routes: dict,
        base: dict | None = None
    ) -> None:
        """
        Merge new_routes into the internal routes dictionary recursively.

        Parameters
        ----------
        new_routes : dict
            Dictionary containing new routes to merge.
        base : dict or None, optional
            Base dictionary to merge into. If None, uses self.__routes.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Use self.__routes as the base if none is provided
        if base is None:
            base = self.__routes

        # Recursively merge dictionaries
        for k, v in new_routes.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                self.__mergeRoutes(v, base[k])
            else:
                base[k] = v

    def __handleDefaultRoute(
        self,
        path: str,
        method: str,
        expects_json: bool,
    ) -> tuple[bool, object, dict]:
        """
        Handle default routes such as health check, favicon, robots.txt, and sitemap.xml.

        Parameters
        ----------
        path : str
            Requested URL path.
        method : str
            HTTP method used in the request.
        expects_json : bool
            Indicates if the client expects a JSON response.

        Returns
        -------
        tuple[bool, object, dict]
            Tuple indicating if the route is default, the response object,
            and an empty dictionary for parameters.
        """
        # Handle health check route
        if path == self.__app.routeHealthCheck:
            handle = (True, self.__default_resources.health(expects_json), {})

        # Handle favicon.ico request
        elif path == "/favicon.ico":
            handle = (True, self.__default_resources.favicon(), {})

        # Handle robots.txt request
        elif path == "/robots.txt":
            handle = (True, self.__default_resources.robotsTxt(), {})

        # Handle sitemap.xml request
        elif path == "/sitemap.xml":
            handle = (True, self.__default_resources.sitemapXml(), {})

        # Cache and return the response for the default route
        cache_key = f"{method}:{path}:{expects_json}"
        self.__cache[cache_key] = handle
        return handle

    def __handleHTTP405(
        self,
        path: str,
        method: str,
        expects_json: bool,
    ) -> tuple[bool, object, dict] | None:
        """
        Return a 405 Method Not Allowed response for unsupported HTTP methods.

        Parameters
        ----------
        path : str
            Requested URL path.
        method : str
            HTTP method used in the request.
        expects_json : bool
            Whether the client expects a JSON response.

        Returns
        -------
        tuple[bool, object, dict] or None
            Tuple indicating if the route is default, the response object,
            and an empty dictionary for parameters. Returns None if no allowed
            methods are found.
        """
        allowed_methods: list[str] = []

        # Collect allowed methods for the requested path, excluding the current method
        for m, routes in self.__regex_compiled_routes.items():
            if m == method:
                continue
            for regex, _ in routes:
                if regex.match(path):
                    allowed_methods.append(m)

        # Return error page for method not allowed, including allowed methods header
        if allowed_methods:
            allowed = sorted(set(allowed_methods))
            handle = self.__default_resources.errorPage(
                status_code=405,
                description="Method Not Allowed",
                expects_json=expects_json,
                headers={"Allow": ", ".join(allowed)},
            )
            cache_key = f"{method}:{path}:{expects_json}"
            self.__cache[cache_key] = (True, handle, {})
            return (True, handle, {})

    def __handleHTTP404(
        self,
        path: str,
        method: str,
        expects_json: bool,
    ) -> tuple[bool, object, dict]:
        """
        Return a 404 Not Found response for unmatched routes.

        Parameters
        ----------
        path : str
            The requested URL path.
        method : str
            The HTTP method used in the request.
        expects_json : bool
            Whether the client expects a JSON response.

        Returns
        -------
        tuple[bool, object, dict]
            Tuple indicating if this is a default route, the response object,
            and an empty dictionary for parameters.
        """
        # If a fallback route is defined, use it as the response
        if self.__fallback:
            route = self.__routes_indexed[self.__fallback]
            response = (False, route["handle"], {})
        else:
            # Otherwise, return a standard 404 error page
            handle = self.__default_resources.errorPage(
                status_code=404,
                description="Not Found",
                expects_json=expects_json,
            )
            response = (True, handle, {})
        # Cache and return the 404 response
        cache_key = f"{method}:{path}:{expects_json}"
        self.__cache[cache_key] = response
        return response

    def __handleOPTIONS(
        self,
        path: str,
        method: str,
        expects_json: bool,
    ) -> tuple[bool, object, dict] | None:
        """
        Handle HTTP OPTIONS requests for a given path.

        Parameters
        ----------
        path : str
            Requested URL path.
        method : str
            HTTP method used in the request.
        expects_json : bool
            Whether the client expects a JSON response.

        Returns
        -------
        tuple[bool, object, dict] or None
            Tuple indicating if the route is default, the response object,
            and an empty dictionary for parameters. Returns None if no allowed
            methods are found.
        """
        allowed_methods: list[str] = []

        # Collect all allowed HTTP methods for the requested path
        for m, routes in self.__regex_compiled_routes.items():
            for regex, _ in routes:
                if regex.match(path):
                    allowed_methods.append(m)

        if allowed_methods:
            allowed = sorted(set(allowed_methods))

            # Add implicit HEAD if GET exists and HEAD is not present
            if "GET" in allowed and "HEAD" not in allowed:
                allowed.append("HEAD")

            # Add implicit OPTIONS if not present
            if "OPTIONS" not in allowed:
                allowed.append("OPTIONS")

            handle = self.__default_resources.emptyResponse(
                headers={"Allow": ", ".join(sorted(allowed))},
            )
            cache_key = f"{method}:{path}:{expects_json}"
            self.__cache[cache_key] = (True, handle, {})
            return (True, handle, {})

    def __matchRoute(
        self,
        path: str,
        method: str,
        expects_json: bool,
        real_method: str | None = None,
    ) -> tuple[bool, object, dict] | None:
        """
        Match the request path and method against compiled regex routes.

        Parameters
        ----------
        path : str
            The requested URL path.
        method : str
            The HTTP method used in the request.
        expects_json : bool
            Whether the client expects a JSON response.
        real_method : str | None, optional
            The actual HTTP method if different (e.g., HEAD mapped to GET).

        Returns
        -------
        tuple[bool, object, dict] | None
            Returns a tuple containing a boolean for default route, the matched
            route object, and a parameters dictionary. Returns None if no match
            is found.
        """
        # Iterate through compiled regex routes for the specified method
        for regex, route_id in self.__regex_compiled_routes.get(method, []):
            # Attempt to match the request path against the regex pattern
            match = regex.match(path)
            if match:
                route = self.__routes_indexed[route_id]
                handle = route["handle"]
                params: dict = {}
                # Parse parameters using converters if available
                for name, value in match.groupdict().items():
                    if name in route["converters"]:
                        converter = route["converters"][name]["converter"]
                        params[name] = converter(value)
                    else:
                        params[name] = value
                # Cache the resolved route for future requests
                method_to_cache = real_method if real_method else method
                cache_key = f"{method_to_cache}:{path}:{expects_json}"
                self.__cache[cache_key] = (False, handle, params)
                # Return the resolved route and parameters
                return (False, handle, params)

    def discover(self) -> None:
        """
        Discover and load routes into internal structures.

        Resolves and loads routes from cache or by importing route files. Compiles
        regex patterns and updates internal dictionaries for indexed and compiled
        routes.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Load routes from cache or by importing route files
        self.__load()

        # Initialize dictionaries for compiled regex routes and indexed routes
        regex_compiled_routes: dict = {}
        routes_indexed: dict = {}

        # Iterate through loaded routes to compile regex and index routes
        for method, paths in self.__routes.items():

            # Handle fallback route by storing its ID for later retrieval
            if method == "ANY":

                # There is always only one fallback route
                route = next(iter(paths.values()))
                handle = self.__action_resolve.resolve(route["type"], route["action"])
                route["handle"] = handle
                routes_indexed[route["id"]] = route
                self.__fallback = route["id"]

                # Skip further processing for fallback routes
                continue

            # Ensure the method key exists in the compiled routes dictionary
            if method not in regex_compiled_routes:
                regex_compiled_routes[method] = []

            # Iterate through each route for the current method
            for _, route in paths.items():

                # Remove default routes from the set of routes to be resolved
                self.__defaults.discard(route["path"])

                # Compile the regex pattern for the route
                regex_pattern = re.compile(route["regex"])

                # Append the compiled regex pattern and route ID as a tuple
                regex_compiled_routes[method].append((regex_pattern, route["id"]))
                route["regex"] = regex_pattern

                # Replace converter names with actual converter functions
                for name, converter in route["converters"].items():
                    route["converters"][name] = PARAM_TYPES[converter]

                # Precompile the route handler using the action resolver
                handle = self.__action_resolve.resolve(route["type"], route["action"])

                # Add the precompiled handler to the route data
                route["handle"] = handle

                # Index routes by method and ID for quick lookup
                routes_indexed[route["id"]] = route

        # Update internal dictionaries with compiled regex and indexed routes
        self.__routes_indexed = routes_indexed
        self.__regex_compiled_routes = regex_compiled_routes

    def resolve(
        self,
        path: str,
        method: str,
        expects_json: bool,
    ) -> tuple[bool, object, dict]:
        """
        Resolve the route for a given HTTP request.

        Parameters
        ----------
        path : str
            Requested URL path.
        method : str
            HTTP method used in the request.
        expects_json : bool
            Whether the client expects a JSON response.

        Returns
        -------
        tuple[bool, object, dict]
            Tuple containing a boolean indicating if the route is default,
            the matched route or response object, and a dictionary of parameters.
        """
        # Normalize the HTTP method to uppercase for consistent matching
        method = method.upper()

        # Return cached route if available
        cache_key = f"{method}:{path}:{expects_json}"
        if cache_key in self.__cache:
            return self.__cache[cache_key]

        # Handle default routes (health check, favicon, etc.)
        if path in self.__defaults:
            return self.__handleDefaultRoute(path, method, expects_json)

        # Attempt to match the request path against compiled regex routes
        handle_route = self.__matchRoute(path, method, expects_json)
        if handle_route:
            return handle_route

        # Handle HEAD requests by matching GET route
        if method == "HEAD":
            handle_head = self.__matchRoute(
                path, "GET", expects_json, real_method="HEAD"
            )
            if handle_head:
                return handle_head

        # Handle OPTIONS requests by checking for allowed methods
        if method == "OPTIONS":
            handle_options = self.__handleOPTIONS(path, method, expects_json)
            if handle_options:
                return handle_options

        # Handle HTTP 405 Method Not Allowed
        handle_405 = self.__handleHTTP405(path, method, expects_json)
        if handle_405:
            return handle_405

        # Return 404 or fallback route if no match is found
        return self.__handleHTTP404(path, method, expects_json)