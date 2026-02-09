from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orionis.console.request.contracts.cli_request import ICLIRequest
    from orionis.console.output.contracts.console import IConsole
    from orionis.failure.entities.throwable import Throwable
    from orionis.services.log.contracts.log_service import ILogger

class IBaseExceptionHandler:

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
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
