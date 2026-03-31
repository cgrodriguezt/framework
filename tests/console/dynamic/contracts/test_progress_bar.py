from __future__ import annotations
import inspect
from orionis.console.dynamic.contracts.progress_bar import IProgressBar
from orionis.test import TestCase

class TestIProgressBar(TestCase):

    def testIsAbstractClass(self) -> None:
        """
        Verify that IProgressBar is an abstract class.

        Ensures that the interface declares abstract methods and cannot
        be instantiated directly without a concrete implementation.
        """
        self.assertTrue(inspect.isabstract(IProgressBar))

    def testCannotBeInstantiatedDirectly(self) -> None:
        """
        Ensure IProgressBar cannot be instantiated directly.

        Attempts to create an instance of the abstract class and expects
        a TypeError because abstract methods remain unimplemented.
        """
        with self.assertRaises(TypeError):
            IProgressBar()

    def testHasRequiredAbstractMethods(self) -> None:
        """
        Verify that IProgressBar declares exactly the expected abstract methods.

        Checks that start, advance, and finish are the only abstract
        methods defined on the interface.
        """
        self.assertEqual(IProgressBar.__abstractmethods__, {"start", "advance", "finish"})

    def testStartMethodSignature(self) -> None:
        """
        Verify the signature of the abstract start method.

        Ensures start accepts only self with no additional parameters,
        consistent with a zero-argument reset operation.
        """
        sig = inspect.signature(IProgressBar.start)
        self.assertEqual(len(sig.parameters), 1)
        self.assertIn("self", sig.parameters)

    def testAdvanceMethodSignature(self) -> None:
        """
        Verify the signature of the abstract advance method.

        Ensures advance accepts self plus an optional increment parameter
        with a default value of 1.
        """
        sig = inspect.signature(IProgressBar.advance)
        params = sig.parameters
        self.assertIn("increment", params)
        self.assertEqual(params["increment"].default, 1)

    def testFinishMethodSignature(self) -> None:
        """
        Verify the signature of the abstract finish method.

        Ensures finish accepts only self with no additional parameters,
        consistent with a zero-argument completion operation.
        """
        sig = inspect.signature(IProgressBar.finish)
        self.assertEqual(len(sig.parameters), 1)
        self.assertIn("self", sig.parameters)

    def testNoneOfTheMethodsAreCoroutines(self) -> None:
        """
        Verify that all three methods are synchronous.

        Ensures that start, advance, and finish are not declared as
        coroutine functions, since progress-bar rendering is synchronous.
        """
        self.assertFalse(inspect.iscoroutinefunction(IProgressBar.start))
        self.assertFalse(inspect.iscoroutinefunction(IProgressBar.advance))
        self.assertFalse(inspect.iscoroutinefunction(IProgressBar.finish))

    def testPartialSubclassCannotBeInstantiated(self) -> None:
        """
        Verify that a subclass implementing only some methods cannot be instantiated.

        Ensures that all three abstract methods must be implemented before
        a concrete instance can be created.
        """
        class Partial(IProgressBar):
            def start(self) -> None: # NOSONAR
                pass
            def advance(self, increment: int = 1) -> None: # NOSONAR
                pass
        with self.assertRaises(TypeError):
            Partial()

    def testFullConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Verify that a fully implemented subclass can be instantiated.

        Ensures that providing concrete implementations for all three
        abstract methods produces a valid instance.
        """
        class Concrete(IProgressBar):
            def start(self) -> None: # NOSONAR
                pass
            def advance(self, increment: int = 1) -> None: # NOSONAR
                pass
            def finish(self) -> None: # NOSONAR
                pass

        instance = Concrete()
        self.assertIsInstance(instance, IProgressBar)
