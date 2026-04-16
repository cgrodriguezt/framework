from dataclasses import FrozenInstanceError
from orionis.test import TestCase
from orionis.foundation.config.http.entitites.security import HTTPSecurity

# ===========================================================================
# HTTPSecurity entity
# ===========================================================================


class TestHTTPSecurity(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Construct HTTPSecurity with all default values.

        Verifies that an HTTPSecurity instance can be created without
        providing any arguments.

        Returns
        -------
        None
            This method does not return a value.
        """
        sec = HTTPSecurity()
        self.assertIsInstance(sec, HTTPSecurity)

    def testDefaultValidateHeadersIsTrue(self) -> None:
        """
        Verify validate_headers defaults to True.

        Ensures header validation is enabled by default, protecting
        against CRLF injection and header duplication.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(HTTPSecurity().validate_headers)

    def testDefaultMaxHeaderSizeIs8192(self) -> None:
        """
        Verify max_header_size defaults to 8192 bytes.

        Ensures the default per-header size cap equals 8 KB.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(HTTPSecurity().max_header_size, 8192)

    def testDefaultBlockMultipleHostHeadersIsTrue(self) -> None:
        """
        Verify block_multiple_host_headers defaults to True.

        Ensures that requests with duplicate Host headers are blocked
        by default as a security measure.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertTrue(HTTPSecurity().block_multiple_host_headers)

    def testDefaultAllowedHostsIsWildcard(self) -> None:
        """
        Verify allowed_hosts defaults to the wildcard string.

        Ensures all host names are permitted by default.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(HTTPSecurity().allowed_hosts, "*")

    def testCustomValidateHeadersFalse(self) -> None:
        """
        Accept False for validate_headers.

        Verifies that disabling header validation is stored on the
        HTTPSecurity instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        sec = HTTPSecurity(validate_headers=False)
        self.assertFalse(sec.validate_headers)

    def testCustomMaxHeaderSize(self) -> None:
        """
        Accept a custom positive integer for max_header_size.

        Verifies that a specific byte cap for individual headers is
        stored on the HTTPSecurity instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        sec = HTTPSecurity(max_header_size=4096)
        self.assertEqual(sec.max_header_size, 4096)

    def testCustomBlockMultipleHostHeadersFalse(self) -> None:
        """
        Accept False for block_multiple_host_headers.

        Verifies that disabling the multiple-host-header guard is
        stored on the HTTPSecurity instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        sec = HTTPSecurity(block_multiple_host_headers=False)
        self.assertFalse(sec.block_multiple_host_headers)

    def testCustomAllowedHostsList(self) -> None:
        """
        Accept a list of host strings for allowed_hosts.

        Verifies that a specific host allowlist is stored on the
        HTTPSecurity instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        hosts = ["localhost", "example.com"]
        sec = HTTPSecurity(allowed_hosts=hosts)
        self.assertEqual(sec.allowed_hosts, hosts)

    def testCustomAllowedHostsWildcard(self) -> None:
        """
        Accept the literal string '*' for allowed_hosts.

        Verifies that the wildcard sentinel is accepted and stored
        unchanged.

        Returns
        -------
        None
            This method does not return a value.
        """
        sec = HTTPSecurity(allowed_hosts="*")
        self.assertEqual(sec.allowed_hosts, "*")

    def testInvalidValidateHeadersTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when validate_headers is not a boolean.

        Verifies that a string value triggers a TypeError during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPSecurity(validate_headers="yes")  # type: ignore[arg-type]

    def testInvalidMaxHeaderSizeTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when max_header_size is not an integer.

        Verifies that a string value for max_header_size triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPSecurity(max_header_size="8192")  # type: ignore[arg-type]

    def testBoolAsMaxHeaderSizeRaisesTypeError(self) -> None:
        """
        Raise TypeError when max_header_size is a boolean.

        Verifies that bool values are rejected even though bool is a
        subclass of int in Python.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPSecurity(max_header_size=True)  # type: ignore[arg-type]

    def testMaxHeaderSizeZeroRaisesValueError(self) -> None:
        """
        Raise ValueError when max_header_size is zero.

        Verifies that a zero-byte header size limit is rejected as
        non-positive.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            HTTPSecurity(max_header_size=0)

    def testMaxHeaderSizeNegativeRaisesValueError(self) -> None:
        """
        Raise ValueError when max_header_size is negative.

        Verifies that a negative header size limit is rejected during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            HTTPSecurity(max_header_size=-1)

    def testInvalidBlockMultipleHostHeadersTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when block_multiple_host_headers is not a boolean.

        Verifies that an integer value triggers a TypeError during
        construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPSecurity(
                block_multiple_host_headers=1  # type: ignore[arg-type]
            )

    def testInvalidAllowedHostsTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when allowed_hosts is not a list or '*'.

        Verifies that an integer value for allowed_hosts triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPSecurity(allowed_hosts=123)  # type: ignore[arg-type]

    def testNonStringInAllowedHostsRaisesTypeError(self) -> None:
        """
        Raise TypeError when allowed_hosts list contains a non-string item.

        Verifies that a list with integer entries triggers a TypeError
        during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPSecurity(allowed_hosts=[123])  # type: ignore[list-item]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Raise FrozenInstanceError when mutating an HTTPSecurity instance.

        Confirms the dataclass is immutable and rejects attribute
        reassignment after construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        sec = HTTPSecurity()
        with self.assertRaises(FrozenInstanceError):
            sec.validate_headers = False  # type: ignore[misc]
