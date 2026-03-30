from orionis.test import TestCase
from orionis.foundation.config.session.entities.session import Session
from orionis.foundation.config.session.enums.same_site_policy import SameSitePolicy
from orionis.foundation.config.session.helpers.secret_key import SecretKey

# ===========================================================================
# SameSitePolicy enum
# ===========================================================================

class TestSameSitePolicyEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that LAX, STRICT and NONE members exist in SameSitePolicy.

        Returns
        -------
        None
            This method does not return a value.
        """
        for name in ("LAX", "STRICT", "NONE"):
            self.assertIn(name, SameSitePolicy._member_names_)

    def testMemberValues(self) -> None:
        """
        Test the string values assigned to each SameSitePolicy member.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(SameSitePolicy.LAX.value, "lax")
        self.assertEqual(SameSitePolicy.STRICT.value, "strict")
        self.assertEqual(SameSitePolicy.NONE.value, "none")

    def testLookupByName(self) -> None:
        """
        Test that SameSitePolicy members can be retrieved by their name.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(SameSitePolicy["STRICT"], SameSitePolicy.STRICT)

    def testLookupByValue(self) -> None:
        """
        Test that SameSitePolicy members can be retrieved by their value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(SameSitePolicy("none"), SameSitePolicy.NONE)

    def testUnknownValueRaises(self) -> None:
        """
        Test that an unknown value raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            SameSitePolicy("samesite")

    def testMemberCount(self) -> None:
        """
        Test that exactly three SameSitePolicy members exist.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(SameSitePolicy), 3)

    def testIsHashable(self) -> None:
        """
        Test that SameSitePolicy members are hashable.

        Returns
        -------
        None
            This method does not return a value.
        """
        mapping = {SameSitePolicy.LAX: "lax"}
        self.assertEqual(mapping[SameSitePolicy.LAX], "lax")

# ===========================================================================
# SecretKey helper
# ===========================================================================

class TestSecretKeyHelper(TestCase):

    def testRandomReturnsString(self) -> None:
        """
        Test that SecretKey.random() returns a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(SecretKey.random(), str)

    def testDefaultLengthIs64Chars(self) -> None:
        """
        Test that the default random key is 64 hex characters (32 bytes).

        Returns
        -------
        None
            This method does not return a value.
        """
        # secrets.token_hex(32) returns 64 hex characters
        self.assertEqual(len(SecretKey.random()), 64)

    def testCustomLength(self) -> None:
        """
        Test that a custom length produces a key of the expected hex length.

        Returns
        -------
        None
            This method does not return a value.
        """
        key = SecretKey.random(length=16)
        self.assertEqual(len(key), 32)  # 16 bytes → 32 hex chars

    def testKeysAreUnique(self) -> None:
        """
        Test that two successive calls produce different keys.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertNotEqual(SecretKey.random(), SecretKey.random())

    def testKeyIsHexString(self) -> None:
        """
        Test that the generated key contains only valid hexadecimal characters.

        Returns
        -------
        None
            This method does not return a value.
        """
        key = SecretKey.random()
        int(key, 16)  # Raises ValueError if not a valid hex string

# ===========================================================================
# Session entity
# ===========================================================================

class TestSessionEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Session can be instantiated with default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Session()
        self.assertIsInstance(s, Session)

    def testDefaultSecretKeyIsNonEmptyString(self) -> None:
        """
        Test that the default secret_key is a non-empty string or bytes value.

        The secret_key may be a str (hex key from SecretKey.random) or bytes
        (decoded from a base64: prefixed APP_KEY env variable), so both types
        are valid.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Session()
        self.assertIsInstance(s.secret_key, (str, bytes))
        key = s.secret_key
        self.assertTrue(key.strip() if isinstance(key, str) else key)

    def testDefaultSessionCookieIsString(self) -> None:
        """
        Test that session_cookie defaults to a non-empty string.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Session().session_cookie, str)

    def testDefaultSameSiteIsNormalized(self) -> None:
        """
        Test that the default same_site is a valid SameSitePolicy value.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Session()
        self.assertIn(s.same_site, [p.value for p in SameSitePolicy])

    def testDefaultPathStartsWithSlash(self) -> None:
        """
        Test that the default path starts with '/'.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(Session().path.startswith("/"))

    def testDefaultHttpsOnlyIsBool(self) -> None:
        """
        Test that https_only defaults to a boolean value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(Session().https_only, bool)

    def testSameSiteStringNormalization(self) -> None:
        """
        Test that a SameSitePolicy string is normalized to its enum value.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Session(same_site="STRICT")
        self.assertEqual(s.same_site, SameSitePolicy.STRICT.value)

    def testSameSiteEnumNormalization(self) -> None:
        """
        Test that a SameSitePolicy enum is stored as its string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Session(same_site=SameSitePolicy.NONE)
        self.assertEqual(s.same_site, SameSitePolicy.NONE.value)

    def testInvalidSecretKeyRaisesValueError(self) -> None:
        """
        Test that an empty secret_key string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Session(secret_key="   ")

    def testInvalidSessionCookieWithSpaceRaisesValueError(self) -> None:
        """
        Test that a session_cookie containing a space raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Session(session_cookie="my cookie")

    def testNegativeMaxAgeRaisesValueError(self) -> None:
        """
        Test that a non-positive max_age raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Session(max_age=0)

    def testInvalidMaxAgeTypeRaisesTypeError(self) -> None:
        """
        Test that a non-integer max_age raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Session(max_age="30")  # type: ignore[arg-type]

    def testInvalidSameSiteRaisesValueError(self) -> None:
        """
        Test that an unrecognized same_site string raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Session(same_site="partial")

    def testInvalidPathRaisesValueError(self) -> None:
        """
        Test that a path not starting with '/' raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Session(path="no-slash")

    def testInvalidHttpsOnlyTypeRaisesTypeError(self) -> None:
        """
        Test that a non-boolean https_only raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Session(https_only="true")  # type: ignore[arg-type]

    def testDomainWithLeadingDotRaisesValueError(self) -> None:
        """
        Test that a domain starting with a dot raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Session(domain=".example.com")

    def testDomainWithConsecutiveDotsRaisesValueError(self) -> None:
        """
        Test that a domain containing consecutive dots raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Session(domain="exam..ple.com")

    def testValidDomainIsAccepted(self) -> None:
        """
        Test that a valid domain string is accepted.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Session(domain="example.com")
        self.assertEqual(s.domain, "example.com")

    def testNullDomainIsAccepted(self) -> None:
        """
        Test that domain=None is valid.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Session(domain=None)
        self.assertIsNone(s.domain)

    def testNullMaxAgeIsAccepted(self) -> None:
        """
        Test that max_age=None represents a browser-session cookie.

        Returns
        -------
        None
            This method does not return a value.
        """
        s = Session(max_age=None)
        self.assertIsNone(s.max_age)

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Session instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        s = Session()
        with self.assertRaises(FrozenInstanceError):
            s.secret_key = "other"  # type: ignore[misc]
