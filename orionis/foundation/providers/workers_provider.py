from __future__ import annotations
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.services.system.contracts.workers import IWorkers
from orionis.services.system.workers import Workers

class WorkersProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the worker management service in the application container.

        Registers the `IWorkers` interface to its concrete implementation
        `Workers` in the dependency injection container. Uses a transient
        lifetime, so a new instance is created for each resolution. An alias
        is provided for identification.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. It registers the service
            in the application container.
        """
        # Bind IWorkers to Workers with transient lifetime and alias.
        self.app.transient(
            IWorkers,
            Workers,
            alias="x-orionis.services.system.contracts.workers.IWorkers"
        )

    def provides(self) -> list[type]:
        """
        Specify the services provided by this provider.

        Returns a list containing the IWorkers interface, indicating the
        services this provider supplies.

        Parameters
        ----------
        None

        Returns
        -------
        list of type
            A list containing the IWorkers interface.
        """
        return [IWorkers]