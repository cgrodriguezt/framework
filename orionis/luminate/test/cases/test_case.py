import unittest
from orionis.luminate.test.output.dumper import TestDumper

class TestCase(unittest.IsolatedAsyncioTestCase, TestDumper):
    """
    A base test case class for asynchronous unit tests.
    Inherits from:
        unittest.IsolatedAsyncioTestCase: Provides support for asynchronous test methods and setup/teardown.
        TestDumper: Mixin for capturing or testing standard output during tests.
    This class defines asynchronous setup and teardown methods to ensure proper initialization and cleanup
    of resources before and after each test case.
    """

    async def asyncSetUp(self):
        """
        Asynchronous setup method called before each test.
        It ensures that the parent class's asyncSetUp method is invoked to initialize
        any required resources.
        """
        await super().asyncSetUp()

    async def asyncTearDown(self):
        """
        Asynchronous teardown method called after each test.
        It ensures that the parent class's asyncTearDown method is invoked to clean up
        any resources used during the test.
        """
        await super().asyncTearDown()