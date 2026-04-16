from dataclasses import FrozenInstanceError
from orionis.test import TestCase
from orionis.foundation.config.http.entitites.proxies import HTTPProxies
from orionis.foundation.config.http.entitites.proxy_strategy import (
    ProxyStrategy as ProxyStrategyEntity,
)
from orionis.foundation.config.http.enums.strategies import ProxyStrategy

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

    def testDefaultProxyStrategyIsString(self) -> None:
        """
        Verify proxy_strategy is coerced to a string after init.

        Confirms that the validation step normalises the enum default
        to its string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIsInstance(HTTPProxies().proxy_strategy, str)

    def testDefaultProxyStrategiesHasExpectedKeys(self) -> None:
        """
        Verify proxy_strategies contains the five built-in strategy keys.

        Ensures the default mapping includes entries for standard,
        nginx, cloudflare, aws, and fastly.

        Returns
        -------
        None
            This method does not return a value.
        """
        strategies = HTTPProxies().proxy_strategies
        for key in ("standard", "nginx", "cloudflare", "aws", "fastly"):
            self.assertIn(key, strategies)

    def testDefaultProxyStrategiesValuesAreEntities(self) -> None:
        """
        Verify each value in proxy_strategies is a ProxyStrategyEntity.

        Ensures all built-in strategy entries hold properly typed
        entity instances.

        Returns
        -------
        None
            This method does not return a value.
        """
        for val in HTTPProxies().proxy_strategies.values():
            self.assertIsInstance(val, ProxyStrategyEntity)

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

    def testCustomProxyStrategyAsString(self) -> None:
        """
        Accept a valid lowercase strategy string for proxy_strategy.

        Verifies that a string matching a ProxyStrategy member name
        (case-insensitive) is accepted and stored as a string.

        Returns
        -------
        None
            This method does not return a value.
        """
        proxies = HTTPProxies(proxy_strategy="nginx")
        self.assertEqual(proxies.proxy_strategy, "nginx")

    def testCustomProxyStrategyAsEnum(self) -> None:
        """
        Accept a ProxyStrategy enum member for proxy_strategy.

        Verifies that an enum member is coerced to its string value
        after validation.

        Returns
        -------
        None
            This method does not return a value.
        """
        proxies = HTTPProxies(proxy_strategy=ProxyStrategy.CLOUDFLARE)
        self.assertEqual(proxies.proxy_strategy, "cloudflare")

    def testProxyStrategiesDictCoercion(self) -> None:
        """
        Coerce dict entries in proxy_strategies to ProxyStrategyEntity.

        Verifies that providing a strategy value as a plain dict results
        in a ProxyStrategyEntity instance on the stored mapping.

        Returns
        -------
        None
            This method does not return a value.
        """
        custom = {
            "custom": {
                "ip_header": "x-custom-ip",
                "proto_header": "x-custom-proto",
            }
        }
        proxies = HTTPProxies(proxy_strategies=custom)
        self.assertIsInstance(
            proxies.proxy_strategies["custom"], ProxyStrategyEntity
        )

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

    def testInvalidProxyStrategyTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when proxy_strategy is not a string or enum.

        Verifies that an integer value for proxy_strategy triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPProxies(proxy_strategy=123)  # type: ignore[arg-type]

    def testInvalidProxyStrategyValueRaisesValueError(self) -> None:
        """
        Raise ValueError when proxy_strategy string has no matching member.

        Verifies that an unrecognised strategy name triggers a
        ValueError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            HTTPProxies(proxy_strategy="unknown_strategy")

    def testInvalidProxyStrategiesTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when proxy_strategies is not a dict.

        Verifies that a non-dict value for proxy_strategies triggers a
        TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(TypeError):
            HTTPProxies(proxy_strategies="bad")  # type: ignore[arg-type]

    def testInvalidProxyStrategiesKeyTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when a proxy_strategies key is not a string.

        Verifies that non-string dictionary keys trigger a TypeError
        during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        bad = {
            123: ProxyStrategyEntity(
                ip_header="x-forwarded-for",
                proto_header="x-forwarded-proto",
            )
        }
        with self.assertRaises(TypeError):
            HTTPProxies(proxy_strategies=bad)  # type: ignore[arg-type]

    def testInvalidProxyStrategiesValueTypeRaisesTypeError(self) -> None:
        """
        Raise TypeError when a proxy_strategies value is an invalid type.

        Verifies that a value that is neither a ProxyStrategyEntity nor
        a dict triggers a TypeError during construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        bad = {"custom": 42}
        with self.assertRaises(TypeError):
            HTTPProxies(proxy_strategies=bad)  # type: ignore[arg-type]

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
