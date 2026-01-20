from unittest.mock import Mock, patch, MagicMock, call
from orionis.test.cases.synchronous import SyncTestCase
from orionis.test.output.printer import TestPrinter
from orionis.foundation.config.testing.enums.verbosity import VerbosityMode
from orionis.test.entities.result import TestResult
from orionis.test.enums import TestStatus

class TestTestingPrinter(SyncTestCase):

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Returns
        -------
        None
        """
        # Mock console patcher to avoid repeated mocking
        self.console_patcher = patch("orionis.test.output.printer.Console")
        self.mock_console_class = self.console_patcher.start()
        self.mock_console = Mock()
        self.mock_console.width = 80  # Set a numeric width for calculations
        self.mock_console_class.return_value = self.mock_console

        # Create printer instances with mocked console
        self.printer = TestPrinter()
        self.detailed_printer = TestPrinter(verbosity=VerbosityMode.DETAILED)
        self.minimal_printer = TestPrinter(verbosity=VerbosityMode.MINIMAL)
        self.silent_printer = TestPrinter(verbosity=VerbosityMode.SILENT)

    def tearDown(self):
        """
        Clean up test fixtures after each test method.

        Returns
        -------
        None
        """
        self.console_patcher.stop()

    def testConstructorWithDefaults(self):
        """
        Test the TestPrinter constructor with default parameters.

        Verifies that the constructor correctly initializes all internal attributes
        with their default values when no parameters are provided.

        Returns
        -------
        None
        """
        printer = TestPrinter()

        # Verify that the printer instance is created correctly
        self.assertIsInstance(printer, TestPrinter)
        self.assertEqual(printer._TestPrinter__verbosity, VerbosityMode.DETAILED.value)
        self.assertEqual(printer._TestPrinter__panel_title, "🧪 Orionis Framework - Component Test Suite")
        # Verify that the console was created (using our mock)
        self.assertIsNotNone(printer._TestPrinter__rich_console)

    def testConstructorWithCustomParameters(self):
        """
        Test the TestPrinter constructor with custom parameters.

        Verifies that the constructor correctly accepts and sets custom values
        for verbosity, title, and width parameters.

        Returns
        -------
        None
        """
        custom_title = "Custom Test Suite"
        custom_width = 50
        custom_verbosity = VerbosityMode.MINIMAL

        printer = TestPrinter(
            verbosity=custom_verbosity,
            title=custom_title,
            width=custom_width,
        )

        # Verify that custom parameters are set correctly
        self.assertEqual(printer._TestPrinter__verbosity, custom_verbosity.value)
        self.assertEqual(printer._TestPrinter__panel_title, custom_title)
        expected_width = int(printer._TestPrinter__rich_console.width * (custom_width / 100))
        self.assertEqual(printer._TestPrinter__panel_width, expected_width)

    def testConstructorWithInvalidVerbosity(self):
        """
        Test the TestPrinter constructor with invalid verbosity parameter.

        Verifies that the constructor raises a ValueError when an invalid
        verbosity type is provided.

        Returns
        -------
        None
        """
        with self.assertRaises(ValueError) as context:
            TestPrinter(verbosity="invalid")

        self.assertIn("verbosity", str(context.exception))

    def testConstructorWithInvalidWidth(self):
        """
        Test the TestPrinter constructor with invalid width parameter.

        Verifies that the constructor raises a ValueError when width is
        outside the valid range (10-100).

        Returns
        -------
        None
        """
        # Test width below minimum
        with self.assertRaises(ValueError) as context:
            TestPrinter(width=5)
        self.assertIn("width", str(context.exception))

        # Test width above maximum
        with self.assertRaises(ValueError) as context:
            TestPrinter(width=150)
        self.assertIn("width", str(context.exception))

    def testConstructorWithInvalidTitle(self):
        """
        Test the TestPrinter constructor with invalid title parameter.

        Verifies that the constructor raises a ValueError when a non-string
        title is provided.

        Returns
        -------
        None
        """
        with self.assertRaises(ValueError) as context:
            TestPrinter(title=123)

        self.assertIn("title", str(context.exception))

    def testMethodsExist(self):
        """
        Verify that all required methods are present in the TestPrinter class.

        This test checks whether each method listed in `required_methods`
        exists as an attribute of the TestPrinter class. An assertion error is raised
        if any required method is missing.

        Returns
        -------
        None
        """
        # List of method names that must exist in TestPrinter
        required_methods = [
            "print",
            "line",
            "zeroTestsMessage",
            "startMessage",
            "progressBar",
            "finishMessage",
            "executePanel",
            "linkWebReport",
            "summaryTable",
            "displayResults",
            "unittestResult",
        ]

        # Check each required method for existence in TestPrinter
        for method_name in required_methods:
            # Assert that the method exists in TestPrinter
            self.assertTrue(
                hasattr(TestPrinter, method_name),
                f"{method_name} does not exist",
            )

    def testPrintWithString(self):
        """
        Test the print method with string input.

        Verifies that the print method correctly outputs string values
        to the console when verbosity is not silent.

        Returns
        -------
        None
        """
        test_string = "Test message"
        self.detailed_printer.print(test_string)
        self.mock_console.print.assert_called_with(test_string)

    def testPrintWithList(self):
        """
        Test the print method with list input.

        Verifies that the print method correctly iterates through list items
        and prints each one separately.

        Returns
        -------
        None
        """
        test_list = ["Item 1", "Item 2", "Item 3"]
        self.detailed_printer.print(test_list)

        expected_calls = [call(item) for item in test_list]
        self.mock_console.print.assert_has_calls(expected_calls)

    def testPrintWithObject(self):
        """
        Test the print method with object input.

        Verifies that the print method converts objects to string
        before printing them.

        Returns
        -------
        None
        """
        test_object = {"key": "value"}
        self.detailed_printer.print(test_object)
        self.mock_console.print.assert_called_with(str(test_object))

    def testPrintWithSilentVerbosity(self):
        """
        Test the print method with silent verbosity.

        Verifies that the print method does not output anything
        when verbosity is set to SILENT.

        Returns
        -------
        None
        """
        self.silent_printer.print("Test message")
        self.mock_console.print.assert_not_called()

    def testLine(self):
        """
        Test the line method with default count.

        Verifies that the line method prints one blank line by default.

        Returns
        -------
        None
        """
        self.detailed_printer.line()
        self.mock_console.line.assert_called_once_with(1)

    def testLineWithCustomCount(self):
        """
        Test the line method with custom count.

        Verifies that the line method prints the specified number of blank lines.

        Returns
        -------
        None
        """
        self.detailed_printer.line(3)
        self.mock_console.line.assert_called_once_with(3)

    def testLineWithSilentVerbosity(self):
        """
        Test the line method with silent verbosity.

        Verifies that the line method does not output anything
        when verbosity is set to SILENT.

        Returns
        -------
        None
        """
        self.silent_printer.line()
        self.mock_console.line.assert_not_called()

    def testZeroTestsMessage(self):
        """
        Test the zeroTestsMessage method.

        Verifies that the method displays a styled panel indicating
        that no tests were found to execute.

        Returns
        -------
        None
        """
        self.detailed_printer.zeroTestsMessage()

        # Verify that print was called (for the panel) and line was called (for spacing)
        self.assertTrue(self.mock_console.print.called)
        self.mock_console.line.assert_called_with(1)

    def testZeroTestsMessageWithSilentVerbosity(self):
        """
        Test the zeroTestsMessage method with silent verbosity.

        Verifies that the method does not output anything
        when verbosity is set to SILENT.

        Returns
        -------
        None
        """
        # Reset the mock to avoid interference from setUp
        self.mock_console.reset_mock()
        self.silent_printer.zeroTestsMessage()

        self.mock_console.print.assert_not_called()
        self.mock_console.line.assert_not_called()

    @patch("orionis.test.output.printer.datetime")
    def testStartMessage(self, mock_datetime):
        """
        Test the startMessage method.

        Verifies that the method displays a formatted start message
        with test session details.

        Parameters
        ----------
        mock_datetime : Mock
            Mock of the datetime module.

        Returns
        -------
        None
        """
        mock_datetime.now.return_value.strftime.return_value = "2025-10-11 12:00:00"

        self.detailed_printer.startMessage(
            length_tests=10,
            execution_mode="parallel",
            max_workers=4,
        )

        # Verify that print and line were called
        self.assertTrue(self.mock_console.print.called)
        self.mock_console.line.assert_called_with(1)

    def testStartMessageSequential(self):
        """
        Test the startMessage method with sequential execution mode.

        Verifies that the method correctly formats the message
        for sequential execution mode.

        Returns
        -------
        None
        """
        self.detailed_printer.startMessage(
            length_tests=5,
            execution_mode="sequential",
            max_workers=1,
        )

        # Verify that print and line were called
        self.assertTrue(self.mock_console.print.called)
        self.mock_console.line.assert_called_with(1)

    def testStartMessageWithSilentVerbosity(self):
        """
        Test the startMessage method with silent verbosity.

        Verifies that the method does not output anything
        when verbosity is set to SILENT.

        Returns
        -------
        None
        """
        # Reset the mock to avoid interference from setUp
        self.mock_console.reset_mock()
        self.silent_printer.startMessage(
            length_tests=10,
            execution_mode="parallel",
            max_workers=4,
        )

        self.mock_console.print.assert_not_called()
        self.mock_console.line.assert_not_called()

    @patch("orionis.test.output.printer.Progress")
    def testProgressBar(self, mock_progress_class):
        """
        Test the progressBar method.

        Verifies that the method returns a properly configured
        Progress instance.

        Parameters
        ----------
        mock_progress_class : Mock
            Mock of the Progress class from rich library.

        Returns
        -------
        None
        """
        mock_progress = Mock()
        mock_progress_class.return_value = mock_progress

        result = self.detailed_printer.progressBar()

        # Verify that Progress was called with correct parameters
        self.assertTrue(mock_progress_class.called)
        self.assertEqual(result, mock_progress)

    @patch("orionis.test.output.printer.Progress")
    def testProgressBarWithMinimalVerbosity(self, mock_progress_class):
        """
        Test the progressBar method with minimal verbosity.

        Verifies that the progress bar is disabled when verbosity
        is MINIMAL or lower.

        Parameters
        ----------
        mock_progress_class : Mock
            Mock of the Progress class from rich library.

        Returns
        -------
        None
        """
        mock_progress = Mock()
        mock_progress_class.return_value = mock_progress

        # Call the method to trigger Progress instantiation
        self.minimal_printer.progressBar()

        # Verify that Progress was called with disable=True
        call_args = mock_progress_class.call_args
        self.assertTrue(call_args.kwargs.get("disable", False))

    def testFinishMessage(self):
        """
        Test the finishMessage method.

        Verifies that the method displays a final summary message
        with test execution details.

        Returns
        -------
        None
        """
        summary = {
            "failed": 2,
            "errors": 1,
            "total_time": 15.75,
        }

        self.detailed_printer.finishMessage(summary=summary)

        # Verify that print and line were called
        self.assertTrue(self.mock_console.print.called)
        self.mock_console.line.assert_called_with(1)

    def testFinishMessageWithAllTestsPassed(self):
        """
        Test the finishMessage method when all tests passed.

        Verifies that the method displays the correct status icon
        when there are no failures or errors.

        Returns
        -------
        None
        """
        summary = {
            "failed": 0,
            "errors": 0,
            "total_time": 10.50,
        }

        self.detailed_printer.finishMessage(summary=summary)

        # Verify that print and line were called
        self.assertTrue(self.mock_console.print.called)
        self.mock_console.line.assert_called_with(1)

    def testFinishMessageWithSilentVerbosity(self):
        """
        Test the finishMessage method with silent verbosity.

        Verifies that the method does not output anything
        when verbosity is set to SILENT.

        Returns
        -------
        None
        """
        # Reset the mock to avoid interference from setUp
        self.mock_console.reset_mock()
        summary = {
            "failed": 1,
            "errors": 0,
            "total_time": 5.25,
        }

        self.silent_printer.finishMessage(summary=summary)

        self.mock_console.print.assert_not_called()
        self.mock_console.line.assert_not_called()

    def testExecutePanelWithNonCallable(self):
        """
        Test the executePanel method with non-callable parameter.

        Verifies that the method raises a ValueError when the
        func parameter is not callable.

        Returns
        -------
        None
        """
        printer = TestPrinter()

        with self.assertRaises(ValueError) as context:
            printer.executePanel(func="not_callable")

        self.assertIn("callable", str(context.exception))

    @patch("orionis.test.output.printer.Live")
    def testExecutePanelWithLiveConsole(self, mock_live_class):
        """
        Test the executePanel method with live console enabled.

        Verifies that the method executes the callable within
        a Live context when live_console is True.

        Parameters
        ----------
        mock_live_class : Mock
            Mock of the Live class from rich library.

        Returns
        -------
        None
        """
        mock_live = MagicMock()
        mock_live_class.return_value = mock_live
        mock_func = Mock(return_value="test_result")

        result = self.detailed_printer.executePanel(func=mock_func, live_console=True)

        # Verify that the function was called and result was returned
        mock_func.assert_called_once()
        self.assertEqual(result, "test_result")
        mock_live_class.assert_called_once()

    def testExecutePanelWithoutLiveConsole(self):
        """
        Test the executePanel method with live console disabled.

        Verifies that the method executes the callable and prints
        a static panel when live_console is False.

        Returns
        -------
        None
        """
        mock_func = Mock(return_value="test_result")

        result = self.detailed_printer.executePanel(func=mock_func, live_console=False)

        # Verify that the function was called and result was returned
        mock_func.assert_called_once()
        self.assertEqual(result, "test_result")
        self.mock_console.print.assert_called()

    def testExecutePanelWithSilentVerbosity(self):
        """
        Test the executePanel method with silent verbosity.

        Verifies that the method executes the callable without
        any panel output when verbosity is SILENT.

        Returns
        -------
        None
        """
        # Reset the mock to avoid interference from setUp
        self.mock_console.reset_mock()
        mock_func = Mock(return_value="test_result")

        result = self.silent_printer.executePanel(func=mock_func)

        # Verify that the function was called and result was returned
        mock_func.assert_called_once()
        self.assertEqual(result, "test_result")
        self.mock_console.print.assert_not_called()

    def testLinkWebReport(self):
        """
        Test the linkWebReport method.

        Verifies that the method displays a styled message with
        the report path.

        Returns
        -------
        None
        """
        test_path = "/path/to/report.html"
        self.detailed_printer.linkWebReport(test_path)
        self.mock_console.print.assert_called()

    def testLinkWebReportWithSilentVerbosity(self):
        """
        Test the linkWebReport method with silent verbosity.

        Verifies that the method does not output anything
        when verbosity is set to SILENT.

        Returns
        -------
        None
        """
        # Reset the mock to avoid interference from setUp
        self.mock_console.reset_mock()
        test_path = "/path/to/report.html"
        self.silent_printer.linkWebReport(test_path)
        self.mock_console.print.assert_not_called()

    def testSummaryTable(self):
        """
        Test the summaryTable method.

        Verifies that the method displays a summary table with
        test execution statistics.

        Returns
        -------
        None
        """
        summary = {
            "total_tests": 10,
            "passed": 7,
            "failed": 2,
            "errors": 1,
            "skipped": 0,
            "total_time": 15.75,
            "success_rate": 70.0,
        }

        self.detailed_printer.summaryTable(summary)

        # Verify that print and line were called
        self.assertTrue(self.mock_console.print.called)
        self.mock_console.line.assert_called_with(1)

    def testSummaryTableWithSilentVerbosity(self):
        """
        Test the summaryTable method with silent verbosity.

        Verifies that the method does not output anything
        when verbosity is set to SILENT.

        Returns
        -------
        None
        """
        # Reset the mock to avoid interference from setUp
        self.mock_console.reset_mock()
        summary = {
            "total_tests": 10,
            "passed": 7,
            "failed": 2,
            "errors": 1,
            "skipped": 0,
            "total_time": 15.75,
            "success_rate": 70.0,
        }

        self.silent_printer.summaryTable(summary)

        self.mock_console.print.assert_not_called()
        self.mock_console.line.assert_not_called()

    @patch("builtins.open", create=True)
    def testDisplayResultsWithFailedTests(self, mock_open):
        """
        Test the displayResults method with failed tests.

        Verifies that the method displays detailed information
        about failed tests including traceback information.

        Parameters
        ----------
        mock_open : Mock
            Mock of the built-in open function.

        Returns
        -------
        None
        """
        # Mock file content for traceback display
        mock_file_content = ["line 1\n", "line 2 with error\n", "line 3\n", "line 4\n"]
        mock_open.return_value.__enter__.return_value.readlines.return_value = mock_file_content

        summary = {
            "total_tests": 3,
            "passed": 1,
            "failed": 1,
            "errors": 1,
            "skipped": 0,
            "total_time": 10.0,
            "success_rate": 33.33,
            "test_details": [
                {
                    "class": "TestClass",
                    "method": "testMethod",
                    "status": TestStatus.FAILED.name,
                    "error_message": "AssertionError: Test failed",
                    "file_path": "/path/to/test.py",
                    "traceback_frames": [
                        {
                            "file": "/path/to/test.py",
                            "line": 2,
                            "code": "assert False",
                        },
                    ],
                },
            ],
        }

        self.detailed_printer.displayResults(summary=summary)

        # Verify that various print methods were called
        self.assertTrue(self.mock_console.print.called)
        self.assertTrue(self.mock_console.line.called)
        self.assertTrue(self.mock_console.rule.called)

    def testDisplayResultsWithSilentVerbosity(self):
        """
        Test the displayResults method with silent verbosity.

        Verifies that the method does not output anything
        when verbosity is set to SILENT.

        Returns
        -------
        None
        """
        # Reset the mock to avoid interference from setUp
        self.mock_console.reset_mock()
        summary = {
            "total_tests": 1,
            "passed": 0,
            "failed": 1,
            "errors": 0,
            "skipped": 0,
            "total_time": 5.0,
            "success_rate": 0.0,
            "test_details": [],
        }

        self.silent_printer.displayResults(summary=summary)

        self.mock_console.print.assert_not_called()
        self.mock_console.line.assert_not_called()

    def testUnittestResultWithPassedTest(self):
        """
        Test the unittestResult method with a passed test.

        Verifies that the method displays the correct status
        for a passed test result.

        Returns
        -------
        None
        """
        test_result = TestResult(
            id=1,
            name="test_example",
            status=TestStatus.PASSED,
            execution_time=1.0,
            error_message=None,
        )

        self.detailed_printer.unittestResult(test_result)

        self.mock_console.print.assert_called_once()
        call_args = self.mock_console.print.call_args[0][0]
        self.assertIn("✅ PASSED", call_args)
        self.assertIn("test_example", call_args)

    def testUnittestResultWithFailedTest(self):
        """
        Test the unittestResult method with a failed test.

        Verifies that the method displays the correct status
        and error message for a failed test result.

        Returns
        -------
        None
        """
        test_result = TestResult(
            id=1,
            name="test_example",
            status=TestStatus.FAILED,
            execution_time=1.0,
            error_message="AssertionError: Test failed",
        )

        self.detailed_printer.unittestResult(test_result)

        self.mock_console.print.assert_called()
        call_args = self.mock_console.print.call_args[0][0]
        self.assertIn("❌ FAILED", call_args)
        self.assertIn("test_example", call_args)
        self.assertIn("AssertionError", call_args)

    def testUnittestResultWithSkippedTest(self):
        """
        Test the unittestResult method with a skipped test.

        Verifies that the method displays the correct status
        for a skipped test result.

        Returns
        -------
        None
        """
        test_result = TestResult(
            id=1,
            name="test_example",
            status=TestStatus.SKIPPED,
            execution_time=0.0,
            error_message=None,
        )

        self.detailed_printer.unittestResult(test_result)

        self.mock_console.print.assert_called()
        call_args = self.mock_console.print.call_args[0][0]
        self.assertIn("⏩ SKIPPED", call_args)
        self.assertIn("test_example", call_args)

    def testUnittestResultWithErroredTest(self):
        """
        Test the unittestResult method with an errored test.

        Verifies that the method displays the correct status
        for an errored test result.

        Returns
        -------
        None
        """
        test_result = TestResult(
            id=1,
            name="test_example",
            status=TestStatus.ERRORED,
            execution_time=1.0,
            error_message="RuntimeError: Unexpected error",
        )

        self.detailed_printer.unittestResult(test_result)

        self.mock_console.print.assert_called()
        call_args = self.mock_console.print.call_args[0][0]
        self.assertIn("💥 ERRORED", call_args)
        self.assertIn("test_example", call_args)

    def testUnittestResultWithMinimalVerbosity(self):
        """
        Test the unittestResult method with minimal verbosity.

        Verifies that the method does not output anything
        when verbosity is below DETAILED.

        Returns
        -------
        None
        """
        # Reset the mock to avoid interference from setUp
        self.mock_console.reset_mock()
        test_result = TestResult(
            id=1,
            name="test_example",
            status=TestStatus.PASSED,
            execution_time=1.0,
            error_message=None,
        )

        self.minimal_printer.unittestResult(test_result)

        self.mock_console.print.assert_not_called()

    def testUnittestResultWithLongMessage(self):
        """
        Test the unittestResult method with a long test message.

        Verifies that the method truncates long messages appropriately
        to fit within the console width.

        Returns
        -------
        None
        """
        # Set a smaller width to trigger truncation
        self.mock_console.width = 50

        test_result = TestResult(
            id=1,
            name="test_example_with_very_long_name_that_exceeds_console_width",
            status=TestStatus.PASSED,
            execution_time=1.0,
            error_message=None,
        )

        self.detailed_printer.unittestResult(test_result)

        self.mock_console.print.assert_called()
        call_args = self.mock_console.print.call_args[0][0]
        # Verify that the message was truncated
        self.assertLessEqual(len(call_args), 48)  # 50 - 2 for margin
