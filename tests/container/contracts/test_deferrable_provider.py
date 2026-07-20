from __future__ import annotations
from abc import ABC
from orionis.test import TestCase
from orionis.container.contracts.deferrable_provider import IDeferrableProvider

class TestIDeferrableProvider(TestCase):

    # ------------------------------------------------------------------
    # Structural / ABC
    # ------------------------------------------------------------------

    def testIDeferrableProviderIsAbstractBaseClass(self) -> None:
        """
        Test that IDeferrableProvider is a subclass of ABC.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(issubclass(IDeferrableProvider, ABC))

    def testIDeferrableProviderCannotBeInstantiatedDirectly(self) -> None:
        """
        Test that direct instantiation of IDeferrableProvider raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            IDeferrableProvider()  # type: ignore[abstract]

    # ------------------------------------------------------------------
    # Abstract method presence
    # ------------------------------------------------------------------

    def testHasAbstractMethodProvides(self) -> None:
        """
        Test that 'provides' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("provides", IDeferrableProvider.__abstractmethods__)

    # ------------------------------------------------------------------
    # Concrete subclass
    # ------------------------------------------------------------------

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Test that a concrete subclass that implements provides() can be created.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _ConcreteProvider(IDeferrableProvider):
            @classmethod
            def provides(cls) -> list[type]:
                return [str]

        obj = _ConcreteProvider()
        self.assertIsInstance(obj, IDeferrableProvider)

    def testProvidesReturnsExpectedList(self) -> None:
        """
        Test that provides() on the concrete subclass returns the declared types.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Provider(IDeferrableProvider):
            @classmethod
            def provides(cls) -> list[type]:
                return [int, str]

        self.assertEqual(_Provider.provides(), [int, str])

    def testProvidesCanReturnEmptyList(self) -> None:
        """
        Test that provides() is allowed to return an empty list.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _EmptyProvider(IDeferrableProvider):
            @classmethod
            def provides(cls) -> list[type]:
                return []

        self.assertEqual(_EmptyProvider.provides(), [])

    def testProvidesIsClassMethod(self) -> None:
        """
        Test that provides() can be called on the class without instantiation.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Provider(IDeferrableProvider):
            @classmethod
            def provides(cls) -> list[type]:
                return [float]

        result = _Provider.provides()
        self.assertIsInstance(result, list)
