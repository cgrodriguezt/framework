from orionis.foundation.config.filesystems.entitites.local import Local
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigFilesystemsLocal(SyncTestCase):

    def testDefaultPath(self):
        """
        Verify that a Local instance is created with the correct default path.

        This method ensures that the default path of a Local instance matches the expected value.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Local instance with default parameters
        local = Local()

        # Assert that the default path is as expected
        self.assertEqual(local.path, "storage/app/private")

    def testCustomPath(self):
        """
        Validate that a custom path can be set during initialization.

        This method ensures that the path attribute accepts and stores valid custom paths.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Define a custom path
        custom_path = "custom/storage/path"

        # Create a Local instance with the custom path
        local = Local(path=custom_path)

        # Assert that the custom path is stored correctly
        self.assertEqual(local.path, custom_path)

    def testEmptyPathValidation(self):
        """
        Validate that empty paths are rejected during initialization.

        This method ensures that initializing Local with an empty path raises OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Local with an empty path; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Local(path="")

    def testPathTypeValidation(self):
        """
        Validate that non-string paths are rejected during initialization.

        This method ensures that non-string path values raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Local with a non-string path; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Local(path=123)

        with self.assertRaises(OrionisIntegrityException):
            Local(path=None)

        with self.assertRaises(OrionisIntegrityException):
            Local(path=[])

    def testToDictMethod(self):
        """
        Validate the dictionary representation of a Local instance.

        This method ensures that toDict returns a dictionary containing the expected path value.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Local instance with default parameters
        local = Local()

        # Convert the Local instance to a dictionary
        config_dict = local.toDict()

        # Assert that the dictionary contains the correct path
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict['path'], "storage/app/private")

    def testCustomPathToDict(self):
        """
        Validate the dictionary representation with a custom path.

        This method ensures that toDict includes custom path values when specified.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Define a custom path
        custom_path = "another/storage/location"

        # Create a Local instance with the custom path
        local = Local(path=custom_path)

        # Convert the Local instance to a dictionary
        config_dict = local.toDict()

        # Assert that the dictionary contains the custom path
        self.assertEqual(config_dict['path'], custom_path)

    def testWhitespacePathHandling(self):
        """
        Validate handling of paths with whitespace in Local.

        This method ensures that paths containing whitespace are accepted and not automatically trimmed.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Define a path with leading and trailing whitespace
        spaced_path = "  storage/with/space  "

        # Create a Local instance with the spaced path
        local = Local(path=spaced_path)

        # Assert that the path is stored as-is, including whitespace
        self.assertEqual(local.path, spaced_path)

    def testHashability(self):
        """
        Validate hashability of Local instances.

        This method ensures that Local instances can be used in sets and as dictionary keys,
        and that identical instances are considered equal.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two identical Local instances
        local1 = Local()
        local2 = Local()

        # Add both to a set; should only contain one unique instance
        local_set = {local1, local2}
        self.assertEqual(len(local_set), 1)

        # Add a custom Local instance with a different path
        custom_local = Local(path="custom/path")
        local_set.add(custom_local)

        # Now the set should contain two unique instances
        self.assertEqual(len(local_set), 2)

    def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Local.

        This method ensures that positional arguments are not allowed for Local initialization
        and raises TypeError if attempted.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Local with a positional argument; should raise TypeError
        with self.assertRaises(TypeError):
            Local("storage/path")