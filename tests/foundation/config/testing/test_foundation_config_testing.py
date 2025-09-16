from orionis.foundation.config.testing.entities.testing import Testing
from orionis.foundation.config.testing.enums.mode import ExecutionMode
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigTesting(AsyncTestCase):

    async def testDefaultValues(self):
        """
        Verify the default values of the Testing configuration.

        This method ensures that all default attributes of the Testing configuration are set as expected.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Testing instance with default parameters
        t = Testing()

        # Assert that all default attribute values are as expected
        self.assertEqual(t.verbosity, 2)
        self.assertEqual(t.execution_mode, ExecutionMode.SEQUENTIAL.value)
        self.assertTrue(isinstance(t.max_workers, int) and t.max_workers >= 1)
        self.assertFalse(t.fail_fast)
        self.assertFalse(t.throw_exception)
        self.assertEqual(t.folder_path, "*")
        self.assertEqual(t.pattern, "test_*.py")
        self.assertIsNone(t.test_name_pattern)

    async def testValidCustomValues(self):
        """
        Validate custom valid values for all fields in Testing.

        This method verifies that the Testing configuration accepts and correctly sets
        custom valid values for all its fields.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Testing instance with custom values
        t = Testing(
            verbosity=1,
            execution_mode=ExecutionMode.PARALLEL,
            max_workers=4,
            fail_fast=True,
            throw_exception=True,
            folder_path=["unit", "integration"],
            pattern="*_spec.py",
            test_name_pattern="test_login*",
        )

        # Assert that all custom values are stored correctly
        self.assertEqual(t.verbosity, 1)
        self.assertEqual(t.execution_mode, ExecutionMode.PARALLEL.value)
        self.assertEqual(t.max_workers, 4)
        self.assertTrue(t.fail_fast)
        self.assertTrue(t.throw_exception)
        self.assertEqual(t.folder_path, ["unit", "integration"])
        self.assertEqual(t.pattern, "*_spec.py")
        self.assertEqual(t.test_name_pattern, "test_login*")

    async def testFolderPathStringAndList(self):
        """
        Validate that folder_path accepts both string and list of strings.

        This method checks that the folder_path attribute can be set as a string or a list of strings.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test folder_path as a string
        t1 = Testing(folder_path="integration")
        self.assertEqual(t1.folder_path, "integration")

        # Test folder_path as a list of strings
        t2 = Testing(folder_path=["integration", "unit"])
        self.assertEqual(t2.folder_path, ["integration", "unit"])

    async def testInvalidVerbosity(self):
        """
        Validate that invalid verbosity values raise OrionisIntegrityException.

        This method verifies that invalid verbosity values raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Testing with invalid verbosity values; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Testing(verbosity=-1)
        with self.assertRaises(OrionisIntegrityException):
            Testing(verbosity=3)
        with self.assertRaises(OrionisIntegrityException):
            Testing(verbosity="high")

    async def testInvalidExecutionMode(self):
        """
        Validate that execution_mode cannot be None.

        This method ensures that setting execution_mode to None raises OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Testing with execution_mode=None; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Testing(execution_mode=None)

    async def testInvalidMaxWorkers(self):
        """
        Validate that invalid max_workers values raise OrionisIntegrityException.

        This method checks that invalid values for max_workers raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Testing with invalid max_workers values; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Testing(max_workers=0)
        with self.assertRaises(OrionisIntegrityException):
            Testing(max_workers=-5)
        with self.assertRaises(OrionisIntegrityException):
            Testing(max_workers="many")

    async def testInvalidFailFast(self):
        """
        Validate that fail_fast must be boolean.

        This method ensures that non-boolean values for fail_fast raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Testing with non-boolean fail_fast; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Testing(fail_fast="yes")

    async def testInvalidThrowException(self):
        """
        Validate that throw_exception must be boolean.

        This method ensures that non-boolean values for throw_exception raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Testing with non-boolean throw_exception; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Testing(throw_exception="no")

    async def testInvalidBasePath(self):
        """
        Validate that base_path must be string.

        This method ensures that non-string values for base_path raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Testing with non-string execution_mode; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Testing(execution_mode=123)

    async def testInvalidFolderPath(self):
        """
        Validate that folder_path must be string or list of strings.

        This method ensures that invalid types for folder_path raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Testing with invalid folder_path values; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Testing(folder_path=123)
        with self.assertRaises(OrionisIntegrityException):
            Testing(folder_path=[1, 2])
        with self.assertRaises(OrionisIntegrityException):
            Testing(folder_path=["ok", 2])

    async def testInvalidPattern(self):
        """
        Validate that pattern must be string.

        This method ensures that non-string values for pattern raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Testing with non-string pattern values; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Testing(pattern=[])
        with self.assertRaises(OrionisIntegrityException):
            Testing(pattern=123)

    async def testInvalidTestNamePattern(self):
        """
        Validate that test_name_pattern must be string or None.

        This method ensures that invalid types for test_name_pattern raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Testing with invalid test_name_pattern values; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Testing(test_name_pattern=[])
        with self.assertRaises(OrionisIntegrityException):
            Testing(test_name_pattern=123)