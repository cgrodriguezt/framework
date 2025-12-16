from orionis.container.facades.facade import Facade

class Welcome(Facade):

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """
        Return the binding key for the Welcome service.

        Retrieves the unique string identifier used by the dependency injection
        container to resolve and instantiate the Welcome service implementation.

        Returns
        -------
        str
            The binding key 'app.services.welcome_service.WelcomeService' that
            identifies the Welcome service within the service container.
        """
        # Return the predefined binding key for the Welcome service
        return "app.services.welcome_service.WelcomeService"
