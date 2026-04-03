from collections.abc import Callable
from orionis.container.contracts.facade import IFacade
from orionis.http.bases.middleware import BaseMiddleware
from orionis.http.contracts.route import IRoute
from orionis.http.routes.fluent import FluentRoute
from orionis.http.routes.router import Router

class Route(IRoute, IFacade):

    @classmethod
    def post(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def get(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def put(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def delete(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def patch(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def head(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def options(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def trace(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def copy(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def link(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def unlink(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def purge(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def lock(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def unlock(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def propfind(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def view(
        cls, path: str, action: Callable | list | None = None,
    ) -> FluentRoute:
        ...

    @classmethod
    def group(cls, *routes: FluentRoute) -> Router:
        ...

    @classmethod
    def middleware(
        cls,
        middleware: list[type[BaseMiddleware]] | type[BaseMiddleware],
    ) -> Router:
        ...

    @classmethod
    def withOutMiddleware(
        cls,
        middleware: type[BaseMiddleware],
    ) -> Router:
        ...

    @classmethod
    def prefix(cls, prefix: str) -> Router:
        ...

    @classmethod
    def fallback(
        cls, action: Callable | list | None = None,
    ) -> None:
        ...
