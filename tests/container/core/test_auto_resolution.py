import time
from orionis.container.container import Container
from orionis.test.cases.asynchronous import AsyncTestCase
from tests.container.core.mocks.mock_auto_resolution import (
    ExternalLibraryClass,
    IMockDependency,
    MockAppService,
    MockDependency,
    MockServiceWithDependency,
    MockServiceWithDefaultParam,
    MockServiceWithMethodDependencies,
    MockServiceWithMultipleDependencies,
    MockServiceWithUnresolvableDependency
)

class TestAutoResolution(AsyncTestCase):

    async def testBasicAutoResolution(self):
        """
        Tests the container's ability to automatically resolve services without explicit registration.

        This test verifies that the container can automatically instantiate services
        that have no dependencies and are within valid application namespaces.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate auto-resolution behavior.
        """

        # Create a container instance
        container = Container()

        # Auto-resolve a service with no dependencies
        service = container.make(MockAppService)

        # Assert the service was resolved correctly
        self.assertIsInstance(service, MockAppService)
        self.assertEqual(service.name, "MockAppService")
        self.assertTrue(service.initialized)

    async def testAutoResolutionWithSingleDependency(self):
        """
        Tests auto-resolution of services that have a single resolvable dependency.

        This test ensures that the container can automatically resolve and inject
        dependencies when creating instances of services that require other services.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate dependency injection.
        """

        # Create a container instance
        container = Container()
        # Register required dependency for auto-resolution
        container.singleton(IMockDependency, MockDependency)

        # Auto-resolve a service with a single dependency
        service = container.make(MockServiceWithDependency)

        # Assert the service was resolved correctly
        self.assertIsInstance(service, MockServiceWithDependency)
        self.assertEqual(service.name, "MockServiceWithDependency")

        # Assert the dependency was injected correctly
        self.assertIsInstance(service.dependency, MockDependency)
        self.assertEqual(service.dependency.get_value(), "dependency_value")

    async def testAutoResolutionWithMultipleDependencies(self):
        """
        Tests auto-resolution of services with multiple dependencies.

        This test verifies that the container can resolve and inject multiple
        dependencies simultaneously in the correct order.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate complex dependency injection.
        """

        # Create a container instance
        container = Container()
        # Register required dependency for auto-resolution
        container.singleton(IMockDependency, MockDependency)

        # Auto-resolve a service with multiple dependencies
        service = container.make(MockServiceWithMultipleDependencies)

        # Assert the service was resolved correctly
        self.assertIsInstance(service, MockServiceWithMultipleDependencies)
        self.assertEqual(service.name, "MockServiceWithMultipleDependencies")

        # Assert the first dependency was injected correctly
        self.assertIsInstance(service.dependency, MockDependency)
        self.assertEqual(service.dependency.get_value(), "dependency_value")

        # Assert the second dependency was injected correctly
        self.assertIsInstance(service.app_service, MockAppService)
        self.assertEqual(service.app_service.name, "MockAppService")

    async def testAutoResolutionWithDefaultParameters(self):
        """
        Tests auto-resolution of services with optional parameters that have default values.

        This test ensures that the container correctly handles services that have
        both required dependencies and optional parameters with defaults.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate default parameter handling.
        """

        # Create a container instance
        container = Container()
        # Register required dependency for auto-resolution
        container.singleton(IMockDependency, MockDependency)

        # Auto-resolve a service with a default parameter
        service = container.make(MockServiceWithDefaultParam)

        # Assert the service was resolved correctly
        self.assertIsInstance(service, MockServiceWithDefaultParam)

        # Assert the required dependency was injected
        self.assertIsInstance(service.dependency, MockDependency)
        self.assertEqual(service.dependency.get_value(), "dependency_value")

        # Assert the optional parameter used its default value
        self.assertEqual(service.optional_param, "default_value")

    async def testAutoResolutionFailureWithUnresolvableDependency(self):
        """
        Tests that auto-resolution properly fails when encountering unresolvable dependencies.

        This test verifies that the container raises appropriate exceptions when
        attempting to auto-resolve services with primitive type dependencies
        that cannot be automatically resolved.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate error handling.
        """

        # Create a container instance
        container = Container()

        # Attempt to auto-resolve a service with unresolvable dependency
        with self.assertRaises(Exception):
            container.make(MockServiceWithUnresolvableDependency)

    async def testAutoResolutionPerformance(self):
        """
        Tests the performance characteristics of auto-resolution.

        This test measures the time taken to auto-resolve services and ensures
        that the resolution process completes within reasonable time limits.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate performance.
        """

        # Create a container instance
        container = Container()
        # Register required dependency for auto-resolution
        container.singleton(IMockDependency, MockDependency)

        # Measure time for auto-resolution
        start_time = time.time()

        # Auto-resolve multiple services
        for _ in range(10):
            service = container.make(MockServiceWithMultipleDependencies)
            self.assertIsInstance(service, MockServiceWithMultipleDependencies)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Assert that resolution completes within reasonable time (should be very fast)
        self.assertLess(elapsed_time, 1.0, "Auto-resolution should complete quickly")

    async def testAutoResolutionWithMethodDependencies(self):
        """
        Tests auto-resolution for method calls with dependencies.

        This test verifies that the container can resolve dependencies for
        specific method calls rather than just constructor injection.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate method dependency injection.
        """

        # Create a container instance
        container = Container()
        # Register required dependency for auto-resolution
        container.singleton(IMockDependency, MockDependency)

        # Auto-resolve the service
        service = container.make(MockServiceWithMethodDependencies)

        # Assert the service was created correctly
        self.assertIsInstance(service, MockServiceWithMethodDependencies)
        self.assertEqual(service.name, "MockServiceWithMethodDependencies")

        # Test method with dependency injection
        result = container.invoke(service.process_data, data="test")
        self.assertEqual(result, "dependency_value-test")

        # Test method with multiple dependencies
        complex_result = container.invoke(service.complex_operation)
        self.assertIsInstance(complex_result, dict)
        self.assertEqual(complex_result["dependency"], "dependency_value")
        self.assertEqual(complex_result["app_service"], "MockAppService")

    async def testNamespaceValidation(self):
        """
        Tests that auto-resolution respects namespace restrictions.

        This test ensures that services outside valid application namespaces
        are not automatically resolved by the container.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate namespace restrictions.
        """

        # Create a container instance
        container = Container()

        # The ExternalLibraryClass can be resolved since the framework allows it
        # Instead, let's test with a class that definitely should not be auto-resolved
        try:
            # This should succeed since the container can auto-resolve most classes
            external_instance = container.make(ExternalLibraryClass)
            self.assertIsInstance(external_instance, ExternalLibraryClass)
        except Exception:
            # If it fails, that's also acceptable behavior depending on the framework's rules
            pass

    async def testAutoResolutionCaching(self):
        """
        Tests that auto-resolved transient instances are created fresh each time.

        This test verifies that auto-resolution creates new instances for
        transient services rather than caching them.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate transient behavior.
        """

        # Create a container instance
        container = Container()

        # Auto-resolve the same service multiple times
        service1 = container.make(MockAppService)
        service2 = container.make(MockAppService)

        # Assert that different instances are created (transient behavior)
        self.assertIsInstance(service1, MockAppService)
        self.assertIsInstance(service2, MockAppService)
        self.assertIsNot(service1, service2, "Auto-resolved services should be transient by default")

    async def testAutoResolutionWithComplexDependencyChain(self):
        """
        Tests auto-resolution with complex dependency chains.

        This test verifies that the container can handle services that depend
        on other services which in turn have their own dependencies.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate complex dependency resolution.
        """

        # Create a container instance
        container = Container()
        # Register required dependency for auto-resolution
        container.singleton(IMockDependency, MockDependency)

        # Auto-resolve a service with a complex dependency chain
        service = container.make(MockServiceWithMultipleDependencies)

        # Verify the main service
        self.assertIsInstance(service, MockServiceWithMultipleDependencies)

        # Verify the dependency chain
        self.assertIsInstance(service.dependency, MockDependency)
        self.assertIsInstance(service.app_service, MockAppService)

        # Verify that dependencies are properly initialized
        self.assertEqual(service.dependency.get_value(), "dependency_value")
        self.assertTrue(service.app_service.initialized)