from orionis.container.providers.service_provider import ServiceProvider
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.services.encrypter.contracts.encrypter import IEncrypter
from orionis.services.encrypter.encrypter import Encrypter

class EncrypterProvider(ServiceProvider, DeferrableProvider):

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
        self.app.singleton(
            abstract=IEncrypter,
            concrete=Encrypter,
            alias="x-orionis.services.encrypter.contracts.encrypter.IEncrypter"
        )

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
