from orionis.console.contracts.progress_bar import IProgressBar
from orionis.console.dynamic.progress_bar import ProgressBar
from orionis.services.introspection.abstract.reflection import ReflectionAbstract
from orionis.services.introspection.concretes.reflection import ReflectionConcrete
from orionis.test.cases.asynchronous import AsyncTestCase

class TestConsoleProgressBar(AsyncTestCase):

    async def onAsyncSetup(self):
        """
        Asynchronous setup method to initialize the ProgressBar debugger instance.

        This method is called before running asynchronous tests to set up the required
        ProgressBar for debugging or progress tracking purposes.

        Returns
        -------
        None
            This method does not return any value. It sets `self.debugger` to a new ProgressBar instance.
        """
        # Initialize the ProgressBar instance for use in tests
        self.debugger = ProgressBar()

    async def testHasMethods(self):
        """
        Test that the debugger object implements the required progress bar methods.

        This test verifies that the debugger instance has the following methods:
        - start: Initializes or starts the progress bar.
        - advance: Advances the progress bar by a step.
        - finish: Completes or finalizes the progress bar.

        Returns
        -------
        None
            Asserts the presence of required methods on the debugger instance.
        """
        # Check for required methods on the debugger instance
        self.assertTrue(hasattr(self.debugger, "start"))
        self.assertTrue(hasattr(self.debugger, "advance"))
        self.assertTrue(hasattr(self.debugger, "finish"))

    async def testHasAttrs(self):
        """
        Test that the debugger object has the required attributes.

        This test checks for the presence of the following attributes:
        - total: The total value for the progress bar.
        - bar_width: The width of the progress bar.
        - progress: The current progress value.

        Returns
        -------
        None
            Asserts the presence of required attributes on the debugger instance.
        """
        # Check for required attributes on the debugger instance
        self.assertTrue(hasattr(self.debugger, "total"))
        self.assertTrue(hasattr(self.debugger, "bar_width"))
        self.assertTrue(hasattr(self.debugger, "progress"))

    async def testDefaultValues(self):
        """
        Assert that the default values for the progress bar debugger are set correctly.

        Verifies that:
            - total is initialized to 100,
            - bar_width is initialized to 50,
            - progress is initialized to 0.

        Returns
        -------
        None
            Asserts that the default values of the ProgressBar instance are correct.
        """
        # Check default values for total, bar_width, and progress
        self.assertEqual(self.debugger.total, 100)
        self.assertEqual(self.debugger.bar_width, 50)
        self.assertEqual(self.debugger.progress, 0)

    async def testCustomInit(self):
        """
        Test initialization with custom total and width.

        This test creates a ProgressBar with custom `total` and `width` values and
        verifies that these values are set correctly, and that progress is initialized to 0.

        Returns
        -------
        None
            Asserts that custom initialization values are set as expected.
        """
        # Create a ProgressBar with custom total and width
        bar = ProgressBar(total=200, width=30)
        self.assertEqual(bar.total, 200)
        self.assertEqual(bar.bar_width, 30)
        self.assertEqual(bar.progress, 0)

    async def testStartResetsProgress(self):
        """
        Test that start() resets progress to zero.

        This test sets the progress to a non-zero value, calls `start()`, and checks
        that progress is reset to 0.

        Returns
        -------
        None
            Asserts that calling start() resets progress to zero.
        """
        # Set progress to a non-zero value and call start()
        self.debugger.progress = 42
        self.debugger.start()
        self.assertEqual(self.debugger.progress, 0)

    async def testAdvanceIncreasesProgress(self):
        """
        Test that advance() increases progress by the specified increment.

        This test starts the progress bar, advances it by a given value, and checks
        that the progress is updated accordingly.

        Returns
        -------
        None
            Asserts that progress increases by the increment value.
        """
        # Start the progress bar and advance by specific increments
        self.debugger.start()
        self.debugger.advance(5)
        self.assertEqual(self.debugger.progress, 5)
        self.debugger.advance(10)
        self.assertEqual(self.debugger.progress, 15)

    async def testAdvanceDoesNotExceedTotal(self):
        """
        Test that progress does not exceed total after advance().

        This test advances the progress bar by a value greater than the total and
        checks that progress does not exceed the total value.

        Returns
        -------
        None
            Asserts that progress is capped at the total value.
        """
        # Advance progress beyond the total and check it is capped
        self.debugger.start()
        self.debugger.advance(200)
        self.assertEqual(self.debugger.progress, self.debugger.total)

    async def testFinishSetsProgressToTotal(self):
        """
        Test that finish() sets progress to total.

        This test advances the progress bar and then calls `finish()`, verifying that
        progress is set to the total value.

        Returns
        -------
        None
            Asserts that finish() sets progress to total.
        """
        # Advance progress and call finish()
        self.debugger.start()
        self.debugger.advance(10)
        self.debugger.finish()
        self.assertEqual(self.debugger.progress, self.debugger.total)

    async def testAdvanceDefaultIncrement(self):
        """
        Test that advance() without argument increments progress by 1.

        This test starts the progress bar, calls `advance()` with no arguments, and
        checks that progress increases by 1.

        Returns
        -------
        None
            Asserts that the default increment for advance() is 1.
        """
        # Call advance() without arguments and check progress increment
        self.debugger.start()
        self.debugger.advance()
        self.assertEqual(self.debugger.progress, 1)

    def testImplementation(self):
        """
        Verifies that all methods declared in the `IProgressBar` interface are implemented
        by the `ProgressBar` concrete class.

        This method uses reflection to retrieve the method names from both the interface
        and its concrete implementation. It then checks that each method defined in the
        interface is present in the implementation.

        Parameters
        ----------
        None

        Returns
        -------
        None
            Raises an AssertionError if any interface method is missing from the concrete class.
        """
        # Retrieve all method names from the interface using reflection
        rf_abstract = ReflectionAbstract(IProgressBar).getMethods()

        # Retrieve all method names from the concrete implementation using reflection
        rf_concrete = ReflectionConcrete(ProgressBar).getMethods()

        # Assert that every interface method is implemented in the concrete class
        for method in rf_abstract:
            self.assertIn(method, rf_concrete)  # Ensure method presence in implementation

    def testPropierties(self):
        """
        Verifies that all properties declared in the `IProgressBar` interface are implemented
        by the `ProgressBar` concrete class.

        This method uses reflection to retrieve the property names from both the interface
        and its concrete implementation. It then checks that each property defined in the
        interface is present in the implementation.

        Parameters
        ----------
        None

        Returns
        -------
        None
            Raises an AssertionError if any interface property is missing from the concrete class.
        """
        # Retrieve all property names from the interface using reflection
        rf_abstract = ReflectionAbstract(IProgressBar).getProperties()

        # Retrieve all property names from the concrete implementation using reflection
        rf_concrete = ReflectionConcrete(ProgressBar).getProperties()

        # Assert that every interface property is implemented in the concrete class
        for prop in rf_abstract:
            self.assertIn(prop, rf_concrete)  # Ensure property presence in implementation
