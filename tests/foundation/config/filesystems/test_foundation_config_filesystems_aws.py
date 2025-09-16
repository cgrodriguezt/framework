from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.foundation.config.filesystems.entitites.aws import S3
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigFilesystemsAws(AsyncTestCase):

    async def testDefaultValues(self):
        """
        Verify that a new S3 instance initializes with correct default values.

        This method checks that all attributes of a newly created S3 instance
        are set to their expected default values as defined in the class.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a new S3 instance with default parameters
        s3 = S3()

        # Assert default values for all attributes
        self.assertEqual(s3.key, "")
        self.assertEqual(s3.secret, "")
        self.assertEqual(s3.region, "us-east-1")
        self.assertEqual(s3.bucket, "")
        self.assertIsNone(s3.url)
        self.assertIsNone(s3.endpoint)
        self.assertFalse(s3.use_path_style_endpoint)
        self.assertFalse(s3.throw)

    async def testRequiredFieldValidation(self):
        """
        Validate required field constraints for the S3 configuration.

        This method checks that the 'region' field must be a non-empty string and
        raises OrionisIntegrityException if the constraint is violated.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test that an empty string for region raises an exception
        with self.assertRaises(OrionisIntegrityException):
            S3(region="")

        # Test that a non-string value for region raises an exception
        with self.assertRaises(OrionisIntegrityException):
            S3(region=123)

    async def testOptionalFieldValidation(self):
        """
        Validate optional field types for the S3 configuration.

        This method ensures that optional fields accept None or valid types, and raises
        OrionisIntegrityException for invalid types.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test valid optional configurations for url and endpoint
        try:
            S3(url=None, endpoint=None)
            S3(url="https://example.com", endpoint="https://s3.example.com")
        except OrionisIntegrityException:
            self.fail("Valid optional configurations should not raise exceptions")

        # Test invalid type for url
        with self.assertRaises(OrionisIntegrityException):
            S3(url=123)

        # Test invalid type for endpoint
        with self.assertRaises(OrionisIntegrityException):
            S3(endpoint=[])

    async def testBooleanFieldValidation(self):
        """
        Validate boolean field types for the S3 configuration.

        This method ensures that boolean fields accept only boolean values and raises
        OrionisIntegrityException for invalid types.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test that a non-boolean value for use_path_style_endpoint raises an exception
        with self.assertRaises(OrionisIntegrityException):
            S3(use_path_style_endpoint="true")

        # Test that a non-boolean value for throw raises an exception
        with self.assertRaises(OrionisIntegrityException):
            S3(throw=1)

    async def testCustomValues(self):
        """
        Validate assignment and storage of custom values in the S3 configuration.

        This method ensures that custom values provided during initialization are correctly
        stored and validated in the S3 instance.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create an S3 instance with custom values for all attributes
        custom_s3 = S3(
            key="AKIAEXAMPLE",
            secret="secret123",
            region="eu-west-1",
            bucket="my-bucket",
            url="https://my-bucket.s3.amazonaws.com",
            endpoint="https://s3.eu-west-1.amazonaws.com",
            use_path_style_endpoint=True,
            throw=True
        )

        # Assert that all custom values are correctly assigned
        self.assertEqual(custom_s3.key, "AKIAEXAMPLE")
        self.assertEqual(custom_s3.secret, "secret123")
        self.assertEqual(custom_s3.region, "eu-west-1")
        self.assertEqual(custom_s3.bucket, "my-bucket")
        self.assertEqual(custom_s3.url, "https://my-bucket.s3.amazonaws.com")
        self.assertEqual(custom_s3.endpoint, "https://s3.eu-west-1.amazonaws.com")
        self.assertTrue(custom_s3.use_path_style_endpoint)
        self.assertTrue(custom_s3.throw)

    async def testToDictMethod(self):
        """
        Validate the dictionary conversion of the S3 configuration.

        This method ensures that the toDict method returns a dictionary containing all
        attributes of the S3 instance with correct values.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a default S3 instance
        s3 = S3()

        # Convert the S3 instance to a dictionary
        s3_dict = s3.toDict()

        # Assert that the result is a dictionary and all values are correct
        self.assertIsInstance(s3_dict, dict)
        self.assertEqual(s3_dict['key'], "")
        self.assertEqual(s3_dict['secret'], "")
        self.assertEqual(s3_dict['region'], "us-east-1")
        self.assertEqual(s3_dict['bucket'], "")
        self.assertIsNone(s3_dict['url'])
        self.assertIsNone(s3_dict['endpoint'])
        self.assertFalse(s3_dict['use_path_style_endpoint'])
        self.assertFalse(s3_dict['throw'])

    async def testHashability(self):
        """
        Validate hashability of S3 configuration instances.

        This method ensures that S3 instances are hashable and can be used in sets and as
        dictionary keys due to unsafe_hash=True.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two identical S3 instances
        s3_1 = S3()
        s3_2 = S3()

        # Add both to a set; should only contain one unique instance
        s3_set = {s3_1, s3_2}
        self.assertEqual(len(s3_set), 1)

        # Add a custom S3 instance with a different bucket value
        custom_s3 = S3(bucket="custom-bucket")
        s3_set.add(custom_s3)

        # Now the set should contain two unique instances
        self.assertEqual(len(s3_set), 2)

    async def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for S3.

        This method ensures that S3 cannot be initialized with positional arguments and
        raises TypeError if attempted.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize S3 with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            S3("key", "secret", "region")