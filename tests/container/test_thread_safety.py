import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from orionis.foundation.application import Application as Orionis
from orionis.container.container import Container
from orionis.test.cases.asynchronous import AsyncTestCase

class TestThreadSafety(AsyncTestCase):

    async def testStressSingleton(self) -> None:
        """
        Test singleton under extreme concurrent conditions.

        This test creates a large number of threads that simultaneously
        attempt to create singleton instances to verify thread-safety.
        """
        container_instances = []
        orionis_instances = []

        def create_container_with_delay():
            """Create container with random delay to simulate real conditions."""
            # Random delay to increase chance of race conditions
            time.sleep(random.uniform(0.001, 0.01))
            container = Container()
            container_instances.append(container)
            return id(container)

        def create_orionis_with_delay():
            """Create orionis with random delay to simulate real conditions."""
            # Random delay to increase chance of race conditions
            time.sleep(random.uniform(0.001, 0.01))
            orionis = Orionis()
            orionis_instances.append(orionis)
            return id(orionis)

        # Create a large number of threads
        num_threads = 100

        with ThreadPoolExecutor(max_workers=50) as executor:
            # Submit container creation tasks
            container_futures = [
                executor.submit(create_container_with_delay)
                for _ in range(num_threads)
            ]

            # Submit orionis creation tasks
            orionis_futures = [
                executor.submit(create_orionis_with_delay)
                for _ in range(num_threads)
            ]

            # Wait for all tasks to complete
            container_ids = [future.result() for future in as_completed(container_futures)]
            orionis_ids = [future.result() for future in as_completed(orionis_futures)]

        # Verify all instances are the same
        unique_container_ids = set(container_ids)
        unique_orionis_ids = set(orionis_ids)

        self.assertEqual(len(container_instances), num_threads)
        self.assertEqual(len(unique_container_ids), 1)
        self.assertEqual(len(orionis_instances), num_threads)
        self.assertEqual(len(unique_orionis_ids), 1)

        # Verify that Container and Orionis are different singletons
        container_id = list(unique_container_ids)[0] if unique_container_ids else None
        orionis_id = list(unique_orionis_ids)[0] if unique_orionis_ids else None

        self.assertNotEqual(container_id, orionis_id)

    async def testRapidAccess(self) -> None:
        """
        Test rapid concurrent access to existing singleton instances.

        This test verifies that rapid concurrent access to already
        created singleton instances maintains consistency.
        """
        # Create initial instances
        initial_container = Container()
        initial_orionis = Orionis()

        container_ids = []
        orionis_ids = []

        def rapid_container_access():
            """Rapidly access container singleton."""
            for _ in range(100):
                container = Container()
                container_ids.append(id(container))

        def rapid_orionis_access():
            """Rapidly access orionis singleton."""
            for _ in range(100):
                orionis = Orionis()
                orionis_ids.append(id(orionis))

        # Create threads for rapid access
        threads = []
        for _ in range(20):
            t1 = threading.Thread(target=rapid_container_access)
            t2 = threading.Thread(target=rapid_orionis_access)
            threads.extend([t1, t2])

        # Start all threads simultaneously
        start_time = time.time()
        for t in threads:
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        end_time = time.time()

        # Verify consistency
        unique_container_ids = set(container_ids)
        unique_orionis_ids = set(orionis_ids)

        self.assertEqual(len(container_ids), 20 * 100)  # 20 threads * 100 accesses each
        self.assertEqual(len(unique_container_ids), 1)
        self.assertEqual(len(orionis_ids), 20 * 100)
        self.assertEqual(len(unique_orionis_ids), 1)

        # Verify performance is reasonable (should complete quickly)
        self.assertLess(end_time - start_time, 10.0)  # Should complete in less than 10 seconds

    async def testMixedOperations(self) -> None:
        """
        Test mixed read/write operations on singletons.

        This test verifies that concurrent read/write operations
        maintain singleton consistency and data integrity.
        """
        errors = []

        def mixed_operations():
            """Perform mixed operations on containers."""
            try:
                # Get instances
                container = Container()
                orionis = Orionis()

                # Perform some operations
                test_key = f"test_func_{threading.current_thread().ident}"
                container.callable(test_key, lambda: "test_value")

                # Verify the same instance
                container2 = Container()
                orionis2 = Orionis()

                if container is not container2:
                    errors.append("Container singleton violated")

                if orionis is not orionis2:
                    errors.append("Orionis singleton violated")

                # Check bindings consistency
                if not container2.bound(test_key):
                    errors.append("Binding not consistent across instances")

            except Exception as e:
                errors.append(f"Exception in mixed operations: {e}")

        # Run mixed operations in multiple threads
        threads = []
        for _ in range(50):
            t = threading.Thread(target=mixed_operations)
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Assert no errors occurred
        self.assertEqual(len(errors), 0, f"Errors found: {errors[:5]}")

    async def testMemoryConsistency(self) -> None:
        """
        Test memory consistency across threads.

        This test verifies that changes made in one thread
        are visible in other threads due to singleton behavior.
        """
        results = []

        def thread_a():
            """Thread A - modifies the container."""
            container = Container()
            container.callable("thread_a_marker", lambda: "from_thread_a")
            results.append("A_completed")

        def thread_b():
            """Thread B - reads from the container."""
            # Small delay to ensure thread A runs first
            time.sleep(0.01)
            container = Container()
            has_marker = container.bound("thread_a_marker")
            results.append(f"B_sees_marker: {has_marker}")

        t1 = threading.Thread(target=thread_a)
        t2 = threading.Thread(target=thread_b)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # Verify that thread B saw the changes made by thread A
        a_completed = "A_completed" in results
        b_saw_marker = any("B_sees_marker: True" in r for r in results)

        self.assertTrue(a_completed, "Thread A should have completed")
        self.assertTrue(b_saw_marker, "Thread B should see Thread A's changes")