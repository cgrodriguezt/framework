from __future__ import annotations
from orionis.console.contracts.loader import ILoader
from orionis.console.core.loader import Loader
from orionis.container.providers.service_provider import ServiceProvider
from orionis.container.providers.deferrable_provider import DeferrableProvider

class LoaderProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the Catch service as a singleton in the application container.

        Registers the `ILoader` interface to the `Loader` implementation as a singleton,
        using a specific alias. Ensures only one instance of `Loader` is created and
        shared throughout the application's lifecycle.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method performs registration as a side effect and returns None.
        """
        # Bind Loader as a singleton for the ILoader interface with an explicit alias
        self.app.singleton(
            ILoader,
            Loader,
            alias="x-orionis.console.contracts.loader.ILoader",
        )

    def provides(self) -> list[type]:
        """
        Specify the services provided by this service provider.

        Returns a list of service types that this provider is responsible for. Used by
        the application container to determine which services can be deferred and loaded
        on demand.

        Parameters
        ----------
        None

        Returns
        -------
        list[type]
            A list containing the types of services provided by this provider.
        """
        # Indicate that this provider supplies the ILoader service
        return [ILoader]
