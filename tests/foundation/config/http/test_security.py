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

    def testCustomAllowedHostsWithWildcardSubdomain(self) -> None:
        """
        Accept wildcard subdomain patterns in allowed_hosts.

        Verifies that entries such as '*.example.com' are stored
        unchanged on the HTTPSecurity instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        hosts = ["*.example.com"]
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
            sec.allowed_hosts = ["localhost"]  # type: ignore[misc]
