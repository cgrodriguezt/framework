from __future__ import annotations
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.support.facades.testing import Test as TestFacade
from orionis.test.contracts.unit_test import IUnitTest
from orionis.test.core.unit_test import UnitTest

class TestingProvider(ServiceProvider, DeferrableProvider):

    def register(self) -> None:
        """
        Register unit testing service in the application container.

        Retrieve the application's testing configuration, create a UnitTest
        service instance, and register it as a singleton in the dependency
        injection container. The service is bound to the IUnitTest interface.

        Returns
        -------
        None
            No return value. Registers the testing service in the container.
        """
        # Register UnitTest service as singleton bound to IUnitTest interface
        self.app.singleton(
            IUnitTest,
            UnitTest,
            alias="x-orionis.test.contracts.unit_test.IUnitTest",
        )

    def provides(self) -> list[type[IUnitTest]]:
        """
        Return the list of services provided by this provider.

        Returns
        -------
        list[type[IUnitTest]]
            A list containing the IUnitTest interface that this provider registers.
        """
        return [IUnitTest]

    async def boot(self) -> None:
        """
        Initialize the testing facade asynchronously.

        This method initializes the TestFacade, preparing the testing
        environment for use.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Initialize the testing facade for the application
        await TestFacade.init()
