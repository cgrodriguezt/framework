from orionis.container.facades.facade import Facade

class Log(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the logger service.

        Returns
        -------
        str
            The string identifier for the logger service contract.
        """
        # Return the identifier for the logger service contract
        return "x-orionis.services.log.contracts.log_service.ILogger"
