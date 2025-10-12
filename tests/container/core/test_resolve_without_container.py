from orionis.container.container import Container
from orionis.test.cases.synchronous import SyncTestCase
from tests.container.core.mocks.mock_simple_classes import Car, ICar
from tests.container.core.mocks.mock_auto_resolution import MockAppService, MockDependency, MockAutoResolvableServiceWithDependency

class TestResolveWithoutContainer(SyncTestCase):

    def testResolveWithoutContainerBasic(self):
        """
        Tests the `resolveWithoutContainer` method with simple classes.

        This test verifies that the container can resolve and instantiate
        classes without using the internal binding system, relying purely
        on reflection and auto-resolution.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate resolution behavior.
        """

        # Create a container instance
        container = Container()

        # Resolve a simple class without container bindings
        car = container.resolveWithoutContainer(Car)

        # Assert the instance was created correctly
        self.assertIsInstance(car, Car)
        self.assertEqual(car.brand, 'a')
        self.assertEqual(car.model, 'b')

        # Test that methods work correctly
        start_message = car.start()
        self.assertEqual(start_message, "a b is starting.")

    def testResolveWithoutContainerWithArguments(self):
        """
        Tests the `resolveWithoutContainer` method with constructor arguments.

        This test verifies that the container can pass arguments to constructors
        when resolving classes without using bindings.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate argument passing.
        """

        # Create a container instance
        container = Container()

        # Resolve with positional arguments
        car_with_args = container.resolveWithoutContainer(Car, "Toyota", "Camry")

        # Assert the instance was created with the provided arguments
        self.assertIsInstance(car_with_args, Car)
        self.assertEqual(car_with_args.brand, "Toyota")
        self.assertEqual(car_with_args.model, "Camry")

        # Test with keyword arguments
        car_with_kwargs = container.resolveWithoutContainer(Car, brand="Honda", model="Civic")

        # Assert the instance was created with keyword arguments
        self.assertIsInstance(car_with_kwargs, Car)
        self.assertEqual(car_with_kwargs.brand, "Honda")
        self.assertEqual(car_with_kwargs.model, "Civic")

    def testResolveWithoutContainerWithDependencies(self):
        """
        Tests the `resolveWithoutContainer` method with dependency injection.

        This test verifies that the container can automatically resolve
        dependencies when creating instances without explicit bindings.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate dependency resolution.
        """

        # Create a container instance
        container = Container()

        # Resolve a service that has dependencies
        service = container.resolveWithoutContainer(MockAutoResolvableServiceWithDependency)

        # Assert the service was created correctly
        self.assertIsInstance(service, MockAutoResolvableServiceWithDependency)
        self.assertEqual(service.name, "MockAutoResolvableServiceWithDependency")

        # Assert the dependency was automatically resolved and injected
        self.assertIsInstance(service.dependency, MockDependency)
        self.assertEqual(service.dependency.get_value(), "dependency_value")

    def testResolveWithoutContainerNoDependencies(self):
        """
        Tests the `resolveWithoutContainer` method with classes that have no dependencies.

        This test verifies that the container can resolve simple classes
        that don't require any dependency injection.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate simple resolution.
        """

        # Create a container instance
        container = Container()

        # Resolve services with no dependencies
        app_service = container.resolveWithoutContainer(MockAppService)
        dependency = container.resolveWithoutContainer(MockDependency)

        # Assert the services were created correctly
        self.assertIsInstance(app_service, MockAppService)
        self.assertTrue(app_service.initialized)
        self.assertEqual(app_service.name, "MockAppService")

        self.assertIsInstance(dependency, MockDependency)
        self.assertEqual(dependency.get_value(), "dependency_value")

    def testResolveWithoutContainerMultipleInstances(self):
        """
        Tests that `resolveWithoutContainer` creates fresh instances each time.

        This test verifies that each call to resolveWithoutContainer
        creates a new instance rather than returning cached instances.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate instance creation.
        """

        # Create a container instance
        container = Container()

        # Resolve the same class multiple times
        instance1 = container.resolveWithoutContainer(MockAppService)
        instance2 = container.resolveWithoutContainer(MockAppService)

        # Assert that different instances are created
        self.assertIsInstance(instance1, MockAppService)
        self.assertIsInstance(instance2, MockAppService)
        self.assertIsNot(instance1, instance2, "resolveWithoutContainer should create fresh instances")

        # Assert that each instance is properly initialized
        self.assertTrue(instance1.initialized)
        self.assertTrue(instance2.initialized)

    def testResolveWithoutContainerMixedArguments(self):
        """
        Tests the `resolveWithoutContainer` method with mixed positional and keyword arguments.

        This test verifies that the container can handle constructor calls
        with both positional and keyword arguments when resolving without bindings.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate mixed argument handling.
        """

        # Create a container instance
        container = Container()

        # Resolve with mixed arguments
        car = container.resolveWithoutContainer(Car, "Ford", model="Focus")

        # Assert the instance was created with mixed arguments
        self.assertIsInstance(car, Car)
        self.assertEqual(car.brand, "Ford")
        self.assertEqual(car.model, "Focus")

        # Test that the instance functions correctly
        stop_message = car.stop()
        self.assertEqual(stop_message, "Ford Focus is stopping.")

    def testResolveWithoutContainerIgnoresBindings(self):
        """
        Tests that `resolveWithoutContainer` ignores existing container bindings.

        This test verifies that resolveWithoutContainer bypasses the container's
        binding system and performs direct resolution based on reflection.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate binding bypass.
        """

        # Create a container instance
        container = Container()

        # Create a pre-configured car instance
        registered_car = Car("Registered", "Car")

        # Register the car as a singleton in the container
        container.instance(ICar, registered_car)

        # Verify that normal resolution uses the registered instance
        resolved_via_make = container.make(ICar)
        self.assertIs(resolved_via_make, registered_car)
        self.assertEqual(resolved_via_make.brand, "Registered")

        # Resolve using resolveWithoutContainer (should ignore the binding)
        resolved_without_container = container.resolveWithoutContainer(Car)

        # Assert that a new instance was created, ignoring the registered one
        self.assertIsInstance(resolved_without_container, Car)
        self.assertIsNot(resolved_without_container, registered_car)
        self.assertEqual(resolved_without_container.brand, "a")  # Default values
        self.assertEqual(resolved_without_container.model, "b")

    def testResolveWithoutContainerErrorHandling(self):
        """
        Tests error handling in the `resolveWithoutContainer` method.

        This test verifies that appropriate exceptions are raised when
        resolveWithoutContainer encounters classes that cannot be instantiated.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate error handling.
        """

        # Create a container instance
        container = Container()

        # Test with abstract class (should fail)
        with self.assertRaises(Exception):
            container.resolveWithoutContainer(ICar)

        # Test with invalid type (should fail)
        with self.assertRaises(Exception):
            container.resolveWithoutContainer("not_a_class")

    def testResolveWithoutContainerPerformance(self):
        """
        Tests the performance characteristics of `resolveWithoutContainer`.

        This test ensures that resolveWithoutContainer performs efficiently
        even when called multiple times with complex dependency chains.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate performance.
        """

        import time

        # Create a container instance
        container = Container()

        # Measure resolution time
        start_time = time.time()

        # Resolve multiple instances
        instances = []
        for _ in range(50):
            instance = container.resolveWithoutContainer(MockAutoResolvableServiceWithDependency)
            instances.append(instance)

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Assert that all instances were created correctly
        self.assertEqual(len(instances), 50)
        for instance in instances:
            self.assertIsInstance(instance, MockAutoResolvableServiceWithDependency)
            self.assertIsInstance(instance.dependency, MockDependency)
            self.assertEqual(instance.dependency.get_value(), "dependency_value")

        # Assert reasonable performance (should complete quickly)
        self.assertLess(elapsed_time, 2.0, "resolveWithoutContainer should perform adequately")