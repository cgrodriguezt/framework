from dataclasses import FrozenInstanceError
from orionis.test import TestCase
from orionis.foundation.config.http.entitites.cors import Cors

# ===========================================================================
# Cors entity
# ===========================================================================


class TestCors(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Construct Cors with all default values.

        Verifies that a Cors instance can be created without providing
        any arguments and that it is the expected type.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors()
        self.assertIsInstance(cors, Cors)

    def testDefaultAllowOriginsIsWildcard(self) -> None:
        """
        Verify allow_origins defaults to the wildcard list.

        Ensures the default value permits requests from any origin
        by using the ``["*"]`` list.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Cors().allow_origins, ["*"])

    def testDefaultAllowOriginRegexIsNone(self) -> None:
        """
        Verify allow_origin_regex defaults to None.

        Ensures that no regex origin filter is applied unless
        explicitly configured.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsNone(Cors().allow_origin_regex)

    def testDefaultAllowMethodsIsWildcard(self) -> None:
        """
        Verify allow_methods defaults to the wildcard list.

        Ensures the default configuration permits all HTTP methods.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Cors().allow_methods, ["*"])

    def testDefaultAllowHeadersIsWildcard(self) -> None:
        """
        Verify allow_headers defaults to the wildcard list.

        Ensures the default configuration permits all HTTP headers.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Cors().allow_headers, ["*"])

    def testDefaultExposeHeadersIsEmpty(self) -> None:
        """
        Verify expose_headers defaults to an empty list.

        Ensures that no response headers are exposed to the browser
        unless explicitly configured.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Cors().expose_headers, [])

    def testDefaultAllowCredentialsIsFalse(self) -> None:
        """
        Verify allow_credentials defaults to False.

        Ensures credentials (cookies, auth headers) are not permitted
        by default.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertFalse(Cors().allow_credentials)

    def testDefaultMaxAgeIs600(self) -> None:
        """
        Verify max_age defaults to 600 seconds.

        Ensures preflight responses are cached for ten minutes by
        default.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Cors().max_age, 600)

    def testCustomAllowOrigins(self) -> None:
        """
        Accept a custom list of allowed origins.

        Verifies that a specific origin list is stored unchanged on
        the Cors instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        origins = ["https://example.com", "https://api.example.com"]
        cors = Cors(allow_origins=origins)
        self.assertEqual(cors.allow_origins, origins)

    def testCustomAllowOriginRegex(self) -> None:
        """
        Accept a valid regex string for allow_origin_regex.

        Verifies that a regex pattern is stored unchanged when provided
        as a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        pattern = r"https://.*\.example\.com"
        cors = Cors(allow_origin_regex=pattern)
        self.assertEqual(cors.allow_origin_regex, pattern)

    def testCustomAllowMethods(self) -> None:
        """
        Accept a list of explicit HTTP method names.

        Verifies that valid method names are stored and accessible after
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        methods = ["GET", "POST"]
        cors = Cors(allow_methods=methods)
        self.assertEqual(cors.allow_methods, methods)

    def testCustomAllowHeaders(self) -> None:
        """
        Accept a custom list of allowed request headers.

        Verifies that a specific header list is stored unchanged on
        the Cors instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        headers = ["Content-Type", "Authorization"]
        cors = Cors(allow_headers=headers)
        self.assertEqual(cors.allow_headers, headers)

    def testCustomExposeHeaders(self) -> None:
        """
        Accept a custom list of exposed response headers.

        Verifies that a list of headers to expose to the browser is
        stored correctly.

        Returns
        -------
        None
            This method does not return a value.
        """
        exposed = ["X-Custom-Header"]
        cors = Cors(expose_headers=exposed)
        self.assertEqual(cors.expose_headers, exposed)

    def testCustomAllowCredentials(self) -> None:
        """
        Accept True for allow_credentials.

        Verifies that enabling credentials is properly stored on the
        Cors instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors(allow_credentials=True)
        self.assertTrue(cors.allow_credentials)

    def testCustomMaxAge(self) -> None:
        """
        Accept a custom positive integer for max_age.

        Verifies that a non-default cache duration is stored on the
        Cors instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors(max_age=3600)
        self.assertEqual(cors.max_age, 3600)

    def testMaxAgeCanBeNone(self) -> None:
        """
        Accept None for max_age.

        Verifies that disabling the preflight cache by passing None is
        supported without raising an error.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors(max_age=None)
        self.assertIsNone(cors.max_age)

    def testInvalidAllowOriginsTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when allow_origins is not a list.

        Verifies that passing a non-list value (e.g. a string) for
        allow_origins triggers a TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(allow_origins="*")  # type: ignore[arg-type]

    def testInvalidAllowOriginRegexTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when allow_origin_regex is not a string.

        Verifies that providing a non-string, non-None value for
        allow_origin_regex triggers a TypeError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(allow_origin_regex=123)  # type: ignore[arg-type]

    def testInvalidAllowMethodsTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when allow_methods is not a list.

        Verifies that a string or other non-list type for allow_methods
        triggers a TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(allow_methods="GET")  # type: ignore[arg-type]

    def testInvalidAllowHeadersTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when allow_headers is not a list.

        Verifies that a non-list value for allow_headers triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(allow_headers="Content-Type")  # type: ignore[arg-type]

    def testInvalidExposeHeadersTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when expose_headers is not a list.

        Verifies that a non-list value for expose_headers triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(expose_headers="X-Header")  # type: ignore[arg-type]

    def testInvalidAllowCredentialsTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when allow_credentials is not a boolean.

        Verifies that an integer or string for allow_credentials
        triggers a TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(allow_credentials="yes")  # type: ignore[arg-type]

    def testInvalidMaxAgeTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when max_age is not an integer or None.

        Verifies that a string value for max_age triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(max_age="600")  # type: ignore[arg-type]

    def testInvalidHttpMethodRaisesValueError(self) -> None:
        """
        Raise ValueError when allow_methods contains an unsupported method.

        Verifies that methods outside the defined allowed set trigger
        a ValueError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Cors(allow_methods=["BREW"])

    def testNonStringInAllowMethodsRaisesTypeError(self) -> None:
        """
        Raise TypeError when allow_methods contains a non-string item.

        Verifies that mixed-type lists for allow_methods trigger a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            Cors(allow_methods=[123])  # type: ignore[list-item]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Raise FrozenInstanceError when mutating a Cors instance.

        Confirms the dataclass is immutable and rejects attribute
        reassignment after construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        cors = Cors()
        with self.assertRaises(FrozenInstanceError):
            cors.allow_origins = ["https://example.com"]  # type: ignore[misc]

    def testToDictReturnsDict(self) -> None:
        """
        Verify toDict returns a plain dictionary representation.

        Ensures the inherited toDict helper converts the Cors instance
        to a dict containing at least the expected keys.

        Returns
        -------
        None
            This method does not return a value.
        """
        result = Cors().toDict()
        self.assertIsInstance(result, dict)
        self.assertIn("allow_origins", result)
        self.assertIn("allow_credentials", result)
