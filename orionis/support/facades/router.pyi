from collections.abc import Callable
from orionis.container.contracts.facade import IFacade
from orionis.http.bases.middleware import BaseMiddleware
from orionis.http.routes.contracts.router import IRouter
from orionis.http.routes.fluent import FluentRoute

class Route(IRouter, IFacade):

    @classmethod
    def post(
        cls,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute: ...

    @classmethod
    def get(
        cls,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute: ...

    @classmethod
    def put(
        cls,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute: ...

    @classmethod
    def delete(
        cls,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute: ...

    @classmethod
    def patch(
        cls,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute: ...

    @classmethod
    def head(
        cls,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute: ...

    @classmethod
    def options(
        cls,
        path: str,
        action: Callable | list | type | None = None,
    ) -> FluentRoute: ...

    @classmethod
    def fallback(
        cls,
        action: Callable | list | type | None = None,
    ) -> None: ...

    @classmethod
    def group(
        cls,
        *,
        prefix: str | None = None,
        middleware: list[type[BaseMiddleware]] | None = None,
        routes: list[FluentRoute] | None = None,
    ) -> None: ...
