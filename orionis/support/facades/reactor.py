from orionis.container.facades.facade import Facade

class Reactor(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the Reactor.

        Returns
        -------
        str
            The string identifier for the Reactor facade accessor.
        """
        # Return the contract string for the Reactor facade accessor
        return "x-orionis.console.contracts.reactor.IReactor"
