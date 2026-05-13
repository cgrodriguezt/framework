import traceback
from typing import ClassVar
from orionis.console.output.console import Console
from orionis.failure.contracts.handler import IBaseExceptionHandler
from orionis.failure.entities.throwable import Throwable
from orionis.http.adapters.request.contracts.transport import TransportAdapter
from orionis.http.default.responses import DefaultResponses
from orionis.http.payload.body import PayloadTooLargeException
from orionis.http.request import Request
from orionis.http.request import UnsupportedMediaTypeException
from orionis.http.response import Response
from orionis.http.routes.contracts.method_not_allowed import MethodNotAllowed
from orionis.http.routes.contracts.route_not_found import RouteNotFound
from orionis.services.log.contracts.log_service import ILogger

class BaseExceptionHandler(IBaseExceptionHandler):

    # ruff: noqa: G004, TC001

    # Exceptions that should not be caught by the handler
    dont_catch: ClassVar[list[type[BaseException]]] = [
        # Add specific exceptions that should not be caught
    ]

    def __init__(
        self,
        default_responses: DefaultResponses,
    ) -> None:
        """
        Initialize the BaseExceptionHandler instance.

        Initializes the handler and sets up a placeholder for a pre-destructured
        exception.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Placeholder for a pre-destructured exception
        self.__destructured_exception: Throwable | None = None

        # Default responses for HTTP error handling
        self.__default_responses = default_responses

    async def toThrowable(
        self,
        exception: Exception,
    ) -> Throwable:
        """
        Convert an exception to a structured Throwable object.

        Parameters
        ----------
        exception : Exception
            Exception instance to be converted.

        Returns
        -------
        Throwable
            Structured Throwable object containing class, message, arguments,
            and traceback.
        """
        # Return pre-converted exception if available
        if self.__destructured_exception:
            return self.__destructured_exception

        # Extract exception arguments, defaulting to an empty string if none exist
        args = getattr(exception, "args", None)
        if not args:
            args = ("",)

        # Ensure all arguments are stringified for consistency
        args = tuple(str(arg) for arg in args)

        # Create and return the Throwable object
        self.__destructured_exception = Throwable(
            classtype=type(exception),
            message=args[0],
            args=args,
            traceback=exception.__traceback__ or traceback.format_exc(),
        )

        return self.__destructured_exception

    async def isExceptionIgnored(
        self,
        exception: Exception,
    ) -> bool:
        """
        Determine whether the given exception should be ignored.

        Parameters
        ----------
        exception : Exception
            The exception instance to check.

        Returns
        -------
        bool
            True if the exception should be ignored, otherwise False.
        """
        # Ensure the input is an exception instance
        if not isinstance(exception, (BaseException, Exception)):
            error_msg = (
                f"Expected BaseException, got {type(exception).__name__}"
            )
            raise TypeError(error_msg)

        # Convert the exception to a structured Throwable object
        throwable = await self.toThrowable(exception)

        # Return True if the exception type is in dont_catch
        return hasattr(self, "dont_catch") and throwable.classtype in self.dont_catch

    async def report(
        self,
        exception: Exception,
        log: ILogger,
    ) -> Throwable | None:
        """
        Report or log an exception.

        Parameters
        ----------
        exception : Exception
            The exception instance that was caught.
        log : ILogger
            The logger instance for error reporting.

        Returns
        -------
        Throwable or None
            The structured Throwable object if reported, otherwise None.
        """
        # Skip reporting if the exception should be ignored
        if await self.isExceptionIgnored(exception):
            return None

        # Convert the exception into a structured Throwable object
        throwable = await self.toThrowable(exception)

        # Log the exception details
        log.error(f"[{throwable.classtype.__name__}] {throwable.message}")

        # Return the structured exception
        return throwable

    async def handleCLI(
        self,
        exception: Exception,
        console: Console,
    ) -> None:
        """
        Render the exception message for CLI output.

        Parameters
        ----------
        exception : Exception
            The exception instance that was caught.
        console : IConsole
            The console instance for output.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Skip reporting if the exception should be ignored
        if await self.isExceptionIgnored(exception):
            return

        # Output the exception details to the console
        console.exception(exception)

    async def handleHTTP(
        self,
        exception: Exception,
        request: Request | TransportAdapter,
    ) -> Response | None:
        """
        Handle the exception for HTTP responses.

        Parameters
        ----------
        exception : Exception
            The exception instance that was caught.
        request : Request | TransportAdapter
            The HTTP request instance or transport adapter that was being processed.

        Returns
        -------
        Response | None
            The HTTP response if handled, otherwise None.
        """
        # Skip reporting if the exception should be ignored
        if await self.isExceptionIgnored(exception):
            return None

        # Handle 404 route not found with fallback attempt.
        if isinstance(exception, RouteNotFound):
            return self.__default_responses.error(
                status_code=404,
                description="Route not found",
                expects_json=request.wantsJson(),
            )

        # Handle 405 method not allowed.
        if isinstance(exception, MethodNotAllowed):
            return self.__default_responses.error(
                status_code=405,
                description="Method not allowed",
                expects_json=request.wantsJson(),
            )

        # Handle 413 payload too large.
        if isinstance(exception, PayloadTooLargeException):
            return self.__default_responses.error(
                status_code=413,
                description="Payload too large",
                expects_json=request.wantsJson(),
            )

        # Handle 415 unsupported media type.
        if isinstance(exception, UnsupportedMediaTypeException):
            return self.__default_responses.error(
                status_code=415,
                description="Unsupported media type",
                expects_json=request.wantsJson(),
            )

        # Handle 500 server error. (Adapter)
        request_path = (
            request.path()
            if isinstance(request, TransportAdapter)
            else request.path
        )
        request_method = (
            request.method()
            if isinstance(request, TransportAdapter)
            else request.method
        )
        return self.__default_responses.exception(
            request_path=request_path,
            request_method=request_method,
            exception=exception,
            status_code=500,
        )
