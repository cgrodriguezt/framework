import traceback
from typing import Any, List
from orionis.console.contracts.cli_request import ICLIRequest
from orionis.console.contracts.console import IConsole
from orionis.failure.contracts.handler import IBaseExceptionHandler
from orionis.failure.entities.throwable import Throwable
from orionis.failure.enums.kernel_type import KernelType
from orionis.services.log.contracts.log_service import ILogger

class BaseExceptionHandler(IBaseExceptionHandler):

    # Exceptions that should not be caught by the handler
    dont_catch: list[type[BaseException]] = [
        # Add specific exceptions that should not be caught
        # Example: OrionisContainerException
    ]

    async def destructureException(self, exception: Exception) -> Throwable:
        """
        Convert an exception into a structured Throwable object.

        Parameters
        ----------
        exception : Exception
            The exception instance to be destructured.

        Returns
        -------
        Throwable
            A Throwable object containing the exception's class, message, arguments,
            and traceback.
        """
        # Extract exception arguments, defaulting to an empty string if none exist
        args = getattr(exception, "args", None)
        if not args:
            args = ("",)

        # Ensure all arguments are stringified for consistency
        args = tuple(str(arg) for arg in args)

        # Create and return the Throwable object
        return Throwable(
            classtype=type(exception),
            message=args[0],
            args=args,
            traceback=exception.__traceback__ or traceback.format_exc(),
        )

    async def shouldIgnoreException(self, exception: Exception) -> bool:
        """
        Determine if the exception should be ignored by the handler.

        Parameters
        ----------
        exception : Exception
            The exception instance to check.

        Returns
        -------
        bool
            True if the exception should be ignored, otherwise False.
        """
        # Validate that the input is an exception instance
        if not isinstance(exception, (BaseException, Exception)):
            error_msg = (
                f"Expected BaseException, got {type(exception).__name__}"
            )
            raise TypeError(error_msg)

        # Convert the exception into a structured Throwable object
        throwable = await self.destructureException(exception)

        # Check if the exception type is in the list of exceptions to ignore
        return hasattr(self, "dont_catch") and throwable.classtype in self.dont_catch

    async def report(
        self, exception: Exception, log: ILogger
    ) -> Throwable | None:
        """
        Report or log an exception.

        Parameters
        ----------
        exception : Exception
            Exception instance that was caught.
        log : ILogger
            Logger instance for error reporting.

        Returns
        -------
        Throwable or None
            Structured Throwable object if reported, otherwise None.
        """
        # Ensure the provided object is an exception
        if not isinstance(exception, (BaseException, Exception)):
            error_msg = (
                f"Expected BaseException, got {type(exception).__name__}"
            )
            raise TypeError(error_msg)

        # Skip reporting if the exception should be ignored
        if await self.shouldIgnoreException(exception):
            return None

        # Convert the exception into a structured Throwable object
        throwable = await self.destructureException(exception)

        # Log the exception details
        log.error(f"[{throwable.classtype.__name__}] {throwable.message}")

        # Return the structured exception
        return throwable

    async def handle(self, origin: KernelType, exception: Exception, log: ILogger, console: IConsole) -> Any:
        """
        Render the exception message for CLI output.

        Parameters
        ----------
        exception : Exception
            The exception instance that was caught.

        Returns
        -------
        None
        """
        # Ensure the provided object is an exception
        if not isinstance(exception, (BaseException, Exception)):
            raise TypeError(f"Expected Exception, got {type(exception).__name__}")

        # Skip reporting if the exception should be ignored
        if await self.shouldIgnoreException(exception):
            return

        # Ensure the request is a CLIRequest
        if not isinstance(request, ICLIRequest):
            raise TypeError(f"Expected ICLIRequest, got {type(request).__name__}")

        # Convert the exception into a structured Throwable object
        throwable = await self.destructureException(exception)

        # Log the CLI error message with arguments
        log.error(f"CLI Error: {throwable.message} (Args: {repr(request.arguments())})")

        # Output the exception traceback to the console
        console.newLine()
        console.exception(exception)
        console.newLine()