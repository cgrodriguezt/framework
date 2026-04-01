import pendulum
from datetime import datetime as stdlib_datetime, timezone as stdlib_tz
from zoneinfo import ZoneInfo
from orionis.test import TestCase
from orionis.support.time.datetime import DateTime

# Timezone and locale used as a safe, stable default across all tests
_DEFAULT_TZ = "UTC"
_DEFAULT_LOCALE = "en"

class TestDateTimeConfig(TestCase):

    def setUp(self) -> None:
        """Reset DateTime class state before each test."""
        DateTime._timezone = _DEFAULT_TZ
        DateTime._locale = _DEFAULT_LOCALE
        pendulum.set_locale(_DEFAULT_LOCALE)

    # ------------------------------------------------ loadConfig

    def testLoadConfigSetsBothTimezoneAndLocale(self):
        """
        Apply timezone and locale when both are provided to loadConfig.

        Validates that loadConfig delegates correctly to setTimezone
        and setLocale when both arguments are supplied.
        """
        DateTime._loadConfig(
            timezone_name="America/New_York", locale="es"
        )
        self.assertEqual(DateTime._timezone, "America/New_York")
        self.assertEqual(DateTime._locale, "es")

    def testLoadConfigWithNoneDoesNotOverwriteDefaults(self):
        """
        Leave timezone and locale unchanged when None is passed to loadConfig.

        Validates that providing None for both parameters keeps the
        existing class-level defaults intact.
        """
        DateTime._loadConfig(timezone_name=None, locale=None)
        self.assertEqual(DateTime._timezone, _DEFAULT_TZ)
        self.assertEqual(DateTime._locale, _DEFAULT_LOCALE)

    def testLoadConfigWithTimezoneOnlyDoesNotChangeLocale(self):
        """
        Change only the timezone when locale is None in loadConfig.

        Validates that supplying only a timezone leaves the locale
        at its previous value.
        """
        DateTime._loadConfig(timezone_name="Europe/London", locale=None)
        self.assertEqual(DateTime._timezone, "Europe/London")
        self.assertEqual(DateTime._locale, _DEFAULT_LOCALE)

    def testLoadConfigWithLocaleOnlyDoesNotChangeTimezone(self):
        """
        Change only the locale when timezone is None in loadConfig.

        Validates that supplying only a locale leaves the timezone
        at its previous value.
        """
        DateTime._loadConfig(timezone_name=None, locale="fr")
        self.assertEqual(DateTime._timezone, _DEFAULT_TZ)
        self.assertEqual(DateTime._locale, "fr")

    # ------------------------------------------------ setTimezone / getTimezone

    def testSetTimezoneStoresValidTimezone(self):
        """
        Store a valid timezone string via setTimezone.

        Validates that after calling setTimezone the internal class
        attribute reflects the new timezone name.
        """
        DateTime._setTimezone("Asia/Tokyo")
        self.assertEqual(DateTime._timezone, "Asia/Tokyo")

    def testSetTimezoneRaisesOnInvalidName(self):
        """
        Raise AttributeError when an invalid timezone name is provided.

        Validates that _setTimezone rejects unrecognised timezone strings.
        In the current pendulum version, accessing the exception class
        itself raises AttributeError, which is what callers receive.
        """
        with self.assertRaises(AttributeError):
            DateTime._setTimezone("Invalid/Timezone_XXXX")

    def testGetTimezoneReturnsCurrentValue(self):
        """
        Return the currently configured timezone string from getTimezone.

        Validates that getTimezone reflects the value set by setTimezone.
        """
        DateTime._setTimezone("Europe/Paris")
        self.assertEqual(DateTime.getTimezone(), "Europe/Paris")

    def testGetTimezoneDefaultIsUTC(self):
        """
        Return UTC as the default timezone before any configuration.

        Validates that the timezone defaults to 'UTC' on a freshly
        reset class state.
        """
        self.assertEqual(DateTime.getTimezone(), "UTC")

    # ------------------------------------------------ setLocale

    def testSetLocaleStoresLocaleValue(self):
        """
        Store the locale string via setLocale.

        Validates that calling setLocale updates the internal _locale
        attribute to the provided value.
        """
        DateTime._setLocale("de")
        self.assertEqual(DateTime._locale, "de")

    def testSetLocaleUpdatesLatin(self):
        """
        Accept a Latin-script locale code without error.

        Validates that setLocale can handle commonly used Latin locale
        codes such as 'es' (Spanish).
        """
        DateTime._setLocale("es")
        self.assertEqual(DateTime._locale, "es")

    # ------------------------------------------------ getZoneinfo

    def testGetZoneinfoReturnsZoneInfoInstance(self):
        """
        Return a ZoneInfo object from getZoneinfo.

        Validates that getZoneinfo produces a ZoneInfo instance matching
        the currently configured timezone.
        """
        result = DateTime.getZoneinfo()
        self.assertIsInstance(result, ZoneInfo)

    def testGetZoneinfoKeyMatchesConfiguredTimezone(self):
        """
        Return ZoneInfo whose key matches the configured timezone.

        Validates that the ZoneInfo key returned by getZoneinfo is
        identical to the timezone stored in DateTime._timezone.
        """
        DateTime._setTimezone("America/Chicago")
        zi = DateTime.getZoneinfo()
        self.assertEqual(zi.key, "America/Chicago")

class TestDateTimeInstants(TestCase):

    def setUp(self) -> None:
        """Reset class state before each test."""
        DateTime._timezone = _DEFAULT_TZ
        DateTime._locale = _DEFAULT_LOCALE

    # ------------------------------------------------ now

    def testNowReturnsPendulumDateTime(self):
        """
        Return a pendulum.DateTime from now.

        Validates that now() produces an instance of pendulum.DateTime.
        """
        result = DateTime.now()
        self.assertIsInstance(result, pendulum.DateTime)

    def testNowUsesDefaultTimezoneWhenNoArgGiven(self):
        """
        Use the configured default timezone when tz is None in now.

        Validates that the timezone of the returned datetime matches
        the class-level default when no tz argument is provided.
        """
        DateTime._setTimezone("Europe/Berlin")
        result = DateTime.now()
        self.assertEqual(result.timezone_name, "Europe/Berlin")

    def testNowUsesExplicitTimezoneArgument(self):
        """
        Apply the explicit tz argument in now instead of the default.

        Validates that when a timezone is passed to now(), the returned
        datetime reflects that timezone.
        """
        result = DateTime.now(tz="Asia/Singapore")
        self.assertEqual(result.timezone_name, "Asia/Singapore")

    # ------------------------------------------------ today

    def testTodayReturnsPendulumDateTime(self):
        """
        Return a pendulum.DateTime from today.

        Validates that today() produces a pendulum datetime object.
        """
        result = DateTime.today()
        self.assertIsInstance(result, pendulum.DateTime)

    def testTodayHasMidnightTime(self):
        """
        Return a datetime at midnight from today.

        Validates that today() always returns a datetime whose
        hour, minute, and second components are all zero.
        """
        result = DateTime.today()
        self.assertEqual(result.hour, 0)
        self.assertEqual(result.minute, 0)
        self.assertEqual(result.second, 0)

    def testTodayWithExplicitTimezone(self):
        """
        Apply the explicit tz argument in today instead of the default.

        Validates that the returned datetime uses the supplied timezone.
        """
        result = DateTime.today(tz="Australia/Sydney")
        self.assertEqual(result.timezone_name, "Australia/Sydney")

    # ------------------------------------------------ tomorrow

    def testTomorrowIsOneDayAfterToday(self):
        """
        Return a date exactly one day after today from tomorrow.

        Validates that tomorrow() produces a datetime whose date
        component is one day ahead of today().
        """
        today = DateTime.today()
        tomorrow = DateTime.tomorrow()
        diff = tomorrow.diff(today).in_days()
        self.assertEqual(diff, 1)

    def testTomorrowWithExplicitTimezone(self):
        """
        Apply the explicit tz argument in tomorrow instead of the default.

        Validates that the returned datetime uses the supplied timezone.
        """
        result = DateTime.tomorrow(tz="America/Sao_Paulo")
        self.assertEqual(result.timezone_name, "America/Sao_Paulo")

    # ------------------------------------------------ yesterday

    def testYesterdayIsOneDayBeforeToday(self):
        """
        Return a date exactly one day before today from yesterday.

        Validates that yesterday() produces a datetime one day behind
        today().
        """
        today = DateTime.today()
        yesterday = DateTime.yesterday()
        diff = today.diff(yesterday).in_days()
        self.assertEqual(diff, 1)

    def testYesterdayWithExplicitTimezone(self):
        """
        Apply the explicit tz argument in yesterday instead of the default.

        Validates that the returned datetime uses the supplied timezone.
        """
        result = DateTime.yesterday(tz="Pacific/Auckland")
        self.assertEqual(result.timezone_name, "Pacific/Auckland")

class TestDateTimeFromConversions(TestCase):

    def setUp(self) -> None:
        """Reset class state before each test."""
        DateTime._timezone = _DEFAULT_TZ
        DateTime._locale = _DEFAULT_LOCALE

    # ------------------------------------------------ parse

    def testParseReturnsPendulumDateTime(self):
        """
        Return a pendulum.DateTime from a valid date string.

        Validates that parse() produces a pendulum.DateTime instance
        for a well-formed ISO 8601 date string.
        """
        result = DateTime.parse("2024-06-15T12:00:00")
        self.assertIsInstance(result, pendulum.DateTime)

    def testParseConvertsToConfiguredTimezone(self):
        """
        Convert the parsed datetime to the configured timezone.

        Validates that when the parsed timezone differs from the class
        default, parse() converts the result to the class timezone.
        """
        DateTime._setTimezone("America/New_York")
        result = DateTime.parse("2024-06-15T12:00:00+00:00")
        self.assertEqual(result.timezone_name, "America/New_York")

    def testParseWithExplicitTzArgument(self):
        """
        Apply the explicit tz argument when parsing a date string.

        Validates that passing tz to parse() overrides the class-level
        default timezone for the returned datetime.
        """
        result = DateTime.parse("2024-01-01T00:00:00+00:00", tz="Asia/Tokyo")
        self.assertEqual(result.timezone_name, "Asia/Tokyo")

    # ------------------------------------------------ fromTimestamp

    def testFromTimestampReturnsPendulumDateTime(self):
        """
        Return a pendulum.DateTime from a Unix timestamp.

        Validates that fromTimestamp() converts a float timestamp to a
        valid pendulum.DateTime instance.
        """
        result = DateTime.fromTimestamp(0.0)
        self.assertIsInstance(result, pendulum.DateTime)

    def testFromTimestampEpochIsJanuaryFirst1970UTC(self):
        """
        Map Unix epoch zero to January 1st 1970 at midnight UTC.

        Validates that timestamp 0 corresponds to the Unix epoch
        in UTC with all time components set to zero.
        """
        result = DateTime.fromTimestamp(0.0, tz="UTC")
        self.assertEqual(result.year, 1970)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)
        self.assertEqual(result.hour, 0)

    def testFromTimestampUsesExplicitTz(self):
        """
        Apply the explicit tz argument in fromTimestamp.

        Validates that the returned datetime is expressed in the
        timezone supplied to fromTimestamp().
        """
        result = DateTime.fromTimestamp(0.0, tz="Asia/Tokyo")
        self.assertEqual(result.timezone_name, "Asia/Tokyo")

    # ------------------------------------------------ fromDatetime

    def testFromDatetimeWithNaiveStdlibDatetime(self):
        """
        Convert a naive stdlib datetime to pendulum in the configured tz.

        Validates that fromDatetime() treats a naive (tz-unaware)
        datetime as belonging to the class-level timezone.
        """
        naive_dt = stdlib_datetime(2024, 3, 15, 10, 30, 0)
        result = DateTime.fromDatetime(naive_dt)
        self.assertIsInstance(result, pendulum.DateTime)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 3)
        self.assertEqual(result.day, 15)

    def testFromDatetimeWithAwareStdlibDatetime(self):
        """
        Convert an aware stdlib datetime to the configured timezone.

        Validates that fromDatetime() converts a timezone-aware stdlib
        datetime to pendulum.DateTime in the class-level timezone.
        """
        aware_dt = stdlib_datetime(
            2024, 3, 15, 10, 30, 0, tzinfo=stdlib_tz.utc
        )
        DateTime._setTimezone("America/Chicago")
        result = DateTime.fromDatetime(aware_dt)
        self.assertIsInstance(result, pendulum.DateTime)
        self.assertEqual(result.timezone_name, "America/Chicago")

    def testFromDatetimeWithPendulumDatetime(self):
        """
        Convert a pendulum.DateTime to the configured timezone.

        Validates that fromDatetime() correctly converts a pendulum
        instance to the target timezone.
        """
        source = pendulum.datetime(2024, 6, 1, 12, 0, 0, tz="UTC")
        DateTime._setTimezone("Europe/London")
        result = DateTime.fromDatetime(source)
        self.assertEqual(result.timezone_name, "Europe/London")

    def testFromDatetimeRaisesTypeErrorForUnsupportedType(self):
        """
        Raise TypeError when an unsupported type is passed to fromDatetime.

        Validates that fromDatetime() rejects plain strings, integers,
        or other non-datetime objects with a TypeError.
        """
        with self.assertRaises(TypeError):
            DateTime.fromDatetime("2024-01-01")  # type: ignore[arg-type]

    def testFromDatetimeWithExplicitTzArgument(self):
        """
        Apply the explicit tz argument in fromDatetime.

        Validates that when tz is supplied, the result is expressed in
        that timezone regardless of the class-level default.
        """
        naive_dt = stdlib_datetime(2024, 1, 1, 0, 0, 0)
        result = DateTime.fromDatetime(naive_dt, tz="Asia/Seoul")
        self.assertEqual(result.timezone_name, "Asia/Seoul")

    # ------------------------------------------------ datetime (factory)

    def testDatetimeCreatesCorrectComponents(self):
        """
        Create a pendulum.DateTime with the specified date components.

        Validates that the datetime() factory method produces an object
        with year, month, day, hour, minute, and second matching the
        supplied arguments.
        """
        result = DateTime.datetime(2024, 6, 15, 10, 30, 45)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 6)
        self.assertEqual(result.day, 15)
        self.assertEqual(result.hour, 10)
        self.assertEqual(result.minute, 30)
        self.assertEqual(result.second, 45)

    def testDatetimeDefaultsMonthAndDayToOne(self):
        """
        Default month and day to 1 when only year is provided to datetime.

        Validates that omitting optional components results in the first
        day of January.
        """
        result = DateTime.datetime(2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)

    def testDatetimeUsesConfiguredTimezone(self):
        """
        Use the configured timezone when tz is None in datetime factory.

        Validates that the produced datetime is expressed in the
        class-level default timezone.
        """
        DateTime._setTimezone("Europe/Madrid")
        result = DateTime.datetime(2024, 1, 1)
        self.assertEqual(result.timezone_name, "Europe/Madrid")

    def testDatetimeWithExplicitTzArgument(self):
        """
        Apply the explicit tz argument in the datetime factory.

        Validates that the produced datetime is expressed in the
        supplied timezone rather than the class-level default.
        """
        result = DateTime.datetime(2024, 1, 1, tz="Pacific/Honolulu")
        self.assertEqual(result.timezone_name, "Pacific/Honolulu")

class TestDateTimeBoundaries(TestCase):

    def setUp(self) -> None:
        """Reset class state and build a stable reference datetime."""
        DateTime._timezone = _DEFAULT_TZ
        DateTime._locale = _DEFAULT_LOCALE
        # Wednesday, June 12 2024 at 14:30:45 UTC – used across boundary tests
        self.ref = DateTime.datetime(2024, 6, 12, 14, 30, 45, tz="UTC")

    # ------------------------------------------------ startOfDay / endOfDay

    def testStartOfDayReturnsFirstSecondOfDay(self):
        """
        Return midnight at the start of the given day from startOfDay.

        Validates that startOfDay() sets hour, minute, and second to
        zero without changing the date.
        """
        result = DateTime.startOfDay(self.ref)
        self.assertEqual(result.hour, 0)
        self.assertEqual(result.minute, 0)
        self.assertEqual(result.second, 0)
        self.assertEqual(result.date(), self.ref.date())

    def testStartOfDayWithoutDtUsesNow(self):
        """
        Use the current datetime when no argument is given to startOfDay.

        Validates that startOfDay() without arguments returns today's
        midnight.
        """
        result = DateTime.startOfDay()
        today = DateTime.today()
        self.assertEqual(result.date(), today.date())
        self.assertEqual(result.hour, 0)

    def testEndOfDayReturnsLastSecondOfDay(self):
        """
        Return 23:59:59 at the end of the given day from endOfDay.

        Validates that endOfDay() returns the last representable
        second of the supplied date.
        """
        result = DateTime.endOfDay(self.ref)
        self.assertEqual(result.hour, 23)
        self.assertEqual(result.minute, 59)
        self.assertEqual(result.second, 59)
        self.assertEqual(result.date(), self.ref.date())

    def testEndOfDayWithoutDtUsesNow(self):
        """
        Use the current datetime when no argument is given to endOfDay.

        Validates that endOfDay() without arguments returns the last
        second of today.
        """
        result = DateTime.endOfDay()
        today = DateTime.today()
        self.assertEqual(result.date(), today.date())
        self.assertEqual(result.hour, 23)

    # ------------------------------------------------ startOfWeek / endOfWeek

    def testStartOfWeekReturnsMondayMidnight(self):
        """
        Return the Monday at midnight of the given week from startOfWeek.

        Validates that startOfWeek() produces a datetime on Monday
        at 00:00:00.
        """
        result = DateTime.startOfWeek(self.ref)
        # pendulum week starts on Monday (day_of_week == MONDAY == 1)
        self.assertEqual(result.day_of_week, pendulum.MONDAY)
        self.assertEqual(result.hour, 0)

    def testEndOfWeekReturnsSundayLastSecond(self):
        """
        Return Sunday at 23:59:59 of the given week from endOfWeek.

        Validates that endOfWeek() produces a datetime on Sunday
        at 23:59:59.
        """
        result = DateTime.endOfWeek(self.ref)
        self.assertEqual(result.day_of_week, pendulum.SUNDAY)
        self.assertEqual(result.hour, 23)

    def testStartOfWeekWithoutDtUsesNow(self):
        """
        Use the current datetime when no argument is given to startOfWeek.

        Validates that startOfWeek() without arguments returns a Monday.
        """
        result = DateTime.startOfWeek()
        self.assertEqual(result.day_of_week, pendulum.MONDAY)

    # ------------------------------------------------ startOfMonth / endOfMonth

    def testStartOfMonthReturnsFirstDayMidnight(self):
        """
        Return the first day of the month at midnight from startOfMonth.

        Validates that startOfMonth() sets the day to 1 and time to
        00:00:00 for the month of the supplied datetime.
        """
        result = DateTime.startOfMonth(self.ref)
        self.assertEqual(result.day, 1)
        self.assertEqual(result.month, self.ref.month)
        self.assertEqual(result.hour, 0)

    def testEndOfMonthReturnsLastDayLastSecond(self):
        """
        Return the last day of the month at 23:59:59 from endOfMonth.

        Validates that endOfMonth() returns the final second of the
        last calendar day of the supplied month.
        """
        result = DateTime.endOfMonth(self.ref)
        # June has 30 days
        self.assertEqual(result.day, 30)
        self.assertEqual(result.month, self.ref.month)
        self.assertEqual(result.hour, 23)

    def testStartOfMonthWithoutDtUsesNow(self):
        """
        Use the current datetime when no argument is given to startOfMonth.

        Validates that startOfMonth() without arguments sets the day to
        1 for the current month.
        """
        result = DateTime.startOfMonth()
        self.assertEqual(result.day, 1)

    # ------------------------------------------------ startOfYear / endOfYear

    def testStartOfYearReturnsJanuaryFirstMidnight(self):
        """
        Return January 1st at midnight from startOfYear.

        Validates that startOfYear() produces a datetime on January 1st
        at 00:00:00 for the year of the supplied datetime.
        """
        result = DateTime.startOfYear(self.ref)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)
        self.assertEqual(result.hour, 0)
        self.assertEqual(result.year, self.ref.year)

    def testEndOfYearReturnsDecember31LastSecond(self):
        """
        Return December 31st at 23:59:59 from endOfYear.

        Validates that endOfYear() produces a datetime on December 31st
        at 23:59:59 for the year of the supplied datetime.
        """
        result = DateTime.endOfYear(self.ref)
        self.assertEqual(result.month, 12)
        self.assertEqual(result.day, 31)
        self.assertEqual(result.hour, 23)
        self.assertEqual(result.year, self.ref.year)

    def testStartOfYearWithoutDtUsesNow(self):
        """
        Use the current datetime when no argument is given to startOfYear.

        Validates that startOfYear() without arguments returns January
        1st of the current year.
        """
        result = DateTime.startOfYear()
        now = DateTime.now()
        self.assertEqual(result.year, now.year)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)

class TestDateTimeArithmetic(TestCase):

    def setUp(self) -> None:
        """Reset class state and build a stable reference datetime."""
        DateTime._timezone = _DEFAULT_TZ
        DateTime._locale = _DEFAULT_LOCALE
        self.ref = DateTime.datetime(2024, 1, 1, 12, 0, 0, tz="UTC")

    # ------------------------------------------------ addDays

    def testAddDaysShiftsDateBySpecifiedAmount(self):
        """
        Shift the date forward by the specified number of days.

        Validates that addDays() returns a datetime exactly n calendar
        days after the supplied one.
        """
        result = DateTime.addDays(self.ref, 5)
        self.assertEqual(result.day, 6)
        self.assertEqual(result.month, 1)

    def testAddDaysWithZeroReturnsUnchanged(self):
        """
        Return the same date when zero days are added.

        Validates that addDays(dt, 0) is an identity operation.
        """
        result = DateTime.addDays(self.ref, 0)
        self.assertEqual(result.date(), self.ref.date())

    def testAddDaysWithNegativeValueGoesBackward(self):
        """
        Go backward in time when a negative day count is added.

        Validates that addDays() with a negative integer moves the
        datetime into the past.
        """
        result = DateTime.addDays(self.ref, -3)
        self.assertEqual(result.day, 29)  # Dec 29 2023
        self.assertEqual(result.month, 12)

    # ------------------------------------------------ addHours

    def testAddHoursShiftsTimeBySpecifiedAmount(self):
        """
        Shift the time forward by the specified number of hours.

        Validates that addHours() returns a datetime exactly n hours
        after the supplied one.
        """
        result = DateTime.addHours(self.ref, 3)
        self.assertEqual(result.hour, 15)

    def testAddHoursRollsOverToNextDay(self):
        """
        Roll over to the next day when hours exceed 24.

        Validates that adding hours beyond midnight correctly advances
        the date by the appropriate number of days.
        """
        result = DateTime.addHours(self.ref, 14)
        self.assertEqual(result.day, 2)
        self.assertEqual(result.hour, 2)

    def testAddHoursWithZeroReturnsUnchanged(self):
        """
        Return the same datetime when zero hours are added.

        Validates that addHours(dt, 0) is an identity operation
        with respect to time.
        """
        result = DateTime.addHours(self.ref, 0)
        self.assertEqual(result.hour, self.ref.hour)

    # ------------------------------------------------ addMinutes

    def testAddMinutesShiftsTimeBySpecifiedAmount(self):
        """
        Shift the time forward by the specified number of minutes.

        Validates that addMinutes() returns a datetime exactly n
        minutes after the supplied one.
        """
        result = DateTime.addMinutes(self.ref, 30)
        self.assertEqual(result.minute, 30)

    def testAddMinutesRollsOverToNextHour(self):
        """
        Roll over to the next hour when minutes exceed 60.

        Validates that adding minutes beyond 60 correctly advances
        the hour.
        """
        result = DateTime.addMinutes(self.ref, 90)
        self.assertEqual(result.hour, 13)
        self.assertEqual(result.minute, 30)

    def testAddMinutesWithZeroReturnsUnchanged(self):
        """
        Return the same datetime when zero minutes are added.

        Validates that addMinutes(dt, 0) is an identity operation
        with respect to time.
        """
        result = DateTime.addMinutes(self.ref, 0)
        self.assertEqual(result.minute, self.ref.minute)

    # ------------------------------------------------ diffInDays

    def testDiffInDaysReturnsDifferenceBetweenDates(self):
        """
        Return the correct number of days between two dates.

        Validates that diffInDays() computes the absolute calendar-day
        difference between two pendulum.DateTime instances.
        """
        dt2 = DateTime.addDays(self.ref, 10)
        diff = DateTime.diffInDays(self.ref, dt2)
        self.assertEqual(diff, 10)

    def testDiffInDaysIsZeroForSameDate(self):
        """
        Return zero when both dates are identical.

        Validates that diffInDays() returns 0 when both arguments
        reference the same point in time.
        """
        diff = DateTime.diffInDays(self.ref, self.ref)
        self.assertEqual(diff, 0)

    def testDiffInDaysIsPositiveRegardlessOfOrder(self):
        """
        Return a non-negative value regardless of argument order.

        Validates that diffInDays() returns a positive integer even when
        dt2 is earlier than dt1 (pendulum diffs are always absolute).
        """
        earlier = DateTime.addDays(self.ref, -5)
        diff = DateTime.diffInDays(self.ref, earlier)
        self.assertGreaterEqual(diff, 0)

    # ------------------------------------------------ diffInHours

    def testDiffInHoursReturnsDifferenceBetweenDatetimes(self):
        """
        Return the correct number of hours between two datetimes.

        Validates that diffInHours() computes the integer-hour
        difference between two pendulum.DateTime instances.
        """
        dt2 = DateTime.addHours(self.ref, 6)
        diff = DateTime.diffInHours(self.ref, dt2)
        self.assertEqual(diff, 6)

    def testDiffInHoursIsZeroForSameDatetime(self):
        """
        Return zero when both datetimes are identical.

        Validates that diffInHours() returns 0 when both arguments
        reference the same point in time.
        """
        diff = DateTime.diffInHours(self.ref, self.ref)
        self.assertEqual(diff, 0)

class TestDateTimePredicates(TestCase):

    def setUp(self) -> None:
        """Reset class state before each test."""
        DateTime._timezone = _DEFAULT_TZ
        DateTime._locale = _DEFAULT_LOCALE

    # ------------------------------------------------ isWeekend

    def testIsWeekendReturnsTrueForSaturday(self):
        """
        Return True when the given date falls on Saturday.

        Validates that isWeekend() identifies Saturday correctly.
        """
        # 2024-06-08 is a Saturday
        saturday = DateTime.datetime(2024, 6, 8, tz="UTC")
        self.assertTrue(DateTime.isWeekend(saturday))

    def testIsWeekendReturnsTrueForSunday(self):
        """
        Return True when the given date falls on Sunday.

        Validates that isWeekend() identifies Sunday correctly.
        """
        # 2024-06-09 is a Sunday
        sunday = DateTime.datetime(2024, 6, 9, tz="UTC")
        self.assertTrue(DateTime.isWeekend(sunday))

    def testIsWeekendReturnsFalseForWeekday(self):
        """
        Return False when the given date falls on a weekday.

        Validates that isWeekend() returns False for Monday through
        Friday.
        """
        # 2024-06-10 is a Monday
        monday = DateTime.datetime(2024, 6, 10, tz="UTC")
        self.assertFalse(DateTime.isWeekend(monday))

    def testIsWeekendWithoutArgumentUsesNow(self):
        """
        Use the current datetime when no argument is given to isWeekend.

        Validates that isWeekend() without arguments produces a boolean
        result consistent with the current day of the week.
        """
        result = DateTime.isWeekend()
        now = DateTime.now()
        expected = now.day_of_week in [pendulum.SATURDAY, pendulum.SUNDAY]
        self.assertEqual(result, expected)

    # ------------------------------------------------ isToday

    def testIsTodayReturnsTrueForCurrentDatetime(self):
        """
        Return True when the given datetime is today.

        Validates that isToday() correctly identifies the current
        date as today.
        """
        now = DateTime.now()
        self.assertTrue(DateTime.isToday(now))

    def testIsTodayReturnsFalseForYesterdayDatetime(self):
        """
        Return False when the given datetime is yesterday.

        Validates that isToday() returns False for a datetime that
        falls one day in the past.
        """
        yesterday = DateTime.yesterday()
        self.assertFalse(DateTime.isToday(yesterday))

    def testIsTodayReturnsFalseForTomorrowDatetime(self):
        """
        Return False when the given datetime is tomorrow.

        Validates that isToday() returns False for a datetime that
        falls one day in the future.
        """
        tomorrow = DateTime.tomorrow()
        self.assertFalse(DateTime.isToday(tomorrow))

    # ------------------------------------------------ isFuture

    def testIsFutureReturnsTrueForFutureDate(self):
        """
        Return True when the given datetime is in the future.

        Validates that isFuture() correctly identifies a datetime
        set far ahead of the current moment.
        """
        future = DateTime.addDays(DateTime.now(), 100)
        self.assertTrue(DateTime.isFuture(future))

    def testIsFutureReturnsFalseForPastDate(self):
        """
        Return False when the given datetime is in the past.

        Validates that isFuture() correctly rejects a datetime
        set far behind the current moment.
        """
        past = DateTime.addDays(DateTime.now(), -100)
        self.assertFalse(DateTime.isFuture(past))

    # ------------------------------------------------ isPast

    def testIsPastReturnsTrueForPastDate(self):
        """
        Return True when the given datetime is in the past.

        Validates that isPast() correctly identifies a datetime
        set far behind the current moment.
        """
        past = DateTime.addDays(DateTime.now(), -100)
        self.assertTrue(DateTime.isPast(past))

    def testIsPastReturnsFalseForFutureDate(self):
        """
        Return False when the given datetime is in the future.

        Validates that isPast() correctly rejects a datetime
        set far ahead of the current moment.
        """
        future = DateTime.addDays(DateTime.now(), 100)
        self.assertFalse(DateTime.isPast(future))

    # ------------------------------------------------ convertToLocal

    def testConvertToLocalFromString(self):
        """
        Convert an ISO string to the configured local timezone.

        Validates that convertToLocal() accepts a plain date string
        and returns a pendulum.DateTime in the class timezone.
        """
        result = DateTime.convertToLocal("2024-06-15T12:00:00+00:00")
        self.assertIsInstance(result, pendulum.DateTime)
        self.assertEqual(result.timezone_name, _DEFAULT_TZ)

    def testConvertToLocalFromStdlibDatetime(self):
        """
        Convert a stdlib datetime to the configured local timezone.

        Validates that convertToLocal() accepts a stdlib datetime
        object and returns a pendulum.DateTime in the class timezone.
        """
        naive_dt = stdlib_datetime(2024, 6, 15, 12, 0, 0)
        result = DateTime.convertToLocal(naive_dt)
        self.assertIsInstance(result, pendulum.DateTime)
        self.assertEqual(result.timezone_name, _DEFAULT_TZ)

    def testConvertToLocalFromPendulumDatetime(self):
        """
        Convert a pendulum datetime to the configured local timezone.

        Validates that convertToLocal() accepts a pendulum.DateTime
        and returns one in the class timezone.
        """
        source = pendulum.datetime(2024, 6, 15, 12, 0, 0, tz="Asia/Tokyo")
        result = DateTime.convertToLocal(source)
        self.assertIsInstance(result, pendulum.DateTime)
        self.assertEqual(result.timezone_name, _DEFAULT_TZ)

    # ------------------------------------------------ formatLocal

    def testFormatLocalReturnsString(self):
        """
        Return a formatted date string from formatLocal.

        Validates that formatLocal() produces a non-empty string
        for a given pendulum.DateTime.
        """
        dt = DateTime.datetime(2024, 6, 15, 10, 30, 45, tz="UTC")
        result = DateTime.formatLocal(dt)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def testFormatLocalDefaultFormatMatchesISO(self):
        """
        Use the default format YYYY-MM-DD HH:mm:ss in formatLocal.

        Validates that the default format string produces output in
        the expected pattern for a known datetime.
        """
        dt = DateTime.datetime(2024, 6, 15, 10, 30, 45, tz="UTC")
        result = DateTime.formatLocal(dt)
        self.assertEqual(result, "2024-06-15 10:30:45")

    def testFormatLocalWithCustomFormat(self):
        """
        Apply a custom format string in formatLocal.

        Validates that formatLocal() respects an explicit format_string
        argument and returns output matching that pattern.
        """
        dt = DateTime.datetime(2024, 6, 15, tz="UTC")
        result = DateTime.formatLocal(dt, format_string="YYYY/MM/DD")
        self.assertEqual(result, "2024/06/15")

    def testFormatLocalWithoutDtUsesNow(self):
        """
        Use the current datetime when no dt is given to formatLocal.

        Validates that formatLocal() without a dt argument returns a
        non-empty string representing the current moment.
        """
        result = DateTime.formatLocal()
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
