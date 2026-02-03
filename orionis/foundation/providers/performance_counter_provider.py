from __future__ import annotations
from orionis.container.providers.service_provider import ServiceProvider
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.support.performance.contracts.counter import IPerformanceCounter
from orionis.support.performance.counter import PerformanceCounter

class PerformanceCounterProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register the performance counter service as a transient dependency.

        Registers the `IPerformanceCounter` interface to the `PerformanceCounter`
        implementation in the application's dependency injection container. Uses
        a transient lifetime so each resolution provides a new instance. An alias
        is set for alternative resolution by name.

        Returns
        -------
        None
            This method does not return a value. It performs service registration
            as a side effect.
        """
        # Bind IPerformanceCounter to PerformanceCounter with transient lifetime
        self.app.transient(
            IPerformanceCounter,
            PerformanceCounter,
            alias="x-orionis.support.performance.contracts.counter.IPerformanceCounter",
        )

    def provides(self) -> list[type[IPerformanceCounter]]:
        """
        Return the list of services provided by this provider.

        Returns
        -------
        list of type[IPerformanceCounter]
            A list containing the IPerformanceCounter interface type.
        """
        # List the provided service interface(s)
        return [IPerformanceCounter]
