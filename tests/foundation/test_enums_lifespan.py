from orionis.test import TestCase
from orionis.foundation.enums.lifespan import Lifespan

# ===========================================================================
# Lifespan enum
# ===========================================================================

class TestLifespanEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that STARTUP and SHUTDOWN members are present in Lifespan.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("STARTUP", Lifespan._member_names_)
        self.assertIn("SHUTDOWN", Lifespan._member_names_)

    def testMemberCount(self) -> None:
        """
        Test that Lifespan has exactly two members.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(Lifespan), 2)

    def testStartupValue(self) -> None:
        """
        Test that STARTUP has the expected string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Lifespan.STARTUP.value, "lifespan.startup")

    def testShutdownValue(self) -> None:
        """
        Test that SHUTDOWN has the expected string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Lifespan.SHUTDOWN.value, "lifespan.shutdown")

    def testLookupByName(self) -> None:
        """
        Test that members can be retrieved by name via bracket notation.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Lifespan["STARTUP"], Lifespan.STARTUP)
        self.assertIs(Lifespan["SHUTDOWN"], Lifespan.SHUTDOWN)

    def testLookupByValue(self) -> None:
        """
        Test that members can be retrieved by their string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Lifespan("lifespan.startup"), Lifespan.STARTUP)
        self.assertIs(Lifespan("lifespan.shutdown"), Lifespan.SHUTDOWN)

    def testStrEnumBehavior(self) -> None:
        """
        Test that Lifespan members behave as regular strings.

        As a StrEnum, each member should compare equal to its string value
        and be usable anywhere a str is expected.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Lifespan.STARTUP, "lifespan.startup")
        self.assertEqual(Lifespan.SHUTDOWN, "lifespan.shutdown")
        self.assertIsInstance(Lifespan.STARTUP, str)
        self.assertIsInstance(Lifespan.SHUTDOWN, str)

    def testIteration(self) -> None:
        """
        Test that iterating over Lifespan yields all members in definition order.

        Returns
        -------
        None
            This method does not return a value.
        """
        members = list(Lifespan)
        self.assertEqual(members, [Lifespan.STARTUP, Lifespan.SHUTDOWN])

    def testIsHashable(self) -> None:
        """
        Test that Lifespan members are hashable and can be used as dict keys.

        Returns
        -------
        None
            This method does not return a value.
        """
        mapping = {Lifespan.STARTUP: "start", Lifespan.SHUTDOWN: "stop"}
        self.assertEqual(mapping[Lifespan.STARTUP], "start")
        self.assertEqual(mapping[Lifespan.SHUTDOWN], "stop")

    def testMemberContainment(self) -> None:
        """
        Test that membership check works with Lifespan members.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn(Lifespan.STARTUP, Lifespan)
        self.assertIn(Lifespan.SHUTDOWN, Lifespan)

    def testUnknownNameRaisesKeyError(self) -> None:
        """
        Test that accessing a non-existent name raises KeyError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(KeyError):
            _ = Lifespan["UNKNOWN"]

    def testUnknownValueRaisesValueError(self) -> None:
        """
        Test that looking up a non-existent value raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            _ = Lifespan("invalid.event")
