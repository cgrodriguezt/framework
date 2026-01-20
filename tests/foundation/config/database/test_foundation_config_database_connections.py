from orionis.foundation.config.database.entities.connections import Connections
from orionis.foundation.config.database.entities.mysql import MySQL
from orionis.foundation.config.database.entities.oracle import Oracle
from orionis.foundation.config.database.entities.pgsql import PGSQL
from orionis.foundation.config.database.entities.sqlite import SQLite
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigDatabaseConnections(SyncTestCase):

    def testDefaultValues(self):
        """
        Test that a Connections instance is created with the correct default values.

        Ensures that all default connection attributes are properly initialized with their respective types.

        Returns
        -------
        None
            This test does not return a value. It asserts the types of the default connection attributes.
        """
        # Create a Connections instance with default configuration
        connections = Connections()

        # Check that each connection attribute is initialized with the correct type
        self.assertIsInstance(connections.sqlite, SQLite)
        self.assertIsInstance(connections.mysql, MySQL)
        self.assertIsInstance(connections.pgsql, PGSQL)
        self.assertIsInstance(connections.oracle, Oracle)

    def testSqliteTypeValidation(self):
        """
        Test type validation for the sqlite attribute.

        Ensures that only instances of SQLite are accepted for the sqlite attribute. Raises OrionisIntegrityException for invalid types.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid types.

        Raises
        ------
        OrionisIntegrityException
            If the sqlite attribute is not a valid SQLite instance.
        """
        # Attempt to assign invalid types to sqlite and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            Connections(sqlite="not_a_sqlite_instance")
        with self.assertRaises(OrionisIntegrityException):
            Connections(sqlite=123)
        with self.assertRaises(OrionisIntegrityException):
            Connections(sqlite=None)

    def testMysqlTypeValidation(self):
        """
        Test type validation for the mysql attribute.

        Ensures that only instances of MySQL are accepted for the mysql attribute. Raises OrionisIntegrityException for invalid types.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid types.

        Raises
        ------
        OrionisIntegrityException
            If the mysql attribute is not a valid MySQL instance.
        """
        # Attempt to assign invalid types to mysql and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            Connections(mysql="not_a_mysql_instance")
        with self.assertRaises(OrionisIntegrityException):
            Connections(mysql=123)
        with self.assertRaises(OrionisIntegrityException):
            Connections(mysql=None)

    def testPgsqlTypeValidation(self):
        """
        Test type validation for the pgsql attribute.

        Ensures that only instances of PGSQL are accepted for the pgsql attribute. Raises OrionisIntegrityException for invalid types.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid types.

        Raises
        ------
        OrionisIntegrityException
            If the pgsql attribute is not a valid PGSQL instance.
        """
        # Attempt to assign invalid types to pgsql and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            Connections(pgsql="not_a_pgsql_instance")
        with self.assertRaises(OrionisIntegrityException):
            Connections(pgsql=123)
        with self.assertRaises(OrionisIntegrityException):
            Connections(pgsql=None)

    def testOracleTypeValidation(self):
        """
        Test type validation for the oracle attribute.

        Ensures that only instances of Oracle are accepted for the oracle attribute. Raises OrionisIntegrityException for invalid types.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid types.

        Raises
        ------
        OrionisIntegrityException
            If the oracle attribute is not a valid Oracle instance.
        """
        # Attempt to assign invalid types to oracle and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            Connections(oracle="not_an_oracle_instance")
        with self.assertRaises(OrionisIntegrityException):
            Connections(oracle=123)
        with self.assertRaises(OrionisIntegrityException):
            Connections(oracle=None)

    def testToDictMethod(self):
        """
        Test that the toDict method returns a proper dictionary representation.

        Ensures that all connection attributes are correctly included in the returned dictionary and that their values are dictionaries.

        Returns
        -------
        None
            This test does not return a value. It asserts the structure and types of the dictionary returned by toDict().
        """
        # Create a Connections instance with default configuration
        connections = Connections()
        connections_dict = connections.toDict()

        # Check that the result is a dictionary
        self.assertIsInstance(connections_dict, dict)

        # Check that each connection entry in the dictionary is itself a dictionary
        self.assertIsInstance(connections_dict["sqlite"], dict)
        self.assertIsInstance(connections_dict["mysql"], dict)
        self.assertIsInstance(connections_dict["pgsql"], dict)
        self.assertIsInstance(connections_dict["oracle"], dict)

    def testCustomConnections(self):
        """
        Test that custom connection instances are properly stored and validated.

        Ensures that custom connection configurations are correctly assigned and their attributes are set as expected.

        Returns
        -------
        None
            This test does not return a value. It asserts the values of custom connection attributes.
        """
        # Create custom connection instances
        custom_sqlite = SQLite(database="custom.db")
        custom_mysql = MySQL(database="custom_db")
        custom_pgsql = PGSQL(database="custom_db")
        custom_oracle = Oracle(service_name="CUSTOM_SID")

        # Assign custom connections to the Connections object
        connections = Connections(
            sqlite=custom_sqlite,
            mysql=custom_mysql,
            pgsql=custom_pgsql,
            oracle=custom_oracle,
        )

        # Assert that the custom attributes are set correctly
        self.assertEqual(connections.sqlite.database, "custom.db")
        self.assertEqual(connections.mysql.database, "custom_db")
        self.assertEqual(connections.pgsql.database, "custom_db")
        self.assertEqual(connections.oracle.service_name, "CUSTOM_SID")

    def testHashability(self):
        """
        Test that Connections instances are hashable due to unsafe_hash=True.

        Ensures that Connections objects can be used in sets and as dictionary keys, and that identical objects are considered equal.

        Returns
        -------
        None
            This test does not return a value. It asserts the hashability and equality of Connections instances.
        """
        # Create two identical Connections instances
        conn1 = Connections()
        conn2 = Connections()

        # Add both to a set; only one should be present due to equality
        conn_set = {conn1, conn2}

        # Assert that only one unique instance exists in the set
        self.assertEqual(len(conn_set), 1)

        # Add a custom Connections instance; set should now have two distinct items
        custom_conn = Connections(sqlite=SQLite(database="custom.db"))
        conn_set.add(custom_conn)
        self.assertEqual(len(conn_set), 2)

    def testKwOnlyInitialization(self):
        """
        Test that Connections enforces keyword-only initialization.

        Ensures that positional arguments are not allowed when initializing a Connections instance. Raises TypeError if positional arguments are used.

        Returns
        -------
        None
            This test does not return a value. It asserts that a TypeError is raised for positional arguments.

        Raises
        ------
        TypeError
            If positional arguments are used for initialization.
        """
        # Attempt to initialize Connections with positional arguments and expect a TypeError
        with self.assertRaises(TypeError):
            Connections(SQLite(), MySQL(), PGSQL(), Oracle())
