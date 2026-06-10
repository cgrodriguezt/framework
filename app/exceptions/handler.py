from typing import ClassVar
from orionis.console.output.console import Console
from orionis.failure.base.handler import BaseExceptionHandler
from orionis.failure.entities.throwable import Throwable
from orionis.http.request import Request
from orionis.http.response import Response
from orionis.services.log.contracts.log_service import ILogger

class ExceptionHandler(BaseExceptionHandler):

    # Exceptions that should not be caught by the handler
    dont_catch: ClassVar[frozenset[type[BaseException]]] = frozenset()

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
        return await super().report(exception, log)

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
        # Delegate CLI rendering to the base exception handler.
        return await super().handleCLI(exception, console)

    async def handleHTTP(
        self,
        exception: Exception,
        request: Request,
    ) -> Response | None:
        """
        Handle the exception for HTTP responses.

        Parameters
        ----------
        exception : Exception
            The exception instance that was caught.
        request : Request
            The HTTP request instance that was being processed.

        Returns
        -------
        Response | None
            The HTTP response representing the error, or None if not handled.
        """
        # Delegate HTTP handling to the base exception handler.
        return await super().handleHTTP(exception, request)
