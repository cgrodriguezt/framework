from orionis.container.facades.facade import Facade
from orionis.test.contracts.engine import ITestingEngine

class Test(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> type:
        """
        Return the facade accessor type for the unit test contract.

        Returns
        -------
        type
            The type of the service that this facade provides access to, which is ITestingEngine
        """
        return ITestingEngine
