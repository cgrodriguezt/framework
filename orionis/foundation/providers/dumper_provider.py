from __future__ import annotations
from orionis.console.debug.contracts.dumper import IDumper
from orionis.console.debug.dumper import Dumper
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.support.facades.dumper import Dumper as DumperFacade

class DumperProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the Dumper service in the application container.

        Registers the `IDumper` interface to the `Dumper` class as a transient
        service. Assigns an alias for convenient retrieval. Ensures a new
        instance is created for each request.

        Returns
        -------
        None
            This method modifies the application's service registry and does not
            return a value.
        """
        # Bind IDumper to Dumper as a transient service with an alias.
        self.app.transient(
            IDumper,
            Dumper,
            alias="x-orionis.console.contracts.dumper.IDumper",
        )

    def provides(self) -> list[type]:
        """
        Specify the services provided by this service provider.

        Returns a list of service types registered by this provider. Indicates
        that `IDumper` is provided.

        Returns
        -------
        list[type]
            A list containing the types of services provided, here only `IDumper`.
        """
        # Return the list of provided service types.
        return [IDumper]

    async def boot(self) -> None:
        """
        Perform asynchronous initialization after registration.

        Imports the `Dumper` facade to ensure it is available in the application
        context and initializes it asynchronously.

        Returns
        -------
        None
            This method performs initialization and does not return a value.
        """
        await DumperFacade.init()
