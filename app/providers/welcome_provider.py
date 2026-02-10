from app.contracts.welcome_service import IWelcomeService
from app.facades.welcome import Welcome as WelcomeFacade
from app.services.welcome_service import WelcomeService
from orionis.container.providers.service_provider import ServiceProvider

class WelcomeProvider(ServiceProvider):

    def register(self) -> None:
        """
        Register the Welcome service as a singleton in the application container.

        Parameters
        ----------
        self : WelcomeProvider
            The instance of the WelcomeProvider.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Binds the `IWelcomeService` interface to the `WelcomeService` implementation
        as a singleton with a specific alias. Ensures only one instance of
        `WelcomeService` is shared throughout the application.
        """
        # Bind IWelcomeService to WelcomeService as a singleton with a specific alias
        self.app.singleton(IWelcomeService, WelcomeService, alias="my_service_alias")

    async def boot(self) -> None:
        """
        Execute post-registration initialization for the provider.

        Parameters
        ----------
        self : WelcomeProvider
            Instance of the WelcomeProvider.

        Returns
        -------
        None
            This method does not return any value.

        Notes
        -----
        Invokes asynchronous initialization for the Welcome facade after registration.
        """
        await WelcomeFacade.init()
