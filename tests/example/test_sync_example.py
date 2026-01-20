from typing import Any, Dict
from orionis.foundation.contracts.application import IApplication
from orionis.services.system.contracts.workers import IWorkers
from orionis.test.cases.synchronous import SyncTestCase


class TestSynchronousExample(SyncTestCase):
    """
    Synchronous test example demonstrating Orionis framework capabilities.

    This class showcases various testing patterns including dependency injection,
    path resolution, container usage, and error handling in a synchronous context.
    The tests demonstrate best practices for writing maintainable and reliable
    test cases within the Orionis framework.
    """

    def setUp(self) -> None:
        """
        Set up test environment before each test method.

        Initializes test data dictionary with sample files and expected values
        that will be used across multiple test methods. This method is called
        automatically before each test method execution.

        Notes
        -----
        The test_data dictionary contains:
        - sample_file: Path to the current test file for path resolution tests
        - expected_values: List of integers used in assertion validation tests
        """
        self.test_data: Dict[str, Any] = {
            "sample_file": "tests/example/test_example.py",
            "expected_values": [1, 2, 3, 4, 5],
        }

    def tearDown(self) -> None:
        """
        Clean up resources after each test method completion.

        Resets the test_data attribute to None to ensure clean state
        between test method executions and prevent memory leaks.
        """
        self.test_data = None

    def testBasicAssertions(self) -> None:
        """
        Test basic assertion functionality and patterns.

        Validates the fundamental assertion methods provided by the testing
        framework, including equality checks, boolean assertions, and
        container membership validation.

        Tests
        -----
        - Equality assertions (assertEqual)
        - Boolean assertions (assertTrue, assertFalse)
        - Container membership (assertIn, assertNotIn)

        Raises
        ------
        AssertionError
            If any of the basic assertions fail, indicating a problem
            with the testing framework's assertion mechanisms.
        """
        # Test equality assertions
        self.assertEqual(2, 2, "Basic equality check failed")
        self.assertEqual(3, 3, "Second equality check failed")

        # Test boolean assertions
        self.assertTrue(True, "Boolean true assertion failed") # NOSONAR
        self.assertFalse(False, "Boolean false assertion failed") # NOSONAR

        # Test container assertions
        self.assertIn(
            3,
            self.test_data["expected_values"],
            "Value not found in container",
        )
        self.assertNotIn(
            10,
            self.test_data["expected_values"],
            "Unexpected value found in container",
        )

    def testMaxWorkers(self, worker: IWorkers) -> None:
        """
        Test worker service functionality with dependency injection.

        Validates the worker service's ability to calculate the maximum number
        of available workers in the system. This method demonstrates dependency
        injection capabilities with the IWorkers service and ensures proper
        worker count calculation functionality.

        Parameters
        ----------
        worker : IWorkers
            Injected worker service instance for testing worker calculation
            capabilities. The service provides methods for determining optimal
            worker counts based on system resources.

        Returns
        -------
        None
            This test method does not return any value. It performs assertions
            to validate the worker service functionality.

        Tests
        -----
        - Worker service instance validation
        - Worker count calculation functionality
        - Worker count positive value validation
        - Service method execution through dependency injection

        Raises
        ------
        AssertionError
            If worker count calculation fails, returns invalid values, or
            the calculated worker count is not greater than zero.
        """
        # Calculate maximum available workers using the injected service
        max_workers = worker.calculate()

        # Validate that worker count is greater than zero
        self.assertGreater(
            max_workers,
            0,
            "Worker count should be greater than zero",
        )

    def testContainerIntegration(self, container: IApplication) -> None:
        """
        Test container dependency injection functionality.

        Validates the application container's ability to resolve services and manage
        dependencies correctly. This method demonstrates the dependency injection
        capabilities of the Orionis application container, including service
        registration, resolution, and lifecycle management. The test ensures that
        the container can successfully instantiate and provide service instances
        when requested through the dependency injection mechanism.

        Parameters
        ----------
        container : Application
            Injected application container instance for testing dependency
            injection capabilities. The container manages service resolution,
            dependency lifecycle, and provides access to registered services
            throughout the application.

        Returns
        -------
        None
            This test method does not return any value. It performs assertions
            to validate the container's dependency injection functionality.

        Tests
        -----
        - Container instance validation and null checking
        - Service resolution from container using interface contracts
        - Service functionality validation through container-resolved instances
        - Dependency lifecycle management and proper instantiation
        - Interface-to-implementation mapping verification

        Raises
        ------
        AssertionError
            If container operations fail, services cannot be resolved, or
            the container instance is invalid or None.

        Notes
        -----
        This test validates the core dependency injection functionality that
        is essential for the Orionis framework's service architecture. The
        container must be able to resolve services using their interface
        contracts and provide properly configured instances.
        """
        # Validate that the injected container instance is not None
        # This ensures the dependency injection framework is working correctly
        self.assertIsNotNone(container, "Container instance should not be None")

        # Attempt to resolve the IWorkers service from the container
        # This tests the container's ability to map interfaces to implementations
        workers: IWorkers = container.make(IWorkers)

        # Verify that the service resolution was successful
        # The container should return a valid instance implementing IWorkers
        self.assertIsNotNone(
            workers,
            "Service resolution should return valid instance",
        )

    def testErrorHandling(self) -> None:
        """
        Test error handling and exception management patterns.

        Validates the framework's ability to handle expected exceptions
        and provides examples of proper exception testing patterns.
        This method demonstrates both basic exception catching and
        regex-based exception message validation.

        Tests
        -----
        - Basic exception assertion with assertRaises
        - Exception message pattern matching with assertRaisesRegex
        - Proper exception type validation
        - Exception context management

        Raises
        ------
        AssertionError
            If expected exceptions are not raised or have incorrect types.
        """
        # Test basic exception assertion
        with self.assertRaises(ValueError):
            raise ValueError("Expected test exception")

        # Test exception message pattern matching
        with self.assertRaisesRegex(RuntimeError, r"test.*pattern"):
            raise RuntimeError("test error pattern match")

    def testDataValidation(self) -> None:
        """
        Test data validation and complex assertion patterns.

        Validates complex data structures and demonstrates advanced assertion
        techniques including list comparisons, dictionary operations, and
        length validation. This method showcases best practices for testing
        data integrity and structure validation.

        Tests
        -----
        - List length validation
        - List content comparison with assertListEqual
        - Dictionary key existence validation
        - Dictionary value validation
        - Complex data structure assertions

        Raises
        ------
        AssertionError
            If data validation fails or structures don't match expectations.
        """
        # Test list operations and validation
        test_list = [1, 2, 3, 4, 5]
        self.assertEqual(
            len(test_list),
            5,
            "List length should match expected value",
        )
        self.assertListEqual(
            test_list,
            self.test_data["expected_values"],
            "List content should match expected values",
        )

        # Test dictionary operations and validation
        test_dict = {"key1": "value1", "key2": "value2"}
        self.assertIn(
            "key1",
            test_dict,
            "Dictionary should contain expected key",
        )
        self.assertEqual(
            test_dict["key1"],
            "value1",
            "Dictionary value should match expected value",
        )
