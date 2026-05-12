from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.http.request import Request
    from orionis.http.response import Response

# Define a type alias for the callable that represents the next
# middleware or route handler in the chain.
CallNext = Callable[[], Awaitable["Response"]]

class BaseMiddleware(ABC):
    """Define the base contract for all HTTP middlewares in the pipeline.

    Middlewares are executed in a chain (onion model), where each
    middleware can inspect or modify the request, delegate to the next
    middleware in the chain, and inspect or modify the response.
    """

    @abstractmethod
    async def handle(
        self,
        request: Request,
        call_next: CallNext,
    ) -> Response:
        """Process an incoming HTTP request and delegate to next handler.

        Parameters
        ----------
        request : Request
            Incoming HTTP request instance.
        call_next : CallNext
            Callable that triggers the next middleware or route handler.

        Returns
        -------
        Response
            Final HTTP response object.
        """
