from __future__ import annotations
from abc import ABC
from typing import Any
from orionis.test import TestCase
from orionis.container.contracts.facade import IFacade

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

    def testHasAbstractMethodInit(self) -> None:
        """
        Test that 'init' is declared as an abstract method.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("init", IFacade.__abstractmethods__)

    # ------------------------------------------------------------------
    # Concrete subclass
    # ------------------------------------------------------------------

    def testConcreteSubclassCanBeInstantiated(self) -> None:
        """
        Test that a concrete subclass implementing init() can be created.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _ConcreteFacade(IFacade):
            @classmethod
            async def init(cls, *args: Any, **kwargs: Any) -> None: # NOSONAR
                pass

        obj = _ConcreteFacade()
        self.assertIsInstance(obj, IFacade)

    def testInitIsClassMethod(self) -> None:
        """
        Test that init is callable on the class without instantiation.

        Verifies that a concrete implementation of init() is accessible
        as a classmethod.

        Returns
        -------
        None
            This method does not return a value.
        """
        class _ConcreteFacade(IFacade):
            initialized: bool = False

            @classmethod
            async def init(cls, *args: Any, **kwargs: Any) -> None:
                cls.initialized = True

        self.assertTrue(callable(_ConcreteFacade.init))
