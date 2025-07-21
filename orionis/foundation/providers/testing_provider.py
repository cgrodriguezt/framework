from orionis.container.providers.service_provider import ServiceProvider
from orionis.test.contracts.unit_test import IUnitTest
from orionis.test.core.unit_test import UnitTest

class TestingProvider(ServiceProvider):

    def register(self) -> None:
        """
        Register services into the application container.
        """
        self.app.singleton(IUnitTest, UnitTest, alias="core.orionis.testing")

    def boot(self) -> None:
        """
        Perform any post-registration bootstrapping or initialization.
        """
        pass