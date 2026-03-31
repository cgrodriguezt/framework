from __future__ import annotations
from abc import ABC
from orionis.test import TestCase
from orionis.container.contracts.service_provider import IServiceProvider

class TestIServiceProvider(TestCase):

    # ------------------------------------------------------------------
    # Structural / ABC
    # ------------------------------------------------------------------

    def testIServiceProviderIsAbstractBaseClass(self) -> None:
        """
        Test that IServiceProvider is a subclass of ABC.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(issubclass(IServiceProvider, ABC))

    def testIServiceProviderCannotBeInstantiatedDirectly(self) -> None:
        """
        Test that direct instantiation of IServiceProvider raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            IServiceProvider()  # type: ignore[abstract]

    # ------------------------------------------------------------------
    # Abstract method presence
    # ------------------------------------------------------------------

    def testHasAbstractMethodRegister(self) -> None:
        """
        Test that 'register' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("register", IServiceProvider.__abstractmethods__)

    def testHasAbstractMethodBoot(self) -> None:
        """
        Test that 'boot' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("boot", IServiceProvider.__abstractmethods__)

    # ------------------------------------------------------------------
    # Concrete subclass
    # ------------------------------------------------------------------

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Test that a concrete subclass implementing both abstract methods
        can be instantiated without error.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _ConcreteProvider(IServiceProvider):
            def register(self) -> None: # NOSONAR
                pass

            async def boot(self) -> None: # NOSONAR
                pass

        obj = _ConcreteProvider()
        self.assertIsInstance(obj, IServiceProvider)

    def testRegisterIsCallable(self) -> None:
        """
        Test that register() is callable on a concrete subclass instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Provider(IServiceProvider):
            def register(self) -> None: # NOSONAR
                pass

            async def boot(self) -> None: # NOSONAR
                pass

        obj = _Provider()
        self.assertTrue(callable(obj.register))

    def testBootIsCallable(self) -> None:
        """
        Test that boot() is callable on a concrete subclass instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Provider(IServiceProvider):
            def register(self) -> None: # NOSONAR
                pass

            async def boot(self) -> None: # NOSONAR
                pass

        obj = _Provider()
        self.assertTrue(callable(obj.boot))

    def testRegisterMethodExecutesWithoutError(self) -> None:
        """
        Test that calling register() on a concrete provider runs without error.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _Provider(IServiceProvider):
            def register(self) -> None:
                self.called = True

            async def boot(self) -> None: # NOSONAR
                pass

        obj = _Provider()
        obj.register()
        self.assertTrue(obj.called)
