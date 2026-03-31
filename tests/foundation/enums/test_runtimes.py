from orionis.test import TestCase
from orionis.foundation.enums.runtimes import Runtime

# ===========================================================================
# Runtime enum
# ===========================================================================

class TestRuntimeEnum(TestCase):

    def testMembersExist(self) -> None:
        """
        Test that HTTP and CLI members are present in Runtime.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("HTTP", Runtime._member_names_)
        self.assertIn("CLI", Runtime._member_names_)

    def testMemberCount(self) -> None:
        """
        Test that Runtime has exactly two members.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(Runtime), 2)

    def testHttpValue(self) -> None:
        """
        Test that HTTP has the expected string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Runtime.HTTP.value, "http")

    def testCliValue(self) -> None:
        """
        Test that CLI has the expected string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Runtime.CLI.value, "cli")

    def testLookupByName(self) -> None:
        """
        Test that members can be retrieved by name via bracket notation.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Runtime["HTTP"], Runtime.HTTP)
        self.assertIs(Runtime["CLI"], Runtime.CLI)

    def testLookupByValue(self) -> None:
        """
        Test that members can be retrieved by their string value.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Runtime("http"), Runtime.HTTP)
        self.assertIs(Runtime("cli"), Runtime.CLI)

    def testStrEnumBehavior(self) -> None:
        """
        Test that Runtime members behave as regular strings.

        As a StrEnum, each member should compare equal to its string value
        and be usable anywhere a str is expected.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Runtime.HTTP, "http")
        self.assertEqual(Runtime.CLI, "cli")
        self.assertIsInstance(Runtime.HTTP, str)
        self.assertIsInstance(Runtime.CLI, str)

    def testIteration(self) -> None:
        """
        Test that iterating over Runtime yields all members in definition order.

        Returns
        -------
        None
            This method does not return a value.
        """
        members = list(Runtime)
        self.assertEqual(members, [Runtime.HTTP, Runtime.CLI])

    def testIsHashable(self) -> None:
        """
        Test that Runtime members are hashable and can be used as dict keys.

        Returns
        -------
        None
            This method does not return a value.
        """
        routing = {Runtime.HTTP: "web", Runtime.CLI: "console"}
        self.assertEqual(routing[Runtime.HTTP], "web")
        self.assertEqual(routing[Runtime.CLI], "console")

    def testMemberContainment(self) -> None:
        """
        Test that membership check works with Runtime members.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn(Runtime.HTTP, Runtime)
        self.assertIn(Runtime.CLI, Runtime)

    def testValuesAreDistinct(self) -> None:
        """
        Test that HTTP and CLI have different string values.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertNotEqual(Runtime.HTTP.value, Runtime.CLI.value)

    def testUnknownNameRaisesKeyError(self) -> None:
        """
        Test that accessing a non-existent name raises KeyError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(KeyError):
            _ = Runtime["GRPC"]

    def testUnknownValueRaisesValueError(self) -> None:
        """
        Test that looking up a non-existent value raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            _ = Runtime("websocket")
