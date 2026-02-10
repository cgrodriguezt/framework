from orionis.container.facades.facade import Facade

class Welcome(Facade):

    @classmethod
    def getFacadeAccessor(cls: type) -> str:
        """
        Return the binding key for the Welcome service.

        Retrieve the unique string identifier used by the dependency injection
        container to resolve and instantiate the Welcome service implementation.

        Parameters
        ----------
        cls : type
            The class object for Welcome.

        Returns
        -------
        str
            The binding key that identifies the Welcome service within the
            service container.
        """
        # Return the unique alias for the Welcome service in the container
        return "my_service_alias"
