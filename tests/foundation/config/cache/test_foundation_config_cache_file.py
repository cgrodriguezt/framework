from orionis.foundation.config.cache.entities.file import File
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigCacheFile(SyncTestCase):

    def testDefaultPath(self):
        """
        Test default path initialization for File cache configuration.

        This test verifies that when a File instance is created without specifying a path,
        it initializes with the expected default path value.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness of the default path.
        """
        # Create a File instance with default parameters
        file_config = File()

        # Assert that the default path is set correctly
        self.assertEqual(file_config.path, "storage/framework/cache/data")

    def testCustomPath(self):
        """
        Test custom path initialization for File cache configuration.

        This test verifies that a custom path provided during initialization of the File
        cache configuration entity is correctly stored in the object's `path` attribute.

        Parameters
        ----------
        self : TestFoundationConfigCacheFile
            The test case instance.

        Returns
        -------
        None
            This method does not return any value. It asserts that the custom path is set correctly.
        """
        # Define a custom path for the cache file
        custom_path = "custom/cache/path"

        # Create a File instance with the custom path
        file_config = File(path=custom_path)

        # Assert that the File instance's path matches the custom path
        self.assertEqual(file_config.path, custom_path)

    def testEmptyPathValidation(self):
        """
        Validate behavior when an empty path is provided to the File cache configuration.

        This test checks that initializing a File instance with an empty string as the path
        raises an OrionisIntegrityException, ensuring that empty paths are not allowed.

        Parameters
        ----------
        self : TestFoundationConfigCacheFile
            The test case instance.

        Returns
        -------
        None
            This method does not return any value. It asserts that an exception is raised.

        Raises
        ------
        OrionisIntegrityException
            Raised when the path is an empty string.
        """
        # Attempt to create a File instance with an empty path and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            File(path="")

    def testPathTypeValidation(self):
        """
        Validate the type of the `path` parameter in File cache configuration.

        This test ensures that the `File` entity enforces strict type checking for the `path`
        attribute. If a non-string value is provided, the entity should raise an
        `OrionisIntegrityException`, preventing invalid configuration states.

        Parameters
        ----------
        self : TestFoundationConfigCacheFile
            The test case instance.

        Returns
        -------
        None
            This method does not return any value. It asserts that exceptions are raised for invalid types.

        Raises
        ------
        OrionisIntegrityException
            Raised when the `path` parameter is not a string.
        """
        # Attempt to create a File instance with an integer path; should raise an exception
        with self.assertRaises(OrionisIntegrityException):
            File(path=123)

        # Attempt to create a File instance with a None path; should raise an exception
        with self.assertRaises(OrionisIntegrityException):
            File(path=None)

        # Attempt to create a File instance with a list as path; should raise an exception
        with self.assertRaises(OrionisIntegrityException):
            File(path=[])

    def testToDictMethod(self):
        """
        Test the dictionary representation of the File cache configuration.

        This test verifies that the `toDict` method of the `File` cache configuration entity
        returns a dictionary containing the expected default path value. It also checks that
        the returned object is of type `dict`.

        Parameters
        ----------
        self : TestFoundationConfigCacheFile
            The test case instance.

        Returns
        -------
        None
            This method does not return any value. It asserts the correctness of the dictionary
            representation and the default path value.
        """
        # Create a File instance with default parameters
        file_config = File()

        # Convert the File configuration to a dictionary
        config_dict = file_config.toDict()

        # Assert that the returned object is a dictionary
        self.assertIsInstance(config_dict, dict)

        # Assert that the dictionary contains the expected default path value
        self.assertEqual(config_dict["path"], "storage/framework/cache/data")

    def testCustomPathToDict(self):
        """
        Test dictionary representation with a custom path.

        Validates that when a custom path is provided to the File cache configuration,
        the `toDict` method returns a dictionary containing the correct custom path value.
        This ensures that the File entity accurately reflects custom configuration in its
        dictionary output.

        Parameters
        ----------
        self : TestFoundationConfigCacheFile
            The test case instance.

        Returns
        -------
        None
            This method does not return any value. It asserts that the dictionary representation
            contains the custom path.
        """
        # Define a custom path for the cache file
        custom_path = "another/cache/location"

        # Create a File instance with the custom path
        file_config = File(path=custom_path)

        # Convert the File configuration to a dictionary
        config_dict = file_config.toDict()

        # Assert that the dictionary contains the custom path value
        self.assertEqual(config_dict["path"], custom_path)

    def testWhitespacePathHandling(self):
        """
        Test behavior when the cache path contains leading or trailing whitespace.

        This test verifies that the File cache configuration entity accepts paths with whitespace
        and does not automatically trim or modify them. It ensures that the provided path value,
        including any whitespace, is stored exactly as given.

        Parameters
        ----------
        self : TestFoundationConfigCacheFile
            The test case instance.

        Returns
        -------
        None
            This method does not return any value. It asserts that the path with whitespace is stored as-is.
        """
        # Define a path string with leading and trailing whitespace
        spaced_path = "  storage/cache/with/space  "

        # Create a File instance using the whitespace-containing path
        file_config = File(path=spaced_path)

        # Assert that the File instance's path matches the original string, including whitespace
        self.assertEqual(file_config.path, spaced_path)
