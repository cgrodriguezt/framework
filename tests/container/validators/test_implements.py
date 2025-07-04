from abc import ABC, abstractmethod
from orionis.unittesting import TestCase
from orionis.container.validators.implements import ImplementsAbstractMethods
from orionis.container.exceptions.exception import OrionisContainerException

class TestImplementsAbstractMethods(TestCase):
    """
    Test cases for the ImplementsAbstractMethods validator in orionis.container.validators.implements.

    Notes
    -----
    This test suite validates the functionality of the ImplementsAbstractMethods validator
    which ensures that concrete classes correctly implement abstract methods.
    """

    async def asyncSetUp(self) -> None:
        """
        Set up test fixtures.
        """
        # Define abstract classes for testing
        class AbstractBase(ABC):
            @abstractmethod
            def abstract_method(self) -> None:
                pass

            @abstractmethod
            def another_abstract_method(self) -> str:
                pass

        class ConcreteCorrect(AbstractBase):
            def abstract_method(self) -> None:
                pass

            def another_abstract_method(self) -> str:
                return "implemented"

        class ConcreteIncomplete(AbstractBase):
            def abstract_method(self) -> None:
                pass

        class NonAbstractBase:
            def regular_method(self) -> None:
                pass

        self.AbstractBase = AbstractBase
        self.ConcreteCorrect = ConcreteCorrect
        self.ConcreteIncomplete = ConcreteIncomplete
        self.NonAbstractBase = NonAbstractBase

    async def testValidImplementation(self) -> None:
        """
        Test that validation passes when all abstract methods are implemented.
        """
        # Test with class
        ImplementsAbstractMethods(
            abstract=self.AbstractBase,
            concrete=self.ConcreteCorrect
        )

        # Test with instance
        instance = self.ConcreteCorrect()
        ImplementsAbstractMethods(
            abstract=self.AbstractBase,
            instance=instance
        )

    async def testIncompleteImplementation(self) -> None:
        """
        Test that validation fails when not all abstract methods are implemented.
        """
        # Test with class
        with self.assertRaises(OrionisContainerException) as context:
            ImplementsAbstractMethods(
                abstract=self.AbstractBase,
                concrete=self.ConcreteIncomplete
            )

        self.assertIn("does not implement the following abstract methods", str(context.exception))
        self.assertIn("another_abstract_method", str(context.exception))

        # Test with instance
        with self.assertRaises(TypeError):
            ImplementsAbstractMethods(
                abstract=self.AbstractBase,
                instance=self.ConcreteIncomplete()
            )

    async def testMissingAbstractClass(self) -> None:
        """
        Test that validation fails when no abstract class is provided.
        """
        with self.assertRaises(OrionisContainerException) as context:
            ImplementsAbstractMethods(
                concrete=self.ConcreteCorrect
            )

        self.assertIn("Abstract class must be provided", str(context.exception))

    async def testMissingConcreteImplementation(self) -> None:
        """
        Test that validation fails when neither concrete class nor instance is provided.
        """
        with self.assertRaises(OrionisContainerException) as context:
            ImplementsAbstractMethods(
                abstract=self.AbstractBase
            )

        self.assertIn("Either concrete class or instance must be provided", str(context.exception))

    async def testNonAbstractClass(self) -> None:
        """
        Test that validation fails when the provided abstract class has no abstract methods.
        """
        with self.assertRaises(OrionisContainerException) as context:
            ImplementsAbstractMethods(
                abstract=self.NonAbstractBase,
                concrete=self.ConcreteCorrect
            )

        self.assertIn("does not define any abstract methods", str(context.exception))

    async def testRenamedAbstractMethods(self) -> None:
        """
        Test handling of renamed abstract methods with class name prefixes.
        """
        # Define classes with renamed methods
        class AbstractWithPrefix(ABC):
            @abstractmethod
            def _AbstractWithPrefix_method(self) -> None:
                pass

        class ConcreteWithPrefix:
            def _ConcreteWithPrefix_method(self) -> None:
                pass

        # Should pass validation because the method is renamed according to class name
        ImplementsAbstractMethods(
            abstract=AbstractWithPrefix,
            concrete=ConcreteWithPrefix
        )