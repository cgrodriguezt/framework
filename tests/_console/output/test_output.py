from orionis.console.output.console import Console
from orionis.test.cases.asynchronous import AsyncTestCase

class TestConsoleMethods(AsyncTestCase):

    def setUp(self):
        """
        Initializes a new Console instance before each test.

        This method is automatically called before each test method in the test case.
        It ensures that a fresh instance of the Console class is available for testing,
        preventing state leakage between tests.

        Returns
        -------
        None
            This method does not return any value.
        """

        # Create a new Console instance for each test to ensure isolation
        self.console = Console()

    def testMethodsExist(self):
        """
        Checks for the existence of required methods in the Console class.

        This test iterates through a predefined list of expected method names and
        asserts that each method is present as an attribute of the Console instance.
        It ensures that the Console class provides all necessary functionality for
        output operations and user interactions.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. It raises an assertion error if any expected method is missing.
        """

        # List of method names that are expected to be present in the Console class
        expected_methods = [
            "success",
            "textSuccess",
            "textSuccessBold",
            "info",
            "textInfo",
            "textInfoBold",
            "warning",
            "textWarning",
            "textWarningBold",
            "fail",
            "error",
            "textError",
            "textErrorBold",
            "textMuted",
            "textMutedBold",
            "textUnderline",
            "clear",
            "clearLine",
            "line",
            "newLine",
            "write",
            "writeLine",
            "ask",
            "confirm",
            "secret",
            "table",
            "anticipate",
            "choice",
            "exception",
            "exitSuccess",
            "exitError"
        ]

        # Iterate through each expected method and check its existence in the Console instance
        for method in expected_methods:

            # Assert that the method exists as an attribute of the Console instance
            self.assertTrue(
                hasattr(self.console, method),
                f"Method '{method}' does not exist in Console class."
            )