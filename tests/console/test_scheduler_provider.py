from __future__ import annotations
from unittest.mock import AsyncMock, MagicMock, patch
from orionis.console.contracts.schedule import ISchedule
from orionis.console.scheduler_provider import ScheduleProvider
from orionis.console.contracts.store import IScheduleStore
from orionis.console.tasks.schedule import Schedule
from orionis.console.tasks.store import ScheduleStore
from orionis.container.providers.service_provider import ServiceProvider
from orionis.test import TestCase

class TestScheduleProvider(TestCase):

    def _make(self) -> tuple[ScheduleProvider, MagicMock]:
        """
        Create a ScheduleProvider with a mock application.

        Returns
        -------
        tuple[ScheduleProvider, MagicMock]
            The provider instance and its mock application.
        """
        mock_app = MagicMock()
        provider = ScheduleProvider(mock_app)
        return provider, mock_app

    def testIsSubclassOfServiceProvider(self) -> None:
        """
        Verify ScheduleProvider extends ServiceProvider.

        Ensures the class hierarchy is correct and the provider
        follows the service provider contract.
        """
        self.assertTrue(issubclass(ScheduleProvider, ServiceProvider))

    def testCanBeInstantiated(self) -> None:
        """
        Verify ScheduleProvider can be instantiated with an application.

        Ensures the constructor accepts the app argument without raising.
        """
        provider, _ = self._make()
        self.assertIsInstance(provider, ScheduleProvider)

    def testRegisterCallsSingleton(self) -> None:
        """
        Verify register() calls app.singleton for IScheduleStore and ISchedule.

        Ensures both the store dependency and the schedule interface are
        bound as singletons in the container.
        """
        provider, mock_app = self._make()
        provider.register()
        self.assertEqual(mock_app.singleton.call_count, 2)

    def testRegisterBindsIScheduleStoreInterface(self) -> None:
        """
        Verify register() binds IScheduleStore to ScheduleStore.

        Ensures the store dependency required by Schedule's constructor
        can be auto-resolved by the container.
        """
        provider, mock_app = self._make()
        provider.register()
        args, _ = mock_app.singleton.call_args_list[0]
        self.assertIs(args[0], IScheduleStore)
        self.assertIs(args[1], ScheduleStore)

    def testRegisterBindsIScheduleInterface(self) -> None:
        """
        Verify register() uses ISchedule as the binding key.

        Ensures resolution by interface is possible through the container.
        """
        provider, mock_app = self._make()
        provider.register()
        args, _ = mock_app.singleton.call_args
        self.assertIs(args[0], ISchedule)

    def testRegisterBindsScheduleImplementation(self) -> None:
        """
        Verify register() binds the Schedule concrete class.

        Ensures the correct implementation is registered, not a mock
        or alternative class.
        """
        provider, mock_app = self._make()
        provider.register()
        args, _ = mock_app.singleton.call_args
        self.assertIs(args[1], Schedule)

    async def testBootCallsScheduleFacadePin(self) -> None:
        """
        Verify boot() invokes ScheduleFacade.pin() exactly once.

        Ensures the schedule facade is initialised during the boot phase
        so it is available for subsequent task registration.
        """
        provider, _ = self._make()
        with patch(
            "orionis.console.scheduler_provider.ScheduleFacade.pin",
            new_callable=AsyncMock,
        ) as mock_pin:
            await provider.boot()
            mock_pin.assert_called_once()

    async def testBootDoesNotCallRegister(self) -> None:
        """
        Verify boot() does not call app.singleton.

        Ensures the boot phase only initialises the facade and does not
        attempt to re-register the binding.
        """
        provider, mock_app = self._make()
        with patch(
            "orionis.console.scheduler_provider.ScheduleFacade.pin",
            new_callable=AsyncMock,
        ):
            await provider.boot()
            mock_app.singleton.assert_not_called()

    async def testRegisterThenBootSequence(self) -> None:
        """
        Verify the full register → boot lifecycle succeeds without error.

        Ensures that calling both methods in sequence does not raise
        and each method performs exactly its own side effects.
        """
        provider, mock_app = self._make()
        provider.register()
        with patch(
            "orionis.console.scheduler_provider.ScheduleFacade.pin",
            new_callable=AsyncMock,
        ) as mock_pin:
            await provider.boot()
        self.assertEqual(mock_app.singleton.call_count, 2)
        mock_pin.assert_called_once()

    def testAppAttributeIsStored(self) -> None:
        """
        Verify that the app attribute is stored correctly on the provider.

        Ensures the application reference is accessible after construction,
        which is required for register() to call app.singleton().
        """
        provider, mock_app = self._make()
        self.assertIs(provider.app, mock_app)

    def testRegisterIsCalledMultipleTimesSafely(self) -> None:
        """
        Verify register() can be called multiple times without raising.

        Ensures there is no guard preventing re-registration, which could
        indicate idempotency or potential double-binding issues.
        """
        provider, mock_app = self._make()
        provider.register()
        provider.register()
        self.assertEqual(mock_app.singleton.call_count, 4)
