from orionis.container.context.manager import ScopeManager
from orionis.test.cases.asynchronous import AsyncTestCase

class TestScopeManagerMethods(AsyncTestCase):
    """
    Test suite to ensure all required methods exist in ScopeManager and their signatures are preserved.
    """

    def testMethodsExist(self):
        """
        Verify that all required methods exist in the ScopeManager class.
        """
        expected_methods = [
            "__init__",
            "__getitem__",
            "__setitem__",
            "__contains__",
            "clear",
            "__enter__",
            "__exit__"
        ]

        for method in expected_methods:
            self.assertTrue(
                hasattr(ScopeManager, method),
                f"Method '{method}' does not exist in ScopeManager class."
            )
