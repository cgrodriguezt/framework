from orionis.console.dynamic.progress_bar import ProgressBar
from orionis.test.cases.asynchronous import AsyncTestCase

class TestProgressBar(AsyncTestCase):

    async def onAsyncSetup(self):
        """
        Asynchronous setup method that initializes the ProgressBar instance for use in test cases.

        This method is called before each test method is executed, ensuring that a fresh
        ProgressBar object is available for every test. It assigns the ProgressBar instance
        to the 'debugger' attribute of the test case.

        Returns:
            None: This method does not return any value.
        """

        # Initialize ProgressBar for use in tests
        self.debugger = ProgressBar()

    async def testHasMethods(self):
        """
        Asynchronously tests whether the ProgressBar instance provides the required methods.

        This test verifies that the ProgressBar object assigned to 'self.debugger' implements
        the essential methods needed for its operation: 'start', 'advance', and 'finish'.
        These methods are typically used to control the lifecycle and progression of the progress bar.

        Returns:
            None: This method performs assertions and does not return any value.
        """

        # Check if the ProgressBar instance has a 'start' method
        self.assertTrue(hasattr(self.debugger, "start"))

        # Check if the ProgressBar instance has an 'advance' method
        self.assertTrue(hasattr(self.debugger, "advance"))

        # Check if the ProgressBar instance has a 'finish' method
        self.assertTrue(hasattr(self.debugger, "finish"))

    async def testHasAttrs(self):
        """
        Asynchronously verifies that the ProgressBar instance contains the required attributes.

        This test ensures that the ProgressBar object assigned to 'self.debugger' has the essential
        attributes necessary for its correct operation: 'total', 'bar_width', and 'progress'.
        These attributes are typically used to track the total steps, the width of the progress bar,
        and the current progress state, respectively.

        Returns:
            None: This method performs assertions to validate attribute existence and does not return any value.
        """

        # Assert that the ProgressBar instance has a 'total' attribute
        self.assertTrue(hasattr(self.debugger, "total"))

        # Assert that the ProgressBar instance has a 'bar_width' attribute
        self.assertTrue(hasattr(self.debugger, "bar_width"))

        # Assert that the ProgressBar instance has a 'progress' attribute
        self.assertTrue(hasattr(self.debugger, "progress"))