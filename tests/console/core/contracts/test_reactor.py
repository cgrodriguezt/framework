from __future__ import annotations
import inspect
from orionis.console.core.contracts.reactor import IReactor
from orionis.test import TestCase

class TestIReactor(TestCase):
    """Test suite for the IReactor abstract interface."""

    def testIsAbstractClass(self) -> None:
        """
        Verify that IReactor is an abstract class.

        Ensures that IReactor has abstract methods defined and cannot be
        instantiated directly without a concrete implementation.
        """
        self.assertTrue(inspect.isabstract(IReactor))

    def testCannotBeInstantiatedDirectly(self) -> None:
        """
        Ensure IReactor cannot be instantiated directly.

        Attempts to create an instance of the abstract class and expects a
        TypeError due to unimplemented abstract methods.
        """
        with self.assertRaises(TypeError):
            IReactor()

    def testHasRequiredAbstractMethods(self) -> None:
        """
        Verify that all required abstract methods are defined on IReactor.

        Checks that the interface declares the expected abstract methods:
        command, info, and call.
        """
        abstract_methods = IReactor.__abstractmethods__
        expected_methods = {"command", "info", "call"}
        self.assertEqual(abstract_methods, expected_methods)

    def testCommandMethodSignature(self) -> None:
        """
        Verify that the command method has the expected signature.

        Ensures the abstract method declares the correct parameters:
        self, signature, and handler.
        """
        sig = inspect.signature(IReactor.command)
        params = list(sig.parameters.keys())
        self.assertIn("signature", params)
        self.assertIn("handler", params)
        self.assertEqual(len(sig.parameters), 3)

    def testInfoMethodSignature(self) -> None:
        """
        Verify that the info method has the expected signature.

        Ensures the abstract method only declares self as its parameter,
        as no additional arguments are needed to retrieve command metadata.
        """
        sig = inspect.signature(IReactor.info)
        self.assertEqual(len(sig.parameters), 1)
        self.assertIn("self", sig.parameters)

    def testCallMethodSignature(self) -> None:
        """
        Verify that the call method has the expected signature.

        Ensures the abstract method declares the correct parameters:
        self, signature, and args with a default value of None.
        """
        sig = inspect.signature(IReactor.call)
        params = sig.parameters
        self.assertIn("signature", params)
        self.assertIn("args", params)
        self.assertEqual(len(params), 3)
        self.assertIsNone(params["args"].default)

    def testInfoIsAsyncMethod(self) -> None:
        """
        Verify that the info method is declared as a coroutine function.

        Ensures that info is defined as async to support non-blocking
        command metadata retrieval.
        """
        self.assertTrue(inspect.iscoroutinefunction(IReactor.info))

    def testCallIsAsyncMethod(self) -> None:
        """
        Verify that the call method is declared as a coroutine function.

        Ensures that call is defined as async to support non-blocking
        command execution.
        """
        self.assertTrue(inspect.iscoroutinefunction(IReactor.call))

    def testCommandIsNotAsyncMethod(self) -> None:
        """
        Verify that the command registration method is synchronous.

        Ensures that command is not a coroutine function, as command
        registration is a synchronous operation.
        """
        self.assertFalse(inspect.iscoroutinefunction(IReactor.command))

    def testConcreteSubclassMustImplementAllMethods(self) -> None:
        """
        Verify that a partial subclass cannot be instantiated.

        Ensures that any subclass that does not implement all abstract
        methods raises a TypeError on instantiation.
        """
        class PartialReactor(IReactor):
            def command(self, signature, handler): # NOSONAR
                pass

        with self.assertRaises(TypeError):
            PartialReactor()

    def testFullConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Verify that a fully implemented subclass can be instantiated.

        Ensures that a class implementing all abstract methods of IReactor
        can be successfully instantiated without errors.
        """
        class ConcreteReactor(IReactor):
            def command(self, signature, handler):
                return None

            async def info(self):
                return []

            async def call(self, signature, args=None):
                return 0

        instance = ConcreteReactor()
        self.assertIsInstance(instance, IReactor)
