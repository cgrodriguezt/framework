import inspect
import io
import json
import os
import re
import time
import traceback
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from rich.console import Console as RichConsole
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from orionis.console.output.console import Console
from orionis.test.entities.test_result import TestResult
from orionis.test.enums.test_mode import ExecutionMode
from orionis.test.enums.test_status import TestStatus
from orionis.test.exceptions.test_failure_exception import OrionisTestFailureException
from orionis.test.exceptions.test_persistence_error import OrionisTestPersistenceError
from orionis.test.exceptions.test_value_error import OrionisTestValueError
from orionis.test.logs.history import TestHistory
from orionis.test.contracts.test_unit import IUnitTest
from orionis.test.view.render import TestingResultRender

class UnitTest(IUnitTest):
    """
    UnitTest is a comprehensive testing utility class for discovering, configuring, and executing unit tests.

    This class supports both sequential and parallel test execution, customizable verbosity, fail-fast behavior,
    and rich output formatting using the `rich` library.

    Attributes
    ----------
    loader : unittest.TestLoader
        The test loader used to discover and load tests.
    suite : unittest.TestSuite
        The test suite containing the discovered tests.
    test_results : list of TestResult
        A list to store the results of executed tests.
    start_time : float
        The start time of the test execution.
    print_result : bool
        Flag to determine whether to print test results.
    verbosity : int
        The verbosity level for test output.
    execution_mode : str
        The mode of test execution (e.g., 'SEQUENTIAL' or 'PARALLEL').
    max_workers : int
        The maximum number of workers for parallel execution.
    fail_fast : bool
        Flag to stop execution on the first failure.
    rich_console : RichConsole
        Console for rich text output.
    orionis_console : Console
        Console for standard output.
    discovered_tests : list
        A list to store discovered test cases.
    width_output_component : int
        The width of the table for displaying results.
    throw_exception : bool
        Flag to determine whether to throw exceptions on test failures.
    persistent : bool
        Flag to determine whether to persist test results in a database.
    base_path : str
        The base directory for test discovery and persistence.
    """

    def __init__(self) -> None:
        """
        Initialize the UnitTest instance with default configurations.

        Parameters
        ----------
        self : UnitTest
            The instance of the UnitTest class.

        Attributes
        ----------
        loader : unittest.TestLoader
            The test loader used to discover tests.
        suite : unittest.TestSuite
            The test suite to hold the discovered tests.
        test_results : list of TestResult
            A list to store the results of executed tests.
        start_time : float
            The start time of the test execution.
        print_result : bool
            Flag to determine whether to print test results.
        verbosity : int
            The verbosity level for test output.
        execution_mode : str
            The mode of test execution (e.g., 'SEQUENTIAL' or 'PARALLEL').
        max_workers : int
            The maximum number of workers for parallel execution.
        fail_fast : bool
            Flag to stop execution on the first failure.
        rich_console : RichConsole
            Console for rich text output.
        orionis_console : Console
            Console for standard output.
        discovered_tests : list
            A list to store discovered test cases.
        width_output_component : int
            The width of the table for displaying results.
        throw_exception : bool
            Flag to determine whether to throw exceptions on test failures.
        persistent : bool
            Flag to determine whether to persist test results in a database.
        base_path : str
            The base directory for test discovery and persistence.
        """
        self.loader = unittest.TestLoader()
        self.suite = unittest.TestSuite()
        self.test_results: List[TestResult] = []
        self.start_time: float = 0.0
        self.print_result: bool = True
        self.verbosity: int = 2
        self.execution_mode: str = ExecutionMode.SEQUENTIAL.value
        self.max_workers: int = 4
        self.fail_fast: bool = False
        self.rich_console = RichConsole()
        self.orionis_console = Console()
        self.discovered_tests: List = []
        self.width_output_component: int = int(self.rich_console.width * 0.75)
        self.throw_exception: bool = False
        self.persistent: bool = False
        self.persistent_driver: str = 'sqlite'
        self.web_report: bool = False
        self.base_path: str = "tests"
        self.withliveconsole: bool = True
        self.__output_buffer = None
        self.__error_buffer = None
        self.__result = None

    def configure(
            self,
            *,
            verbosity: int = None,
            execution_mode: str | ExecutionMode = None,
            max_workers: int = None,
            fail_fast: bool = None,
            print_result: bool = None,
            throw_exception: bool = False,
            persistent: bool = False,
            persistent_driver: str = 'sqlite',
            web_report: bool = False
        ) -> 'UnitTest':
        """
        Configures the UnitTest instance with the specified parameters.

        Parameters
        ----------
        verbosity : int, optional
            The verbosity level for test output. If None, the current setting is retained.
        execution_mode : str or ExecutionMode, optional
            The mode in which the tests will be executed ('SEQUENTIAL' or 'PARALLEL'). If None, the current setting is retained.
        max_workers : int, optional
            The maximum number of workers to use for parallel execution. If None, the current setting is retained.
        fail_fast : bool, optional
            Whether to stop execution upon the first failure. If None, the current setting is retained.
        print_result : bool, optional
            Whether to print the test results after execution. If None, the current setting is retained.
        throw_exception : bool, optional
            Whether to throw an exception if any test fails. Defaults to False.
        persistent : bool, optional
            Whether to persist the test results in a database. Defaults to False.
        persistent_driver : str, optional
            The driver to use for persistent storage. Defaults to 'sqlite'.

        Returns
        -------
        UnitTest
            The configured UnitTest instance.
        """
        if verbosity is not None:
            self.verbosity = verbosity

        if execution_mode is not None and isinstance(execution_mode, ExecutionMode):
            self.execution_mode = execution_mode.value
        else:
            self.execution_mode = execution_mode

        if max_workers is not None:
            self.max_workers = max_workers

        if fail_fast is not None:
            self.fail_fast = fail_fast

        if print_result is not None:
            self.print_result = print_result

        if throw_exception is not None:
            self.throw_exception = throw_exception

        if persistent is not None:
            self.persistent = persistent

        if persistent_driver is not None:
            self.persistent_driver = persistent_driver

        if web_report is not None:
            self.web_report = web_report

        return self

    def discoverTestsInFolder(
        self,
        *,
        folder_path: str,
        base_path: str = "tests",
        pattern: str = "test_*.py",
        test_name_pattern: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> 'UnitTest':
        """
        Parameters
        ----------
        folder_path : str
            The relative path to the folder containing the tests.
        base_path : str, optional
            The base directory where the test folder is located. Defaults to "tests".
        pattern : str, optional
            The filename pattern to match test files. Defaults to "test_*.py".
        test_name_pattern : str or None, optional
            A pattern to filter test names. Defaults to None.
        tags : list of str or None, optional
            A list of tags to filter tests. Defaults to None.

        Returns
        -------
        UnitTest
            The current instance of the UnitTest class with the discovered tests added.

        Raises
        ------
        OrionisTestValueError
            If the test folder does not exist, no tests are found, or an error occurs during test discovery.

        Notes
        -----
        This method updates the internal test suite with the discovered tests and tracks the number of tests found.
        """
        try:
            self.base_path = base_path

            full_path = Path(base_path) / folder_path
            if not full_path.exists():
                raise OrionisTestValueError(f"Test folder not found: {full_path}")

            tests = self.loader.discover(
                start_dir=str(full_path),
                pattern=pattern,
                top_level_dir=None
            )

            if test_name_pattern:
                tests = self._filterTestsByName(tests, test_name_pattern)

            if tags:
                tests = self._filterTestsByTags(tests, tags)

            if not list(tests):
                raise OrionisTestValueError(f"No tests found in '{full_path}' matching pattern '{pattern}'")

            self.suite.addTests(tests)

            test_count = len(list(self._flattenTestSuite(tests)))
            self.discovered_tests.append({
                "folder": str(full_path),
                "test_count": test_count,
            })

            return self

        except ImportError as e:
            raise OrionisTestValueError(f"Error importing tests from '{full_path}': {str(e)}")
        except Exception as e:
            raise OrionisTestValueError(f"Unexpected error discovering tests: {str(e)}")

    def discoverTestsInModule(self, *, module_name: str, test_name_pattern: Optional[str] = None) -> 'UnitTest':
        """
        Discovers and loads tests from a specified module, optionally filtering by a test name pattern, and adds them to the test suite.

        Parameters
        ----------
        module_name : str
            Name of the module from which to discover tests.
        test_name_pattern : str, optional
            Pattern to filter test names. Only tests matching this pattern will be included. Defaults to None.

        Returns
        -------
        UnitTest
            The current instance of the UnitTest class, allowing method chaining.

        Exceptions
        ----------
        OrionisTestValueError
            If the specified module cannot be imported.
        """
        try:

            tests = self.loader.loadTestsFromName(module_name)

            if test_name_pattern:
                tests = self._filterTestsByName(tests, test_name_pattern)

            self.suite.addTests(tests)

            test_count = len(list(self._flattenTestSuite(tests)))
            self.discovered_tests.append({
                "module": module_name,
                "test_count": test_count,
            })

            return self
        except ImportError as e:
            raise OrionisTestValueError(f"Error importing module '{module_name}': {str(e)}")

    def _startMessage(self) -> None:
        """
        Prints a formatted message indicating the start of the test suite execution.

        Parameters
        ----------
        self : UnitTest
            The instance of the UnitTest class.

        Notes
        -----
        This method displays details about the test suite, including the total number of tests,
        the execution mode (parallel or sequential), and the start time. The message is styled
        and displayed using the `rich` library.

        Attributes Used
        --------------
        print_result : bool
            Determines whether the message should be printed.
        suite : unittest.TestSuite
            The test suite containing the tests to be executed.
        max_workers : int
            The number of workers used in parallel execution mode.
        execution_mode : str
            The mode of execution ('SEQUENTIAL' or 'PARALLEL').
        orionis_console : Console
            The console object for handling standard output.
        rich_console : RichConsole
            The rich console object for styled output.
        width_output_component : int
            The calculated width of the message panel for formatting.
        """
        if self.print_result:
            test_count = len(list(self._flattenTestSuite(self.suite)))
            mode_text = f"[stat]Parallel with {self.max_workers} workers[/stat]" if self.execution_mode == ExecutionMode.PARALLEL.value else "Sequential"
            textlines = [
                f"[bold]Total Tests:[/bold] [dim]{test_count}[/dim]",
                f"[bold]Mode:[/bold] [dim]{mode_text}[/dim]",
                f"[bold]Started at:[/bold] [dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]"
            ]

            self.orionis_console.newLine()
            self.rich_console.print(
                Panel(
                    str('\n').join(textlines),
                    border_style="blue",
                    title="🧪 Orionis Framework - Component Test Suite",
                    title_align="center",
                    width=self.width_output_component,
                    padding=(0, 1)
                )
            )
            self.orionis_console.newLine()

    def run(self, print_result: bool = None, throw_exception: bool = None) -> Dict[str, Any]:
        """
        Executes the test suite and processes the results.

        Parameters
        ----------
        print_result : bool, optional
            If provided, overrides the instance's `print_result` attribute to determine whether to print results.
        throw_exception : bool, optional
            If True, raises an exception if any test failures or errors are detected.

        Returns
        -------
        dict
            A summary of the test execution, including details such as execution time, results, and timestamp.

        Raises
        ------
        OrionisTestFailureException
            If `throw_exception` is True and there are test failures or errors.
        """

        # Check if required print_result and throw_exception
        if print_result is not None:
            self.print_result = print_result
        if throw_exception is not None:
            self.throw_exception = throw_exception

        # Dynamically determine if live console should be enabled based on test code usage
        self._withLiveConsole()

        # Start the timer and print the start message
        self.start_time = time.time()
        self._startMessage()

        # Prepare the running message based on whether live console is enabled
        if self.print_result:
            message = "[bold yellow]⏳ Running tests...[/bold yellow]\n"
            message += "[dim]This may take a few seconds. Please wait...[/dim]" if self.withliveconsole else "[dim]Please wait, results will appear below...[/dim]"

            # Panel for running message
            running_panel = Panel(
                message,
                border_style="yellow",
                title="In Progress",
                title_align="left",
                width=self.width_output_component,
                padding=(1, 2)
            )

            # Elegant "running" message using Rich Panel
            if self.withliveconsole:
                with Live(running_panel, console=self.rich_console, refresh_per_second=4, transient=True):
                    result, output_buffer, error_buffer = self._runSuite()
            else:
                self.rich_console.print(running_panel)
                result, output_buffer, error_buffer = self._runSuite()
        else:
            # If not printing results, run the suite without live console
            result, output_buffer, error_buffer = self._runSuite()

        # Save Outputs
        self.__output_buffer = output_buffer.getvalue()
        self.__error_buffer = error_buffer.getvalue()

        # Process results
        execution_time = time.time() - self.start_time
        summary = self._generateSummary(result, execution_time)

        # Print captured output
        if self.print_result:
            self._displayResults(summary)

        # Print Execution Time
        if not result.wasSuccessful() and self.throw_exception:
            raise OrionisTestFailureException(result)

        # Return the summary of the test results
        self.__result = summary
        return summary

    def _withLiveConsole(self) -> None:
        """
        Determines if the live console should be used based on the presence of debug or dump calls in the test code.

        Returns
        -------
        bool
            True if the live console should be used, False otherwise.
        """
        if self.withliveconsole:

            try:

                # Flatten the test suite to get all test cases
                for test_case in self._flattenTestSuite(self.suite):

                    # Get the source code of the test case class
                    source = inspect.getsource(test_case.__class__)

                    # Only match if the keyword is not inside a comment
                    for keyword in ('self.dd', 'self.dump'):

                        # Find all lines containing the keyword
                        for line in source.splitlines():
                            if keyword in line:

                                # Remove leading/trailing whitespace
                                stripped = line.strip()

                                # Ignore lines that start with '#' (comments)
                                if not stripped.startswith('#') and not re.match(r'^\s*#', line):
                                    self.withliveconsole = False
                                    break

                        # If we found a keyword, no need to check further
                        if not self.withliveconsole:
                            break

                    # If we found a keyword in any test case, no need to check further
                    if not self.withliveconsole:
                        break

            except Exception:
                pass

    def _runSuite(self):
        """
        Run the test suite according to the selected execution mode (parallel or sequential),
        capturing standard output and error streams during execution.

        Returns
        -------
        tuple
            result : unittest.TestResult
            The result object from the test execution.
            output_buffer : io.StringIO
            Captured standard output during test execution.
            error_buffer : io.StringIO
            Captured standard error during test execution.
        """

        # Setup output capture
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()

        # Execute tests based on selected mode
        if self.execution_mode == ExecutionMode.PARALLEL.value:
            result = self._runTestsInParallel(output_buffer, error_buffer)
        else:
            result = self._runTestsSequentially(output_buffer, error_buffer)

        # Return the result along with captured output and error streams
        return result, output_buffer, error_buffer

    def _runTestsSequentially(self, output_buffer: io.StringIO, error_buffer: io.StringIO) -> unittest.TestResult:
        """
        Executes the test suite sequentially, capturing the output and error streams.

        Parameters
        ----------
        output_buffer : io.StringIO
            A buffer to capture the standard output during test execution.
        error_buffer : io.StringIO
            A buffer to capture the standard error during test execution.

        Returns
        -------
        unittest.TestResult
            The result of the test suite execution, containing information about
            passed, failed, and skipped tests.
        """
        with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
            runner = unittest.TextTestRunner(
                stream=output_buffer,
                verbosity=self.verbosity,
                failfast=self.fail_fast,
                resultclass=self._createCustomResultClass()
            )
            result = runner.run(self.suite)

        return result

    def _runTestsInParallel(self, output_buffer: io.StringIO, error_buffer: io.StringIO) -> unittest.TestResult:
        """
        Runs all test cases in the provided test suite concurrently using a thread pool,
        aggregating the results into a single result object. Standard output and error
        are redirected to the provided buffers during execution.

        Parameters
        ----------
        output_buffer : io.StringIO
            Buffer to capture standard output during test execution.
        error_buffer : io.StringIO
            Buffer to capture standard error during test execution.

        Returns
        -------
        unittest.TestResult
            Combined result object containing the outcomes of all executed tests.

        Notes
        -----
        - Uses a custom result class to aggregate test results.
        - If `fail_fast` is enabled and a test fails, remaining tests are canceled.
        """

        # Flatten the test suite to get individual test cases
        test_cases = list(self._flattenTestSuite(self.suite))

        # Create a custom result instance to collect all results
        result_class = self._createCustomResultClass()
        combined_result = result_class(io.StringIO(), descriptions=True, verbosity=self.verbosity)

        # Helper function to run a single test and return its result.
        # Minimal output for parallel runs
        def run_single_test(test):
            runner = unittest.TextTestRunner(
                stream=io.StringIO(),
                verbosity=0,
                failfast=False,
                resultclass=result_class
            )
            return runner.run(unittest.TestSuite([test]))

        with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(run_single_test, test) for test in test_cases]

                for future in as_completed(futures):
                    test_result = future.result()
                    self._mergeTestResults(combined_result, test_result)

                    if self.fail_fast and not combined_result.wasSuccessful():
                        for f in futures:
                            f.cancel()
                        break

        return combined_result

    def _mergeTestResults(self, combined_result: unittest.TestResult, individual_result: unittest.TestResult) -> None:
        """
        Merge the results of two unittest.TestResult objects.

        This method updates the `combined_result` object by adding the test run counts,
        failures, errors, skipped tests, expected failures, and unexpected successes
        from the `individual_result` object. Additionally, it merges any custom test
        results stored in the `test_results` attribute, if present.

        Parameters
        ----------
        combined_result : unittest.TestResult
            The TestResult object to which the results will be merged.
        individual_result : unittest.TestResult
            The TestResult object containing the results to be merged into the combined_result.

        Returns
        -------
        None
        """
        combined_result.testsRun += individual_result.testsRun
        combined_result.failures.extend(individual_result.failures)
        combined_result.errors.extend(individual_result.errors)
        combined_result.skipped.extend(individual_result.skipped)
        combined_result.expectedFailures.extend(individual_result.expectedFailures)
        combined_result.unexpectedSuccesses.extend(individual_result.unexpectedSuccesses)

        # Merge our custom test results
        if hasattr(individual_result, 'test_results'):
            if not hasattr(combined_result, 'test_results'):
                combined_result.test_results = []
            combined_result.test_results.extend(individual_result.test_results)

    def _createCustomResultClass(self) -> type:
        """
        Creates a custom test result class for enhanced test tracking.
        This method dynamically generates an `EnhancedTestResult` class that extends
        `unittest.TextTestResult`. The custom class provides advanced functionality for
        tracking test execution details, including timings, statuses, and error information.

        Returns
        -------
        type
            A dynamically created class `EnhancedTestResult` that overrides methods to handle
            test results, including success, failure, error, and skipped tests. The class
            collects detailed information about each test, such as execution time, error
            messages, traceback, and file path.

        Notes
        -----
        The `EnhancedTestResult` class includes the following method overrides:
        The method uses the `this` reference to access the outer class's methods, such as
        `_extractErrorInfo`, for extracting and formatting error information.
        """

        # Use `this` to refer to the outer class instance
        this = self

        # Define the custom test result class
        class EnhancedTestResult(unittest.TextTestResult):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.test_results = []
                self._test_timings = {}
                self._current_test_start = None

            def startTest(self, test):
                self._current_test_start = time.time()
                super().startTest(test)

            def stopTest(self, test):
                elapsed = time.time() - self._current_test_start
                self._test_timings[test] = elapsed
                super().stopTest(test)

            def addSuccess(self, test):
                super().addSuccess(test)
                elapsed = self._test_timings.get(test, 0.0)
                self.test_results.append(
                    TestResult(
                        id=test.id(),
                        name=str(test),
                        status=TestStatus.PASSED,
                        execution_time=elapsed,
                        class_name=test.__class__.__name__,
                        method=getattr(test, "_testMethodName", None),
                        module=getattr(test, "__module__", None),
                        file_path=inspect.getfile(test.__class__),
                        doc_string=getattr(getattr(test, test._testMethodName, None), "__doc__", None),
                    )
                )

            def addFailure(self, test, err):
                super().addFailure(test, err)
                elapsed = self._test_timings.get(test, 0.0)
                tb_str = ''.join(traceback.format_exception(*err))
                file_path, clean_tb = this._extractErrorInfo(tb_str)
                self.test_results.append(
                    TestResult(
                        id=test.id(),
                        name=str(test),
                        status=TestStatus.FAILED,
                        execution_time=elapsed,
                        error_message=str(err[1]),
                        traceback=clean_tb,
                        class_name=test.__class__.__name__,
                        method=getattr(test, "_testMethodName", None),
                        module=getattr(test, "__module__", None),
                        file_path=inspect.getfile(test.__class__),
                        doc_string=getattr(getattr(test, test._testMethodName, None), "__doc__", None),
                    )
                )

            def addError(self, test, err):
                super().addError(test, err)
                elapsed = self._test_timings.get(test, 0.0)
                tb_str = ''.join(traceback.format_exception(*err))
                file_path, clean_tb = this._extractErrorInfo(tb_str)
                self.test_results.append(
                    TestResult(
                        id=test.id(),
                        name=str(test),
                        status=TestStatus.ERRORED,
                        execution_time=elapsed,
                        error_message=str(err[1]),
                        traceback=clean_tb,
                        class_name=test.__class__.__name__,
                        method=getattr(test, "_testMethodName", None),
                        module=getattr(test, "__module__", None),
                        file_path=inspect.getfile(test.__class__),
                        doc_string=getattr(getattr(test, test._testMethodName, None), "__doc__", None),
                    )
                )

            def addSkip(self, test, reason):
                super().addSkip(test, reason)
                elapsed = self._test_timings.get(test, 0.0)
                self.test_results.append(
                    TestResult(
                        id=test.id(),
                        name=str(test),
                        status=TestStatus.SKIPPED,
                        execution_time=elapsed,
                        error_message=reason,
                        class_name=test.__class__.__name__,
                        method=getattr(test, "_testMethodName", None),
                        module=getattr(test, "__module__", None),
                        file_path=inspect.getfile(test.__class__),
                        doc_string=getattr(getattr(test, test._testMethodName, None), "__doc__", None),
                    )
                )

        # Return the dynamically created EnhancedTestResult class
        return EnhancedTestResult

    def _generateSummary(self, result: unittest.TestResult, execution_time: float) -> Dict[str, Any]:
        """
        Generate a summary of the test results, including statistics and details for each test.

        Parameters
        ----------
        result : unittest.TestResult
            The result object containing details of the test execution.
        execution_time : float
            The total execution time of the test suite in seconds.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the following keys:
                total_tests : int
                    The total number of tests executed.
                passed : int
                    The number of tests that passed.
                failed : int
                    The number of tests that failed.
                errors : int
                    The number of tests that encountered errors.
                skipped : int
                    The number of tests that were skipped.
                total_time : float
                    The total execution time of the test suite.
                success_rate : float
                    The percentage of tests that passed.
                test_details : List[Dict[str, Any]]
                    A list of dictionaries with details for each test, including:
                        id : str
                            The unique identifier of the test.
                        class : str
                            The class name of the test.
                        method : str
                            The method name of the test.
                        status : str
                            The status of the test (e.g., "PASSED", "FAILED").
                        execution_time : float
                            The execution time of the test in seconds.
                        error_message : str
                            The error message if the test failed or errored.
                        traceback : str
                            The traceback information if the test failed or errored.
                        file_path : str
                            The file path of the test.
                        doc_string : str
                            The docstring of the test method, if available.
        """
        test_details = []

        for test_result in result.test_results:
            rst: TestResult = test_result
            test_details.append({
                'id': rst.id,
                'class': rst.class_name,
                'method': rst.method,
                'status': rst.status.name,
                'execution_time': float(rst.execution_time),
                'error_message': rst.error_message,
                'traceback': rst.traceback,
                'file_path': rst.file_path,
                'doc_string': rst.doc_string
            })

        passed = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
        success_rate = (passed / result.testsRun * 100) if result.testsRun > 0 else 100.0

        # Create a summary report
        report = {
            "total_tests": result.testsRun,
            "passed": passed,
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "total_time": float(execution_time),
            "success_rate": success_rate,
            "test_details": test_details,
            "timestamp": datetime.now().isoformat()
        }

        # Handle persistence of the report
        if self.persistent:
            self._persistTestResults(report)

        # Handle Web Report Rendering
        if self.web_report:

            # Generate the web report and get the path
            path = self._webReport(report)

            # Elegant invitation to view the results, with underlined path
            invite_text = Text("Test results saved. ", style="green")
            invite_text.append("View report: ", style="bold green")
            invite_text.append(str(path), style="underline blue")
            self.rich_console.print(invite_text)

        # Return the summary
        return {
            "total_tests": result.testsRun,
            "passed": passed,
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "total_time": float(execution_time),
            "success_rate": success_rate,
            "test_details": test_details
        }

    def _webReport(self, summary: Dict[str, Any]) -> None:
        """
        Generates a web report for the test results summary.

        Parameters
        ----------
        summary : dict
            The summary of test results to generate a web report for.

        Returns
        -------
        str
            The path to the generated web report.

        Notes
        -----
        - Determines the storage path based on the current working directory and base_path.
        - Uses TestingResultRender to generate the report.
        - If persistence is enabled and the driver is 'sqlite', the report is marked as persistent.
        - Returns the path to the generated report for further use.
        """
        # Determine the absolute path for storing results
        project = os.path.basename(os.getcwd())
        storage_path = os.path.abspath(os.path.join(os.getcwd(), self.base_path))

        # Only use storage_path if project is recognized
        if project not in ['framework', 'orionis']:
            storage_path = None

        # Create the TestingResultRender instance with the storage path and summary
        render = TestingResultRender(
            storage_path=storage_path,
            result=summary,
            persist=self.persistent and self.persistent_driver == 'sqlite'
        )

        # Render the report and return the path
        return render.render()

    def _persistTestResults(self, summary: Dict[str, Any]) -> None:
        """
        Persist the test results summary using the configured persistent driver.

        Parameters
        ----------
        summary : dict
            The summary of test results to persist.

        Notes
        -----
        Depending on the value of `self.persistent_driver`, the summary is either:
            - Stored in an SQLite database (using the TestHistory class), or
            - Written to a timestamped JSON file in the specified base path.

        Raises
        ------
        OSError
            If there is an error creating directories or writing files.
        Exception
            If database operations fail.
        """

        try:
            # Determine the absolute path for storing results
            project = os.getcwd().split(os.sep)[-1]
            storage_path = None
            if project in ['framework', 'orionis']:
                storage_path = os.path.abspath(os.path.join(os.getcwd(), self.base_path))

            if self.persistent_driver == 'sqlite':

                # Initialize the TestHistory class for database operations
                history = TestHistory(
                    storage_path=storage_path,
                    db_name='tests.sqlite',
                    table_name='reports'
                )

                # Insert the summary into the database
                history.create(summary)

            elif self.persistent_driver == 'json':

                # Ensure the base path exists and write the summary to a JSON file
                os.makedirs(storage_path, exist_ok=True)

                # Get the current timestamp for the log file name
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Create the log file path with the timestamp
                log_path = os.path.abspath(os.path.join(storage_path, f'test_{timestamp}.json'))

                # Write the summary to the JSON file
                with open(log_path, 'w', encoding='utf-8') as log:
                    json.dump(summary, log, indent=4)
        except OSError as e:
            raise OSError(f"Error creating directories or writing files: {str(e)}")
        except Exception as e:
            raise OrionisTestPersistenceError(f"Error persisting test results: {str(e)}")

    def _printSummaryTable(self, summary: Dict[str, Any]) -> None:
        """
        Prints a summary table of test results using the Rich library.

        Parameters
        ----------
        summary : dict
            Dictionary with the test summary data. Must contain the following keys:
            total_tests : int
                Total number of tests executed.
            passed : int
                Number of tests that passed.
            failed : int
                Number of tests that failed.
            errors : int
                Number of tests that had errors.
            skipped : int
                Number of tests that were skipped.
            total_time : float
                Total duration of the test execution in seconds.
            success_rate : float
                Percentage of tests that passed.

        Returns
        -------
        None
        """
        table = Table(
            show_header=True,
            header_style="bold white",
            width=self.width_output_component,
            border_style="blue"
        )
        table.add_column("Total", justify="center")
        table.add_column("Passed", justify="center")
        table.add_column("Failed", justify="center")
        table.add_column("Errors", justify="center")
        table.add_column("Skipped", justify="center")
        table.add_column("Duration", justify="center")
        table.add_column("Success Rate", justify="center")
        table.add_row(
            str(summary["total_tests"]),
            str(summary["passed"]),
            str(summary["failed"]),
            str(summary["errors"]),
            str(summary["skipped"]),
            f"{summary['total_time']:.2f}s",
            f"{summary['success_rate']:.2f}%"
        )
        self.rich_console.print(table)
        self.orionis_console.newLine()

    def _filterTestsByName(self, suite: unittest.TestSuite, pattern: str) -> unittest.TestSuite:
        """
        Filters tests in a given test suite based on a specified name pattern.
        Parameters
        ----------
        suite : unittest.TestSuite
            The test suite containing the tests to filter.
        pattern : str
            A regular expression pattern to match test names.
        Returns
        -------
        unittest.TestSuite
            A new test suite containing only the tests that match the pattern.
        Raises
        ------
        OrionisTestValueError
            If the provided pattern is not a valid regular expression.
        Notes
        -----
        """
        filtered_suite = unittest.TestSuite()
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise OrionisTestValueError(f"Invalid test name pattern: {str(e)}")

        for test in self._flattenTestSuite(suite):
            if regex.search(test.id()):
                filtered_suite.addTest(test)

        return filtered_suite

    def _filterTestsByTags(self, suite: unittest.TestSuite, tags: List[str]) -> unittest.TestSuite:
        """
        Filter tests in a unittest TestSuite by specified tags.

        Iterates through all tests in the provided TestSuite and checks for a `__tags__`
        attribute either on the test method or the test case class. If any of the specified
        tags match the tags associated with the test, the test is included in the filtered suite.

        Parameters
        ----------
        suite : unittest.TestSuite
            The original TestSuite containing all tests.
        tags : list of str
            List of tags to filter the tests by.

        Returns
        -------
        unittest.TestSuite
            A new TestSuite containing only the tests that match the specified tags.
        """

        # Initialize an empty TestSuite to hold the filtered tests
        filtered_suite = unittest.TestSuite()
        tag_set = set(tags)

        for test in self._flattenTestSuite(suite):

            # Get test method if this is a TestCase instance
            test_method = getattr(test, test._testMethodName, None)

            # Check for tags attribute on the test method
            if hasattr(test_method, '__tags__'):
                method_tags = set(getattr(test_method, '__tags__'))
                if tag_set.intersection(method_tags):
                    filtered_suite.addTest(test)

            # Also check on the test case class
            elif hasattr(test, '__tags__'):
                class_tags = set(getattr(test, '__tags__'))
                if tag_set.intersection(class_tags):
                    filtered_suite.addTest(test)

        # Return the filtered suite containing only tests with matching tags
        return filtered_suite

    def _flattenTestSuite(self, suite: unittest.TestSuite) -> List[unittest.TestCase]:
        """
        Recursively flattens a nested unittest.TestSuite into a list of unique unittest.TestCase instances.

        Parameters
        ----------
        suite : unittest.TestSuite
            The test suite to flatten, which may contain nested suites or test cases.

        Returns
        -------
        List[unittest.TestCase]
            A list containing all unique TestCase instances extracted from the suite.

        Notes
        -----
        This method traverses the given TestSuite recursively, collecting all TestCase instances
        and ensuring that each test appears only once in the resulting list.
        """
        tests = []
        seen_ids = set()

        def _flatten(item):
            if isinstance(item, unittest.TestSuite):
                for sub_item in item:
                    _flatten(sub_item)
            elif hasattr(item, "id"):
                test_id = item.id()
                parts = test_id.split('.')
                if len(parts) >= 2:
                    short_id = '.'.join(parts[-2:])
                else:
                    short_id = test_id
                if short_id not in seen_ids:
                    seen_ids.add(short_id)
                    tests.append(item)

        _flatten(suite)
        return tests

    def _sanitizeTraceback(self, test_path: str, traceback_test: str) -> str:
        """
        Sanitize a traceback string to extract and display the most relevant parts
        related to a specific test file.

        Parameters
        ----------
        test_path : str
            The file path of the test file being analyzed.
        traceback_test : str
            The full traceback string to be sanitized.

        Returns
        -------
        str
            A sanitized traceback string containing only the relevant parts related to the test file.
            If no relevant parts are found, the full traceback is returned.
            If the traceback is empty, a default message "No traceback available for this test." is returned.
        """
        if not traceback_test:
            return "No traceback available for this test."

        # Try to extract the test file name
        file_match = re.search(r'([^/\\]+)\.py', test_path)
        file_name = file_match.group(1) if file_match else None

        if not file_name:
            return traceback_test

        # Process traceback to show most relevant parts
        lines = traceback_test.splitlines()
        relevant_lines = []
        found_test_file = False if file_name in traceback_test else True

        for line in lines:
            if file_name in line and not found_test_file:
                found_test_file = True
            if found_test_file:
                if 'File' in line:
                    relevant_lines.append(line.strip())
                elif line.strip() != '':
                    relevant_lines.append(line)

        # If we didn't find the test file, return the full traceback
        if not relevant_lines:
            return traceback_test

        # Remove any lines that are not relevant to the test file
        return str('\n').join(relevant_lines)

    def _displayResults(self, summary: Dict[str, Any]) -> None:
        """
        Display the results of the test execution, including a summary table and detailed
        information about failed or errored tests grouped by their test classes.

        Parameters
        ----------
        summary : dict
            Dictionary containing the summary of the test execution, including test details,
            statuses, and execution times.

        Notes
        -----
        - Prints a summary table of the test results.
        - Groups failed and errored tests by their test class and displays them in a structured
          format using panels.
        - For each failed or errored test, displays the traceback in a syntax-highlighted panel
          with additional metadata such as the test method name and execution time.
        - Uses different icons and border colors to distinguish between failed and errored tests.
        - Calls a finishing message method after displaying all results.
        """

        # Print summary table
        self._printSummaryTable(summary)

        # Group failures and errors by test class
        failures_by_class = {}
        for test in summary["test_details"]:
            if test["status"] in (TestStatus.FAILED.name, TestStatus.ERRORED.name):
                class_name = test["class"]
                if class_name not in failures_by_class:
                    failures_by_class[class_name] = []
                failures_by_class[class_name].append(test)

        # Display grouped failures
        for class_name, tests in failures_by_class.items():

            class_panel = Panel.fit(f"[bold]{class_name}[/bold]", border_style="red", padding=(0, 2))
            self.rich_console.print(class_panel)

            for test in tests:
                traceback_str = self._sanitizeTraceback(test['file_path'], test['traceback'])
                syntax = Syntax(
                    traceback_str,
                    lexer="python",
                    line_numbers=False,
                    background_color="default",
                    word_wrap=True,
                    theme="monokai"
                )

                icon = "❌" if test["status"] == TestStatus.FAILED.name else "💥"
                border_color = "yellow" if test["status"] == TestStatus.FAILED.name else "red"

                # Ensure execution time is never zero for display purposes
                if not test['execution_time'] or test['execution_time'] == 0:
                    test['execution_time'] = 0.001

                panel = Panel(
                    syntax,
                    title=f"{icon} {test['method']}",
                    subtitle=f"Duration: {test['execution_time']:.3f}s",
                    border_style=border_color,
                    title_align="left",
                    padding=(1, 1),
                    subtitle_align="right",
                    width=self.width_output_component
                )
                self.rich_console.print(panel)
                self.orionis_console.newLine()

        self._finishMessage(summary)

    def _extractErrorInfo(self, traceback_str: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract error information from a traceback string.
        This method processes a traceback string to extract the file path of the Python file where the error occurred and
        cleans up the traceback by removing framework internals and irrelevant noise.

        Parameters
        ----------
        traceback_str : str
            The traceback string to process.

        Returns
        -------
        Tuple[Optional[str], Optional[str]]
            A tuple containing:

        Notes
        -----
        Framework internals and lines containing 'unittest/', 'lib/python', or 'site-packages' are removed from the traceback.
        The cleaned traceback starts from the first occurrence of the test file path.
        """
        # Extract file path
        file_matches = re.findall(r'File ["\'](.*?.py)["\']', traceback_str)
        file_path = file_matches[-1] if file_matches else None

        # Clean up traceback by removing framework internals and noise
        tb_lines = traceback_str.split('\n')
        clean_lines = []
        relevant_lines_started = False

        for line in tb_lines:
            # Skip framework internal lines
            if any(s in line for s in ['unittest/', 'lib/python', 'site-packages']):
                continue

            # Start capturing when we hit the test file
            if file_path and file_path in line and not relevant_lines_started:
                relevant_lines_started = True

            if relevant_lines_started:
                clean_lines.append(line)

        clean_tb = str('\n').join(clean_lines) if clean_lines else traceback_str

        return file_path, clean_tb

    def _finishMessage(self, summary: Dict[str, Any]) -> None:
        """
        Display a summary message for the test suite execution.

        Parameters
        ----------
        summary : dict
            Dictionary containing the test suite summary, including keys such as
            'failed', 'errors', and 'total_time'.

        Notes
        -----
        - If `self.print_result` is False, the method returns without displaying anything.
        - Shows a status icon (✅ for success, ❌ for failure) based on the presence of
          failures or errors in the test suite.
        - Formats and prints the message within a styled panel using the `rich` library.
        """
        if not self.print_result:
            return

        status_icon = "✅" if (summary['failed'] + summary['errors']) == 0 else "❌"
        msg = f"Test suite completed in {summary['total_time']:.2f} seconds"
        self.rich_console.print(
            Panel(
                msg,
                border_style="blue",
                title=f"{status_icon} Test Suite Finished",
                title_align='left',
                width=self.width_output_component,
                padding=(0, 1)
            )
        )
        self.rich_console.print()

    def getTestNames(self) -> List[str]:
        """
        Get a list of test names (unique identifiers) from the test suite.

        Returns
        -------
        List[str]
            List of test names (unique identifiers) from the test suite.
        """
        return [test.id() for test in self._flattenTestSuite(self.suite)]

    def getTestCount(self) -> int:
        """
        Returns the total number of test cases in the test suite.

        Returns
        -------
        int
            The total number of individual test cases in the suite.
        """
        return len(list(self._flattenTestSuite(self.suite)))

    def clearTests(self) -> None:
        """
        Clear all tests from the current test suite.

        Resets the internal test suite to an empty `unittest.TestSuite`, removing any previously added tests.
        """
        self.suite = unittest.TestSuite()

    def getResult(self) -> dict:
        """
        Returns the results of the executed test suite.

        Returns
        -------
        UnitTest
            The result of the executed test suite.
        """
        return self.__result

    def getOutputBuffer(self) -> int:
        """
        Returns the output buffer used for capturing test results.
        This method returns the internal output buffer that collects the results of the test execution.
        Returns
        -------
        int
            The output buffer containing the results of the test execution.
        """
        return self.__output_buffer

    def printOutputBuffer(self) -> None:
        """
        Prints the contents of the output buffer to the console.
        This method retrieves the output buffer and prints its contents using the rich console.
        """
        if self.__output_buffer:
            print(self.__output_buffer)

    def getErrorBuffer(self) -> int:
        """
        Returns the error buffer used for capturing test errors.
        This method returns the internal error buffer that collects any errors encountered during test execution.
        Returns
        -------
        int
            The error buffer containing the errors encountered during the test execution.
        """
        return self.__error_buffer

    def printErrorBuffer(self) -> None:
        """
        Prints the contents of the error buffer to the console.
        This method retrieves the error buffer and prints its contents using the rich console.
        """
        if self.__error_buffer:
            print(self.__error_buffer)