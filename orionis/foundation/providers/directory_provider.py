from __future__ import annotations
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.services.file.contracts.directory import IDirectory
from orionis.services.file.directory import Directory
from orionis.support.facades.directory import Directory as DirectoryFacade

class DirectoryProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the directory service as a singleton in the application container.

        Binds the `IDirectory` interface to the `Directory` implementation as a
        singleton. The alias ensures unique identification within the container.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return a value.
        """
        # Bind IDirectory to Directory as a singleton with a specific alias.
        self.app.singleton(
            IDirectory,
            Directory,
            alias="x-orionis.services.file.contracts.directory.IDirectory",
        )

    def provides(self) -> list[type]:
        """
        Specify the services provided by this provider.

        Returns a list of service types that this provider is responsible for.

        Parameters
        ----------
        None

        Returns
        -------
        list of type
            A list containing the types of services provided by this provider.
        """
        # Return the list of provided service types.
        return [IDirectory]

    async def boot(self) -> None:
        """
        Initialize the directory service asynchronously.

        This method is called after all services have been registered. It imports and
        initializes the `Directory` facade to ensure it is ready for use in the
        application context.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return a value. The coroutine completes when
            initialization is done.
        """
        await DirectoryFacade.init()
