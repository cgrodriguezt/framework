from orionis.foundation.config.queue.entities.database import Database
from orionis.foundation.config.queue.enums.strategy import Strategy
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigQueueDatabase(SyncTestCase):

    def testDefaultInitialization(self):
        """
        Verify that a Database instance is initialized with correct default values.

        This method checks that a Database instance is initialized with the correct default values for
        table name, queue name, retry_after, and strategy.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Database instance with default parameters
        db_queue = Database()

        # Assert that all default attribute values are as expected
        self.assertEqual(db_queue.table, "jobs")
        self.assertEqual(db_queue.queue, "default")
        self.assertEqual(db_queue.retry_after, 90)
        self.assertEqual(db_queue.strategy, Strategy.FIFO.value)

    def testTableNameValidation(self):
        """
        Validate the table name attribute for correct value and type.

        This method checks that invalid table names raise an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Attempt to initialize Database with invalid table names; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Database(table="1jobs")  # Starts with number
        with self.assertRaises(OrionisIntegrityException):
            Database(table="Jobs")  # Uppercase letter
        with self.assertRaises(OrionisIntegrityException):
            Database(table="jobs-table")  # Invalid character
        with self.assertRaises(OrionisIntegrityException):
            Database(table=123)  # Non-string value

    def testQueueNameValidation(self):
        """
        Validate the queue name attribute for correct value and type.

        This method checks that non-ASCII queue names and non-string values raise an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Attempt to initialize Database with a non-ASCII queue name; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Database(queue="café")  # Non-ASCII character

        # Attempt to initialize Database with a non-string queue name; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Database(queue=123)  # Non-string value

    def testRetryAfterValidation(self):
        """
        Validate the retry_after attribute for correct value and type.

        This method ensures that non-positive integers and non-integer values raise an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Attempt to initialize Database with invalid retry_after values; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Database(retry_after=0)
        with self.assertRaises(OrionisIntegrityException):
            Database(retry_after=-1)
        with self.assertRaises(OrionisIntegrityException):
            Database(retry_after="90")  # String instead of int

    def testStrategyValidation(self):
        """
        Validate the strategy attribute for correct value and normalization.

        This method verifies that both string and Strategy enum inputs are handled properly, and that
        invalid inputs raise an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Test string inputs (case-insensitive)
        db1 = Database(strategy="fifo")
        self.assertEqual(db1.strategy, Strategy.FIFO.value)
        db2 = Database(strategy="LIFO")
        self.assertEqual(db2.strategy, Strategy.LIFO.value)

        # Test enum inputs
        db3 = Database(strategy=Strategy.PRIORITY)
        self.assertEqual(db3.strategy, Strategy.PRIORITY.value)

        # Attempt to initialize Database with invalid strategy values; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Database(strategy="invalid_strategy")
        with self.assertRaises(OrionisIntegrityException):
            Database(strategy=123)

    def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Database.

        This method ensures that the toDict method returns a dictionary representation of the Database
        instance with all fields included and correct values.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Database instance
        db_queue = Database()

        # Convert the Database instance to a dictionary
        result = db_queue.toDict()

        # Assert that the dictionary contains the expected keys and values
        self.assertIsInstance(result, dict)
        self.assertEqual(result["table"], "jobs")
        self.assertEqual(result["queue"], "default")
        self.assertEqual(result["retry_after"], 90)
        self.assertEqual(result["strategy"], Strategy.FIFO.value)

    def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Database.

        This method ensures that the Database class requires keyword arguments for initialization,
        enforcing kw_only=True in its dataclass decorator. Raises a TypeError if positional arguments are used.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Attempt to initialize Database with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Database("jobs", "default", 90, Strategy.FIFO)
