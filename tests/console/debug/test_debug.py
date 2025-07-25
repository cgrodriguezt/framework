from orionis.console.dumper.dump import Debug
from orionis.test.cases.asynchronous import AsyncTestCase

class TestDebug(AsyncTestCase):

    async def onAsyncSetup(self):
        """
        Asynchronous setup method called before each test.

        Initializes the Debug instance and assigns it to self.debugger.

        Returns:
            None
        """

        # Create a new Debug instance for use in tests
        self.debugger = Debug()

    async def testHasDump(self):
        """
        Test if the Debug instance has a 'dump' attribute.

        Returns:
            None
        """

        # Check for 'dump' method
        self.assertTrue(hasattr(self.debugger, "dump"))

    async def testHasDD(self):
        """
        Test if the Debug instance has a 'dd' attribute.

        Returns:
            None
        """
        # Check for 'dd' method
        self.assertTrue(hasattr(self.debugger, "dd"))

    async def testHasAttr(self):
        """
        Test if the Debug instance has required attributes.

        Checks for the presence of 'console', 'indent_size', '_recursion_guard', and 'line_tcbk' attributes.

        Returns:
            None
        """
        # Debug output console
        self.assertTrue(hasattr(self.debugger, "console"))

        # Indentation size for output
        self.assertTrue(hasattr(self.debugger, "indent_size"))

        # Recursion guard attribute
        self.assertTrue(hasattr(self.debugger, "_recursion_guard"))

        # Line traceback attribute
        self.assertTrue(hasattr(self.debugger, "line_tcbk"))
