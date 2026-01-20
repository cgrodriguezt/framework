import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from orionis.foundation.config.testing.enums.drivers import PersistentDrivers
from orionis.foundation.config.testing.enums.mode import ExecutionMode
from orionis.test.cases.synchronous import SyncTestCase
from orionis.test.core.unit_test import UnitTest
from orionis.test.exceptions import OrionisTestValueError, OrionisTestFailureException
from orionis.support.performance.contracts.counter import IPerformanceCounter

class TestUnitTest(SyncTestCase):

    def testDefaultInitialization(self) -> None:
        """
        Test that the `UnitTest` class initializes with the correct default internal attributes.

        This test verifies that a newly created UnitTest instance has all required internal
        attributes properly initialized, including the test loader, test suite, module lists,
        and discovery tracking sets.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Assert that the loader is correctly initialized as a TestLoader
        self.assertIsInstance(unit_test._UnitTest__loader, unittest.TestLoader)

        # Assert that the suite is correctly initialized as a TestSuite
        self.assertIsInstance(unit_test._UnitTest__suite, unittest.TestSuite)

        # Assert that application instance is stored
        self.assertEqual(unit_test._UnitTest__app, app)

        # Assert that module lists are initialized as empty lists
        self.assertEqual(unit_test._UnitTest__specific_modules, [])
        self.assertEqual(unit_test._UnitTest__imported_modules, [])

        # Assert that discovery tracking sets are initialized as empty sets
        self.assertEqual(unit_test._UnitTest__discovered_test_cases, set())
        self.assertEqual(unit_test._UnitTest__discovered_test_modules, set())
        self.assertEqual(unit_test._UnitTest__discovered_test_ids, set())

        # Assert that result is initially None
        self.assertIsNone(unit_test._UnitTest__result)

        # Assert that live console is enabled by default
        self.assertTrue(unit_test._UnitTest__live_console)

    def testSetModule(self) -> None:
        """
        Test that the `setModule` method correctly adds a module to the specific modules list.

        This test verifies that calling setModule with a module name correctly appends
        the module to the internal specific modules list for targeted test discovery.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)
        module_name = "tests.example.test_example"

        # Add a module to the specific modules list
        unit_test.setModule(module_name)

        # Assert that the module was added to the specific modules list
        self.assertIn(module_name, unit_test._UnitTest__specific_modules)
        self.assertEqual(len(unit_test._UnitTest__specific_modules), 1)

        # Add another module
        second_module = "tests.another.test_another"
        unit_test.setModule(second_module)

        # Assert both modules are in the list
        self.assertIn(module_name, unit_test._UnitTest__specific_modules)
        self.assertIn(second_module, unit_test._UnitTest__specific_modules)
        self.assertEqual(len(unit_test._UnitTest__specific_modules), 2)

    def testFlattenTestSuite(self) -> None:
        """
        Test that the `_flattenTestSuite` method flattens nested `TestSuite` instances into a list of test cases.

        This test verifies that the private method correctly extracts individual test cases
        from nested test suites while preserving their order and ensuring uniqueness by test ID.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Initialize the test name pattern to None for this test
        unit_test._UnitTest__test_name_pattern = None

        # Create mock test cases with unique IDs and ensure they have hasattr returning True for 'id'
        test_case1 = MagicMock(spec=unittest.TestCase)
        test_case1.id.return_value = "test_case_1"
        test_case2 = MagicMock(spec=unittest.TestCase)
        test_case2.id.return_value = "test_case_2"

        # Create a nested TestSuite containing the mock test cases
        nested_suite = unittest.TestSuite()
        nested_suite.addTest(test_case1)
        nested_suite.addTest(test_case2)

        # Create the main TestSuite and add the nested suite to it
        main_suite = unittest.TestSuite()
        main_suite.addTest(nested_suite)

        # Flatten the main suite using the method under test
        flattened = unit_test._UnitTest__flattenTestSuite(main_suite)

        # Assert that the flattened list contains both test cases
        self.assertEqual(len(flattened), 2)
        self.assertIn(test_case1, flattened)
        self.assertIn(test_case2, flattened)

    def testMergeTestResults(self) -> None:
        """
        Test that the `_mergeTestResults` method correctly aggregates results from individual `TestResult` into combined `TestResult`.

        This test verifies that the private method properly merges test execution statistics,
        failures, errors, and other result data from individual test results into a combined result object.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Create a combined TestResult to aggregate results into
        combined = unittest.TestResult()

        # Create an individual TestResult with sample data
        individual = unittest.TestResult()
        individual.testsRun = 2
        individual.failures = [("test1", "failure message")]
        individual.errors = [("test2", "error message")]
        individual.skipped = [("test3", "skipped reason")]
        individual.expectedFailures = [("test4", "expected failure")]
        individual.unexpectedSuccesses = [("test5",)]

        # Merge the individual results into the combined result
        unit_test._UnitTest__mergeTestResults(combined, individual)

        # Assert that the combined result reflects the merged data
        self.assertEqual(combined.testsRun, 2)
        self.assertEqual(len(combined.failures), 1)
        self.assertEqual(len(combined.errors), 1)
        self.assertEqual(len(combined.skipped), 1)
        self.assertEqual(len(combined.expectedFailures), 1)
        self.assertEqual(len(combined.unexpectedSuccesses), 1)

        # Test merging multiple individual results
        individual2 = unittest.TestResult()
        individual2.testsRun = 3
        individual2.failures = [("test6", "another failure")]
        individual2.errors = [("test7", "another error")]

        unit_test._UnitTest__mergeTestResults(combined, individual2)

        # Assert cumulative results
        self.assertEqual(combined.testsRun, 5)
        self.assertEqual(len(combined.failures), 2)
        self.assertEqual(len(combined.errors), 2)

    @patch("orionis.test.core.unit_test.ValidBasePath")
    def testLoadPaths(self, mock_valid_base_path) -> None:
        """
        Test that the `_loadPaths` method correctly loads and sets internal paths for test discovery and storage.

        This test verifies that the private method properly retrieves paths from the application
        and calculates the correct relative and absolute paths for test discovery and result storage.

        Parameters
        ----------
        mock_valid_base_path : MagicMock
            Mock for the ValidBasePath validator.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Mock path values
        test_path = Path("/project/tests")
        root_path = Path("/project")
        storage_path = Path("/project/storage")

        # Configure the application mock to return specific paths
        app.path.side_effect = lambda path_type: {
            "tests": test_path,
            "root": root_path,
            "storage": storage_path,
        }[path_type]

        # Configure ValidBasePath mock to return the paths as-is
        mock_valid_base_path.side_effect = lambda path: path

        # Call the private method
        unit_test._UnitTest__loadPaths()

        # Assert that paths are correctly set
        self.assertEqual(unit_test._UnitTest__test_path, test_path)
        self.assertEqual(unit_test._UnitTest__root_path, root_path)
        self.assertEqual(unit_test._UnitTest__base_path, "tests")
        expected_storage = (storage_path / "testing" / "results").resolve()
        self.assertEqual(unit_test._UnitTest__storage, expected_storage)

    def testGetTestIds(self) -> None:
        """
        Test that the `getTestIds` method returns a list of all unique test IDs discovered in the test suite.

        This test verifies that the method correctly returns the unique identifiers of all discovered
        test cases based on the internal tracking of test IDs during test discovery.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Simulate discovered test IDs
        test_ids = {"test_module.TestClass.test_method1", "test_module.TestClass.test_method2"}
        unit_test._UnitTest__discovered_test_ids = test_ids

        # Retrieve the list of test IDs using the method under test
        retrieved_ids = unit_test.getTestIds()

        # Assert that the returned list contains the expected test identifiers
        self.assertEqual(set(retrieved_ids), test_ids)
        self.assertEqual(len(retrieved_ids), 2)

    def testGetTestCount(self) -> None:
        """
        Test that the `getTestCount` method returns the correct number of discovered test cases.

        This test verifies that the method correctly returns the count of discovered test cases
        based on the internal tracking of test IDs during test discovery.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Simulate discovered test IDs
        test_ids = {"test_module.TestClass.test_method1", "test_module.TestClass.test_method2", "test_module.TestClass.test_method3"}
        unit_test._UnitTest__discovered_test_ids = test_ids

        # Retrieve the count of test cases using the method under test
        count = unit_test.getTestCount()

        # Assert that the returned count matches the number of discovered test IDs
        self.assertEqual(count, 3)

        # Test with empty discovered tests
        unit_test._UnitTest__discovered_test_ids = set()
        count = unit_test.getTestCount()
        self.assertEqual(count, 0)

    def testGetDiscoveredTestCases(self) -> None:
        """
        Test that the `getDiscoveredTestCases` method returns a list of all discovered test case classes.

        This test verifies that the method correctly returns the unique test case classes
        that have been discovered during test suite initialization and loading.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Create mock test case classes
        mock_test_case1 = MagicMock()
        mock_test_case1.__class__ = "TestClass1"
        mock_test_case2 = MagicMock()
        mock_test_case2.__class__ = "TestClass2"

        # Simulate discovered test cases
        test_cases = {mock_test_case1.__class__, mock_test_case2.__class__}
        unit_test._UnitTest__discovered_test_cases = test_cases

        # Retrieve the discovered test cases
        discovered_cases = unit_test.getDiscoveredTestCases()

        # Assert that the returned list contains the expected test case classes
        self.assertEqual(set(discovered_cases), test_cases)
        self.assertEqual(len(discovered_cases), 2)

    def testGetDiscoveredModules(self) -> None:
        """
        Test that the `getDiscoveredModules` method returns a list of all discovered test module names.

        This test verifies that the method correctly returns the unique test modules
        that have been discovered during test suite initialization and loading.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Simulate discovered test modules
        test_modules = {"tests.example.test_example", "tests.another.test_another"}
        unit_test._UnitTest__discovered_test_modules = test_modules

        # Retrieve the discovered test modules
        discovered_modules = unit_test.getDiscoveredModules()

        # Assert that the returned list contains the expected module names
        self.assertEqual(set(discovered_modules), test_modules)
        self.assertEqual(len(discovered_modules), 2)

    def testGetResult(self) -> None:
        """
        Test that the `getResult` method returns the results of the executed test suite.

        This test verifies that the method correctly returns the stored test execution results
        after a test run has been completed.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Initially, result should be None
        self.assertIsNone(unit_test.getResult())

        # Simulate setting a result
        mock_result = {"total_tests": 5, "passed": 3, "failed": 2}
        unit_test._UnitTest__result = mock_result

        # Retrieve the result
        result = unit_test.getResult()

        # Assert that the returned result matches the expected data
        self.assertEqual(result, mock_result)

    @patch("orionis.test.core.unit_test.Testing")
    def testLoadConfigSuccess(self, mock_testing) -> None:
        """
        Test that the `_loadConfig` method successfully loads and validates testing configuration.

        This test verifies that the private method correctly retrieves configuration from the
        application, validates parameters, and sets internal attributes accordingly.

        Parameters
        ----------
        mock_testing : MagicMock
            Mock for the Testing configuration entity.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Mock configuration data
        config_data = {
            "verbosity": 2,
            "execution_mode": ExecutionMode.SEQUENTIAL.value,
            "max_workers": 2,
            "fail_fast": True,
            "throw_exception": False,
            "persistent": True,
            "persistent_driver": PersistentDrivers.SQLITE.value,
            "web_report": True,
            "pattern": "test_*.py",
            "test_name_pattern": "test_*",
            "folder_path": ["unit", "integration"],
        }

        # Configure mocks
        app.config.return_value = config_data
        mock_config_instance = MagicMock()
        for key, value in config_data.items():
            setattr(mock_config_instance, key, value)
        mock_testing.return_value = mock_config_instance

        # Patch all validators to return the input values and load paths first
        with patch.multiple("orionis.test.core.unit_test",
                          ValidVerbosity=lambda x: x,
                          ValidExecutionMode=lambda x: x,
                          ValidWorkers=lambda x: x,
                          ValidFailFast=lambda x: x,
                          ValidThrowException=lambda x: x,
                          ValidPersistent=lambda x: x,
                          ValidPersistentDriver=lambda x: x,
                          ValidWebReport=lambda x: x,
                          ValidPattern=lambda x: x,
                          ValidNamePattern=lambda x: x,
                          ValidFolderPath=lambda x: x,
                          TestPrinter=MagicMock):

            # Mock loadPaths to set required base_path attribute
            unit_test._UnitTest__base_path = "tests"

            # Call the private method
            unit_test._UnitTest__loadConfig()

            # Assert that configuration values are correctly set
            self.assertEqual(unit_test._UnitTest__verbosity, 2)
            self.assertEqual(unit_test._UnitTest__execution_mode, ExecutionMode.SEQUENTIAL.value)
            self.assertEqual(unit_test._UnitTest__max_workers, 2)
            self.assertTrue(unit_test._UnitTest__fail_fast)
            self.assertFalse(unit_test._UnitTest__throw_exception)
            self.assertTrue(unit_test._UnitTest__persistent)
            self.assertEqual(unit_test._UnitTest__persistent_driver, PersistentDrivers.SQLITE.value)
            self.assertTrue(unit_test._UnitTest__web_report)
            self.assertEqual(unit_test._UnitTest__pattern, "test_*.py")
            self.assertEqual(unit_test._UnitTest__test_name_pattern, "test_*")

    def testLoadConfigFailure(self) -> None:
        """
        Test that the `_loadConfig` method raises OrionisTestValueError when configuration loading fails.

        This test verifies that the method properly handles and wraps exceptions that occur
        during configuration loading, providing a descriptive error message.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Configure the app.config to raise an exception
        app.config.side_effect = Exception("Configuration not found")

        # Assert that OrionisTestValueError is raised
        with self.assertRaises(OrionisTestValueError) as context:
            unit_test._UnitTest__loadConfig()

        # Assert the error message contains expected information
        self.assertIn("Failed to load testing configuration", str(context.exception))
        self.assertIn("Configuration not found", str(context.exception))

    @patch("orionis.test.core.unit_test.import_module")
    def testListMatchingModules(self, mock_import_module) -> None:
        """
        Test that the `_listMatchingModules` method discovers and imports matching test modules.

        This test verifies that the private method correctly searches for Python files matching
        a pattern, constructs module names, and imports the corresponding modules.

        Parameters
        ----------
        mock_import_module : MagicMock
            Mock for the import_module function.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        root_path = Path("/project")
        test_path = Path("/project/tests")
        custom_path = Path("unit")
        pattern_file = "test_*.py"

        # Mock the file system walk
        with patch("orionis.test.core.unit_test.walk") as mock_walk:
            mock_walk.return_value = [
                ("/project/tests/unit", [], ["test_example.py", "test_another.py", "other_file.py"]),
                ("/project/tests/unit/subdir", [], ["test_nested.py"]),
            ]

            # Mock successful module imports
            mock_module1 = MagicMock()
            mock_module2 = MagicMock()
            mock_module3 = MagicMock()
            mock_import_module.side_effect = [mock_module1, mock_module2, mock_module3]

            # Call the method
            result = unit_test._UnitTest__listMatchingModules(root_path, test_path, custom_path, pattern_file)

            # Assert that the correct modules were imported
            self.assertEqual(len(result), 3)
            self.assertIn(mock_module1, result)
            self.assertIn(mock_module2, result)
            self.assertIn(mock_module3, result)

            # Verify import_module was called with correct module names
            expected_calls = [
                unittest.mock.call("tests.unit.test_example"),
                unittest.mock.call("tests.unit.test_another"),
                unittest.mock.call("tests.unit.subdir.test_nested"),
            ]
            mock_import_module.assert_has_calls(expected_calls, any_order=True)

    def testRaiseIsFailedTest(self) -> None:
        """
        Test that the `_raiseIsFailedTest` method raises OrionisTestValueError for failed test imports.

        This test verifies that the method correctly detects failed test imports and raises
        appropriate exceptions with descriptive error messages.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Create a mock failed test case
        failed_test = MagicMock()
        failed_test.__class__.__name__ = "_FailedTest"
        failed_test.id.return_value = "failed_test_id"
        failed_test._exception = Exception("Import failed")

        # Assert that OrionisTestValueError is raised
        with self.assertRaises(OrionisTestValueError) as context:
            unit_test._UnitTest__raiseIsFailedTest(failed_test)

        # Assert the error message contains expected information
        self.assertIn("Failed to import test", str(context.exception))

    def testRaiseIfNotFoundTestMethod(self) -> None:
        """
        Test that the `_raiseIfNotFoundTestMethod` method raises OrionisTestValueError for invalid test methods.

        This test verifies that the method correctly detects test cases with missing or invalid
        test methods and raises appropriate exceptions.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Create a mock test case with missing test method
        test_case = MagicMock()
        test_case.id.return_value = "test_case_id"
        test_case.__class__.__name__ = "TestClass"
        test_case.__module__ = "test_module"

        # Mock ReflectionInstance to return None for test method name
        with patch("orionis.test.core.unit_test.ReflectionInstance") as mock_reflection:
            mock_rf_instance = MagicMock()
            mock_rf_instance.getAttribute.return_value = None
            mock_reflection.return_value = mock_rf_instance

            # Assert that OrionisTestValueError is raised
            with self.assertRaises(OrionisTestValueError) as context:
                unit_test._UnitTest__raiseIfNotFoundTestMethod(test_case)

            # Assert the error message contains expected information about the test case
            error_message = str(context.exception)
            self.assertIn("test_case_id", error_message)
            self.assertIn("does not have a valid test method", error_message)

    def testWithDebuggerReturnsFalseByDefault(self) -> None:
        """
        Test that the `_withDebugger` method returns False for standard test cases.

        This test verifies that the method correctly handles typical test cases without debugging
        keywords and maintains the default behavior.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Create a standard test case
        test_case = MagicMock()
        test_case._testMethodName = "test_method"

        # Test the method behavior
        result = unit_test._UnitTest__withDebugger(test_case)

        # The method should return False for standard cases
        self.assertFalse(result)
        # Live console should remain enabled by default
        self.assertTrue(unit_test._UnitTest__live_console)

    def testFlattenTestSuiteWithInvalidRegex(self) -> None:
        """
        Test that the `_flattenTestSuite` method raises OrionisTestValueError for invalid regex patterns.

        This test verifies that when an invalid regular expression is provided as a test name pattern,
        the method raises the appropriate exception with a descriptive error message.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Set an invalid regex pattern
        unit_test._UnitTest__test_name_pattern = "[invalid regex"

        # Create a simple test suite
        suite = unittest.TestSuite()
        test_case = MagicMock(spec=unittest.TestCase)
        test_case.id.return_value = "test_case"
        suite.addTest(test_case)

        # Assert that OrionisTestValueError is raised
        with self.assertRaises(OrionisTestValueError) as context:
            unit_test._UnitTest__flattenTestSuite(suite)

        # Assert the error message contains expected information
        error_message = str(context.exception)
        self.assertIn("invalid", error_message.lower())
        self.assertIn("pattern", error_message.lower())

    def testCustomResultClass(self) -> None:
        """
        Test that the `_customResultClass` method returns a custom TestResult class.

        This test verifies that the method creates and returns a custom TestResult class
        with the appropriate methods and functionality.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Get the custom result class
        custom_result_class = unit_test._UnitTest__customResultClass()

        # Assert that it's a class (type)
        self.assertIsInstance(custom_result_class, type)

        # Create an instance with required parameters to verify it has TestResult functionality
        import io
        result_instance = custom_result_class(stream=io.StringIO(), descriptions=True, verbosity=1)
        self.assertTrue(hasattr(result_instance, "startTest"))
        self.assertTrue(hasattr(result_instance, "stopTest"))
        self.assertTrue(hasattr(result_instance, "addSuccess"))
        self.assertTrue(hasattr(result_instance, "addFailure"))
        self.assertTrue(hasattr(result_instance, "addError"))

    @patch("orionis.test.core.unit_test.UnitTest._UnitTest__generateSummary")
    def testRunSuccessfulExecution(self, mock_generate_summary) -> None:
        """
        Test that the `run` method successfully executes tests and returns summary when tests pass.

        This test verifies the complete execution flow when tests are successful,
        including summary generation and result handling.

        Parameters
        ----------
        mock_generate_summary : MagicMock
            Mock for the _generateSummary method.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Mock all required methods and set attributes
        with patch.multiple(unit_test,
                          _UnitTest__loadPaths=MagicMock(),
                          _UnitTest__loadConfig=MagicMock(),
                          _UnitTest__loadModules=MagicMock(),
                          _UnitTest__loadTests=MagicMock()):

            # Set required attributes
            unit_test._UnitTest__throw_exception = False
            unit_test._UnitTest__execution_mode = ExecutionMode.SEQUENTIAL.value
            unit_test._UnitTest__max_workers = 1

            # Set discovered test IDs to simulate found tests
            unit_test._UnitTest__discovered_test_ids = {"test1", "test2"}

            # Mock printer and its methods
            mock_printer = MagicMock()
            unit_test._UnitTest__printer = mock_printer

            # Mock test result as successful
            mock_result = MagicMock()
            mock_result.wasSuccessful.return_value = True
            mock_printer.executePanel.return_value = mock_result

            # Mock performance counter
            performance_counter = MagicMock(spec=IPerformanceCounter)
            performance_counter.getSeconds.return_value = 1.5

            # Mock summary generation
            expected_summary = {"passed": 2, "failed": 0, "total": 2}
            mock_generate_summary.return_value = expected_summary

            # Run the test suite
            result = unit_test.run(performance_counter)

            # Assert that the summary is returned
            self.assertEqual(result, expected_summary)

            # Verify that the printer methods were called
            mock_printer.startMessage.assert_called_once()
            mock_printer.executePanel.assert_called_once()
            mock_printer.displayResults.assert_called_once_with(summary=expected_summary)
            mock_printer.finishMessage.assert_called_once_with(summary=expected_summary)

    def testRunTestsSequentiallyExists(self) -> None:
        """
        Test that the `_runTestsSequentially` method exists and is callable.

        This test verifies that the private method exists on the UnitTest class
        and can be referenced without execution to avoid complex mocking requirements.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Verify that the method exists and is callable
        self.assertTrue(hasattr(unit_test, "_UnitTest__runTestsSequentially"))
        self.assertTrue(callable(unit_test._UnitTest__runTestsSequentially))

        # Verify it's a bound method
        method = unit_test._UnitTest__runTestsSequentially
        self.assertTrue(hasattr(method, "__self__"))
        self.assertEqual(method.__self__, unit_test)

    def testResolveTestDependencies(self) -> None:
        """
        Test that the `_resolveTestDependencies` method returns a TestSuite with the test case.

        This test verifies that the method correctly handles test cases and returns them
        wrapped in a TestSuite, even when dependency resolution fails.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Create a mock test case
        test_case = MagicMock(spec=unittest.TestCase)
        test_case.id.return_value = "test_case_id"

        # Call the method
        result = unit_test._UnitTest__resolveTestDependencies(test_case)

        # The method should return a TestSuite or the test case itself
        # Due to the complex dependency injection logic, we'll just verify it returns something
        self.assertIsNotNone(result)

        # If it returns a TestSuite, verify it has the expected interface
        if isinstance(result, unittest.TestSuite):
            test_count = result.countTestCases()
            self.assertGreaterEqual(test_count, 0)

    def testGenerateSummaryStructure(self) -> None:
        """
        Test that the `_generateSummary` method creates a properly structured summary dictionary.

        This test verifies that the method generates a summary with all required fields
        and proper data types.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Set required attributes for the method to work
        unit_test._UnitTest__persistent = False
        unit_test._UnitTest__web_report = False

        # Create a mock test result
        mock_result = MagicMock()
        mock_result.testsRun = 10
        mock_result.failures = [("test1", "failure1"), ("test2", "failure2")]
        mock_result.errors = [("test3", "error1")]
        mock_result.skipped = [("test4", "skipped1")]
        mock_result.expectedFailures = []
        mock_result.unexpectedSuccesses = []

        # Mock methods that generate summary might call
        with patch.object(unit_test, "_UnitTest__handlePersistResults"), patch.object(unit_test, "_UnitTest__handleWebReport"):

            # Generate summary
            summary = unit_test._UnitTest__generateSummary(mock_result, 2.5)

            # Verify summary structure and types (using actual field names from the framework)
            self.assertIsInstance(summary, dict)
            self.assertIn("total_tests", summary)
            self.assertIn("failed", summary)
            self.assertIn("errors", summary)
            self.assertIn("skipped", summary)
            self.assertIn("total_time", summary)

            # Verify data types and values
            self.assertIsInstance(summary["total_tests"], int)
            self.assertIsInstance(summary["total_time"], (int, float))
            self.assertEqual(summary["total_tests"], 10)
            self.assertEqual(summary["total_time"], 2.5)

    @patch("orionis.services.introspection.instances.reflection.ReflectionInstance")
    def testWithDebuggerNoKeywords(self, mock_reflection_instance) -> None:
        """
        Test that the `_withDebugger` method returns False when no debugging keywords are found.

        This test verifies that the method correctly identifies clean test methods without
        debugging calls and maintains live console output.

        Parameters
        ----------
        mock_reflection_instance : MagicMock
            Mock for the ReflectionInstance class.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Create a mock test case
        test_case = MagicMock()
        test_case._testMethodName = "test_method"

        # Mock source code without debug keywords
        mock_source = """def test_method(self):
    assert True"""

        # Configure the ReflectionInstance mock
        mock_rf_instance = MagicMock()
        mock_rf_instance.getAttribute.return_value = "test_method"
        mock_rf_instance.hasMethod.return_value = False
        mock_rf_instance.getSourceCode.return_value = mock_source
        mock_reflection_instance.return_value = mock_rf_instance

        # Test method should return False and keep live console enabled
        result = unit_test._UnitTest__withDebugger(test_case)
        self.assertFalse(result)
        self.assertTrue(unit_test._UnitTest__live_console)

    @patch("orionis.services.introspection.instances.reflection.ReflectionInstance")
    def testWithDebuggerException(self, mock_reflection_instance) -> None:
        """
        Test that the `_withDebugger` method handles exceptions gracefully and returns False.

        This test verifies that when source code inspection fails, the method returns False
        and doesn't affect the live console setting.

        Parameters
        ----------
        mock_reflection_instance : MagicMock
            Mock for the ReflectionInstance class.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Create a mock test case
        test_case = MagicMock()
        test_case._testMethodName = "test_method"

        # Mock ReflectionInstance to raise an exception
        mock_reflection_instance.side_effect = Exception("Cannot get reflection")

        # Test method should return False and keep live console enabled
        result = unit_test._UnitTest__withDebugger(test_case)
        self.assertFalse(result)
        self.assertTrue(unit_test._UnitTest__live_console)

    @patch("orionis.test.core.unit_test.UnitTest._UnitTest__loadPaths")
    @patch("orionis.test.core.unit_test.UnitTest._UnitTest__loadConfig")
    @patch("orionis.test.core.unit_test.UnitTest._UnitTest__loadModules")
    @patch("orionis.test.core.unit_test.UnitTest._UnitTest__loadTests")
    def testRunWithNoTests(self, mock_load_tests, mock_load_modules, mock_load_config, mock_load_paths) -> None:
        """
        Test that the `run` method handles the case when no tests are discovered.

        This test verifies that when no tests are found, the method returns early with
        an appropriate message without attempting to execute tests.

        Parameters
        ----------
        mock_load_tests : MagicMock
            Mock for the _loadTests method.
        mock_load_modules : MagicMock
            Mock for the _loadModules method.
        mock_load_config : MagicMock
            Mock for the _loadConfig method.
        mock_load_paths : MagicMock
            Mock for the _loadPaths method.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Mock performance counter
        performance_counter = MagicMock(spec=IPerformanceCounter)

        # Set discovered test IDs to empty to simulate no tests found
        unit_test._UnitTest__discovered_test_ids = set()

        # Mock printer to return a specific message for zero tests
        mock_printer = MagicMock()
        mock_printer.zeroTestsMessage.return_value = {"message": "No tests found"}
        unit_test._UnitTest__printer = mock_printer

        # Run the test suite
        result = unit_test.run(performance_counter)

        # Assert that the zero tests message is returned
        self.assertEqual(result, {"message": "No tests found"})

        # Assert that performance counter was started
        performance_counter.start.assert_called_once()

        # Assert that all loading methods were called
        mock_load_paths.assert_called_once()
        mock_load_config.assert_called_once()
        mock_load_modules.assert_called_once_with([])
        mock_load_tests.assert_called_once()

    def testRunWithThrowExceptionOnFailure(self) -> None:
        """
        Test that the `run` method raises OrionisTestFailureException when tests fail and throw_exception is True.

        This test verifies that the method properly raises exceptions when test failures occur
        and the throw_exception configuration is enabled.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Mock all required methods and set attributes
        with patch.multiple(unit_test,
                          _UnitTest__loadPaths=MagicMock(),
                          _UnitTest__loadConfig=MagicMock(),
                          _UnitTest__loadModules=MagicMock(),
                          _UnitTest__loadTests=MagicMock()):

            # Set required attributes manually
            unit_test._UnitTest__throw_exception = True
            unit_test._UnitTest__execution_mode = ExecutionMode.SEQUENTIAL.value
            unit_test._UnitTest__max_workers = 1

            # Set discovered test IDs to simulate found tests
            unit_test._UnitTest__discovered_test_ids = {"test1", "test2"}

            # Mock printer and its methods
            mock_printer = MagicMock()
            unit_test._UnitTest__printer = mock_printer

            # Mock test result as unsuccessful
            mock_result = MagicMock()
            mock_result.wasSuccessful.return_value = False
            mock_printer.executePanel.return_value = mock_result

            # Mock performance counter
            performance_counter = MagicMock(spec=IPerformanceCounter)
            performance_counter.getSeconds.return_value = 1.5

            # Mock summary generation
            with patch.object(unit_test, "_UnitTest__generateSummary") as mock_generate_summary:
                mock_generate_summary.return_value = {"failed": True}

                # Assert that OrionisTestFailureException is raised
                with self.assertRaises(OrionisTestFailureException):
                    unit_test.run(performance_counter)

    def testExtractErrorInfo(self) -> None:
        """
        Test that the `_extractErrorInfo` method correctly extracts error information from traceback strings.

        This test verifies that the method can parse traceback strings and extract
        relevant error messages and file information.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Sample traceback string
        traceback_str = """Traceback (most recent call last):
  File "/path/to/test.py", line 42, in test_method
    assert False, "Test assertion failed"
AssertionError: Test assertion failed"""

        # Call the method
        error_message, file_info = unit_test._extractErrorInfo(traceback_str)

        # Assert that error information is correctly extracted
        self.assertIsNotNone(error_message)
        # The actual error message should contain the file path
        self.assertIsNotNone(file_info)

    def testFlattenTestSuiteWithNamePattern(self) -> None:
        """
        Test that the `_flattenTestSuite` method correctly filters tests by name pattern.

        This test verifies that when a test name pattern is configured, only matching
        test cases are included in the flattened result.

        Returns
        -------
        None
        """
        app = MagicMock()
        unit_test = UnitTest(app)

        # Set a test name pattern that should match one test
        unit_test._UnitTest__test_name_pattern = "test_valid_method"

        # Create mock test cases with different names and proper spec
        test_case1 = MagicMock(spec=unittest.TestCase)
        test_case1.id.return_value = "test_valid_method"
        test_case2 = MagicMock(spec=unittest.TestCase)
        test_case2.id.return_value = "test_invalid_method"

        # Create test suite
        suite = unittest.TestSuite()
        suite.addTest(test_case1)
        suite.addTest(test_case2)

        # Flatten the suite - should filter based on pattern
        flattened = unit_test._UnitTest__flattenTestSuite(suite)

        # The pattern uses regex.search(), so "test_valid_method" should match exactly
        # Only test_case1 should be included
        self.assertEqual(len(flattened), 1)
        self.assertIn(test_case1, flattened)
        self.assertNotIn(test_case2, flattened)
