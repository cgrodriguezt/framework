from __future__ import annotations
import inspect
import re
from typing import TYPE_CHECKING
from orionis.http.routes.enums.route_types import RouteType
from orionis.http.routes.compiled_route import CompiledRoute
from orionis.http.routes.contracts.route_compiler import IRouteCompiler
from orionis.http.routes.params_types import PARAM_TYPES

if TYPE_CHECKING:
    from collections.abc import Callable

class RouteCompiler(IRouteCompiler):
    """
    Compile raw route dictionaries into runtime-ready ``CompiledRoute`` objects.

    This class owns all logic that transforms the plain dicts exported by
    ``Router.export()`` into the structures used by the dispatcher:

    - Action type resolution (function / invokable / controller)
    - Path regex compilation and parameter converter building
    - Priority scoring
    - Collision detection for dynamic routes

    The only public surface is :meth:`compile` (batch) and
    :meth:`compilePath` (single path, also used by :class:`RouteCache`
    during cache deserialisation).
    """

    def compile(
        self,
        routes: list[dict],
        fallback: tuple | None,
    ) -> tuple[dict[str, dict], tuple | None]:
        """
        Compile a list of raw route dicts into a ready-to-dispatch structure.

        Parameters
        ----------
        routes : list[dict]
            Raw route dicts as returned by ``Router.export()["routes"]``.
        fallback : tuple | None
            Raw fallback tuple from ``Router.export()["fallback"]``.

        Returns
        -------
        tuple[dict[str, dict], tuple | None]
            A pair ``(compiled_routes, fallback)`` where
            ``compiled_routes`` maps each HTTP method to
            ``{"static": {path: CompiledRoute},
            "dynamic": [CompiledRoute, ...]}``. Dynamic lists are
            sorted descending by ``priority_score`` so more-specific
            patterns are matched first.

        Raises
        ------
        ValueError
            If two dynamic routes produce the same structural URL
            pattern (collision).
        TypeError
            If an invokable class does not define ``__call__``.
        """
        compiled_routes: dict[str, dict] = {}
        seen_signatures: dict[str, str] = {}

        for route in routes:
            method = route["method"]
            is_static, compiled = self.__compileRoute(route)

            if method not in compiled_routes:
                compiled_routes[method] = {"static": {}, "dynamic": []}

            if is_static:
                compiled_routes[method]["static"][route["path"]] = compiled
            else:
                # Collision detection: two dynamic routes whose regex patterns
                # are structurally identical would match identical URLs,
                # making one unreachable.
                signature = self.__routeSignature(method, compiled.regex)
                if signature in seen_signatures:
                    error_msg = (
                        f"Route conflict detected for {method} "
                        f"'{route['path']}':\n"
                        f"  '{route['path']}' and "
                        f"'{seen_signatures[signature]}' produce the same "
                        "URL pattern and would collide at dispatch.\n"
                        f"  Signature: {signature}"
                    )
                    raise ValueError(error_msg)
                seen_signatures[signature] = route["path"]
                compiled_routes[method]["dynamic"].append(compiled)

        # Sort each method's dynamic routes by specificity (descending).
        # More static segments → higher score → matched first.
        for bucket in compiled_routes.values():
            bucket["dynamic"].sort(
                key=lambda r: r.priority_score,
                reverse=True,
            )

        return compiled_routes, fallback

    @staticmethod
    def compilePath(
        path: str,
    ) -> tuple[bool, re.Pattern | None, dict[str, Callable]]:
        """
        Determine whether a path is static or dynamic and compile its regex.

        This method is intentionally public so that :class:`RouteCache`
        can call it during cache deserialisation to reconstruct ``regex``
        and ``converters`` without ever persisting callable objects.

        Parameters
        ----------
        path : str
            The route path, e.g. ``'/users/{id:int}'``.

        Returns
        -------
        tuple[bool, re.Pattern | None, dict[str, Callable]]
            ``(is_static, regex, converters)`` — ``regex`` and
            ``converters`` are ``None`` / empty for static paths.
        """
        if "{" not in path:
            return True, None, {}

        regex, converters = RouteCompiler.__buildPathRegex(path)
        return False, regex, converters

    # ── Private helpers ───────────────────────────────────────────────────────

    def __compileRoute(self, route: dict) -> tuple[bool, CompiledRoute]:
        """
        Compile a single raw route dict into a ``CompiledRoute``.

        Parameters
        ----------
        route : dict
            Raw route dictionary from the router export.

        Returns
        -------
        tuple[bool, CompiledRoute]
            ``(is_static, compiled_route)``.
        """
        route_type, action = self.__buildAction(route)
        is_static, regex, converters = self.compilePath(route["path"])

        compiled = CompiledRoute(
            path=route["path"],
            method=route["method"],
            type=route_type,
            action=action,
            name=route.get("name"),
            regex=regex,
            segment_count=sum(
                1 for s in route["path"].split("/") if s
            ),
            priority_score=self.__routeScore(route["path"]),
            kind=route.get("kind", "web"),
            converters=converters,
            middleware=route.get("middleware", []),
            without_middleware=set(route.get("without_middleware", [])),
        )
        return is_static, compiled

    @staticmethod
    def __buildAction(route: dict) -> tuple[RouteType, dict]:
        """
        Resolve the handler type and build the action descriptor for a route.

        Parameters
        ----------
        route : dict
            Raw route dictionary from the router export.

        Returns
        -------
        tuple[RouteType, dict]
            A tuple of the resolved ``RouteType`` and an action
            descriptor dict containing the information needed to
            dispatch the request.

        Raises
        ------
        TypeError
            If an invokable class does not define ``__call__``.
        """
        callable_handler = route.get("callable_handler")

        if callable_handler is not None:
            # A class is treated as invokable only when it explicitly defines
            # __call__.
            if inspect.isclass(callable_handler):
                if "__call__" not in callable_handler.__dict__:
                    error_msg = (
                        f"Class '{callable_handler.__name__}' cannot be "
                        "used as an invokable route handler because it "
                        "does not define __call__."
                    )
                    raise TypeError(error_msg)
                return RouteType.INVOKABLE, {
                    "class": callable_handler.__name__,
                    "module": callable_handler.__module__,
                    "method": "__call__",
                }
            # Any other callable (function, lambda, partial, ...)
            if callable(callable_handler):
                return RouteType.FUNCTION, {
                    "function": callable_handler.__name__,
                    "module": callable_handler.__module__,
                }

        # Controller-based route: [ControllerClass, 'method_name']
        _class = route.get("class")
        return RouteType.CONTROLLER, {
            "class": _class.__name__,
            "module": _class.__module__,
            "method": route.get("handler"),
        }

    @staticmethod
    def __buildPathRegex(
        path: str,
    ) -> tuple[re.Pattern, dict[str, Callable]]:
        """
        Compile a route path with placeholders into a regex and converters.

        Parameters
        ----------
        path : str
            Route path containing placeholders,
            e.g. ``'/user/{id:int}'``.

        Returns
        -------
        tuple[re.Pattern, dict[str, Callable]]
            Compiled regex pattern and a dict mapping parameter names
            to their converter callables.

        Raises
        ------
        ValueError
            If an unknown parameter type is encountered in the path.
        """
        param_types = PARAM_TYPES
        converters: dict[str, Callable] = {}
        parts: list[str] = []
        last_end = 0

        # Iterate over placeholders and build the regex incrementally.
        # Static segments are escaped so characters like '.' are literals.
        for match in re.finditer(r"\{(\w+)(?::(\w+))?\}", path):
            parts.append(re.escape(path[last_end : match.start()]))
            name, type_name = match.groups()
            if type_name is None:
                type_name = "str"
            if type_name not in param_types:
                error_msg = (
                    f"Unknown parameter type: '{type_name}' in path '{path}'"
                )
                raise ValueError(error_msg)
            type_info = param_types[type_name]
            parts.append(f"(?P<{name}>{type_info['pattern']})")
            converters[name] = type_info["converter"]
            last_end = match.end()

        # Escape any remaining static tail after the last placeholder.
        parts.append(re.escape(path[last_end:]))

        regex = re.compile(f"^{''.join(parts)}$")
        return regex, converters

    @staticmethod
    def __routeSignature(method: str, regex: re.Pattern) -> str:
        """
        Build a collision-detection key for a dynamic route.

        Two routes collide when they match the same set of URLs regardless
        of parameter names, e.g. ``/users/{id}`` and ``/users/{name}``
        both produce ``^/users/(?P<param>[^/]+)$``.

        The key normalises every named capture group to the fixed
        placeholder ``param`` and prefixes with the HTTP method::

            GET:^/users/(?P<param>[^/]+)$

        Parameters
        ----------
        method : str
            HTTP method in uppercase.
        regex : re.Pattern
            Compiled route regex.

        Returns
        -------
        str
            Normalised signature string.
        """
        normalised = re.sub(r"\(\?P<\w+>", "(?P<param>", regex.pattern)
        return f"{method}:{normalised}"

    @staticmethod
    def __routeScore(path: str) -> int:
        """
        Compute a specificity score for a dynamic route path.

        Higher scores are more specific and should be matched first.
        The formula weights static segments heavily so that
        ``/users/me`` (score 20) always beats ``/users/{id}``
        (score 9).

        Parameters
        ----------
        path : str
            The route path, e.g. ``'/users/{id}/settings'``.

        Returns
        -------
        int
            ``static_segments * 10 - dynamic_segments``.
        """
        segments = [s for s in path.split("/") if s]
        static = sum(1 for s in segments if "{" not in s)
        dynamic = len(segments) - static
        return static * 10 - dynamic
