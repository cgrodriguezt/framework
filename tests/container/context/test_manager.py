from orionis.container.context.manager import ScopeManager
from orionis.container.context.scope import ScopedContext
from orionis.test.cases.asynchronous import AsyncTestCase

class TestScopeManagerMethods(AsyncTestCase):

    async def testMethodsExist(self):
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
            "__exit__"
        ]

        # Check each method for existence in ScopeManager
        for method in expected_methods:
            self.assertTrue(
                hasattr(ScopeManager, method),  # Assert method exists
                f"Method '{method}' does not exist in ScopeManager class."
            )

    async def testInitializationCreatesEmptyScope(self):
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
        self.assertFalse("test_key" in scope_manager)
        self.assertFalse("another_key" in scope_manager)

        # Verify that accessing non-existent keys returns None
        self.assertIsNone(scope_manager["non_existent_key"])

    async def testSetAndGetItem(self):
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

    async def testContainsOperation(self):
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
        self.assertFalse(test_key in scope_manager)

        # After adding the key, it should exist
        scope_manager[test_key] = test_value
        self.assertTrue(test_key in scope_manager)

        # Other keys should still not exist
        self.assertFalse("non_existent_key" in scope_manager)

    async def testClearOperation(self):
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
        self.assertTrue("key1" in scope_manager)
        self.assertTrue("key2" in scope_manager)
        self.assertTrue("key3" in scope_manager)

        # Clear the scope
        scope_manager.clear()

        # Verify all instances are removed
        self.assertFalse("key1" in scope_manager)
        self.assertFalse("key2" in scope_manager)
        self.assertFalse("key3" in scope_manager)

        # Verify accessing cleared keys returns None
        self.assertIsNone(scope_manager["key1"])
        self.assertIsNone(scope_manager["key2"])
        self.assertIsNone(scope_manager["key3"])

    async def testContextManagerEnter(self):
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

    async def testContextManagerExit(self):
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
        self.assertTrue("test_key" in scope_manager)

        # Exit the context
        scope_manager.__exit__(None, None, None)

        # Verify the scope is cleared and no longer active
        self.assertIsNone(ScopedContext.getCurrentScope())
        self.assertFalse("test_key" in scope_manager)
        self.assertIsNone(scope_manager["test_key"])

    async def testContextManagerWithStatement(self):
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
            self.assertTrue("service1" in scope)
            self.assertTrue("service2" in scope)
            self.assertEqual(scope["service1"], "instance1")
            self.assertEqual(scope["service2"], {"complex": "instance"})

        # After exiting the context, scope should be cleared
        self.assertIsNone(ScopedContext.getCurrentScope())

    async def testContextManagerWithException(self):
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
                self.assertTrue("test_service" in scope)

                # Raise an exception to test cleanup
                raise ValueError("Test exception")

        except ValueError:
            exception_occurred = True

        # Verify the exception was raised
        self.assertTrue(exception_occurred)

        # Verify cleanup occurred despite the exception
        self.assertIsNone(ScopedContext.getCurrentScope())
        self.assertFalse("test_service" in scope_manager)

    async def testMultipleScopeInstances(self):
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
        self.assertTrue("unique_key" in scope1)
        self.assertFalse("unique_key" in scope2)
        self.assertIsNone(scope2["unique_key"])

    async def testGetItemWithNonExistentKey(self):
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
