from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from orionis.foundation.config.testing.enums import ExecutionMode
from orionis.foundation.contracts.application import IApplication
from orionis.services.system.workers import Workers

class IUnitTest(ABC):

    @abstractmethod
    def configure(
        self,
        *,
        verbosity: int,
        execution_mode: str | ExecutionMode,
        max_workers: int,
        fail_fast: bool,
        print_result: bool,
        throw_exception: bool,
        persistent: bool,
        persistent_driver: str,
        web_report: bool
    ) -> 'IUnitTest':
        """
        Configure the UnitTest instance with the specified parameters.

         Parameters
        ----------
        verbosity : int
            Verbosity level for test output. Must be a non-negative integer.
        execution_mode : str or ExecutionMode
            Mode of test execution. Accepts a string or an ExecutionMode enum member.
        max_workers : int
            Maximum number of worker threads/processes. Must be between 1 and the value returned by Workers().calculate().
        fail_fast : bool
            If True, stops execution upon the first test failure.
        print_result : bool
            If True, prints the test results to the console.
        throw_exception : bool
            If True, raises exceptions on test failures.
        persistent : bool
            If True, enables persistent storage for test results.
        persistent_driver : str
            The driver to use for persistence. Must be either 'sqlite' or 'json'.
        web_report : bool
            If True, enables web-based reporting of test results.

        Returns
        -------
        UnitTest
            The configured UnitTest instance (self), allowing method chaining.

        Raises
        ------
        OrionisTestValueError
            If any parameter is of an invalid type or value.
        """
        pass

    @abstractmethod
    def setApplication(
        self,
        app: 'IApplication'
    ) -> 'IUnitTest':
        """
        Set the application instance for dependency resolution in tests.

        Associates an application instance with the UnitTest object, enabling
        dependency injection for test cases that require services or components
        from the application context. This is essential for tests that depend
        on the application's configuration, services, or lifecycle.

        Parameters
        ----------
        app : IApplication
            The application instance to be used for dependency resolution.
            Must implement the `IApplication` contract.

        Returns
        -------
        UnitTest
            The current UnitTest instance (self), allowing method chaining.

        Raises
        ------
        OrionisTestValueError
            If `app` is not an instance of `IApplication`.

        Notes
        -----
        - This method should be called before running tests that require
          dependency injection.
        - The application instance is used internally by the resolver to
          inject dependencies into test methods.
        """
        pass

    @abstractmethod
    def discoverTestsInFolder(
        self,
        *,
        base_path: str,
        folder_path: str,
        pattern: str,
        test_name_pattern: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> 'IUnitTest':
        """
        Discover and add unit tests from a specified folder to the test suite.

        Searches for test files in the given folder path, optionally filtering by file name pattern,
        test name pattern, and tags. Discovered tests are added to the suite, and information about
        the discovery is recorded.

        Parameters
        ----------
        base_path : str, optional
            The base directory to search for tests.
        folder_path : str
            The relative path to the folder containing test files.
        pattern : str, optional
            The file name pattern to match test files.
        test_name_pattern : Optional[str], optional
            A pattern to filter test names. Defaults to None.
        tags : Optional[List[str]], optional
            A list of tags to filter tests. Defaults to None.

        Returns
        -------
        UnitTest
            The current instance with discovered tests added to the suite.

        Raises
        ------
        OrionisTestValueError
            If any argument is invalid, the folder does not exist, no tests are found,
            or if there are import or discovery errors.
        """
        pass

    @abstractmethod
    def discoverTestsInModule(
        self,
        *,
        module_name: str,
        test_name_pattern: Optional[str] = None
    ) -> 'IUnitTest':
        """
        Discover and add unit tests from a specified module to the test suite.

        Parameters
        ----------
        module_name : str
            The name of the module from which to discover tests. Must be a non-empty string.
        test_name_pattern : Optional[str], optional
            A pattern to filter test names. If provided, only tests matching this pattern will be included.

        Returns
        -------
        UnitTest
            The current instance with the discovered tests added to the suite.

        Raises
        ------
        OrionisTestValueError
            If the module_name is invalid, the test_name_pattern is invalid, the module cannot be imported,
            or any unexpected error occurs during test discovery.

        Notes
        -----
        - The method validates the input parameters before attempting to discover tests.
        - If a test_name_pattern is provided, only tests matching the pattern are included.
        - Information about the discovered tests is appended to the 'discovered_tests' attribute.
        """
        pass

    @abstractmethod
    def run(
        self
    ) -> Dict[str, Any]:
        """
        Executes the test suite, manages output and error buffers, and returns a summary of the test results.

        Parameters
        ----------
        self : object
            Instance of the test runner containing the test suite and configuration.

        Returns
        -------
        summary : Dict[str, Any]
            A dictionary summarizing the test results, including statistics and execution time.

        Raises
        ------
        OrionisTestFailureException
            If the test suite execution fails and `throw_exception` is set to True.

        Notes
        -----
        - Starts a timer to measure execution time.
        - Prints start and finish messages using the printer object.
        - Executes the test suite and captures output and error buffers.
        - Processes and displays the results.
        - Raises an exception if tests fail and exception throwing is enabled.
        """
        pass

    @abstractmethod
    def getTestNames(
        self
    ) -> List[str]:
        """
        Get a list of test names (unique identifiers) from the test suite.

        Returns
        -------
        List[str]
            List of test names (unique identifiers) from the test suite.
        """
        pass

    @abstractmethod
    def getTestCount(
        self
    ) -> int:
        """
        Returns the total number of test cases in the test suite.

        Returns
        -------
        int
            The total number of individual test cases in the suite.
        """
        pass

    @abstractmethod
    def clearTests(
        self
    ) -> None:
        """
        Clear all tests from the current test suite.

        Resets the internal test suite to an empty `unittest.TestSuite`, removing any previously added tests.
        """
        pass

    @abstractmethod
    def getResult(
        self
    ) -> dict:
        """
        Returns the results of the executed test suite.

        Returns
        -------
        UnitTest
            The result of the executed test suite.
        """
        pass

    @abstractmethod
    def getOutputBuffer(
        self
    ) -> int:
        """
        Returns the output buffer used for capturing test results.
        This method returns the internal output buffer that collects the results of the test execution.
        Returns
        -------
        int
            The output buffer containing the results of the test execution.
        """
        pass

    @abstractmethod
    def printOutputBuffer(
        self
    ) -> None:
        """
        Prints the contents of the output buffer to the console.
        This method retrieves the output buffer and prints its contents using the rich console.
        """
        pass

    @abstractmethod
    def getErrorBuffer(
        self
    ) -> int:
        """
        Returns the error buffer used for capturing test errors.
        This method returns the internal error buffer that collects any errors encountered during test execution.
        Returns
        -------
        int
            The error buffer containing the errors encountered during the test execution.
        """
        pass

    @abstractmethod
    def printErrorBuffer(
        self
    ) -> None:
        """
        Prints the contents of the error buffer to the console.
        This method retrieves the error buffer and prints its contents using the rich console.
        """
        pass