from orionis.test.cases.synchronous import SyncTestCase
from orionis.test.entities.result import TestResult
from orionis.test.enums import TestStatus

class TestTestingResult(SyncTestCase):

    def testDefaultValues(self) -> None:
        """
        Test that optional fields in TestResult are set to None by default.

        Checks that the fields `error_message`, `traceback`, `class_name`, `method`, `module`, and `file_path`
        are None when not provided during initialization.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Create a TestResult instance with only required fields
        result = TestResult(
            id=1,
            name="Sample Test",
            status=TestStatus.PASSED,
            execution_time=0.5
        )
        # Assert that all optional fields are set to None by default
        self.assertIsNone(result.error_message)
        self.assertIsNone(result.traceback)
        self.assertIsNone(result.class_name)
        self.assertIsNone(result.method)
        self.assertIsNone(result.module)
        self.assertIsNone(result.file_path)

    def testRequiredFields(self) -> None:
        """
        Test that TestResult enforces required fields during initialization.

        Verifies that omitting required fields raises a TypeError.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Attempt to create TestResult with no arguments; should raise TypeError
        with self.assertRaises(TypeError):
            TestResult()  # Missing all required fields

        # Attempt to create TestResult missing the 'id' field; should raise TypeError
        with self.assertRaises(TypeError):
            TestResult(
                name="Sample Test",
                status=TestStatus.PASSED,
                execution_time=0.5
            )

    def testImmutable(self) -> None:
        """
        Test that TestResult instances are immutable.

        Ensures that modifying an attribute of a TestResult instance raises an exception.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Create a TestResult instance
        result = TestResult(
            id=1,
            name="Sample Test",
            status=TestStatus.PASSED,
            execution_time=0.5
        )
        # Attempt to modify an attribute; should raise an exception due to immutability
        with self.assertRaises(Exception):
            result.name = "Modified Name"

    def testStatusValues(self) -> None:
        """
        Test that all TestStatus enum values can be assigned to TestResult.

        Iterates through each TestStatus value and checks assignment to the status field.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Iterate through all possible TestStatus values
        for status in TestStatus:
            # Create a TestResult instance with the current status
            result = TestResult(
                id=1,
                name="Status Test",
                status=status,
                execution_time=0.1
            )
            # Assert that the status field matches the assigned value
            self.assertEqual(result.status, status)

    def testErrorFields(self) -> None:
        """
        Test that error_message and traceback fields are stored correctly in TestResult.

        Verifies that providing values for error_message and traceback sets them as expected.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        error_msg = "Test failed"
        traceback = "Traceback info"
        # Create a TestResult instance with error fields
        result = TestResult(
            id=1,
            name="Failing Test",
            status=TestStatus.FAILED,
            execution_time=0.2,
            error_message=error_msg,
            traceback=traceback
        )
        # Assert that error_message and traceback fields are set correctly
        self.assertEqual(result.error_message, error_msg)
        self.assertEqual(result.traceback, traceback)

    def testAllFieldsPopulated(self) -> None:
        """
        Test that TestResult correctly stores all fields when provided.

        Verifies that all optional and required fields are set correctly when
        provided during initialization.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Create a TestResult instance with all fields populated
        result = TestResult(
            id="test_123",
            name="Complete Test",
            status=TestStatus.PASSED,
            execution_time=1.5,
            error_message="No error",
            traceback="No traceback",
            class_name="TestClass",
            method="test_method",
            module="test_module",
            file_path="/path/to/test.py",
            doc_string="Test documentation",
            exception=ValueError("Test exception")
        )
        # Assert all fields are set correctly
        self.assertEqual(result.id, "test_123")
        self.assertEqual(result.name, "Complete Test")
        self.assertEqual(result.status, TestStatus.PASSED)
        self.assertEqual(result.execution_time, 1.5)
        self.assertEqual(result.error_message, "No error")
        self.assertEqual(result.traceback, "No traceback")
        self.assertEqual(result.class_name, "TestClass")
        self.assertEqual(result.method, "test_method")
        self.assertEqual(result.module, "test_module")
        self.assertEqual(result.file_path, "/path/to/test.py")
        self.assertEqual(result.doc_string, "Test documentation")
        self.assertIsInstance(result.exception, ValueError)

    def testExecutionTimeBoundaryValues(self) -> None:
        """
        Test TestResult with boundary values for execution_time field.

        Verifies that the execution_time field accepts zero, very small positive
        values, and large values correctly.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Test with zero execution time
        result_zero = TestResult(
            id=1,
            name="Zero Time Test",
            status=TestStatus.PASSED,
            execution_time=0.0
        )
        self.assertEqual(result_zero.execution_time, 0.0)

        # Test with very small execution time
        result_small = TestResult(
            id=2,
            name="Small Time Test",
            status=TestStatus.PASSED,
            execution_time=0.001
        )
        self.assertEqual(result_small.execution_time, 0.001)

        # Test with large execution time
        result_large = TestResult(
            id=3,
            name="Large Time Test",
            status=TestStatus.PASSED,
            execution_time=9999.999
        )
        self.assertEqual(result_large.execution_time, 9999.999)

    def testStringFieldEdgeCases(self) -> None:
        """
        Test TestResult with edge cases for string fields.

        Verifies that string fields handle empty strings, very long strings,
        and special characters correctly.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Test with empty strings
        result_empty = TestResult(
            id=1,
            name="",
            status=TestStatus.PASSED,
            execution_time=0.1,
            error_message="",
            traceback="",
            class_name="",
            method="",
            module="",
            file_path="",
            doc_string=""
        )
        self.assertEqual(result_empty.name, "")
        self.assertEqual(result_empty.error_message, "")
        self.assertEqual(result_empty.class_name, "")

        # Test with long strings
        long_string = "a" * 1000
        result_long = TestResult(
            id=2,
            name=long_string,
            status=TestStatus.PASSED,
            execution_time=0.1,
            error_message=long_string,
            doc_string=long_string
        )
        self.assertEqual(result_long.name, long_string)
        self.assertEqual(result_long.error_message, long_string)
        self.assertEqual(result_long.doc_string, long_string)

        # Test with special characters
        special_string = "Test with 特殊字符 and émojis 🎉 and\nnewlines\tand\ttabs"
        result_special = TestResult(
            id=3,
            name=special_string,
            status=TestStatus.PASSED,
            execution_time=0.1,
            error_message=special_string
        )
        self.assertEqual(result_special.name, special_string)
        self.assertEqual(result_special.error_message, special_string)

    def testExceptionField(self) -> None:
        """
        Test TestResult with various exception types in the exception field.

        Verifies that the exception field correctly stores different types of
        BaseException instances.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Test with ValueError
        value_error = ValueError("Test value error")
        result_value_error = TestResult(
            id=1,
            name="Value Error Test",
            status=TestStatus.ERRORED,
            execution_time=0.1,
            exception=value_error
        )
        self.assertEqual(result_value_error.exception, value_error)
        self.assertIsInstance(result_value_error.exception, ValueError)

        # Test with TypeError
        type_error = TypeError("Test type error")
        result_type_error = TestResult(
            id=2,
            name="Type Error Test",
            status=TestStatus.ERRORED,
            execution_time=0.1,
            exception=type_error
        )
        self.assertEqual(result_type_error.exception, type_error)
        self.assertIsInstance(result_type_error.exception, TypeError)

        # Test with custom exception
        class CustomException(Exception):
            pass

        custom_error = CustomException("Custom error message")
        result_custom = TestResult(
            id=3,
            name="Custom Error Test",
            status=TestStatus.ERRORED,
            execution_time=0.1,
            exception=custom_error
        )
        self.assertEqual(result_custom.exception, custom_error)
        self.assertIsInstance(result_custom.exception, CustomException)

    def testDocStringField(self) -> None:
        """
        Test TestResult with various doc_string field values.

        Verifies that the doc_string field correctly stores different types of
        documentation strings including multi-line docstrings.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Test with simple docstring
        simple_doc = "Simple test documentation"
        result_simple = TestResult(
            id=1,
            name="Simple Doc Test",
            status=TestStatus.PASSED,
            execution_time=0.1,
            doc_string=simple_doc
        )
        self.assertEqual(result_simple.doc_string, simple_doc)

        # Test with multi-line docstring
        multiline_doc = """
        This is a multi-line docstring.

        It contains multiple paragraphs and
        various formatting elements.

        Parameters
        ----------
        param1 : str
            Description of parameter 1

        Returns
        -------
        bool
            Description of return value
        """
        result_multiline = TestResult(
            id=2,
            name="Multiline Doc Test",
            status=TestStatus.PASSED,
            execution_time=0.1,
            doc_string=multiline_doc
        )
        self.assertEqual(result_multiline.doc_string, multiline_doc)

    def testDataclassEquality(self) -> None:
        """
        Test TestResult equality comparison between instances.

        Verifies that two TestResult instances with identical field values
        are considered equal, and instances with different values are not equal.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Create two identical TestResult instances
        result1 = TestResult(
            id=1,
            name="Equality Test",
            status=TestStatus.PASSED,
            execution_time=0.5,
            error_message="No error"
        )
        result2 = TestResult(
            id=1,
            name="Equality Test",
            status=TestStatus.PASSED,
            execution_time=0.5,
            error_message="No error"
        )
        # Assert that identical instances are equal
        self.assertEqual(result1, result2)

        # Create a different TestResult instance
        result3 = TestResult(
            id=2,
            name="Different Test",
            status=TestStatus.FAILED,
            execution_time=1.0,
            error_message="Test failed"
        )
        # Assert that different instances are not equal
        self.assertNotEqual(result1, result3)

    def testDataclassHashing(self) -> None:
        """
        Test TestResult hashing functionality for frozen dataclass.

        Verifies that TestResult instances can be used as dictionary keys
        and that equal instances produce the same hash.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Create two identical TestResult instances
        result1 = TestResult(
            id=1,
            name="Hash Test",
            status=TestStatus.PASSED,
            execution_time=0.5
        )
        result2 = TestResult(
            id=1,
            name="Hash Test",
            status=TestStatus.PASSED,
            execution_time=0.5
        )
        # Assert that identical instances have the same hash
        self.assertEqual(hash(result1), hash(result2))

        # Test using TestResult as dictionary key
        test_dict = {result1: "test_value"}
        self.assertEqual(test_dict[result2], "test_value")

    def testIdFieldTypes(self) -> None:
        """
        Test TestResult with different types for the id field.

        Verifies that the id field accepts various data types including
        strings, integers, and other hashable objects.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Test with integer id
        result_int = TestResult(
            id=42,
            name="Integer ID Test",
            status=TestStatus.PASSED,
            execution_time=0.1
        )
        self.assertEqual(result_int.id, 42)
        self.assertIsInstance(result_int.id, int)

        # Test with string id
        result_str = TestResult(
            id="test_string_id",
            name="String ID Test",
            status=TestStatus.PASSED,
            execution_time=0.1
        )
        self.assertEqual(result_str.id, "test_string_id")
        self.assertIsInstance(result_str.id, str)

        # Test with tuple id
        tuple_id = ("module", "class", "method")
        result_tuple = TestResult(
            id=tuple_id,
            name="Tuple ID Test",
            status=TestStatus.PASSED,
            execution_time=0.1
        )
        self.assertEqual(result_tuple.id, tuple_id)
        self.assertIsInstance(result_tuple.id, tuple)

    def testPathFieldsWithVariousFormats(self) -> None:
        """
        Test TestResult with various file path formats.

        Verifies that the file_path field handles different path formats
        including absolute paths, relative paths, and paths with special characters.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        # Test with absolute Unix path
        unix_path = "/home/user/project/tests/test_module.py"
        result_unix = TestResult(
            id=1,
            name="Unix Path Test",
            status=TestStatus.PASSED,
            execution_time=0.1,
            file_path=unix_path
        )
        self.assertEqual(result_unix.file_path, unix_path)

        # Test with Windows path
        windows_path = r"C:\Users\User\Project\tests\test_module.py"
        result_windows = TestResult(
            id=2,
            name="Windows Path Test",
            status=TestStatus.PASSED,
            execution_time=0.1,
            file_path=windows_path
        )
        self.assertEqual(result_windows.file_path, windows_path)

        # Test with relative path
        relative_path = "./tests/unit/test_module.py"
        result_relative = TestResult(
            id=3,
            name="Relative Path Test",
            status=TestStatus.PASSED,
            execution_time=0.1,
            file_path=relative_path
        )
        self.assertEqual(result_relative.file_path, relative_path)

    def testFailedTestWithCompleteErrorInfo(self) -> None:
        """
        Test TestResult representing a failed test with complete error information.

        Verifies that a TestResult instance correctly stores all error-related
        information for a failed test scenario.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        error_exception = AssertionError("Expected 5 but got 3")
        error_message = "Assertion failed in test_calculation"
        traceback_info = """Traceback (most recent call last):
  File "/project/tests/test_math.py", line 25, in test_calculation
    self.assertEqual(result, 5)
AssertionError: Expected 5 but got 3"""

        result = TestResult(
            id="test_calculation_001",
            name="test_calculation",
            status=TestStatus.FAILED,
            execution_time=0.023,
            error_message=error_message,
            traceback=traceback_info,
            class_name="TestMathOperations",
            method="test_calculation",
            module="tests.test_math",
            file_path="/project/tests/test_math.py",
            doc_string="Test basic arithmetic calculations",
            exception=error_exception
        )

        # Assert all error-related fields are correctly set
        self.assertEqual(result.status, TestStatus.FAILED)
        self.assertEqual(result.error_message, error_message)
        self.assertEqual(result.traceback, traceback_info)
        self.assertEqual(result.exception, error_exception)
        self.assertEqual(result.class_name, "TestMathOperations")
        self.assertEqual(result.method, "test_calculation")
        self.assertEqual(result.module, "tests.test_math")

    def testSkippedTestScenario(self) -> None:
        """
        Test TestResult representing a skipped test scenario.

        Verifies that a TestResult instance correctly represents a test
        that was intentionally skipped during execution.

        Parameters
        ----------
        self : TestTestingResult
            The test case instance.

        Returns
        -------
        None
        """
        result = TestResult(
            id="test_skip_001",
            name="test_database_integration",
            status=TestStatus.SKIPPED,
            execution_time=0.0,
            error_message="Database not available",
            class_name="TestDatabaseIntegration",
            method="test_database_integration",
            module="tests.test_integration",
            file_path="/project/tests/test_integration.py",
            doc_string="Test database integration functionality"
        )

        # Assert skipped test properties
        self.assertEqual(result.status, TestStatus.SKIPPED)
        self.assertEqual(result.execution_time, 0.0)
        self.assertEqual(result.error_message, "Database not available")
        self.assertIsNone(result.exception)
        self.assertIsNone(result.traceback)
