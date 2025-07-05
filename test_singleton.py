#!/usr/bin/env python3
"""
Test script to verify the singleton pattern implementation.
"""

import threading
import time
from orionis.foundation.application import Orionis
from orionis.container.container import Container

def test_singleton_basic():
    """Test basic singleton functionality."""
    print("=== Test: Basic Singleton ===")
    
    # Create multiple instances
    container1 = Container()
    container2 = Container()
    orionis1 = Orionis()
    orionis2 = Orionis()
    
    # Test that Container instances are the same
    print(f"Container instances are the same: {container1 is container2}")
    print(f"Container1 ID: {id(container1)}")
    print(f"Container2 ID: {id(container2)}")
    
    # Test that Orionis instances are the same
    print(f"Orionis instances are the same: {orionis1 is orionis2}")
    print(f"Orionis1 ID: {id(orionis1)}")
    print(f"Orionis2 ID: {id(orionis2)}")
    
    # Test that Container and Orionis are different singletons
    print(f"Container and Orionis are different: {container1 is not orionis1}")
    
    print()

def test_singleton_threading():
    """Test singleton in multi-threaded environment."""
    print("=== Test: Threading Safety ===")
    
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
    
    print(f"All Container instances are the same: {len(set(container_ids)) == 1}")
    print(f"All Orionis instances are the same: {len(set(orionis_ids)) == 1}")
    print(f"Container instances created: {len(container_instances)}")
    print(f"Orionis instances created: {len(orionis_instances)}")
    
    print()

def test_initialization():
    """Test that initialization only happens once."""
    print("=== Test: Initialization ===")
    
    # Create first instance
    orionis1 = Orionis()
    providers_count_1 = len(orionis1.getProviders())
    
    # Create second instance (should be the same)
    orionis2 = Orionis()
    providers_count_2 = len(orionis2.getProviders())
    
    print(f"First instance providers count: {providers_count_1}")
    print(f"Second instance providers count: {providers_count_2}")
    print(f"Counts are the same: {providers_count_1 == providers_count_2}")
    print(f"Instances are the same object: {orionis1 is orionis2}")
    
    print()

def test_inheritance_separation():
    """Test that Container and Orionis maintain separate singleton instances."""
    print("=== Test: Inheritance Separation ===")
    
    container = Container()
    orionis = Orionis()
    
    # Add some data to each to verify they're separate
    container.callable("test_container", lambda: "container_value")
    
    # Check that they're different instances but both are singletons
    print(f"Container type: {type(container).__name__}")
    print(f"Orionis type: {type(orionis).__name__}")
    print(f"They are different objects: {container is not orionis}")
    print(f"Container has test_container binding: {container.bound('test_container')}")
    print(f"Orionis has test_container binding: {orionis.bound('test_container')}")
    
    print()

if __name__ == "__main__":
    print("Testing Singleton Pattern Implementation\n")
    
    test_singleton_basic()
    test_singleton_threading()
    test_initialization()
    test_inheritance_separation()
    
    print("All tests completed!")
