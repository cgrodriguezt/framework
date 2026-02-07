from typing import TYPE_CHECKING, Any
from orionis.failure.contracts.catch import ICatch
from orionis.failure.enums.kernel_type import KernelType
from orionis.foundation.contracts.application import IApplication

if TYPE_CHECKING:
    from orionis.failure.contracts.handler import IBaseExceptionHandler

class Catch(ICatch):

    def __init__(self, app: IApplication) -> None:
        """
        Initialize the Catch handler with application services.

        Parameters
        ----------
        app : IApplication
            The application instance used to resolve required services.

        Returns
        -------
        None
            This constructor does not return any value.

        Notes
        -----
        Retrieves the exception handler from the application container for
        error reporting and output.
        """
        # Store the application instance for later use
        self.__app: IApplication = app
        # Initialize the exception handler to None; it will be retrieved when needed
        self.__exception_handler: IBaseExceptionHandler | None = None

    async def exception(
        self,
        kernel: KernelType,
        request: type[Any],
        exception: BaseException | Exception,
    ) -> None:
        """
        Handle and report exceptions during CLI execution.

        Parameters
        ----------
        kernel : KernelType
            The kernel instance associated with the CLI, or None if not available.
        request : type[Any]
            The request or arguments associated with the CLI command.
        exception : BaseException | Exception
            The exception instance to be handled.

        Returns
        -------
        None
            This method performs side effects such as logging and output.
        """
        # Retrieve the exception handler from the application container
        if not self.__exception_handler:
            self.__exception_handler = await self.__app.getExceptionHandler()

        # Report the exception using the exception handler and logger
        await self.__app.call(self.__exception_handler, "report", exception=exception)

        # If kernel is of type CONSOLE, render the exception to CLI
        if kernel == KernelType.CONSOLE:
            await self.__app.call(
                self.__exception_handler,
                "handleCLI",
                request=request,
                exception=exception,
            )
