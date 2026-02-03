from orionis.container.facades.facade import Facade

class Dumper(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the Dumper.

        Returns
        -------
        str
            The string identifier for the Dumper contract.
        """
        # Return the contract identifier for the Dumper facade
        return "x-orionis.console.contracts.dumper.IDumper"
