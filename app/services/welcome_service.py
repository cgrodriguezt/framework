import asyncio
from app.contracts.welcome_service import IWelcomeService
from orionis.console.output.console import Console
from orionis.console.request.cli_request import CLIRequest

class WelcomeService(IWelcomeService):

    def __init__(
        self,
        console: Console,
        request: CLIRequest,
    ) -> None:
        """
        Initialize WelcomeService with console and request interfaces.

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

    async def greetUser(self) -> str:
        """
        Output a personalized greeting message for the user.

        Retrieves the 'name' argument from the CLI request. If not provided,
        defaults to 'Guest'. Outputs the greeting using the console interface
        and returns the greeting message.

        Parameters
        ----------
        self : WelcomeService
            Instance of WelcomeService.

        Returns
        -------
        str
            Greeting message addressed to the user.
        """
        # Get the 'name' argument, defaulting to 'Guest' if not present
        name: str = self._request.getArgument("name", "Guest")
        message: str = f"Hello, {name}! Welcome to Orionis Framework."

        # Output the greeting message to the console character by character
        for i, letter in enumerate(message):
            await asyncio.sleep(0.025)
            newline = "\n" if i == len(message) - 1 else ""
            self._console.write(letter, end=newline, flush=True)

        # Return the complete greeting message after outputting it to the console
        return message
