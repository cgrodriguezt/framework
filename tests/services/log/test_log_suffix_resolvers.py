from __future__ import annotations
import threading
from datetime import datetime, time
from zoneinfo import ZoneInfo
from orionis.services.log.handlers.chunked_suffix_resolver import (
    ChunkedSuffixResolver,
)
from orionis.services.log.handlers.daily_suffix_resolver import DailySuffixResolver
from orionis.services.log.handlers.hourly_suffix_resolver import HourlySuffixResolver
from orionis.services.log.handlers.monthly_suffix_resolver import (
    MonthlySuffixResolver,
)
from orionis.services.log.handlers.weekly_suffix_resolver import WeeklySuffixResolver
from orionis.test import TestCase

# Shared UTC timezone for all tests to ensure deterministic results.
_UTC = ZoneInfo("UTC")

# ---------------------------------------------------------------------------
# TestHourlySuffixResolver
# ---------------------------------------------------------------------------

class TestHourlySuffixResolver(TestCase):

    def _resolver(self) -> HourlySuffixResolver:
        """Return a resolver pinned to UTC to avoid locale-dependent behaviour."""
        r = HourlySuffixResolver()
        r.tz = _UTC
        return r

    def testGetSuffixFormatWithExplicitDatetime(self) -> None:
        """
        Return a correctly-formatted hourly suffix for an explicit datetime.

        Validates that the suffix matches the pattern 'YYYY-MM-DD_HH' when
        a specific datetime is supplied.
        """
        r = self._resolver()
        dt = datetime(2025, 4, 9, 14, 30, 45, tzinfo=_UTC)
        result = r.getSuffix(dt=dt)
        self.assertEqual(result, "2025-04-09_14")

    def testGetSuffixFormatWhenNone(self) -> None:
        """
        Return a valid hourly suffix when no datetime is provided.

        Validates that calling getSuffix() with dt=None produces a string
        matching the expected 'YYYY-MM-DD_HH' pattern.
        """
        r = self._resolver()
        result = r.getSuffix()
        self.assertRegex(result, r"^\d{4}-\d{2}-\d{2}_\d{2}$")

    def testGetNextRotationTimeIsExactNextHour(self) -> None:
        """
        Produce a next-rotation datetime at the start of the following hour.

        Validates that minutes, seconds, and microseconds are zeroed and the
        hour is incremented by one.
        """
        r = self._resolver()
        current = datetime(2025, 4, 9, 14, 30, 45, tzinfo=_UTC)
        expected = datetime(2025, 4, 9, 15, 0, 0, tzinfo=_UTC)
        result = r.getNextRotationTime(current)
        self.assertEqual(result, expected)

    def testGetNextRotationTimeMidnightBoundary(self) -> None:
        """
        Wrap to the next day when current hour is 23.

        Validates that the next rotation crosses the day boundary correctly
        from 23:xx to 00:00 of the following day.
        """
        r = self._resolver()
        current = datetime(2025, 4, 9, 23, 59, 59, tzinfo=_UTC)
        expected = datetime(2025, 4, 10, 0, 0, 0, tzinfo=_UTC)
        result = r.getNextRotationTime(current)
        self.assertEqual(result, expected)

    def testGetNextRotationTimeIsAfterCurrentTime(self) -> None:
        """
        Guarantee that the next rotation time is always in the future.

        Validates that getNextRotationTime always returns a datetime strictly
        greater than the provided current_time.
        """
        r = self._resolver()
        current = datetime(2025, 6, 15, 8, 45, 0, tzinfo=_UTC)
        result = r.getNextRotationTime(current)
        self.assertGreater(result, current)

# ---------------------------------------------------------------------------
# TestDailySuffixResolver
# ---------------------------------------------------------------------------

class TestDailySuffixResolver(TestCase):

    def _resolver(
        self,
        at_time: time | None = None,
    ) -> DailySuffixResolver:
        """Return a resolver pinned to UTC."""
        r = DailySuffixResolver(at_time=at_time)
        r.tz = _UTC
        return r

    def testGetSuffixFormatWithExplicitDatetime(self) -> None:
        """
        Return a date-based suffix for an explicit datetime.

        Validates that the suffix matches 'YYYY-MM-DD' for a given date.
        """
        r = self._resolver()
        dt = datetime(2025, 3, 31, 10, 0, 0, tzinfo=_UTC)
        self.assertEqual(r.getSuffix(dt=dt), "2025-03-31")

    def testGetSuffixFormatWhenNone(self) -> None:
        """
        Return a valid date suffix when no datetime argument is passed.

        Validates that the returned string matches 'YYYY-MM-DD'.
        """
        r = self._resolver()
        result = r.getSuffix()
        self.assertRegex(result, r"^\d{4}-\d{2}-\d{2}$")

    def testGetNextRotationTimePastAtTimeMovesToNextDay(self) -> None:
        """
        Advance to the next day when at_time has already passed today.

        Validates that if the configured rotation time is earlier than
        current_time, the result is at_time on the following day.
        """
        r = self._resolver(at_time=time(0, 0, 0))
        current = datetime(2025, 4, 9, 14, 30, 0, tzinfo=_UTC)
        expected = datetime(2025, 4, 10, 0, 0, 0, tzinfo=_UTC)
        self.assertEqual(r.getNextRotationTime(current), expected)

    def testGetNextRotationTimeFutureAtTimeStaysSameDay(self) -> None:
        """
        Remain on the same day when at_time is still ahead of current_time.

        Validates that a rotation time set in the future of the current day is
        returned without adding an extra day.
        """
        r = self._resolver(at_time=time(18, 0, 0))
        current = datetime(2025, 4, 9, 14, 30, 0, tzinfo=_UTC)
        expected = datetime(2025, 4, 9, 18, 0, 0, tzinfo=_UTC)
        self.assertEqual(r.getNextRotationTime(current), expected)

    def testGetNextRotationTimeDefaultAtTimeIsMidnight(self) -> None:
        """
        Default to midnight as the rotation time when at_time is not provided.

        Validates that the resolver uses 00:00:00 when constructed without an
        explicit at_time.
        """
        r = self._resolver()
        self.assertEqual(r.at_time, time(0, 0, 0))

    def testGetNextRotationTimeIsAfterCurrentTime(self) -> None:
        """
        Always produce a next-rotation time that is in the future.

        Validates the invariant that getNextRotationTime > current_time for
        any valid input.
        """
        r = self._resolver(at_time=time(0, 0, 0))
        current = datetime(2025, 7, 20, 5, 0, 0, tzinfo=_UTC)
        result = r.getNextRotationTime(current)
        self.assertGreater(result, current)

# ---------------------------------------------------------------------------
# TestWeeklySuffixResolver
# ---------------------------------------------------------------------------

class TestWeeklySuffixResolver(TestCase):

    def _resolver(
        self,
        at_time: time | None = None,
    ) -> WeeklySuffixResolver:
        """Return a resolver pinned to UTC."""
        r = WeeklySuffixResolver(at_time=at_time)
        r.tz = _UTC
        return r

    def testGetSuffixFormatWithExplicitDatetime(self) -> None:
        """
        Return a week-based suffix for an explicit datetime.

        Validates that the suffix follows the 'YYYY-weekWW' pattern using
        ISO calendar week numbering.
        """
        r = self._resolver()
        # Jan 6, 2025 is a Monday – ISO week 2 of 2025
        dt = datetime(2025, 1, 6, 12, 0, 0, tzinfo=_UTC)
        self.assertEqual(r.getSuffix(dt=dt), "2025-week02")

    def testGetSuffixFormatWhenNone(self) -> None:
        """
        Return a valid weekly suffix when no datetime argument is passed.

        Validates the pattern 'YYYY-weekWW' when dt=None.
        """
        r = self._resolver()
        result = r.getSuffix()
        self.assertRegex(result, r"^\d{4}-week\d{2}$")

    def testGetNextRotationTimeIsUpcomingMonday(self) -> None:
        """
        Advance to the upcoming Monday when called on a mid-week day.

        Validates that for a Wednesday input the next rotation is set to the
        following Monday at the configured at_time.
        """
        r = self._resolver(at_time=time(0, 0, 0))
        # April 9, 2025 is a Wednesday (weekday=2)
        current = datetime(2025, 4, 9, 14, 0, 0, tzinfo=_UTC)
        # Next Monday is April 14, 2025
        expected = datetime(2025, 4, 14, 0, 0, 0, tzinfo=_UTC)
        result = r.getNextRotationTime(current)
        self.assertEqual(result, expected)

    def testGetNextRotationTimeIsAfterCurrentTime(self) -> None:
        """
        Ensure the next rotation time is strictly in the future.

        Validates the time-forward invariant of getNextRotationTime.
        """
        r = self._resolver(at_time=time(0, 0, 0))
        current = datetime(2025, 4, 9, 14, 0, 0, tzinfo=_UTC)
        result = r.getNextRotationTime(current)
        self.assertGreater(result, current)

    def testGetNextRotationTimeDefaultAtTimeIsMidnight(self) -> None:
        """
        Use midnight as the default rotation time when at_time is omitted.

        Validates that the resolver defaults to 00:00:00 when constructed
        without an at_time argument.
        """
        r = self._resolver()
        self.assertEqual(r.at_time, time(0, 0, 0))

    def testCustomAtTimeIsPreserved(self) -> None:
        """
        Preserve a custom at_time in the next rotation datetime.

        Validates that specifying a non-midnight rotation time produces a
        result whose time component equals the configured at_time.
        """
        at = time(6, 0, 0)
        r = self._resolver(at_time=at)
        # April 9, 2025 is a Wednesday
        current = datetime(2025, 4, 9, 3, 0, 0, tzinfo=_UTC)
        result = r.getNextRotationTime(current)
        self.assertEqual(result.hour, 6)
        self.assertEqual(result.minute, 0)

# ---------------------------------------------------------------------------
# TestMonthlySuffixResolver
# ---------------------------------------------------------------------------

class TestMonthlySuffixResolver(TestCase):

    def _resolver(
        self,
        at_time: time | None = None,
    ) -> MonthlySuffixResolver:
        """Return a resolver pinned to UTC."""
        r = MonthlySuffixResolver(at_time=at_time)
        r.tz = _UTC
        return r

    def testGetSuffixFormatWithExplicitDatetime(self) -> None:
        """
        Return a month-based suffix for an explicit datetime.

        Validates the suffix follows 'YYYY-MM' for a regular month.
        """
        r = self._resolver()
        dt = datetime(2025, 3, 15, 10, 0, 0, tzinfo=_UTC)
        self.assertEqual(r.getSuffix(dt=dt), "2025-03")

    def testGetSuffixFormatWhenNone(self) -> None:
        """
        Return a valid monthly suffix when no datetime argument is passed.

        Validates 'YYYY-MM' pattern with dt=None.
        """
        r = self._resolver()
        result = r.getSuffix()
        self.assertRegex(result, r"^\d{4}-\d{2}$")

    def testGetNextRotationTimeRegularMonth(self) -> None:
        """
        Advance to the first day of the following month for a regular month.

        Validates that March 2025 produces a rotation date of April 1, 2025.
        """
        r = self._resolver(at_time=time(0, 0, 0))
        current = datetime(2025, 3, 15, 12, 0, 0, tzinfo=_UTC)
        expected = datetime(2025, 4, 1, 0, 0, 0, tzinfo=_UTC)
        self.assertEqual(r.getNextRotationTime(current), expected)

    def testGetNextRotationTimeDecemberWrapsToJanuary(self) -> None:
        """
        Wrap December to January of the next year.

        Validates that a December input produces a rotation date of
        January 1 of the following year.
        """
        r = self._resolver(at_time=time(0, 0, 0))
        current = datetime(2025, 12, 20, 8, 0, 0, tzinfo=_UTC)
        expected = datetime(2026, 1, 1, 0, 0, 0, tzinfo=_UTC)
        self.assertEqual(r.getNextRotationTime(current), expected)

    def testGetNextRotationTimeIsAfterCurrentTime(self) -> None:
        """
        Produce a rotation time that is always after the current time.

        Validates the forward-time invariant of getNextRotationTime.
        """
        r = self._resolver()
        current = datetime(2025, 8, 31, 23, 59, 59, tzinfo=_UTC)
        result = r.getNextRotationTime(current)
        self.assertGreater(result, current)

    def testGetNextRotationTimeDayIsFirstOfMonth(self) -> None:
        """
        Always land on the first day of the target month.

        Validates that the computed next-rotation date has day=1.
        """
        r = self._resolver()
        current = datetime(2025, 5, 10, 0, 0, 0, tzinfo=_UTC)
        result = r.getNextRotationTime(current)
        self.assertEqual(result.day, 1)

    def testDefaultAtTimeIsMidnight(self) -> None:
        """
        Default at_time to midnight when not provided.

        Validates the resolver uses 00:00:00 when constructed without at_time.
        """
        r = self._resolver()
        self.assertEqual(r.at_time, time(0, 0, 0))

# ---------------------------------------------------------------------------
# TestChunkedSuffixResolver
# ---------------------------------------------------------------------------

class TestChunkedSuffixResolver(TestCase):

    def testGetSuffixFormatWithExplicitDatetime(self) -> None:
        """
        Return a correctly-formatted chunked suffix for a given datetime.

        Validates the format 'YYYYMMDD_HHMMSS_NNNN' where NNNN is a
        zero-padded counter.
        """
        resolver = ChunkedSuffixResolver()
        dt = datetime(2025, 4, 9, 14, 30, 5, tzinfo=_UTC)
        result = resolver.getSuffix(dt=dt)
        self.assertRegex(result, r"^\d{8}_\d{6}_\d{4}$")
        self.assertTrue(result.startswith("20250409_143005_"))

    def testGetSuffixCounterStartsAtOne(self) -> None:
        """
        Begin the internal counter at one on the first getSuffix call.

        Validates that a freshly created resolver produces a suffix ending
        in '0001' for the first invocation.
        """
        resolver = ChunkedSuffixResolver()
        dt = datetime(2025, 1, 1, 0, 0, 0, tzinfo=_UTC)
        result = resolver.getSuffix(dt=dt)
        self.assertTrue(result.endswith("_0001"))

    def testGetSuffixCounterIncrementsWithEachCall(self) -> None:
        """
        Increment the counter with every successive getSuffix call.

        Validates that consecutive calls produce unique suffixes with
        monotonically increasing counters.
        """
        resolver = ChunkedSuffixResolver()
        dt = datetime(2025, 1, 1, 0, 0, 0, tzinfo=_UTC)
        first = resolver.getSuffix(dt=dt)
        second = resolver.getSuffix(dt=dt)
        third = resolver.getSuffix(dt=dt)
        self.assertTrue(first.endswith("_0001"))
        self.assertTrue(second.endswith("_0002"))
        self.assertTrue(third.endswith("_0003"))

    def testGetSuffixFormatWhenNone(self) -> None:
        """
        Return a valid chunked suffix when no datetime argument is passed.

        Validates that getSuffix() with dt=None uses the current time and
        produces the expected format.
        """
        resolver = ChunkedSuffixResolver()
        result = resolver.getSuffix()
        self.assertRegex(result, r"^\d{8}_\d{6}_\d{4}$")

    def testGetNextRotationTimeIsOneHourLater(self) -> None:
        """
        Return current_time plus one hour as the next rotation time.

        Validates that chunked rotation always schedules the next rotation
        exactly one hour from the provided current_time.
        """
        resolver = ChunkedSuffixResolver()
        current = datetime(2025, 4, 9, 10, 0, 0, tzinfo=_UTC)
        expected = datetime(2025, 4, 9, 11, 0, 0, tzinfo=_UTC)
        self.assertEqual(resolver.getNextRotationTime(current), expected)

    def testGetSuffixThreadSafeUniqueCounters(self) -> None:
        """
        Guarantee unique counters under concurrent getSuffix calls.

        Validates thread safety of the internal counter by collecting suffixes
        from multiple threads and verifying there are no duplicates.
        """
        resolver = ChunkedSuffixResolver()
        dt = datetime(2025, 1, 1, 0, 0, 0, tzinfo=_UTC)
        results: list[str] = []
        lock = threading.Lock()

        def _call() -> None:
            suffix = resolver.getSuffix(dt=dt)
            with lock:
                results.append(suffix)

        threads = [threading.Thread(target=_call) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), len(set(results)))
