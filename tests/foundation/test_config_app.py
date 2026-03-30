from orionis.test import TestCase
from orionis.foundation.config.app.entities.app import App
from orionis.foundation.config.app.enums.ciphers import Cipher
from orionis.foundation.config.app.enums.environments import Environments

# ===========================================================================
# Environments enum
# ===========================================================================

class TestEnvironmentsEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that all expected Environments members are present.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("DEVELOPMENT", Environments._member_names_)
        self.assertIn("TESTING", Environments._member_names_)
        self.assertIn("PRODUCTION", Environments._member_names_)

    def testMemberValues(self) -> None:
        """
        Test the string values assigned to each Environments member.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Environments.DEVELOPMENT.value, "development")
        self.assertEqual(Environments.TESTING.value, "testing")
        self.assertEqual(Environments.PRODUCTION.value, "production")

    def testLookupByName(self) -> None:
        """
        Test that Environments members can be retrieved by name.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Environments["DEVELOPMENT"], Environments.DEVELOPMENT)

    def testLookupByValue(self) -> None:
        """
        Test that Environments members can be retrieved by value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Environments("production"), Environments.PRODUCTION)

    def testUnknownValueRaises(self) -> None:
        """
        Test that looking up an unknown value raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Environments("staging")

    def testMemberCount(self) -> None:
        """
        Test that exactly three Environments members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(Environments), 3)

    def testIsHashable(self) -> None:
        """
        Test that Environments members are hashable and usable as dict keys.

        Returns
        -------
        None
            This method does not return a value.
        """
        mapping = {Environments.DEVELOPMENT: 1}
        self.assertEqual(mapping[Environments.DEVELOPMENT], 1)

# ===========================================================================
# Cipher enum
# ===========================================================================

class TestCipherEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that all expected Cipher members are present.

        Returns
        -------
        None
            This method does not return a value.
        """
        expected = {"AES_128_CBC", "AES_256_CBC", "AES_128_GCM", "AES_256_GCM"}
        self.assertEqual(set(Cipher._member_names_), expected)

    def testMemberValues(self) -> None:
        """
        Test the string values assigned to each Cipher member.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Cipher.AES_128_CBC.value, "AES-128-CBC")
        self.assertEqual(Cipher.AES_256_CBC.value, "AES-256-CBC")
        self.assertEqual(Cipher.AES_128_GCM.value, "AES-128-GCM")
        self.assertEqual(Cipher.AES_256_GCM.value, "AES-256-GCM")

    def testLookupByName(self) -> None:
        """
        Test that Cipher members can be retrieved by name.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Cipher["AES_256_CBC"], Cipher.AES_256_CBC)

    def testLookupByValue(self) -> None:
        """
        Test that Cipher members can be retrieved by their string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Cipher("AES-256-GCM"), Cipher.AES_256_GCM)

    def testUnknownValueRaises(self) -> None:
        """
        Test that looking up an unknown cipher value raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Cipher("DES-64")

    def testMemberCount(self) -> None:
        """
        Test that exactly four Cipher members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(Cipher), 4)

# ===========================================================================
# App entity
# ===========================================================================

class TestAppEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that App can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App()
        self.assertIsInstance(app, App)

    def testDefaultNameIsString(self) -> None:
        """
        Test that the default name attribute is a non-empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App()
        self.assertIsInstance(app.name, str)
        self.assertTrue(app.name.strip())

    def testDefaultEnvIsNormalized(self) -> None:
        """
        Test that the env attribute is normalized to a lowercase string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App()
        self.assertIn(app.env, [e.value for e in Environments])

    def testDefaultDebugIsBoolean(self) -> None:
        """
        Test that the debug attribute defaults to a boolean value.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App()
        self.assertIsInstance(app.debug, bool)

    def testDefaultPortIsPositiveInt(self) -> None:
        """
        Test that the default port is a positive integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App()
        self.assertIsInstance(app.port, int)
        self.assertGreater(app.port, 0)

    def testDefaultWorkersIsPositiveInt(self) -> None:
        """
        Test that the default workers attribute is a positive integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App()
        self.assertIsInstance(app.workers, int)
        self.assertGreaterEqual(app.workers, 1)

    def testDefaultKeyIsSet(self) -> None:
        """
        Test that the key attribute is auto-generated when not supplied.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App()
        self.assertIsNotNone(app.key)
        self.assertTrue(str(app.key).strip())

    def testDefaultCipherIsNormalized(self) -> None:
        """
        Test that the cipher attribute is a valid Cipher string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App()
        self.assertIn(app.cipher, [c.value for c in Cipher])

    def testEnvStringNormalization(self) -> None:
        """
        Test that passing an environment string is normalized to its enum value.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App(env="production")
        self.assertEqual(app.env, Environments.PRODUCTION.value)

    def testEnvEnumNormalization(self) -> None:
        """
        Test that passing an Environments enum is stored as its value string.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App(env=Environments.TESTING)
        self.assertEqual(app.env, Environments.TESTING.value)

    def testCipherStringNormalization(self) -> None:
        """
        Test that cipher string input is normalized to the enum value.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App(cipher="AES-256-GCM")
        self.assertEqual(app.cipher, Cipher.AES_256_GCM.value)

    def testCipherEnumNormalization(self) -> None:
        """
        Test that a Cipher enum instance is normalized to its string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        app = App(cipher=Cipher.AES_128_CBC)
        self.assertEqual(app.cipher, Cipher.AES_128_CBC.value)

    def testInvalidEnvRaisesValueError(self) -> None:
        """
        Test that an unrecognized env string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            App(env="staging")

    def testInvalidEnvTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string, non-Environments env raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            App(env=42)  # type: ignore[arg-type]

    def testInvalidDebugTypeRaisesTypeError(self) -> None:
        """
        Test that a non-boolean debug value raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            App(debug="yes")  # type: ignore[arg-type]

    def testInvalidCipherRaisesValueError(self) -> None:
        """
        Test that an unrecognized cipher string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            App(cipher="DES-64")

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen App instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        app = App()
        with self.assertRaises(FrozenInstanceError):
            app.name = "changed"  # type: ignore[misc]

    def testInvalidWorkersRaisesValueError(self) -> None:
        """
        Test that workers=0 raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            App(workers=0)
