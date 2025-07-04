from abc import ABC, abstractmethod
import unittest.mock
from orionis.container.validators.is_abstract_class import IsAbstractClass
from orionis.container.exceptions.type import OrionisContainerTypeError
from orionis.unittesting import TestCase

class TestIsAbstractClass(TestCase):
    """
    Test cases for the IsAbstractClass validator in orionis.container.validators.is_abstract_class.

    Notes
    -----
    This test suite validates the functionality of the IsAbstractClass validator
    which ensures that a provided class is an abstract class.
    """

    async def testValidAbstractClass(self) -> None:
        """
        Test that validation passes for valid abstract classes.
        """
        # Create abstract class
        class AbstractBase(ABC):
            @abstractmethod
            def abstract_method(self):
                pass

        # Should pass without raising an exception
        with unittest.mock.patch('orionis.services.introspection.abstract.reflection.ReflectionAbstract.ensureIsAbstractClass') as mock_ensure:
            IsAbstractClass(AbstractBase, "singleton")
            mock_ensure.assert_called_once_with(AbstractBase)

    async def testNonAbstractClass(self) -> None:
        """
        Test that validation fails for non-abstract classes.
        """
        class ConcreteClass:
            def some_method(self):
                pass

        # Mock the ensureIsAbstractClass to raise an exception
        with unittest.mock.patch('orionis.services.introspection.abstract.reflection.ReflectionAbstract.ensureIsAbstractClass', 
                                side_effect=ValueError("Not an abstract class")) as mock_ensure:
            with self.assertRaises(OrionisContainerTypeError) as context:
                IsAbstractClass(ConcreteClass, "scoped")

            self.assertIn("Unexpected error registering scoped service", str(context.exception))
            mock_ensure.assert_called_once_with(ConcreteClass)

    async def testWithInheritedAbstractClass(self) -> None:
        """
        Test validation with classes that inherit from abstract classes but are still abstract.
        """
        class BaseAbstract(ABC):
            @abstractmethod
            def method1(self):
                pass

        class DerivedAbstract(BaseAbstract):
            @abstractmethod
            def method2(self):
                pass

        # Should pass if the derived class is still abstract
        with unittest.mock.patch('orionis.services.introspection.abstract.reflection.ReflectionAbstract.ensureIsAbstractClass') as mock_ensure:
            IsAbstractClass(DerivedAbstract, "transient")
            mock_ensure.assert_called_once_with(DerivedAbstract)

    async def testWithConcreteImplementation(self) -> None:
        """
        Test validation with concrete implementations of abstract classes.
        """
        class BaseAbstract(ABC):
            @abstractmethod
            def method(self):
                pass

        class ConcreteImplementation(BaseAbstract):
            def method(self):
                return "Implemented"

        # Should fail since ConcreteImplementation is not abstract
        with unittest.mock.patch('orionis.services.introspection.abstract.reflection.ReflectionAbstract.ensureIsAbstractClass', 
                               side_effect=TypeError("Not an abstract class")) as mock_ensure:
            with self.assertRaises(OrionisContainerTypeError) as context:
                IsAbstractClass(ConcreteImplementation, "singleton")

            self.assertIn("Unexpected error registering singleton service", str(context.exception))
            mock_ensure.assert_called_once_with(ConcreteImplementation)

    async def testWithNonClassTypes(self) -> None:
        """
        Test validation with values that aren't classes at all.
        """
        # Test with primitive types
        for invalid_value in [1, "string", [], {}, lambda: None]:
            with unittest.mock.patch('orionis.services.introspection.abstract.reflection.ReflectionAbstract.ensureIsAbstractClass', 
                                   side_effect=TypeError(f"{type(invalid_value)} is not a class")) as mock_ensure:
                with self.assertRaises(OrionisContainerTypeError):
                    IsAbstractClass(invalid_value, "transient")
