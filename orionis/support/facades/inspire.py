from orionis.container.facades.facade import Facade

class Inspire(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the Inspire service.

        Returns
        -------
        str
            The accessor string for the IInspire contract.
        """
        # Provide the unique accessor for the IInspire service contract
        return "x-orionis.services.inspirational.contracts.inspire.IInspire"
