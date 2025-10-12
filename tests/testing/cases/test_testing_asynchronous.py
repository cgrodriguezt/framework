from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.test.contracts.dumper import ITestDumper
from orionis.test.output.dumper import TestDumper
import unittest
import asyncio
from unittest.mock import patch

class TestAsyncTestCase(AsyncTestCase):
    """
    Test suite for the AsyncTestCase class in the Orionis framework.

    This test class verifies the functionality of the AsyncTestCase base class,
    including its inheritance structure, async test capabilities, and debugging features.
    """

    def testInheritanceFromIsolatedAsyncioTestCase(self):
        """
        Test that AsyncTestCase inherits from unittest.IsolatedAsyncioTestCase.

        Verifies that AsyncTestCase properly inherits from the standard library's
        IsolatedAsyncioTestCase, ensuring it has all the necessary async test capabilities.

        Returns
        -------
        None
        """
        self.assertIsInstance(self, unittest.IsolatedAsyncioTestCase)
        self.assertTrue(issubclass(AsyncTestCase, unittest.IsolatedAsyncioTestCase))

    def testInheritanceFromTestDumper(self):
        """
        Test that AsyncTestCase inherits from TestDumper.

        Verifies that AsyncTestCase properly inherits from TestDumper,
        ensuring it has access to debugging methods like dd() and dump().

        Returns
        -------
        None
        """
        self.assertIsInstance(self, TestDumper)
        self.assertTrue(issubclass(AsyncTestCase, TestDumper))

    def testImplementsITestDumperInterface(self):
        """
        Test that AsyncTestCase implements the ITestDumper interface.

        Verifies that AsyncTestCase implements the ITestDumper interface
        through its TestDumper inheritance, ensuring proper contract compliance.

        Returns
        -------
        None
        """
        self.assertIsInstance(self, ITestDumper)
        self.assertTrue(issubclass(AsyncTestCase, ITestDumper))

    def testHasDumpMethod(self):
        """
        Test that AsyncTestCase has the dump method.

        Verifies that the dump method is available and callable in AsyncTestCase instances,
        ensuring debugging functionality is properly inherited.

        Returns
        -------
        None
        """
        self.assertTrue(hasattr(self, 'dump'))
        self.assertTrue(callable(getattr(self, 'dump')))

    def testHasDdMethod(self):
        """
        Test that AsyncTestCase has the dd method.

        Verifies that the dd method is available and callable in AsyncTestCase instances,
        ensuring debugging functionality with execution halting is properly inherited.

        Returns
        -------
        None
        """
        self.assertTrue(hasattr(self, 'dd'))
        self.assertTrue(callable(getattr(self, 'dd')))

    async def testAsyncTestExecution(self):
        """
        Test that async test methods can be executed properly.

        Verifies that AsyncTestCase can properly execute asynchronous test methods
        using the asyncio event loop provided by IsolatedAsyncioTestCase.

        Returns
        -------
        None
        """
        # Simulate an async operation
        await asyncio.sleep(0.001)
        result = await self._asyncHelperReturnsTrue()
        self.assertTrue(result)

    async def testAsyncAssertions(self):
        """
        Test that async assertions work correctly in AsyncTestCase.

        Verifies that standard unittest assertions work properly within
        asynchronous test methods in AsyncTestCase.

        Returns
        -------
        None
        """
        # Test various assertions in async context
        self.assertEqual(1 + 1, 2)
        self.assertTrue(await self._asyncHelperReturnsTrue())
        self.assertFalse(await self._asyncHelperReturnsFalse())

    async def testAsyncExceptionHandling(self):
        """
        Test that async exception handling works correctly.

        Verifies that AsyncTestCase properly handles exceptions raised
        in asynchronous test methods and async operations.

        Returns
        -------
        None
        """
        with self.assertRaises(ValueError):
            await self._asyncHelperRaisesError()

    @patch('orionis.support.facades.console.Console.dump')
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
        test_data = "test data"
        self.dump(test_data)

        mock_console_dump.assert_called_once()
        args, kwargs = mock_console_dump.call_args

        # Verify the test data is passed
        self.assertIn(test_data, args)

        # Verify expected keyword arguments
        self.assertFalse(kwargs.get('force_exit'))
        self.assertTrue(kwargs.get('redirect_output'))
        self.assertTrue(kwargs.get('insert_line'))

    @patch('orionis.support.facades.console.Console.dump')
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
        test_data = "test data for dd"
        self.dd(test_data)

        mock_console_dump.assert_called_once()
        args, kwargs = mock_console_dump.call_args

        # Verify the test data is passed
        self.assertIn(test_data, args)

        # Verify expected keyword arguments for dd (force_exit should be True)
        self.assertTrue(kwargs.get('force_exit'))
        self.assertTrue(kwargs.get('redirect_output'))
        self.assertTrue(kwargs.get('insert_line'))

    @patch('orionis.support.facades.console.Console.dump')
    def testDumpFiltersSelfFromArgs(self, mock_console_dump):
        """
        Test that dump method filters out test case instances from arguments.

        Verifies that when the test case instance itself is passed to dump(),
        it gets filtered out to avoid dumping sensitive test case objects.

        Parameters
        ----------
        mock_console_dump : Mock
            Mocked Console.dump method for testing

        Returns
        -------
        None
        """
        test_data = "filtered test"
        self.dump(self, test_data)

        mock_console_dump.assert_called_once()
        args, _ = mock_console_dump.call_args

        # Verify self is not in the dumped arguments
        self.assertNotIn(self, args)
        # Verify test_data is still there
        self.assertIn(test_data, args)

    def testAsyncioEventLoopIsolation(self):
        """
        Test that each test method runs in an isolated asyncio event loop.

        Verifies that AsyncTestCase provides proper event loop isolation
        as expected from IsolatedAsyncioTestCase inheritance.

        Returns
        -------
        None
        """
        # Verify that we have access to an event loop policy
        try:
            loop = asyncio.get_event_loop()
            self.assertIsNotNone(loop)
        except RuntimeError:
            # If no event loop is running in sync context, that's expected
            # The important thing is that async methods will have their own loop
            pass

        # Verify that the class supports async methods
        self.assertTrue(hasattr(self, '_testMethodName'))
        self.assertTrue(hasattr(self, 'asyncSetUp'))
        self.assertTrue(hasattr(self, 'asyncTearDown'))

    async def testMultipleAsyncOperations(self):
        """
        Test that multiple async operations can be executed in sequence.

        Verifies that AsyncTestCase can handle multiple asynchronous operations
        within a single test method without interference.

        Returns
        -------
        None
        """
        result1 = await self._asyncHelperWithValue(10)
        result2 = await self._asyncHelperWithValue(20)

        self.assertEqual(result1, 10)
        self.assertEqual(result2, 20)

    def testAsyncSetUpAndTearDown(self):
        """
        Test that async setUp and tearDown methods are supported.

        Verifies that AsyncTestCase supports asynchronous setUp and tearDown
        methods through its IsolatedAsyncioTestCase inheritance.

        Returns
        -------
        None
        """
        # This test verifies that the test infrastructure supports async lifecycle methods
        self.assertTrue(hasattr(self, 'asyncSetUp'))
        self.assertTrue(hasattr(self, 'asyncTearDown'))

    async def _asyncHelperReturnsTrue(self):
        """
        Helper method that returns True asynchronously.

        Returns
        -------
        bool
            Always returns True after a small delay
        """
        await asyncio.sleep(0.001)
        return True

    async def _asyncHelperReturnsFalse(self):
        """
        Helper method that returns False asynchronously.

        Returns
        -------
        bool
            Always returns False after a small delay
        """
        await asyncio.sleep(0.001)
        return False

    async def _asyncHelperRaisesError(self):
        """
        Helper method that raises a ValueError asynchronously.

        Raises
        ------
        ValueError
            Always raises a ValueError after a small delay
        """
        await asyncio.sleep(0.001)
        raise ValueError("Test error")

    async def _asyncHelperWithValue(self, value):
        """
        Helper method that returns a value asynchronously.

        Parameters
        ----------
        value : any
            The value to return

        Returns
        -------
        any
            The input value after a small delay
        """
        await asyncio.sleep(0.001)
        return value