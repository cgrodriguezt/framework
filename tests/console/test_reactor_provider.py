from __future__ import annotations
from unittest.mock import AsyncMock, MagicMock, patch
from orionis.console.core.contracts.reactor import IReactor
from orionis.console.core.reactor import Reactor
from orionis.console.reactor_provider import ReactorProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.test import TestCase

class TestReactorProvider(TestCase):

    def _make(self) -> tuple[ReactorProvider, MagicMock]:
        """
        Create a ReactorProvider with a mock application.

        Returns
        -------
        tuple[ReactorProvider, MagicMock]
            The provider instance and its mock application.
        """
        mock_app = MagicMock()
        provider = ReactorProvider(mock_app)
        return provider, mock_app

    def testIsSubclassOfServiceProvider(self) -> None:
        """
        Verify ReactorProvider extends ServiceProvider.

        Ensures the class hierarchy is correct and the provider
        follows the service provider contract.
        """
        self.assertTrue(issubclass(ReactorProvider, ServiceProvider))

    def testCanBeInstantiated(self) -> None:
        """
        Verify ReactorProvider can be instantiated with an application.

        Ensures the constructor accepts the app argument without raising.
        """
        provider, _ = self._make()
        self.assertIsInstance(provider, ReactorProvider)

    def testRegisterCallsSingleton(self) -> None:
        """
        Verify register() calls app.singleton with IReactor and Reactor.

        Ensures the reactor interface is bound to its concrete
        implementation as a singleton in the container.
        """
        provider, mock_app = self._make()
        provider.register()
        mock_app.singleton.assert_called_once_with(
            IReactor,
            Reactor,
            alias="x-orionis-IReactor",
        )

    def testRegisterUsesCorrectAlias(self) -> None:
        """
        Verify register() registers the binding with the expected alias.

        Ensures the facade accessor alias is set so the ReactorFacade
        can resolve the correct instance from the container.
        """
        provider, mock_app = self._make()
        provider.register()
        _, kwargs = mock_app.singleton.call_args
        self.assertEqual(kwargs.get("alias"), "x-orionis-IReactor")

    def testRegisterBindsIReactorInterface(self) -> None:
        """
        Verify register() uses IReactor as the binding key.

        Ensures resolution by interface is possible through the container.
        """
        provider, mock_app = self._make()
        provider.register()
        args, _ = mock_app.singleton.call_args
        self.assertIs(args[0], IReactor)

    def testRegisterBindsReactorImplementation(self) -> None:
        """
        Verify register() binds the Reactor concrete class.

        Ensures the correct implementation is registered, not a mock
        or alternative class.
        """
        provider, mock_app = self._make()
        provider.register()
        args, _ = mock_app.singleton.call_args
        self.assertIs(args[1], Reactor)

    async def testBootCallsReactorFacadePin(self) -> None:
        """
        Verify boot() invokes ReactorFacade.pin() exactly once.

        Ensures the reactor facade is initialised during the boot phase
        so it is available for subsequent requests.
        """
        provider, _ = self._make()
        with patch(
            "orionis.console.reactor_provider.ReactorFacade.pin",
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
            "orionis.console.reactor_provider.ReactorFacade.pin",
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
            "orionis.console.reactor_provider.ReactorFacade.pin",
            new_callable=AsyncMock,
        ) as mock_pin:
            await provider.boot()
        mock_app.singleton.assert_called_once()
        mock_pin.assert_called_once()

    def testAppAttributeIsStored(self) -> None:
        """
        Verify that the app attribute is stored correctly on the provider.

        Ensures the application reference is accessible after construction,
        which is required for register() to call app.singleton().
        """
        provider, mock_app = self._make()
        self.assertIs(provider.app, mock_app)
