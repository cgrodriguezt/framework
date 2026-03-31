from __future__ import annotations
import inspect
from abc import ABC
from inspect import isabstract
from orionis.services.environment.contracts.env import IEnv
from orionis.test import TestCase

class _ConcreteEnv(IEnv):
    """Minimal concrete implementation used to verify the contract."""

    @classmethod
    def get(cls, key: str, default=None) -> object:
        return default

    @classmethod
    def set(cls, key: str, value, type_hint=None, *, only_os: bool = False) -> bool:
        return True

    @classmethod
    def unset(cls, key: str, *, only_os: bool = False) -> bool:
        return True

    @classmethod
    def all(cls) -> dict:
        return {}

    @classmethod
    def reload(cls) -> bool:
        return True


class _PartialEnv(IEnv):
    """Subclass implementing only get — intentionally incomplete."""

    @classmethod
    def get(cls, key: str, default=None) -> object:
        return default

# ===========================================================================
# TestIEnvContract
# ===========================================================================

class TestIEnvContract(TestCase):

    def testInheritsFromABC(self) -> None:
        """
        Assert that IEnv inherits from ABC.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(issubclass(IEnv, ABC))

    def testIsAbstractClass(self) -> None:
        """
        Assert that inspect.isabstract identifies IEnv as abstract.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(isabstract(IEnv))

    def testCannotInstantiateDirectly(self) -> None:
        """
        Assert that instantiating IEnv directly raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            IEnv()  # type: ignore[abstract]

    def testGetIsAbstractMethod(self) -> None:
        """
        Assert that 'get' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("get", IEnv.__abstractmethods__)

    def testSetIsAbstractMethod(self) -> None:
        """
        Assert that 'set' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("set", IEnv.__abstractmethods__)

    def testUnsetIsAbstractMethod(self) -> None:
        """
        Assert that 'unset' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("unset", IEnv.__abstractmethods__)

    def testAllIsAbstractMethod(self) -> None:
        """
        Assert that 'all' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("all", IEnv.__abstractmethods__)

    def testReloadIsAbstractMethod(self) -> None:
        """
        Assert that 'reload' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("reload", IEnv.__abstractmethods__)

    def testAbstractMethodsSetContainsFiveMethods(self) -> None:
        """
        Assert that __abstractmethods__ contains exactly five methods.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(
            IEnv.__abstractmethods__,
            frozenset({"get", "set", "unset", "all", "reload"}),
        )

    def testPartialSubclassCannotBeInstantiated(self) -> None:
        """
        Assert that a subclass missing methods cannot be instantiated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            _PartialEnv()  # type: ignore[abstract]

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Assert that a fully implemented subclass can be created without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteEnv()
        self.assertIsInstance(instance, IEnv)

    def testConcreteGetReturnsDefault(self) -> None:
        """
        Assert that a concrete get returns the default when called.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = _ConcreteEnv.get("KEY", "default_val")
        self.assertEqual(result, "default_val")

    def testConcreteSetReturnsBool(self) -> None:
        """
        Assert that a concrete set returns a bool.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = _ConcreteEnv.set("KEY", "value")
        self.assertIsInstance(result, bool)

    def testConcreteAllReturnsDict(self) -> None:
        """
        Assert that a concrete all returns a dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = _ConcreteEnv.all()
        self.assertIsInstance(result, dict)

    def testConcreteReloadReturnsBool(self) -> None:
        """
        Assert that a concrete reload returns a bool.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        result = _ConcreteEnv.reload()
        self.assertIsInstance(result, bool)

    def testGetMethodAcceptsKeyAndDefault(self) -> None:
        """
        Assert that the get method accepts key and default parameters.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = inspect.signature(IEnv.get)
        self.assertIn("key", sig.parameters)
        self.assertIn("default", sig.parameters)
