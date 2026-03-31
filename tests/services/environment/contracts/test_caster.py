from __future__ import annotations
import inspect
from abc import ABC
from inspect import isabstract
from orionis.services.environment.contracts.caster import IEnvironmentCaster
from orionis.test import TestCase

class _ConcreteCaster(IEnvironmentCaster):
    """Minimal concrete implementation used to verify the contract."""

    def get(self) -> object:
        return "raw_value"

    def to(self, type_hint) -> str:
        return f"str:{type_hint}"


class _PartialCaster(IEnvironmentCaster):
    """Subclass implementing only get — intentionally incomplete."""

    def get(self) -> object:
        return None

# ===========================================================================
# TestIEnvironmentCasterContract
# ===========================================================================

class TestIEnvironmentCasterContract(TestCase):

    def testInheritsFromABC(self) -> None:
        """
        Assert that IEnvironmentCaster inherits from ABC.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(issubclass(IEnvironmentCaster, ABC))

    def testIsAbstractClass(self) -> None:
        """
        Assert that inspect.isabstract identifies IEnvironmentCaster as abstract.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertTrue(isabstract(IEnvironmentCaster))

    def testCannotInstantiateDirectly(self) -> None:
        """
        Assert that instantiating IEnvironmentCaster directly raises TypeError.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            IEnvironmentCaster()  # type: ignore[abstract]

    def testGetIsAbstractMethod(self) -> None:
        """
        Assert that 'get' is declared as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("get", IEnvironmentCaster.__abstractmethods__)

    def testToIsAbstractMethod(self) -> None:
        """
        Assert that 'to' is declared as an abstract method.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertIn("to", IEnvironmentCaster.__abstractmethods__)

    def testAbstractMethodsSetContainsExactlyGetAndTo(self) -> None:
        """
        Assert that __abstractmethods__ contains exactly get and to.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        self.assertEqual(
            IEnvironmentCaster.__abstractmethods__,
            frozenset({"get", "to"}),
        )

    def testPartialSubclassCannotBeInstantiated(self) -> None:
        """
        Assert that a subclass missing 'to' cannot be instantiated.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        with self.assertRaises(TypeError):
            _PartialCaster()  # type: ignore[abstract]

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Assert that a fully implemented subclass can be created without error.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteCaster()
        self.assertIsInstance(instance, IEnvironmentCaster)

    def testConcreteGetReturnsObject(self) -> None:
        """
        Assert that a concrete get returns a value.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteCaster()
        result = instance.get()
        self.assertIsNotNone(result)

    def testConcreteToReturnsString(self) -> None:
        """
        Assert that a concrete to implementation returns a string.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        instance = _ConcreteCaster()
        result = instance.to("int")
        self.assertIsInstance(result, str)

    def testGetMethodSignatureDocumented(self) -> None:
        """
        Assert that the get method has a signature with parameters.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = inspect.signature(IEnvironmentCaster.get)
        self.assertIn("self", sig.parameters)

    def testToMethodAcceptsTypeHintParameter(self) -> None:
        """
        Assert that 'to' accepts a type_hint parameter.

        Returns
        -------
        None
            Raises AssertionError on failure.
        """
        sig = inspect.signature(IEnvironmentCaster.to)
        self.assertIn("type_hint", sig.parameters)
