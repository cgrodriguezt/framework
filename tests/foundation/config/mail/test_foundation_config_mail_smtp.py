from orionis.foundation.config.mail.entities.smtp import Smtp
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.synchronous import SyncTestCase
from orionis.services.environment.env import Env

class TestFoundationConfigMailSmtp(SyncTestCase):

    def testDefaultInitialization(self):
        """
        Test default initialization of Smtp.

        Checks that an instance of Smtp is initialized with the correct default values.

        Returns
        -------
        None
        """
        smtp = Smtp()
        self.assertEqual(smtp.url, Env.get("MAIL_URL", ""))
        self.assertEqual(smtp.host, Env.get("MAIL_HOST", ""))
        self.assertEqual(smtp.port, Env.get("MAIL_PORT", 587))
        self.assertEqual(smtp.encryption, Env.get("MAIL_ENCRYPTION", "TLS"))
        self.assertEqual(smtp.username, Env.get("MAIL_USERNAME", ""))
        self.assertEqual(smtp.password, Env.get("MAIL_PASSWORD", ""))
        self.assertIsNone(smtp.timeout)

    def testTypeValidation(self):
        """
        Test type validation for Smtp attributes.

        Validates type checking for Smtp attributes and raises OrionisIntegrityException on invalid types.

        Returns
        -------
        None
        """
        with self.assertRaises(OrionisIntegrityException):
            Smtp(url=123)
        with self.assertRaises(OrionisIntegrityException):
            Smtp(host=456)
        with self.assertRaises(OrionisIntegrityException):
            Smtp(port="invalid")
        with self.assertRaises(OrionisIntegrityException):
            Smtp(encryption=123)
        with self.assertRaises(OrionisIntegrityException):
            Smtp(username=123)
        with self.assertRaises(OrionisIntegrityException):
            Smtp(password=123)
        with self.assertRaises(OrionisIntegrityException):
            Smtp(timeout="invalid")

    def testPortValidation(self):
        """
        Test port attribute validation.

        Checks that the port attribute does not accept negative values.

        Returns
        -------
        None
        """
        with self.assertRaises(OrionisIntegrityException):
            Smtp(port=-1)

    def testTimeoutValidation(self):
        """
        Test timeout attribute validation.

        Checks that the timeout attribute does not accept negative values.

        Returns
        -------
        None
        """
        with self.assertRaises(OrionisIntegrityException):
            Smtp(timeout=-1)

    def testValidCustomInitialization(self):
        """
        Test custom initialization with valid parameters.

        Validates custom initialization of Smtp with valid parameters.

        Returns
        -------
        None
        """
        custom_config = Smtp(
            url="smtp.example.com",
            host="mail.example.com",
            port=465,
            encryption="SSL",
            username="user",
            password="pass",
            timeout=30,
        )
        self.assertEqual(custom_config.url, "smtp.example.com")
        self.assertEqual(custom_config.host, "mail.example.com")
        self.assertEqual(custom_config.port, 465)
        self.assertEqual(custom_config.encryption, "SSL")
        self.assertEqual(custom_config.username, "user")
        self.assertEqual(custom_config.password, "pass")
        self.assertEqual(custom_config.timeout, 30)

    def testToDictMethod(self):
        """
        Test Smtp.toDict method output.

        Validates the dictionary output of the Smtp.toDict method.

        Returns
        -------
        None
        """
        smtp = Smtp()
        result = smtp.toDict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["url"], Env.get("MAIL_URL", ""))
        self.assertEqual(result["host"], Env.get("MAIL_HOST", ""))
        self.assertEqual(result["port"], Env.get("MAIL_PORT", 587))
        self.assertEqual(result["encryption"], Env.get("MAIL_ENCRYPTION", "TLS"))
        self.assertEqual(result["username"], Env.get("MAIL_USERNAME", ""))
        self.assertEqual(result["password"], Env.get("MAIL_PASSWORD", ""))
        self.assertIsNone(result["timeout"])

    def testKwOnlyInitialization(self):
        """
        Test keyword-only initialization requirement.

        Checks that Smtp requires keyword-only arguments (kw_only=True).

        Returns
        -------
        None
        """
        with self.assertRaises(TypeError):
            Smtp("smtp.mailtrap.io", "smtp.mailtrap.io", 587, "TLS", "", "", None)
