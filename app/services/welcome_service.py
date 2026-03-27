import asyncio
from app.contracts.welcome_service import IWelcomeService
from orionis.console.output.console import Console

class WelcomeService(IWelcomeService):

    def __init__(
        self,
        console: Console,
    ) -> None:
        """
        Initialize the WelcomeService.

        Parameters
        ----------
        console : Console
            Console interface for output and interaction.

        Returns
        -------
        None
        """
        self._console = console

    async def greetUser(self, name: str = "Guest") -> str:
        """
        Output a personalized greeting message to the user.

        Constructs a greeting message with the provided name and displays
        it to the console with a character-by-character animation effect.

        Parameters
        ----------
        name : str, optional
            The user's name for personalization. Defaults to "Guest".

        Returns
        -------
        str
            The complete greeting message.
        """
        # Construct the greeting message
        message: str = f"Hello, {name}! Welcome to Orionis Framework."

        # Output message with character-by-character animation
        for i, letter in enumerate(message):
            await asyncio.sleep(0.025)
            newline = "\n" if i == len(message) - 1 else ""
            self._console.write(letter, end=newline, flush=True)

        return message
