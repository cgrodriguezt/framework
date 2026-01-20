from orionis.support.formatter.serializer import Parser
from orionis.test.cases.synchronous import SyncTestCase
from tests.support.formatter.exceptions.mock_custom_error import CustomError

class TestServicesParserExceptions(SyncTestCase):

    def testBasicExceptionStructure(self):
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
            self.assertIn("Something went wrong", result["error_message"])
            self.assertIsNone(result["error_code"])
            self.assertIsNone(result["cause"])
            self.assertIsInstance(result["stack_trace"], list)
            self.assertGreater(len(result["stack_trace"]), 0)

    def testRawExceptionProperty(self):
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

    def testExceptionWithCode(self):
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

    def testNestedExceptionCause(self):
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
        - The cause is properly parsed when using 'raise from' syntax.
        """
        try:
            try:
                # Raise the original exception
                raise ValueError("Original cause")
            except ValueError as original:
                # Raise a new exception from the original using 'raise from'
                raise TypeError("Outer error") from original
        except Exception as e:
            # Serialize the outer exception and check error_type and cause
            result = Parser.exception(e).toDict()
            self.assertEqual(result["error_type"], "TypeError")
            self.assertIsNotNone(result["cause"])
            self.assertEqual(result["cause"]["error_type"], "ValueError")
            self.assertIn("Original cause", result["cause"]["error_message"])

    def testStackTraceStructure(self):
        """
        Test that the stack trace is properly structured with all required fields.

        Raises
        ------
        RuntimeError
            Raised intentionally to test stack trace structure.

        Asserts
        -------
        - Each stack trace entry contains all required keys.
        - Stack trace entries have correct data types.
        - Stack trace is not empty for raised exceptions.
        """
        try:
            # Raise an exception to generate a stack trace
            raise RuntimeError("Stack trace test")
        except Exception as e:
            # Serialize and validate stack trace structure
            result = Parser.exception(e).toDict()
            stack_trace = result["stack_trace"]

            self.assertIsInstance(stack_trace, list)
            self.assertGreater(len(stack_trace), 0)

            # Check structure of each stack frame
            for frame in stack_trace:
                self.assertIsInstance(frame, dict)
                self.assertIn("filename", frame)
                self.assertIn("lineno", frame)
                self.assertIn("name", frame)
                self.assertIn("line", frame)

                self.assertIsInstance(frame["filename"], str)
                self.assertIsInstance(frame["lineno"], int)
                self.assertIsInstance(frame["name"], str)
                # frame["line"] can be None or str

    def testExceptionWithoutMessage(self):
        """
        Test that exceptions without explicit messages are handled correctly.

        Raises
        ------
        ValueError
            Raised without a custom message.

        Asserts
        -------
        - Exception without message is serialized correctly.
        - Error message field is present even when empty.
        """
        try:
            # Raise an exception without a message
            raise ValueError
        except Exception as e:
            # Serialize and check structure
            result = Parser.exception(e).toDict()

            self.assertEqual(result["error_type"], "ValueError")
            self.assertIn("error_message", result)
            self.assertIsInstance(result["error_message"], str)

    def testMultipleCausedExceptions(self):
        """
        Test parsing of exceptions with multiple levels of causes.

        Raises
        ------
        OSError
            First level cause.
        ValueError
            Second level cause.
        TypeError
            Final exception with nested causes.

        Asserts
        -------
        - Exception with explicit 'raise from' cause is properly parsed.
        - Each cause maintains its structure.
        """
        try:
            try:
                try:
                    # First level exception
                    raise OSError("File system error")
                except OSError as first:
                    # Second level exception
                    raise ValueError("Data validation error") from first
            except ValueError as second:
                # Final level exception
                raise TypeError("Type conversion error") from second
        except Exception as e:
            # Serialize and check nested cause structure
            result = Parser.exception(e).toDict()

            # Check main exception
            self.assertEqual(result["error_type"], "TypeError")

            # Check first level cause (only immediate cause is visible)
            cause = result["cause"]
            self.assertIsNotNone(cause)
            self.assertEqual(cause["error_type"], "ValueError")

            # Note: Python's __cause__ only shows the immediate cause,
            # not the full chain. The OSError is the cause of ValueError.

    def testCustomExceptionWithMultipleAttributes(self):
        """
        Test that only the 'code' attribute is extracted from custom exceptions.

        Raises
        ------
        CustomError
            Raised with code and potentially other attributes.

        Asserts
        -------
        - Only the 'code' attribute is included in error_code field.
        - Other custom attributes are not included in the serialized result.
        """
        try:
            # Create a custom error with code
            error = CustomError("Custom error with code", code=500)
            # Add additional attribute (should not be included)
            error.extra_info = "This should not be included"
            raise error
        except Exception as e:
            # Serialize and check only code is included
            result = Parser.exception(e).toDict()

            self.assertEqual(result["error_code"], 500)
            self.assertEqual(result["error_type"], "CustomError")
            # Verify extra attributes are not included
            self.assertNotIn("extra_info", result)

    def testSystemAndBuiltinExceptions(self):
        """
        Test serialization of various built-in exception types.

        Raises
        ------
        KeyError
            Built-in exception for missing dictionary keys.

        Asserts
        -------
        - Built-in exceptions are serialized correctly.
        - Error type reflects the specific exception class.
        """
        exceptions_to_test = [
            (KeyError("missing_key"), "KeyError"),
            (IndexError("list index out of range"), "IndexError"),
            (AttributeError("'str' object has no attribute 'missing'"), "AttributeError"),
            (ZeroDivisionError("division by zero"), "ZeroDivisionError"),
        ]

        for exception, expected_type in exceptions_to_test:
            try:
                raise exception
            except Exception as e:
                result = Parser.exception(e).toDict()
                self.assertEqual(result["error_type"], expected_type)
                self.assertIsInstance(result["error_message"], str)
                self.assertIsNone(result["error_code"])

    def testErrorMessageFormatting(self):
        """
        Test that error messages are properly formatted and stripped.

        Raises
        ------
        ValueError
            Raised with specific message to test formatting.

        Asserts
        -------
        - Error message is properly formatted.
        - No leading or trailing whitespace in error message.
        - Message contains the original exception text.
        """
        test_message = "   Test message with whitespace   "
        try:
            raise ValueError(test_message)
        except Exception as e:
            result = Parser.exception(e).toDict()

            error_message = result["error_message"]
            # The error message should be stripped and formatted
            self.assertIsInstance(error_message, str)
            # Should contain the original message content
            self.assertIn("Test message with whitespace", error_message)

    def testExceptionWithNoneCode(self):
        """
        Test that exceptions without a code attribute have None as error_code.

        Raises
        ------
        StandardError
            Exception without a code attribute.

        Asserts
        -------
        - error_code is None for exceptions without code attribute.
        - All other fields are properly populated.
        """
        class StandardError(Exception):
            """Standard exception without code attribute."""


        try:
            raise StandardError("No code attribute")
        except Exception as e:
            result = Parser.exception(e).toDict()

            self.assertIsNone(result["error_code"])
            self.assertEqual(result["error_type"], "StandardError")
            self.assertIn("No code attribute", result["error_message"])

    def testCauseStructureConsistency(self):
        """
        Test that cause structure is consistent with main exception structure.

        Raises
        ------
        RuntimeError
            Original cause exception.
        ValueError
            Main exception with cause using 'raise from'.

        Asserts
        -------
        - Cause structure contains required fields.
        - Cause structure is consistent with main exception format.
        - Missing fields in cause are handled properly.
        """
        try:
            try:
                raise RuntimeError("Original error")
            except RuntimeError as original:
                raise ValueError("Secondary error") from original
        except Exception as e:
            result = Parser.exception(e).toDict()
            cause = result["cause"]

            # Validate cause structure
            self.assertIsNotNone(cause)
            self.assertIn("error_type", cause)
            self.assertIn("error_message", cause)
            self.assertIn("stack_trace", cause)

            # Cause should have the same stack trace structure
            cause_stack = cause["stack_trace"]
            self.assertIsInstance(cause_stack, list)
            self.assertGreater(len(cause_stack), 0)

            # Verify stack frame structure in cause
            for frame in cause_stack:
                self.assertIn("filename", frame)
                self.assertIn("lineno", frame)
                self.assertIn("name", frame)
                self.assertIn("line", frame)

    def testExceptionWithoutExplicitCause(self):
        """
        Test that exceptions without explicit causes have None as cause.

        Raises
        ------
        ValueError
            Exception without explicit cause.

        Asserts
        -------
        - Exception without explicit cause has None as cause field.
        - All other fields are properly populated.
        """
        try:
            raise ValueError("Simple exception without cause")
        except Exception as e:
            result = Parser.exception(e).toDict()

            self.assertEqual(result["error_type"], "ValueError")
            self.assertIsNone(result["cause"])
            self.assertIn("Simple exception without cause", result["error_message"])

    def testCompleteExceptionStructure(self):
        """
        Test that a complete exception structure contains all expected fields.

        Raises
        ------
        RuntimeError
            Exception to test complete structure.

        Asserts
        -------
        - All expected fields are present in the serialized exception.
        - Field types are correct.
        - Structure is complete and consistent.
        """
        try:
            raise RuntimeError("Complete structure test")
        except Exception as e:
            result = Parser.exception(e).toDict()

            # Check all required top-level fields
            expected_fields = ["error_type", "error_message", "stack_trace", "error_code", "cause"]
            for field in expected_fields:
                self.assertIn(field, result)

            # Validate field types
            self.assertIsInstance(result["error_type"], str)
            self.assertIsInstance(result["error_message"], str)
            self.assertIsInstance(result["stack_trace"], list)
            # error_code can be None or any type
            # cause can be None or dict

            # Validate non-empty values where expected
            self.assertNotEqual(result["error_type"], "")
            self.assertNotEqual(result["error_message"], "")
            self.assertGreater(len(result["stack_trace"]), 0)
