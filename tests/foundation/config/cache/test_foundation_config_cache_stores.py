from orionis.foundation.config.cache.entities.stores import Stores
from orionis.foundation.config.cache.entities.file import File
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigCacheStores(AsyncTestCase):

    async def testDefaultFileStore(self):
        """
        Test initialization with the default File instance.

        This test verifies that a `Stores` object is initialized with a default `File` instance and that the `file` attribute is set to the default configuration path.

        Returns
        -------
        None
            This test does not return a value; it asserts correctness using test assertions.
        """

        # Initialize Stores without any parameters to use default values
        stores = Stores()

        # Assert that the file attribute is an instance of File
        self.assertIsInstance(stores.file, File)

        # Assert that the default file path is set correctly
        self.assertEqual(stores.file.path, 'storage/framework/cache/data')

    async def testCustomFileStore(self):
        """
        Test initialization with a custom File configuration.

        This test verifies that a custom `File` instance or a dictionary can be provided during initialization and is correctly assigned to the `file` attribute.

        Returns
        -------
        None
            This test does not return a value; it asserts correctness using test assertions.
        """

        # Create a custom File instance and pass it to Stores
        custom_file = File(path='custom/cache/path')
        stores = Stores(file=custom_file)
        self.assertIsInstance(stores.file, File)
        self.assertEqual(stores.file.path, 'custom/cache/path')

        # Pass a dictionary to Stores and verify the file path
        stores_dict = Stores(file={'path': 'dict/cache/path'})
        self.assertIsInstance(stores_dict.file, File)
        self.assertEqual(stores_dict.file.path, 'dict/cache/path')

    async def testFileTypeValidation(self):
        """
        Test type validation for the file attribute.

        This test ensures that providing a value other than a `File` instance or a dictionary to the `file` attribute raises an `OrionisIntegrityException`.

        Returns
        -------
        None
            This test does not return a value; it asserts correctness using test assertions.

        Raises
        ------
        OrionisIntegrityException
            If the `file` attribute is not a `File` instance or dict.
        """

        # Attempt to initialize Stores with an invalid string value
        with self.assertRaises(OrionisIntegrityException):
            Stores(file="not_a_file_instance")

        # Attempt to initialize Stores with an invalid integer value
        with self.assertRaises(OrionisIntegrityException):
            Stores(file=123)

        # Attempt to initialize Stores with None
        with self.assertRaises(OrionisIntegrityException):
            Stores(file=None)

    async def testToDictMethodWithDefaults(self):
        """
        Test dictionary representation with default values.

        This test verifies that the `toDict` method returns a dictionary with the correct default file path when no custom configuration is provided.

        Returns
        -------
        None
            This test does not return a value; it asserts correctness using test assertions.
        """

        # Create a Stores instance with default configuration
        stores = Stores()
        stores_dict = stores.toDict()

        # Assert that the result is a dictionary
        self.assertIsInstance(stores_dict, dict)
        # Assert that the 'file' key contains a dictionary
        self.assertIsInstance(stores_dict['file'], dict)
        # Assert that the default file path is present in the dictionary
        self.assertEqual(stores_dict['file']['path'], 'storage/framework/cache/data')

    async def testToDictMethodWithCustomFile(self):
        """
        Test dictionary representation with custom file configuration.

        This test verifies that the `toDict` method reflects custom file paths in its dictionary representation when a custom configuration is provided.

        Returns
        -------
        None
            This test does not return a value; it asserts correctness using test assertions.
        """

        # Create a Stores instance with a custom File path
        custom_file = File(path='alternate/cache/location')
        stores = Stores(file=custom_file)
        stores_dict = stores.toDict()

        # Assert that the custom file path is present in the dictionary
        self.assertEqual(stores_dict['file']['path'], 'alternate/cache/location')

        # Create a Stores instance with a custom dictionary path
        stores_dict_input = Stores(file={'path': 'dict/location'})
        stores_dict2 = stores_dict_input.toDict()
        # Assert that the dictionary path is present in the dictionary
        self.assertEqual(stores_dict2['file']['path'], 'dict/location')

    async def testHashability(self):
        """
        Test hashability of Stores instances.

        This test verifies that `Stores` instances are hashable and can be used in sets and as dictionary keys.

        Returns
        -------
        None
            This test does not return a value; it asserts correctness using test assertions.
        """

        # Create two Stores instances with default configuration
        store1 = Stores()
        store2 = Stores()

        # Add two Stores instances with default configuration to a set
        store_set = {store1, store2}

        # Assert that only one unique instance exists in the set
        self.assertEqual(len(store_set), 1)

        # Add a Stores instance with a custom file path to the set
        custom_store = Stores(file=File(path='custom/path'))
        store_set.add(custom_store)

        # Assert that the set now contains two unique instances
        self.assertEqual(len(store_set), 2)

    async def testKwOnlyInitialization(self):
        """
        Test keyword-only initialization enforcement.

        This test verifies that `Stores` enforces keyword-only arguments and does not allow positional arguments during initialization.

        Returns
        -------
        None
            This test does not return a value; it asserts correctness using test assertions.

        Raises
        ------
        TypeError
            If positional arguments are provided during initialization.
        """

        # Attempt to initialize Stores with a positional argument
        with self.assertRaises(TypeError):
            Stores(File())