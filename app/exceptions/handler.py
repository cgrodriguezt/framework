from __future__ import annotations
from typing import ClassVar, TYPE_CHECKING
from orionis.failure.base.handler import BaseExceptionHandler

if TYPE_CHECKING:
    from orionis.console.contracts.cli_request import ICLIRequest
    from orionis.console.contracts.console import IConsole
    from orionis.failure.entities.throwable import Throwable
    from orionis.services.log.contracts.log_service import ILogger

class ExceptionHandler(BaseExceptionHandler):

    # Exceptions that should not be caught by the handler
    dont_catch: ClassVar[list[type[BaseException]]] = [
        # Add specific exceptions that should not be caught
    ]

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
        # Delegate reporting to the base exception handler.
        await super().report(exception, log)

    async def handleCLI(
        self,
        request: ICLIRequest,
        exception: Exception,
        console: IConsole,
    ) -> None:
        """
        Render the exception message for CLI output.

        Parameters
        ----------
        request : ICLIRequest
            The CLI request instance.
        exception : Exception
            The exception instance that was caught.
        console : IConsole
            The console instance for output.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Delegate CLI rendering to the base exception handler.
        await super().handleCLI(request, exception, console)
