from __future__ import annotations
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.console.contracts.reactor import IReactor
from orionis.console.core.reactor import Reactor

class ReactorProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the reactor management service in the application container.

        Bind the `IReactor` interface as a singleton to the `Reactor`
        implementation in the application's dependency injection container.

        Returns
        -------
        None
            No return value. Service is registered in the container.
        """
        # Bind IReactor to Reactor as a singleton with alias for retrieval
        self.app.singleton(
            IReactor,
            Reactor,
            alias="x-orionis.console.contracts.reactor.IReactor",
        )

    def provides(self) -> list[type]:
        """
        Return the services provided by this ReactorProvider.

        Returns
        -------
        list[type]
            List containing the `IReactor` type indicating the provider
            supplies the reactor management service.
        """
        # Return the IReactor service type this provider supplies
        return [IReactor]
