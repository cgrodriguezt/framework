from orionis.foundation.config.logging.entities.logging import Logging
from orionis.foundation.config.logging.entities.channels import Channels
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigLogging(AsyncTestCase):

    async def testDefaultValues(self):
        """
        Verify that a Logging instance is created with correct default values.

        This method ensures that a new Logging instance is initialized with the correct default values
        for its attributes.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Logging instance with default parameters
        logging = Logging()

        # Assert that the default channel and channels attributes are as expected
        self.assertEqual(logging.default, "stack")
        self.assertIsInstance(logging.channels, Channels)

    async def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Logging.

        This method checks that the toDict method returns a dictionary representation with all expected fields.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Logging instance
        logging = Logging()

        # Convert the Logging instance to a dictionary
        result = logging.toDict()

        # Assert that the dictionary contains the expected keys
        self.assertIsInstance(result, dict)
        self.assertIn("default", result)
        self.assertIn("channels", result)

    async def testPostInitValidation(self):
        """
        Validate post-initialization checks for Logging.

        This method verifies that providing an invalid default channel or channels type raises an exception.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Logging with an invalid default channel; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Logging(default="invalid_channel")

        # Attempt to initialize Logging with an invalid channels type; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Logging(channels="invalid_channels")

    async def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Logging.

        This method ensures that Logging requires keyword arguments for initialization and raises
        a TypeError if positional arguments are used.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Logging with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Logging("stack", Channels())