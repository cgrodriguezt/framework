import unittest
from unittest.mock import MagicMock
from orionis.foundation.config.testing.enums.drivers import PersistentDrivers
from orionis.foundation.config.testing.enums.mode import ExecutionMode
from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.test.core.unit_test import UnitTest

class TestTestingUnit(AsyncTestCase):

    async def testDefaultConfiguration(self) -> None:
        """
        Test that the `UnitTest` class initializes with correct default configuration values.
        """
        unit_test = UnitTest()
        self.assertIsInstance(unit_test._UnitTest__loader, unittest.TestLoader)
        self.assertIsInstance(unit_test._UnitTest__suite, unittest.TestSuite)

    async def testConfigureMethod(self) -> None:
        """
        Tests the `configure` method of the `UnitTest` class for correct configuration updates.
        """
        unit_test = UnitTest()
        configured = unit_test.configure(
            verbosity=1,
            execution_mode=ExecutionMode.PARALLEL,
            max_workers=8,
            fail_fast=True,
            print_result=False,
            throw_exception=True,
            persistent=False,
            persistent_driver=PersistentDrivers.JSON,
            web_report=False
        )
        self.assertEqual(unit_test._UnitTest__verbosity, 1)
        self.assertEqual(unit_test._UnitTest__execution_mode, ExecutionMode.PARALLEL.value)
        self.assertEqual(unit_test._UnitTest__max_workers, 8)
        self.assertTrue(unit_test._UnitTest__fail_fast)
        self.assertTrue(unit_test._UnitTest__throw_exception)
        self.assertFalse(unit_test._UnitTest__persistent)
        self.assertEqual(unit_test._UnitTest__persistent_driver, PersistentDrivers.JSON.value)
        self.assertFalse(unit_test._UnitTest__web_report)
        self.assertIs(configured, unit_test)

    async def testFlattenTestSuite(self) -> None:
        """
        Tests the `_flattenTestSuite` method of the `UnitTest` class for correct flattening of nested test suites.
        """
        unit_test = UnitTest()
        test_case1 = MagicMock()
        test_case2 = MagicMock()
        nested_suite = unittest.TestSuite()
        nested_suite.addTest(test_case1)
        nested_suite.addTest(test_case2)
        main_suite = unittest.TestSuite()
        main_suite.addTest(nested_suite)
        flattened = unit_test._UnitTest__flattenTestSuite(main_suite)
        self.assertEqual(len(flattened), 2)
        self.assertIn(test_case1, flattened)
        self.assertIn(test_case2, flattened)

    async def testMergeTestResults(self) -> None:
        """
        Tests the `_mergeTestResults` method of the `UnitTest` class for correct aggregation of test results.
        """
        unit_test = UnitTest()
        combined = unittest.TestResult()
        individual = unittest.TestResult()
        individual.testsRun = 2
        individual.failures = [('test1', 'failure')]
        individual.errors = [('test2', 'error')]
        individual.skipped = []
        individual.expectedFailures = []
        individual.unexpectedSuccesses = []
        unit_test._UnitTest__mergeTestResults(combined, individual)
        self.assertEqual(combined.testsRun, 2)
        self.assertEqual(len(combined.failures), 1)
        self.assertEqual(len(combined.errors), 1)

    async def testClearTests(self) -> None:
        """
        Tests the `clearTests` method of the `UnitTest` class to ensure it properly resets the test suite.
        """
        unit_test = UnitTest()
        mock_test = MagicMock()
        unit_test._UnitTest__suite.addTest(mock_test)
        unit_test.clearTests()
        self.assertEqual(len(unit_test._UnitTest__suite._tests), 0)

    async def testGetTestNames(self) -> None:
        """
        Tests the `getTestNames` method of the `UnitTest` class for correct extraction of test identifiers.
        """
        unit_test = UnitTest()
        mock_test = MagicMock()
        mock_test.id.return_value = 'test_id'
        unit_test._UnitTest__suite.addTest(mock_test)
        names = unit_test.getTestNames()
        self.assertEqual(names, ['test_id'])

    async def testGetTestCount(self) -> None:
        """
        Tests the `getTestCount` method of the `UnitTest` class for accurate test counting.
        """
        unit_test = UnitTest()
        mock_test1 = MagicMock()
        mock_test2 = MagicMock()
        unit_test._UnitTest__suite.addTest(mock_test1)
        unit_test._UnitTest__suite.addTest(mock_test2)
        count = unit_test.getTestCount()
        self.assertEqual(count, 2)
