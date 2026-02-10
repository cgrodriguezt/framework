from app.contracts.welcome_service import IWelcomeService
from orionis.console.request.contracts.cli_request import ICLIRequest
from orionis.console.output.contracts.console import IConsole

class WelcomeService(IWelcomeService):
    def __init__(
        self,
        console: IConsole,
        request: ICLIRequest,
    ) -> None:
        """
        Initialize the WelcomeService with console and request interfaces.

        Parameters
        ----------
        console : IConsole
            Console interface for output and interaction.
        request : ICLIRequest
            CLI request object containing command-line arguments.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Store the console and request interfaces for internal use
        self._console = console
        self._request = request

    async def hello(self) -> str:
        """
        Greet the user by name using the CLI request.

        Retrieves the 'name' argument from the CLI request. If not provided,
        defaults to 'Guest'. Outputs the greeting using the console interface
        and returns the greeting message.

        Returns
        -------
        str
            Greeting message addressed to the user.
        """
        # Retrieve the 'name' argument, defaulting to 'Guest' if not present
        name: str = self._request.argument("name", "Guest")
        message: str = f"Hello, {name}! Welcome to Orionis Framework."
        # Output the greeting message to the console
        self._console.info(message)
        return message
