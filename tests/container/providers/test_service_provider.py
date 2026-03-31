from __future__ import annotations
from orionis.test import TestCase
from orionis.container.providers.service_provider import ServiceProvider
from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.contracts.service_provider import IServiceProvider
from orionis.container.contracts.deferrable_provider import IDeferrableProvider

# ---------------------------------------------------------------------------
# Minimal stubs — no external dependencies
# ---------------------------------------------------------------------------

class _FakeApp:
    """Lightweight application stub; satisfies the type hint without booting."""
    pass

class _RegistrationRecorder(ServiceProvider):
    """Subclass that records register() calls."""

    def __init__(self, app: _FakeApp) -> None:
        super().__init__(app)
        self.register_called: bool = False

    def register(self) -> None:
        self.register_called = True

class _BootRecorder(ServiceProvider):
    """Subclass that records async boot() calls."""

    def __init__(self, app: _FakeApp) -> None:
        super().__init__(app)
        self.boot_called: bool = False

    async def boot(self) -> None:
        self.boot_called = True

class _FullProvider(ServiceProvider):
    """Subclass that overrides both register and boot."""

    def __init__(self, app: _FakeApp) -> None:
        super().__init__(app)
        self.registered: bool = False
        self.booted: bool = False

    def register(self) -> None:
        self.registered = True

    async def boot(self) -> None:
        self.booted = True

class _ConcreteDeferred(DeferrableProvider):
    """Concrete DeferrableProvider that returns a real list from provides()."""

    @classmethod
    def provides(cls) -> list[type]:
        return [str, int]

class _EmptyDeferred(DeferrableProvider):
    """Concrete DeferrableProvider that returns an empty list."""

    @classmethod
    def provides(cls) -> list[type]:
        return []

# ===========================================================================
# ServiceProvider tests
# ===========================================================================

class TestServiceProviderInit(TestCase):

    def testAppAttributeIsStoredOnInit(self) -> None:
        """
        Test that __init__ stores the application object as self.app.

        Verifies that the injected application instance is preserved exactly
        (identity check) after construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FakeApp()
        provider = _RegistrationRecorder(app)
        self.assertIs(provider.app, app)

    def testMultipleProvidersHaveIndependentAppReferences(self) -> None:
        """
        Test that two ServiceProvider instances store independent app references.

        Returns
        -------
        None
            This method does not return a value.
        """
        app1, app2 = _FakeApp(), _FakeApp()
        p1 = _RegistrationRecorder(app1)
        p2 = _RegistrationRecorder(app2)
        self.assertIs(p1.app, app1)
        self.assertIs(p2.app, app2)
        self.assertIsNot(p1.app, p2.app)

class TestServiceProviderInheritance(TestCase):

    def testServiceProviderIsInstanceOfIServiceProvider(self) -> None:
        """
        Test that ServiceProvider satisfies the IServiceProvider contract.

        Returns
        -------
        None
            This method does not return a value.
        """
        provider = _RegistrationRecorder(_FakeApp())
        self.assertIsInstance(provider, IServiceProvider)

    def testConcreteSubclassIsInstanceOfServiceProvider(self) -> None:
        """
        Test that a concrete subclass is an instance of ServiceProvider.

        Returns
        -------
        None
            This method does not return a value.
        """
        provider = _FullProvider(_FakeApp())
        self.assertIsInstance(provider, ServiceProvider)

class TestServiceProviderRegister(TestCase):

    def testBaseRegisterIsCallableAndReturnsNone(self) -> None:
        """
        Test that the base register() method can be called and returns None.

        The base ServiceProvider.register() is a no-op; it must not raise and
        must return None.

        Returns
        -------
        None
            This method does not return a value.
        """
        provider = _RegistrationRecorder(_FakeApp())
        # Call the *base* register directly (not the override)
        result = ServiceProvider.register(provider) # NOSONAR
        self.assertIsNone(result)

    def testOverriddenRegisterIsInvoked(self) -> None:
        """
        Test that a subclass override of register() is properly executed.

        Returns
        -------
        None
            This method does not return a value.
        """
        provider = _RegistrationRecorder(_FakeApp())
        self.assertFalse(provider.register_called)
        provider.register()
        self.assertTrue(provider.register_called)

    def testRegisterCanBeCalledMultipleTimes(self) -> None:
        """
        Test that calling register() multiple times does not raise an error.

        Returns
        -------
        None
            This method does not return a value.
        """
        provider = _RegistrationRecorder(_FakeApp())
        provider.register()
        provider.register()
        self.assertTrue(provider.register_called)

class TestServiceProviderBoot(TestCase):

    async def testBaseBootIsAwaitableAndReturnsNone(self) -> None:
        """
        Test that the base async boot() can be awaited and returns None.

        The base ServiceProvider.boot() is an async no-op that must be awaitable
        without raising any exception.

        Returns
        -------
        None
            This method does not return a value.
        """
        provider = _BootRecorder(_FakeApp())
        # Call base boot() directly (bypassing override) via super()
        result = await ServiceProvider.boot(provider)
        self.assertIsNone(result)

    async def testOverriddenBootIsInvokedWhenAwaited(self) -> None:
        """
        Test that a subclass override of async boot() is executed when awaited.

        Returns
        -------
        None
            This method does not return a value.
        """
        provider = _BootRecorder(_FakeApp())
        self.assertFalse(provider.boot_called)
        await provider.boot()
        self.assertTrue(provider.boot_called)

    async def testBootCanBeCalledMultipleTimes(self) -> None:
        """
        Test that awaiting boot() multiple times does not raise an error.

        Returns
        -------
        None
            This method does not return a value.
        """
        provider = _BootRecorder(_FakeApp())
        await provider.boot()
        await provider.boot()
        self.assertTrue(provider.boot_called)

    async def testFullProviderRegisterAndBootAreIndependent(self) -> None:
        """
        Test that register() and boot() operate independently on the same provider.

        Ensures that calling one does not implicitly trigger the other.

        Returns
        -------
        None
            This method does not return a value.
        """
        provider = _FullProvider(_FakeApp())
        provider.register()
        self.assertTrue(provider.registered)
        self.assertFalse(provider.booted)

        await provider.boot()
        self.assertTrue(provider.booted)

    def testBootMethodIsCoroutineFunction(self) -> None:
        """
        Test that ServiceProvider.boot is declared as a coroutine function (async def).

        Validates the contract alignment: IServiceProvider declares boot() as async,
        so the base ServiceProvider must also expose it as async.

        Returns
        -------
        None
            This method does not return a value.
        """
        import inspect
        self.assertTrue(inspect.iscoroutinefunction(ServiceProvider.boot))

# ===========================================================================
# DeferrableProvider tests
# ===========================================================================

class TestDeferrableProviderInheritance(TestCase):

    def testDeferrableProviderIsInstanceOfIDeferrableProvider(self) -> None:
        """
        Test that a concrete DeferrableProvider satisfies the IDeferrableProvider contract.

        Returns
        -------
        None
            This method does not return a value.
        """
        provider = _ConcreteDeferred()
        self.assertIsInstance(provider, IDeferrableProvider)

    def testConcreteSubclassIsInstanceOfDeferrableProvider(self) -> None:
        """
        Test that a concrete subclass is an instance of DeferrableProvider.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(_ConcreteDeferred(), DeferrableProvider)

class TestDeferrableProviderProvides(TestCase):

    def testProvidesRaisesNotImplementedErrorOnBase(self) -> None:
        """
        Test that calling provides() on DeferrableProvider directly raises NotImplementedError.

        DeferrableProvider.provides() is a sentinel implementation that forces
        subclasses to declare their services explicitly.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(NotImplementedError):
            DeferrableProvider.provides()

    def testProvidesErrorMessageIsDescriptive(self) -> None:
        """
        Test that the NotImplementedError message from provides() is informative.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(NotImplementedError) as ctx:
            DeferrableProvider.provides()
        self.assertIn("provides", str(ctx.exception).lower())

    def testConcreteProviderReturnsList(self) -> None:
        """
        Test that a concrete provides() implementation returns a list.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = _ConcreteDeferred.provides()
        self.assertIsInstance(result, list)

    def testConcreteProviderReturnsExpectedTypes(self) -> None:
        """
        Test that provides() returns the exact types declared by the subclass.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = _ConcreteDeferred.provides()
        self.assertIn(str, result)
        self.assertIn(int, result)

    def testProvidesCanReturnEmptyList(self) -> None:
        """
        Test that provides() is allowed to return an empty list without error.

        An empty return is valid when the provider has no eagerly declared services.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = _EmptyDeferred.provides()
        self.assertEqual(result, [])

    def testProvidesIsClassMethod(self) -> None:
        """
        Test that provides() is accessible as a classmethod without instantiation.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Should not raise when called on the class directly
        result = _ConcreteDeferred.provides()
        self.assertIsNotNone(result)

    def testProvidesReturnsSameResultOnRepeatedCalls(self) -> None:
        """
        Test that successive calls to provides() return equivalent results.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(_ConcreteDeferred.provides(), _ConcreteDeferred.provides())

    def testProvidesOnInstanceAndClassAreEquivalent(self) -> None:
        """
        Test that calling provides() on an instance yields the same result as on the class.

        Returns
        -------
        None
            This method does not return a value.
        """
        instance = _ConcreteDeferred()
        self.assertEqual(instance.provides(), _ConcreteDeferred.provides())
