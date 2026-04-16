from __future__ import annotations
import inspect
from abc import ABC
from inspect import isabstract
from orionis.services.system.contracts.imports import IImports
from orionis.test import TestCase

class _ConcreteImports(IImports):
    """Minimal concrete implementation used to verify the contract."""

    def collect(self) -> IImports:
        return self

    def display(self) -> None: # NOSONAR
        pass

    def clear(self) -> None: # NOSONAR
        pass

class _PartialImports(IImports):
    """Subclass implementing only collect — intentionally incomplete."""

    def collect(self) -> IImports:
        return self

# ===========================================================================
# TestIImportsContract
# ===========================================================================

class TestIImportsContract(TestCase):

    def testInheritsFromABC(self) -> None:
        """
        Assert that IImports inherits from ABC.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(issubclass(IImports, ABC))

    def testIsAbstractClass(self) -> None:
        """
        Assert that inspect.isabstract identifies IImports as abstract.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(isabstract(IImports))

    def testCannotInstantiateDirectly(self) -> None:
        """
        Assert that instantiating IImports directly raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            IImports()  # type: ignore[abstract]

    def testCollectIsAbstractMethod(self) -> None:
        """
        Assert that 'collect' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("collect", IImports.__abstractmethods__)

    def testDisplayIsAbstractMethod(self) -> None:
        """
        Assert that 'display' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("display", IImports.__abstractmethods__)

    def testClearIsAbstractMethod(self) -> None:
        """
        Assert that 'clear' is present in __abstractmethods__.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("clear", IImports.__abstractmethods__)

    def testAbstractMethodsContainsThreeMembers(self) -> None:
        """
        Assert that __abstractmethods__ contains exactly collect, display, clear.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(
            IImports.__abstractmethods__,
            frozenset({"collect", "display", "clear"}),
        )

    def testPartialSubclassCannotBeInstantiated(self) -> None:
        """
        Assert that a subclass missing display and clear cannot be instantiated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            _PartialImports()  # type: ignore[abstract]

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Assert that a fully implemented subclass can be created without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteImports()
        self.assertIsInstance(instance, IImports)

    def testConcreteCollectReturnsSelf(self) -> None:
        """
        Assert that a concrete collect returns an IImports instance.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteImports()
        result = instance.collect()
        self.assertIsInstance(result, IImports)

    def testConcreteDisplayDoesNotRaise(self) -> None:
        """
        Assert that a concrete display runs without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteImports()
        instance.display()

    def testConcreteClearDoesNotRaise(self) -> None:
        """
        Assert that a concrete clear runs without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteImports()
        instance.clear()

    def testCollectMethodSignatureIsValid(self) -> None:
        """
        Assert that collect has a valid signature with self.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = inspect.signature(IImports.collect)
        self.assertIn("self", sig.parameters)
