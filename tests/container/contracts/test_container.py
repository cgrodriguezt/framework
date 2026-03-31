from __future__ import annotations
from abc import ABC
from orionis.test import TestCase
from orionis.container.contracts.container import IContainer

class TestIContainer(TestCase):

    # ------------------------------------------------------------------
    # Structural / ABC
    # ------------------------------------------------------------------

    def testIContainerIsAbstractBaseClass(self) -> None:
        """
        Test that IContainer is a subclass of ABC.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(issubclass(IContainer, ABC))

    def testIContainerCannotBeInstantiatedDirectly(self) -> None:
        """
        Test that direct instantiation of IContainer raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            IContainer()  # type: ignore[abstract]

    # ------------------------------------------------------------------
    # Abstract method presence
    # ------------------------------------------------------------------

    def testHasAbstractMethodInstance(self) -> None:
        """
        Test that 'instance' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("instance", IContainer.__abstractmethods__)

    def testHasAbstractMethodTransient(self) -> None:
        """
        Test that 'transient' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("transient", IContainer.__abstractmethods__)

    def testHasAbstractMethodSingleton(self) -> None:
        """
        Test that 'singleton' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("singleton", IContainer.__abstractmethods__)

    def testHasAbstractMethodScoped(self) -> None:
        """
        Test that 'scoped' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("scoped", IContainer.__abstractmethods__)

    def testHasAbstractMethodBound(self) -> None:
        """
        Test that 'bound' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("bound", IContainer.__abstractmethods__)

    def testHasAbstractMethodBeginScope(self) -> None:
        """
        Test that 'beginScope' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("beginScope", IContainer.__abstractmethods__)

    def testHasAbstractMethodGetCurrentScope(self) -> None:
        """
        Test that 'getCurrentScope' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("getCurrentScope", IContainer.__abstractmethods__)

    def testHasAbstractMethodMake(self) -> None:
        """
        Test that 'make' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("make", IContainer.__abstractmethods__)

    def testHasAbstractMethodBuild(self) -> None:
        """
        Test that 'build' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("build", IContainer.__abstractmethods__)

    def testHasAbstractMethodInvoke(self) -> None:
        """
        Test that 'invoke' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("invoke", IContainer.__abstractmethods__)

    def testHasAbstractMethodCall(self) -> None:
        """
        Test that 'call' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("call", IContainer.__abstractmethods__)

    # ------------------------------------------------------------------
    # Concrete subclass can be instantiated once all methods are defined
    # ------------------------------------------------------------------

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Test that a concrete subclass implementing all abstract methods
        can be instantiated without error.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _ConcreteContainer(IContainer):
            def instance(self, abstract, instance, *, alias=None, override=False):  # type: ignore[override]
                return True
            def transient(self, abstract, concrete, *, alias=None, override=False):  # type: ignore[override]
                return True
            def singleton(self, abstract, concrete, *, alias=None, override=False):  # type: ignore[override]
                return True
            def scoped(self, abstract, concrete, *, alias=None, override=False):  # type: ignore[override]
                return True
            def bound(self, key):  # type: ignore[override]
                return False
            def beginScope(self):  # type: ignore[override]
                return None
            def getCurrentScope(self):  # type: ignore[override]
                return None
            async def make(self, key, *args, **kwargs):  # type: ignore[override]
                return None
            async def build(self, type_, *args, **kwargs):  # type: ignore[override]
                return None
            async def invoke(self, fn, *args, **kwargs):  # type: ignore[override]
                return None
            async def call(self, instance, method_name, *args, **kwargs):  # type: ignore[override]
                return None

        obj = _ConcreteContainer()
        self.assertIsInstance(obj, IContainer)
