from __future__ import annotations
from typing import TYPE_CHECKING
from app.contracts.welcome_service import IWelcomeService

if TYPE_CHECKING:
    from orionis.console.contracts.cli_request import ICLIRequest
    from orionis.console.contracts.console import IConsole

class WelcomeService(IWelcomeService):

    def __init__(self, console: IConsole, request: ICLIRequest) -> None:
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
        self.console = console
        self.request = request

    async def helloWorld(self) -> str:
        """
        Greet the user by name using the CLI request.

        Extract the 'name' argument from the ICLIRequest instance. If not provided,
        default to 'Guest'. Display the greeting using the IConsole interface and
        return it as a string.

        Returns
        -------
        str
            Greeting message addressed to the user.
        """
        # Retrieve the 'name' argument, defaulting to 'Guest' if not present
        name = self.request.argument("name", "Guest")
        message = f"Hello, {name}! Welcome to Orionis Framework."

        # Output the greeting message to the console
        self.console.info(message)
        return message
