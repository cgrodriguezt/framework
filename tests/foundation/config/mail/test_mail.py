from orionis.test import TestCase
from orionis.foundation.config.mail.entities.mail import Mail
from orionis.foundation.config.mail.entities.mailers import Mailers
from orionis.foundation.config.mail.entities.smtp import Smtp
from orionis.foundation.config.mail.entities.file import File as MailFile

# ===========================================================================
# Smtp entity
# ===========================================================================

class TestSmtpEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Smtp can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Smtp()
        self.assertIsInstance(s, Smtp)

    def testDefaultPortIsNonNegativeInt(self) -> None:
        """
        Test that the default port is a non-negative integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Smtp()
        self.assertIsInstance(s.port, int)
        self.assertGreaterEqual(s.port, 0)

    def testDefaultTimeoutIsNoneOrPositive(self) -> None:
        """
        Test that the default timeout is None or a positive integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Smtp()
        self.assertTrue(s.timeout is None or (isinstance(s.timeout, int) and s.timeout >= 0))

    def testInvalidPortTypeRaisesTypeError(self) -> None:
        """
        Test that a non-integer port raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Smtp(port="587")  # type: ignore[arg-type]

    def testNegativePortRaisesValueError(self) -> None:
        """
        Test that a negative port value raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Smtp(port=-1)

    def testNegativeTimeoutRaisesValueError(self) -> None:
        """
        Test that a negative timeout raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Smtp(timeout=-10)

    def testInvalidTimeoutTypeRaisesTypeError(self) -> None:
        """
        Test that a non-integer timeout raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Smtp(timeout="30")  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Smtp instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        s = Smtp()
        with self.assertRaises(FrozenInstanceError):
            s.port = 25  # type: ignore[misc]

# ===========================================================================
# MailFile entity
# ===========================================================================

class TestMailFileEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that mail File can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        f = MailFile()
        self.assertIsInstance(f, MailFile)

    def testDefaultPath(self) -> None:
        """
        Test that the default mail file path is 'storage/mail'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(MailFile().path, "storage/mail")

    def testEmptyPathRaisesValueError(self) -> None:
        """
        Test that an empty path raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            MailFile(path="")

    def testWhitespacePathRaisesValueError(self) -> None:
        """
        Test that a whitespace-only path raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            MailFile(path="   ")

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen mail File instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        f = MailFile()
        with self.assertRaises(FrozenInstanceError):
            f.path = "other"  # type: ignore[misc]

# ===========================================================================
# Mailers entity
# ===========================================================================

class TestMailersEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Mailers can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        m = Mailers()
        self.assertIsInstance(m, Mailers)

    def testDefaultSmtpIsSmtpInstance(self) -> None:
        """
        Test that the default smtp attribute is a Smtp instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Mailers().smtp, Smtp)

    def testDefaultFileIsMailFileInstance(self) -> None:
        """
        Test that the default file attribute is a mail File instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Mailers().file, MailFile)

    def testSmtpDictConversion(self) -> None:
        """
        Test that a dict for smtp is converted to a Smtp instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        m = Mailers(smtp={"host": "mail.example.com"})
        self.assertIsInstance(m.smtp, Smtp)

    def testInvalidSmtpTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for smtp raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Mailers(smtp="not_smtp")  # type: ignore[arg-type]

    def testInvalidFileTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for file raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Mailers(file=123)  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Mailers instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        m = Mailers()
        with self.assertRaises(FrozenInstanceError):
            m.smtp = Smtp()  # type: ignore[misc]

# ===========================================================================
# Mail entity
# ===========================================================================

class TestMailEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Mail can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        mail = Mail()
        self.assertIsInstance(mail, Mail)

    def testDefaultIsString(self) -> None:
        """
        Test that the default attribute is a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Mail().default, str)

    def testDefaultMailersIsMailersInstance(self) -> None:
        """
        Test that the mailers attribute is a Mailers instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Mail().mailers, Mailers)

    def testInvalidDefaultRaisesValueError(self) -> None:
        """
        Test that an unrecognized default mailer raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Mail(default="sendgrid")

    def testDictMailersConversion(self) -> None:
        """
        Test that a dict for mailers is converted to a Mailers instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        mail = Mail(mailers={})
        self.assertIsInstance(mail.mailers, Mailers)

    def testInvalidMailersTypeRaisesTypeError(self) -> None:
        """
        Test that an invalid type for mailers raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Mail(mailers="invalid")  # type: ignore[arg-type]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Mail instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        mail = Mail()
        with self.assertRaises(FrozenInstanceError):
            mail.default = "file"  # type: ignore[misc]
