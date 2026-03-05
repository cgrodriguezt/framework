from __future__ import annotations
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.services.encrypter.contracts.encrypter import IEncrypter
from orionis.services.encrypter.encrypter import Encrypter
from orionis.support.facades.encrypter import Crypt as CryptFacade

class EncrypterProvider(ServiceProvider, DeferrableProvider):

    @classmethod
    def provides(self) -> list[type]:
        """
        Return the services provided by this provider.

        Specify the service types that this provider is responsible for.
        Used by the application container to determine which services can be
        deferred and loaded on demand.

        Returns
        -------
        list[type]
            List containing the types of services provided by this provider.
        """
        return [IEncrypter]

    def register(self) -> None:
        """
        Register the encrypter service in the application container.

        This method binds the IEncrypter interface to its concrete implementation
        as a singleton, ensuring a single instance is shared across the application.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.app.singleton(IEncrypter, Encrypter, alias="x-orionis-IEncrypter")

    async def boot(self) -> None:
        """
        Perform asynchronous initialization after service registration.

        This method is used for setup tasks that require registered services,
        such as initializing facades or performing asynchronous operations.

        Returns
        -------
        None
            This method does not return a value. It performs initialization only.
        """
        await CryptFacade.init()
