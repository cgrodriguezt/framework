from typing import Any, List
from orionis.console.output.contracts.console import IConsole
from orionis.failure.contracts.catch import ICatch
from orionis.failure.entities.throwable import Throwable
from orionis.foundation.contracts.application import IApplication
from orionis.services.log.contracts.log_service import ILogger

class Catch(ICatch):

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

        # Retrieve the console output service from the application container
        self.console: IConsole = app.make('x-orionis.console.output.console')

        # Retrieve the logger service from the application container
        self.logger: ILogger = app.make('x-orionis.services.log.log_service')

    def destructureException(self, e: BaseException) -> Throwable:
        """
        Converts an exception into a structured `Throwable` object containing detailed information.

        Parameters
        ----------
        e : BaseException
            The exception instance to be destructured.

        Returns
        -------
        Throwable
            A `Throwable` object encapsulating the exception's class type, message, arguments, and traceback.

        Notes
        -----
        This method extracts the type, message, arguments, and traceback from the provided exception
        and wraps them in a `Throwable` object for consistent error handling and reporting.
        """

        # Create and return a Throwable object with detailed exception information
        return Throwable(
            classtype=type(e),                              # The class/type of the exception
            message=str(e),                                 # The exception message as a string
            args=e.args,                                    # The arguments passed to the exception
            traceback=getattr(e, '__traceback__', None)     # The traceback object, if available
        )

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

        # Ensure the provided object is an exception
        if not isinstance(exception, BaseException):
            raise TypeError(f"Expected BaseException, got {type(exception).__name__}")

        # Convert the exception into a structured Throwable object
        throwable = self.destructureException(exception)

        # Log the exception details
        self.logger.error(f"[{throwable.classtype.__name__}] {throwable.message}")

        # Return the structured exception
        return throwable

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

        # Ensure the provided object is an exception
        if not isinstance(exception, BaseException):
            raise TypeError(f"Expected BaseException, got {type(exception).__name__}")

        # Convert the exception into a structured Throwable object
        throwable = self.destructureException(exception)

        # Log the CLI error message with arguments
        self.logger.error(f"CLI Error: {throwable.message} (Args: {args})")

        # Output the exception traceback to the console
        self.console.exception(exception)