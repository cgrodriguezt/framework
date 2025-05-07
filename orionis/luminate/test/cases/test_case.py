import unittest
from orionis.luminate.test.output.test_std_out import TestStdOut

class TestCase(unittest.IsolatedAsyncioTestCase, TestStdOut):
    """
    TestCase is a base class for unit tests that provides support for asynchronous
    testing using `unittest.IsolatedAsyncioTestCase` and additional functionality
    from `TestStdOut`."""
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