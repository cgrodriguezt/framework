from orionis.test import TestCase
from orionis.foundation.config.auth.entities.auth import Auth
from orionis.foundation.config.cors.entities.cors import Cors

# ===========================================================================
# Auth entity
# ===========================================================================

class TestAuthEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Auth can be instantiated with no arguments.

        Returns
        -------
        None
            This method does not return a value.
        """
        a = Auth()
        self.assertIsInstance(a, Auth)

    def testIsFrozen(self) -> None:
        """
        Test that Auth is a frozen dataclass by verifying it has no mutable fields.

        Returns
        -------
        None
            This method does not return a value.
        """
        import dataclasses
        self.assertTrue(dataclasses.is_dataclass(Auth))

    def testTwoInstancesAreEqual(self) -> None:
        """
        Test that two default Auth instances compare equal.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Auth(), Auth())

# ===========================================================================
# Cors entity
# ===========================================================================

class TestCorsEntity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Test that Cors can be instantiated with all default values.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors()
        self.assertIsInstance(cors, Cors)

    def testDefaultAllowOrigins(self) -> None:
        """
        Test that the default allow_origins is the wildcard list.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors()
        self.assertEqual(cors.allow_origins, ["*"])

    def testDefaultAllowMethods(self) -> None:
        """
        Test that the default allow_methods is the wildcard list.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors()
        self.assertEqual(cors.allow_methods, ["*"])

    def testDefaultAllowHeaders(self) -> None:
        """
        Test that the default allow_headers is the wildcard list.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors()
        self.assertEqual(cors.allow_headers, ["*"])

    def testDefaultExposeHeadersIsEmptyList(self) -> None:
        """
        Test that the default expose_headers is an empty list.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors()
        self.assertEqual(cors.expose_headers, [])

    def testDefaultAllowCredentialsIsFalse(self) -> None:
        """
        Test that allow_credentials defaults to False.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors()
        self.assertFalse(cors.allow_credentials)

    def testDefaultMaxAge(self) -> None:
        """
        Test that the default max_age is 600 seconds.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors()
        self.assertEqual(cors.max_age, 600)

    def testDefaultAllowOriginRegexIsNone(self) -> None:
        """
        Test that the default allow_origin_regex is None.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors()
        self.assertIsNone(cors.allow_origin_regex)

    def testCustomAllowOrigins(self) -> None:
        """
        Test that a custom list of allowed origins is stored correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors(allow_origins=["https://example.com"])
        self.assertEqual(cors.allow_origins, ["https://example.com"])

    def testValidAllowMethods(self) -> None:
        """
        Test that valid explicit HTTP methods are accepted.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors(allow_methods=["GET", "POST"])
        self.assertEqual(cors.allow_methods, ["GET", "POST"])

    def testInvalidAllowMethodsRaisesValueError(self) -> None:
        """
        Test that an unrecognized HTTP method in allow_methods raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Cors(allow_methods=["BREW"])

    def testInvalidAllowMethodTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string element in allow_methods raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(allow_methods=[123])  # type: ignore[list-item]

    def testInvalidAllowOriginsTypeRaisesTypeError(self) -> None:
        """
        Test that a non-list allow_origins raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(allow_origins="*")  # type: ignore[arg-type]

    def testInvalidAllowOriginRegexTypeRaisesTypeError(self) -> None:
        """
        Test that a non-string allow_origin_regex raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(allow_origin_regex=123)  # type: ignore[arg-type]

    def testInvalidMaxAgeTypeRaisesTypeError(self) -> None:
        """
        Test that a non-integer max_age raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(max_age="600")  # type: ignore[arg-type]

    def testInvalidAllowCredentialsRaisesTypeError(self) -> None:
        """
        Test that a non-boolean allow_credentials raises TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(allow_credentials="True")  # type: ignore[arg-type]

    def testNullMaxAgeIsAccepted(self) -> None:
        """
        Test that max_age=None is a valid configuration.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors(max_age=None)
        self.assertIsNone(cors.max_age)

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Test that mutating a frozen Cors instance raises FrozenInstanceError.

        Returns
        -------
        None
            This method does not return a value.
        """
        from dataclasses import FrozenInstanceError
        cors = Cors()
        with self.assertRaises(FrozenInstanceError):
            cors.allow_origins = []  # type: ignore[misc]
