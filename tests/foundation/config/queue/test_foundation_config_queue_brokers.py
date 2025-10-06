from orionis.foundation.config.queue.entities.brokers import Brokers
from orionis.foundation.config.queue.entities.database import Database
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigQueueBrokers(SyncTestCase):

    def testDefaultInitialization(self):
        """
        Verify that a Brokers instance is initialized with correct default values.

        This method checks that `sync` is `True` by default and `database` is a `Database` instance.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Brokers instance with default parameters
        brokers = Brokers()

        # Assert that sync is True and database is a Database instance
        self.assertTrue(brokers.sync)
        self.assertIsInstance(brokers.database, Database)

    def testSyncValidation(self):
        """
        Validate the sync attribute for correct type.

        This method checks that non-boolean values for `sync` raise `OrionisIntegrityException`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Brokers with a string for sync; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Brokers(sync="true")

        # Attempt to initialize Brokers with an integer for sync; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Brokers(sync=1)

    def testCustomInitialization(self):
        """
        Validate custom initialization with valid parameters.

        This method checks that valid boolean and `Database` instances are accepted for initialization.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a custom Database instance
        custom_db = Database(table="custom_queue")

        # Initialize Brokers with custom values
        brokers = Brokers(sync=False, database=custom_db)

        # Assert that the custom values are stored correctly
        self.assertFalse(brokers.sync)
        self.assertIs(brokers.database, custom_db)
        self.assertEqual(brokers.database.table, "custom_queue")

    def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Brokers.

        This method checks that all fields are included with correct values in the returned dictionary.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Brokers instance
        brokers = Brokers()

        # Convert the Brokers instance to a dictionary
        result = brokers.toDict()

        # Assert that the dictionary contains the expected keys and values
        self.assertIsInstance(result, dict)
        self.assertIn("sync", result)
        self.assertIn("database", result)
        self.assertTrue(result["sync"])
        self.assertIsInstance(result["database"], dict)

    def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Brokers.

        This method ensures that the class enforces `kw_only=True` in its dataclass decorator and raises a TypeError if positional arguments are used.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Brokers with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Brokers(True, Database())