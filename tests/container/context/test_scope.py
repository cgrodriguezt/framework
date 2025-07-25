from orionis.container.context.scope import ScopedContext
from orionis.test.cases.asynchronous import AsyncTestCase

class TestScopedContextMethods(AsyncTestCase):
    """
    Test suite to ensure all required methods exist in ScopedContext and their signatures are preserved.
    """

    def testMethodsExist(self):
        """
        Verify that all required methods exist in the ScopedContext class.
        """
        expected_methods = [
            "getCurrentScope",
            "setCurrentScope",
            "clear"
        ]

        for method in expected_methods:
            self.assertTrue(
                hasattr(ScopedContext, method),
                f"Method '{method}' does not exist in ScopedContext class."
            )
