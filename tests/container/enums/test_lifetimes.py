from __future__ import annotations
from orionis.test import TestCase
from orionis.container.enums.lifetimes import Lifetime

class TestLifetime(TestCase):

    # ------------------------------------------------------------------
    # Member existence
    # ------------------------------------------------------------------

    def testAllMembersExist(self) -> None:
        """
        Test that all expected members are present in the Lifetime enum.

        Verifies that TRANSIENT, SINGLETON, and SCOPED are defined so that
        any accidental removal is caught immediately.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIn("TRANSIENT", Lifetime.__members__)
        self.assertIn("SINGLETON", Lifetime.__members__)
        self.assertIn("SCOPED", Lifetime.__members__)

    def testExactMemberCount(self) -> None:
        """
        Test that the Lifetime enum contains exactly three members.

        Ensures that no undocumented members have been added or that no
        existing member has been silently removed.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(len(Lifetime), 3)

    # ------------------------------------------------------------------
    # Identity and type
    # ------------------------------------------------------------------

    def testMembersAreLifetimeInstances(self) -> None:
        """
        Test that each member is an instance of the Lifetime enum class.

        Returns
        -------
        None
            This method does not return a value.
        """
        for member in Lifetime:
            self.assertIsInstance(member, Lifetime)

    def testMembersAreEnumInstances(self) -> None:
        """
        Test that each Lifetime member is also an instance of the base Enum class.

        Returns
        -------
        None
            This method does not return a value.
        """
        from enum import Enum
        for member in Lifetime:
            self.assertIsInstance(member, Enum)

    def testMembersHaveIntegerValues(self) -> None:
        """
        Test that every Lifetime member's value is an integer (produced by auto()).

        Returns
        -------
        None
            This method does not return a value.
        """
        for member in Lifetime:
            self.assertIsInstance(member.value, int)

    # ------------------------------------------------------------------
    # Value ordering (auto() assigns sequential integers starting at 1)
    # ------------------------------------------------------------------

    def testTransientValueIsOne(self) -> None:
        """
        Test that TRANSIENT is assigned the first auto() value (1).

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Lifetime.TRANSIENT.value, 1)

    def testSingletonValueIsTwo(self) -> None:
        """
        Test that SINGLETON is assigned the second auto() value (2).

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Lifetime.SINGLETON.value, 2)

    def testScopedValueIsThree(self) -> None:
        """
        Test that SCOPED is assigned the third auto() value (3).

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Lifetime.SCOPED.value, 3)

    def testValuesAreUnique(self) -> None:
        """
        Test that all Lifetime members have distinct integer values.

        Returns
        -------
        None
            This method does not return a value.
        """
        values = [m.value for m in Lifetime]
        self.assertEqual(len(values), len(set(values)))

    # ------------------------------------------------------------------
    # Name attribute
    # ------------------------------------------------------------------

    def testMemberNamesMatchExpected(self) -> None:
        """
        Test that each member's name attribute equals its declared identifier.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertEqual(Lifetime.TRANSIENT.name, "TRANSIENT")
        self.assertEqual(Lifetime.SINGLETON.name, "SINGLETON")
        self.assertEqual(Lifetime.SCOPED.name, "SCOPED")

    # ------------------------------------------------------------------
    # Lookup by value
    # ------------------------------------------------------------------

    def testLookupByValueReturnsCorrectMember(self) -> None:
        """
        Test that constructing a Lifetime from an integer value returns the correct member.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Lifetime(1), Lifetime.TRANSIENT)
        self.assertIs(Lifetime(2), Lifetime.SINGLETON)
        self.assertIs(Lifetime(3), Lifetime.SCOPED)

    def testLookupByNameReturnsCorrectMember(self) -> None:
        """
        Test that accessing a Lifetime member via Lifetime['NAME'] returns the correct member.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Lifetime["TRANSIENT"], Lifetime.TRANSIENT)
        self.assertIs(Lifetime["SINGLETON"], Lifetime.SINGLETON)
        self.assertIs(Lifetime["SCOPED"], Lifetime.SCOPED)

    def testInvalidValueRaisesValueError(self) -> None:
        """
        Test that constructing a Lifetime from an unknown integer raises ValueError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(ValueError):
            Lifetime(0)

    def testInvalidNameRaisesKeyError(self) -> None:
        """
        Test that accessing a Lifetime member with an unknown name raises KeyError.

        Returns
        -------
        None
            This method does not return a value.
        """
        with self.assertRaises(KeyError):
            _ = Lifetime["UNKNOWN"]

    # ------------------------------------------------------------------
    # Equality and identity
    # ------------------------------------------------------------------

    def testSameMemberIsIdentical(self) -> None:
        """
        Test that two references to the same Lifetime member are the same object (is).

        Enum members are singletons, so identity must hold.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertIs(Lifetime.TRANSIENT, Lifetime.TRANSIENT)
        self.assertIs(Lifetime.SINGLETON, Lifetime.SINGLETON)
        self.assertIs(Lifetime.SCOPED, Lifetime.SCOPED)

    def testDifferentMembersAreNotEqual(self) -> None:
        """
        Test that distinct Lifetime members compare as not equal.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.assertNotEqual(Lifetime.TRANSIENT, Lifetime.SINGLETON)
        self.assertNotEqual(Lifetime.SINGLETON, Lifetime.SCOPED)
        self.assertNotEqual(Lifetime.TRANSIENT, Lifetime.SCOPED)

    # ------------------------------------------------------------------
    # Hashability (usefulness as dict key / set member)
    # ------------------------------------------------------------------

    def testMembersAreHashable(self) -> None:
        """
        Test that Lifetime members can be used as dictionary keys and set elements.

        Returns
        -------
        None
            This method does not return a value.
        """
        mapping = {lt: lt.name for lt in Lifetime}
        self.assertEqual(mapping[Lifetime.TRANSIENT], "TRANSIENT")
        self.assertEqual(mapping[Lifetime.SINGLETON], "SINGLETON")
        self.assertEqual(mapping[Lifetime.SCOPED], "SCOPED")

        as_set = set(Lifetime)
        self.assertEqual(len(as_set), 3)

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def testIterationYieldsAllThreeMembers(self) -> None:
        """
        Test that iterating over Lifetime yields exactly the three expected members.

        Returns
        -------
        None
            This method does not return a value.
        """
        members = list(Lifetime)
        self.assertIn(Lifetime.TRANSIENT, members)
        self.assertIn(Lifetime.SINGLETON, members)
        self.assertIn(Lifetime.SCOPED, members)
        self.assertEqual(len(members), 3)

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    def testStrRepresentationContainsMemberName(self) -> None:
        """
        Test that str() of a Lifetime member includes the member's name.

        Returns
        -------
        None
            This method does not return a value.
        """
        for member in Lifetime:
            self.assertIn(member.name, str(member))

    def testReprContainsClassAndName(self) -> None:
        """
        Test that repr() of a Lifetime member contains both the class name and the member name.

        Returns
        -------
        None
            This method does not return a value.
        """
        for member in Lifetime:
            r = repr(member)
            self.assertIn("Lifetime", r)
            self.assertIn(member.name, r)
