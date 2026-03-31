from orionis.test import TestCase
from orionis.foundation.config.database.entities.connections import Connections
from orionis.foundation.config.database.entities.database import Database
from orionis.foundation.config.database.entities.mysql import MySQL
from orionis.foundation.config.database.entities.sqlite import SQLite
from orionis.foundation.config.database.enums.mysql_engine import MySQLEngine
from orionis.foundation.config.database.enums.sqlite_foreign_key import SQLiteForeignKey
from orionis.foundation.config.database.enums.sqlite_journal import SQLiteJournalMode
from orionis.foundation.config.database.enums.sqlite_synchronous import SQLiteSynchronous

# ===========================================================================
# MySQLEngine enum
# ===========================================================================

class TestMySQLEngineEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that all expected MySQLEngine members are present.

        Returns
        -------
        None
            This method does not return a value.
        """
        for name in ("INNODB", "MYISAM", "MEMORY", "NDB"):
            self.assertIn(name, MySQLEngine._member_names_)

    def testInnoDbValue(self) -> None:
        """
        Test that INNODB member has the correct string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(MySQLEngine.INNODB.value, "InnoDB")

    def testLookupByName(self) -> None:
        """
        Test that MySQLEngine members can be retrieved by name.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(MySQLEngine["MEMORY"], MySQLEngine.MEMORY)

    def testLookupByValue(self) -> None:
        """
        Test that MySQLEngine members can be retrieved by their value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(MySQLEngine("MyISAM"), MySQLEngine.MYISAM)

    def testUnknownValueRaises(self) -> None:
        """
        Test that an unknown value raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            MySQLEngine("ROCKSDB")

    def testMemberCount(self) -> None:
        """
        Test that exactly four MySQLEngine members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(MySQLEngine), 4)

# ===========================================================================
# SQLiteForeignKey enum
# ===========================================================================

class TestSQLiteForeignKeyEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that ON and OFF members exist in SQLiteForeignKey.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("ON", SQLiteForeignKey._member_names_)
        self.assertIn("OFF", SQLiteForeignKey._member_names_)

    def testMemberValues(self) -> None:
        """
        Test the string values for SQLiteForeignKey members.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(SQLiteForeignKey.ON.value, "ON")
        self.assertEqual(SQLiteForeignKey.OFF.value, "OFF")

    def testMemberCount(self) -> None:
        """
        Test that exactly two SQLiteForeignKey members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(SQLiteForeignKey), 2)

# ===========================================================================
# SQLiteJournalMode enum
# ===========================================================================

class TestSQLiteJournalModeEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that all expected SQLiteJournalMode members are present.

        Returns
        -------
        None
            This method does not return a value.
        """
        for name in ("DELETE", "TRUNCATE", "PERSIST", "MEMORY", "WAL", "OFF"):
            self.assertIn(name, SQLiteJournalMode._member_names_)

    def testWalValue(self) -> None:
        """
        Test that WAL has the correct string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(SQLiteJournalMode.WAL.value, "WAL")

    def testMemberCount(self) -> None:
        """
        Test that exactly six SQLiteJournalMode members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(SQLiteJournalMode), 6)

# ===========================================================================
# SQLiteSynchronous enum
# ===========================================================================

class TestSQLiteSynchronousEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that FULL, NORMAL and OFF members exist in SQLiteSynchronous.

        Returns
        -------
        None
            This method does not return a value.
        """
        for name in ("FULL", "NORMAL", "OFF"):
            self.assertIn(name, SQLiteSynchronous._member_names_)

    def testMemberValues(self) -> None:
        """
        Test the string values for SQLiteSynchronous members.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(SQLiteSynchronous.FULL.value, "FULL")
        self.assertEqual(SQLiteSynchronous.NORMAL.value, "NORMAL")
        self.assertEqual(SQLiteSynchronous.OFF.value, "OFF")

    def testMemberCount(self) -> None:
        """
        Test that exactly three SQLiteSynchronous members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(SQLiteSynchronous), 3)

# ===========================================================================
# SQLite entity
# ===========================================================================

class TestSQLiteEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that SQLite can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = SQLite()
        self.assertIsInstance(s, SQLite)

    def testDefaultDriver(self) -> None:
        """
        Test that the driver defaults to 'sqlite'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(SQLite().driver, "sqlite")

    def testDefaultForeignKeyIsNormalized(self) -> None:
        """
        Test that the default foreign_key_constraints is a valid SQLiteForeignKey value.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = SQLite()
        self.assertIn(s.foreign_key_constraints, [e.value for e in SQLiteForeignKey])

    def testDefaultJournalModeIsNormalized(self) -> None:
        """
        Test that the default journal_mode is a valid SQLiteJournalMode value.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = SQLite()
        self.assertIn(s.journal_mode, [e.value for e in SQLiteJournalMode])

    def testDefaultSynchronousIsNormalized(self) -> None:
        """
        Test that the default synchronous is a valid SQLiteSynchronous value.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = SQLite()
        self.assertIn(s.synchronous, [e.value for e in SQLiteSynchronous])

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen SQLite instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            s = SQLite()
            s.driver = "other"  # type: ignore[misc]

# ===========================================================================
# MySQL entity
# ===========================================================================

class TestMySQLEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that MySQL can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        m = MySQL()
        self.assertIsInstance(m, MySQL)

    def testDefaultDriver(self) -> None:
        """
        Test that the driver defaults to 'mysql'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(MySQL().driver, "mysql")

    def testDefaultPortIsInt(self) -> None:
        """
        Test that the default port is an integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(MySQL().port, int)

    def testDefaultEngineIsNormalized(self) -> None:
        """
        Test that the engine attribute is normalized to a valid MySQLEngine value.

        Returns
        -------
        None
            This method does not return a value.
        """
        m = MySQL()
        self.assertIn(m.engine, [e.value for e in MySQLEngine])

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen MySQL instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            m = MySQL()
            m.driver = "other"  # type: ignore[misc]

# ===========================================================================
# Connections entity
# ===========================================================================

class TestConnectionsEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Connections can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Connections()
        self.assertIsInstance(c, Connections)

    def testDefaultSQLiteInstance(self) -> None:
        """
        Test that the default sqlite attribute is an SQLite instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Connections().sqlite, SQLite)

    def testDefaultMySQLInstance(self) -> None:
        """
        Test that the default mysql attribute is a MySQL instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Connections().mysql, MySQL)

    def testDictConversionSQLite(self) -> None:
        """
        Test that a dict for sqlite is converted to a SQLite instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        c = Connections(sqlite={"driver": "sqlite"})
        self.assertIsInstance(c.sqlite, SQLite)

    def testInvalidTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for sqlite raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Connections(sqlite="not_a_dict_or_sqlite")  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Connections instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            c = Connections()
            c.sqlite = SQLite()  # type: ignore[misc]

# ===========================================================================
# Database entity
# ===========================================================================

class TestDatabaseEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Database can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        db = Database()
        self.assertIsInstance(db, Database)

    def testDefaultIsString(self) -> None:
        """
        Test that the default attribute is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Database().default, str)

    def testDefaultConnectionsIsConnectionsInstance(self) -> None:
        """
        Test that the connections attribute is a Connections instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Database().connections, Connections)

    def testCustomDefault(self) -> None:
        """
        Test that a valid custom default connection name is accepted.

        Returns
        -------
        None
            This method does not return a value.
        """
        db = Database(default="mysql")
        self.assertEqual(db.default, "mysql")

    def testInvalidDefaultRaisesValueError(self) -> None:
        """
        Test that an unrecognized default connection raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Database(default="fakedb")

    def testInvalidDefaultTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string default raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Database(default=42)  # type: ignore[arg-type]

    def testDictConnectionsConversion(self) -> None:
        """
        Test that a non-empty dict for connections is converted to a Connections instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        db = Database(connections={"sqlite": {}})
        self.assertIsInstance(db.connections, Connections)

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Database instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            db = Database()
            db.default = "mysql"  # type: ignore[misc]
