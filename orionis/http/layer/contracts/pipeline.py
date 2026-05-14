from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING
from orionis.http.request import Request

if TYPE_CHECKING:
    from orionis.http.response import Response

# Type alias for the final route handler: receives a request, returns a response
RouteHandler = Callable[[Request], Awaitable["Response"]]

# Type alias for the no-arg async callable that advances to the next layer
NextCallable = Callable[[], Awaitable["Response"]]

class IMiddlewarePipeline(ABC):
    """Define the contract for immutable middleware pipeline implementations."""

    @abstractmethod
    async def handle(
        self,
        request: Request,
    ) -> Response:
        """Execute the compiled middleware chain for the given request.

        Parameters
        ----------
        request : Request
            Incoming HTTP request passed through the pipeline.

        Returns
        -------
        Response
            HTTP response produced by the chain or the bound handler.
        """
