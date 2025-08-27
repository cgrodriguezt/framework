from orionis.console.contracts.cli_request import ICLIRequest
from orionis.console.contracts.console import IConsole

class WelcomeService:

    def __init__(self, console: IConsole):
        """
        Initialize the service with a console interface.

        Parameters
        ----------
        console : IConsole
            The console interface used for output and interaction.
        """

        # Store the console interface as a private attribute for internal use
        self.__console = console

    def simplePrint(self, request: ICLIRequest) -> None:
        """
        Print a simple "Hello World" message from FakeService to the console.

        This method demonstrates basic console output functionality by sending
        an informational message through the injected console interface. The
        method accepts a CLI request parameter for potential future extensibility
        but currently does not utilize it in the message output process.

        Parameters
        ----------
        request : ICLIRequest
            The CLI request object containing command-line interface data.

        Returns
        -------
        None
            This method performs a console output operation and does not
            return any value.
        """

        # Example of accessing request data if needed in the future
        # command = request.command()
        # args = request.all()
        name = request.argument('name', 'Guest')

        # Use the injected console interface to output an informational message
        # The info method ensures proper logging level and formatting
        self.__console.info(f"Welcome {name}! This is a simple print from WelcomeService.")