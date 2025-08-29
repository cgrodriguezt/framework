from abc import ABC, abstractmethod
from orionis.console.contracts.cli_request import ICLIRequest

class IWelcomeService(ABC):

    @abstractmethod
    async def helloWorld(self, request: ICLIRequest) -> str:
        """
        Generate and display a personalized greeting message for the user.

        This method retrieves the 'name' argument from the provided `ICLIRequest` instance.
        If the 'name' argument is missing, it defaults to 'Guest'. The greeting message
        is both displayed using the injected console interface and returned as a string.

        Parameters
        ----------
        request : ICLIRequest
            The CLI request object containing command-line arguments and context.
            Used to extract the 'name' argument for the greeting.

        Returns
        -------
        str
            The greeting message addressed to the user. For example, "Hello, Alice!".

        Notes
        -----
        The `ICLIRequest` interface provides structured access to command-line arguments,
        options, and other request data. This method is intended to be implemented by
        subclasses to provide the actual greeting logic.
        """

        # This is an abstract method; implementation should be provided by subclasses.
        pass