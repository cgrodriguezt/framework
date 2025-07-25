from orionis.console.dynamic.progress_bar import ProgressBar
from orionis.test.cases.asynchronous import AsyncTestCase

class TestProgressBar(AsyncTestCase):

    async def onAsyncSetup(self):
        """
        Asynchronously initializes the ProgressBar instance before each test.

        This method is executed prior to each test case to ensure that a new ProgressBar
        object is available for testing. The ProgressBar instance is assigned to the
        'debugger' attribute of the test class, allowing subsequent test methods to
        interact with a fresh progress bar.

        Notes
        -----
        This setup is performed asynchronously to support test cases that require
        asynchronous initialization.

        Returns
        -------
        None
            This method does not return any value. It sets up the 'debugger' attribute.
        """

        # Create a new ProgressBar instance for each test
        self.debugger = ProgressBar()

    async def testHasMethods(self):
        """
        Asynchronously verifies that the ProgressBar instance implements the required methods.

        This test checks whether the ProgressBar object assigned to `self.debugger` provides
        the essential methods for its operation: `start`, `advance`, and `finish`. These methods
        are necessary to control the lifecycle and progression of the progress bar.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method performs assertions to validate method existence and does not return any value.
        """

        # Assert that the ProgressBar instance has a 'start' method
        self.assertTrue(hasattr(self.debugger, "start"))

        # Assert that the ProgressBar instance has an 'advance' method
        self.assertTrue(hasattr(self.debugger, "advance"))

        # Assert that the ProgressBar instance has a 'finish' method
        self.assertTrue(hasattr(self.debugger, "finish"))

    async def testHasAttrs(self):
        """
        Asynchronously checks that the ProgressBar instance contains the required attributes.

        This test validates that the ProgressBar object assigned to `self.debugger` has the essential
        attributes for its correct operation: `total`, `bar_width`, and `progress`. These attributes
        are used to track the total number of steps, the visual width of the progress bar, and the
        current progress state, respectively.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method performs assertions to verify the existence of attributes and does not return any value.
        """

        # Check if the ProgressBar instance has a 'total' attribute
        self.assertTrue(hasattr(self.debugger, "total"))

        # Check if the ProgressBar instance has a 'bar_width' attribute
        self.assertTrue(hasattr(self.debugger, "bar_width"))

        # Check if the ProgressBar instance has a 'progress' attribute
        self.assertTrue(hasattr(self.debugger, "progress"))