from orionis.foundation.config.database.entities.database import Database
from orionis.foundation.config.database.entities.connections import Connections
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigDatabase(SyncTestCase):

    def testDefaultValues(self):
        """
        Verify that a Database instance initializes with the correct default values.

        The method checks that the `default` attribute is set to 'sqlite' and the
        `connections` attribute is an instance of the Connections class.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Database instance with default parameters
        db = Database()

        # Assert that the default connection type is 'sqlite'
        self.assertEqual(db.default, "sqlite")

        # Assert that the connections attribute is an instance of Connections
        self.assertIsInstance(db.connections, Connections)

    def testDefaultConnectionValidation(self):
        """
        Validate the `default` attribute for allowed connection types and error handling.

        This method checks that only valid connection types are accepted for the `default`
        attribute. It verifies that invalid, empty, or non-string values raise
        OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Test valid connection types for the 'default' attribute
        valid_connections = ["sqlite", "mysql", "pgsql", "oracle"]
        for conn in valid_connections:
            try:
                # Should not raise exception for valid connection types
                Database(default=conn)
            except OrionisIntegrityException:
                self.fail(f"Valid connection type '{conn}' should not raise exception")

        # Test invalid connection type
        with self.assertRaises(OrionisIntegrityException):
            # Should raise exception for an invalid connection type
            Database(default="invalid_connection")

        # Test empty default value
        with self.assertRaises(OrionisIntegrityException):
            # Should raise exception for empty string as default
            Database(default="")

        # Test non-string default value
        with self.assertRaises(OrionisIntegrityException):
            # Should raise exception for non-string default value
            Database(default=123)

    def testConnectionsValidation(self):
        """
        Validate the `connections` attribute for correct type and error handling.

        This method ensures that only instances of Connections are accepted for the
        `connections` attribute. It verifies that invalid types or None raise
        OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Test invalid type for connections attribute
        with self.assertRaises(OrionisIntegrityException):
            # Should raise exception for non-Connections type
            Database(connections="not_a_connections_instance")

        # Test None as connections attribute
        with self.assertRaises(OrionisIntegrityException):
            # Should raise exception for None as connections
            Database(connections=None)

        # Test valid Connections instance
        try:
            # Should not raise exception for valid Connections instance
            Database(connections=Connections())
        except OrionisIntegrityException:
            self.fail("Valid Connections instance should not raise exception")

    def testToDictMethod(self):
        """
        Test the `toDict` method for correct dictionary representation of Database.

        This method ensures that the `toDict` method returns a dictionary containing
        all attributes of the Database instance, including `default` and `connections`.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a Database instance
        db = Database()

        # Convert the Database instance to a dictionary
        db_dict = db.toDict()

        # Assert that the result is a dictionary
        self.assertIsInstance(db_dict, dict)

        # Assert that the 'default' key is 'sqlite'
        self.assertEqual(db_dict["default"], "sqlite")

        # Assert that the 'connections' key is a dictionary
        self.assertIsInstance(db_dict["connections"], dict)

    def testCustomValues(self):
        """
        Test correct handling and validation of custom attribute values in Database.

        This method ensures that custom values for `default` and `connections` are
        correctly stored and validated in the Database instance.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create a custom Connections instance
        custom_connections = Connections()

        # Create a Database instance with custom values
        custom_db = Database(
            default="mysql",
            connections=custom_connections,
        )

        # Assert that the custom default value is set
        self.assertEqual(custom_db.default, "mysql")

        # Assert that the custom connections instance is set
        self.assertIs(custom_db.connections, custom_connections)

    def testHashability(self):
        """
        Test that Database instances are hashable and behave correctly in sets.

        This method verifies that Database instances can be used in sets and as dictionary
        keys, and that identical instances are considered equal.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Create two identical Database instances
        db1 = Database()
        db2 = Database()

        # Add both to a set; should only contain one unique instance
        db_set = {db1, db2}
        self.assertEqual(len(db_set), 1)

        # Add a custom Database instance with a different default value
        custom_db = Database(default="pgsql")
        db_set.add(custom_db)

        # Now the set should contain two unique instances
        self.assertEqual(len(db_set), 2)

    def testKwOnlyInitialization(self):
        """
        Test enforcement of keyword-only initialization for Database.

        This method ensures that Database raises TypeError when positional arguments are
        used instead of keyword arguments during initialization.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """
        # Attempt to initialize Database with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Database("sqlite", Connections())
