from dataclasses import FrozenInstanceError
from orionis.test import TestCase
from orionis.foundation.config.http.entitites.proxy_strategy import (
    ProxyStrategy as ProxyStrategyEntity,
)

# ===========================================================================
# ProxyStrategy entity
# ===========================================================================


class TestProxyStrategyEntity(TestCase):

    def testConstruction(self) -> None:
        """
        Construct a ProxyStrategyEntity with valid header names.

        Verifies that the dataclass accepts ``ip_header`` and
        ``proto_header`` positional keyword arguments without error.

        Returns
        -------
        None
            This method does not return a value.
        """
        entity = ProxyStrategyEntity(
            ip_header="x-forwarded-for",
            proto_header="x-forwarded-proto",
        )
        self.assertIsInstance(entity, ProxyStrategyEntity)

    def testIpHeaderStored(self) -> None:
        """
        Verify the ip_header attribute is stored correctly.

        Ensures the provided header name is accessible on the
        entity instance after construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        entity = ProxyStrategyEntity(
            ip_header="cf-connecting-ip",
            proto_header="x-forwarded-proto",
        )
        self.assertEqual(entity.ip_header, "cf-connecting-ip")

    def testProtoHeaderStored(self) -> None:
        """
        Verify the proto_header attribute is stored correctly.

        Ensures the protocol header name is accessible on the
        entity instance after construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        entity = ProxyStrategyEntity(
            ip_header="x-real-ip",
            proto_header="x-forwarded-proto",
        )
        self.assertEqual(entity.proto_header, "x-forwarded-proto")

    def testFrozenRaisesAttributeError(self) -> None:
        """
        Verify mutating a ProxyStrategyEntity raises FrozenInstanceError.

        Confirms that the dataclass is immutable and rejects any
        attempt to reassign an attribute after construction.

        Returns
        -------
        None
            This method does not return a value.
        """
        entity = ProxyStrategyEntity(
            ip_header="x-forwarded-for",
            proto_header="x-forwarded-proto",
        )
        with self.assertRaises(FrozenInstanceError):
            entity.ip_header = "changed"  # type: ignore[misc]
