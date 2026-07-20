from orionis.test import TestCase
from orionis.test.enums.status import TestStatus

class TestTestStatus(TestCase):

    # ------------------------------------------------ member existence

    def testPassedMemberExists(self):
        """
        Confirm that the PASSED member exists in TestStatus.

        Validates that accessing TestStatus.PASSED does not raise an
        AttributeError and returns a valid member.
        """
        self.assertIn(TestStatus.PASSED, TestStatus)

    def testFailedMemberExists(self):
        """
        Confirm that the FAILED member exists in TestStatus.

        Validates that accessing TestStatus.FAILED does not raise
        an AttributeError and returns a valid member.
        """
        self.assertIn(TestStatus.FAILED, TestStatus)

    def testErroredMemberExists(self):
        """
        Confirm that the ERRORED member exists in TestStatus.

        Validates that accessing TestStatus.ERRORED does not raise
        an AttributeError and returns a valid member.
        """
        self.assertIn(TestStatus.ERRORED, TestStatus)

    def testSkippedMemberExists(self):
        """
        Confirm that the SKIPPED member exists in TestStatus.

        Validates that accessing TestStatus.SKIPPED does not raise
        an AttributeError and returns a valid member.
        """
        self.assertIn(TestStatus.SKIPPED, TestStatus)

    # ------------------------------------------------ exact four members

    def testEnumerationHasExactlyFourMembers(self):
        """
        Confirm that TestStatus contains exactly four members.

        Validates that no unintended members have been added to the
        enumeration beyond the four documented ones.
        """
        self.assertEqual(len(TestStatus), 4)

    # ------------------------------------------------ string values

    def testPassedValueIsUpperCaseString(self):
        """
        Confirm the PASSED member value equals the uppercase string 'PASSED'.

        Validates that StrEnum assigns the correct string value to
        the PASSED member.
        """
        self.assertEqual(TestStatus.PASSED, "PASSED")

    def testFailedValueIsUpperCaseString(self):
        """
        Confirm the FAILED member value equals the uppercase string 'FAILED'.

        Validates that StrEnum assigns the correct string value to
        the FAILED member.
        """
        self.assertEqual(TestStatus.FAILED, "FAILED")

    def testErroredValueIsUpperCaseString(self):
        """
        Confirm the ERRORED member value equals the uppercase string 'ERRORED'.

        Validates that StrEnum assigns the correct string value to
        the ERRORED member.
        """
        self.assertEqual(TestStatus.ERRORED, "ERRORED")

    def testSkippedValueIsUpperCaseString(self):
        """
        Confirm the SKIPPED member value equals the uppercase string 'SKIPPED'.

        Validates that StrEnum assigns the correct string value to
        the SKIPPED member.
        """
        self.assertEqual(TestStatus.SKIPPED, "SKIPPED")

    # ------------------------------------------------ StrEnum behaviour

    def testMembersAreInstancesOfStr(self):
        """
        Confirm that all TestStatus members are also str instances.

        Validates that TestStatus inherits from StrEnum properly,
        making each member usable as a plain string.
        """
        for member in TestStatus:
            self.assertIsInstance(member, str)

    def testPassedCanBeComparedToPlainString(self):
        """
        Compare PASSED directly with its equivalent plain string.

        Validates the StrEnum equality contract so that members behave
        like strings in conditional comparisons.
        """
        self.assertTrue(TestStatus.PASSED == "PASSED")

    def testMemberLookupByValue(self):
        """
        Retrieve a TestStatus member by its string value.

        Validates that TestStatus("FAILED") returns the FAILED member,
        confirming standard enum value-lookup behaviour.
        """
        result = TestStatus("FAILED")
        self.assertIs(result, TestStatus.FAILED)

    def testMemberNamesMatchValues(self):
        """
        Confirm that each member's name matches its string value.

        Validates the consistency between the Python identifier name
        and the underlying string value for every member.
        """
        for member in TestStatus:
            self.assertEqual(member.name, member.value)

    # ------------------------------------------------ iteration and ordering

    def testAllExpectedMembersInIteration(self):
        """
        Confirm all four expected members appear during iteration.

        Validates that iterating over TestStatus yields exactly the
        four documented members in any order.
        """
        members = set(TestStatus)
        self.assertEqual(
            members,
            {
                TestStatus.PASSED,
                TestStatus.FAILED,
                TestStatus.ERRORED,
                TestStatus.SKIPPED,
            },
        )
