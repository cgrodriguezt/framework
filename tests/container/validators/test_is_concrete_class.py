from abc import ABC, abstractmethod
from orionis.container.validators.is_concrete_class import IsConcreteClass
from orionis.container.exceptions.type_error_exception import OrionisContainerTypeError
from orionis.test.cases.test_case import TestCase

class TestIsConcreteClass(TestCase):
    """
    Test cases for the IsConcreteClass validator in orionis.container.validators.is_concrete_class.

    Notes
    -----
    This test suite validates the functionality of the IsConcreteClass validator
    which ensures that a provided class is a concrete (non-abstract) class.
    """

    async def testValidConcreteClasses(self) -> None:
        """
        Test that validation passes for valid concrete classes.
        """
        class SimpleClass:
            pass

        class ClassWithInit:
            def __init__(self, value):
                self.value = value

        # These should not raise exceptions
        IsConcreteClass(SimpleClass, "singleton")
        IsConcreteClass(ClassWithInit, "transient")

    async def testAbstractClasses(self) -> None:
        """
        Test that validation fails for abstract classes.
        """
        class AbstractBase(ABC):
            @abstractmethod
            def abstract_method(self):
                pass

        with self.assertRaises(OrionisContainerTypeError) as context:
            IsConcreteClass(AbstractBase, "scoped")
        self.assertIn("Unexpected error registering scoped service", str(context.exception))

    async def testNonClassTypes(self) -> None:
        """
        Test that validation fails for non-class types.
        """
        with self.assertRaises(OrionisContainerTypeError) as context:
            IsConcreteClass(42, "singleton")
        self.assertIn("Unexpected error registering singleton service", str(context.exception))

        with self.assertRaises(OrionisContainerTypeError) as context:
            IsConcreteClass("string", "scoped")
        self.assertIn("Unexpected error registering scoped service", str(context.exception))

        with self.assertRaises(OrionisContainerTypeError) as context:
            IsConcreteClass(lambda x: x, "transient")
        self.assertIn("Unexpected error registering transient service", str(context.exception))

    async def testInheritedConcreteClasses(self) -> None:
        """
        Test that validation passes for concrete classes that inherit from abstract classes.
        """
        class AbstractBase(ABC):
            @abstractmethod
            def abstract_method(self):
                pass

        class ConcreteImplementation(AbstractBase):
            def abstract_method(self):
                return "Implemented"

        # This should not raise an exception
        IsConcreteClass(ConcreteImplementation, "singleton")

    async def testPartialImplementations(self) -> None:
        """
        Test that validation fails for classes that don't implement all abstract methods.
        """
        class AbstractBase(ABC):
            @abstractmethod
            def method1(self):
                pass

            @abstractmethod
            def method2(self):
                pass

        class PartialImplementation(AbstractBase):
            def method1(self):
                return "Implemented"

            # method2 is not implemented

        with self.assertRaises(OrionisContainerTypeError) as context:
            IsConcreteClass(PartialImplementation, "scoped")
        self.assertIn("Unexpected error registering scoped service", str(context.exception))
