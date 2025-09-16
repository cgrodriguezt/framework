from orionis.foundation.config.mail.entities.mail import Mail
from orionis.foundation.config.mail.entities.mailers import Mailers
from orionis.foundation.exceptions import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigMail(AsyncTestCase):

    async def testDefaultInitialization(self):
        """
        Verify that a Mail instance is initialized with correct default values.

        This method checks that a Mail instance is initialized with the correct default values for its attributes.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Mail instance with default parameters
        mail = Mail()

        # Assert that the default mailer and mailers attributes are as expected
        self.assertEqual(mail.default, "smtp")
        self.assertIsInstance(mail.mailers, Mailers)

    async def testDefaultValidation(self):
        """
        Validate the default mailer attribute for correct value and type.

        This method ensures that providing an invalid default mailer raises an exception.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Mail with an invalid default mailer string; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Mail(default="invalid_mailer")

        # Attempt to initialize Mail with a non-string default mailer; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Mail(default=123)

    async def testMailersTypeValidation(self):
        """
        Validate the mailers attribute for correct type.

        This method ensures that assigning a non-Mailers object to mailers raises an exception.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Mail with a non-Mailers object; should raise exception
        with self.assertRaises(OrionisIntegrityException):
            Mail(mailers="invalid_mailers_object")

    async def testToDictMethod(self):
        """
        Validate the dictionary output of the toDict method for Mail.

        This method checks that the toDict method returns a dictionary representation of the Mail instance with all expected fields.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Mail instance
        mail = Mail()

        # Convert the Mail instance to a dictionary
        result = mail.toDict()

        # Assert that the dictionary contains the expected keys and values
        self.assertIsInstance(result, dict)
        self.assertIn("default", result)
        self.assertIn("mailers", result)
        self.assertEqual(result["default"], "smtp")

    async def testHashability(self):
        """
        Validate hashability of Mail instances.

        This method ensures that Mail instances are hashable and can be used in sets or as dictionary keys.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create two Mail instances with the same default value
        mail1 = Mail()
        mail2 = Mail(default="smtp")

        # Add both to a set; should only contain one unique instance
        test_set = {mail1, mail2}
        self.assertEqual(len(test_set), 1)

    async def testKwOnlyInitialization(self):
        """
        Validate enforcement of keyword-only initialization for Mail.

        This method ensures that Mail requires keyword arguments for initialization and raises a TypeError if positional arguments are used.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Attempt to initialize Mail with positional arguments; should raise TypeError
        with self.assertRaises(TypeError):
            Mail("smtp", Mailers())

    async def testValidCustomInitialization(self):
        """
        Validate custom initialization with valid parameters for Mail.

        This method checks that a Mail instance can be created with valid, non-default values and that the instance is initialized with the provided values.

        Returns
        -------
        None
            This method does not return a value. It asserts conditions for testing purposes.
        """

        # Create a Mail instance with custom values
        mail = Mail(default="smtp", mailers=Mailers())

        # Assert that the instance is initialized with the provided values
        self.assertEqual(mail.default, "smtp")
        self.assertIsInstance(mail.mailers, Mailers)