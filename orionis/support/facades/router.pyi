from collections.abc import Callable
from orionis.container.contracts.facade import IFacade
from orionis.http.middleware import BaseMiddleware
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
    def query(
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
    def fallback(
        cls,
        action: Callable | list | type | None = None,
    ) -> None: ...

    @classmethod
    def group(
        cls,
        *,
        prefix: str | None = None,
        middleware: type[BaseMiddleware] | list | tuple | set | None = None,
        without_middleware: (
            type[BaseMiddleware] | list | tuple | set | None
        ) = None,
        routes: list[FluentRoute] | None = None,
    ) -> None: ...
