import inspect
from orionis.container.contracts.resolver import IResolver
from orionis.container.resolver.resolver import Resolver
from orionis.test.cases.asynchronous import AsyncTestCase

class TestResolverMethods(AsyncTestCase):

    async def testMethodsExist(self):
        """
        Checks that the `Resolver` class implements all required methods and inherits from `IResolver`.

        This test verifies the presence of specific methods in the `Resolver` class, ensures that
        `Resolver` is a subclass of `IResolver`, and confirms that the main public methods are not asynchronous.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate class structure.
        """

        # List of required method names that must be implemented by Resolver
        required_methods = [
            "__init__",
            "resolve",
            "resolveType",
            "resolveSignature",
            "_Resolver__resolveTransient",
            "_Resolver__resolveSingleton",
            "_Resolver__resolveScoped",
            "_Resolver__instantiateConcreteWithArgs",
            "_Resolver__instantiateCallableWithArgs",
            "_Resolver__instantiateConcreteReflective",
            "_Resolver__instantiateCallableReflective",
            "_Resolver__resolveDependencies",
        ]

        # Assert that each required method exists in Resolver
        for method in required_methods:
            self.assertTrue(
                hasattr(Resolver, method),
                f"Resolver must implement the method '{method}'"
            )

        # Assert that Resolver inherits from IResolver
        self.assertTrue(
            issubclass(Resolver, IResolver),
            "Resolver must inherit from IResolver"
        )

        # Assert that main public methods are not asynchronous
        for method in ["resolve", "resolveType", "resolveSignature"]:
            self.assertFalse(
                inspect.iscoroutinefunction(getattr(Resolver, method)),
                f"The method '{method}' must not be async"
            )
