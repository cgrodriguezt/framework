from orionis.foundation.config.database.entities.mysql import MySQL
from orionis.foundation.config.database.enums.mysql_charsets import MySQLCharset
from orionis.foundation.config.database.enums.mysql_collations import MySQLCollation
from orionis.foundation.config.database.enums.mysql_engine import MySQLEngine
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigDatabaseMysql(SyncTestCase):

    def testDefaultValues(self):
        """
        Test that a MySQL instance is created with the correct default values.

        Ensures all default values match the expected defaults from the class definition.

        Returns
        -------
        None
            This test does not return a value. It asserts the default values of the MySQL instance attributes.
        """

        # Create a MySQL instance with default configuration
        mysql = MySQL()

        # Assert each default attribute value
        self.assertEqual(mysql.driver, 'mysql')
        self.assertEqual(mysql.host, '127.0.0.1')
        self.assertEqual(mysql.port, 3306)
        self.assertEqual(mysql.database, 'orionis')
        self.assertEqual(mysql.username, 'root')
        self.assertEqual(mysql.password, '')
        self.assertEqual(mysql.unix_socket, '')
        self.assertEqual(mysql.charset, MySQLCharset.UTF8MB4.value)
        self.assertEqual(mysql.collation, MySQLCollation.UTF8MB4_UNICODE_CI.value)
        self.assertEqual(mysql.prefix, '')
        self.assertTrue(mysql.prefix_indexes)
        self.assertTrue(mysql.strict)
        self.assertEqual(mysql.engine, MySQLEngine.INNODB.value)

    def testDriverValidation(self):
        """
        Test validation for the driver attribute.

        Ensures that only the value 'mysql' is accepted for the driver attribute. Raises OrionisIntegrityException for invalid values.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid driver values.

        Raises
        ------
        OrionisIntegrityException
            If the driver value is invalid.
        """

        # Attempt to assign invalid values to driver and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            MySQL(driver='')
        with self.assertRaises(OrionisIntegrityException):
            MySQL(driver='postgres')
        with self.assertRaises(OrionisIntegrityException):
            MySQL(driver=123)

    def testHostValidation(self):
        """
        Test validation for the host attribute.

        Ensures that empty or non-string host values raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid host values.

        Raises
        ------
        OrionisIntegrityException
            If the host value is invalid.
        """

        # Attempt to assign invalid values to host and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            MySQL(host='')
        with self.assertRaises(OrionisIntegrityException):
            MySQL(host=123)

    def testPortValidation(self):
        """
        Test validation for the port attribute.

        Ensures that invalid port numbers or types raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid port values.

        Raises
        ------
        OrionisIntegrityException
            If the port value is invalid.
        """

        # Attempt to assign invalid values to port and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            MySQL(port=0)
        with self.assertRaises(OrionisIntegrityException):
            MySQL(port=65536)
        with self.assertRaises(OrionisIntegrityException):
            MySQL(port='3306')

    def testDatabaseValidation(self):
        """
        Test validation for the database attribute.

        Ensures that empty or non-string database names raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid database values.

        Raises
        ------
        OrionisIntegrityException
            If the database value is invalid.
        """

        # Attempt to assign invalid values to database and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            MySQL(database='')
        with self.assertRaises(OrionisIntegrityException):
            MySQL(database=123)

    def testUsernameValidation(self):
        """
        Test validation for the username attribute.

        Ensures that empty or non-string usernames raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid username values.

        Raises
        ------
        OrionisIntegrityException
            If the username value is invalid.
        """

        # Attempt to assign invalid values to username and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            MySQL(username='')
        with self.assertRaises(OrionisIntegrityException):
            MySQL(username=123)

    def testPasswordValidation(self):
        """
        Test validation for the password attribute.

        Ensures that non-string passwords raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid password values.

        Raises
        ------
        OrionisIntegrityException
            If the password value is invalid.
        """

        # Attempt to assign an invalid value to password and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            MySQL(password=123)

    def testUnixSocketValidation(self):
        """
        Test validation for the unix_socket attribute.

        Ensures that non-string socket paths raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid unix_socket values.

        Raises
        ------
        OrionisIntegrityException
            If the unix_socket value is invalid.
        """

        # Attempt to assign an invalid value to unix_socket and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            MySQL(unix_socket=123)

    def testCharsetValidation(self):
        """
        Test validation for the charset attribute.

        Ensures correct enum conversion and invalid value handling for charset.

        Returns
        -------
        None
            This test does not return a value. It asserts correct conversion and exception handling for charset values.

        Raises
        ------
        OrionisIntegrityException
            If the charset value is invalid.
        """

        # Test string conversion to enum value
        mysql = MySQL(charset='UTF8')
        self.assertEqual(mysql.charset, MySQLCharset.UTF8.value)

        # Test enum assignment
        mysql = MySQL(charset=MySQLCharset.LATIN1)
        self.assertEqual(mysql.charset, MySQLCharset.LATIN1.value)

        # Attempt to assign an invalid value to charset and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            MySQL(charset='INVALID')

    def testCollationValidation(self):
        """
        Test validation for the collation attribute.

        Ensures correct enum conversion and invalid value handling for collation.

        Returns
        -------
        None
            This test does not return a value. It asserts correct conversion and exception handling for collation values.

        Raises
        ------
        OrionisIntegrityException
            If the collation value is invalid.
        """

        # Test string conversion to enum value
        mysql = MySQL(collation='UTF8_GENERAL_CI')
        self.assertEqual(mysql.collation, MySQLCollation.UTF8_GENERAL_CI.value)

        # Test enum assignment
        mysql = MySQL(collation=MySQLCollation.UTF8MB4_BIN)
        self.assertEqual(mysql.collation, MySQLCollation.UTF8MB4_BIN.value)

        # Attempt to assign an invalid value to collation and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            MySQL(collation='INVALID')

    def testPrefixValidation(self):
        """
        Test validation for the prefix attribute.

        Ensures that non-string prefixes raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid prefix values.

        Raises
        ------
        OrionisIntegrityException
            If the prefix value is invalid.
        """

        # Attempt to assign an invalid value to prefix and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            MySQL(prefix=123)

    def testPrefixIndexesValidation(self):
        """
        Test validation for the prefix_indexes attribute.

        Ensures that non-boolean values raise exceptions for prefix_indexes.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid prefix_indexes values.

        Raises
        ------
        OrionisIntegrityException
            If the prefix_indexes value is invalid.
        """

        # Attempt to assign invalid values to prefix_indexes and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            MySQL(prefix_indexes='true')
        with self.assertRaises(OrionisIntegrityException):
            MySQL(prefix_indexes=1)

    def testStrictValidation(self):
        """
        Test validation for the strict attribute.

        Ensures that non-boolean values raise exceptions for strict.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid strict values.

        Raises
        ------
        OrionisIntegrityException
            If the strict value is invalid.
        """

        # Attempt to assign invalid values to strict and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            MySQL(strict='true')
        with self.assertRaises(OrionisIntegrityException):
            MySQL(strict=1)

    def testEngineValidation(self):
        """
        Test validation for the engine attribute.

        Ensures correct enum conversion and invalid value handling for engine.

        Returns
        -------
        None
            This test does not return a value. It asserts correct conversion and exception handling for engine values.

        Raises
        ------
        OrionisIntegrityException
            If the engine value is invalid.
        """

        # Test string conversion to enum value
        mysql = MySQL(engine='MYISAM')
        self.assertEqual(mysql.engine, MySQLEngine.MYISAM.value)

        # Test enum assignment
        mysql = MySQL(engine=MySQLEngine.MEMORY)
        self.assertEqual(mysql.engine, MySQLEngine.MEMORY.value)

        # Attempt to assign an invalid value to engine and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            MySQL(engine='INVALID')

    def testToDictMethod(self):
        """
        Test that the toDict method returns a proper dictionary representation.

        Ensures all attributes are correctly included in the returned dictionary and their values match the expected defaults.

        Returns
        -------
        None
            This test does not return a value. It asserts the structure and values of the dictionary returned by toDict().
        """

        # Create a MySQL instance with default configuration
        mysql = MySQL()
        mysql_dict = mysql.toDict()

        # Assert each attribute in the dictionary matches the expected default value
        self.assertEqual(mysql_dict['driver'], 'mysql')
        self.assertEqual(mysql_dict['host'], '127.0.0.1')
        self.assertEqual(mysql_dict['port'], 3306)
        self.assertEqual(mysql_dict['database'], 'orionis')
        self.assertEqual(mysql_dict['username'], 'root')
        self.assertEqual(mysql_dict['password'], '')
        self.assertEqual(mysql_dict['unix_socket'], '')
        self.assertEqual(mysql_dict['charset'], MySQLCharset.UTF8MB4.value)
        self.assertEqual(mysql_dict['collation'], MySQLCollation.UTF8MB4_UNICODE_CI.value)
        self.assertEqual(mysql_dict['prefix'], '')
        self.assertTrue(mysql_dict['prefix_indexes'])
        self.assertTrue(mysql_dict['strict'])
        self.assertEqual(mysql_dict['engine'], MySQLEngine.INNODB.value)

    def testCustomValues(self):
        """
        Test that custom values are properly stored and validated.

        Ensures custom configuration values are correctly assigned and validated in the MySQL instance.

        Returns
        -------
        None
            This test does not return a value. It asserts the values of custom attributes in the MySQL instance.
        """

        # Create a MySQL instance with custom configuration values
        custom_mysql = MySQL(
            host='db.example.com',
            port=3307,
            database='custom_db',
            username='admin',
            password='secure123',
            unix_socket='/var/run/mysqld/mysqld.sock',
            charset='LATIN1',
            collation='LATIN1_GENERAL_CI',
            prefix='app_',
            prefix_indexes=False,
            strict=False,
            engine='MEMORY'
        )

        # Assert that each custom attribute is set correctly
        self.assertEqual(custom_mysql.host, 'db.example.com')
        self.assertEqual(custom_mysql.port, 3307)
        self.assertEqual(custom_mysql.database, 'custom_db')
        self.assertEqual(custom_mysql.username, 'admin')
        self.assertEqual(custom_mysql.password, 'secure123')
        self.assertEqual(custom_mysql.unix_socket, '/var/run/mysqld/mysqld.sock')
        self.assertEqual(custom_mysql.charset, MySQLCharset.LATIN1.value)
        self.assertEqual(custom_mysql.collation, MySQLCollation.LATIN1_GENERAL_CI.value)
        self.assertEqual(custom_mysql.prefix, 'app_')
        self.assertFalse(custom_mysql.prefix_indexes)
        self.assertFalse(custom_mysql.strict)
        self.assertEqual(custom_mysql.engine, MySQLEngine.MEMORY.value)