from orionis.foundation.config.cache.entities.cache import Cache
from orionis.foundation.config.cache.enums.drivers import Drivers
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.foundation.config.cache.entities.stores import Stores
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigCache(SyncTestCase):

    def testDefaultValues(self):
        """
        Validates the default attribute values of a newly created Cache instance.

        This test checks that when a Cache object is instantiated without any arguments,
        its `default` attribute is set to the expected default driver value, and its
        `stores` attribute is an instance of the Stores class.

        Returns
        -------
        None
            This method does not return any value. Assertions are used to validate behavior.
        """

        # Create a Cache instance with default parameters
        cache = Cache()

        # Assert that the default driver is set to MEMORY
        self.assertEqual(cache.default, Drivers.MEMORY.value)

        # Assert that the stores attribute is an instance of Stores
        self.assertIsInstance(cache.stores, Stores)

    def testDriverValidation(self):
        """
        Validates the handling and conversion of the `default` driver attribute in the Cache class.

        This test ensures that:
            - String representations of valid drivers are correctly converted to their corresponding enum values.
            - Invalid driver names raise an OrionisIntegrityException.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. Assertions are used to validate expected behavior.
        """

        # Test that a valid string driver is converted to the correct enum value
        cache = Cache(default="FILE")
        self.assertEqual(cache.default, Drivers.FILE.value)

        # Test that an invalid driver name raises an exception
        with self.assertRaises(OrionisIntegrityException):
            Cache(default="INVALID_DRIVER")

    def testDriverCaseInsensitivity(self):
        """
        Validates that driver names provided as strings are handled in a case-insensitive manner.

        This test ensures that the Cache class correctly normalizes driver names regardless of their case
        (lowercase, mixed case, or uppercase), and maps them to the appropriate enum value.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. Assertions are used to validate expected behavior.
        """

        # Test lowercase driver name
        cache = Cache(default="file")
        self.assertEqual(cache.default, Drivers.FILE.value)

        # Test mixed case driver name
        cache = Cache(default="FiLe")
        self.assertEqual(cache.default, Drivers.FILE.value)

        # Test uppercase driver name
        cache = Cache(default="FILE")
        self.assertEqual(cache.default, Drivers.FILE.value)

    def testTypeValidation(self):
        """
        Test type validation for all attributes.

        Ensures that invalid types for each attribute raise
        OrionisIntegrityException.

        Returns
        -------
        None
        """

        # Test invalid default type
        with self.assertRaises(OrionisIntegrityException):
            Cache(default=123)

        # Test invalid stores type
        with self.assertRaises(OrionisIntegrityException):
            Cache(stores="invalid_stores")

    def testToDictMethod(self):
        """
        Tests the `toDict` method of the Cache class for correct dictionary representation.

        This test verifies that calling `toDict` on a Cache instance returns a dictionary
        containing all expected keys and values. Specifically, it checks that:
            - The returned object is a dictionary.
            - The 'default' key in the dictionary matches the expected default driver value.
            - The 'stores' key contains a dictionary representation of the stores attribute.

        Returns
        -------
        None
            This method does not return any value. Assertions are used to validate expected behavior.
        """

        # Create a Cache instance with default parameters
        cache = Cache()

        # Call the toDict method to get the dictionary representation
        cache_dict = cache.toDict()

        # Assert that the returned object is a dictionary
        self.assertIsInstance(cache_dict, dict)

        # Assert that the 'default' key matches the expected driver value
        self.assertEqual(cache_dict['default'], Drivers.MEMORY.value)

        # Assert that the 'stores' key contains a dictionary
        self.assertIsInstance(cache_dict['stores'], dict)

    def testStoresInstanceValidation(self):
        """
        Test that the stores attribute must be an instance of Stores.

        Ensures that only Stores instances are accepted for the stores
        attribute and invalid types raise exceptions.

        Returns
        -------
        None
        """

        # Test with proper Stores instance
        # Assuming Stores has a default constructor
        stores = Stores()
        cache = Cache(stores=stores)
        self.assertIsInstance(cache.stores, Stores)

        # Test with invalid stores type
        with self.assertRaises(OrionisIntegrityException):
            Cache(stores={"file": "some_path"})

    def testDriverEnumConversion(self):
        """
        Test conversion of Drivers enum values to string representations.

        Ensures that enum members are converted to their value representations
        when used as the default driver.

        Returns
        -------
        None
        """

        # Test with enum member
        cache = Cache(default=Drivers.MEMORY)
        self.assertEqual(cache.default, Drivers.MEMORY.value)