from __future__ import annotations
import inspect
from orionis.console.fluent.contracts.command import ICommand
from orionis.test import TestCase

class TestICommand(TestCase):

    def testIsAbstractClass(self) -> None:
        """
        Verify that ICommand is an abstract class.

        Ensures the interface defines abstract methods and cannot be
        instantiated directly without a concrete implementation.
        """
        self.assertTrue(inspect.isabstract(ICommand))

    def testCannotBeInstantiatedDirectly(self) -> None:
        """
        Ensure ICommand cannot be instantiated directly.

        Attempts to create an instance of the abstract class and expects
        a TypeError because abstract methods are unimplemented.
        """
        with self.assertRaises(TypeError):
            ICommand()

    def testHasRequiredAbstractMethods(self) -> None:
        """
        Verify that ICommand declares exactly the expected abstract methods.

        Checks that timestamp, description, arguments, and get are all
        listed as abstract methods on the interface.
        """
        self.assertEqual(
            ICommand.__abstractmethods__,
            {"timestamp", "description", "arguments", "get"},
        )

    def testTimestampMethodSignature(self) -> None:
        """
        Verify the signature of the abstract timestamp method.

        Ensures timestamp accepts self plus a keyword-only `enabled`
        parameter with a default value of True.
        """
        sig = inspect.signature(ICommand.timestamp)
        params = sig.parameters
        self.assertIn("enabled", params)
        self.assertEqual(params["enabled"].default, True)
        self.assertEqual(
            params["enabled"].kind,
            inspect.Parameter.KEYWORD_ONLY,
        )

    def testDescriptionMethodSignature(self) -> None:
        """
        Verify the signature of the abstract description method.

        Ensures description accepts self and a positional `desc`
        parameter with no default value.
        """
        sig = inspect.signature(ICommand.description)
        params = sig.parameters
        self.assertIn("desc", params)
        self.assertEqual(params["desc"].default, inspect.Parameter.empty)

    def testArgumentsMethodSignature(self) -> None:
        """
        Verify the signature of the abstract arguments method.

        Ensures arguments accepts self and a positional `args`
        parameter with no default value.
        """
        sig = inspect.signature(ICommand.arguments)
        params = sig.parameters
        self.assertIn("args", params)

    def testGetMethodSignature(self) -> None:
        """
        Verify the signature of the abstract get method.

        Ensures get accepts only self, returning control to the caller
        without requiring additional arguments.
        """
        sig = inspect.signature(ICommand.get)
        self.assertEqual(len(sig.parameters), 1)
        self.assertIn("self", sig.parameters)

    def testNoneOfTheMethodsAreCoroutines(self) -> None:
        """
        Verify that all abstract methods are synchronous.

        Ensures none of the interface methods are declared as coroutine
        functions, since fluent command configuration is synchronous.
        """
        for name in ("timestamp", "description", "arguments", "get"):
            self.assertFalse(
                inspect.iscoroutinefunction(getattr(ICommand, name)),
                msg=f"{name} should not be a coroutine",
            )

    def testPartialSubclassCannotBeInstantiated(self) -> None:
        """
        Verify that a subclass implementing only some methods cannot be instantiated.

        Ensures that all four abstract methods must be implemented before
        a concrete instance can be created.
        """
        class Partial(ICommand):
            def timestamp(self, *, enabled: bool = True):
                return self
            def description(self, desc: str):
                return self

        with self.assertRaises(TypeError):
            Partial()

    def testFullConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Verify that a fully implemented subclass can be instantiated.

        Ensures that providing concrete bodies for all four abstract
        methods produces a valid instance.
        """
        class Concrete(ICommand):
            def timestamp(self, *, enabled: bool = True):
                return self
            def description(self, desc: str):
                return self
            def arguments(self, args: list):
                return self
            def get(self):
                return ("sig", None)

        instance = Concrete()
        self.assertIsInstance(instance, ICommand)
