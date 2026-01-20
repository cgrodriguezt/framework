from orionis.foundation.config.filesystems.entitites.disks import Disks
from orionis.foundation.config.filesystems.entitites.filesystems import Filesystems
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigFilesystems(SyncTestCase):
    """
    Test cases for the Filesystems configuration class.

    This class contains unit tests for the `Filesystems` configuration class,
    including validation of default values, disk types, dictionary conversion,
    custom values, hashability, and keyword-only initialization.
    """

    def testDefaultValues(self):
        """
        Verify that a Filesystems instance is created with correct default values.

        This method ensures that the default disk is set to 'local' and the disks attribute
        is properly initialized as a Disks instance.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Filesystems instance with default parameters
        fs = Filesystems()

        # Assert that the default disk is 'local'
        self.assertEqual(fs.default, "local")

        # Assert that the disks attribute is an instance of Disks
        self.assertIsInstance(fs.disks, Disks)

    def testDefaultDiskValidation(self):
        """
        Validate the default disk attribute for allowed values and error handling.

        This method checks that only valid disk types are accepted as default and that
        invalid types raise an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Test valid disk types for the default attribute
        valid_disks = ["local", "public", "aws"]
        for disk in valid_disks:
            try:
                # Should not raise exception for valid disk types
                Filesystems(default=disk)
            except OrionisIntegrityException:
                self.fail(f"Valid disk type '{disk}' should not raise exception")

        # Test invalid disk type
        with self.assertRaises(OrionisIntegrityException):
            # Should raise exception for an invalid disk type
            Filesystems(default="invalid_disk")

        # Test empty default value
        with self.assertRaises(OrionisIntegrityException):
            # Should raise exception for empty string as default
            Filesystems(default="")

        # Test non-string default value
        with self.assertRaises(OrionisIntegrityException):
            # Should raise exception for non-string default value
            Filesystems(default=123)

    def testDisksValidation(self):
        """
        Validate the disks attribute for correct type and error handling.

        This method ensures that only instances of Disks are accepted for the disks attribute.
        Invalid types should raise an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Test invalid type for disks attribute
        with self.assertRaises(OrionisIntegrityException):
            # Should raise exception for non-Disks type
            Filesystems(disks="not_a_disks_instance")

        # Test None as disks attribute
        with self.assertRaises(OrionisIntegrityException):
            # Should raise exception for None as disks
            Filesystems(disks=None)

        # Test valid Disks instance
        try:
            # Should not raise exception for valid Disks instance
            Filesystems(disks=Disks())
        except OrionisIntegrityException:
            self.fail("Valid Disks instance should not raise exception")

    def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method.

        This method ensures that the method returns a dictionary representation of the
        Filesystems instance with all attributes correctly included.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Filesystems instance with default parameters
        fs = Filesystems()

        # Convert the Filesystems instance to a dictionary
        fs_dict = fs.toDict()

        # Assert that the dictionary contains the correct values
        self.assertIsInstance(fs_dict, dict)
        self.assertEqual(fs_dict["default"], "local")
        self.assertIsInstance(fs_dict["disks"], dict)

    def testCustomValues(self):
        """
        Validate assignment and storage of custom values in Filesystems.

        This method ensures that custom configurations are properly stored and validated
        in the Filesystems instance.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a custom Disks instance
        custom_disks = Disks()

        # Create a Filesystems instance with custom values
        custom_fs = Filesystems(
            default="aws",
            disks=custom_disks,
        )

        # Assert that the custom values are stored correctly
        self.assertEqual(custom_fs.default, "aws")
        self.assertIs(custom_fs.disks, custom_disks)

    def testHashability(self):
        """
        Validate hashability of Filesystems instances.

        This method ensures that Filesystems instances are hashable and can be used in sets
        and as dictionary keys due to `unsafe_hash=True`, and that identical instances are considered equal.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create two identical Filesystems instances
        fs1 = Filesystems()
        fs2 = Filesystems()

        # Add both to a set; should only contain one unique instance
        fs_set = {fs1, fs2}
        self.assertEqual(len(fs_set), 1)

        # Add a custom Filesystems instance with a different default value
        custom_fs = Filesystems(default="public")
        fs_set.add(custom_fs)

        # Now the set should contain two unique instances
        self.assertEqual(len(fs_set), 2)

    def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Filesystems.

        This method ensures that Filesystems enforces keyword-only arguments and does not
        allow positional arguments during initialization. Raises TypeError if attempted.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Attempt to initialize Filesystems with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Filesystems("local", Disks())
