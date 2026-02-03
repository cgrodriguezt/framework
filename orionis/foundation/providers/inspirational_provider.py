from __future__ import annotations
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.services.inspirational.contracts.inspire import IInspire
from orionis.services.inspirational.inspire import Inspire

class InspirationalProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the inspirational service as a transient binding in the container.

        Registers the `IInspire` interface to the `Inspire` implementation as a
        transient service. Each resolution from the container provides a new instance.
        The service is registered with an alias for convenient resolution and
        identification.

        Returns
        -------
        None
            This method performs service registration and does not return a value.
        """
        # Bind IInspire to Inspire as a transient service with a specific alias.
        self.app.transient(
            IInspire,
            Inspire,
            alias="x-orionis.services.inspirational.contracts.inspire.IInspire",
        )

    def provides(self) -> list[type]:
        """
        List the services provided by this provider.

        Returns
        -------
        list of type
            A list containing the types of services provided by this provider.
        """
        return [IInspire]
