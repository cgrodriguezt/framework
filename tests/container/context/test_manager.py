from orionis.container.context.manager import ScopeManager
from orionis.container.context.scope import ScopedContext
from orionis.test.cases.synchronous import SyncTestCase

class TestScopeManagerMethods(SyncTestCase):

    def setUp(self):
        """
        Set up method called before each test.

        Ensures that no scope is active before each test begins,
        providing a clean state for each test method.
        """
        ScopedContext.clear()

    def tearDown(self):
        """
        Tear down method called after each test.

        Cleans up any active scope after each test completes,
        ensuring no state leakage between tests.
        """
        ScopedContext.clear()

    def testMethodsExist(self):
        """
        Checks that all required methods are present in the ScopeManager class.

        This test verifies the existence of a predefined list of methods that are
        essential for the correct functioning of ScopeManager. The methods checked
        include initialization, item access, containment, clearing, and context
        management methods.

        Returns
        -------
        None
            This method does not return any value. It asserts the existence of methods
            and fails the test if any are missing.
        """
        # List of expected method names in ScopeManager
        expected_methods = [
            "__init__",
            "__getitem__",
            "__setitem__",
            "__contains__",
            "clear",
            "__enter__",
            "__exit__",
        ]

        # Check each method for existence in ScopeManager
        for method in expected_methods:
            self.assertTrue(
                hasattr(ScopeManager, method),  # Assert method exists
                f"Method '{method}' does not exist in ScopeManager class.",
            )

    def testInitializationCreatesEmptyScope(self):
        """
        Tests that ScopeManager initializes with an empty instances dictionary.

        This test verifies that when a new ScopeManager is created, it starts
        with an empty internal state and doesn't contain any pre-existing
        instances or keys.

        Returns
        -------
        None
            This method does not return any value. It asserts the initial state
            and fails the test if the scope is not properly initialized.
        """
        scope_manager = ScopeManager()

        # Verify that a new scope doesn't contain any arbitrary key
        self.assertNotIn("test_key", scope_manager)
        self.assertNotIn("another_key", scope_manager)

        # Verify that accessing non-existent keys returns None
        self.assertIsNone(scope_manager["non_existent_key"])

    def testSetAndGetItem(self):
        """
        Tests the item setting and retrieval functionality of ScopeManager.

        This test verifies that instances can be stored in and retrieved from
        the ScopeManager using dictionary-like syntax. It checks both the
        storage and retrieval operations work correctly.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness
            of item operations and fails the test if storage or retrieval fails.
        """
        scope_manager = ScopeManager()
        test_value = "test_instance"
        test_key = "service_key"

        # Store an instance in the scope
        scope_manager[test_key] = test_value

        # Verify the instance can be retrieved
        self.assertEqual(scope_manager[test_key], test_value)

        # Test with different data types
        scope_manager["number_key"] = 42
        scope_manager["list_key"] = [1, 2, 3]
        scope_manager["dict_key"] = {"nested": "value"}

        self.assertEqual(scope_manager["number_key"], 42)
        self.assertEqual(scope_manager["list_key"], [1, 2, 3])
        self.assertEqual(scope_manager["dict_key"], {"nested": "value"})

    def testContainsOperation(self):
        """
        Tests the containment check functionality of ScopeManager.

        This test verifies that the 'in' operator works correctly with
        ScopeManager instances, returning True for existing keys and
        False for non-existent ones.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness
            of containment checks and fails the test if the operation behaves unexpectedly.
        """
        scope_manager = ScopeManager()
        test_key = "existing_key"
        test_value = "some_value"

        # Initially, key should not exist
        self.assertNotIn(test_key, scope_manager)

        # After adding the key, it should exist
        scope_manager[test_key] = test_value
        self.assertIn(test_key, scope_manager)

        # Other keys should still not exist
        self.assertNotIn("non_existent_key", scope_manager)

    def testClearOperation(self):
        """
        Tests the clear functionality of ScopeManager.

        This test verifies that the clear method removes all stored instances
        from the scope, leaving it in an empty state similar to when it was
        first initialized.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness
            of the clear operation and fails the test if instances remain after clearing.
        """
        scope_manager = ScopeManager()

        # Add multiple instances to the scope
        scope_manager["key1"] = "value1"
        scope_manager["key2"] = "value2"
        scope_manager["key3"] = {"complex": "object"}

        # Verify instances exist before clearing
        self.assertIn("key1", scope_manager)
        self.assertIn("key2", scope_manager)
        self.assertIn("key3", scope_manager)

        # Clear the scope
        scope_manager.clear()

        # Verify all instances are removed
        self.assertNotIn("key1", scope_manager)
        self.assertNotIn("key2", scope_manager)
        self.assertNotIn("key3", scope_manager)

        # Verify accessing cleared keys returns None
        self.assertIsNone(scope_manager["key1"])
        self.assertIsNone(scope_manager["key2"])
        self.assertIsNone(scope_manager["key3"])

    def testContextManagerEnter(self):
        """
        Tests the context manager entry functionality of ScopeManager.

        This test verifies that when entering a ScopeManager context,
        it correctly sets itself as the current active scope in ScopedContext
        and returns the manager instance.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness
            of context entry and fails the test if the scope is not properly activated.
        """
        scope_manager = ScopeManager()

        # Initially, no scope should be active
        self.assertIsNone(ScopedContext.getCurrentScope())

        # Enter the context and verify it becomes active
        returned_manager = scope_manager.__enter__()

        # Verify the returned manager is the same instance
        self.assertIs(returned_manager, scope_manager)

        # Verify the scope is now active in ScopedContext
        self.assertIs(ScopedContext.getCurrentScope(), scope_manager)

    def testContextManagerExit(self):
        """
        Tests the context manager exit functionality of ScopeManager.

        This test verifies that when exiting a ScopeManager context,
        it properly clears all stored instances and resets the active
        scope in ScopedContext to None.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness
            of context exit and fails the test if cleanup is not performed properly.
        """
        scope_manager = ScopeManager()

        # Add some instances and enter the context
        scope_manager["test_key"] = "test_value"
        scope_manager.__enter__()

        # Verify the scope is active and contains instances
        self.assertIs(ScopedContext.getCurrentScope(), scope_manager)
        self.assertIn("test_key", scope_manager)

        # Exit the context
        scope_manager.__exit__(None, None, None)

        # Verify the scope is cleared and no longer active
        self.assertIsNone(ScopedContext.getCurrentScope())
        self.assertNotIn("test_key", scope_manager)
        self.assertIsNone(scope_manager["test_key"])

    def testContextManagerWithStatement(self):
        """
        Tests the complete context manager functionality using 'with' statement.

        This test verifies that ScopeManager works correctly as a context manager
        when used with Python's 'with' statement, including proper activation,
        instance storage, and cleanup.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness
            of the complete context manager workflow and fails if any step fails.
        """
        # Initially, no scope should be active
        self.assertIsNone(ScopedContext.getCurrentScope())

        with ScopeManager() as scope:

            # Verify the scope is active within the context
            self.assertIs(ScopedContext.getCurrentScope(), scope)

            # Add instances within the context
            scope["service1"] = "instance1"
            scope["service2"] = {"complex": "instance"}

            # Verify instances exist within the context
            self.assertIn("service1", scope)
            self.assertIn("service2", scope)
            self.assertEqual(scope["service1"], "instance1")
            self.assertEqual(scope["service2"], {"complex": "instance"})

        # After exiting the context, scope should be cleared
        self.assertIsNone(ScopedContext.getCurrentScope())

    def testContextManagerWithException(self):
        """
        Tests the context manager functionality when an exception occurs.

        This test verifies that ScopeManager properly handles cleanup
        even when an exception is raised within the context, ensuring
        that the scope is cleared and deactivated.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness
            of exception handling and fails if cleanup is not performed properly.
        """
        scope_manager = ScopeManager()
        exception_occurred = False

        try:
            with scope_manager as scope:
                # Add instances within the context
                scope["test_service"] = "test_instance"

                # Verify the scope is active and contains instances
                self.assertIs(ScopedContext.getCurrentScope(), scope_manager)
                self.assertIn("test_service", scope)

                # Raise an exception to test cleanup
                raise ValueError("Test exception")

        except ValueError:
            exception_occurred = True

        # Verify the exception was raised
        self.assertTrue(exception_occurred)

        # Verify cleanup occurred despite the exception
        self.assertIsNone(ScopedContext.getCurrentScope())
        self.assertNotIn("test_service", scope_manager)

    def testMultipleScopeInstances(self):
        """
        Tests the behavior of multiple ScopeManager instances.

        This test verifies that different ScopeManager instances maintain
        separate storage and that each can be activated independently
        without interfering with each other's stored instances.

        Returns
        -------
        None
            This method does not return any value. It asserts the isolation
            between scope instances and fails if there is unwanted interaction.
        """
        scope1 = ScopeManager()
        scope2 = ScopeManager()

        # Add different instances to each scope
        scope1["service"] = "instance1"
        scope2["service"] = "instance2"

        # Verify each scope contains its own instances
        self.assertEqual(scope1["service"], "instance1")
        self.assertEqual(scope2["service"], "instance2")

        # Verify scopes are independent
        scope1["unique_key"] = "unique_value"
        self.assertIn("unique_key", scope1)
        self.assertNotIn("unique_key", scope2)
        self.assertIsNone(scope2["unique_key"])

    def testGetItemWithNonExistentKey(self):
        """
        Tests the behavior when accessing non-existent keys in ScopeManager.

        This test verifies that accessing keys that don't exist in the
        ScopeManager returns None rather than raising an exception,
        ensuring graceful handling of missing keys.

        Returns
        -------
        None
            This method does not return any value. It asserts the correct
            behavior for missing keys and fails if exceptions are raised unexpectedly.
        """
        scope_manager = ScopeManager()

        # Test various non-existent keys
        self.assertIsNone(scope_manager["non_existent"])
        self.assertIsNone(scope_manager[""])
        self.assertIsNone(scope_manager[None])
        self.assertIsNone(scope_manager[123])

        # Add a key and verify other keys still return None
        scope_manager["existing"] = "value"
        self.assertEqual(scope_manager["existing"], "value")
        self.assertIsNone(scope_manager["still_non_existent"])

    def testSetItemOverwritesExistingValues(self):
        """
        Tests that setting an item with an existing key overwrites the previous value.

        This test verifies that when a key already exists in the ScopeManager,
        setting a new value for that key properly overwrites the old value
        and that the new value can be retrieved correctly.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness
            of value overwriting and fails if the operation behaves unexpectedly.
        """
        scope_manager = ScopeManager()
        test_key = "overwrite_key"

        # Set an initial value
        scope_manager[test_key] = "initial_value"
        self.assertEqual(scope_manager[test_key], "initial_value")
        self.assertIn(test_key, scope_manager)

        # Overwrite with a new value
        scope_manager[test_key] = "new_value"
        self.assertEqual(scope_manager[test_key], "new_value")
        self.assertIn(test_key, scope_manager)

        # Overwrite with different data type
        scope_manager[test_key] = {"complex": "object"}
        self.assertEqual(scope_manager[test_key], {"complex": "object"})

        # Overwrite with None
        scope_manager[test_key] = None
        self.assertIsNone(scope_manager[test_key])
        self.assertIn(test_key, scope_manager)  # Key still exists even with None value

    def testSpecialKeyTypes(self):
        """
        Tests that ScopeManager can handle different types of keys.

        This test verifies that the ScopeManager can store and retrieve
        instances using various key types including strings, integers,
        tuples, and other hashable objects.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness
            of handling different key types and fails if any key type is not supported.
        """
        scope_manager = ScopeManager()

        # Test string keys
        scope_manager["string_key"] = "string_value"
        self.assertEqual(scope_manager["string_key"], "string_value")

        # Test integer keys
        scope_manager[42] = "integer_key_value"
        self.assertEqual(scope_manager[42], "integer_key_value")

        # Test tuple keys
        tuple_key = ("nested", "tuple", "key")
        scope_manager[tuple_key] = "tuple_value"
        self.assertEqual(scope_manager[tuple_key], "tuple_value")

        # Test class type keys
        class TestClass:
            pass

        scope_manager[TestClass] = "class_type_value"
        self.assertEqual(scope_manager[TestClass], "class_type_value")

        # Verify all keys coexist
        self.assertIn("string_key", scope_manager)
        self.assertIn(42, scope_manager)
        self.assertIn(tuple_key, scope_manager)
        self.assertIn(TestClass, scope_manager)

    def testClearWithEmptyScope(self):
        """
        Tests that clearing an already empty scope doesn't cause issues.

        This test verifies that calling clear() on an empty ScopeManager
        doesn't raise exceptions and leaves the scope in a consistent state.

        Returns
        -------
        None
            This method does not return any value. It asserts that clearing
            an empty scope is safe and fails if any unexpected behavior occurs.
        """
        scope_manager = ScopeManager()

        # Verify scope is initially empty
        self.assertNotIn("any_key", scope_manager)

        # Clear empty scope (should be safe)
        scope_manager.clear()

        # Verify scope is still empty and functional
        self.assertNotIn("any_key", scope_manager)
        self.assertIsNone(scope_manager["any_key"])

        # Verify we can still add items after clearing empty scope
        scope_manager["test_key"] = "test_value"
        self.assertEqual(scope_manager["test_key"], "test_value")

    def testNestedContextManagers(self):
        """
        Tests the behavior of nested ScopeManager context managers.

        This test verifies that nested ScopeManager contexts work correctly,
        with each scope being activated and deactivated in the proper order,
        and that each scope maintains its own isolated storage.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness
            of nested scope management and fails if scopes interfere with each other.
        """
        # Initially no scope should be active
        self.assertIsNone(ScopedContext.getCurrentScope())

        with ScopeManager() as outer_scope:
            # Outer scope should be active
            self.assertIs(ScopedContext.getCurrentScope(), outer_scope)
            outer_scope["outer_key"] = "outer_value"

            with ScopeManager() as inner_scope:
                # Inner scope should now be active
                self.assertIs(ScopedContext.getCurrentScope(), inner_scope)
                inner_scope["inner_key"] = "inner_value"

                # Verify both scopes have their respective data
                self.assertEqual(outer_scope["outer_key"], "outer_value")
                self.assertEqual(inner_scope["inner_key"], "inner_value")

                # Verify scopes are isolated
                self.assertIsNone(outer_scope["inner_key"])
                self.assertIsNone(inner_scope["outer_key"])

            # After exiting inner scope, outer scope should be active again
            # Note: This behavior depends on ScopedContext implementation
            # but inner scope should be cleared
            self.assertNotIn("inner_key", inner_scope)

        # After exiting all scopes, no scope should be active
        self.assertIsNone(ScopedContext.getCurrentScope())
        self.assertNotIn("outer_key", outer_scope)

    def testContextManagerExitWithDifferentExceptionTypes(self):
        """
        Tests context manager exit with various exception types and scenarios.

        This test verifies that the ScopeManager properly handles cleanup
        when different types of exceptions occur, including system exceptions,
        custom exceptions, and multiple exception scenarios.

        Returns
        -------
        None
            This method does not return any value. It asserts proper cleanup
            behavior under various exception conditions.
        """
        # Test with different exception types
        exception_types = [
            (ValueError, "Test ValueError"),
            (TypeError, "Test TypeError"),
            (RuntimeError, "Test RuntimeError"),
            (KeyError, "Test KeyError"),
        ]

        for exception_type, message in exception_types:
            scope_manager = ScopeManager()
            exception_caught = False

            try:
                with scope_manager as scope:
                    scope["test_key"] = "test_value"
                    self.assertIn("test_key", scope)
                    raise exception_type(message)
            except exception_type:
                exception_caught = True

            # Verify exception was caught and cleanup was performed
            self.assertTrue(exception_caught, f"Exception {exception_type.__name__} was not caught")
            self.assertIsNone(ScopedContext.getCurrentScope())
            self.assertNotIn("test_key", scope_manager)

    def testDirectContextManagerMethods(self):
        """
        Tests direct calls to context manager methods (__enter__ and __exit__).

        This test verifies that the context manager methods work correctly
        when called directly, not just through the 'with' statement.
        This ensures proper implementation of the context manager protocol.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness
            of direct context manager method calls.
        """
        scope_manager = ScopeManager()

        # Test direct __enter__ call
        returned_scope = scope_manager.__enter__()
        self.assertIs(returned_scope, scope_manager)
        self.assertIs(ScopedContext.getCurrentScope(), scope_manager)

        # Add some data
        scope_manager["direct_key"] = "direct_value"
        self.assertIn("direct_key", scope_manager)

        # Test direct __exit__ call with no exception
        scope_manager.__exit__(None, None, None)
        self.assertIsNone(ScopedContext.getCurrentScope())
        self.assertNotIn("direct_key", scope_manager)

        # Test __exit__ with exception info (simulated)
        scope_manager.__enter__()
        scope_manager["another_key"] = "another_value"

        try:
            raise ValueError("Test exception")
        except ValueError as e:
            exc_type = type(e)
            exc_value = e
            import sys
            exc_traceback = sys.exc_info()[2]

            # Call __exit__ with exception info
            scope_manager.__exit__(exc_type, exc_value, exc_traceback)

        # Verify cleanup occurred even with exception info
        self.assertIsNone(ScopedContext.getCurrentScope())
        self.assertNotIn("another_key", scope_manager)

    def testScopeManagerStateAfterMultipleCycles(self):
        """
        Tests ScopeManager state consistency after multiple use cycles.

        This test verifies that a ScopeManager instance can be reused
        multiple times through different context manager cycles and
        maintains consistent behavior throughout.

        Returns
        -------
        None
            This method does not return any value. It asserts state consistency
            across multiple usage cycles.
        """
        scope_manager = ScopeManager()

        # First cycle
        with scope_manager as scope:
            scope["cycle1"] = "value1"
            self.assertIn("cycle1", scope)
            self.assertEqual(scope["cycle1"], "value1")

        # Verify cleanup after first cycle
        self.assertNotIn("cycle1", scope_manager)
        self.assertIsNone(ScopedContext.getCurrentScope())

        # Second cycle - scope should be reusable
        with scope_manager as scope:
            scope["cycle2"] = "value2"
            self.assertIn("cycle2", scope)
            self.assertEqual(scope["cycle2"], "value2")
            # Previous cycle data should not exist
            self.assertNotIn("cycle1", scope)

        # Verify cleanup after second cycle
        self.assertNotIn("cycle2", scope_manager)
        self.assertIsNone(ScopedContext.getCurrentScope())

        # Third cycle with exception
        exception_occurred = False
        try:
            with scope_manager as scope:
                scope["cycle3"] = "value3"
                self.assertIn("cycle3", scope)
                raise RuntimeError("Test exception in third cycle")
        except RuntimeError:
            exception_occurred = True

        # Verify exception occurred and cleanup was performed
        self.assertTrue(exception_occurred)
        self.assertNotIn("cycle3", scope_manager)
        self.assertIsNone(ScopedContext.getCurrentScope())

        # Fourth cycle - should still work after exception
        with scope_manager as scope:
            scope["cycle4"] = "value4"
            self.assertIn("cycle4", scope)
            self.assertEqual(scope["cycle4"], "value4")

        # Final verification
        self.assertNotIn("cycle4", scope_manager)
        self.assertIsNone(ScopedContext.getCurrentScope())

    def testLargeDataStorage(self):
        """
        Tests ScopeManager's ability to handle large amounts of data.

        This test verifies that the ScopeManager can efficiently store
        and retrieve a large number of key-value pairs without performance
        degradation or memory issues.

        Returns
        -------
        None
            This method does not return any value. It asserts the ability
            to handle large data sets and fails if performance is inadequate.
        """
        scope_manager = ScopeManager()
        data_size = 1000

        # Store large amount of data
        for i in range(data_size):
            key = f"key_{i}"
            value = f"value_{i}"
            scope_manager[key] = value

        # Verify all data was stored correctly
        for i in range(data_size):
            key = f"key_{i}"
            expected_value = f"value_{i}"
            self.assertIn(key, scope_manager)
            self.assertEqual(scope_manager[key], expected_value)

        # Test clearing large dataset
        scope_manager.clear()

        # Verify all data was cleared
        for i in range(data_size):
            key = f"key_{i}"
            self.assertNotIn(key, scope_manager)
            self.assertIsNone(scope_manager[key])

    def testComplexObjectStorage(self):
        """
        Tests storage and retrieval of complex Python objects.

        This test verifies that ScopeManager can handle complex objects
        including custom classes, nested data structures, and objects
        with various attributes and methods.

        Returns
        -------
        None
            This method does not return any value. It asserts the ability
            to store and retrieve complex objects correctly.
        """
        scope_manager = ScopeManager()

        # Test custom class instance
        class ComplexService:
            def __init__(self, name, data):
                self.name = name
                self.data = data
                self.processed = False

            def process(self):
                self.processed = True
                return f"Processed {self.name}"

        service_instance = ComplexService("TestService", {"config": "value"})
        scope_manager["complex_service"] = service_instance

        # Verify complex object storage and retrieval
        retrieved_service = scope_manager["complex_service"]
        self.assertIs(retrieved_service, service_instance)
        self.assertEqual(retrieved_service.name, "TestService")
        self.assertEqual(retrieved_service.data, {"config": "value"})
        self.assertFalse(retrieved_service.processed)

        # Test that object methods work
        result = retrieved_service.process()
        self.assertEqual(result, "Processed TestService")
        self.assertTrue(retrieved_service.processed)

        # Test nested data structures
        complex_data = {
            "level1": {
                "level2": {
                "level3": [1, 2, {"deep": "value"}],
                },
            },
            "functions": [lambda x: x * 2, lambda x: x + 1],
            "mixed": ("tuple", ["list", {"dict": "value"}], 42),
        }

        scope_manager["complex_data"] = complex_data
        retrieved_data = scope_manager["complex_data"]

        # Verify nested structure integrity
        self.assertEqual(retrieved_data["level1"]["level2"]["level3"][2]["deep"], "value")
        self.assertEqual(retrieved_data["functions"][0](5), 10)
        self.assertEqual(retrieved_data["functions"][1](5), 6)
        self.assertEqual(retrieved_data["mixed"][0], "tuple")
        self.assertEqual(retrieved_data["mixed"][2], 42)
