from __future__ import annotations
import inspect
from orionis.test import TestCase
from orionis.container.facades.facade import Facade
from orionis.container.facades.meta import FacadeMeta

# ---------------------------------------------------------------------------
# Module-level domain helpers
# ---------------------------------------------------------------------------

class _DummyAsyncContext:
    """Minimal async context manager returned by a proxied method."""

    def __init__(self, value: str) -> None:
        self.value = value
        self.exited = False

    async def __aenter__(self) -> str:
        """Return the fixed value carried by this context."""
        return self.value

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
        """Record that the context was exited and never suppress errors."""
        self.exited = True
        return False

class _DummyService:
    """Lightweight service used as a stand-in for facade tests."""

    def greet(self) -> str:
        """Return a greeting string."""
        return "hello"

    def add(self, a: int, b: int) -> int:
        """Return the sum of two integers."""
        return a + b

    def openContext(self) -> _DummyAsyncContext:
        """Return an async context manager carrying a fixed value."""
        return _DummyAsyncContext("ctx-value")

class _ConcreteFacade(Facade):
    """Facade subclass with a fixed accessor key."""

    @classmethod
    def getFacadeAccessor(cls) -> str:
        """Return the service key for this facade."""
        return "dummy_service"

class _NoAccessorFacade(Facade):
    """Facade subclass that deliberately omits getFacadeAccessor."""

class _UnbootedApp:
    """Fake application that reports itself as not booted."""

    isBooted: bool = False  # noqa: N815

class _BootedApp:
    """Fake booted application whose make() always returns a _DummyService."""

    isBooted: bool = True  # noqa: N815

    async def make(
        self,
        _key: object,
        *_args: object,
        **_kwargs: object,
    ) -> _DummyService:
        """Return a fresh _DummyService regardless of the requested key."""
        return _DummyService()

class _CapturingApp:
    """Fake booted application that records the key passed to make()."""

    isBooted: bool = True  # noqa: N815
    captured_key: object = None

    async def make(
        self,
        key: object,
        *_args: object,
        **_kwargs: object,
    ) -> _DummyService:
        """Record the key and return a fresh _DummyService."""
        _CapturingApp.captured_key = key
        return _DummyService()

# ---------------------------------------------------------------------------
# FacadeMeta tests
# ---------------------------------------------------------------------------

class TestFacadeMeta(TestCase):

    def setUp(self) -> None:
        """Reset shared facade state before each test."""
        _ConcreteFacade._pinned_instance = None
        _ConcreteFacade._application = None

    def tearDown(self) -> None:
        """Restore shared facade state after each test."""
        _ConcreteFacade._pinned_instance = None
        _ConcreteFacade._application = None

    def testFacadeClassUsesFacadeMetaAsMetaclass(self) -> None:
        """
        Test that Facade uses FacadeMeta as its metaclass.

        Verifies the metaclass wiring so that attribute-routing via
        __getattr__ is active on any Facade subclass.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Facade, FacadeMeta)

    def testFacadeSubclassAlsoUsesFacadeMetaAsMetaclass(self) -> None:
        """
        Test that a Facade subclass inherits FacadeMeta as its metaclass.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(_ConcreteFacade, FacadeMeta)

    def testGetAttrWithPinnedInstanceRoutesToServiceAttribute(self) -> None:
        """
        Test that __getattr__ forwards attribute access to the pinned instance.

        When _pinned_instance is set, accessing a facade class attribute must
        return the corresponding attribute of the pinned service object
        directly, without creating an async dispatcher.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._pinned_instance = _DummyService()
        method = _ConcreteFacade.greet
        self.assertTrue(callable(method))
        self.assertEqual(method(), "hello")

    def testGetAttrWithPinnedInstanceRaisesAttributeErrorForMissing(self) -> None:
        """
        Raise AttributeError for missing attributes on a pinned facade.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._pinned_instance = _DummyService()
        with self.assertRaises(AttributeError):
            _ = _ConcreteFacade.nonexistent_method

    def testGetAttrWithoutPinnedInstanceReturnsDeferredDispatcher(self) -> None:
        """
        Return a deferred dispatcher when no instance is pinned.

        The dispatcher itself is a plain (sync) callable; calling it builds
        a deferred call object that resolves the service only once it is
        awaited or entered as an async context manager.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._pinned_instance = None
        dispatcher = _ConcreteFacade.greet
        self.assertTrue(callable(dispatcher))
        self.assertFalse(inspect.iscoroutinefunction(dispatcher))
        deferred = dispatcher()
        self.assertTrue(hasattr(deferred, "__await__"))
        self.assertTrue(hasattr(deferred, "__aenter__"))
        self.assertTrue(hasattr(deferred, "__aexit__"))

    async def testUnpinnedDispatcherResolvesWhenAwaited(self) -> None:
        """
        Resolve the service and return the call result when awaited.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._pinned_instance = None
        _ConcreteFacade._application = _BootedApp()
        result = await _ConcreteFacade.greet()
        self.assertEqual(result, "hello")

    async def testUnpinnedDispatcherSupportsAsyncWith(self) -> None:
        """
        Enter and exit an async context manager through an unpinned facade.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._pinned_instance = None
        _ConcreteFacade._application = _BootedApp()
        async with _ConcreteFacade.openContext() as value:
            self.assertEqual(value, "ctx-value")

    def testDispatcherIsCachedOnSubsequentAccesses(self) -> None:
        """
        Return the same cached dispatcher on repeated unpinned accesses.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._pinned_instance = None
        d1 = _ConcreteFacade.greet
        d2 = _ConcreteFacade.greet
        self.assertIs(d1, d2)

    def testDifferentAttributeNamesProduceDifferentDispatchers(self) -> None:
        """
        Produce distinct dispatchers for different attribute names.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._pinned_instance = None
        d_greet = _ConcreteFacade.greet
        d_add = _ConcreteFacade.add
        self.assertIsNot(d_greet, d_add)

# ---------------------------------------------------------------------------
# Facade class-attribute tests
# ---------------------------------------------------------------------------

class TestFacadeClassAttributes(TestCase):

    def testFacadeHasPinnedInstanceAttribute(self) -> None:
        """
        Verify Facade has a _pinned_instance attribute defaulting to None.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(hasattr(Facade, "_pinned_instance"))
        self.assertIsNone(Facade._pinned_instance)

    def testFacadeHasApplicationAttribute(self) -> None:
        """
        Test that Facade exposes a _application class attribute.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(hasattr(Facade, "_application"))

# ---------------------------------------------------------------------------
# Facade.getFacadeAccessor tests
# ---------------------------------------------------------------------------

class TestFacadeGetFacadeAccessor(TestCase):

    def testBaseClassRaisesNotImplementedError(self) -> None:
        """
        Raise NotImplementedError on the base Facade getFacadeAccessor.

        Every concrete subclass must supply its own accessor key.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(NotImplementedError):
            Facade.getFacadeAccessor()

    def testUnoverriddenSubclassRaisesNotImplementedError(self) -> None:
        """
        Raise NotImplementedError when getFacadeAccessor is not overridden.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(NotImplementedError):
            _NoAccessorFacade.getFacadeAccessor()

    def testOverriddenSubclassReturnsExpectedString(self) -> None:
        """
        Return the expected string from an overridden getFacadeAccessor.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(_ConcreteFacade.getFacadeAccessor(), "dummy_service")

    def testErrorMessageContainsClassName(self) -> None:
        """
        Include the class name in the getFacadeAccessor error message.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(NotImplementedError) as ctx:
            Facade.getFacadeAccessor()
        self.assertIn("Facade", str(ctx.exception))

# ---------------------------------------------------------------------------
# Facade.resolve tests
# ---------------------------------------------------------------------------

class TestFacadeResolve(TestCase):

    def setUp(self) -> None:
        """Reset shared facade state before each test."""
        _ConcreteFacade._pinned_instance = None
        _ConcreteFacade._application = None

    def tearDown(self) -> None:
        """Restore shared facade state after each test."""
        _ConcreteFacade._pinned_instance = None
        _ConcreteFacade._application = None

    async def testRaisesRuntimeErrorWhenApplicationNotBooted(self) -> None:
        """
        Raise RuntimeError when the application reports isBooted as False.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._application = _UnbootedApp()
        with self.assertRaises(RuntimeError):
            await _ConcreteFacade.resolve()

    async def testRaisesRuntimeErrorMessageContainsBootHint(self) -> None:
        """
        Test that the RuntimeError message from resolve() mentions booting.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._application = _UnbootedApp()
        with self.assertRaises(RuntimeError) as ctx:
            await _ConcreteFacade.resolve()
        self.assertIn("Boot", str(ctx.exception))

    async def testReturnsServiceInstanceWhenBooted(self) -> None:
        """
        Return a service instance from resolve() when the application is booted.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._application = _BootedApp()
        result = await _ConcreteFacade.resolve()
        self.assertIsInstance(result, _DummyService)

    async def testCallsMakeWithFacadeAccessorKey(self) -> None:
        """
        Forward the facade accessor key to the application make() method.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._application = _CapturingApp()
        await _ConcreteFacade.resolve()
        self.assertEqual(_CapturingApp.captured_key, "dummy_service")

# ---------------------------------------------------------------------------
# Facade.pin tests
# ---------------------------------------------------------------------------

class TestFacadePin(TestCase):

    def setUp(self) -> None:
        """Reset shared facade state before each test."""
        _ConcreteFacade._pinned_instance = None
        _ConcreteFacade._application = None

    def tearDown(self) -> None:
        """Restore shared facade state after each test."""
        _ConcreteFacade._pinned_instance = None
        _ConcreteFacade._application = None

    async def testPinStoresPinnedInstance(self) -> None:
        """
        Test that pin() caches the resolved service in _pinned_instance.

        After pin() is awaited, _pinned_instance must be a non-None
        _DummyService object.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._application = _BootedApp()
        await _ConcreteFacade.pin()
        self.assertIsNotNone(_ConcreteFacade._pinned_instance)
        self.assertIsInstance(_ConcreteFacade._pinned_instance, _DummyService)

    async def testPinRaisesRuntimeErrorWhenNotBooted(self) -> None:
        """
        Propagate RuntimeError from resolve() when the app is not booted.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._application = _UnbootedApp()
        with self.assertRaises(RuntimeError):
            await _ConcreteFacade.pin()

# ---------------------------------------------------------------------------
# Facade.unpin tests
# ---------------------------------------------------------------------------

class TestFacadeUnpin(TestCase):

    def setUp(self) -> None:
        """Seed a pinned instance before each test."""
        _ConcreteFacade._pinned_instance = _DummyService()
        _ConcreteFacade._application = None

    def tearDown(self) -> None:
        """Restore shared facade state after each test."""
        _ConcreteFacade._pinned_instance = None
        _ConcreteFacade._application = None

    def testUnpinClearsPinnedInstance(self) -> None:
        """
        Test that unpin() sets _pinned_instance back to None.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade.unpin()
        self.assertIsNone(_ConcreteFacade._pinned_instance)

    def testUnpinOnAlreadyNoneIsNoop(self) -> None:
        """
        Confirm unpin() is a noop when _pinned_instance is already None.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._pinned_instance = None
        _ConcreteFacade.unpin()
        self.assertIsNone(_ConcreteFacade._pinned_instance)

    async def testPinAndUnpinCycle(self) -> None:
        """
        Verify pin sets and unpin clears the _pinned_instance in sequence.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._application = _BootedApp()
        await _ConcreteFacade.pin()
        self.assertIsNotNone(_ConcreteFacade._pinned_instance)
        _ConcreteFacade.unpin()
        self.assertIsNone(_ConcreteFacade._pinned_instance)

# ---------------------------------------------------------------------------
# End-to-end proxy delegation (pinned instance path)
# ---------------------------------------------------------------------------

class TestFacadeProxyDelegation(TestCase):

    def setUp(self) -> None:
        """Pin a live DummyService instance before each test."""
        _ConcreteFacade._pinned_instance = _DummyService()
        _ConcreteFacade._application = None

    def tearDown(self) -> None:
        """Clear the pinned instance after each test."""
        _ConcreteFacade._pinned_instance = None
        _ConcreteFacade._application = None

    def testDelegatedMethodReturnsExpectedValue(self) -> None:
        """
        Forward a method call through the pinned facade and return the result.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(_ConcreteFacade.greet(), "hello")

    def testDelegatedMethodWithArgumentsReturnsExpectedValue(self) -> None:
        """
        Forward a method with positional arguments through the pinned facade.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(_ConcreteFacade.add(3, 4), 7)

    def testMissingAttributeRaisesAttributeError(self) -> None:
        """
        Raise AttributeError for a missing attribute via the pinned facade.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(AttributeError):
            _ = _ConcreteFacade.does_not_exist
