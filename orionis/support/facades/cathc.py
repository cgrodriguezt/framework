from orionis.container.facades.facade import Facade

class Catch(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """Return the facade accessor string for the catch service.

        Returns
        -------
        str
            The facade accessor identifier for the catch service.
        """
        return "x-orionis.failure.contracts.catch.ICatch"
