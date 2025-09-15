from orionis.foundation.config.database.entities.oracle import Oracle
from orionis.foundation.config.database.enums.oracle_encoding import OracleEncoding
from orionis.foundation.config.database.enums.oracle_nencoding import OracleNencoding
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigDatabaseOracle(AsyncTestCase):

    async def testDefaultValues(self):
        """
        Test Oracle instance creation with default values.

        Ensures that all default attribute values match the expected defaults as defined in the class.

        Returns
        -------
        None
            This test does not return a value. It asserts the default values of the Oracle instance attributes.

        Raises
        ------
        AssertionError
            If any default value does not match the expected value.
        """

        # Create an Oracle instance with default configuration
        oracle = Oracle()

        # Assert each default attribute value
        self.assertEqual(oracle.driver, 'oracle')
        self.assertEqual(oracle.username, 'sys')
        self.assertEqual(oracle.password, '')
        self.assertEqual(oracle.host, 'localhost')
        self.assertEqual(oracle.port, 1521)
        self.assertEqual(oracle.service_name, 'ORCL')
        self.assertIsNone(oracle.sid)
        self.assertIsNone(oracle.dsn)
        self.assertIsNone(oracle.tns_name)
        self.assertEqual(oracle.encoding, OracleEncoding.AL32UTF8.value)
        self.assertEqual(oracle.nencoding, OracleNencoding.AL32UTF8.value)

    async def testDriverValidation(self):
        """
        Test validation for the `driver` attribute.

        Ensures that only the value 'oracle' is accepted for the driver attribute. Raises OrionisIntegrityException for invalid values.

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
            Oracle(driver='')
        with self.assertRaises(OrionisIntegrityException):
            Oracle(driver='postgres')
        with self.assertRaises(OrionisIntegrityException):
            Oracle(driver=123)

    async def testUsernameValidation(self):
        """
        Test validation for the `username` attribute.

        Ensures that empty or non-string usernames raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid username values.

        Raises
        ------
        OrionisIntegrityException
            If the username is invalid.
        """

        # Attempt to assign invalid values to username and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            Oracle(username='')
        with self.assertRaises(OrionisIntegrityException):
            Oracle(username=123)

    async def testPasswordValidation(self):
        """
        Test validation for the `password` attribute.

        Ensures that non-string passwords raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid password values.

        Raises
        ------
        OrionisIntegrityException
            If the password is invalid.
        """

        # Attempt to assign an invalid value to password and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            Oracle(password=123)

    async def testHostValidation(self):
        """
        Test validation for the `host` attribute when not using DSN/TNS.

        Ensures that empty or non-string hosts raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid host values.

        Raises
        ------
        OrionisIntegrityException
            If the host is invalid.
        """

        # Attempt to assign invalid values to host and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            Oracle(host='', dsn=None, tns_name=None)
        with self.assertRaises(OrionisIntegrityException):
            Oracle(host=123, dsn=None, tns_name=None)

    async def testPortValidation(self):
        """
        Test validation for the `port` attribute when not using DSN/TNS.

        Ensures that invalid port numbers or types raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid port values.

        Raises
        ------
        OrionisIntegrityException
            If the port is invalid.
        """

        # Attempt to assign invalid values to port and expect exceptions
        with self.assertRaises(OrionisIntegrityException):
            Oracle(port=0, dsn=None, tns_name=None)
        with self.assertRaises(OrionisIntegrityException):
            Oracle(port=65536, dsn=None, tns_name=None)
        with self.assertRaises(OrionisIntegrityException):
            Oracle(port='1521', dsn=None, tns_name=None)

    async def testServiceNameAndSidValidation(self):
        """
        Test validation for `service_name` and `sid` attributes when not using DSN/TNS.

        Ensures that at least one of `service_name` or `sid` is required. Raises OrionisIntegrityException if both are missing.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised when both service_name and sid are missing, and that valid values do not raise exceptions.

        Raises
        ------
        OrionisIntegrityException
            If both `service_name` and `sid` are missing.
        """

        # Test with neither service_name nor sid
        with self.assertRaises(OrionisIntegrityException):
            Oracle(service_name=None, sid=None, dsn=None, tns_name=None)

        # Test valid with service_name only
        try:
            Oracle(service_name='ORCL', sid=None, dsn=None, tns_name=None)
        except OrionisIntegrityException:
            self.fail("Valid service_name should not raise exception")

        # Test valid with sid only
        try:
            Oracle(service_name=None, sid='XE', dsn=None, tns_name=None)
        except OrionisIntegrityException:
            self.fail("Valid sid should not raise exception")

    async def testDsnValidation(self):
        """
        Test validation for the `dsn` attribute.

        Ensures that `dsn` must be a non-empty string or None. Raises OrionisIntegrityException for invalid values.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid dsn values, and that valid values do not raise exceptions.

        Raises
        ------
        OrionisIntegrityException
            If the dsn is invalid.
        """

        # Attempt to assign an invalid value to dsn and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            Oracle(dsn='')

        # Test valid dsn value
        try:
            Oracle(dsn='valid_dsn_string')
        except OrionisIntegrityException:
            self.fail("Valid dsn should not raise exception")

    async def testTnsNameValidation(self):
        """
        Test validation for the `tns_name` attribute.

        Ensures that `tns_name` must be a non-empty string or None. Raises OrionisIntegrityException for invalid values.

        Returns
        -------
        None
            This test does not return a value. It asserts that exceptions are raised for invalid tns_name values, and that valid values do not raise exceptions.

        Raises
        ------
        OrionisIntegrityException
            If the tns_name is invalid.
        """

        # Attempt to assign an invalid value to tns_name and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            Oracle(tns_name='')

        # Test valid tns_name value
        try:
            Oracle(tns_name='valid_tns_name')
        except OrionisIntegrityException:
            self.fail("Valid tns_name should not raise exception")

    async def testEncodingValidation(self):
        """
        Test validation for the `encoding` attribute.

        Ensures correct enum conversion and invalid value handling for encoding.

        Returns
        -------
        None
            This test does not return a value. It asserts correct conversion and exception handling for encoding values.

        Raises
        ------
        OrionisIntegrityException
            If the encoding value is invalid.
        """

        # Test enum assignment
        oracle = Oracle(encoding=OracleEncoding.WE8ISO8859P1)
        self.assertEqual(oracle.encoding, OracleEncoding.WE8ISO8859P1.value)

        # Attempt to assign an invalid value to encoding and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            Oracle(encoding='INVALID')

    async def testNencodingValidation(self):
        """
        Test validation for the `nencoding` attribute.

        Ensures correct enum conversion and invalid value handling for nencoding.

        Returns
        -------
        None
            This test does not return a value. It asserts correct conversion and exception handling for nencoding values.

        Raises
        ------
        OrionisIntegrityException
            If the nencoding value is invalid.
        """

        # Test string conversion to enum value
        oracle = Oracle(nencoding='EE8MSWIN1250')
        self.assertEqual(oracle.nencoding, OracleNencoding.EE8MSWIN1250.value)

        # Test enum assignment
        oracle = Oracle(nencoding=OracleNencoding.ZHS16GBK)
        self.assertEqual(oracle.nencoding, OracleNencoding.ZHS16GBK.value)

        # Attempt to assign an invalid value to nencoding and expect an exception
        with self.assertRaises(OrionisIntegrityException):
            Oracle(nencoding='INVALID')

    async def testToDictMethod(self):
        """
        Test the `toDict` method for dictionary representation.

        Ensures that all attributes are correctly included in the returned dictionary and their values match the expected defaults.

        Returns
        -------
        None
            This test does not return a value. It asserts the structure and values of the dictionary returned by toDict().

        Raises
        ------
        AssertionError
            If any attribute is missing or incorrect in the dictionary.
        """

        # Create an Oracle instance with default configuration
        oracle = Oracle()
        oracle_dict = oracle.toDict()

        # Assert each attribute in the dictionary matches the expected default value
        self.assertEqual(oracle_dict['driver'], 'oracle')
        self.assertEqual(oracle_dict['username'], 'sys')
        self.assertEqual(oracle_dict['password'], '')
        self.assertEqual(oracle_dict['host'], 'localhost')
        self.assertEqual(oracle_dict['port'], 1521)
        self.assertEqual(oracle_dict['service_name'], 'ORCL')
        self.assertIsNone(oracle_dict['sid'])
        self.assertIsNone(oracle_dict['dsn'])
        self.assertIsNone(oracle_dict['tns_name'])
        self.assertEqual(oracle_dict['encoding'], OracleEncoding.AL32UTF8.value)
        self.assertEqual(oracle_dict['nencoding'], OracleNencoding.AL32UTF8.value)

    async def testConnectionMethods(self):
        """
        Test handling of different Oracle connection methods.

        Ensures that DSN, TNS, or host/port/service/sid combinations are valid and do not raise exceptions.

        Returns
        -------
        None
            This test does not return a value. It asserts that valid connection methods do not raise exceptions.

        Raises
        ------
        OrionisIntegrityException
            If a valid connection method raises an exception.
        """

        # Test DSN connection
        try:
            Oracle(dsn='valid_dsn', host=None, port=None, service_name=None, sid=None)
        except OrionisIntegrityException:
            self.fail("Valid DSN connection should not raise exception")

        # Test TNS connection
        try:
            Oracle(tns_name='valid_tns', host=None, port=None, service_name=None, sid=None)
        except OrionisIntegrityException:
            self.fail("Valid TNS connection should not raise exception")

        # Test host/port/service connection
        try:
            Oracle(dsn=None, tns_name=None, host='localhost', port=1521, service_name='ORCL')
        except OrionisIntegrityException:
            self.fail("Valid host/port/service connection should not raise exception")

        # Test host/port/sid connection
        try:
            Oracle(dsn=None, tns_name=None, host='localhost', port=1521, sid='XE')
        except OrionisIntegrityException:
            self.fail("Valid host/port/sid connection should not raise exception")