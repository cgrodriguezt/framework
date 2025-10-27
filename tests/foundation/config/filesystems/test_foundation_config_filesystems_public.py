from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.foundation.config.filesystems.entitites.public import Public
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigFilesystemsPublic(SyncTestCase):

    def testDefaultValues(self):
        """
        Verify that a Public instance is created with correct default values.

        This method ensures that the default `path` and `url` attributes are set as defined
        in the class.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Public instance with default parameters
        public = Public()

        # Assert that the default path and url are as expected
        self.assertEqual(public.path, "storage/app/public")
        self.assertEqual(public.url, "/static")

    def testCustomValues(self):
        """
        Validate assignment of custom values to path and url attributes.

        This method checks that custom `path` and `url` values are accepted and stored
        correctly during initialization.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Define custom values for path and url
        custom_path = "custom/public/path"
        custom_url = "assets"

        # Create a Public instance with custom values
        public = Public(path=custom_path, url=custom_url)

        # Assert that the custom values are stored correctly
        self.assertEqual(public.path, custom_path)
        self.assertEqual(public.url, custom_url)

    def testEmptyPathValidation(self):
        """
        Validate that empty path values are rejected during initialization.

        This method verifies that providing an empty string for `path` raises
        OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Public with an empty path; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Public(path="")

    def testEmptyUrlValidation(self):
        """
        Validate that empty url values are rejected during initialization.

        This method verifies that providing an empty string for `url` raises
        OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Public with an empty url; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Public(url="")

    def testTypeValidation(self):
        """
        Validate type checking for path and url attributes.

        This method ensures that non-string values for `path` and `url` raise
        OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test path type validation
        with self.assertRaises(OrionisIntegrityException):
            Public(path=123)

        with self.assertRaises(OrionisIntegrityException):
            Public(path=None)

        # Test url type validation
        with self.assertRaises(OrionisIntegrityException):
            Public(url=123)

        with self.assertRaises(OrionisIntegrityException):
            Public(url=None)

    def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for default values.

        This method ensures that the dictionary representation contains the correct
        default values for `path` and `url`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Public instance with default parameters
        public = Public()

        # Convert the Public instance to a dictionary
        config_dict = public.toDict()

        # Assert that the dictionary contains the correct default values
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict['path'], "storage/app/public")
        self.assertEqual(config_dict['url'], "/static")

    def testCustomValuesToDict(self):
        """
        Validate the dictionary output of toDict with custom values.

        This method ensures that the dictionary representation includes custom
        `path` and `url` values when specified.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Define custom values for path and url
        custom_path = "public/assets"
        custom_url = "cdn"

        # Create a Public instance with custom values
        public = Public(path=custom_path, url=custom_url)

        # Convert the Public instance to a dictionary
        config_dict = public.toDict()

        # Assert that the dictionary contains the custom values
        self.assertEqual(config_dict['path'], custom_path)
        self.assertEqual(config_dict['url'], custom_url)

    def testWhitespaceHandling(self):
        """
        Validate handling of whitespace in attribute values.

        This method verifies that values containing whitespace are accepted and
        not automatically trimmed.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Define values with leading and trailing whitespace
        spaced_path = "  public/storage  "
        spaced_url = "  static/files  "

        # Create a Public instance with whitespace in path and url
        public = Public(path=spaced_path, url=spaced_url)

        # Assert that the values are stored as-is, including whitespace
        self.assertEqual(public.path, spaced_path)
        self.assertEqual(public.url, spaced_url)

    def testHashability(self):
        """
        Validate hashability of Public instances.

        This method ensures that Public instances are hashable and can be used in sets
        and as dictionary keys due to `unsafe_hash=True`, and that identical instances are considered equal.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two identical Public instances
        public1 = Public()
        public2 = Public()

        # Add both to a set; should only contain one unique instance
        public_set = {public1, public2}
        self.assertEqual(len(public_set), 1)

        # Add a custom Public instance with different values
        custom_public = Public(path="custom/public", url="custom-url")
        public_set.add(custom_public)

        # Now the set should contain two unique instances
        self.assertEqual(len(public_set), 2)

    def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Public.

        This method verifies that positional arguments are not allowed when initializing
        a Public instance and raises TypeError if attempted.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Public with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Public("storage/path", "static")