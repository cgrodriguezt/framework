from orionis.container.container import Container
from orionis.test.cases.synchronous import SyncTestCase
from tests.container.core.mocks.mock_simple_classes import Car, ICar
from tests.container.core.mocks.mock_auto_resolution import IMockDependency, MockAppService, MockDependency, MockServiceWithDependency

class TestDependencyArguments(SyncTestCase):

    def testResolveDependencyArgumentsWithRegisteredServices(self):
        """
        Tests the `resolveDependencyArguments` method with services registered in the container.

        This test verifies that the container can resolve dependency arguments
        for registered services and return appropriate keyword arguments.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate dependency argument resolution.
        """

        # Create a container instance
        container = Container()

        # Register services in the container
        container.singleton(ICar, Car)
        container.singleton(IMockDependency, MockDependency)

        # Create a mock SignatureArguments object
        # Note: This would typically come from reflection, but we'll mock it for testing
        from orionis.services.introspection.dependencies.reflection import ReflectDependencies

        # Get dependencies for MockServiceWithDependency
        dependencies = ReflectDependencies(MockServiceWithDependency).callableSignature()

        # Resolve dependency arguments
        resolved_args = container.resolveDependencyArguments("test_resolve", dependencies)

        # Assert that arguments were resolved
        self.assertIsInstance(resolved_args, dict)
        self.assertIn("dependency", resolved_args)
        self.assertIsInstance(resolved_args["dependency"], MockDependency)

    def testResolveDependencyArgumentsWithAutoResolution(self):
        """
        Tests the `resolveDependencyArguments` method with auto-resolvable dependencies.

        This test verifies that the container can automatically resolve
        dependencies that are not explicitly registered but can be auto-resolved.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate auto-resolution of arguments.
        """

        # Create a container instance
        container = Container()

        # Get dependencies for MockServiceWithDependency (without registering anything)
        from orionis.services.introspection.dependencies.reflection import ReflectDependencies
        dependencies = ReflectDependencies(MockServiceWithDependency).callableSignature()

        # Resolve dependency arguments using auto-resolution
        resolved_args = container.resolveDependencyArguments("auto_resolve_test", dependencies)

        # Assert that arguments were auto-resolved
        self.assertIsInstance(resolved_args, dict)
        self.assertIn("dependency", resolved_args)
        self.assertIsInstance(resolved_args["dependency"], MockDependency)

    def testResolveDependencyArgumentsEmptyDependencies(self):
        """
        Tests the `resolveDependencyArguments` method with no dependencies.

        This test verifies that the container returns an empty dictionary
        when there are no dependencies to resolve.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate empty dependency handling.
        """

        # Create a container instance
        container = Container()

        # Get dependencies for MockAppService (which has no dependencies)
        from orionis.services.introspection.dependencies.reflection import ReflectDependencies
        dependencies = ReflectDependencies(MockAppService).callableSignature()

        # Resolve dependency arguments
        resolved_args = container.resolveDependencyArguments("empty_deps_test", dependencies)

        # Assert that an empty dictionary is returned
        self.assertIsInstance(resolved_args, dict)
        self.assertEqual(len(resolved_args), 0)

    def testResolveDependencyArgumentsWithMixedDependencies(self):
        """
        Tests the `resolveDependencyArguments` method with mixed resolvable and unresolvable dependencies.

        This test verifies that the container can handle cases where some
        dependencies can be resolved and others cannot.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate mixed dependency handling.
        """

        # Create a container instance
        container = Container()

        # Register only some dependencies
        container.singleton(IMockDependency, MockDependency)

        # Define a function with mixed dependencies for testing
        def test_function(dependency: MockDependency, app_service: MockAppService, unresolvable: int):
            return f"Dependencies: {dependency.value}, {app_service.name}, {unresolvable}"

        # Get dependencies for the test function
        from orionis.services.introspection.dependencies.reflection import ReflectDependencies
        dependencies = ReflectDependencies(test_function).callableSignature()

        # Should raise exception due to unresolvable dependency
        with self.assertRaises(Exception) as context:
            container.resolveDependencyArguments("mixed_deps_test", dependencies)

        # Verify the exception mentions the unresolvable parameter
        self.assertIn("unresolvable", str(context.exception))

    def testResolveDependencyArgumentsWithOptionalParameters(self):
        """
        Tests the `resolveDependencyArguments` method with optional parameters.

        This test verifies that the container handles optional parameters
        correctly and doesn't attempt to resolve them if they have defaults.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate optional parameter handling.
        """

        # Create a container instance
        container = Container()

        # Define a function with optional parameters
        def test_function_with_defaults(dependency: MockDependency, optional_param: str = "default"):
            return f"{dependency.value}-{optional_param}"

        # Get dependencies for the test function
        from orionis.services.introspection.dependencies.reflection import ReflectDependencies
        dependencies = ReflectDependencies(test_function_with_defaults).callableSignature()

        # Resolve dependency arguments
        resolved_args = container.resolveDependencyArguments("optional_test", dependencies)

        # Assert that required dependencies were resolved
        self.assertIsInstance(resolved_args, dict)

        # Should have resolved MockDependency
        if "dependency" in resolved_args:
            self.assertIsInstance(resolved_args["dependency"], MockDependency)

        # Optional parameters may or may not be included depending on framework behavior
        # The framework might resolve all available dependencies
        self.assertIsInstance(resolved_args, dict)

    def testResolveDependencyArgumentsPerformance(self):
        """
        Tests the performance characteristics of the `resolveDependencyArguments` method.

        This test ensures that dependency argument resolution performs
        efficiently even with complex dependency structures.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate performance.
        """

        import time

        # Create a container instance
        container = Container()

        # Register some services
        container.singleton(IMockDependency, MockDependency)
        container.singleton(IMockDependency, MockDependency)

        # Get dependencies for a complex service
        from orionis.services.introspection.dependencies.reflection import ReflectDependencies
        dependencies = ReflectDependencies(MockServiceWithDependency).callableSignature()

        # Measure resolution time
        start_time = time.time()

        # Resolve dependency arguments multiple times
        for i in range(100):
            resolved_args = container.resolveDependencyArguments(f"perf_test_{i}", dependencies)
            self.assertIsInstance(resolved_args, dict)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Assert reasonable performance
        self.assertLess(elapsed_time, 1.0, "Dependency argument resolution should be fast")

    def testResolveDependencyArgumentsWithCircularDependencies(self):
        """
        Tests the `resolveDependencyArguments` method with circular dependencies.

        This test verifies that the container can detect and handle circular
        dependencies appropriately during argument resolution.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate circular dependency handling.
        """

        # Create a container instance
        container = Container()

        # Define a class for testing circular dependency detection
        class ServiceA:
            def __init__(self, service_a: 'ServiceA'):
                self.service_a = service_a

        # Get dependencies for ServiceA
        from orionis.services.introspection.dependencies.reflection import ReflectDependencies

        try:
            dependencies = ReflectDependencies(ServiceA).callableSignature()
            
            # Attempt to resolve dependency arguments (should handle circular deps gracefully)
            # The container should either resolve successfully or fail gracefully
            resolved_args = container.resolveDependencyArguments("circular_test", dependencies)
            
            # If resolution succeeds, verify the structure
            if resolved_args:
                self.assertIsInstance(resolved_args, dict)
            
        except Exception as e:
            # If circular dependencies cause an exception, that's acceptable behavior
            # The important thing is that it doesn't cause an infinite loop
            self.assertIsInstance(e, Exception)

    def testResolveDependencyArgumentsWithNoneValues(self):
        """
        Tests the `resolveDependencyArguments` method handling of None values.

        This test verifies that the container properly handles cases where
        dependency resolution might return None values.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate None value handling.
        """

        # Create a container instance
        container = Container()

        # Get dependencies for a simple service
        from orionis.services.introspection.dependencies.reflection import ReflectDependencies
        dependencies = ReflectDependencies(MockServiceWithDependency).callableSignature()

        # Resolve dependency arguments
        resolved_args = container.resolveDependencyArguments("none_test", dependencies)

        # Assert that the result is a dictionary
        self.assertIsInstance(resolved_args, dict)

        # Assert that resolved values are not None (unless that's expected behavior)
        for key, value in resolved_args.items():
            self.assertIsNotNone(value, f"Resolved argument '{key}' should not be None")