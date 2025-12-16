from abc import ABC, abstractmethod

class IWelcomeService(ABC):

    @abstractmethod
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
