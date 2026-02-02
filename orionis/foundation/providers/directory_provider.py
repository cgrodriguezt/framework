from __future__ import annotations
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.services.file.contracts.directory import IDirectory
from orionis.services.file.directory import Directory

class DirectoryProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the directory service as a singleton in the application container.

        Binds the `IDirectory` interface to the `Directory` implementation as a singleton.
        The alias ensures unique identification within the container.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method performs registration as a side effect and returns None.
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
        list[type]
            A list containing the types of services provided by this provider.
        """
        # Return the list of provided service types.
        return [IDirectory]
