from orionis.foundation.config.mail.entities.smtp import Smtp
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase

class TestFoundationConfigMailSmtp(SyncTestCase):

    def testDefaultInitialization(self):
        """
        Verify that an Smtp instance is initialized with correct default values.

        This method ensures that an Smtp instance is initialized with the correct default values for all attributes.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create an Smtp instance with default parameters
        smtp = Smtp()

        # Assert that all default attribute values are as expected
        self.assertEqual(smtp.url, "smtp.mailtrap.io")
        self.assertEqual(smtp.host, "smtp.mailtrap.io")
        self.assertEqual(smtp.port, 587)
        self.assertEqual(smtp.encryption, "TLS")
        self.assertEqual(smtp.username, "")
        self.assertEqual(smtp.password, "")
        self.assertIsNone(smtp.timeout)

    def testTypeValidation(self):
        """
        Validate type checking for Smtp attributes.

        This method ensures that providing invalid types for Smtp attributes raises
        OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test invalid type for url
        with self.assertRaises(OrionisIntegrityException):
            Smtp(url=123)

        # Test invalid type for host
        with self.assertRaises(OrionisIntegrityException):
            Smtp(host=456)

        # Test invalid type for port
        with self.assertRaises(OrionisIntegrityException):
            Smtp(port="invalid")

        # Test invalid type for encryption
        with self.assertRaises(OrionisIntegrityException):
            Smtp(encryption=123)

        # Test invalid type for username
        with self.assertRaises(OrionisIntegrityException):
            Smtp(username=123)

        # Test invalid type for password
        with self.assertRaises(OrionisIntegrityException):
            Smtp(password=123)

        # Test invalid type for timeout
        with self.assertRaises(OrionisIntegrityException):
            Smtp(timeout="invalid")

    def testPortValidation(self):
        """
        Validate the port attribute for correct value.

        This method ensures that negative port numbers raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test negative port value; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Smtp(port=-1)

    def testTimeoutValidation(self):
        """
        Validate the timeout attribute for correct value.

        This method ensures that negative timeout values raise OrionisIntegrityException.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Test negative timeout value; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Smtp(timeout=-1)

    def testValidCustomInitialization(self):
        """
        Validate custom initialization with valid parameters.

        This method ensures that valid custom values are accepted and stored correctly.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create an Smtp instance with custom values
        custom_config = Smtp(
            url="smtp.example.com",
            host="mail.example.com",
            port=465,
            encryption="SSL",
            username="user",
            password="pass",
            timeout=30
        )

        # Assert that all custom values are stored correctly
        self.assertEqual(custom_config.url, "smtp.example.com")
        self.assertEqual(custom_config.host, "mail.example.com")
        self.assertEqual(custom_config.port, 465)
        self.assertEqual(custom_config.encryption, "SSL")
        self.assertEqual(custom_config.username, "user")
        self.assertEqual(custom_config.password, "pass")
        self.assertEqual(custom_config.timeout, 30)

    def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Smtp.

        This method ensures that the toDict method returns a dictionary containing all fields
        with correct values.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create an Smtp instance
        smtp = Smtp()

        # Convert the Smtp instance to a dictionary
        result = smtp.toDict()

        # Assert that the dictionary contains the expected values
        self.assertIsInstance(result, dict)
        self.assertEqual(result["url"], "smtp.mailtrap.io")
        self.assertEqual(result["host"], "smtp.mailtrap.io")
        self.assertEqual(result["port"], 587)
        self.assertEqual(result["encryption"], "TLS")
        self.assertEqual(result["username"], "")
        self.assertEqual(result["password"], "")
        self.assertIsNone(result["timeout"])

    def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Smtp.

        This method ensures that Smtp requires keyword arguments for initialization and
        enforces kw_only=True in its dataclass decorator. Raises a TypeError if positional arguments are used.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Smtp with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Smtp("smtp.mailtrap.io", "smtp.mailtrap.io", 587, "TLS", "", "", None)