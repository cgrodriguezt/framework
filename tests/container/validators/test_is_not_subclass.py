from abc import ABC
from orionis.container.validators.is_not_subclass import IsNotSubclass
from orionis.container.exceptions.container_exception import OrionisContainerException
from orionis.test.cases.test_case import TestCase

class TestIsNotSubclass(TestCase):
    """
    Test cases for the IsNotSubclass validator in orionis.container.validators.is_not_subclass.

    Notes
    -----
    This test suite validates the functionality of the IsNotSubclass validator
    which ensures that a concrete class is NOT a subclass of an abstract class.
    """

    async def testValidNonSubclass(self) -> None:
        """
        Test that validation passes when concrete class is not a subclass.
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

        # These should not raise exceptions
        IsNotSubclass(AbstractClass1, AbstractClass2)
        IsNotSubclass(AbstractClass1, ConcreteClass2)
        IsNotSubclass(ConcreteClass1, AbstractClass1)
        IsNotSubclass(int, str)
        IsNotSubclass(list, dict)

    async def testInvalidNonSubclass(self) -> None:
        """
        Test that validation fails when concrete class IS a subclass.
        """
        # Define test classes
        class AbstractClass(ABC):
            pass

        class ConcreteClass(AbstractClass):
            pass

        class SubConcreteClass(ConcreteClass):
            pass

        # These should raise exceptions
        with self.assertRaises(OrionisContainerException) as context:
            IsNotSubclass(AbstractClass, ConcreteClass)
        self.assertIn("must NOT inherit", str(context.exception))

        with self.assertRaises(OrionisContainerException) as context:
            IsNotSubclass(AbstractClass, SubConcreteClass)
        self.assertIn("must NOT inherit", str(context.exception))

        with self.assertRaises(OrionisContainerException) as context:
            IsNotSubclass(ConcreteClass, SubConcreteClass)
        self.assertIn("must NOT inherit", str(context.exception))

    async def testSameClass(self) -> None:
        """
        Test validation when abstract and concrete are the same class.
        """
        class TestClass:
            pass

        # A class is considered a subclass of itself, so this should raise an exception
        with self.assertRaises(OrionisContainerException) as context:
            IsNotSubclass(TestClass, TestClass)
        self.assertIn("must NOT inherit", str(context.exception))

    async def testBuiltinTypes(self) -> None:
        """
        Test validation with built-in types.
        """
        # Valid non-subclass relationships
        IsNotSubclass(ValueError, Exception)
        IsNotSubclass(int, str)
        IsNotSubclass(list, dict)

        # Invalid non-subclass relationships (are actually subclasses)
        with self.assertRaises(OrionisContainerException):
            IsNotSubclass(Exception, ValueError)

        with self.assertRaises(OrionisContainerException):
            IsNotSubclass(BaseException, Exception)

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
                IsNotSubclass(TestClass, arg)

            with self.assertRaises(TypeError):
                IsNotSubclass(arg, TestClass)
