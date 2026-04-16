from dataclasses import FrozenInstanceError
from orionis.test import TestCase
from orionis.foundation.config.http.entitites.request import HTTPRequest

# ===========================================================================
# HTTPRequest entity
# ===========================================================================


class TestHTTPRequest(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Construct HTTPRequest with all default values.

        Verifies that an HTTPRequest instance can be created without
        providing any arguments.

        Returns
        -------
        None
            This method does not return a value.
        """
        req = HTTPRequest()
        self.assertIsInstance(req, HTTPRequest)

    def testDefaultAllowedContentTypesIsWildcard(self) -> None:
        """
        Verify allowed_content_types defaults to the wildcard string.

        Ensures all content types are permitted by default.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(HTTPRequest().allowed_content_types, "*")

    def testDefaultMaxContentLengthIsPositiveInt(self) -> None:
        """
        Verify max_content_length defaults to a positive integer.

        Ensures the default body size limit is a strictly positive int
        when no environment variable overrides it.

        Returns
        -------
        None
            This method does not return a value.
        """
        val = HTTPRequest().max_content_length
        self.assertIsInstance(val, int)
        self.assertGreater(val, 0)

    def testDefaultEnableMethodOverrideIsBool(self) -> None:
        """
        Verify enable_method_override defaults to a boolean.

        Ensures the field holds a proper boolean type when built with
        defaults.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(HTTPRequest().enable_method_override, bool)

    def testDefaultMethodOverrideHeaderIsString(self) -> None:
        """
        Verify method_override_header defaults to a non-empty string.

        Ensures the default override header name is a valid string
        ready for HTTP header matching.

        Returns
        -------
        None
            This method does not return a value.
        """
        val = HTTPRequest().method_override_header
        self.assertIsInstance(val, str)
        self.assertTrue(len(val) > 0)

    def testCustomAllowedContentTypesAsList(self) -> None:
        """
        Accept a list of MIME type strings for allowed_content_types.

        Verifies that an explicit list of content types is stored
        unchanged on the HTTPRequest instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        types = ["application/json", "text/plain"]
        req = HTTPRequest(allowed_content_types=types)
        self.assertEqual(req.allowed_content_types, types)

    def testAllowedContentTypesWildcardString(self) -> None:
        """
        Accept the literal string '*' for allowed_content_types.

        Verifies that the wildcard sentinel is accepted and stored
        unchanged.

        Returns
        -------
        None
            This method does not return a value.
        """
        req = HTTPRequest(allowed_content_types="*")
        self.assertEqual(req.allowed_content_types, "*")

    def testCustomMaxContentLength(self) -> None:
        """
        Accept a custom positive integer for max_content_length.

        Verifies that a specific byte limit is stored on the
        HTTPRequest instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        req = HTTPRequest(max_content_length=1024)
        self.assertEqual(req.max_content_length, 1024)

    def testMaxContentLengthNone(self) -> None:
        """
        Accept None for max_content_length.

        Verifies that disabling the body size limit by passing None is
        supported without raising an error.

        Returns
        -------
        None
            This method does not return a value.
        """
        req = HTTPRequest(max_content_length=None)
        self.assertIsNone(req.max_content_length)

    def testCustomEnableMethodOverrideFalse(self) -> None:
        """
        Accept False for enable_method_override.

        Verifies that disabling the method override feature is stored
        on the HTTPRequest instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        req = HTTPRequest(enable_method_override=False)
        self.assertFalse(req.enable_method_override)

    def testCustomMethodOverrideHeader(self) -> None:
        """
        Accept a custom string for method_override_header.

        Verifies that an alternative header name for method override
        is stored on the HTTPRequest instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        req = HTTPRequest(method_override_header="x-method-override")
        self.assertEqual(req.method_override_header, "x-method-override")

    def testInvalidAllowedContentTypesTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when allowed_content_types is neither a list nor '*'.

        Verifies that an integer value for allowed_content_types
        triggers a TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPRequest(allowed_content_types=123)  # type: ignore[arg-type]

    def testNonStringInAllowedContentTypesRaisesTypeError(self) -> None:
        """
        Raise TypeError when allowed_content_types list has non-string items.

        Verifies that a list containing integers triggers a TypeError
        during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPRequest(
                allowed_content_types=[123]  # type: ignore[list-item]
            )

    def testInvalidMaxContentLengthTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when max_content_length is not an integer or None.

        Verifies that a string value triggers a TypeError during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPRequest(max_content_length="10mb")  # type: ignore[arg-type]

    def testBoolAsMaxContentLengthRaisesTypeError(self) -> None:
        """
        Raise TypeError when max_content_length is a boolean.

        Verifies that bool values are rejected even though bool is a
        subclass of int in Python.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPRequest(max_content_length=True)  # type: ignore[arg-type]

    def testMaxContentLengthZeroRaisesValueError(self) -> None:
        """
        Raise ValueError when max_content_length is zero.

        Verifies that a zero-byte limit is rejected as a non-positive
        integer.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            HTTPRequest(max_content_length=0)

    def testMaxContentLengthNegativeRaisesValueError(self) -> None:
        """
        Raise ValueError when max_content_length is negative.

        Verifies that a negative byte limit is rejected during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            HTTPRequest(max_content_length=-1)

    def testInvalidEnableMethodOverrideTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when enable_method_override is not a boolean.

        Verifies that a string value triggers a TypeError during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPRequest(
                enable_method_override="yes"  # type: ignore[arg-type]
            )

    def testInvalidMethodOverrideHeaderTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when method_override_header is not a string.

        Verifies that an integer value for the header name triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPRequest(
                method_override_header=123  # type: ignore[arg-type]
            )

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Raise FrozenInstanceError when mutating an HTTPRequest instance.

        Confirms the dataclass is immutable and rejects attribute
        reassignment after construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        req = HTTPRequest()
        with self.assertRaises(FrozenInstanceError):
            req.allowed_content_types = ["text/html"]  # type: ignore[misc]
