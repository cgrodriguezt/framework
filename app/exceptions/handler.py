from typing import Any, List
from orionis.console.contracts.cli_request import ICLIRequest
from orionis.console.contracts.console import IConsole
from orionis.failure.base.handler import BaseExceptionHandler
from orionis.services.log.contracts.log_service import ILogger

class ExceptionHandler(BaseExceptionHandler):

    # List of exception types that should not be caught by this handler.
    # Extend this list with specific exceptions as needed.
    # WARNING: Be cautious when adding exceptions to this list,
    # as it may lead to unhandled exceptions and application crashes.
    dont_catch: List[type[BaseException]] = [
        # Example: ValueError, TypeError, etc.
    ]

    async def report(self, exception: Exception, log: ILogger) -> Any:
        """
        Logs or reports an exception using the provided logger.

        Parameters
        ----------
        exception : Exception
            The exception instance that was caught and needs to be reported.
        log : ILogger
            The logger service used to record the exception details.

        Returns
        -------
        Any
            The result of the parent class's report method, if any. Typically None.

        Notes
        -----
        This method can be overridden to implement custom reporting logic,
        such as sending notifications or integrating with external monitoring tools.
        """

        # Delegate reporting to the base exception handler.
        await super().report(exception, log)

    async def renderCLI(self, exception: Exception, request: ICLIRequest, log: ILogger, console: IConsole) -> Any:
        """
        Renders the exception message for command-line interface (CLI) output.

        Parameters
        ----------
        exception : Exception
            The exception instance that was caught and needs to be rendered.
        request : ICLIRequest
            The CLI request context in which the exception occurred.
        log : ILogger
            The logger service used to record the exception details.
        console : IConsole
            The console interface used to display the exception message.

        Returns
        -------
        Any
            The result of the parent class's renderCLI method, if any. Typically None.

        Notes
        -----
        This method can be overridden to customize how exceptions are displayed
        in the CLI, such as formatting or additional output.
        """

        # Delegate CLI rendering to the base exception handler.
        await super().renderCLI(exception, request, log, console)