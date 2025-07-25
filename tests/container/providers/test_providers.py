import inspect
from orionis.container.contracts.service_provider import IServiceProvider
from orionis.container.providers.service_provider import ServiceProvider
from orionis.test.cases.asynchronous import AsyncTestCase

class TestServiceProviderMethods(AsyncTestCase):

    async def testMethodsExist(self):
        """
        Checks that the ServiceProvider class implements the required methods and constructor.

        This test verifies the following:
        - The existence of the '__init__', 'register', and 'boot' methods in ServiceProvider.
        - That 'register' and 'boot' are asynchronous methods.
        - That ServiceProvider inherits from IServiceProvider.

        Returns:
            None. The method uses assertions to validate class structure and method types.
        """
        # List of required methods and their associated class
        expected_methods = [
            ("__init__", ServiceProvider),
            ("register", ServiceProvider),
            ("boot", ServiceProvider),
        ]

        # Check that each required method exists in ServiceProvider
        for method_name, cls in expected_methods:
            self.assertTrue(
                hasattr(cls, method_name),
                f"Method '{method_name}' does not exist in {cls.__name__}."
            )

        # Ensure 'register' and 'boot' are asynchronous methods
        self.assertTrue(
            inspect.iscoroutinefunction(ServiceProvider.register),
            "register must be async"
        )
        self.assertTrue(
            inspect.iscoroutinefunction(ServiceProvider.boot),
            "boot must be async"
        )

        # Ensure ServiceProvider inherits from IServiceProvider
        self.assertTrue(
            issubclass(ServiceProvider, IServiceProvider),
            "ServiceProvider must inherit from IServiceProvider"
        )
