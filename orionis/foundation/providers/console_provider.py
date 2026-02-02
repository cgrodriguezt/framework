from __future__ import annotations
from orionis.console.contracts.console import IConsole
from orionis.console.output.console import Console
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider

class ConsoleProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the console output service in the application's container.

        Registers the `IConsole` interface to the `Console` implementation as a
        transient service. This ensures a new `Console` instance is provided each
        time the service is resolved. Uses a predefined alias for consistent
        identification.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method modifies the application's service container and does not return
            any value.
        """
        # Bind IConsole to Console as a transient service for dependency injection.
        self.app.transient(
            IConsole,
            Console,
            alias="x-orionis.console.contracts.console.IConsole"
        )

    def provides(self) -> list[type]:
        """
        Specify the services provided by this service provider.

        Returns a list of service types registered by this provider. In this case,
        it indicates that the provider offers the `IConsole` service.

        Parameters
        ----------
        None

        Returns
        -------
        list of type
            A list containing the types of services provided, here only `IConsole`.
        """
        # Return the list of provided service types.
        return [IConsole]
