import inspect
import linecache
import time
import traceback
import unittest
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from orionis.services.introspection.instances.reflection import ReflectionInstance
from orionis.support.strings.stringable import Stringable
from orionis.test.entities.result import TestResult
from orionis.test.enums.status import TestStatus

class TestResultProcessor(unittest.TestResult):

    # ruff: noqa: PLR2004,PLW2901

    _print_verbosity: int | None = None

    @classmethod
    def setPrintVerbosity(cls, verbosity: int) -> None:
        """
        Set the print verbosity level for test result output.

        Parameters
        ----------
        verbosity : int
            The verbosity level to set for printing test results.

        Returns
        -------
        None
            This method sets a class-level attribute and returns None.
        """
        cls._print_verbosity = verbosity

    def __init__(self, *args: object, **kwargs: object) -> None:
        """
        Initialize the TestResultProcessor instance.

        Parameters
        ----------
        *args : object
            Positional arguments passed to the superclass.
        **kwargs : object
            Keyword arguments passed to the superclass.

        Returns
        -------
        None
            This constructor initializes instance attributes and returns None.
        """
        super().__init__(*args, **kwargs)
        self.__test_results: list[TestResult] = []
        self.__console = Console()
        self.__max_width = self.__console.width * 0.8

    def startTest(self, test: unittest.case.TestCase) -> None:
        """
        Start timing for a test case execution.

        Parameters
        ----------
        test : unittest.case.TestCase
            The test case instance being started.

        Returns
        -------
        None
            This method starts a timer and calls the superclass method.
        """
        self.__start_time = time.perf_counter()
        super().startTest(test)

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        """
        Record a successful test result and print it.

        Parameters
        ----------
        test : unittest.case.TestCase
            The test case instance that succeeded.

        Returns
        -------
        None
            This method appends the result and prints it, then calls the
            superclass method.
        """
        result = self.__createTestResult(test, TestStatus.PASSED)
        self.__test_results.append(result)
        self.__printTestResult(result)
        super().addSuccess(test)

    def addFailure(
        self,
        test: unittest.case.TestCase,
        err: tuple[type[BaseException], BaseException, object],
    ) -> None:
        """
        Record a failed test result and print it.

        Parameters
        ----------
        test : unittest.case.TestCase
            The test case instance that failed.
        err : tuple[type[BaseException], BaseException, object]
            The exception info tuple for the failure.

        Returns
        -------
        None
            This method appends the result and prints it, then calls the
            superclass method.
        """
        result = self.__createTestResult(test, TestStatus.FAILED, err)
        self.__test_results.append(result)
        self.__printTestResult(result)
        super().addFailure(test, err)

    def addError(
        self,
        test: unittest.case.TestCase,
        err: tuple[type[BaseException], BaseException, object],
    ) -> None:
        """
        Record an errored test result and print it.

        Parameters
        ----------
        test : unittest.case.TestCase
            The test case instance that errored.
        err : tuple[type[BaseException], BaseException, object]
            The exception info tuple for the error.

        Returns
        -------
        None
            This method appends the result and prints it, then calls the
            superclass method.
        """
        result = self.__createTestResult(test, TestStatus.ERRORED, err)
        self.__test_results.append(result)
        self.__printTestResult(result)
        super().addError(test, err)

    def addSkip(
        self,
        test: unittest.case.TestCase,
        reason: str,
    ) -> None:
        """
        Record a skipped test result and print it.

        Parameters
        ----------
        test : unittest.case.TestCase
            The test case instance that was skipped.
        reason : str
            The reason for skipping the test.

        Returns
        -------
        None
            This method appends the result and prints it, then calls the
            superclass method.
        """
        result = self.__createTestResult(test, TestStatus.SKIPPED)
        self.__test_results.append(result)
        self.__printTestResult(result)
        super().addSkip(test, reason)

    def __printTestResult(self, result: TestResult) -> None: # NOSONAR
        """
        Print the result of a test that did not fail.

        Parameters
        ----------
        result : TestResult
            The test result instance to display.

        Returns
        -------
        None
            This method prints the formatted test result to the console and
            does not return a value.
        """
        # Prepare text components for status, test ID, and execution time
        status_text: str = Stringable(result.status).padBoth(9)
        test_id: str = result.name
        exec_time_text: str = f"~ {result.execution_time:.3f}s"

        status_style_map = {
            TestStatus.PASSED: "green",
            TestStatus.SKIPPED: "yellow",
            TestStatus.FAILED: "magenta",
            TestStatus.ERRORED: "red",
        }
        status_style = status_style_map.get(result.status, "white")

        # Only print the test result if the verbosity level is set to 1
        if self._print_verbosity is not None and self._print_verbosity == 1:

            # Calculate filler length for formatting
            max_width: int = int(self.__max_width)
            status_len: int = len(status_text)
            test_id_len: int = len(test_id)
            exec_time_len: int = len(exec_time_text)

            # Length for separators and spaces
            separator_len: int = 6

            # Calculate the length of the filler based on the maximum width
            # and lengths of other components
            filler_length: int = max(
                0,
                max_width - status_len - test_id_len - exec_time_len - separator_len,
            )

            if filler_length < 0:
                # Truncate test name if necessary to fit within max width
                test_id = (
                    test_id[
                        : max(
                            0,
                            max_width - len(status_text) - len(exec_time_text) - 9,
                        )
                    ]
                    + "..."
                )
                filler_length = 0

            filler: str = "." * filler_length
            text_segments: list[Text] = [
                Text(status_text, style=f"bold white on {status_style}"),
                Text(" • ", style="dim"),
                Text(test_id, style="white"),
                Text(" ", style="dim"),
                Text(filler, style="dim"),
                Text(" • ", style="dim"),
                Text(exec_time_text, style="cyan"),
            ]
            formatted_text: Text = Text.assemble(*text_segments)

            # Output formatted test result to console
            self.__console.print(formatted_text)

        elif self._print_verbosity is not None and self._print_verbosity == 2:

            # Define style constants
            bold_white_style: str = "bold bright_white"
            dim_style: str = "dim white"

            text_path = Text(f"📄 Path: {result.file_path}")
            other_texts: list[Text] = []
            if result.status in [TestStatus.ERRORED, TestStatus.FAILED]:
                icon = "❌" if result.status == TestStatus.FAILED else "💥"
                text_path = Text(
                    f"📄 Path: {result.file_path}:{result.line_no}", style="cyan",
                )
                other_texts.append(
                    Text(
                        f"\n{icon} {result.exception}: {result.error_message}\n",
                        style="red",
                    ),
                )
                for line_no, code_line in result.source_code:
                    code_line = (
                        code_line[:70] + "..."
                        if len(code_line) > 73
                        else code_line
                    )
                    if line_no == result.line_no:
                        other_texts.append(
                            Text(
                                f"\n *| {line_no}: {code_line}",
                                style="white on grey23",
                            ),
                        )
                    else:
                        other_texts.append(
                            Text(
                                f"\n  | {line_no}: {code_line}",
                                style="dim white",
                            ),
                        )

            # Create elegant panel with subtle border
            panel = Panel(
                Text.assemble(
                    Text("🔑 "),
                    Text("ID: ", style=bold_white_style),
                    Text(f"{result.id}", style=dim_style),
                    Text(" | ", style=dim_style),
                    Text("📌 "),
                    Text("Name: ", style=bold_white_style),
                    Text(f"{result.name}", style=dim_style),
                    Text("\n"),
                    Text("📁 "),
                    Text("Class: ", style=bold_white_style),
                    Text(f"{result.class_name}", style=dim_style),
                    Text(" | ", style=dim_style),
                    Text("🔧 "),
                    Text("Method: ", style=bold_white_style),
                    Text(f"{result.method}", style=dim_style),
                    Text(" | ", style=dim_style),
                    Text("📦 "),
                    Text("Module: ", style=bold_white_style),
                    Text(f"{result.module}", style=dim_style),
                    Text("\n"),
                    text_path,
                    *other_texts,
                ),
                title=result.status,
                title_align="left",
                subtitle=exec_time_text,
                subtitle_align="right",
                border_style=f"bright_{status_style}",
                width=int(self.__max_width * 0.85),
                padding=(0, 1),
            )
            self.__console.print(panel)

    def __createTestResult(
        self,
        test: unittest.case.TestCase,
        status: TestStatus,
        exc_info: tuple[type[BaseException], BaseException, object] | None = None,
    ) -> TestResult:
        """
        Create and return a TestResult instance for the given test.

        Parameters
        ----------
        test : unittest.case.TestCase
            The test case instance being processed.
        status : TestStatus
            The status of the test (e.g., PASSED, FAILED).
        exc_info : tuple[type[BaseException], BaseException, object] or None, optional
            Exception info tuple as returned by sys.exc_info(), by default None.

        Returns
        -------
        TestResult
            The constructed TestResult object containing test outcome details.
        """
        # Measure elapsed time for the test execution
        elapsed = time.perf_counter() - self.__start_time
        rf_instance = ReflectionInstance(test)

        _traceback = None
        _code: list[tuple[int, str]] = []
        line_no: int | None = None

        # Extract traceback and relevant source code if exception info is provided
        if exc_info and isinstance(exc_info, tuple):
            _traceback = traceback.format_exception(*exc_info)
            for exc in inspect.trace():
                frame = exc.frame
                lineno = exc.lineno
                if rf_instance.getFile() in frame.f_code.co_filename:
                    filename = frame.f_code.co_filename
                    start = max(1, lineno - 2)
                    end = lineno + 1
                    line_no = lineno
                    for i in range(start, end + 1):
                        code_line = linecache.getline(filename, i).rstrip()
                        _code.append((i, code_line))

        # Construct and return the TestResult instance with all relevant information
        return TestResult(
            id=id(test),
            name=test.id(),
            status=status,
            execution_time=elapsed,
            error_message=str(exc_info[1]) if exc_info else None,
            traceback=_traceback,
            class_name=rf_instance.getClassName(),
            method=rf_instance.getAttribute("_testMethodName"),
            module=rf_instance.getModuleName(),
            file_path=rf_instance.getFile(),
            doc_string=rf_instance.getAttributeDocstring("_testMethodName"),
            exception=exc_info[0].__name__ if exc_info else None,
            line_no=line_no,
            source_code=_code,
        )

    def getTestResults(self) -> list[TestResult]:
        """
        Retrieve the list of test results collected during execution.

        Returns
        -------
        list[TestResult]
            A list of TestResult instances representing the outcomes of
            executed tests.
        """
        return self.__test_results
