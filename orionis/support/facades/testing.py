from orionis.container.facades.facade import Facade

class Test(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the unit test contract.

        Returns
        -------
        str
            The string identifier for the unit test contract.
        """
        return "x-orionis-ITest"
