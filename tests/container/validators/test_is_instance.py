from abc import ABC, abstractmethod
from orionis.container.validators.is_instance import IsInstance
from orionis.container.exceptions.type import OrionisContainerTypeError
from orionis.test.cases.case import TestCase

class TestIsInstance(TestCase):
    """
    Test cases for the IsInstance validator in orionis.container.validators.is_instance.

    Notes
    -----
    This test suite validates the functionality of the IsInstance validator
    which ensures that a provided object is a valid instance (not a class or abstract type).
    """

    async def testValidInstances(self) -> None:
        """
        Test that validation passes for valid instances.
        """

        # Custom class instances
        class SimpleClass:
            pass

        # Class with __init__ method
        class ClassWithInit:
            def __init__(self, value):
                self.value = value

        IsInstance(SimpleClass())
        IsInstance(ClassWithInit(42))

    async def testInvalidClasses(self) -> None:
        """
        Test that validation fails when provided with classes instead of instances.
        """
        with self.assertRaises(OrionisContainerTypeError) as context:
            IsInstance(str)
        self.assertIn("Error registering instance", str(context.exception))

        class TestClass:
            pass

        with self.assertRaises(OrionisContainerTypeError) as context:
            IsInstance(TestClass)
        self.assertIn("Error registering instance", str(context.exception))

    async def testAbstractClasses(self) -> None:
        """
        Test that validation fails for abstract classes and their types.
        """
        class AbstractBase(ABC):
            @abstractmethod
            def abstract_method(self):
                pass

        class ConcreteImplementation(AbstractBase):
            def abstract_method(self):
                return "Implemented"

        # Abstract class should fail
        with self.assertRaises(OrionisContainerTypeError) as context:
            IsInstance(AbstractBase)
        self.assertIn("Error registering instance", str(context.exception))

        # But instance of concrete implementation should pass
        IsInstance(ConcreteImplementation())

    async def testTypeObjects(self) -> None:
        """
        Test validation with various type objects.
        """
        with self.assertRaises(OrionisContainerTypeError):
            IsInstance(type)

        with self.assertRaises(OrionisContainerTypeError):
            IsInstance(int)

        with self.assertRaises(OrionisContainerTypeError):
            IsInstance(list)

    async def testNoneValue(self) -> None:
        """
        Test validation with None value.
        """
        # None is a valid instance in Python
        with self.assertRaises(OrionisContainerTypeError):
            IsInstance(None)

    async def testCallables(self) -> None:
        """
        Test validation with callable objects.
        """
        # Functions and lambdas are valid instances
        def test_function():
            pass

        # Lambda functions are also valid instances
        with self.assertRaises(OrionisContainerTypeError):
            IsInstance(test_function)
            IsInstance(lambda x: x * 2)

        # But their types are not
        with self.assertRaises(OrionisContainerTypeError):
            IsInstance(type(test_function))
