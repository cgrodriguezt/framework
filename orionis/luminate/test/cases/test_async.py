import unittest
from orionis.luminate.test.output.test_std_out import TestStdOut

class AsyncTestCase(unittest.IsolatedAsyncioTestCase, TestStdOut):
    """
    AsyncTestCase is a test case class designed for asynchronous unit testing.
    It inherits from `unittest.IsolatedAsyncioTestCase` to provide support for
    async test methods and `TestStdOut` for additional functionality.
    """

    async def asyncSetUp(self):
        """
        Asynchronous setup method called before each test.
        It ensures that the parent class's asyncSetUp method is invoked to initialize
        """
        await super().asyncSetUp()

    async def asyncTearDown(self):
        """
        Asynchronous teardown method called after each test.
        It ensures that the parent class's asyncTearDown method is invoked to clean up
        """
        await super().asyncTearDown()