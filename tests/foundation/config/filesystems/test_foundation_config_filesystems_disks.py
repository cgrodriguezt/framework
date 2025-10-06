from orionis.foundation.config.filesystems.entitites.aws import S3
from orionis.foundation.config.filesystems.entitites.disks import Disks
from orionis.foundation.config.filesystems.entitites.local import Local
from orionis.foundation.config.filesystems.entitites.public import Public
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigFilesystemsDisks(SyncTestCase):

    def testDefaultValues(self):
        """
        Verify that a Disks instance is created with correct default values.

        This method ensures that all default disk configurations are properly initialized
        and that each attribute is an instance of its expected class.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Disks instance with default parameters
        disks = Disks()

        # Assert that each disk attribute is an instance of the correct class
        self.assertIsInstance(disks.local, Local)
        self.assertIsInstance(disks.public, Public)
        self.assertIsInstance(disks.aws, S3)

    def testLocalTypeValidation(self):
        """
        Validate that only `Local` instances are accepted for the `local` attribute.

        This method ensures that the `local` attribute of Disks only accepts instances
        of the Local class and raises OrionisIntegrityException otherwise.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test invalid types for the local attribute
        with self.assertRaises(OrionisIntegrityException):
            Disks(local="not_a_local_instance")

        with self.assertRaises(OrionisIntegrityException):
            Disks(local=123)

        with self.assertRaises(OrionisIntegrityException):
            Disks(local=None)

    def testPublicTypeValidation(self):
        """
        Validate that only `Public` instances are accepted for the `public` attribute.

        This method ensures that the `public` attribute of Disks only accepts instances
        of the Public class and raises OrionisIntegrityException otherwise.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test invalid types for the public attribute
        with self.assertRaises(OrionisIntegrityException):
            Disks(public="not_a_public_instance")

        with self.assertRaises(OrionisIntegrityException):
            Disks(public=123)

        with self.assertRaises(OrionisIntegrityException):
            Disks(public=None)

    def testAwsTypeValidation(self):
        """
        Validate that only `S3` instances are accepted for the `aws` attribute.

        This method ensures that the `aws` attribute of Disks only accepts instances
        of the S3 class and raises OrionisIntegrityException otherwise.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test invalid types for the aws attribute
        with self.assertRaises(OrionisIntegrityException):
            Disks(aws="not_an_s3_instance")

        with self.assertRaises(OrionisIntegrityException):
            Disks(aws=123)

        with self.assertRaises(OrionisIntegrityException):
            Disks(aws=None)

    def testCustomDiskConfigurations(self):
        """
        Validate that custom disk configurations are properly stored and validated.

        This method ensures that custom disk configurations are correctly handled and their
        attributes are properly set in the Disks instance.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create custom disk configuration instances
        custom_local = Local(path="custom/local/path")
        custom_public = Public(path="custom/public/path", url="assets")
        custom_aws = S3(bucket="custom-bucket", region="eu-west-1")

        # Create a Disks instance with custom configurations
        disks = Disks(
            local=custom_local,
            public=custom_public,
            aws=custom_aws
        )

        # Assert that all custom values are correctly assigned
        self.assertEqual(disks.local.path, "custom/local/path")
        self.assertEqual(disks.public.path, "custom/public/path")
        self.assertEqual(disks.public.url, "assets")
        self.assertEqual(disks.aws.bucket, "custom-bucket")
        self.assertEqual(disks.aws.region, "eu-west-1")

    def testToDictMethod(self):
        """
        Validate that toDict returns a proper dictionary representation.

        This method ensures that all disk configurations are correctly included in the
        dictionary representation returned by toDict.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Disks instance with default parameters
        disks = Disks()

        # Convert the Disks instance to a dictionary
        disks_dict = disks.toDict()

        # Assert that the result is a dictionary and all values are correct
        self.assertIsInstance(disks_dict, dict)
        self.assertIsInstance(disks_dict['local'], dict)
        self.assertIsInstance(disks_dict['public'], dict)
        self.assertIsInstance(disks_dict['aws'], dict)

    def testHashability(self):
        """
        Validate that Disks instances are hashable and behave correctly in sets.

        This method ensures that Disks instances can be used in sets and as dictionary keys
        due to unsafe_hash=True, and that identical instances are considered equal.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two identical Disks instances
        disks1 = Disks()
        disks2 = Disks()

        # Add both to a set; should only contain one unique instance
        disks_set = {disks1, disks2}
        self.assertEqual(len(disks_set), 1)

        # Add a custom Disks instance with a different local path
        custom_disks = Disks(local=Local(path="custom/path"))
        disks_set.add(custom_disks)

        # Now the set should contain two unique instances
        self.assertEqual(len(disks_set), 2)

    def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Disks.

        This method ensures that positional arguments are not allowed for initialization
        and raises TypeError if attempted.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Disks with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Disks(Local(), Public(), S3())