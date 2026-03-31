from __future__ import annotations
from enum import Enum
from orionis.console.enums.states import ScheduleStates
from orionis.test import TestCase

class TestScheduleStates(TestCase):

    # ------------------------------------------------------------------ #
    #  Type & membership                                                 #
    # ------------------------------------------------------------------ #

    def testIsEnumSubclass(self) -> None:
        """
        Verify that ScheduleStates is a subclass of Enum.

        Ensures the class participates in Python's standard enum
        machinery and supports membership, iteration, and value lookup.
        """
        self.assertTrue(issubclass(ScheduleStates, Enum))

    def testHasExpectedMemberCount(self) -> None:
        """
        Verify that ScheduleStates defines exactly three members.

        Ensures no states have been accidentally added or removed from
        the enum definition.
        """
        self.assertEqual(len(ScheduleStates), 3)

    def testAllMembersHaveStringValues(self) -> None:
        """
        Verify that every member value is a string.

        Ensures the enum values can be used directly for string
        comparison or serialisation without conversion.
        """
        for member in ScheduleStates:
            self.assertIsInstance(member.value, str)

    # ------------------------------------------------------------------ #
    #  Individual member values                                          #
    # ------------------------------------------------------------------ #

    def testStoppedValue(self) -> None:
        """
        Verify that STOPPED has the value 'STOPPED'.

        Ensures the string representation is uppercase and consistent
        with the declared enum definition.
        """
        self.assertEqual(ScheduleStates.STOPPED.value, "STOPPED")

    def testRunningValue(self) -> None:
        """
        Verify that RUNNING has the value 'RUNNING'.

        Ensures the string representation is uppercase and consistent
        with the declared enum definition.
        """
        self.assertEqual(ScheduleStates.RUNNING.value, "RUNNING")

    def testPausedValue(self) -> None:
        """
        Verify that PAUSED has the value 'PAUSED'.

        Ensures the string representation is uppercase and consistent
        with the declared enum definition.
        """
        self.assertEqual(ScheduleStates.PAUSED.value, "PAUSED")

    # ------------------------------------------------------------------ #
    #  Lookup                                                            #
    # ------------------------------------------------------------------ #

    def testLookupByValue(self) -> None:
        """
        Verify that members can be retrieved by their string value.

        Ensures ScheduleStates('RUNNING') returns ScheduleStates.RUNNING,
        enabling reverse-lookup from serialised state strings.
        """
        self.assertIs(ScheduleStates("RUNNING"), ScheduleStates.RUNNING)

    def testLookupInvalidValueRaisesValueError(self) -> None:
        """
        Verify that looking up an unknown string raises ValueError.

        Ensures the enum rejects any string not defined as a member
        value, preventing silent misuse.
        """
        with self.assertRaises(ValueError):
            ScheduleStates("UNKNOWN_STATE")

    def testLookupIsCaseSensitive(self) -> None:
        """
        Verify that value lookup is case-sensitive.

        Ensures that lowercase variants such as 'running' are rejected,
        since the enum values are uppercase strings.
        """
        with self.assertRaises(ValueError):
            ScheduleStates("running")

    # ------------------------------------------------------------------ #
    #  Uniqueness                                                        #
    # ------------------------------------------------------------------ #

    def testAllValuesAreUnique(self) -> None:
        """
        Verify that no two members share the same string value.

        Ensures each scheduler state maps to exactly one enum member
        without aliasing.
        """
        values = [m.value for m in ScheduleStates]
        self.assertEqual(len(values), len(set(values)))

    def testAllNamesAreUnique(self) -> None:
        """
        Verify that no two members share the same name.

        Ensures the enum definition is self-consistent and no accidental
        aliasing has been introduced.
        """
        names = [m.name for m in ScheduleStates]
        self.assertEqual(len(names), len(set(names)))

    # ------------------------------------------------------------------ #
    #  Membership check                                                  #
    # ------------------------------------------------------------------ #

    def testContainsMembership(self) -> None:
        """
        Verify that recognised members are detected via the 'in' operator.

        Ensures ScheduleStates.STOPPED in ScheduleStates evaluates to
        True, confirming standard enum membership behaviour.
        """
        self.assertIn(ScheduleStates.STOPPED, ScheduleStates)
        self.assertIn(ScheduleStates.RUNNING, ScheduleStates)
        self.assertIn(ScheduleStates.PAUSED, ScheduleStates)
