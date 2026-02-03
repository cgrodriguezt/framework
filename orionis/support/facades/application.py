from orionis.container.facades.facade import Facade

class Application(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Get the service container binding key for the application component.

        Returns
        -------
        str
            The binding key used to resolve the application service from the
            service container.
        """
        # Return the binding key for the application service interface
        return "x-orionis.foundation.contracts.application.IApplication"
