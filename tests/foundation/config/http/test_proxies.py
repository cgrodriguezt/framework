from dataclasses import FrozenInstanceError
from orionis.test import TestCase
from orionis.foundation.config.http.entitites.proxies import HTTPProxies

# ===========================================================================
# HTTPProxies entity
# ===========================================================================


class TestHTTPProxies(TestCase):

    def testDefaultConstruction(self) -> None:
        """
        Construct HTTPProxies with all default values.

        Verifies that an HTTPProxies instance can be created without
        providing any arguments.

        Returns
        -------
        None
            This method does not return a value.
        """
        proxies = HTTPProxies()
        self.assertIsInstance(proxies, HTTPProxies)

    def testDefaultTrustedProxiesIsList(self) -> None:
        """
        Verify trusted_proxies defaults to a list.

        Ensures the default value is a list (empty when the
        environment variable is not set).

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(HTTPProxies().trusted_proxies, list)

    def testCustomTrustedProxies(self) -> None:
        """
        Accept a list of IP strings for trusted_proxies.

        Verifies that an explicit list of proxy addresses is stored
        unchanged on the HTTPProxies instance.

        Returns
        -------
        None
            This method does not return a value.
        """
        ips = ["10.0.0.1", "192.168.1.0/24"]
        proxies = HTTPProxies(trusted_proxies=ips)
        self.assertEqual(proxies.trusted_proxies, ips)

    def testInvalidTrustedProxiesTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when trusted_proxies is not a list.

        Verifies that a string or other non-list type triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPProxies(trusted_proxies="10.0.0.1")  # type: ignore[arg-type]

    def testNonStringInTrustedProxiesRaisesTypeError(self) -> None:
        """
        Raise TypeError when trusted_proxies contains a non-string item.

        Verifies that a list with integer entries triggers a TypeError
        during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPProxies(trusted_proxies=[192])  # type: ignore[list-item]

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Raise FrozenInstanceError when mutating an HTTPProxies instance.

        Confirms the dataclass is immutable and rejects attribute
        reassignment after construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        proxies = HTTPProxies()
        with self.assertRaises(FrozenInstanceError):
            proxies.trusted_proxies = ["10.0.0.1"]  # type: ignore[misc]
