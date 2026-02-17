from typing import Awaitable, Callable, Any

NextCallable = Callable[[], Awaitable[Any]]

class BaseMiddleware:

    async def handle( # NOSONAR
        self,
        request: Any,
        next: NextCallable
    ) -> Any:
        """
        Raise NotImplementedError to enforce implementation in subclasses.

        Parameters
        ----------
        request : Any
            The incoming HTTP request object.
        next : NextCallable
            The next middleware or handler to call.

        Returns
        -------
        Any
            The result of the middleware or handler chain.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """
        # Enforce that subclasses must implement this method.
        error_msg = "Middleware must implement the handle method."
        raise NotImplementedError(error_msg)