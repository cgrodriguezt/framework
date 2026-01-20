from orionis.test.cases.synchronous import SyncTestCase
from orionis.test.contracts.dumper import ITestDumper
from orionis.test.output.dumper import TestDumper
import unittest
from unittest.mock import patch

class TestSyncTestCase(SyncTestCase):
    """
    Test suite for the SyncTestCase class in the Orionis framework.

    This test class verifies the functionality of the SyncTestCase base class,
    including its inheritance structure, synchronous test capabilities, and debugging features.
    """

    def testInheritanceFromTestCase(self):
        """
        Test that SyncTestCase inherits from unittest.TestCase.

        Verifies that SyncTestCase properly inherits from the standard library's
        TestCase, ensuring it has all the necessary synchronous test capabilities.

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        self.assertIsInstance(sync_instance, unittest.TestCase)
        self.assertTrue(issubclass(SyncTestCase, unittest.TestCase))

    def testInheritanceFromTestDumper(self):
        """
        Test that SyncTestCase inherits from TestDumper.

        Verifies that SyncTestCase properly inherits from TestDumper,
        ensuring it has access to debugging methods like dd() and dump().

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        self.assertIsInstance(sync_instance, TestDumper)
        self.assertTrue(issubclass(SyncTestCase, TestDumper))

    def testImplementsITestDumperInterface(self):
        """
        Test that SyncTestCase implements the ITestDumper interface.

        Verifies that SyncTestCase implements the ITestDumper interface
        through its TestDumper inheritance, ensuring proper contract compliance.

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        self.assertIsInstance(sync_instance, ITestDumper)
        self.assertTrue(issubclass(SyncTestCase, ITestDumper))

    def testHasDumpMethod(self):
        """
        Test that SyncTestCase has the dump method.

        Verifies that the dump method is available and callable in SyncTestCase instances,
        ensuring debugging functionality is properly inherited.

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        self.assertTrue(hasattr(sync_instance, "dump"))
        self.assertTrue(callable(sync_instance.dump))

    def testHasDdMethod(self):
        """
        Test that SyncTestCase has the dd method.

        Verifies that the dd method is available and callable in SyncTestCase instances,
        ensuring debugging functionality with execution halting is properly inherited.

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        self.assertTrue(hasattr(sync_instance, "dd"))
        self.assertTrue(callable(sync_instance.dd))

    def testSyncTestExecution(self):
        """
        Test that synchronous test methods can be executed properly.

        Verifies that SyncTestCase can properly execute synchronous test methods
        using the standard unittest framework.

        Returns
        -------
        None
        """
        # Simulate a sync operation
        result = self._syncHelperReturnsTrue()
        self.assertTrue(result)

    def testSyncAssertions(self):
        """
        Test that synchronous assertions work correctly in SyncTestCase.

        Verifies that standard unittest assertions work properly within
        synchronous test methods in SyncTestCase.

        Returns
        -------
        None
        """
        # Test various assertions in sync context through direct instantiation
        sync_instance = SyncTestCase()
        sync_instance.assertEqual(1 + 1, 2)
        sync_instance.assertTrue(self._syncHelperReturnsTrue())
        sync_instance.assertFalse(self._syncHelperReturnsFalse())

    def testSyncExceptionHandling(self):
        """
        Test that synchronous exception handling works correctly.

        Verifies that SyncTestCase properly handles exceptions raised
        in synchronous test methods and operations.

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        with sync_instance.assertRaises(ValueError):
            self._syncHelperRaisesError()

    @patch("orionis.support.facades.console.Console.dump")
    def testDumpMethodCall(self, mock_console_dump):
        """
        Test that the dump method properly calls Console.dump.

        Verifies that the dump method inherited from TestDumper correctly
        delegates to Console.dump with appropriate parameters.

        Parameters
        ----------
        mock_console_dump : Mock
            Mocked Console.dump method for testing

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        test_data = "test data"
        sync_instance.dump(test_data)

        mock_console_dump.assert_called_once()
        args, kwargs = mock_console_dump.call_args

        # Verify the test data is passed
        self.assertIn(test_data, args)

        # Verify expected keyword arguments
        self.assertFalse(kwargs.get("force_exit"))
        self.assertTrue(kwargs.get("redirect_output"))
        self.assertTrue(kwargs.get("insert_line"))

    @patch("orionis.support.facades.console.Console.dump")
    def testDdMethodCall(self, mock_console_dump):
        """
        Test that the dd method properly calls Console.dump.

        Verifies that the dd method inherited from TestDumper correctly
        delegates to Console.dump with force_exit=True to halt execution.

        Parameters
        ----------
        mock_console_dump : Mock
            Mocked Console.dump method for testing

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        test_data = "test data for dd"
        sync_instance.dd(test_data)

        mock_console_dump.assert_called_once()
        args, kwargs = mock_console_dump.call_args

        # Verify the test data is passed
        self.assertIn(test_data, args)

        # Verify expected keyword arguments for dd (force_exit should be True)
        self.assertTrue(kwargs.get("force_exit"))
        self.assertTrue(kwargs.get("redirect_output"))
        self.assertTrue(kwargs.get("insert_line"))

    @patch("orionis.support.facades.console.Console.dump")
    def testDumpFiltersSelfFromArgs(self, mock_console_dump):
        """
        Test that dump method filters out test case instances from arguments.

        Verifies that when a test case instance is passed to dump(),
        it gets filtered out to avoid dumping sensitive test case objects.

        Parameters
        ----------
        mock_console_dump : Mock
            Mocked Console.dump method for testing

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        test_data = "filtered test"
        sync_instance.dump(sync_instance, test_data)

        mock_console_dump.assert_called_once()
        args, _ = mock_console_dump.call_args

        # Verify sync_instance is not in the dumped arguments
        self.assertNotIn(sync_instance, args)
        # Verify test_data is still there
        self.assertIn(test_data, args)

    def testStandardTestCaseFeatures(self):
        """
        Test that SyncTestCase supports standard TestCase features.

        Verifies that SyncTestCase has access to all standard unittest.TestCase
        methods and features through proper inheritance.

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()

        # Verify that the class supports standard TestCase methods
        self.assertTrue(hasattr(sync_instance, "_testMethodName"))
        self.assertTrue(hasattr(sync_instance, "setUp"))
        self.assertTrue(hasattr(sync_instance, "tearDown"))
        self.assertTrue(hasattr(sync_instance, "assertEqual"))
        self.assertTrue(hasattr(sync_instance, "assertTrue"))
        self.assertTrue(hasattr(sync_instance, "assertFalse"))
        self.assertTrue(hasattr(sync_instance, "assertRaises"))

    def testMultipleSyncOperations(self):
        """
        Test that multiple synchronous operations can be executed in sequence.

        Verifies that SyncTestCase can handle multiple synchronous operations
        within a single test method without interference.

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        result1 = self._syncHelperWithValue(10)
        result2 = self._syncHelperWithValue(20)

        sync_instance.assertEqual(result1, 10)
        sync_instance.assertEqual(result2, 20)

    def testSyncSetUpAndTearDown(self):
        """
        Test that synchronous setUp and tearDown methods are supported.

        Verifies that SyncTestCase supports synchronous setUp and tearDown
        methods through its unittest.TestCase inheritance.

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        # This test verifies that the test infrastructure supports sync lifecycle methods
        self.assertTrue(hasattr(sync_instance, "setUp"))
        self.assertTrue(hasattr(sync_instance, "tearDown"))

    def testNotAsyncTestCase(self):
        """
        Test that SyncTestCase is not an AsyncTestCase or IsolatedAsyncioTestCase.

        Verifies that SyncTestCase is specifically designed for synchronous testing
        and does not inherit from asynchronous test case classes.

        Returns
        -------
        None
        """
        sync_instance = SyncTestCase()
        self.assertNotIsInstance(sync_instance, unittest.IsolatedAsyncioTestCase)
        # Import AsyncTestCase to verify it's not an instance
        from orionis.test.cases.asynchronous import AsyncTestCase
        self.assertNotIsInstance(sync_instance, AsyncTestCase)

    def testClassDocstring(self):
        """
        Test that SyncTestCase has proper documentation.

        Verifies that SyncTestCase includes appropriate class-level documentation
        to help developers understand its purpose.

        Returns
        -------
        None
        """
        self.assertIsNotNone(SyncTestCase.__doc__)
        self.assertIn("synchronous", SyncTestCase.__doc__.lower())

    def testMultipleInstancesIndependence(self):
        """
        Test that multiple SyncTestCase instances are independent.

        Verifies that creating multiple instances of SyncTestCase does not
        cause interference between test instances.

        Returns
        -------
        None
        """
        instance1 = SyncTestCase()
        instance2 = SyncTestCase()

        # Verify they are different instances
        self.assertIsNot(instance1, instance2)

        # Verify they both have the expected functionality
        self.assertTrue(hasattr(instance1, "dump"))
        self.assertTrue(hasattr(instance2, "dump"))
        self.assertTrue(hasattr(instance1, "dd"))
        self.assertTrue(hasattr(instance2, "dd"))

    def _syncHelperReturnsTrue(self):
        """
        Helper method that returns True synchronously.

        Returns
        -------
        bool
            Always returns True
        """
        return True

    def _syncHelperReturnsFalse(self):
        """
        Helper method that returns False synchronously.

        Returns
        -------
        bool
            Always returns False
        """
        return False

    def _syncHelperRaisesError(self):
        """
        Helper method that raises a ValueError synchronously.

        Raises
        ------
        ValueError
            Always raises a ValueError
        """
        raise ValueError("Test error")

    def _syncHelperWithValue(self, value):
        """
        Helper method that returns a value synchronously.

        Parameters
        ----------
        value : any
            The value to return

        Returns
        -------
        any
            The input value
        """
        return value
