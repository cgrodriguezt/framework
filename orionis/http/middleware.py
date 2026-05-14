from __future__ import annotations
from typing import TYPE_CHECKING
from orionis.http.layer.contracts.middleware import IBaseMiddleware
from orionis.http.layer.contracts.pipeline import NextCallable

if TYPE_CHECKING:
    from orionis.http.request import Request
    from orionis.http.response import Response

class BaseMiddleware(IBaseMiddleware):

    # ruff: noqa: TC001

    async def handle(
        self,
        request: Request,  # noqa: ARG002
        call_next: NextCallable,
    ) -> Response:
        """Process an incoming HTTP request and delegate to next handler.

        The default implementation is a transparent pass-through that
        immediately delegates to the next layer. Subclasses override
        this method to add before/after logic or early returns.

        Parameters
        ----------
        request : Request
            Incoming HTTP request instance.
        call_next : NextCallable
            No-arg async callable that advances to the next middleware
            or final route handler in the pipeline.

        Returns
        -------
        Response
            HTTP response object returned by the next handler.
        """
        # Transparent pass-through: delegate to the next layer directly
        return await call_next()
