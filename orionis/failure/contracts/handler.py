from abc import abstractmethod
from typing import Any, List
from orionis.console.output.contracts.console import IConsole
from orionis.services.log.contracts.log_service import ILogger

class IBaseExceptionHandler:

    @abstractmethod
    def report (self, exception: BaseException, log: ILogger) -> Any:
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
        pass

    @abstractmethod
    def renderCLI(self, args: List[str], exception: BaseException, log: ILogger, console: IConsole) -> Any:
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
        pass