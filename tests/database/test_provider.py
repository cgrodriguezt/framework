from __future__ import annotations
from orionis.container.providers.service_provider import ServiceProvider
from orionis.database.connection_manager import ConnectionManager
from orionis.database.contracts.manager import IConnectionManager
from orionis.database.database_provider import DatabaseProvider
from orionis.foundation.application import Application
from orionis.orm.resolver import ConnectionResolver
from orionis.support.facades.db import DB
from orionis.test import TestCase

class _CaptureApp:
    """Application stub capturing singleton registrations."""

    def __init__(self) -> None:
        self.bindings: list[tuple[type, type]] = []

    def singleton(self, contract: type, implementation: type) -> None:
        self.bindings.append((contract, implementation))

class TestDatabaseProvider(TestCase):

    def testProviderInheritsFrameworkBase(self) -> None:
        """
        Extend the framework ServiceProvider base.

        Validates the provider class hierarchy.
        """
        self.assertTrue(issubclass(DatabaseProvider, ServiceProvider))

    def testRegisterBindsManagerAsSingleton(self) -> None:
        """
        Bind IConnectionManager to ConnectionManager as a singleton.

        Validates the container registration.
        """
        app = _CaptureApp()
        provider = DatabaseProvider(app)  # type: ignore[arg-type]
        provider.register()
        self.assertEqual(
            app.bindings,
            [(IConnectionManager, ConnectionManager)],
        )

    async def testBootWiresResolverAndPinsFacade(self) -> None:
        """
        Install the manager on the resolver and pin the DB facade.

        Validates the boot wiring against the booted application.
        """
        previous = ConnectionResolver._manager
        try:
            app = Application()
            provider = DatabaseProvider(app)
            await provider.boot()

            manager = ConnectionResolver.manager()
            self.assertIsInstance(manager, ConnectionManager)
            self.assertIsNotNone(DB._pinned_instance)
            self.assertEqual(DB.getDefaultName(), manager.getDefaultName())
        finally:
            ConnectionResolver._manager = previous

class TestDBFacade(TestCase):

    def testFacadeAccessorIsManagerContract(self) -> None:
        """
        Expose IConnectionManager as the facade accessor.

        Validates the facade to container binding.
        """
        self.assertIs(DB.getFacadeAccessor(), IConnectionManager)
