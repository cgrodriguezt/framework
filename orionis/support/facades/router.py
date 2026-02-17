from orionis.container.facades.facade import Facade

class Route(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the unit test contract.

        Returns
        -------
        str
            String identifier for the unit test contract.
        """
        # Return the contract identifier for the unit test facade
        return "x-orionis.http.contracts.route.IRoute"
