from app.contracts.welcome_service import IWelcomeService
from app.services.welcome_service import WelcomeService
from orionis.container.providers.service_provider import ServiceProvider

class WelcomeProvider(ServiceProvider):
    """
    Service provider for registering the Welcome service in the application container.

    This class binds the `IWelcomeService` interface to its concrete implementation,
    `WelcomeService`, as a singleton. This ensures that a single shared instance of
    `WelcomeService` is available for dependency injection throughout the application.

    Methods
    -------
    register() -> None
        Registers the `IWelcomeService` interface to the `WelcomeService` implementation
        as a singleton in the application container.
    boot() -> None
        Executes any post-registration logic required after all providers have been registered.
    """

    def register(self) -> None:
        """
        Register the Welcome service as a singleton in the application container.

        This method binds the `IWelcomeService` interface to the `WelcomeService`
        implementation with a specific alias, ensuring that only one instance of
        `WelcomeService` is created and shared throughout the application.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Bind IWelcomeService to WelcomeService as a singleton with a specific alias
        self.app.singleton(IWelcomeService, WelcomeService, alias="app.services.welcome_service.WelcomeService")

    def boot(self) -> None:
        """
        Perform post-registration actions after all providers have been registered.

        This method is called after the `register` phase and can be used to perform
        additional initialization if needed. No additional logic is required for this
        provider.

        Returns
        -------
        None
            This method does not return any value.
        """

        # No additional boot logic required for this provider
        pass