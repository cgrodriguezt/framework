from orionis.foundation.config.queue.entities.queue import Queue
from orionis.foundation.config.queue.entities.brokers import Brokers
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigQueue(SyncTestCase):

    def testDefaultInitialization(self):
        """
        Verify that a Queue instance is initialized with correct default values.

        This method checks that a Queue instance is initialized with the correct default values for its attributes.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Queue instance with default parameters
        queue = Queue()

        # Assert that the default value and brokers attribute are as expected
        self.assertEqual(queue.default, "sync")
        self.assertIsInstance(queue.brokers, Brokers)

    def testDefaultValidation(self):
        """
        Validate the default attribute for correct value.

        This method checks that invalid values for the `default` attribute raise an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Queue with invalid default values; should raise exception
        invalid_options = ["invalid", "", 123, None]
        for option in invalid_options:
            with self.assertRaises(OrionisIntegrityException):
                Queue(default=option)

    def testValidCustomInitialization(self):
        """
        Validate custom initialization with valid parameters for Queue.

        This method verifies that a Queue instance can be initialized with a valid default value and a Brokers instance.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a custom Brokers instance
        custom_brokers = Brokers(sync=False)

        # Initialize Queue with custom values
        queue = Queue(default="sync", brokers=custom_brokers)

        # Assert that the custom values are stored correctly
        self.assertEqual(queue.default, "sync")
        self.assertIs(queue.brokers, custom_brokers)
        self.assertFalse(queue.brokers.sync)

    def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Queue.

        This method ensures that the `toDict` method returns a dictionary representation of the Queue instance with all fields and correct values.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Queue instance
        queue = Queue()

        # Convert the Queue instance to a dictionary
        result = queue.toDict()

        # Assert that the dictionary contains the expected keys and values
        self.assertIsInstance(result, dict)
        self.assertEqual(result["default"], "sync")
        self.assertIsInstance(result["brokers"], dict)
        self.assertTrue(result["brokers"]["sync"])