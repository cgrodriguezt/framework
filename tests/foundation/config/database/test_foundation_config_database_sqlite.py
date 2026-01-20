from orionis.foundation.config.database.entities.sqlite import SQLite
from orionis.foundation.config.database.enums.sqlite_foreign_key import SQLiteForeignKey
from orionis.foundation.config.database.enums.sqlite_journal import SQLiteJournalMode
from orionis.foundation.config.database.enums.sqlite_synchronous import SQLiteSynchronous
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigDatabaseSqlite(SyncTestCase):

    def testDefaultValues(self):
        """
        Verify that a SQLite instance is initialized with the correct default values.

        This test checks that all attributes of the SQLite class are set to their expected default values upon instantiation.

        Returns
        -------
        None
            This method does not return a value. It asserts correctness of default attribute values.
        """
        # Create a default SQLite instance
        sqlite = SQLite()

        # Assert default driver is 'sqlite'
        self.assertEqual(sqlite.driver, "sqlite")

        # Assert default URL starts with 'sqlite:///'
        self.assertTrue(sqlite.url.startswith("sqlite:///"))

        # Assert default database name
        self.assertEqual(sqlite.database, "database.sqlite")

        # Assert default prefix is empty
        self.assertEqual(sqlite.prefix, "")

        # Assert default foreign key constraints setting
        self.assertEqual(sqlite.foreign_key_constraints, SQLiteForeignKey.OFF.value)

        # Assert default busy timeout
        self.assertEqual(sqlite.busy_timeout, 5000)

        # Assert default journal mode
        self.assertEqual(sqlite.journal_mode, SQLiteJournalMode.DELETE.value)

        # Assert default synchronous mode
        self.assertEqual(sqlite.synchronous, SQLiteSynchronous.NORMAL.value)

    def testDriverValidation(self):
        """
        Test validation of the 'driver' attribute in SQLite.

        Ensures that providing an empty string or a non-string value for the driver raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts that exceptions are raised for invalid driver values.
        """
        # Assert that an empty string for driver raises an exception
        with self.assertRaises(OrionisIntegrityException):
            SQLite(driver="")

        # Assert that a non-string driver raises an exception
        with self.assertRaises(OrionisIntegrityException):
            SQLite(driver=123)

    def testUrlValidation(self):
        """
        Test validation of the 'url' attribute in SQLite.

        Ensures that providing an empty string or a non-string value for the URL raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts that exceptions are raised for invalid URL values.
        """
        # Assert that an empty string for url raises an exception
        with self.assertRaises(OrionisIntegrityException):
            SQLite(url="")

        # Assert that a non-string url raises an exception
        with self.assertRaises(OrionisIntegrityException):
            SQLite(url=123)

    def testDatabaseValidation(self):
        """
        Test validation of the 'database' attribute in SQLite.

        Ensures that providing an empty string or a non-string value for the database path raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts that exceptions are raised for invalid database values.
        """
        # Assert that an empty string for database raises an exception
        with self.assertRaises(OrionisIntegrityException):
            SQLite(database="")

        # Assert that a non-string database raises an exception
        with self.assertRaises(OrionisIntegrityException):
            SQLite(database=123)

    def testForeignKeyConstraintsValidation(self):
        """
        Test validation and conversion of the 'foreign_key_constraints' attribute.

        Ensures that string and enum values are correctly converted, and invalid values raise an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts correct conversion and exception raising for invalid values.
        """
        # Test string conversion to enum value
        sqlite = SQLite(foreign_key_constraints="ON")
        self.assertEqual(sqlite.foreign_key_constraints, SQLiteForeignKey.ON.value)

        # Test direct enum assignment
        sqlite = SQLite(foreign_key_constraints=SQLiteForeignKey.OFF)
        self.assertEqual(sqlite.foreign_key_constraints, SQLiteForeignKey.OFF.value)

        # Assert that an invalid value raises an exception
        with self.assertRaises(OrionisIntegrityException):
            SQLite(foreign_key_constraints="INVALID")

    def testBusyTimeoutValidation(self):
        """
        Test validation of the 'busy_timeout' attribute in SQLite.

        Ensures that only non-negative integers are accepted for busy_timeout, and invalid values raise an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts that exceptions are raised for invalid busy_timeout values.
        """
        # Assert that a negative busy_timeout raises an exception
        with self.assertRaises(OrionisIntegrityException):
            SQLite(busy_timeout=-1)

        # Assert that a non-integer busy_timeout raises an exception
        with self.assertRaises(OrionisIntegrityException):
            SQLite(busy_timeout="invalid")

    def testJournalModeValidation(self):
        """
        Test validation and conversion of the 'journal_mode' attribute.

        Ensures that string and enum values are correctly converted, and invalid values raise an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts correct conversion and exception raising for invalid values.
        """
        # Test string conversion to enum value
        sqlite = SQLite(journal_mode="WAL")
        self.assertEqual(sqlite.journal_mode, SQLiteJournalMode.WAL.value)

        # Test direct enum assignment
        sqlite = SQLite(journal_mode=SQLiteJournalMode.TRUNCATE)
        self.assertEqual(sqlite.journal_mode, SQLiteJournalMode.TRUNCATE.value)

        # Assert that an invalid value raises an exception
        with self.assertRaises(OrionisIntegrityException):
            SQLite(journal_mode="INVALID")

    def testSynchronousValidation(self):
        """
        Test validation and conversion of the 'synchronous' attribute.

        Ensures that string and enum values are correctly converted, and invalid values raise an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts correct conversion and exception raising for invalid values.
        """
        # Test string conversion to enum value
        sqlite = SQLite(synchronous="FULL")
        self.assertEqual(sqlite.synchronous, SQLiteSynchronous.FULL.value)

        # Test direct enum assignment
        sqlite = SQLite(synchronous=SQLiteSynchronous.OFF)
        self.assertEqual(sqlite.synchronous, SQLiteSynchronous.OFF.value)

        # Assert that an invalid value raises an exception
        with self.assertRaises(OrionisIntegrityException):
            SQLite(synchronous="INVALID")

    def testToDictMethod(self):
        """
        Test the toDict method for correct dictionary representation.

        Ensures that all attributes of the SQLite instance are accurately reflected in the dictionary returned by toDict().

        Returns
        -------
        None
            This method does not return a value. It asserts correctness of the dictionary representation.
        """
        # Create a default SQLite instance
        sqlite = SQLite()

        # Convert the instance to a dictionary
        sqlite_dict = sqlite.toDict()

        # Assert all dictionary values match the instance's attributes
        self.assertEqual(sqlite_dict["driver"], "sqlite")
        self.assertTrue(sqlite_dict["url"].startswith("sqlite:///"))
        self.assertEqual(sqlite_dict["database"], "database.sqlite")
        self.assertEqual(sqlite_dict["prefix"], "")
        self.assertEqual(sqlite_dict["foreign_key_constraints"], SQLiteForeignKey.OFF.value)
        self.assertEqual(sqlite_dict["busy_timeout"], 5000)
        self.assertEqual(sqlite_dict["journal_mode"], SQLiteJournalMode.DELETE.value)
        self.assertEqual(sqlite_dict["synchronous"], SQLiteSynchronous.NORMAL.value)

    def testCustomValues(self):
        """
        Test that custom configuration values are correctly stored and validated in SQLite.

        Ensures that user-supplied values for all configurable attributes are properly set and validated.

        Returns
        -------
        None
            This method does not return a value. It asserts correctness of custom attribute assignment and validation.
        """
        # Create a SQLite instance with custom values
        custom_sqlite = SQLite(
            database="custom.db",
            prefix="app_",
            foreign_key_constraints="ON",
            busy_timeout=10000,
            journal_mode="MEMORY",
            synchronous="OFF",
        )

        # Assert all custom values are set correctly
        self.assertEqual(custom_sqlite.database, "custom.db")
        self.assertEqual(custom_sqlite.prefix, "app_")
        self.assertEqual(custom_sqlite.foreign_key_constraints, SQLiteForeignKey.ON.value)
        self.assertEqual(custom_sqlite.busy_timeout, 10000)
        self.assertEqual(custom_sqlite.journal_mode, SQLiteJournalMode.MEMORY.value)
        self.assertEqual(custom_sqlite.synchronous, SQLiteSynchronous.OFF.value)
