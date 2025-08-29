from app.contracts.welcome_service import IWelcomeService
from orionis.console.contracts.cli_request import ICLIRequest
from orionis.console.contracts.console import IConsole

class WelcomeService(IWelcomeService):

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

    async def helloWorld(self, request: ICLIRequest) -> str:
        """
        Greets the user by name using the provided CLI request.

        This method extracts the 'name' argument from the given ICLIRequest instance.
        If the argument is not provided, it defaults to 'Guest'. The greeting is
        displayed using the injected IConsole interface and also returned as a string.

        Parameters
        ----------
        request : ICLIRequest
            The CLI request object containing command-line arguments and context.
            Used to retrieve the 'name' argument for the greeting.

        Returns
        -------
        str
            A greeting message addressed to the user.

        Notes
        -----
        The ICLIRequest interface provides methods to access command-line arguments,
        options, and other request data in a structured way.
        """

        name = request.argument('name', 'Guest')
        message = f"Hello, {name}! Welcome to Orionis Framework."
        self.__console.info(message)

        # Return the greeting message for further use if needed
        return message