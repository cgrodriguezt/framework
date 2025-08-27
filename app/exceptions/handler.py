from typing import Any, List
from orionis.console.contracts.cli_request import ICLIRequest
from orionis.console.contracts.console import IConsole
from orionis.failure.base.handler import BaseExceptionHandler
from orionis.services.log.contracts.log_service import ILogger

class ExceptionHandler(BaseExceptionHandler):

    # Exceptions that should not be caught by the handler.
    # WARNING: This will fail silently if you misspell the attribute name or use it incorrectly.
    # This list can be extended with specific exceptions that should not be caught.
    dont_catch: List[type[BaseException]] = [
        # Add specific exceptions that should not be caught here
        # Example: ValueError, TypeError, etc.
    ]

    async def report(self, exception: BaseException, log: ILogger) -> Any:
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
        await super().report(exception, log)

    async def renderCLI(self, exception: BaseException, request: ICLIRequest, log: ILogger, console: IConsole) -> Any:
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
        await super().renderCLI(exception, request, log, console)