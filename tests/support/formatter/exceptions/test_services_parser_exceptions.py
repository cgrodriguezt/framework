from orionis.support.formatter.serializer import Parser
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.support.formatter.exceptions.mocks.mock_custom_error import CustomError

class TestServicesParserExceptions(AsyncTestCase):

    async def testBasicExceptionStructure(self):
        """
        Tests that the ExceptionParser correctly structures a basic exception.

        This method raises a ValueError and verifies that the serialized output
        from Parser.exception contains all expected fields and values.

        Returns
        -------
        None
            This test does not return anything. It asserts correctness of the exception structure.
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
        Tests that the raw_exception property returns the original exception object.

        This method raises a RuntimeError and checks that Parser.exception.raw_exception
        is the same object as the one raised.

        Returns
        -------
        None
            This test does not return anything. It asserts the raw exception property.
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
        Tests that exceptions with a custom error code are serialized correctly.

        This method raises a CustomError with a specific code and verifies that
        the serialized output contains the correct error code and type.

        Returns
        -------
        None
            This test does not return anything. It asserts error code serialization.
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
        Tests that the Parser.exception correctly handles nested exceptions.

        This method raises a ValueError as the original cause, then raises a TypeError
        from it, and verifies that the serialized output reflects the correct error type.

        Returns
        -------
        None
            This test does not return anything. It asserts nested exception handling.
        """
        try:
            try:
                # Raise the original exception
                raise ValueError("Original cause")
            except ValueError as exc:
                # Raise a new exception from the original
                raise TypeError("Outer error")
        except Exception as e:
            # Serialize the outer exception and check error_type
            result = Parser.exception(e).toDict()
            self.assertEqual(result["error_type"], "TypeError")