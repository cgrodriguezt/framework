import threading
import time
from orionis.foundation.application import Application as Orionis
from orionis.container.container import Container
from orionis.test.cases.asynchronous import AsyncTestCase

class TestSingleton(AsyncTestCase):
    """Test suite for singleton pattern implementation."""

    async def testSingletonBasicFunctionality(self) -> None:
        """
        Test basic singleton functionality.

        This test verifies that:
        1. Multiple Container instances are the same object
        2. Multiple Orionis instances are the same object
        3. Container and Orionis are different singletons
        """
        # Create multiple instances
        container1 = Container()
        container2 = Container()
        orionis1 = Orionis()
        orionis2 = Orionis()

        # Test that Container instances are the same
        self.assertIs(container1, container2)
        self.assertEqual(id(container1), id(container2))

        # Test that Orionis instances are the same
        self.assertIs(orionis1, orionis2)
        self.assertEqual(id(orionis1), id(orionis2))

        # Test that Container and Orionis are different singletons
        self.assertIsNot(container1, orionis1)

    async def testSingletonThreadingSafety(self) -> None:
        """
        Test singleton in multi-threaded environment.

        This test verifies that singleton pattern works correctly
        when instances are created from multiple threads simultaneously.
        """
        container_instances = []
        orionis_instances = []

        def create_container():
            """Create container instance in thread."""
            time.sleep(0.01)  # Small delay to increase chance of race condition
            container_instances.append(Container())

        def create_orionis():
            """Create orionis instance in thread."""
            time.sleep(0.01)  # Small delay to increase chance of race condition
            orionis_instances.append(Orionis())

        # Create multiple threads
        threads = []
        for i in range(10):
            t1 = threading.Thread(target=create_container)
            t2 = threading.Thread(target=create_orionis)
            threads.extend([t1, t2])

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Check that all instances are the same
        container_ids = [id(c) for c in container_instances]
        orionis_ids = [id(o) for o in orionis_instances]

        self.assertEqual(len(set(container_ids)), 1)
        self.assertEqual(len(set(orionis_ids)), 1)
        self.assertEqual(len(container_instances), 10)
        self.assertEqual(len(orionis_instances), 10)

    async def testInitializationConsistency(self) -> None:
        """
        Test that initialization only happens once.

        This test verifies that singleton instances maintain
        consistent state across multiple instantiations.
        """
        # Create first instance
        orionis1 = Orionis()
        providers_count_1 = len(orionis1.getProviders())

        # Create second instance (should be the same)
        orionis2 = Orionis()
        providers_count_2 = len(orionis2.getProviders())

        self.assertEqual(providers_count_1, providers_count_2)
        self.assertIs(orionis1, orionis2)

    async def testInheritanceSeparation(self) -> None:
        """
        Test that Container and Orionis maintain separate singleton instances.

        This test verifies that different singleton classes maintain
        their own separate instances while both implementing singleton pattern.
        """
        container = Container()
        orionis = Orionis()

        # Add some data to each to verify they're separate
        container.callable("test_container", lambda: "container_value")

        # Check that they're different instances but both are singletons
        self.assertEqual(type(container).__name__, "Container")
        self.assertEqual(type(orionis).__name__, "Application")
        self.assertIsNot(container, orionis)
        self.assertTrue(container.bound('test_container'))
        self.assertFalse(orionis.bound('test_container'))
