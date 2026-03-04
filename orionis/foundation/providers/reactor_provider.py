from __future__ import annotations
from orionis.console.core.contracts.reactor import IReactor
from orionis.console.core.reactor import Reactor
from orionis.container.providers.service_provider import ServiceProvider

class ReactorProvider(ServiceProvider):

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
        self.app.singleton(
            abstract=IReactor,
            concrete=Reactor,
            alias="x-orionis.console.contracts.reactor.IReactor",
        )
