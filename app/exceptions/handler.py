from typing import Any, List
from orionis.console.entities.request import CLIRequest
from orionis.console.output.contracts.console import IConsole
from orionis.failure.base.handler import BaseExceptionHandler
from orionis.services.log.contracts.log_service import ILogger

class ExceptionHandler(BaseExceptionHandler):

    # Exceptions that should not be caught by the handler.
    # WARNING: This will fail silently if you misspell the attribute name or use it incorrectly.
    # This list can be extended with specific exceptions that should not be caught.
    dont_cathc: List[type[BaseException]] = [
        # Add specific exceptions that should not be caught here
        # Example: ValueError, TypeError, etc.
    ]

    def report(self, exception: BaseException, log: ILogger) -> Any:
        """
        Report or log an exception.

        Parameters
        ----------
        exception : BaseException
            The exception instance that was caught.

        Returns
        -------
        None
        """
        super().report(exception, log)

    def renderCLI(self, request: CLIRequest, exception: BaseException, log: ILogger, console: IConsole) -> Any:
        """
        Render the exception message for CLI output.

        Parameters
        ----------
        exception : BaseException
            The exception instance that was caught.

        Returns
        -------
        None
        """
        super().renderCLI(request, exception, log, console)