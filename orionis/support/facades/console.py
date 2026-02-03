from orionis.container.facades.facade import Facade

class Console(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the Console.

        Returns
        -------
        str
            The string identifier for the Console facade accessor.
        """
        # Return the unique identifier for the Console facade accessor
        return "x-orionis.console.contracts.console.IConsole"
