from typing import TYPE_CHECKING
from orionis.failure.contracts.catch import ICatch
from orionis.failure.enums.kernel_type import KernelContext
from orionis.foundation.contracts.application import IApplication
from orionis.http.request import Request
from orionis.http.response import Response

if TYPE_CHECKING:
    from orionis.failure.contracts.handler import IBaseExceptionHandler
    from orionis.http.adapters.request.contracts.transport import TransportAdapter

class Catch(ICatch):

    # ruff: noqa: TC001

    def __init__(self, app: IApplication) -> None:
        """
        Initialize the Catch handler with the application instance.

        Parameters
        ----------
        app : IApplication
            The application instance used to resolve required services.

        Returns
        -------
        None
            This constructor does not return any value.
        """
        self.__app: IApplication = app
        self.__exception_handler: IBaseExceptionHandler | None = None

    async def __getContext(self) -> KernelContext:
        """
        Retrieve the current kernel context from the application scope.

        Returns
        -------
        KernelContext
            The kernel type representing the current execution context.

        Raises
        ------
        RuntimeError
            If no active scope or kernel is found.
        """
        # Get the current application scope
        scope = self.__app.getCurrentScope()
        if scope is None:
            error_msg = "No active scope found for context retrieval."
            raise RuntimeError(error_msg)

        # Retrieve the kernel type from the scope
        kernel = await scope.get("kernel")
        if kernel is None:
            error_msg = "No kernel found in the current scope for context retrieval."
            raise RuntimeError(error_msg)

        # Return the kernel type as a string for context identification
        return kernel

    async def __handleReport(
        self,
        exception: BaseException | Exception,
    ) -> None:
        """
        Report an exception using the registered exception handler.

        Parameters
        ----------
        exception : BaseException | Exception
            The exception instance to be reported.

        Returns
        -------
        None
            This method performs side effects and returns None.

        Notes
        -----
        Retrieves the exception handler if not already set and delegates the
        reporting of the exception.
        """
        # Ensure the exception handler is available
        if not self.__exception_handler:
            self.__exception_handler = await self.__app.getExceptionHandler()

        # Report the exception using the exception handler
        return await self.__app.call(
            self.__exception_handler, "report", exception=exception,
        )

    async def __handleCLI(
        self,
        exception: BaseException | Exception,
    ) -> None:
        """
        Handle an exception in the CLI context.

        Parameters
        ----------
        exception : BaseException | Exception
            The exception instance to handle.

        Returns
        -------
        None
            This method performs side effects and returns None.

        Notes
        -----
        Delegates exception handling to the registered CLI exception handler.
        """
        # Ensure the exception handler is available
        if not self.__exception_handler:
            self.__exception_handler = await self.__app.getExceptionHandler()

        # Handle the exception in the context of a CLI request
        if hasattr(self.__exception_handler, "handleCLI"):
            return await self.__app.call(
                self.__exception_handler,
                "handleCLI",
                exception=exception,
            )

        # If no specific CLI handler is defined, simply return None
        return None

    async def __handleHTTP(
        self,
        exception: BaseException | Exception,
        request: Request | TransportAdapter | None = None,
    ) -> Response:
        """
        Handle an exception in the HTTP context.

        Parameters
        ----------
        exception : BaseException | Exception
            The exception instance to handle.
        request : Request | TransportAdapter | None, optional
            The HTTP request or transport adapter associated with the exception.

        Returns
        -------
        Response
            An HTTP response representing the error.

        Notes
        -----
        Delegates exception handling to the registered HTTP exception handler.
        """
        # Ensure the exception handler is available
        if not self.__exception_handler:
            self.__exception_handler = await self.__app.getExceptionHandler()

        # Handle the exception in the context of an HTTP request
        if hasattr(self.__exception_handler, "handleHTTP"):
            return await self.__app.call(
                self.__exception_handler,
                "handleHTTP",
                exception=exception,
                request=request,
            )

        # If no specific HTTP handler is defined
        # return a generic error response
        return Response(
            status_code=500,
            content=str(exception),
            headers={
                "Content-Type": "text/plain",
                "X-Error": "Unhandled exception without specific HTTP handler",
            },
        )

    async def exception(
        self,
        exception: BaseException | Exception,
        request: Request | TransportAdapter | None = None,
    ) -> Response | None:
        """
        Handle an exception based on the current kernel context.

        Parameters
        ----------
        exception : BaseException | Exception
            The exception instance to handle.
        request : Request | TransportAdapter | None, optional
            The HTTP request or transport adapter associated with the exception.

        Returns
        -------
        None | Response
            This method performs side effects and may return a Response.

        Notes
        -----
        Determines the context and delegates exception handling accordingly.
        """
        # Retrieve the current kernel context
        context = await self.__getContext()

        # Report the exception using the registered handler
        await self.__handleReport(exception)

        # Handle the exception according to the kernel context
        if context == KernelContext.CONSOLE:
            return await self.__handleCLI(exception)

        # Handle HTTP exceptions if the context is HTTP
        if context == KernelContext.HTTP:
            return await self.__handleHTTP(exception, request)

        # For other contexts (e.g., HTTP), additional handling can be implemented here
        return None
