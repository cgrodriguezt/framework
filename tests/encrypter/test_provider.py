from __future__ import annotations

import inspect

from orionis.container.providers.deferrable_provider import DeferrableProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.encrypter.contracts.encrypter import IEncrypter
from orionis.encrypter.encrypter import Encrypter
from orionis.encrypter.provider import EncrypterProvider
from orionis.test import TestCase


# ---------------------------------------------------------------------------
# Module-level stub application
# ---------------------------------------------------------------------------


class _FakeApp:
    """Minimal application stub for EncrypterProvider registration tests."""

    def __init__(self) -> None:
        self.singletons: list[tuple[object, object]] = []

    def singleton(self, abstract: object, concrete: object) -> None:
        """Record a singleton binding."""
        self.singletons.append((abstract, concrete))


# ===========================================================================
# EncrypterProvider
# ===========================================================================


class TestEncrypterProviderInheritance(TestCase):

    def testInheritsServiceProvider(self) -> None:
        """
        Verify EncrypterProvider inherits from ServiceProvider.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(issubclass(EncrypterProvider, ServiceProvider))

    def testInheritsDeferrableProvider(self) -> None:
        """
        Verify EncrypterProvider inherits from DeferrableProvider.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(issubclass(EncrypterProvider, DeferrableProvider))

    def testAppAttributeIsStoredOnInit(self) -> None:
        """
        Verify the application reference is stored after initialization.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FakeApp()
        provider = EncrypterProvider(app)  # type: ignore[arg-type]
        self.assertIs(provider.app, app)


class TestEncrypterProviderProvides(TestCase):

    def testProvidesReturnsListType(self) -> None:
        """
        Verify provides() returns a list.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = EncrypterProvider.provides()
        self.assertIsInstance(result, list)

    def testProvidesContainsIEncrypter(self) -> None:
        """
        Verify provides() returns a list that includes IEncrypter.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn(IEncrypter, EncrypterProvider.provides())

    def testProvidesReturnsSingleElement(self) -> None:
        """
        Verify provides() returns exactly one service type.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(EncrypterProvider.provides()), 1)

    def testProvidesIsCallableAsClassMethod(self) -> None:
        """
        Verify provides() can be called on the class without instantiation.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = EncrypterProvider.provides()
        self.assertIsNotNone(result)


class TestEncrypterProviderRegister(TestCase):

    def testRegisterBindsIEncrypterToEncrypterSingleton(self) -> None:
        """
        Verify register() binds IEncrypter to Encrypter as a singleton.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FakeApp()
        provider = EncrypterProvider(app)  # type: ignore[arg-type]
        provider.register()
        self.assertEqual(len(app.singletons), 1)
        abstract, concrete = app.singletons[0]
        self.assertIs(abstract, IEncrypter)
        self.assertIs(concrete, Encrypter)

    def testRegisterCallsAppSingletonOnce(self) -> None:
        """
        Verify register() invokes app.singleton exactly once.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FakeApp()
        provider = EncrypterProvider(app)  # type: ignore[arg-type]
        provider.register()
        self.assertEqual(len(app.singletons), 1)


class TestEncrypterProviderBoot(TestCase):

    def testBootIsAsyncCoroutineFunction(self) -> None:
        """
        Verify boot() is declared as an async coroutine function.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = _FakeApp()
        provider = EncrypterProvider(app)  # type: ignore[arg-type]
        self.assertTrue(inspect.iscoroutinefunction(provider.boot))
