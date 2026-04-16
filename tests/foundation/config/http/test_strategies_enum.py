from orionis.test import TestCase
from orionis.foundation.config.http.enums.strategies import ProxyStrategy

# ===========================================================================
# ProxyStrategy enum
# ===========================================================================


class TestProxyStrategyEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Verify all expected ProxyStrategy members are defined.

        Checks that each canonical proxy strategy name is present
        in the enumeration's member registry.

        Returns
        -------
        None
            This method does not return a value.
        """
        expected = {"STANDARD", "NGINX", "CLOUDFLARE", "AWS", "FASTLY"}
        for name in expected:
            self.assertIn(name, ProxyStrategy._member_names_)

    def testMemberValues(self) -> None:
        """
        Verify the string values assigned to each ProxyStrategy member.

        Ensures that each enum member holds the expected lowercase
        string value used for configuration and environment variable
        resolution.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(ProxyStrategy.STANDARD.value, "standard")
        self.assertEqual(ProxyStrategy.NGINX.value, "nginx")
        self.assertEqual(ProxyStrategy.CLOUDFLARE.value, "cloudflare")
        self.assertEqual(ProxyStrategy.AWS.value, "aws")
        self.assertEqual(ProxyStrategy.FASTLY.value, "fastly")

    def testIsStrEnum(self) -> None:
        """
        Verify ProxyStrategy inherits from StrEnum.

        Confirms that each member behaves as a plain string, allowing
        direct comparison with string literals without calling .value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(ProxyStrategy.STANDARD, "standard")
        self.assertEqual(ProxyStrategy.NGINX, "nginx")

    def testLookupByName(self) -> None:
        """
        Retrieve ProxyStrategy members by name using bracket notation.

        Validates that the standard dictionary-style lookup returns
        the correct enum member for each registered name.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(ProxyStrategy["STANDARD"], ProxyStrategy.STANDARD)
        self.assertIs(ProxyStrategy["AWS"], ProxyStrategy.AWS)

    def testIterationYieldsAllMembers(self) -> None:
        """
        Verify iterating over ProxyStrategy yields exactly five members.

        Ensures no members have been added or removed from the
        enumeration without updating this test.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(list(ProxyStrategy)), 5)
