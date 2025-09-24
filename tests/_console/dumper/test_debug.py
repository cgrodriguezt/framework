from orionis.console.debug.dumper import Debug
from orionis.test.cases.asynchronous import AsyncTestCase

class TestDebug(AsyncTestCase):

    async def onAsyncSetup(self):
        """
        Asynchronous setup method called before each test.

        Initializes a new instance of the Debug class and assigns it to the
        `self.debugger` attribute for use in subsequent tests.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Instantiate Debug and assign to self.debugger for test usage
        self.debugger = Debug()

    async def testHasDump(self):
        """
        Test whether the Debug instance has a 'dump' attribute.

        Checks if the 'dump' method exists on the Debug instance.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Assert that the Debug instance has a 'dump' method
        self.assertTrue(hasattr(self.debugger, "dump"))

    async def testHasDD(self):
        """
        Test whether the Debug instance has a 'dd' attribute.

        Checks if the 'dd' method exists on the Debug instance.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Assert that the Debug instance has a 'dd' method
        self.assertTrue(hasattr(self.debugger, "dd"))

    async def testHasAttr(self):
        """
        Test whether the Debug instance has required attributes.

        Verifies the presence of the following attributes on the Debug instance:
        'console', 'indent_size', '_recursion_guard', and 'line_tcbk'.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Assert that the Debug instance has a 'console' attribute
        self.assertTrue(hasattr(self.debugger, "console"))

        # Assert that the Debug instance has an 'indent_size' attribute
        self.assertTrue(hasattr(self.debugger, "indent_size"))

        # Assert that the Debug instance has a '_recursion_guard' attribute
        self.assertTrue(hasattr(self.debugger, "_recursion_guard"))

        # Assert that the Debug instance has a 'line_tcbk' attribute
        self.assertTrue(hasattr(self.debugger, "line_tcbk"))