from __future__ import annotations
import pendulum
from datetime import datetime as stdlib_datetime
from zoneinfo import ZoneInfo

class DateTime:
    """
    Provide a high-level interface for date and time operations.

    All methods are class-level, using a configurable default timezone
    and locale backed by `pendulum` for immutable datetime arithmetic.
    """

    # ruff: noqa: PLR0913

    # Default timezone and locale
    _timezone: str = "UTC"
    _locale: str = "en"

    @classmethod
    def _loadConfig(
        cls,
        timezone_name: str | None = None,
        locale: str | None = None,
    ) -> None:
        """
        Load configuration for timezone and locale.

        Parameters
        ----------
        timezone_name : str | None, optional
            Name of the timezone (e.g., 'America/Mexico_City'). If None, uses
            the default.
        locale : str | None, optional
            Language code (e.g., 'es', 'en', 'fr'). If None, uses the default.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Set timezone if provided
        if timezone_name:
            cls._setTimezone(timezone_name)
        # Set locale if provided
        if locale:
            cls._setLocale(locale)

    @classmethod
    def _setTimezone(cls, timezone_name: str) -> None:
        """
        Set the default timezone for the application.

        Parameters
        ----------
        timezone_name : str
            Name of the timezone (e.g., 'America/Mexico_City').

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        ValueError
            If the timezone is invalid.
        """
        try:
            # Validate that the timezone exists
            pendulum.now(timezone_name)
            cls._timezone = timezone_name
        except pendulum.tz.zoneinfo.exceptions.InvalidTimezone as e:
            error_msg = f"Invalid timezone '{timezone_name}': {e}"
            raise ValueError(error_msg) from e

    @classmethod
    def _setLocale(cls, locale: str) -> None:
        """
        Set the default locale for date and time formatting.

        Parameters
        ----------
        locale : str
            Language code (e.g., 'es', 'en', 'fr').

        Returns
        -------
        None
            This method does not return a value.
        """
        # Set the locale for pendulum and store it in the class variable
        cls._locale = locale
        pendulum.set_locale(locale)

    @classmethod
    def getTimezone(cls) -> str:
        """
        Return the configured timezone.

        Returns
        -------
        str
            The currently configured timezone name.
        """
        return cls._timezone

    @classmethod
    def getZoneinfo(cls) -> ZoneInfo:
        """
        Return the ZoneInfo object for the configured timezone.

        Returns
        -------
        ZoneInfo
            The ZoneInfo instance corresponding to the configured timezone.
        """
        return ZoneInfo(cls._timezone)

    @classmethod
    def now(cls, tz: str | None = None) -> pendulum.DateTime:
        """
        Get the current date and time.

        Parameters
        ----------
        tz : str | None, optional
            Specific timezone name. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            The current date and time in the specified or default timezone.
        """
        # Return the current datetime in the specified or default timezone
        timezone = tz or cls._timezone
        return pendulum.now(timezone)

    @classmethod
    def today(cls, tz: str | None = None) -> pendulum.Date:
        """
        Return the current date without time component.

        Parameters
        ----------
        tz : str | None, optional
            Specific timezone name. If None, uses the configured default.

        Returns
        -------
        pendulum.Date
            The current date in the specified or default timezone.
        """
        # Return today's date in the specified or default timezone
        timezone = tz or cls._timezone
        return pendulum.today(timezone)

    @classmethod
    def tomorrow(cls, tz: str | None = None) -> pendulum.Date:
        """
        Return tomorrow's date in the specified or default timezone.

        Parameters
        ----------
        tz : str | None, optional
            Timezone name. If None, uses the configured default.

        Returns
        -------
        pendulum.Date
            The date for tomorrow in the specified or default timezone.
        """
        timezone = tz or cls._timezone
        return pendulum.tomorrow(timezone)

    @classmethod
    def yesterday(cls, tz: str | None = None) -> pendulum.Date:
        """
        Return the date for yesterday in the specified or default timezone.

        Parameters
        ----------
        tz : str | None, optional
            Timezone name. If None, uses the configured default.

        Returns
        -------
        pendulum.Date
            The date for yesterday in the specified or default timezone.
        """
        # Return yesterday's date in the specified or default timezone
        timezone = tz or cls._timezone
        return pendulum.yesterday(timezone)

    @classmethod
    def parse(
        cls, date_string: str, tz: str | None = None, **kwargs: object,
    ) -> pendulum.DateTime:
        """
        Parse a date string and convert it to the configured timezone.

        Parameters
        ----------
        date_string : str
            Date string to parse.
        tz : str | None, optional
            Specific timezone name. If None, uses the configured default.
        **kwargs
            Additional arguments for pendulum.parse.

        Returns
        -------
        pendulum.DateTime
            Parsed datetime object in the specified or default timezone.
        """
        # Determine the timezone to use
        timezone = tz or cls._timezone
        parsed_dt = pendulum.parse(date_string, **kwargs)

        # Convert to the configured timezone if necessary
        if parsed_dt.timezone_name != timezone:
            return parsed_dt.in_timezone(timezone)
        return parsed_dt

    @classmethod
    def fromTimestamp(
        cls, timestamp: float, tz: str | None = None,
    ) -> pendulum.DateTime:
        """
        Convert a Unix timestamp to a datetime in the configured timezone.

        Parameters
        ----------
        timestamp : int | float
            Unix timestamp to convert.
        tz : str | None, optional
            Specific timezone name. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            Datetime object in the specified or default timezone.
        """
        # Convert the timestamp to a pendulum datetime in the desired timezone
        timezone = tz or cls._timezone
        return pendulum.from_timestamp(timestamp, tz=timezone)

    @classmethod
    def fromDatetime(
        cls,
        dt: stdlib_datetime | pendulum.DateTime,
        tz: str | None = None,
    ) -> pendulum.DateTime:
        """
        Convert a standard datetime object to the configured timezone.

        Parameters
        ----------
        dt : datetime.datetime or pendulum.DateTime
            Datetime object to convert.
        tz : str or None, optional
            Specific timezone name. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            Datetime object in the specified or default timezone.

        Raises
        ------
        TypeError
            If the input type is not supported.
        """
        timezone = tz or cls._timezone

        # Convert standard datetime to pendulum.DateTime in the desired timezone
        if isinstance(dt, stdlib_datetime):
            if dt.tzinfo is None:
                # Naive datetime: assume it is in the configured timezone
                return pendulum.instance(dt, tz=timezone)
            # Aware datetime: convert to the configured timezone
            return pendulum.instance(dt).in_timezone(timezone)
        if isinstance(dt, pendulum.DateTime):
            return dt.in_timezone(timezone)
        error_msg = f"Unsupported type: {type(dt)}"
        raise TypeError(error_msg)

    @classmethod
    def datetime(
        cls,
        year: int,
        month: int = 1,
        day: int = 1,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
        tz: str | None = None,
    ) -> pendulum.DateTime:
        """
        Create a datetime object in the configured timezone.

        Parameters
        ----------
        year : int
            Year component.
        month : int, optional
            Month component, by default 1.
        day : int, optional
            Day component, by default 1.
        hour : int, optional
            Hour component, by default 0.
        minute : int, optional
            Minute component, by default 0.
        second : int, optional
            Second component, by default 0.
        microsecond : int, optional
            Microsecond component, by default 0.
        tz : str | None, optional
            Specific timezone name. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            Datetime object in the specified or default timezone.
        """
        # Use the provided timezone or the class default
        timezone = tz or cls._timezone
        return pendulum.datetime(
            year, month, day, hour, minute, second, microsecond, tz=timezone,
        )

    @classmethod
    def startOfDay(
        cls, dt: pendulum.DateTime | None = None, tz: str | None = None,
    ) -> pendulum.DateTime:
        """
        Return the start of the day (00:00:00).

        Parameters
        ----------
        dt : pendulum.DateTime | None, optional
            The datetime to use. If None, uses the current datetime.
        tz : str | None, optional
            The timezone to use. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            The datetime at the start of the day.
        """
        # Use current datetime if none is provided
        if dt is None:
            dt = cls.now(tz)
        return dt.start_of("day")

    @classmethod
    def endOfDay(
        cls, dt: pendulum.DateTime | None = None, tz: str | None = None,
    ) -> pendulum.DateTime:
        """
        Return the end of the day (23:59:59).

        Parameters
        ----------
        dt : pendulum.DateTime | None, optional
            The datetime to use. If None, uses the current datetime.
        tz : str | None, optional
            The timezone to use. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            The datetime at the end of the day.
        """
        # Use current datetime if none is provided
        if dt is None:
            dt = cls.now(tz)
        return dt.end_of("day")

    @classmethod
    def convertToLocal(
        cls, dt: str | stdlib_datetime | pendulum.DateTime,
    ) -> pendulum.DateTime:
        """
        Convert a date to the configured local timezone.

        Parameters
        ----------
        dt : str | datetime.datetime | pendulum.DateTime
            Date to convert. Accepts string, standard datetime, or pendulum.DateTime.

        Returns
        -------
        pendulum.DateTime
            The date converted to the configured timezone.
        """
        # Parse string to pendulum.DateTime if needed
        if isinstance(dt, str):
            dt = pendulum.parse(dt)
        # Convert standard datetime to pendulum.DateTime if needed
        elif isinstance(dt, stdlib_datetime):
            dt = pendulum.instance(dt)
        # Convert to the configured timezone
        return dt.in_timezone(cls._timezone)

    @classmethod
    def formatLocal(
        cls,
        dt: pendulum.DateTime | None = None,
        format_string: str = "YYYY-MM-DD HH:mm:ss",
    ) -> str:
        """
        Format a date in the local timezone.

        Parameters
        ----------
        dt : pendulum.DateTime | None, optional
            Date to format. If None, uses now().
        format_string : str, optional
            Output format string.

        Returns
        -------
        str
            The formatted date string.
        """
        # Use current datetime if none is provided
        if dt is None:
            dt = cls.now()
        # Ensure dt is a pendulum.DateTime in the local timezone
        if not isinstance(dt, pendulum.DateTime):
            dt = cls.convertToLocal(dt)
        return dt.format(format_string)

    @classmethod
    def startOfWeek(
        cls, dt: pendulum.DateTime | None = None, tz: str | None = None,
    ) -> pendulum.DateTime:
        """
        Return the start of the week (Monday 00:00:00).

        Parameters
        ----------
        dt : pendulum.DateTime | None, optional
            The datetime to use. If None, uses the current datetime.
        tz : str | None, optional
            The timezone to use. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            The datetime at the start of the week.
        """
        # Use current datetime if none is provided
        if dt is None:
            dt = cls.now(tz)
        return dt.start_of("week")

    @classmethod
    def endOfWeek(
        cls, dt: pendulum.DateTime | None = None, tz: str | None = None,
    ) -> pendulum.DateTime:
        """
        Return the end of the week (Sunday 23:59:59).

        Parameters
        ----------
        dt : pendulum.DateTime | None, optional
            The datetime to use. If None, uses the current datetime.
        tz : str | None, optional
            The timezone to use. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            The datetime at the end of the week.
        """
        # Use current datetime if none is provided
        if dt is None:
            dt = cls.now(tz)
        return dt.end_of("week")

    @classmethod
    def startOfMonth(
        cls, dt: pendulum.DateTime | None = None, tz: str | None = None,
    ) -> pendulum.DateTime:
        """
        Return the start of the month (first day at 00:00:00).

        Parameters
        ----------
        dt : pendulum.DateTime | None, optional
            The datetime to use. If None, uses the current datetime.
        tz : str | None, optional
            The timezone to use. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            The datetime at the start of the month.
        """
        # Use current datetime if none is provided
        if dt is None:
            dt = cls.now(tz)
        return dt.start_of("month")

    @classmethod
    def endOfMonth(
        cls, dt: pendulum.DateTime | None = None, tz: str | None = None,
    ) -> pendulum.DateTime:
        """
        Return the end of the month (last day at 23:59:59).

        Parameters
        ----------
        dt : pendulum.DateTime | None, optional
            The datetime to use. If None, uses the current datetime.
        tz : str | None, optional
            The timezone to use. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            The datetime at the end of the month.
        """
        # Use current datetime if none is provided
        if dt is None:
            dt = cls.now(tz)
        return dt.end_of("month")

    @classmethod
    def startOfYear(
        cls, dt: pendulum.DateTime | None = None, tz: str | None = None,
    ) -> pendulum.DateTime:
        """
        Return the start of the year (January 1st at 00:00:00).

        Parameters
        ----------
        dt : pendulum.DateTime | None, optional
            The datetime to use. If None, uses the current datetime.
        tz : str | None, optional
            The timezone to use. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            The datetime at the start of the year.
        """
        # Use current datetime if none is provided
        if dt is None:
            dt = cls.now(tz)
        return dt.start_of("year")

    @classmethod
    def endOfYear(
        cls, dt: pendulum.DateTime | None = None, tz: str | None = None,
    ) -> pendulum.DateTime:
        """
        Return the end of the year (December 31st at 23:59:59).

        Parameters
        ----------
        dt : pendulum.DateTime | None, optional
            The datetime to use. If None, uses the current datetime.
        tz : str | None, optional
            The timezone to use. If None, uses the configured default.

        Returns
        -------
        pendulum.DateTime
            The datetime at the end of the year.
        """
        # Use current datetime if none is provided
        if dt is None:
            dt = cls.now(tz)
        return dt.end_of("year")

    @classmethod
    def addDays(cls, dt: pendulum.DateTime, days: int) -> pendulum.DateTime:
        """
        Add days to a given date.

        Parameters
        ----------
        dt : pendulum.DateTime
            The original date.
        days : int
            Number of days to add.

        Returns
        -------
        pendulum.DateTime
            The resulting date after adding the specified days.
        """
        # Add the specified number of days to the date
        return dt.add(days=days)

    @classmethod
    def addHours(cls, dt: pendulum.DateTime, hours: int) -> pendulum.DateTime:
        """
        Add hours to a given datetime.

        Parameters
        ----------
        dt : pendulum.DateTime
            The original datetime.
        hours : int
            Number of hours to add.

        Returns
        -------
        pendulum.DateTime
            The resulting datetime after adding the specified hours.
        """
        # Add the specified number of hours to the datetime
        return dt.add(hours=hours)

    @classmethod
    def addMinutes(
        cls, dt: pendulum.DateTime, minutes: int,
    ) -> pendulum.DateTime:
        """
        Add minutes to a given datetime.

        Parameters
        ----------
        dt : pendulum.DateTime
            The original datetime.
        minutes : int
            Number of minutes to add.

        Returns
        -------
        pendulum.DateTime
            The resulting datetime after adding the specified minutes.
        """
        # Add the specified number of minutes to the datetime
        return dt.add(minutes=minutes)

    @classmethod
    def diffInDays(
        cls, dt1: pendulum.DateTime, dt2: pendulum.DateTime,
    ) -> int:
        """
        Calculate the difference in days between two dates.

        Parameters
        ----------
        dt1 : pendulum.DateTime
            The first date.
        dt2 : pendulum.DateTime
            The second date.

        Returns
        -------
        int
            The difference in days between the two dates.
        """
        # Calculate the difference in days between dt1 and dt2
        return dt1.diff(dt2).in_days()

    @classmethod
    def diffInHours(
        cls, dt1: pendulum.DateTime, dt2: pendulum.DateTime,
    ) -> int:
        """
        Compute the difference in hours between two dates.

        Parameters
        ----------
        dt1 : pendulum.DateTime
            The first datetime.
        dt2 : pendulum.DateTime
            The second datetime.

        Returns
        -------
        int
            The difference in hours between the two dates.
        """
        return dt1.diff(dt2).in_hours()

    @classmethod
    def isWeekend(
        cls, dt: pendulum.DateTime | None = None,
    ) -> bool:
        """
        Determine if the given date falls on a weekend.

        Parameters
        ----------
        dt : pendulum.DateTime | None, optional
            The datetime to check. If None, uses the current datetime.

        Returns
        -------
        bool
            True if the date is Saturday or Sunday, False otherwise.
        """
        # Use current datetime if none is provided
        if dt is None:
            dt = cls.now()
        return dt.day_of_week in [pendulum.SATURDAY, pendulum.SUNDAY]

    @classmethod
    def isToday(cls, dt: pendulum.DateTime) -> bool:
        """
        Check if the given date is today.

        Parameters
        ----------
        dt : pendulum.DateTime
            The datetime to check.

        Returns
        -------
        bool
            True if the date is today, False otherwise.
        """
        # Both sides must be datetime.date for equality to work correctly.
        # pendulum.today() returns pendulum.DateTime (datetime.datetime subclass),
        # so comparing datetime.date with pendulum.DateTime always yields False.
        today = cls.today()
        return dt.date() == today.date()

    @classmethod
    def isFuture(cls, dt: pendulum.DateTime) -> bool:
        """
        Determine if the given date is in the future.

        Parameters
        ----------
        dt : pendulum.DateTime
            The datetime to check.

        Returns
        -------
        bool
            True if the date is in the future, False otherwise.
        """
        return dt > cls.now()

    @classmethod
    def isPast(cls, dt: pendulum.DateTime) -> bool:
        """
        Determine if the given date is in the past.

        Parameters
        ----------
        dt : pendulum.DateTime
            The datetime to check.

        Returns
        -------
        bool
            True if the date is in the past, False otherwise.
        """
        return dt < cls.now()
