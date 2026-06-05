from __future__ import annotations
from typing import TYPE_CHECKING
from orionis.http.layer.contracts.pipeline import IMiddlewarePipeline

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from orionis.foundation.contracts.application import IApplication
    from orionis.http.middleware import BaseMiddleware
    from orionis.http.request import Request
    from orionis.http.response import Response

    type FinalHandler = Callable[
        [],
        Awaitable[Response],
    ]

    type NextCallable = Callable[
        [],
        Awaitable[Response],
    ]

class MiddlewarePipeline(IMiddlewarePipeline):

    def __init__(
        self,
        app: IApplication,
        request: Request,
        middlewares: list[type[BaseMiddleware]],
        final_handler: FinalHandler,
    ) -> None:
        """Initialize the middleware pipeline with its dependencies.

        Parameters
        ----------
        app : IApplication
            Application container used to resolve middleware instances.
        request : Request
            Incoming HTTP request shared across the middleware chain.
        middlewares : list[type[BaseMiddleware]]
            Ordered middleware classes executed before the final handler.
        final_handler : FinalHandler
            Final callable executed after all middleware complete.

        Returns
        -------
        None
            Initializes instance attributes; no value is returned.
        """
        # Store application container for middleware resolution
        self.__app = app

        # Store the shared request object for the chain
        self.__request = request

        # Convert to tuple for immutability and O(1) index access
        self.__middlewares = tuple(middlewares)

        # Store the final handler invoked after all middleware
        self.__final_handler = final_handler

    async def handle(self) -> Response:
        """Execute the middleware pipeline from the first layer.

        Returns
        -------
        Response
            Final response produced by middleware or the final handler.
        """
        # Start dispatching from index 0 (first middleware)
        return await self.__dispatch(0)

    async def __dispatch(
        self,
        index: int,
    ) -> Response:
        """Dispatch execution to the middleware layer at the given index.

        Parameters
        ----------
        index : int
            Current position in the ordered middleware stack.

        Returns
        -------
        Response
            Response produced by the current middleware or the final
            handler when the stack is exhausted.
        """
        # End of middleware stack — invoke the final handler
        if index >= len(self.__middlewares):
            return await self.__final_handler()

        # Resolve the middleware class at the current index
        middleware_class = self.__middlewares[index]

        # Build the middleware instance via the application container
        middleware = await self.__app.build(middleware_class)

        # Guard flag to prevent multiple next() invocations per layer
        called = False

        async def next_fn() -> Response:
            """Advance execution to the next middleware layer.

            Returns
            -------
            Response
                Response from the subsequent middleware or final handler.

            Raises
            ------
            RuntimeError
                If ``next()`` is called more than once in the same layer.
            """
            nonlocal called

            # Raise if next() was already invoked in this layer
            if called:
                error_msg = (
                    "next() has already been called "
                    "in this middleware layer."
                )
                raise RuntimeError(error_msg)

            # Mark as called before advancing to the next layer
            called = True

            # Dispatch recursively to the next middleware layer
            return await self.__dispatch(index + 1)

        # Execute the current middleware and return its response
        return await middleware.handle(self.__request, next_fn)
