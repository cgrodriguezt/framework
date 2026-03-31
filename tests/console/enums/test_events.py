from __future__ import annotations
from enum import IntEnum
from orionis.console.enums.events import TaskEvent, SchedulerEvent
from orionis.test import TestCase

class TestTaskEvent(TestCase):

    # ------------------------------------------------------------------ #
    #  Type & membership                                                 #
    # ------------------------------------------------------------------ #

    def testIsIntEnumSubclass(self) -> None:
        """
        Verify that TaskEvent is a subclass of IntEnum.

        Ensures the enum values are integers and support integer
        arithmetic and comparison operations.
        """
        self.assertTrue(issubclass(TaskEvent, IntEnum))

    def testHasExpectedMemberCount(self) -> None:
        """
        Verify that TaskEvent defines exactly eight members.

        Ensures no members have been accidentally added or removed.
        """
        self.assertEqual(len(TaskEvent), 8)

    def testAllMembersHaveIntegerValues(self) -> None:
        """
        Verify that every member value is an integer.

        Ensures the values can be compared with APScheduler event codes
        without type conversion.
        """
        for member in TaskEvent:
            self.assertIsInstance(int(member), int)

    # ------------------------------------------------------------------ #
    #  Individual member values (powers of two)                          #
    # ------------------------------------------------------------------ #

    def testAddedValue(self) -> None:
        """
        Verify that ADDED equals 2**9.

        Ensures the event code matches the expected APScheduler constant.
        """
        self.assertEqual(TaskEvent.ADDED, 2 ** 9)

    def testRemovedValue(self) -> None:
        """
        Verify that REMOVED equals 2**10.

        Ensures the event code matches the expected APScheduler constant.
        """
        self.assertEqual(TaskEvent.REMOVED, 2 ** 10)

    def testModifiedValue(self) -> None:
        """
        Verify that MODIFIED equals 2**11.

        Ensures the event code matches the expected APScheduler constant.
        """
        self.assertEqual(TaskEvent.MODIFIED, 2 ** 11)

    def testExecutedValue(self) -> None:
        """
        Verify that EXECUTED equals 2**12.

        Ensures the event code matches the expected APScheduler constant.
        """
        self.assertEqual(TaskEvent.EXECUTED, 2 ** 12)

    def testErrorValue(self) -> None:
        """
        Verify that ERROR equals 2**13.

        Ensures the event code matches the expected APScheduler constant.
        """
        self.assertEqual(TaskEvent.ERROR, 2 ** 13)

    def testMissedValue(self) -> None:
        """
        Verify that MISSED equals 2**14.

        Ensures the event code matches the expected APScheduler constant.
        """
        self.assertEqual(TaskEvent.MISSED, 2 ** 14)

    def testSubmittedValue(self) -> None:
        """
        Verify that SUBMITTED equals 2**15.

        Ensures the event code matches the expected APScheduler constant.
        """
        self.assertEqual(TaskEvent.SUBMITTED, 2 ** 15)

    def testMaxInstancesValue(self) -> None:
        """
        Verify that MAX_INSTANCES equals 2**16.

        Ensures the event code matches the expected APScheduler constant.
        """
        self.assertEqual(TaskEvent.MAX_INSTANCES, 2 ** 16)

    # ------------------------------------------------------------------ #
    #  Lookup & uniqueness                                               #
    # ------------------------------------------------------------------ #

    def testLookupByValue(self) -> None:
        """
        Verify that members can be retrieved by their integer value.

        Ensures reverse lookup from a raw APScheduler event code works
        correctly.
        """
        self.assertIs(TaskEvent(2 ** 12), TaskEvent.EXECUTED)

    def testLookupInvalidValueRaisesValueError(self) -> None:
        """
        Verify that looking up an unknown integer raises ValueError.

        Ensures the enum rejects arbitrary integers that do not
        correspond to a defined member.
        """
        with self.assertRaises(ValueError):
            TaskEvent(9999)

    def testAllValuesAreUnique(self) -> None:
        """
        Verify that no two TaskEvent members share the same integer value.

        Ensures each APScheduler event code maps to exactly one enum
        member without aliasing.
        """
        values = [int(m) for m in TaskEvent]
        self.assertEqual(len(values), len(set(values)))

    def testValuesArePowersOfTwo(self) -> None:
        """
        Verify that every TaskEvent value is a power of two.

        Ensures the bit-flag design is consistent so events can be
        combined with bitwise OR without collision.
        """
        for member in TaskEvent:
            v = int(member)
            self.assertGreater(v, 0)
            self.assertEqual(v & (v - 1), 0)


class TestSchedulerEvent(TestCase):
    """Test suite for the SchedulerEvent IntEnum."""

    # ------------------------------------------------------------------ #
    #  Type & membership                                                 #
    # ------------------------------------------------------------------ #

    def testIsIntEnumSubclass(self) -> None:
        """
        Verify that SchedulerEvent is a subclass of IntEnum.

        Ensures the enum values are integers compatible with APScheduler
        event codes.
        """
        self.assertTrue(issubclass(SchedulerEvent, IntEnum))

    def testHasExpectedMemberCount(self) -> None:
        """
        Verify that SchedulerEvent defines exactly four members.

        Ensures no members have been accidentally added or removed.
        """
        self.assertEqual(len(SchedulerEvent), 4)

    # ------------------------------------------------------------------ #
    #  Individual member values                                          #
    # ------------------------------------------------------------------ #

    def testStartedValue(self) -> None:
        """
        Verify that STARTED equals 2**0 (1).

        Ensures the scheduler-started code matches the expected value.
        """
        self.assertEqual(SchedulerEvent.STARTED, 2 ** 0)

    def testShutdownValue(self) -> None:
        """
        Verify that SHUTDOWN equals 2**1 (2).

        Ensures the scheduler-shutdown code matches the expected value.
        """
        self.assertEqual(SchedulerEvent.SHUTDOWN, 2 ** 1)

    def testPausedValue(self) -> None:
        """
        Verify that PAUSED equals 2**2 (4).

        Ensures the scheduler-paused code matches the expected value.
        """
        self.assertEqual(SchedulerEvent.PAUSED, 2 ** 2)

    def testResumedValue(self) -> None:
        """
        Verify that RESUMED equals 2**3 (8).

        Ensures the scheduler-resumed code matches the expected value.
        """
        self.assertEqual(SchedulerEvent.RESUMED, 2 ** 3)

    # ------------------------------------------------------------------ #
    #  Lookup & uniqueness                                               #
    # ------------------------------------------------------------------ #

    def testLookupByValue(self) -> None:
        """
        Verify that members can be retrieved by their integer value.

        Ensures SchedulerEvent(1) returns SchedulerEvent.STARTED.
        """
        self.assertIs(SchedulerEvent(1), SchedulerEvent.STARTED)

    def testLookupInvalidValueRaisesValueError(self) -> None:
        """
        Verify that looking up an unknown integer raises ValueError.

        Ensures the enum rejects arbitrary integers not defined as
        members.
        """
        with self.assertRaises(ValueError):
            SchedulerEvent(9999)

    def testAllValuesAreUnique(self) -> None:
        """
        Verify that no two SchedulerEvent members share the same value.

        Ensures each scheduler event code maps to exactly one member.
        """
        values = [int(m) for m in SchedulerEvent]
        self.assertEqual(len(values), len(set(values)))

    def testValuesArePowersOfTwo(self) -> None:
        """
        Verify that every SchedulerEvent value is a power of two.

        Ensures the bit-flag design is self-consistent for potential
        bitwise combination of scheduler states.
        """
        for member in SchedulerEvent:
            v = int(member)
            self.assertGreater(v, 0)
            self.assertEqual(v & (v - 1), 0)

    def testTaskEventAndSchedulerEventValuesDoNotOverlap(self) -> None:
        """
        Verify that TaskEvent and SchedulerEvent values do not overlap.

        Ensures that no integer is shared between the two enums,
        preventing ambiguity when dispatching raw event codes.
        """
        task_values = {int(m) for m in TaskEvent}
        scheduler_values = {int(m) for m in SchedulerEvent}
        self.assertEqual(len(task_values & scheduler_values), 0)
