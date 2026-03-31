from __future__ import annotations
import inspect
from abc import ABC
from inspect import isabstract
from orionis.services.cache.contracts.file_based_cache import IFileBasedCache
from orionis.test import TestCase

class _ConcreteFileBasedCache(IFileBasedCache):
    """Minimal concrete implementation used to verify the contract can be satisfied."""

    def get(self) -> dict | None:
        return {"key": "value"}

    def save(self, data: dict) -> tuple[int, str]:
        return (1, "abc123")

    def clear(self) -> bool:
        return True


class _PartialFileBasedCache(IFileBasedCache):
    """Subclass implementing only get — intentionally incomplete."""

    def get(self) -> dict | None:
        return None

# ===========================================================================
# TestIFileBasedCacheContract
# ===========================================================================

class TestIFileBasedCacheContract(TestCase):

    def testInheritsFromABC(self) -> None:
        """
        Assert that IFileBasedCache inherits from ABC.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(issubclass(IFileBasedCache, ABC))

    def testIsAbstractClass(self) -> None:
        """
        Assert that inspect.isabstract identifies IFileBasedCache as abstract.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(isabstract(IFileBasedCache))

    def testCannotInstantiateDirectly(self) -> None:
        """
        Assert that instantiating IFileBasedCache directly raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            IFileBasedCache()  # type: ignore[abstract]

    def testGetIsAbstractMethod(self) -> None:
        """
        Assert that 'get' is declared as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("get", IFileBasedCache.__abstractmethods__)

    def testSaveIsAbstractMethod(self) -> None:
        """
        Assert that 'save' is declared as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("save", IFileBasedCache.__abstractmethods__)

    def testClearIsAbstractMethod(self) -> None:
        """
        Assert that 'clear' is declared as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("clear", IFileBasedCache.__abstractmethods__)

    def testAbstractMethodsSetContainsExactlyThreeMethods(self) -> None:
        """
        Assert that __abstractmethods__ contains exactly get, save, and clear.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(
            IFileBasedCache.__abstractmethods__,
            frozenset({"get", "save", "clear"}),
        )

    def testPartialSubclassCannotBeInstantiated(self) -> None:
        """
        Assert that a subclass implementing only get cannot be instantiated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            _PartialFileBasedCache()  # type: ignore[abstract]

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Assert that a fully implemented subclass can be created without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteFileBasedCache()
        self.assertIsInstance(instance, IFileBasedCache)

    def testConcreteGetReturnsDict(self) -> None:
        """
        Assert that a concrete get implementation returns a dict.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteFileBasedCache()
        result = instance.get()
        self.assertIsInstance(result, dict)

    def testConcreteSaveReturnsVersionAndHash(self) -> None:
        """
        Assert that a concrete save implementation returns a (int, str) tuple.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteFileBasedCache()
        version, hash_str = instance.save({"x": 1})
        self.assertIsInstance(version, int)
        self.assertIsInstance(hash_str, str)

    def testConcreteClearReturnsBool(self) -> None:
        """
        Assert that a concrete clear implementation returns a bool.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteFileBasedCache()
        result = instance.clear()
        self.assertIsInstance(result, bool)

    def testGetMethodSignatureReturnsNoneOrDict(self) -> None:
        """
        Assert that get is annotated to return dict or None.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = inspect.signature(IFileBasedCache.get)
        self.assertIn("->", str(sig))
