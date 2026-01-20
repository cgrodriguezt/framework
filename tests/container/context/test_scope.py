import contextvars
from orionis.container.context.scope import ScopedContext
from orionis.test.cases.synchronous import SyncTestCase

class TestScopedContextMethods(SyncTestCase):

    def testMethodsExist(self):
        """
        Checks that all required methods are present in the ScopedContext class.

        This test verifies the existence of specific methods that are essential for the correct
        operation of ScopedContext. It ensures that the class interface is complete and that
        method names have not been changed or removed.

        Returns
        -------
        None
            This method does not return anything. It asserts the existence of methods and fails the test if any are missing.
        """
        # List of method names expected to be present in ScopedContext
        expected_methods = [
            "getCurrentScope",
            "setCurrentScope",
            "clear",
        ]

        # Iterate through each expected method and assert its existence
        for method in expected_methods:
            self.assertTrue(
                hasattr(ScopedContext, method),
                f"Method '{method}' does not exist in ScopedContext class.",
            )

    def testGetCurrentScopeReturnsNoneByDefault(self):
        """
        Test that getCurrentScope returns None when no scope has been set.

        This test verifies the default behavior of the getCurrentScope method,
        ensuring it returns None when called in a fresh context where no scope
        has been previously established.

        Returns
        -------
        None
            This method does not return anything. It asserts the default state and fails the test if the behavior is incorrect.
        """
        # Clear any existing scope to ensure clean state
        ScopedContext.clear()

        # Verify that the current scope is None by default
        current_scope = ScopedContext.getCurrentScope()
        self.assertIsNone(
            current_scope,
            "getCurrentScope should return None when no scope is set",
        )

    def testSetCurrentScopeStoresScope(self):
        """
        Test that setCurrentScope properly stores a scope object.

        This test verifies that the setCurrentScope method correctly stores
        a scope object and that it can be retrieved using getCurrentScope.
        It tests basic functionality of setting and getting scope values.

        Returns
        -------
        None
            This method does not return anything. It asserts the storage behavior and fails the test if the scope is not properly stored.
        """
        # Define a test scope object
        test_scope = {"name": "test_scope", "id": 123}

        # Set the current scope
        ScopedContext.setCurrentScope(test_scope)

        # Verify that the scope was stored correctly
        retrieved_scope = ScopedContext.getCurrentScope()
        self.assertEqual(
            retrieved_scope,
            test_scope,
            "getCurrentScope should return the same object that was set with setCurrentScope",
        )

    def testSetCurrentScopeOverwritesPreviousScope(self):
        """
        Test that setCurrentScope overwrites previously set scopes.

        This test verifies that when a new scope is set using setCurrentScope,
        it replaces any previously stored scope, ensuring that only the most
        recently set scope is active.

        Returns
        -------
        None
            This method does not return anything. It asserts the overwrite behavior and fails the test if scopes are not properly replaced.
        """
        # Set initial scope
        first_scope = {"name": "first_scope", "value": "initial"}
        ScopedContext.setCurrentScope(first_scope)

        # Set a different scope
        second_scope = {"name": "second_scope", "value": "updated"}
        ScopedContext.setCurrentScope(second_scope)

        # Verify that only the second scope is active
        current_scope = ScopedContext.getCurrentScope()
        self.assertEqual(
            current_scope,
            second_scope,
            "setCurrentScope should overwrite the previously set scope",
        )
        self.assertNotEqual(
            current_scope,
            first_scope,
            "getCurrentScope should not return the first scope after it was overwritten",
        )

    def testClearResetsCurrentScope(self):
        """
        Test that clear method resets the current scope to None.

        This test verifies that the clear method properly resets the active
        scope to None, effectively removing any previously set scope from
        the current context.

        Returns
        -------
        None
            This method does not return anything. It asserts the clearing behavior and fails the test if the scope is not properly cleared.
        """
        # Set a scope first
        test_scope = {"name": "test_scope", "active": True}
        ScopedContext.setCurrentScope(test_scope)

        # Verify the scope was set
        self.assertIsNotNone(
            ScopedContext.getCurrentScope(),
            "Scope should be set before clearing",
        )

        # Clear the scope
        ScopedContext.clear()

        # Verify the scope is now None
        current_scope = ScopedContext.getCurrentScope()
        self.assertIsNone(
            current_scope,
            "getCurrentScope should return None after clear() is called",
        )

    def testScopeIsolationBetweenContexts(self):
        """
        Test that scopes are properly isolated between different context variable contexts.

        This test verifies that when using context variables in different contexts
        (like with contextvars.copy_context()), each context maintains its own
        independent scope state without interfering with others.

        Returns
        -------
        None
            This method does not return anything. It asserts context isolation and fails the test if contexts interfere with each other.
        """
        # Set scope in current context
        main_scope = {"context": "main", "id": 1}
        ScopedContext.setCurrentScope(main_scope)

        # Create a new context and run code in it
        ctx = contextvars.copy_context()

        def run_in_new_context():
            # In the new context, scope should be isolated
            nested_scope = ScopedContext.getCurrentScope()
            self.assertEqual(
                nested_scope,
                main_scope,
                "New context should inherit the scope from parent context",
            )

            # Set a different scope in the new context
            new_scope = {"context": "nested", "id": 2}
            ScopedContext.setCurrentScope(new_scope)

            # Verify the new scope is active in this context
            self.assertEqual(
                ScopedContext.getCurrentScope(),
                new_scope,
                "New scope should be active in nested context",
            )

        # Run the function in the new context
        ctx.run(run_in_new_context)

        # Verify that the main context still has its original scope
        current_scope = ScopedContext.getCurrentScope()
        self.assertEqual(
            current_scope,
            main_scope,
            "Main context scope should remain unchanged after operations in nested context",
        )

    def testSetCurrentScopeWithDifferentDataTypes(self):
        """
        Test that setCurrentScope works correctly with different data types.

        This test verifies that the ScopedContext can store and retrieve
        various types of objects as scopes, including strings, numbers,
        lists, dictionaries, and custom objects.

        Returns
        -------
        None
            This method does not return anything. It asserts type compatibility and fails the test if any data type is not properly handled.
        """
        # Test with string
        string_scope = "test_string_scope"
        ScopedContext.setCurrentScope(string_scope)
        self.assertEqual(
            ScopedContext.getCurrentScope(),
            string_scope,
            "Should handle string scopes correctly",
        )

        # Test with integer
        int_scope = 42
        ScopedContext.setCurrentScope(int_scope)
        self.assertEqual(
            ScopedContext.getCurrentScope(),
            int_scope,
            "Should handle integer scopes correctly",
        )

        # Test with list
        list_scope = [1, 2, 3, "test"]
        ScopedContext.setCurrentScope(list_scope)
        self.assertEqual(
            ScopedContext.getCurrentScope(),
            list_scope,
            "Should handle list scopes correctly",
        )

        # Test with dictionary
        dict_scope = {"key": "value", "nested": {"inner": "data"}}
        ScopedContext.setCurrentScope(dict_scope)
        self.assertEqual(
            ScopedContext.getCurrentScope(),
            dict_scope,
            "Should handle dictionary scopes correctly",
        )

        # Test with None explicitly
        ScopedContext.setCurrentScope(None)
        self.assertIsNone(
            ScopedContext.getCurrentScope(),
            "Should handle None scope correctly",
        )

    def testMultipleClearOperations(self):
        """
        Test that multiple consecutive clear operations work correctly.

        This test verifies that calling clear() multiple times in succession
        does not cause errors and maintains the expected behavior of keeping
        the scope as None.

        Returns
        -------
        None
            This method does not return anything. It asserts the stability of multiple clear operations and fails the test if any unexpected behavior occurs.
        """
        # Set a scope
        test_scope = {"test": "data"}
        ScopedContext.setCurrentScope(test_scope)

        # Clear multiple times
        ScopedContext.clear()
        ScopedContext.clear()
        ScopedContext.clear()

        # Verify scope is still None
        self.assertIsNone(
            ScopedContext.getCurrentScope(),
            "Multiple clear operations should maintain None state",
        )

        # Verify we can still set a new scope after multiple clears
        new_scope = {"after": "clear"}
        ScopedContext.setCurrentScope(new_scope)
        self.assertEqual(
            ScopedContext.getCurrentScope(),
            new_scope,
            "Should be able to set new scope after multiple clear operations",
        )

    def testScopeReferenceIntegrity(self):
        """
        Test that scope objects maintain reference integrity.

        This test verifies that when an object is stored as a scope,
        the same object reference is returned when retrieved, ensuring
        that modifications to the object are reflected when accessed
        through getCurrentScope.

        Returns
        -------
        None
            This method does not return anything. It asserts reference integrity and fails the test if object references are not maintained.
        """
        # Create a mutable object
        mutable_scope = {"counter": 0, "items": []}

        # Set as current scope
        ScopedContext.setCurrentScope(mutable_scope)

        # Get the scope and modify it
        retrieved_scope = ScopedContext.getCurrentScope()
        retrieved_scope["counter"] = 5
        retrieved_scope["items"].append("test_item")

        # Verify that getting the scope again reflects the changes
        updated_scope = ScopedContext.getCurrentScope()
        self.assertEqual(
            updated_scope["counter"],
            5,
            "Modifications to scope object should be reflected in subsequent retrievals",
        )
        self.assertIn(
            "test_item",
            updated_scope["items"],
            "List modifications in scope object should be reflected in subsequent retrievals",
        )

        # Verify it's the same object reference
        self.assertIs(
            retrieved_scope,
            updated_scope,
            "getCurrentScope should return the same object reference",
        )
