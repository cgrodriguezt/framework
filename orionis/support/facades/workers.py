from orionis.container.facades.facade import Facade

class Workers(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the facade accessor string for the workers service.

        Returns
        -------
        str
            The identifier for the workers service contract.
        """
        # Return the service contract identifier for workers
        return "x-orionis.services.system.contracts.workers.IWorkers"
