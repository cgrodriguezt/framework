from orionis.container.validators.is_callable import IsCallable
from orionis.container.exceptions.type import OrionisContainerTypeError
from orionis.test.cases.test_case import TestCase

class TestIsCallable(TestCase):
    """
    Test cases for the IsCallable validator in orionis.container.validators.is_callable.

    Notes
    -----
    This test suite validates the functionality of the IsCallable validator
    which ensures that a provided value is callable.
    """

    async def testValidCallables(self) -> None:
        """
        Test that validation passes for valid callable objects.
        """
        def simple_function():
            pass

        class ClassWithCall:
            def __call__(self):
                pass

        lambda_func = lambda x: x

        # These should not raise exceptions
        IsCallable(simple_function)
        IsCallable(ClassWithCall())
        IsCallable(lambda_func)
        IsCallable(len)
        IsCallable(print)

    async def testNonCallables(self) -> None:
        """
        Test that validation fails for non-callable objects.
        """
        non_callables = [
            42,
            "string",
            [1, 2, 3],
            {"key": "value"},
            None,
            True,
            (1, 2, 3)
        ]

        for value in non_callables:
            with self.assertRaises(OrionisContainerTypeError) as context:
                IsCallable(value)
            expected_message = f"Expected a callable type, but got {type(value).__name__} instead."
            self.assertEqual(str(context.exception), expected_message)

    async def testClassesAsCallables(self) -> None:
        """
        Test that classes themselves are considered callable (since they can be instantiated).
        """
        class SimpleClass:
            pass

        # This should not raise an exception
        IsCallable(SimpleClass)

    async def testBuiltinFunctions(self) -> None:
        """
        Test that built-in functions are properly identified as callable.
        """
        # These should not raise exceptions
        IsCallable(sum)
        IsCallable(map)
        IsCallable(filter)
        IsCallable(sorted)
