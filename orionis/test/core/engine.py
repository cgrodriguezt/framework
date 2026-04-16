import asyncio
import fnmatch
import json
import time
import unittest
from typing import Self, TYPE_CHECKING
from orionis.foundation.contracts.application import IApplication
from orionis.test.cases.case import TestCase
from orionis.test.contracts.engine import ITestingEngine
from orionis.test.executors.runner import TestRunner
from orionis.test.executors.results import TestResultProcessor

if TYPE_CHECKING:
    from pathlib import Path
    from collections.abc import Generator
    from orionis.test.entities.result import TestResult

class TestingEngine(ITestingEngine):

    # ruff: noqa: TC001

    def __init__(
        self,
        app: IApplication,
    ) -> None:
        """
        Initialize the TestingEngine with application configuration.

        Parameters
        ----------
        app : IApplication
            Application instance providing configuration values.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Retrieve configuration values from the application instance.
        self.__verbosity: int = app.config("testing.verbosity")
        self.__fail_fast: bool = app.config("testing.fail_fast") in [
            1, True, "1", "true", "True",
        ]
        self.__start_dir: str = app.config("testing.start_dir")
        self.__file_pattern: str = app.config("testing.file_pattern")
        self.__method_pattern: str = app.config("testing.method_pattern")
        self.__json_cache: bool = app.config("testing.cache_results")
        self.__cache_folder: Path = (
            app.path("storage") / "framework" / "cache" / "testing"
        )
        self.__with_panel: bool = True  # Default to showing the start panel
        self.__suite: unittest.TestSuite = unittest.TestSuite()

    def setVerbosity(self, verbosity: int) -> Self:
        """
        Set the verbosity level for the testing engine.

        Parameters
        ----------
        verbosity : int
            Verbosity level to set.

        Returns
        -------
        Self
            Returns self for method chaining.
        """
        self.__verbosity = verbosity
        return self

    def setFailFast(self, *, fail_fast: bool) -> Self:
        """
        Set the fail-fast behavior for the testing engine.

        Parameters
        ----------
        fail_fast : bool
            Whether to stop on first failure.

        Returns
        -------
        Self
            Returns self for method chaining.
        """
        self.__fail_fast = fail_fast
        return self

    def setStartDir(self, start_dir: str) -> Self:
        """
        Set the start directory for test discovery.

        Parameters
        ----------
        start_dir : str
            Directory to start test discovery from.

        Returns
        -------
        Self
            Returns self for method chaining.
        """
        self.__start_dir = start_dir
        return self

    def setFilePattern(self, file_pattern: str) -> Self:
        """
        Set the file pattern for test file discovery.

        Parameters
        ----------
        file_pattern : str
            Pattern to match test files.

        Returns
        -------
        Self
            Returns self for method chaining.
        """
        self.__file_pattern = file_pattern
        return self

    def setMethodPattern(self, method_pattern: str) -> Self:
        """
        Set the method pattern for test method discovery.

        Parameters
        ----------
        method_pattern : str
            Pattern to match test methods.

        Returns
        -------
        Self
            Returns self for method chaining.
        """
        # Update the method pattern in TestCase to ensure
        # test methods are correctly identified.
        TestCase.setMethodPattern(method_pattern)

        # Update the method pattern in the engine for internal use.
        self.__method_pattern = method_pattern
        return self

    def withoutPanel(self) -> Self:
        """
        Disable the start panel display for the testing engine.

        Returns
        -------
        Self
            Returns self for method chaining.
        """
        self.__with_panel = False
        return self

    def __extractTests(
        self, test_suite: unittest.TestSuite,
    ) -> Generator[unittest.TestCase]:
        """
        Extract individual test cases from a test suite recursively.

        Parameters
        ----------
        test_suite : unittest.TestSuite
            Test suite to extract test cases from.

        Returns
        -------
        Generator[unittest.TestCase, None, None]
            Generator yielding individual test cases.
        """
        # Recursively extract test cases from nested suites.
        for test in test_suite:
            if isinstance(test, unittest.TestSuite):
                yield from self.__extractTests(test)
            else:
                yield test

    def discover(self) -> unittest.TestSuite:
        """
        Discover and filter tests using configuration parameters.

        Returns
        -------
        unittest.TestSuite
            Test suite containing filtered test cases.
        """
        # Discover tests by directory and file pattern.
        suite: unittest.TestSuite = unittest.defaultTestLoader.discover(
            start_dir=self.__start_dir,
            pattern=self.__file_pattern,
            top_level_dir=None,
        )

        # Filter test methods according to the method pattern.
        filtered_suite: unittest.TestSuite = unittest.TestSuite()
        for test_case in self.__extractTests(suite):
            method_name = getattr(test_case, "_testMethodName", None)
            if method_name and fnmatch.fnmatch(method_name, self.__method_pattern):
                filtered_suite.addTest(test_case)
        return filtered_suite

    async def __saveCache(self, results: list[TestResult]) -> None:
        """
        Save test results to a JSON cache file asynchronously.

        Parameters
        ----------
        results : list[TestResult]
            List of test results to save.

        Returns
        -------
        None
            This method does not return a value.
        """
        # If JSON caching is disabled or cache folder is not set, skip saving.
        if not self.__json_cache or not self.__cache_folder:
            return

        # Ensure the cache folder exists
        self.__cache_folder.mkdir(parents=True, exist_ok=True)

        data = [result.toDict() for result in results]
        timestamp = int(time.time())
        full_path = self.__cache_folder / f"{timestamp}.json"

        # Use asyncio to write the file asynchronously
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: full_path.write_text(
                json.dumps(data, indent=4, default=str),
                encoding="utf-8",
            ),
        )

    async def run(self) -> list[TestResult]:
        """
        Run the discovered test suite asynchronously.

        Adds discovered tests to the suite, sets verbosity, and executes the tests
        using a thread pool to avoid blocking. Saves results to cache if enabled.

        Returns
        -------
        list[TestResult]
            List of TestResult objects containing test execution outcomes.
        """
        # Add discovered tests to the suite.
        self.__suite.addTests(self.discover())

        # Set verbosity level in TestResult for output formatting.
        TestResultProcessor.setPrintVerbosity(self.__verbosity)

        # Create runner with current configuration.
        runner = TestRunner(
            verbosity=0,  # Keep at 0 to manage detail printing from TestResult.
            failfast=self.__fail_fast,
            with_panel=self.__with_panel,
        )

        # Execute tests in thread pool to avoid blocking.
        loop = asyncio.get_event_loop()
        result: TestResultProcessor = await loop.run_in_executor(
            None, runner.run, self.__suite,
        )
        results = result.getTestResults()
        await self.__saveCache(results)
        return results
