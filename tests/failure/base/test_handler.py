from unittest.mock import MagicMock
from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.failure.base.handler import BaseExceptionHandler
from orionis.failure.entities.throwable import Throwable
from orionis.console.request.contracts.cli_request import ICLIRequest
from orionis.console.output.contracts.console import IConsole
from orionis.services.log.contracts.log_service import ILogger

class TestBaseExceptionHandler(AsyncTestCase):

    async def testDestructureExceptionBasic(self):
        """
        Test that destructureException correctly converts a basic exception into a Throwable object.

        This test verifies that the method can handle a simple ValueError with a message
        and properly extract all relevant information into a structured Throwable format.

        Returns
        -------
        None
            This method performs assertions to verify the correctness of the destructuring process.
        """
        handler = BaseExceptionHandler()
        exception = ValueError("Test error message")

        result = await handler.destructureException(exception)

        self.assertIsInstance(result, Throwable)
        self.assertEqual(result.classtype, ValueError)
        self.assertEqual(result.message, "Test error message")
        self.assertEqual(result.args, ("Test error message",))
        # For a basic exception without active traceback, it should be the formatted traceback
        self.assertIsNotNone(result.traceback)

    async def testDestructureExceptionWithMultipleArgs(self):
        """
        Test that destructureException handles exceptions with multiple arguments correctly.

        This test ensures that when an exception is raised with multiple arguments,
        all arguments are properly captured and stringified in the resulting Throwable.

        Returns
        -------
        None
            This method performs assertions to verify proper handling of multiple arguments.
        """
        handler = BaseExceptionHandler()
        exception = TypeError("Invalid type", 42, True)

        result = await handler.destructureException(exception)

        self.assertIsInstance(result, Throwable)
        self.assertEqual(result.classtype, TypeError)
        self.assertEqual(result.message, "Invalid type")
        self.assertEqual(result.args, ("Invalid type", "42", "True"))

    async def testDestructureExceptionWithNoArgs(self):
        """
        Test that destructureException handles exceptions with no arguments.

        This test ensures that when an exception has no arguments, the method
        provides a default empty string argument to maintain consistency.

        Returns
        -------
        None
            This method performs assertions to verify proper handling of argumentless exceptions.
        """
        handler = BaseExceptionHandler()
        exception = RuntimeError()
        # Clear the args to simulate an exception with no arguments
        exception.args = ()

        result = await handler.destructureException(exception)

        self.assertIsInstance(result, Throwable)
        self.assertEqual(result.classtype, RuntimeError)
        self.assertEqual(result.message, "")
        self.assertEqual(result.args, ("",))

    async def testDestructureExceptionWithTraceback(self):
        """
        Test that destructureException captures traceback information when available.

        This test verifies that when an exception has an associated traceback,
        it is properly captured in the resulting Throwable object.

        Returns
        -------
        None
            This method performs assertions to verify proper traceback handling.
        """
        handler = BaseExceptionHandler()

        try:
            raise ValueError("Exception with traceback")
        except ValueError as e:
            result = await handler.destructureException(e)

        self.assertIsInstance(result, Throwable)
        self.assertEqual(result.classtype, ValueError)
        self.assertEqual(result.message, "Exception with traceback")
        self.assertIsNotNone(result.traceback)

    async def testShouldIgnoreExceptionWithValidInput(self):
        """
        Test that shouldIgnoreException returns False for exceptions not in dont_catch list.

        This test verifies that the method correctly identifies exceptions that should
        be handled (not ignored) by checking against the dont_catch attribute.

        Returns
        -------
        None
            This method performs assertions to verify proper exception filtering logic.
        """
        handler = BaseExceptionHandler()
        exception = ValueError("Should not be ignored")

        result = await handler.shouldIgnoreException(exception)

        self.assertFalse(result)

    async def testShouldIgnoreExceptionWithIgnoredType(self):
        """
        Test that shouldIgnoreException returns True for exceptions in dont_catch list.

        This test verifies that exceptions listed in the dont_catch attribute
        are properly identified as exceptions that should be ignored.

        Returns
        -------
        None
            This method performs assertions to verify proper exception filtering for ignored types.
        """
        handler = BaseExceptionHandler()
        handler.dont_catch = [ValueError, TypeError]
        exception = ValueError("Should be ignored")

        result = await handler.shouldIgnoreException(exception)

        self.assertTrue(result)

    async def testShouldIgnoreExceptionWithInvalidInput(self):
        """
        Test that shouldIgnoreException raises TypeError for non-exception inputs.

        This test ensures that the method properly validates its input and raises
        a TypeError when provided with objects that are not exception instances.

        Returns
        -------
        None
            This method performs assertions to verify proper input validation.
        """
        handler = BaseExceptionHandler()

        with self.assertRaises(TypeError) as context:
            await handler.shouldIgnoreException("not an exception")

        self.assertIn("Expected BaseException", str(context.exception))

    async def testReportWithValidException(self):
        """
        Test that report method correctly logs exception information and returns Throwable.

        This test verifies that the report method properly logs the exception details
        using the provided logger and returns the structured Throwable object.

        Returns
        -------
        None
            This method performs assertions to verify proper exception reporting functionality.
        """
        handler = BaseExceptionHandler()
        mock_logger = MagicMock(spec=ILogger)
        exception = ValueError("Test exception for reporting")

        result = await handler.report(exception, mock_logger)

        self.assertIsInstance(result, Throwable)
        self.assertEqual(result.classtype, ValueError)
        self.assertEqual(result.message, "Test exception for reporting")
        mock_logger.error.assert_called_once_with("[ValueError] Test exception for reporting")

    async def testReportWithInvalidException(self):
        """
        Test that report method raises TypeError for non-exception inputs.

        This test ensures that the report method properly validates its input
        and raises a TypeError when provided with invalid exception objects.

        Returns
        -------
        None
            This method performs assertions to verify proper input validation in report method.
        """
        handler = BaseExceptionHandler()
        mock_logger = MagicMock(spec=ILogger)

        with self.assertRaises(TypeError) as context:
            await handler.report("not an exception", mock_logger)

        self.assertIn("Expected BaseException", str(context.exception))

    async def testRenderCLIWithValidInputs(self):
        """
        Test that renderCLI correctly renders exception information to console.

        This test verifies that the renderCLI method properly logs the CLI error
        and outputs the exception information to the console with proper formatting.

        Returns
        -------
        None
            This method performs assertions to verify proper CLI rendering functionality.
        """
        handler = BaseExceptionHandler()
        mock_logger = MagicMock(spec=ILogger)
        mock_console = MagicMock(spec=IConsole)
        mock_request = MagicMock(spec=ICLIRequest)
        mock_request.arguments.return_value = {"arg1": "value1", "flag": True}

        exception = RuntimeError("CLI test exception")

        await handler.renderCLI(exception, mock_request, mock_logger, mock_console)

        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        self.assertIn("CLI Error: CLI test exception", error_call_args)
        self.assertIn("{'arg1': 'value1', 'flag': True}", error_call_args)

        mock_console.newLine.assert_called()
        mock_console.exception.assert_called_once_with(exception)
        # Verify newLine is called twice (before and after exception)
        self.assertEqual(mock_console.newLine.call_count, 2)

    async def testRenderCLIWithInvalidException(self):
        """
        Test that renderCLI raises TypeError for non-exception inputs.

        This test ensures that the renderCLI method properly validates the exception
        parameter and raises a TypeError when provided with invalid inputs.

        Returns
        -------
        None
            This method performs assertions to verify proper input validation in renderCLI.
        """
        handler = BaseExceptionHandler()
        mock_logger = MagicMock(spec=ILogger)
        mock_console = MagicMock(spec=IConsole)
        mock_request = MagicMock(spec=ICLIRequest)

        with self.assertRaises(TypeError) as context:
            await handler.renderCLI("not an exception", mock_request, mock_logger, mock_console)

        self.assertIn("Expected Exception", str(context.exception))

    async def testRenderCLIWithInvalidRequest(self):
        """
        Test that renderCLI raises TypeError for non-ICLIRequest inputs.

        This test ensures that the renderCLI method properly validates the request
        parameter and raises a TypeError when provided with invalid request objects.

        Returns
        -------
        None
            This method performs assertions to verify proper request validation in renderCLI.
        """
        handler = BaseExceptionHandler()
        mock_logger = MagicMock(spec=ILogger)
        mock_console = MagicMock(spec=IConsole)
        exception = ValueError("Test exception")

        with self.assertRaises(TypeError) as context:
            await handler.renderCLI(exception, "not a request", mock_logger, mock_console)

        self.assertIn("Expected ICLIRequest", str(context.exception))

    def testHandlerInheritsDontCatchAttribute(self):
        """
        Test that BaseExceptionHandler correctly initializes the dont_catch attribute.

        This test verifies that the handler has the dont_catch attribute properly
        initialized as an empty list by default, following the expected pattern.

        Returns
        -------
        None
            This method performs assertions to verify proper attribute initialization.
        """
        handler = BaseExceptionHandler()

        self.assertTrue(hasattr(handler, "dont_catch"))
        self.assertIsInstance(handler.dont_catch, list)
        self.assertEqual(len(handler.dont_catch), 0)

    async def testShouldIgnoreExceptionWithNoDontCatchAttribute(self):
        """
        Test that shouldIgnoreException handles a handler without dont_catch properly.

        This test creates a custom handler class without the dont_catch attribute
        to verify that the method returns False when the attribute is missing.

        Returns
        -------
        None
            This method performs assertions to verify graceful handling of missing attributes.
        """
        class HandlerWithoutDontCatch(BaseExceptionHandler):
            def __init__(self):
                # Deliberately not calling super().__init__() to avoid dont_catch
                pass

        handler = HandlerWithoutDontCatch()
        exception = ValueError("Test exception")

        result = await handler.shouldIgnoreException(exception)

        self.assertFalse(result)

    async def testDestructureExceptionPreservesOriginalArgs(self):
        """
        Test that destructureException preserves the original exception arguments.

        This test verifies that the original exception arguments are maintained
        in their converted string format without losing any information.

        Returns
        -------
        None
            This method performs assertions to verify argument preservation during destructuring.
        """
        handler = BaseExceptionHandler()
        original_args = ("Error message", 404, {"key": "value"})
        exception = Exception(*original_args)

        result = await handler.destructureException(exception)

        self.assertEqual(len(result.args), 3)
        self.assertEqual(result.args[0], "Error message")
        self.assertEqual(result.args[1], "404")
        self.assertEqual(result.args[2], "{'key': 'value'}")

    async def testReportLogsCorrectExceptionClass(self):
        """
        Test that report method logs the correct exception class name.

        This test verifies that different exception types are correctly identified
        and logged with their proper class names in the error message.

        Returns
        -------
        None
            This method performs assertions to verify correct exception class logging.
        """
        handler = BaseExceptionHandler()
        mock_logger = MagicMock(spec=ILogger)

        # Test with different exception types
        exceptions = [
            (ValueError("value error"), "ValueError"),
            (TypeError("type error"), "TypeError"),
            (RuntimeError("runtime error"), "RuntimeError"),
            (KeyError("key error"), "KeyError"),
        ]

        for exception, expected_class in exceptions:
            mock_logger.reset_mock()
            await handler.report(exception, mock_logger)
            expected_message = f"[{expected_class}] {exception.args[0]}"
            mock_logger.error.assert_called_once_with(expected_message)
