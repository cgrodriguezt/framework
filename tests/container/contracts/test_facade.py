from __future__ import annotations
from abc import ABC
from orionis.test import TestCase
from orionis.container.contracts.facade import IFacade

# ---------------------------------------------------------------------------
# Concrete stub — implements all abstract methods for structural tests
# ---------------------------------------------------------------------------

class _StubFacade(IFacade):
    """Minimal IFacade implementation used only for structural tests."""

    @classmethod
    def getFacadeAccessor(cls) -> str:  # NOSONAR
        return "stub"

    @classmethod
    async def resolve(cls, *_args: object, **_kwargs: object) -> object:  # NOSONAR
        return None

    @classmethod
    async def pin(cls) -> None:  # NOSONAR
        pass

    @classmethod
    def unpin(cls) -> None:  # NOSONAR
        pass

class TestIFacade(TestCase):

    # ------------------------------------------------------------------
    # Structural / ABC
    # ------------------------------------------------------------------

    def testIFacadeIsAbstractBaseClass(self) -> None:
        """
        Test that IFacade is a subclass of ABC.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(issubclass(IFacade, ABC))

    def testIFacadeCannotBeInstantiatedDirectly(self) -> None:
        """
        Test that direct instantiation of IFacade raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            IFacade()  # type: ignore[abstract]

    # ------------------------------------------------------------------
    # Abstract method presence
    # ------------------------------------------------------------------

    def testHasAbstractMethodGetFacadeAccessor(self) -> None:
        """
        Test that 'getFacadeAccessor' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("getFacadeAccessor", IFacade.__abstractmethods__)

    def testHasAbstractMethodResolve(self) -> None:
        """
        Test that 'resolve' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("resolve", IFacade.__abstractmethods__)

    def testHasAbstractMethodPin(self) -> None:
        """
        Test that 'pin' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("pin", IFacade.__abstractmethods__)

    def testHasAbstractMethodUnpin(self) -> None:
        """
        Test that 'unpin' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("unpin", IFacade.__abstractmethods__)

    def testAbstractMethodsMatchExpectedSet(self) -> None:
        """
        Test that IFacade declares exactly the expected set of abstract methods.

        Catches silent removals or unintended additions to the contract.

        Returns
        -------
        None
            This method does not return a value.
        """
        expected = frozenset({"getFacadeAccessor", "resolve", "pin", "unpin"})
        self.assertEqual(IFacade.__abstractmethods__, expected)

    # ------------------------------------------------------------------
    # Concrete subclass
    # ------------------------------------------------------------------

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Instantiate a concrete subclass implementing all abstract methods.

        Returns
        -------
        None
            This method does not return a value.
        """
        obj = _StubFacade()
        self.assertIsInstance(obj, IFacade)

    def testGetFacadeAccessorReturnsString(self) -> None:
        """
        Test that the overridden getFacadeAccessor returns the declared string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(_StubFacade.getFacadeAccessor(), "stub")

    def testGetFacadeAccessorIsCallableWithoutInstantiation(self) -> None:
        """
        Verify that getFacadeAccessor is callable without instantiation.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(callable(_StubFacade.getFacadeAccessor))

    def testUnpinIsCallableWithoutInstantiation(self) -> None:
        """
        Verify that unpin() is callable on the class without instantiation.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(callable(_StubFacade.unpin))

