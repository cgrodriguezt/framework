from app.contracts.welcome_service import IWelcomeService
from app.services.welcome_service import WelcomeService
from orionis.container.providers.service_provider import ServiceProvider

class WelcomeProvider(ServiceProvider):

    def register(self) -> None:
        """
        Register the Welcome service as a singleton in the application container.

        Binds the `IWelcomeService` interface to the `WelcomeService` implementation
        as a singleton with a specific alias. Ensures only one instance of
        `WelcomeService` is shared throughout the application.

        Returns
        -------
        None
            This method does not return any value.
        """
        # Bind IWelcomeService to WelcomeService as a singleton with a specific alias
        self.app.singleton(
            IWelcomeService,
            WelcomeService,
            alias="app.services.welcome_service.WelcomeService",
        )

    def boot(self) -> None:
        """
        Perform post-registration actions after all providers have been registered.

        Called after the `register` phase to allow for additional initialization.
        No extra logic is required for this provider.

        Returns
        -------
        None
            This method does not return any value.
        """
        # No additional boot logic required for this provider
