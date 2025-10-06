from orionis.foundation.config.database.entities.pgsql import PGSQL
from orionis.foundation.config.database.enums.pgsql_charsets import PGSQLCharset
from orionis.foundation.config.database.enums.pgsql_mode import PGSQLSSLMode
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigDatabasePgsql(SyncTestCase):

    def testDefaultValues(self):
        """
        Test that a PGSQL instance is initialized with the correct default values.

        This method verifies that all default attributes of the PGSQL class are set as expected upon instantiation.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Create a PGSQL instance with default parameters
        pgsql = PGSQL()

        # Assert default values for each attribute
        self.assertEqual(pgsql.driver, 'pgsql')
        self.assertEqual(pgsql.host, '127.0.0.1')
        self.assertEqual(pgsql.port, 5432)
        self.assertEqual(pgsql.database, 'orionis')
        self.assertEqual(pgsql.username, 'postgres')
        self.assertEqual(pgsql.password, '')
        self.assertEqual(pgsql.charset, PGSQLCharset.UTF8.value)
        self.assertEqual(pgsql.prefix, '')
        self.assertTrue(pgsql.prefix_indexes)
        self.assertEqual(pgsql.search_path, 'public')
        self.assertEqual(pgsql.sslmode, PGSQLSSLMode.PREFER.value)

    def testDriverValidation(self):
        """
        Test validation logic for the 'driver' attribute of PGSQL.

        This method checks that providing an empty string or a non-string value for the driver raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Assert that an empty string for driver raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(driver='')

        # Assert that a non-string value for driver raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(driver=123)

    def testHostValidation(self):
        """
        Test validation logic for the 'host' attribute of PGSQL.

        This method checks that providing an empty string or a non-string value for the host raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Assert that an empty string for host raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(host='')

        # Assert that a non-string value for host raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(host=123)

    def testPortValidation(self):
        """
        Test validation logic for the 'port' attribute of PGSQL.

        This method checks that providing a non-numeric string or a non-string value for the port raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Assert that a non-numeric string for port raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(port='abc')

        # Assert that a string that is not a valid port raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(port='string')

    def testDatabaseValidation(self):
        """
        Test validation logic for the 'database' attribute of PGSQL.

        This method checks that providing an empty string or a non-string value for the database name raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Assert that an empty string for database raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(database='')

        # Assert that a non-string value for database raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(database=123)

    def testUsernameValidation(self):
        """
        Test validation logic for the 'username' attribute of PGSQL.

        This method checks that providing an empty string or a non-string value for the username raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Assert that an empty string for username raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(username='')

        # Assert that a non-string value for username raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(username=123)

    def testPasswordValidation(self):
        """
        Test validation logic for the 'password' attribute of PGSQL.

        This method checks that providing a non-string value for the password raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Assert that a non-string value for password raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(password=123)

    def testCharsetValidation(self):
        """
        Test validation logic for the 'charset' attribute of PGSQL.

        This method ensures that the charset attribute correctly handles string and enum assignments, and raises an exception for invalid values.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Test that a valid string value for charset is converted to the correct enum value
        pgsql = PGSQL(charset='UTF8')
        self.assertEqual(pgsql.charset, PGSQLCharset.UTF8.value)

        # Test that a valid enum value for charset is accepted
        pgsql = PGSQL(charset=PGSQLCharset.LATIN1)
        self.assertEqual(pgsql.charset, PGSQLCharset.LATIN1.value)

        # Test that an invalid value for charset raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(charset='INVALID')

    def testPrefixIndexesValidation(self):
        """
        Test validation logic for the 'prefix_indexes' attribute of PGSQL.

        This method checks that providing a non-boolean value for prefix_indexes raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Assert that a string value for prefix_indexes raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(prefix_indexes='true')

        # Assert that a non-boolean integer value for prefix_indexes raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(prefix_indexes=1)

    def testSearchPathValidation(self):
        """
        Test validation logic for the 'search_path' attribute of PGSQL.

        This method checks that providing an empty string or a non-string value for search_path raises an OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Assert that an empty string for search_path raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(search_path='')

        # Assert that a non-string value for search_path raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(search_path=123)

    def testSSLModeValidation(self):
        """
        Test validation logic for the 'sslmode' attribute of PGSQL.

        This method ensures that the sslmode attribute correctly handles string and enum assignments, and raises an exception for invalid values.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Test that a valid string value for sslmode is converted to the correct enum value
        pgsql = PGSQL(sslmode='REQUIRE')
        self.assertEqual(pgsql.sslmode, PGSQLSSLMode.REQUIRE.value)

        # Test that a valid enum value for sslmode is accepted
        pgsql = PGSQL(sslmode=PGSQLSSLMode.DISABLE)
        self.assertEqual(pgsql.sslmode, PGSQLSSLMode.DISABLE.value)

        # Test that an invalid value for sslmode raises an exception
        with self.assertRaises(OrionisIntegrityException):
            PGSQL(sslmode='INVALID')

    def testToDictMethod(self):
        """
        Test the toDict method of the PGSQL class.

        This method ensures that the dictionary representation of a PGSQL instance contains all expected attributes with correct values.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Create a PGSQL instance with default parameters
        pgsql = PGSQL()

        # Convert the instance to a dictionary
        pgsql_dict = pgsql.toDict()

        # Assert that all expected keys and values are present in the dictionary
        self.assertEqual(pgsql_dict['driver'], 'pgsql')
        self.assertEqual(pgsql_dict['host'], '127.0.0.1')
        self.assertEqual(pgsql_dict['port'], 5432)
        self.assertEqual(pgsql_dict['database'], 'orionis')
        self.assertEqual(pgsql_dict['username'], 'postgres')
        self.assertEqual(pgsql_dict['password'], '')
        self.assertEqual(pgsql_dict['charset'], PGSQLCharset.UTF8.value)
        self.assertEqual(pgsql_dict['prefix'], '')
        self.assertTrue(pgsql_dict['prefix_indexes'])
        self.assertEqual(pgsql_dict['search_path'], 'public')
        self.assertEqual(pgsql_dict['sslmode'], PGSQLSSLMode.PREFER.value)

    def testCustomValues(self):
        """
        Test that custom configuration values are correctly stored and validated in PGSQL.

        This method ensures that when custom values are provided to the PGSQL constructor, they are properly assigned and validated.

        Returns
        -------
        None
            This method does not return a value. Assertions are used for validation.
        """

        # Create a PGSQL instance with custom parameters
        custom_pgsql = PGSQL(
            host='db.example.com',
            port='6432',
            database='custom_db',
            username='admin',
            password='secure123',
            charset='LATIN1',
            prefix='app_',
            prefix_indexes=False,
            search_path='app_schema',
            sslmode='VERIFY_FULL'
        )

        # Assert that all custom values are correctly set
        self.assertEqual(custom_pgsql.host, 'db.example.com')
        self.assertEqual(custom_pgsql.port, '6432')
        self.assertEqual(custom_pgsql.database, 'custom_db')
        self.assertEqual(custom_pgsql.username, 'admin')
        self.assertEqual(custom_pgsql.password, 'secure123')
        self.assertEqual(custom_pgsql.charset, PGSQLCharset.LATIN1.value)
        self.assertEqual(custom_pgsql.prefix, 'app_')
        self.assertFalse(custom_pgsql.prefix_indexes)
        self.assertEqual(custom_pgsql.search_path, 'app_schema')
        self.assertEqual(custom_pgsql.sslmode, PGSQLSSLMode.VERIFY_FULL.value)