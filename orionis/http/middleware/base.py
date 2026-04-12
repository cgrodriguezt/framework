from typing import Awaitable, Callable

NextCallable = Callable[["Request"], Awaitable["Response"]]

class Middleware:

    async def handle(
        self,
        request: "Request",
        next: callable,
    ) -> "Response":
        """Pass the request to the next middleware or handler.

        Parameters
        ----------
        request : Request
            The incoming HTTP request object.
        next : NextCallable
            The next callable in the middleware pipeline.

        Returns
        -------
        Response
            The HTTP response returned by the next handler.
        """
        # Delegate to the next middleware or route handler
        return await next(request)
