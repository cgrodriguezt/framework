from __future__ import annotations
from typing import Any
from orionis.test import TestCase
from orionis.container.facades.facade import Facade
from orionis.container.facades.meta import FacadeMeta

# ---------------------------------------------------------------------------
# Minimal concrete helpers (defined at module level for pickling safety)
# ---------------------------------------------------------------------------

class _DummyService:
    """Lightweight service used as a stand-in for test facades."""

    def greet(self) -> str:
        return "hello"

    def add(self, a: int, b: int) -> int:
        return a + b

class _ConcreteFacade(Facade):
    """A fully initialised facade whose _service_instance is pre-set."""

    @classmethod
    def getFacadeAccessor(cls) -> str:
        return "dummy_service"

class _UninitialisedFacade(Facade):
    """A facade that is never initialised (no _service_instance set)."""

    @classmethod
    def getFacadeAccessor(cls) -> str:
        return "uninitialised_service"

class _NoAccessorFacade(Facade):
    """A facade that deliberately does NOT override getFacadeAccessor."""

# ---------------------------------------------------------------------------
# FacadeMeta tests
# ---------------------------------------------------------------------------

class TestFacadeMeta(TestCase):

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
        Test that a concrete Facade subclass inherits FacadeMeta as its metaclass.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(_ConcreteFacade, FacadeMeta)

    def testGetServiceInstanceOnMetaRaisesNotImplementedError(self) -> None:
        """
        Test that calling _getServiceInstance directly on
        FacadeMeta raises NotImplementedError.

        FacadeMeta._getServiceInstance is a sentinel that must be overridden
        by concrete Facade classes.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(NotImplementedError):
            FacadeMeta._getServiceInstance()

    def testGetAttrRoutesToServiceAttribute(self) -> None:
        """
        Test that __getattr__ on the facade class proxies to the cached service.

        Pre-seeds _service_instance and verifies that attribute access on the
        facade class is transparently forwarded to the service object.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._service_instance = _DummyService()
        try:
            method = _ConcreteFacade.greet
            self.assertTrue(callable(method))
            self.assertEqual(method(), "hello")
        finally:
            _ConcreteFacade._service_instance = None

    def testGetAttrRaisesAttributeErrorForMissingServiceAttribute(self) -> None:
        """
        Test that __getattr__ raises AttributeError when the service
        lacks the requested attribute.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._service_instance = _DummyService()
        try:
            with self.assertRaises(AttributeError):
                _ = _ConcreteFacade.nonexistent_method
        finally:
            _ConcreteFacade._service_instance = None

    def testGetAttrErrorMessageContainsFacadeNameAndAttributeName(self) -> None:
        """
        Test that the AttributeError message includes both the facade class name
        and the missing attribute name.

        Returns
        -------
        None
            This method does not return a value.
        """
        _ConcreteFacade._service_instance = _DummyService()
        try:
            with self.assertRaises(AttributeError) as ctx:
                _ = _ConcreteFacade.totally_missing
            self.assertIn("_ConcreteFacade", str(ctx.exception))
            self.assertIn("totally_missing", str(ctx.exception))
        finally:
            _ConcreteFacade._service_instance = None

# ---------------------------------------------------------------------------
# Facade._getServiceInstance tests
# ---------------------------------------------------------------------------

class TestFacadeGetServiceInstance(TestCase):

    def setUp(self) -> None:
        """Reset cached state before each test."""
        _ConcreteFacade._service_instance = None
        _ConcreteFacade._application = None
        _UninitialisedFacade._service_instance = None
        _UninitialisedFacade._application = None

    def tearDown(self) -> None:
        """Reset cached state after each test."""
        _ConcreteFacade._service_instance = None
        _ConcreteFacade._application = None
        _UninitialisedFacade._service_instance = None
        _UninitialisedFacade._application = None

    def testGetServiceInstanceRaisesRuntimeErrorWhenNotInitialised(self) -> None:
        """
        Test that _getServiceInstance raises RuntimeError when no instance is cached.

        Verifies the guard that prevents using a facade before init() is called.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(RuntimeError):
            _UninitialisedFacade._getServiceInstance()

    def testGetServiceInstanceErrorMessageContainsFacadeName(self) -> None:
        """
        Test that the RuntimeError message includes the facade class name.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(RuntimeError) as ctx:
            _UninitialisedFacade._getServiceInstance()
        self.assertIn("_UninitialisedFacade", str(ctx.exception))

    def testGetServiceInstanceReturnsServiceWhenInitialised(self) -> None:
        """
        Test that _getServiceInstance returns the cached service when it has been set.

        Returns
        -------
        None
            This method does not return a value.
        """
        service = _DummyService()
        _ConcreteFacade._service_instance = service
        result = _ConcreteFacade._getServiceInstance()
        self.assertIs(result, service)

# ---------------------------------------------------------------------------
# Facade.getFacadeAccessor tests
# ---------------------------------------------------------------------------

class TestFacadeGetFacadeAccessor(TestCase):

    def testGetFacadeAccessorRaisesNotImplementedErrorOnBaseClass(self) -> None:
        """
        Test that calling getFacadeAccessor on the base Facade raises NotImplementedError.

        The base class has no default accessor; every subclass must define one.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(NotImplementedError):
            Facade.getFacadeAccessor()

    def testGetFacadeAccessorRaisesNotImplementedErrorOnUnoverrriddenSubclass(self) -> None:
        """
        Test that a subclass which does not override getFacadeAccessor raises NotImplementedError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(NotImplementedError):
            _NoAccessorFacade.getFacadeAccessor()

    def testGetFacadeAccessorReturnsStringOnConcreteSubclass(self) -> None:
        """
        Test that a properly overridden getFacadeAccessor returns the expected string.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = _ConcreteFacade.getFacadeAccessor()
        self.assertEqual(result, "dummy_service")

    def testGetFacadeAccessorErrorMessageContainsClassName(self) -> None:
        """
        Test that the NotImplementedError message from getFacadeAccessor includes the class name.

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
        """Reset cached state before each test."""
        _ConcreteFacade._service_instance = None
        _ConcreteFacade._application = None

    def tearDown(self) -> None:
        """Reset cached state after each test."""
        _ConcreteFacade._service_instance = None
        _ConcreteFacade._application = None

    def testResolveRaisesRuntimeErrorWhenNotInitialised(self) -> None:
        """
        Test that resolve() raises RuntimeError when the facade has not been initialised.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(RuntimeError):
            _ConcreteFacade.resolve()

    def testResolveReturnsCachedServiceInstance(self) -> None:
        """
        Test that resolve() returns the exact cached service instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        service = _DummyService()
        _ConcreteFacade._service_instance = service
        result = _ConcreteFacade.resolve()
        self.assertIs(result, service)

    def testResolveReturnsSameObjectOnSubsequentCalls(self) -> None:
        """
        Test that successive calls to resolve() return the same cached instance (no re-creation).

        Returns
        -------
        None
            This method does not return a value.
        """
        service = _DummyService()
        _ConcreteFacade._service_instance = service
        self.assertIs(_ConcreteFacade.resolve(), _ConcreteFacade.resolve())

# ---------------------------------------------------------------------------
# Facade.init tests  (those not requiring a fully booted application)
# ---------------------------------------------------------------------------

class TestFacadeInit(TestCase):

    def setUp(self) -> None:
        """Reset cached state before each test."""
        _ConcreteFacade._service_instance = None
        _ConcreteFacade._application = None

    def tearDown(self) -> None:
        """Reset cached state after each test."""
        _ConcreteFacade._service_instance = None
        _ConcreteFacade._application = None

    async def testInitRaisesRuntimeErrorWhenApplicationNotBooted(self) -> None:
        """
        Test that init() raises RuntimeError when the application exists but is not booted.

        Injects a mock application object whose isBooted property returns False
        to simulate the unbooted state without starting a real application.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _FakeApp:
            isBooted: bool = False # NOSONAR

        _ConcreteFacade._application = _FakeApp()

        with self.assertRaises(RuntimeError) as ctx:
            await _ConcreteFacade.init()

        self.assertIn("not booted", str(ctx.exception).lower())

    async def testInitRaisesRuntimeErrorWhenMakeRaisesException(self) -> None:
        """
        Test that init() wraps exceptions from make() inside a RuntimeError.

        Injects a booted application whose make() raises an arbitrary exception
        and verifies the facade re-raises it as RuntimeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _BrokenApp:
            isBooted: bool = True # NOSONAR

            async def make(self, *args: Any, **kwargs: Any) -> None:
                raise ValueError("service not found")

        _ConcreteFacade._application = _BrokenApp()

        with self.assertRaises(RuntimeError) as ctx:
            await _ConcreteFacade.init()

        self.assertIn("_ConcreteFacade", str(ctx.exception))

    async def testInitCachesServiceInstanceOnSuccess(self) -> None:
        """
        Test that a successful init() stores the resolved service in _service_instance.

        Injects a booted application whose make() returns a known service object.

        Returns
        -------
        None
            This method does not return a value.
        """
        service = _DummyService()

        class _OkApp:
            isBooted: bool = True # NOSONAR

            async def make(self, *args: Any, **kwargs: Any) -> _DummyService: # NOSONAR
                return service

        _ConcreteFacade._application = _OkApp()
        await _ConcreteFacade.init()

        self.assertIs(_ConcreteFacade._service_instance, service)

# ---------------------------------------------------------------------------
# End-to-end proxy delegation
# ---------------------------------------------------------------------------

class TestFacadeProxyDelegation(TestCase):

    def setUp(self) -> None:
        """Seed the facade with a live DummyService instance."""
        _ConcreteFacade._service_instance = _DummyService()

    def tearDown(self) -> None:
        """Clear the cached service after each test."""
        _ConcreteFacade._service_instance = None
        _ConcreteFacade._application = None

    def testDelegatedMethodReturnsExpectedValue(self) -> None:
        """
        Test that a method call forwarded through the facade returns the correct result.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(_ConcreteFacade.greet(), "hello")

    def testDelegatedMethodWithArgumentsReturnsExpectedValue(self) -> None:
        """
        Test that a method requiring arguments is forwarded correctly through the facade.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(_ConcreteFacade.add(3, 4), 7)

    def testDelegatedAttributeAccessOnMissingAttributeRaisesAttributeError(self) -> None:
        """
        Test that accessing a non-existent attribute via the facade raises AttributeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(AttributeError):
            _ = _ConcreteFacade.does_not_exist
