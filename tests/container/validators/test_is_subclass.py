from abc import ABC
from orionis.container.validators.is_subclass import IsSubclass
from orionis.container.exceptions.container_exception import OrionisContainerException
from orionis.test.cases.test_case import TestCase

class TestIsSubclass(TestCase):
    """
    Test cases for the IsSubclass validator in orionis.container.validators.is_subclass.

    Notes
    -----
    This test suite validates the functionality of the IsSubclass validator
    which ensures that a concrete class is a subclass of an abstract class.
    """

    async def testValidSubclass(self) -> None:
        """
        Test that validation passes when concrete class is a valid subclass.
        """
        # Define test classes
        class AbstractClass(ABC):
            pass

        class ConcreteClass(AbstractClass):
            pass

        class SubConcreteClass(ConcreteClass):
            pass

        # These should not raise exceptions
        IsSubclass(AbstractClass, ConcreteClass)
        IsSubclass(AbstractClass, SubConcreteClass)
        IsSubclass(ConcreteClass, SubConcreteClass)

    async def testInvalidSubclass(self) -> None:
        """
        Test that validation fails when concrete class is not a subclass.
        """
        # Define test classes
        class AbstractClass1(ABC):
            pass

        class AbstractClass2(ABC):
            pass

        class ConcreteClass1(AbstractClass1):
            pass

        class ConcreteClass2(AbstractClass2):
            pass

        # These should raise exceptions
        with self.assertRaises(OrionisContainerException) as context:
            IsSubclass(AbstractClass1, AbstractClass2)
        self.assertIn("concrete class must inherit", str(context.exception))

        with self.assertRaises(OrionisContainerException) as context:
            IsSubclass(AbstractClass1, ConcreteClass2)
        self.assertIn("concrete class must inherit", str(context.exception))

        with self.assertRaises(OrionisContainerException) as context:
            IsSubclass(ConcreteClass1, AbstractClass1)
        self.assertIn("concrete class must inherit", str(context.exception))

    async def testSameClass(self) -> None:
        """
        Test validation when abstract and concrete are the same class.
        """
        class TestClass:
            pass

        # A class is considered a subclass of itself
        IsSubclass(TestClass, TestClass)

    async def testBuiltinTypes(self) -> None:
        """
        Test validation with built-in types.
        """
        # Valid subclass relationships
        IsSubclass(Exception, ValueError)
        IsSubclass(BaseException, Exception)

        # Invalid subclass relationships
        with self.assertRaises(OrionisContainerException):
            IsSubclass(ValueError, Exception)

        with self.assertRaises(OrionisContainerException):
            IsSubclass(int, str)

        with self.assertRaises(OrionisContainerException):
            IsSubclass(list, dict)

    async def testNonClassArguments(self) -> None:
        """
        Test validation with non-class arguments which should raise TypeError.
        """
        class TestClass:
            pass

        # These should raise TypeError when passed to issubclass()
        non_class_args = [
            None,
            123,
            "string",
            [],
            {},
            lambda x: x
        ]

        for arg in non_class_args:
            with self.assertRaises(TypeError):
                IsSubclass(TestClass, arg)

            with self.assertRaises(TypeError):
                IsSubclass(arg, TestClass)
