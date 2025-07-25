import inspect
from orionis.console.output.console import Console
from orionis.test.cases.asynchronous import AsyncTestCase

class TestConsoleMethods(AsyncTestCase):
    """
    Test suite to ensure all required methods exist in Console and their signatures are preserved.
    """

    def setUp(self):
        """
        Set up the test environment by initializing a Console instance.

        This method is called before each test method is executed to ensure
        that a fresh Console object is available for testing.

        Returns:
            None
        """
        self.console = Console()

    def testMethodsExist(self):
        """
        Verify that all required methods exist in the Console class.

        This test iterates through a predefined list of expected method names and
        asserts that each method is present as an attribute of the Console instance.

        Returns:
            None
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

        # Check that each expected method exists in the Console instance
        for method in expected_methods:
            self.assertTrue(
                hasattr(self.console, method),
                f"Method '{method}' does not exist in Console class."
            )