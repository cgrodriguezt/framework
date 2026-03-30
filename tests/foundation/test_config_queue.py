from orionis.test import TestCase
from orionis.foundation.config.queue.entities.queue import Queue
from orionis.foundation.config.queue.entities.brokers import Brokers
from orionis.foundation.config.queue.entities.database import Database as QueueDatabase
from orionis.foundation.config.queue.enums.strategy import Strategy

# ===========================================================================
# Strategy enum
# ===========================================================================

class TestStrategyEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that FIFO, LIFO and PRIORITY members exist in Strategy.

        Returns
        -------
        None
            This method does not return a value.
        """
        for name in ("FIFO", "LIFO", "PRIORITY"):
            self.assertIn(name, Strategy._member_names_)

    def testMemberValues(self) -> None:
        """
        Test the string values assigned to each Strategy member.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Strategy.FIFO.value, "fifo")
        self.assertEqual(Strategy.LIFO.value, "lifo")
        self.assertEqual(Strategy.PRIORITY.value, "priority")

    def testLookupByName(self) -> None:
        """
        Test that Strategy members can be retrieved by their name.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Strategy["FIFO"], Strategy.FIFO)

    def testLookupByValue(self) -> None:
        """
        Test that Strategy members can be retrieved by their string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Strategy("priority"), Strategy.PRIORITY)

    def testUnknownValueRaises(self) -> None:
        """
        Test that an unknown strategy value raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Strategy("random")

    def testMemberCount(self) -> None:
        """
        Test that exactly three Strategy members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(Strategy), 3)

# ===========================================================================
# QueueDatabase entity
# ===========================================================================

class TestQueueDatabaseEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that queue Database can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        d = QueueDatabase()
        self.assertIsInstance(d, QueueDatabase)

    def testDefaultJobsTable(self) -> None:
        """
        Test that the default jobs_table value is 'jobs'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(QueueDatabase().jobs_table, "jobs")

    def testDefaultFailedJobsTable(self) -> None:
        """
        Test that the default failed_jobs_table value is 'failed_jobs'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(QueueDatabase().failed_jobs_table, "failed_jobs")

    def testDefaultStrategyIsNormalized(self) -> None:
        """
        Test that the default strategy is a valid Strategy value string.

        Returns
        -------
        None
            This method does not return a value.
        """
        d = QueueDatabase()
        self.assertIn(d.strategy, [s.value for s in Strategy])

    def testStrategyStringNormalization(self) -> None:
        """
        Test that a strategy string (e.g. 'LIFO') is normalized to its enum value.

        Returns
        -------
        None
            This method does not return a value.
        """
        d = QueueDatabase(strategy="LIFO")
        self.assertEqual(d.strategy, Strategy.LIFO.value)

    def testStrategyEnumNormalization(self) -> None:
        """
        Test that a Strategy enum is stored as its string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        d = QueueDatabase(strategy=Strategy.PRIORITY)
        self.assertEqual(d.strategy, Strategy.PRIORITY.value)

    def testInvalidJobsTableRaisesValueError(self) -> None:
        """
        Test that a jobs_table with digits raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            QueueDatabase(jobs_table="jobs123")

    def testInvalidVisibilityTimeoutRaisesValueError(self) -> None:
        """
        Test that a non-positive visibility_timeout raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            QueueDatabase(visibility_timeout=0)

    def testInvalidRetryDelayRaisesValueError(self) -> None:
        """
        Test that a non-positive retry_delay raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            QueueDatabase(retry_delay=-5)

    def testInvalidMaxAttemptsRaisesValueError(self) -> None:
        """
        Test that a non-positive max_attempts raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            QueueDatabase(max_attempts=0)

    def testInvalidStrategyRaisesValueError(self) -> None:
        """
        Test that an unrecognized strategy string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            QueueDatabase(strategy="RANDOM")

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen queue Database instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        d = QueueDatabase()
        with self.assertRaises(FrozenInstanceError):
            d.jobs_table = "other"  # type: ignore[misc]

# ===========================================================================
# Brokers entity
# ===========================================================================

class TestBrokersEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Brokers can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        b = Brokers()
        self.assertIsInstance(b, Brokers)

    def testDefaultDatabaseIsDatabaseInstance(self) -> None:
        """
        Test that the default database attribute is a QueueDatabase instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Brokers().database, QueueDatabase)

    def testDictConversion(self) -> None:
        """
        Test that a dict for database is converted to a QueueDatabase instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        b = Brokers(database={"jobs_table": "tasks"})
        self.assertIsInstance(b.database, QueueDatabase)

    def testInvalidDatabaseTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for database raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Brokers(database="not_valid")  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Brokers instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        b = Brokers()
        with self.assertRaises(FrozenInstanceError):
            b.database = QueueDatabase()  # type: ignore[misc]

# ===========================================================================
# Queue entity
# ===========================================================================

class TestQueueEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Queue can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        q = Queue()
        self.assertIsInstance(q, Queue)

    def testDefaultIsString(self) -> None:
        """
        Test that the default attribute is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Queue().default, str)

    def testDefaultBrokersIsBrokersInstance(self) -> None:
        """
        Test that the brokers attribute is a Brokers instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Queue().brokers, Brokers)

    def testInvalidDefaultRaisesValueError(self) -> None:
        """
        Test that an unrecognized default broker raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Queue(default="kafka")

    def testDictBrokersConversion(self) -> None:
        """
        Test that a dict for brokers is converted to a Brokers instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        q = Queue(brokers={})
        self.assertIsInstance(q.brokers, Brokers)

    def testInvalidBrokersTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for brokers raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Queue(brokers="invalid")  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Queue instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        q = Queue()
        with self.assertRaises(FrozenInstanceError):
            q.default = "database"  # type: ignore[misc]
