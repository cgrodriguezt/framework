#!/usr/bin/env python3
"""
Comprehensive thread-safety test for the singleton pattern.
This test creates extreme concurrency conditions to verify thread-safety.
"""

import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from orionis.foundation.application import Orionis
from orionis.container.container import Container

def stress_test_singleton():
    """Test singleton under extreme concurrent conditions."""
    print("=== Stress Test: Extreme Concurrency ===")
    
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
    
    print(f"Container instances created: {len(container_instances)}")
    print(f"Unique Container IDs: {len(unique_container_ids)}")
    print(f"All Container instances are the same: {len(unique_container_ids) == 1}")
    
    print(f"Orionis instances created: {len(orionis_instances)}")
    print(f"Unique Orionis IDs: {len(unique_orionis_ids)}")
    print(f"All Orionis instances are the same: {len(unique_orionis_ids) == 1}")
    
    # Verify that Container and Orionis are different singletons
    container_id = list(unique_container_ids)[0] if unique_container_ids else None
    orionis_id = list(unique_orionis_ids)[0] if unique_orionis_ids else None
    
    print(f"Container and Orionis are different singletons: {container_id != orionis_id}")
    
    print()

def test_rapid_access():
    """Test rapid concurrent access to existing singleton instances."""
    print("=== Test: Rapid Concurrent Access ===")
    
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
    
    print(f"Total Container accesses: {len(container_ids)}")
    print(f"Unique Container IDs: {len(unique_container_ids)}")
    print(f"All Container accesses returned same instance: {len(unique_container_ids) == 1}")
    
    print(f"Total Orionis accesses: {len(orionis_ids)}")
    print(f"Unique Orionis IDs: {len(unique_orionis_ids)}")
    print(f"All Orionis accesses returned same instance: {len(unique_orionis_ids) == 1}")
    
    print(f"Test completed in: {end_time - start_time:.4f} seconds")
    print()

def test_mixed_operations():
    """Test mixed read/write operations on singletons."""
    print("=== Test: Mixed Operations ===")
    
    errors = []
    
    def mixed_operations():
        """Perform mixed operations on containers."""
        try:
            # Get instances
            container = Container()
            orionis = Orionis()
            
            # Perform some operations
            container.callable("test_func", lambda: "test_value")
            
            # Verify the same instance
            container2 = Container()
            orionis2 = Orionis()
            
            if container is not container2:
                errors.append("Container singleton violated")
            
            if orionis is not orionis2:
                errors.append("Orionis singleton violated")
            
            # Check bindings consistency
            if not container2.bound("test_func"):
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
    
    print(f"Errors found: {len(errors)}")
    if errors:
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    else:
        print("No errors found - all operations were consistent!")
    
    print()

def test_memory_consistency():
    """Test memory consistency across threads."""
    print("=== Test: Memory Consistency ===")
    
    # This test verifies that changes made in one thread are visible in others
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
    
    print(f"Results: {results}")
    
    # Verify that thread B saw the changes made by thread A
    a_completed = "A_completed" in results
    b_saw_marker = any("B_sees_marker: True" in r for r in results)
    
    print(f"Thread A completed: {a_completed}")
    print(f"Thread B saw Thread A's changes: {b_saw_marker}")
    print(f"Memory consistency verified: {a_completed and b_saw_marker}")
    
    print()

if __name__ == "__main__":
    print("Comprehensive Thread-Safety Test for Singleton Pattern\n")
    print("=" * 60)
    
    stress_test_singleton()
    test_rapid_access()
    test_mixed_operations()
    test_memory_consistency()
    
    print("=" * 60)
    print("All thread-safety tests completed!")
    print("\nIf all tests show positive results, your singleton is thread-safe!")
