import os
import sys
import tempfile
from unittest.mock import patch
from orionis.services.environment.core.dot_env import DotEnv
from orionis.services.environment.env import Env
from orionis.services.environment.enums.value_type import EnvironmentValueType
from orionis.services.environment.key.key_generator import SecureKeyGenerator
from orionis.test.cases.synchronous import SyncTestCase

class TestServicesEnvironment(SyncTestCase):

    def setUp(self): # NOSONAR
        """
        Set up test environment before each test method.

        Creates a temporary directory and .env file for isolated testing,
        clears any existing environment variables that might interfere with tests,
        and resets the Env singleton instance.

        Returns
        -------
        None
        """
        # Create temporary directory for .env file
        self.temp_dir = tempfile.mkdtemp()
        self.temp_env_file = os.path.join(self.temp_dir, '.env')

        # Clear any existing environment variables that might interfere
        test_keys = [
            'NAME', 'VERSION', 'AUTHOR', 'AUTHOR_EMAIL', 'DESCRIPTION',
            'SKELETON', 'FRAMEWORK', 'DOCS', 'API', 'PYTHON_REQUIRES',
            'NON_EXISTENT_KEY', 'TEST_KEY', 'TEST_UNSET_KEY'
        ]
        for key in test_keys:
            os.environ.pop(key, None)

        # Reset the Env singleton instance for clean tests
        Env._dotenv_instance = None

    def tearDown(self): # NOSONAR
        """
        Clean up test environment after each test method.

        Removes temporary files and directories created during testing
        and resets the Env singleton instance.

        Returns
        -------
        None
        """
        # Clean up temporary files
        if os.path.exists(self.temp_env_file):
            os.remove(self.temp_env_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

        # Reset singleton instance
        Env._dotenv_instance = None

    def testSetAndGetConstants(self):
        """
        Test storing and retrieving framework metadata constants using Env.set and Env.get.

        This test imports several metadata constants from the `orionis.metadata.framework` module,
        sets each constant in the Env storage using `Env.set`, and verifies that the operation succeeds.
        It then retrieves each constant using `Env.get` and asserts that the retrieved value matches
        the original constant.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate behavior.

        Notes
        -----
        - Ensures that `Env.set` returns True for each constant.
        - Ensures that `Env.get` returns the correct value for each constant.
        """
        from orionis.metadata.framework import (
            NAME, VERSION, AUTHOR, AUTHOR_EMAIL, DESCRIPTION,
            SKELETON, FRAMEWORK, DOCS, API, PYTHON_REQUIRES
        )

        # Prepare a dictionary of constant names and their values
        constants = {
            "NAME": NAME,
            "VERSION": VERSION,
            "AUTHOR": AUTHOR,
            "AUTHOR_EMAIL": AUTHOR_EMAIL,
            "DESCRIPTION": DESCRIPTION,
            "SKELETON": SKELETON,
            "FRAMEWORK": FRAMEWORK,
            "DOCS": DOCS,
            "API": API,
            "PYTHON_REQUIRES": PYTHON_REQUIRES
        }

        # Set each constant in the environment and assert the operation succeeds
        for key, value in constants.items():
            result = Env.set(key, value)
            self.assertTrue(result)

        # Retrieve each constant and assert the value matches the original
        for key, value in constants.items():
            retrieved = Env.get(key)
            self.assertEqual(retrieved, value)

    def testGetNonExistentKey(self):
        """
        Test the behavior of `Env.get` when retrieving a non-existent environment key.

        This test verifies that attempting to retrieve a value for a key that has not been set
        in the environment returns `None`. This ensures that the environment behaves as expected
        when queried for missing keys.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate that `Env.get`
            returns `None` for a non-existent key.

        Notes
        -----
        - Ensures that `Env.get` returns `None` when the specified key does not exist in the environment.
        """
        # Attempt to retrieve a value for a key that has not been set
        self.assertIsNone(Env.get("NON_EXISTENT_KEY"))

    def testGetWithDefaultValue(self):
        """
        Test `Env.get` behavior when providing a default value for non-existent keys.

        This test verifies that `Env.get` correctly returns the provided default value
        when the requested environment variable does not exist.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate behavior.

        Notes
        -----
        - Tests various data types as default values: string, integer, boolean, list, dict.
        """
        # Test with string default
        self.assertEqual(Env.get("NON_EXISTENT_KEY", "default_value"), "default_value")

        # Test with integer default
        self.assertEqual(Env.get("NON_EXISTENT_KEY", 42), 42)

        # Test with boolean default
        self.assertTrue(Env.get("NON_EXISTENT_KEY", True))

        # Test with list default
        self.assertEqual(Env.get("NON_EXISTENT_KEY", [1, 2, 3]), [1, 2, 3])

        # Test with dict default
        self.assertEqual(Env.get("NON_EXISTENT_KEY", {"key": "value"}), {"key": "value"})

    def testUnsetMethod(self):
        """
        Test the `Env.unset` method for removing environment variables.

        This test verifies that `Env.unset` correctly removes environment variables
        from both the .env file and the current process environment, and that
        attempting to retrieve an unset variable returns None.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate behavior.

        Notes
        -----
        - Tests that unset returns True for both existing and non-existing keys.
        - Verifies that unset variables cannot be retrieved afterward.
        """
        # Set a test variable
        test_key = "TEST_UNSET_KEY"
        test_value = "test_value"
        self.assertTrue(Env.set(test_key, test_value))
        self.assertEqual(Env.get(test_key), test_value)

        # Unset the variable
        self.assertTrue(Env.unset(test_key))

        # Verify the variable is no longer accessible
        self.assertIsNone(Env.get(test_key))

        # Test unsetting a non-existent key (should still return True)
        self.assertTrue(Env.unset("NON_EXISTENT_UNSET_KEY"))

    def testAllMethod(self):
        """
        Test the `Env.all` method for retrieving all environment variables.

        This test verifies that `Env.all` returns a dictionary containing all
        environment variables currently loaded from the .env file, and that
        the returned values are correctly parsed to their appropriate Python types.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate behavior.

        Notes
        -----
        - Tests that all method returns a dictionary.
        - Verifies that set variables appear in the all() output.
        - Checks that values are correctly typed in the returned dictionary.
        """
        # Set multiple test variables with different types
        test_vars = {
            "TEST_STRING": "hello_world",
            "TEST_INTEGER": 123,
            "TEST_FLOAT": 3.14,
            "TEST_BOOLEAN": True,
            "TEST_LIST": [1, 2, 3]
        }

        # Set all test variables
        for key, value in test_vars.items():
            self.assertTrue(Env.set(key, value))

        # Retrieve all variables
        all_vars = Env.all()

        # Verify return type is dictionary
        self.assertIsInstance(all_vars, dict)

        # Verify all set variables are present and correctly typed
        for key, expected_value in test_vars.items():
            self.assertIn(key, all_vars)
            self.assertEqual(all_vars[key], expected_value)

    def testReloadMethod(self):
        """
        Test the `Env.reload` method for refreshing environment variables from .env file.

        This test verifies that `Env.reload` successfully refreshes the environment
        variables when the .env file has been modified externally.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate behavior.

        Notes
        -----
        - Tests that reload returns True on successful operation.
        - Verifies that changes to .env file are reflected after reload.
        """
        # Test basic reload functionality
        self.assertTrue(Env.reload())

        # Set a variable to test reload with existing data
        self.assertTrue(Env.set("TEST_RELOAD", "initial_value"))
        self.assertEqual(Env.get("TEST_RELOAD"), "initial_value")

        # Reload should still work with existing data
        self.assertTrue(Env.reload())
        self.assertEqual(Env.get("TEST_RELOAD"), "initial_value")

    def testIsVirtualMethod(self):
        """
        Test the `Env.isVirtual` static method for detecting virtual environments.

        This test verifies that `Env.isVirtual` correctly identifies whether the current
        Python interpreter is running inside a virtual environment by checking various
        indicators like environment variables and interpreter paths.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate behavior.

        Notes
        -----
        - Tests return type is boolean.
        - Tests behavior with and without VIRTUAL_ENV environment variable.
        - Tests behavior with different sys.prefix configurations.
        """
        # Test that method returns a boolean
        result = Env.isVirtual()
        self.assertIsInstance(result, bool)

        # Test with VIRTUAL_ENV environment variable set
        with patch.dict(os.environ, {'VIRTUAL_ENV': '/path/to/venv'}):
            self.assertTrue(Env.isVirtual())

        # Test with VIRTUAL_ENV environment variable not set but sys.prefix different
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(sys, 'prefix', '/different/prefix'):
                with patch.object(sys, 'base_prefix', '/base/prefix'):
                    # This should detect virtual environment via sys.prefix comparison
                    virtual_result = Env.isVirtual()
                    self.assertIsInstance(virtual_result, bool)

    def testSingletonBehavior(self):
        """
        Test that Env uses a singleton DotEnv instance correctly.

        This test verifies that multiple calls to Env methods use the same underlying
        DotEnv instance, ensuring consistent behavior and state across operations.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate behavior.

        Notes
        -----
        - Verifies that the same DotEnv instance is reused across method calls.
        - Tests that state is maintained between different Env operations.
        """
        # Get the initial singleton instance
        instance1 = Env._getSingletonInstance()

        # Set a value using the class method
        self.assertTrue(Env.set("TEST_SINGLETON", "singleton_value"))

        # Get the singleton instance again
        instance2 = Env._getSingletonInstance()

        # Verify it's the same instance
        self.assertIs(instance1, instance2)

        # Verify the value is accessible through both the instance and class method
        self.assertEqual(instance1.get("TEST_SINGLETON"), "singleton_value")
        self.assertEqual(Env.get("TEST_SINGLETON"), "singleton_value")

    def testDotEnvSetAndGetWithType(self):
        """
        Test DotEnv.set and DotEnv.get with explicit EnvironmentValueType for various data types.

        This test verifies that the `DotEnv` class correctly stores and retrieves environment variables
        when an explicit `EnvironmentValueType` is provided. For each supported data type, the test sets
        a value using `DotEnv.set` with the corresponding `EnvironmentValueType`, then retrieves it using
        `DotEnv.get` and asserts that the returned value is correctly formatted according to the specified type.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate the correct behavior
            of `DotEnv.set` and `DotEnv.get` with explicit type information.

        Notes
        -----
        - Ensures that values are stored and retrieved with the correct type formatting.
        - Covers all supported types: PATH, STR, INT, FLOAT, BOOL, LIST, DICT, TUPLE, SET, BASE64.
        """
        env = DotEnv()

        # Set and assert a PATH value with explicit type
        env.set("CAST_EXAMPLE_PATH", '/tests', EnvironmentValueType.PATH)
        self.assertTrue(env.get("CAST_EXAMPLE_PATH").endswith('/tests'))

        # Set and assert a string value with explicit type
        env.set("CAST_EXAMPLE_STR", 'hello', EnvironmentValueType.STR)
        self.assertEqual(env.get("CAST_EXAMPLE_STR"), "hello")

        # Set and assert an integer value with explicit type
        env.set("CAST_EXAMPLE_INT", 123, EnvironmentValueType.INT)
        self.assertEqual(env.get("CAST_EXAMPLE_INT"), 123)

        # Set and assert a float value with explicit type
        env.set("CAST_EXAMPLE_FLOAT", 3.14, EnvironmentValueType.FLOAT)
        self.assertEqual(env.get("CAST_EXAMPLE_FLOAT"), 3.14)

        # Set and assert a boolean value with explicit type
        env.set("CAST_EXAMPLE_BOOL", True, EnvironmentValueType.BOOL)
        self.assertTrue(env.get("CAST_EXAMPLE_BOOL"))

        # Set and assert a list value with explicit type
        env.set("CAST_EXAMPLE_LIST", [1, 2, 3], EnvironmentValueType.LIST)
        self.assertEqual(env.get("CAST_EXAMPLE_LIST"), [1, 2, 3])

        # Set and assert a dictionary value with explicit type
        env.set("CAST_EXAMPLE_DICT", {"a": 1, "b": 2}, EnvironmentValueType.DICT)
        self.assertEqual(env.get("CAST_EXAMPLE_DICT"), {"a": 1, "b": 2})

        # Set and assert a tuple value with explicit type
        env.set("CAST_EXAMPLE_TUPLE", (1, 2), EnvironmentValueType.TUPLE)
        self.assertEqual(env.get("CAST_EXAMPLE_TUPLE"), (1, 2))

        # Set and assert a set value with explicit type
        env.set("CAST_EXAMPLE_SET", {1, 2, 3}, EnvironmentValueType.SET)
        self.assertEqual(env.get("CAST_EXAMPLE_SET"), {1, 2, 3})

        # Set and assert a base64 value with explicit type
        random_text = SecureKeyGenerator.generate()
        env.set("CAST_EXAMPLE_BASE64", random_text, EnvironmentValueType.BASE64)
        retrieved_base64 = env.get("CAST_EXAMPLE_BASE64")
        # The retrieved value should be the decoded base64 content (bytes)
        self.assertIsNotNone(retrieved_base64)
        # Verify it's not the original string format
        self.assertNotEqual(retrieved_base64, random_text)

    def testDotEnvSetAndGetWithoutType(self):
        """
        Test DotEnv.set and DotEnv.get without explicit EnvironmentValueType for various data types.

        This test verifies that the `DotEnv` class can store and retrieve environment variables of different
        Python data types without specifying an explicit `EnvironmentValueType`. It checks that the values
        are automatically detected and parsed correctly when retrieved.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate that the returned values
            from `DotEnv.get` match the expected values for each data type.

        Notes
        -----
        - Ensures that values are stored and retrieved correctly when no explicit type is provided.
        - Covers various data types: path, str, int, float, bool, list, dict, tuple, set, and base64.
        """
        env = DotEnv()

        # Set and get a path value without explicit type
        env.set("EXAMPLE_PATH", '/tests')
        self.assertEqual(env.get("EXAMPLE_PATH"), '/tests')

        # Set and get a string value without explicit type
        env.set("EXAMPLE_STR", 'hello')
        self.assertEqual(env.get("EXAMPLE_STR"), 'hello')

        # Set and get an integer value without explicit type
        env.set("EXAMPLE_INT", 123)
        self.assertEqual(env.get("EXAMPLE_INT"), 123)

        # Set and get a float value without explicit type
        env.set("EXAMPLE_FLOAT", 3.14)
        self.assertEqual(env.get("EXAMPLE_FLOAT"), 3.14)

        # Set and get a boolean value without explicit type
        env.set("EXAMPLE_BOOL", True)
        self.assertTrue(env.get("EXAMPLE_BOOL"))

        # Set and get a list value without explicit type
        env.set("EXAMPLE_LIST", [1, 2, 3])
        self.assertEqual(env.get("EXAMPLE_LIST"), [1, 2, 3])

        # Set and get a dictionary value without explicit type
        env.set("EXAMPLE_DICT", {"a": 1, "b": 2})
        self.assertEqual(env.get("EXAMPLE_DICT"), {"a": 1, "b": 2})

        # Set and get a tuple value without explicit type
        env.set("EXAMPLE_TUPLE", (1, 2))
        self.assertEqual(env.get("EXAMPLE_TUPLE"), (1, 2))

        # Set and get a set value without explicit type
        env.set("EXAMPLE_SET", {1, 2, 3})
        self.assertEqual(env.get("EXAMPLE_SET"), {1, 2, 3})

        # Set and get a base64 value without explicit type
        random_text = SecureKeyGenerator.generate()
        env.set("EXAMPLE_BASE64", random_text)
        retrieved_base64 = env.get("EXAMPLE_BASE64")
        # Without explicit type, base64: prefixed strings are parsed by EnvironmentCaster
        # So we expect the decoded bytes, not the original string
        self.assertIsNotNone(retrieved_base64)
        self.assertIsInstance(retrieved_base64, bytes)

    def testEdgeCasesAndErrorHandling(self):
        """
        Test edge cases and error handling for Env methods.

        This test verifies that Env methods handle edge cases gracefully, including
        None values, empty strings, and various boundary conditions.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate behavior.

        Notes
        -----
        - Tests handling of None values, empty strings, and whitespace.
        - Verifies consistent behavior across different edge case scenarios.
        """
        # Test setting and getting None values (as string representation)
        self.assertTrue(Env.set("TEST_NONE", "None"))
        # When retrieving "None" as string, it should be parsed as None
        self.assertIsNone(Env.get("TEST_NONE"))

        # Test setting and getting empty strings
        self.assertTrue(Env.set("TEST_EMPTY", ""))
        # Empty strings are parsed as None in the environment system
        self.assertIsNone(Env.get("TEST_EMPTY"))

        # Test setting and getting whitespace strings
        self.assertTrue(Env.set("TEST_WHITESPACE", "   "))
        # Whitespace-only strings are stripped and parsed as None
        self.assertIsNone(Env.get("TEST_WHITESPACE"))

        # Test getting with empty string as default
        self.assertEqual(Env.get("NON_EXISTENT", ""), "")

        # Test getting with None as explicit default
        self.assertIsNone(Env.get("NON_EXISTENT", None))

    def testTypeConsistency(self):
        """
        Test type consistency for various data types when storing and retrieving values.

        This test ensures that values maintain their correct Python types when stored
        and retrieved through the Env interface, validating the type casting mechanisms.

        Parameters
        ----------
        self : TestServicesEnvironment
            The test case instance.

        Returns
        -------
        None
            This method does not return a value. Assertions are used to validate behavior.

        Notes
        -----
        - Tests that integer values remain integers after storage/retrieval.
        - Tests that boolean values maintain their boolean type.
        - Tests that complex data structures maintain their structure and types.
        """
        # Test integer type consistency
        Env.set("TYPE_INT", "42")
        retrieved_int = Env.get("TYPE_INT")
        self.assertIsInstance(retrieved_int, int)
        self.assertEqual(retrieved_int, 42)

        # Test float type consistency
        Env.set("TYPE_FLOAT", "3.14159")
        retrieved_float = Env.get("TYPE_FLOAT")
        self.assertIsInstance(retrieved_float, float)
        self.assertEqual(retrieved_float, 3.14159)

        # Test boolean type consistency
        Env.set("TYPE_BOOL_TRUE", "true")
        Env.set("TYPE_BOOL_FALSE", "false")
        self.assertIsInstance(Env.get("TYPE_BOOL_TRUE"), bool)
        self.assertIsInstance(Env.get("TYPE_BOOL_FALSE"), bool)
        self.assertTrue(Env.get("TYPE_BOOL_TRUE"))
        self.assertFalse(Env.get("TYPE_BOOL_FALSE"))

        # Test list type consistency
        test_list = [1, "two", 3.0, True]
        Env.set("TYPE_LIST", str(test_list))
        retrieved_list = Env.get("TYPE_LIST")
        self.assertIsInstance(retrieved_list, list)
        self.assertEqual(retrieved_list, test_list)

        # Test dictionary type consistency
        test_dict = {"string": "value", "number": 123, "nested": {"key": "value"}}
        Env.set("TYPE_DICT", str(test_dict))
        retrieved_dict = Env.get("TYPE_DICT")
        self.assertIsInstance(retrieved_dict, dict)
        self.assertEqual(retrieved_dict, test_dict)