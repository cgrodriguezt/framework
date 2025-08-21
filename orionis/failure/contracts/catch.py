from abc import ABC, abstractmethod
from typing import Any, List
from orionis.foundation.contracts.application import IApplication

class ICatch(ABC):

    @abstractmethod
    def __init__(self, app: IApplication) -> None:
        """
        Initializes the Catch handler with application services for console output and logging.

        Parameters
        ----------
        app : IApplication
            The application instance used to resolve required services.

        Attributes
        ----------
        console : IConsole
            Console output service obtained from the application for displaying messages and exceptions.
        logger : ILogger
            Logger service obtained from the application for logging errors and exceptions.

        Returns
        -------
        None
            This constructor does not return any value.

        Notes
        -----
        The constructor retrieves the console and logger services from the application container
        using their respective service keys. These services are used throughout the class for
        error reporting and output.
        """
        pass

    @abstractmethod
    def report(self, exception: BaseException) -> Any:
        """
        Logs and returns a destructured representation of an exception.

        Parameters
        ----------
        exception : BaseException
            The exception instance to be reported.

        Returns
        -------
        Throwable
            A destructured representation of the exception, containing its type, message, arguments, and traceback.

        Raises
        ------
        TypeError
            If the provided exception is not an instance of BaseException.

        Notes
        -----
        This method logs the exception details using the configured logger and returns a structured
        representation of the exception for further processing.
        """
        pass

    @abstractmethod
    def renderCLI(self, args: List[str], exception: BaseException) -> Any:
        """
        Renders a CLI-friendly error message for a given exception.

        Parameters
        ----------
        args : list
            The list of command-line arguments that were passed to the CLI.
        exception : BaseException
            The exception instance to be rendered.

        Returns
        -------
        None
            This method does not return any value.

        Raises
        ------
        TypeError
            If the provided exception is not an instance of BaseException.

        Notes
        -----
        This method logs the error message using the configured logger and outputs
        the exception traceback to the console for user visibility.
        """
        pass