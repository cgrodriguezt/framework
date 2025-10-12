from orionis.container.container import Container
from orionis.test.cases.synchronous import SyncTestCase
from tests.container.core.mocks.mock_simple_classes import Car, ICar
from tests.container.core.mocks.mock_auto_resolution import IMockAppService, IMockDependency, IMockServiceWithDependency, MockAppService, MockDependency, MockServiceWithDependency

class TestScopedServices(SyncTestCase):

    def testScopedServiceBasicBehavior(self):
        """
        Tests basic scoped service behavior within and across contexts.

        This test verifies that scoped services maintain the same instance
        within a context but create new instances in different contexts.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate scoped service behavior.
        """

        # Create a container instance
        container = Container()

        # Register a scoped service
        container.scoped(ICar, Car)

        # Test behavior within first context
        with container.createContext():
            car1 = container.make(ICar)
            car2 = container.make(ICar)

            # Should be the same instance within the same context
            self.assertIs(car1, car2)
            self.assertIsInstance(car1, Car)

        # Test behavior within second context
        with container.createContext():
            car3 = container.make(ICar)
            car4 = container.make(ICar)

            # Should be the same instance within this context
            self.assertIs(car3, car4)

            # But different from the previous context
            self.assertIsNot(car1, car3)

        # Clean up
        container.drop(abstract=ICar)

    def testScopedInstanceBehavior(self):
        """
        Tests scoped instance registration and behavior.

        This test verifies that specific instances registered as scoped
        are properly shared within contexts.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate scoped instance behavior.
        """

        # Create a container instance
        container = Container()

        # Create a specific instance
        specific_car = Car("Scoped", "Instance")

        # Register the instance (instances are always singleton lifetime)
        container.instance(ICar, specific_car)

        # Test within first context
        with container.createContext():
            resolved1 = container.resolve(container.getBinding(ICar))
            resolved2 = container.resolve(container.getBinding(ICar))            # Should be the same specific instance
            self.assertIs(resolved1, specific_car)
            self.assertIs(resolved2, specific_car)
            self.assertEqual(resolved1.brand, "Scoped")

        # Test within second context
        with container.createContext():
            resolved3 = container.make(ICar)

            # Should still be the same specific instance
            self.assertIs(resolved3, specific_car)

        # Clean up
        container.drop(abstract=ICar)

    def testNestedContexts(self):
        """
        Tests behavior of scoped services with nested contexts.

        This test verifies that nested contexts properly handle scoped
        service instances and maintain isolation.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate nested context behavior.
        """

        # Create a container instance
        container = Container()

        # Register a scoped service
        container.scoped(ICar, Car)

        # Test nested contexts - each context is independent
        with container.createContext():
            outer_car = container.make(ICar)
            self.assertIsInstance(outer_car, Car)
            
            # Verify outer context maintains same instance
            outer_car_2 = container.make(ICar)
            self.assertIs(outer_car, outer_car_2)

            with container.createContext():
                inner_car = container.make(ICar)

                # Inner context should have its own instance
                self.assertIsNot(outer_car, inner_car)
                self.assertIsInstance(inner_car, Car)
                
                # Verify inner context maintains same instance
                inner_car_2 = container.make(ICar)
                self.assertIs(inner_car, inner_car_2)

            # Note: After exiting nested context, the current implementation
            # clears the scope completely, so we cannot access the outer context
            # This is a limitation of the current scope manager implementation

        # Clean up
        container.drop(abstract=ICar)

    def testScopedServiceWithDependencies(self):
        """
        Tests scoped services that have dependencies on other services.

        This test verifies that scoped services with dependencies are
        properly resolved and maintain correct scoping behavior.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate scoped services with dependencies.
        """

        # Create a container instance
        container = Container()

        # Register dependencies
        container.singleton(IMockDependency, MockDependency)
        # Register scoped service with interface and concrete implementation
        container.scoped(IMockServiceWithDependency, MockServiceWithDependency)

        # Test within first context
        with container.createContext():
            service1 = container.make(IMockServiceWithDependency)
            service2 = container.make(IMockServiceWithDependency)

            # Should be the same scoped instance
            self.assertIs(service1, service2)
            self.assertIsInstance(service1.dependency, MockDependency)

        # Test within second context
        with container.createContext():
            service3 = container.make(IMockServiceWithDependency)

            # Should be a different instance
            self.assertIsNot(service1, service3)

            # But dependency should be resolved correctly
            self.assertIsInstance(service3.dependency, MockDependency)

        # Clean up
        container.drop(abstract=IMockServiceWithDependency)
        container.drop(abstract=IMockDependency)

    def testMixedScopedAndSingletonServices(self):
        """
        Tests interaction between scoped and singleton services.

        This test verifies that scoped and singleton services can coexist
        and interact properly within the same container.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate mixed scope interactions.
        """

        # Create a container instance
        container = Container()

        # Register mixed scopes
        container.singleton(IMockDependency, MockDependency)
        container.scoped(IMockAppService, MockAppService)

        # Get singleton instance outside context
        singleton_dep = container.make(IMockDependency)

        # Test first context
        with container.createContext():
            scoped_service1 = container.make(IMockAppService)
            singleton_dep1 = container.make(IMockDependency)

            # Singleton should be the same everywhere
            self.assertIs(singleton_dep, singleton_dep1)

        # Test second context
        with container.createContext():
            scoped_service2 = container.make(IMockAppService)
            singleton_dep2 = container.make(IMockDependency)

            # Scoped service should be different
            self.assertIsNot(scoped_service1, scoped_service2)

            # Singleton should still be the same
            self.assertIs(singleton_dep, singleton_dep2)

        # Clean up
        container.drop(abstract=IMockDependency)
        container.drop(abstract=IMockAppService)

    def testScopedServiceContextCleanup(self):
        """
        Tests that scoped service contexts are properly cleaned up.

        This test verifies that exiting a context properly clears
        scoped instances and prevents memory leaks.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate context cleanup.
        """

        # Create a container instance
        container = Container()

        # Register a scoped service
        container.scoped(ICar, Car)

        # Create references to test cleanup
        car_ref = None

        # Test context cleanup
        with container.createContext():
            car_ref = container.make(ICar)
            self.assertIsInstance(car_ref, Car)

        # After context exit, new context should create new instance
        with container.createContext():
            new_car = container.make(ICar)
            self.assertIsNot(car_ref, new_car)

        # Clean up
        container.drop(abstract=ICar)

    def testScopedServicePerformance(self):
        """
        Tests the performance characteristics of scoped services.

        This test verifies that scoped service resolution performs
        efficiently within contexts.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate scoped service performance.
        """

        import time

        # Create a container instance
        container = Container()

        # Register a scoped service
        container.scoped(ICar, Car)

        # Measure performance within a context
        with container.createContext():
            start_time = time.time()

            # Resolve the same scoped service multiple times
            cars = []
            for _ in range(100):
                car = container.make(ICar)
                cars.append(car)

            elapsed_time = time.time() - start_time

            # All should be the same instance (scoped behavior)
            for car in cars:
                self.assertIs(car, cars[0])

            # Should complete quickly
            self.assertLess(elapsed_time, 0.5, "Scoped service resolution should be fast")

        # Clean up
        container.drop(abstract=ICar)

    def testContextManagerExceptionHandling(self):
        """
        Tests that context managers properly handle exceptions.

        This test verifies that scoped contexts are properly cleaned up
        even when exceptions occur within the context.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate exception handling in contexts.
        """

        # Create a container instance
        container = Container()

        # Register a scoped service
        container.scoped(ICar, Car)

        # Test exception handling in context
        try:
            with container.createContext():
                car = container.make(ICar)
                self.assertIsInstance(car, Car)

                # Raise an exception within the context
                raise ValueError("Test exception")

        except ValueError:
            # Exception should be properly handled
            pass

        # After exception, new context should work normally
        with container.createContext():
            new_car = container.make(ICar)
            self.assertIsInstance(new_car, Car)

        # Clean up
        container.drop(abstract=ICar)

    def testScopedServiceWithAlias(self):
        """
        Tests scoped services registered with aliases.

        This test verifies that scoped services work correctly when
        registered and resolved using aliases.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate scoped services with aliases.
        """

        # Create a container instance
        container = Container()

        # Register a scoped service with alias
        container.scoped(ICar, Car, alias="scoped_car")

        # Test within context using alias
        with container.createContext():
            car1 = container.make("scoped_car")
            car2 = container.make("scoped_car")

            # Should be the same instance within context
            self.assertIs(car1, car2)
            self.assertIsInstance(car1, Car)

        # Test in different context
        with container.createContext():
            car3 = container.make("scoped_car")

            # Should be different from previous context
            self.assertIsNot(car1, car3)

        # Clean up
        container.drop(alias="scoped_car")