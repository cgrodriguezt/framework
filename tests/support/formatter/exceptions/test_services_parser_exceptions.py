from orionis.support.formatter.serializer import Parser
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.support.formatter.exceptions.mocks.mock_custom_error import CustomError

class TestServicesParserExceptions(AsyncTestCase):

    async def testBasicExceptionStructure(self):
        """
        Test that the ExceptionParser structures a basic exception as expected.

        Raises
        ------
        ValueError
            Raised intentionally to test serialization.

        Asserts
        -------
        - The serialized exception is a dictionary.
        - The dictionary contains the keys: "error_type", "error_message", "stack_trace", "error_code", and "cause".
        - The "error_type" is "ValueError".
        - The "error_message" contains the raised message.
        - The "error_code" and "cause" are None.
        - The "stack_trace" is a non-empty list.
        """
        try:
            # Raise a basic exception
            raise ValueError("Something went wrong")
        except Exception as e:
            # Serialize the exception using Parser
            result = Parser.exception(e).toDict()

            # Check that the result is a dictionary and contains required keys
            self.assertIsInstance(result, dict)
            self.assertIn("error_type", result)
            self.assertIn("error_message", result)
            self.assertIn("stack_trace", result)
            self.assertIn("error_code", result)
            self.assertIn("cause", result)

            # Validate the values of the serialized exception
            self.assertEqual(result["error_type"], "ValueError")
            self.assertTrue("Something went wrong" in result["error_message"])
            self.assertIsNone(result["error_code"])
            self.assertIsNone(result["cause"])
            self.assertIsInstance(result["stack_trace"], list)
            self.assertGreater(len(result["stack_trace"]), 0)

    async def testRawExceptionProperty(self):
        """
        Test that the raw_exception property returns the original exception object.

        Raises
        ------
        RuntimeError
            Raised intentionally to test the raw_exception property.

        Asserts
        -------
        - The raw_exception property of the Parser instance is the same as the raised exception.
        """
        try:
            # Raise a RuntimeError
            raise RuntimeError("Test exception")
        except Exception as e:
            # Create a Parser instance and check raw_exception property
            parser = Parser.exception(e)
            self.assertIs(parser.raw_exception, e)

    async def testExceptionWithCode(self):
        """
        Test that exceptions with a custom error code are serialized correctly.

        Raises
        ------
        CustomError
            Raised with a specific code to test error code serialization.

        Asserts
        -------
        - The serialized exception contains the correct error code.
        - The error type matches the custom exception.
        """
        try:
            # Raise a CustomError with a custom code
            raise CustomError("Custom message", code=404)
        except Exception as e:
            # Serialize the exception and check error_code and error_type
            result = Parser.exception(e).toDict()
            self.assertEqual(result["error_code"], 404)
            self.assertEqual(result["error_type"], "CustomError")

    async def testNestedExceptionCause(self):
        """
        Test that the Parser.exception handles nested exceptions correctly.

        Raises
        ------
        ValueError
            Raised as the original cause.
        TypeError
            Raised from the original exception to test nested exception handling.

        Asserts
        -------
        - The serialized outer exception has the correct error type.
        """
        try:
            try:
                # Raise the original exception
                raise ValueError("Original cause")
            except ValueError:
                # Raise a new exception from the original
                raise TypeError("Outer error")
        except Exception as e:
            # Serialize the outer exception and check error_type
            result = Parser.exception(e).toDict()
            self.assertEqual(result["error_type"], "TypeError")