from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    from orionis.console.contracts.schedule_event_listener import IScheduleEventListener

class IEvent(ABC):

    @abstractmethod
    def misfireGraceTime(
        self,
        seconds: int = 60,
    ) -> IEvent:
        """
        Configure misfire grace time for event execution.

        Add a grace period in seconds for missed executions. If the event is
        not triggered within this period after its scheduled time, it will be
        skipped to prevent delayed execution.

        Parameters
        ----------
        seconds : int
            Number of seconds for the misfire grace period. Must be positive.

        Returns
        -------
        IEvent
            Current instance for method chaining.

        Raises
        ------
        CLIOrionisValueError
            If seconds is not a positive integer.
        """

    @abstractmethod
    def purpose(
        self,
        purpose: str,
    ) -> IEvent:
        """
        Assign a purpose description to the scheduled command.

        Set a human-readable purpose or description for the scheduled command.
        The purpose must be a non-empty string. This is useful for
        documentation, logging, or displaying information about the scheduled
        job.

        Parameters
        ----------
        purpose : str
            Purpose or description for the scheduled command. Must be
            non-empty.

        Returns
        -------
        IEvent
            Current instance for method chaining.

        Raises
        ------
        CLIOrionisValueError
            If the provided purpose is not a non-empty string.
        """

    @abstractmethod
    def startDate(
        self,
        start_date: datetime,
    ) -> IEvent:
        """
        Configure the start date for event execution.

        Specify the datetime when the event should begin. The start date must
        be a valid datetime object representing when scheduled execution
        begins.

        Parameters
        ----------
        start_date : datetime
            Datetime when the event should start.

        Returns
        -------
        IEvent
            Current instance for method chaining.
        """

    @abstractmethod
    def endDate(
        self,
        end_date: datetime,
    ) -> IEvent:
        """
        Configure the end date for event execution.

        Define when the event should stop executing. The end date must be a
        valid datetime object representing when scheduled execution stops.

        Parameters
        ----------
        end_date : datetime
            Datetime when the event should stop.

        Returns
        -------
        IEvent
            Current instance for method chaining.
        """

    @abstractmethod
    def randomDelay(
        self,
        max_seconds: int = 10,
    ) -> IEvent:
        """
        Configure random delay for event execution.

        Apply a random delay up to a maximum number of seconds before the
        event is executed. This is useful for distributing load or avoiding
        collisions in scheduled tasks.

        Parameters
        ----------
        max_seconds : int
            Maximum number of seconds to wait before executing the event.

        Returns
        -------
        IEvent
            Current instance for method chaining.
        """

    @abstractmethod
    def maxInstances(
        self,
        max_instances: int,
    ) -> IEvent:
        """
        Configure maximum concurrent instances for the event.

        Specify the maximum number of instances of the event that can run
        concurrently. This prevents resource contention and system overload
        from simultaneous executions.

        Parameters
        ----------
        max_instances : int
            Maximum number of concurrent instances allowed. Must be positive.

        Returns
        -------
        IEvent
            Current instance for method chaining.

        Raises
        ------
        CLIOrionisValueError
            If max_instances is not a positive integer.

        Notes
        -----
        Particularly useful for resource-intensive operations to ensure
        system stability and responsiveness.
        """

    @abstractmethod
    def subscribeListener(
        self,
        listener: IScheduleEventListener,
    ) -> IEvent:
        """
        Attach a listener to the event.

        Subscribe a listener that implements the IScheduleEventListener
        interface to receive notifications when the event is triggered.
        The listener handles event-specific logic during execution.

        Parameters
        ----------
        listener : IScheduleEventListener
            Instance implementing IScheduleEventListener interface.

        Returns
        -------
        IEvent
            Current instance for method chaining.

        Raises
        ------
        CLIOrionisValueError
            If listener does not implement IScheduleEventListener interface.

        Notes
        -----
        The listener is stored internally and used for event-specific logic
        when the event executes.
        """

    @abstractmethod
    def onceAt(
        self,
        date: datetime,
    ) -> bool:
        """
        Schedule the event to execute once at a specific date and time.

        Configure the event to run a single time at the provided date and
        time. Internally, this sets both start and end dates to the
        specified value using a DateTrigger for one-time execution.

        Parameters
        ----------
        date : datetime
            Exact date and time for execution. Must be valid datetime object.

        Returns
        -------
        bool
            True if the scheduling was successfully configured for single
            execution.

        Raises
        ------
        CLIOrionisValueError
            If date is not a valid datetime instance.
        """

    @abstractmethod
    def everySeconds(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule the event at fixed intervals measured in seconds.

        Configure the event to execute repeatedly at specified second
        intervals. Optionally restrict execution to a time window using
        start_date and end_date. Apply random delay if configured.

        Parameters
        ----------
        seconds : int
            Interval in seconds for execution. Must be positive integer.

        Returns
        -------
        bool
            True if interval scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If seconds is not a positive integer.

        Notes
        -----
        Event triggers every specified seconds, respecting configured
        start_date and end_date boundaries.
        """

    @abstractmethod
    def everyFiveSeconds(
        self,
    ) -> bool:
        """
        Schedule the event to run every five seconds.

        Configure the event to execute at five-second intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for five-
            second execution.

        Notes
        -----
        Event triggers at 0, 5, 10, 15, ..., 55 seconds of each minute
        within optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyTenSeconds(
        self,
    ) -> bool:
        """
        Schedule the event to run every ten seconds.

        Configure the event to execute at ten-second intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for ten-
            second execution.

        Notes
        -----
        Event triggers at 0, 10, 20, 30, 40, and 50 seconds of each
        minute within optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFifteenSeconds(
        self,
    ) -> bool:
        """
        Schedule the event to run every fifteen seconds.

        Configure the event to execute at fifteen-second intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            fifteen-second execution.

        Notes
        -----
        Event triggers at 0, 15, 30, and 45 seconds of each minute within
        optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyTwentySeconds(
        self,
    ) -> bool:
        """
        Schedule the event to run every twenty seconds.

        Configure the event to execute at twenty-second intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            twenty-second execution.

        Notes
        -----
        Event triggers at 0, 20, and 40 seconds of each minute within
        optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyTwentyFiveSeconds(
        self,
    ) -> bool:
        """
        Schedule the event to run every twenty-five seconds.

        Configure the event to execute at twenty-five-second intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            twenty-five-second execution.

        Notes
        -----
        Event triggers at 0, 25, and 50 seconds of each minute within
        optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyThirtySeconds(
        self,
    ) -> bool:
        """
        Schedule the event to run every thirty seconds.

        Configure the event to execute at thirty-second intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            thirty-second execution.

        Notes
        -----
        Event triggers at 0 and 30 seconds of each minute within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyThirtyFiveSeconds(
        self,
    ) -> bool:
        """
        Schedule the event to run every thirty-five seconds.

        Configure the event to execute at thirty-five-second intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            thirty-five-second execution.

        Notes
        -----
        Event triggers at 0 and 35 seconds of each minute within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFortySeconds(
        self,
    ) -> bool:
        """
        Schedule the event to run every forty seconds.

        Configure the event to execute at forty-second intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            forty-second execution.

        Notes
        -----
        Event triggers at 0 and 40 seconds of each minute within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFortyFiveSeconds(
        self,
    ) -> bool:
        """
        Schedule the event to run every forty-five seconds.

        Configure the event to execute at forty-five-second intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            forty-five-second execution.

        Notes
        -----
        Event triggers at 0 and 45 seconds of each minute within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFiftySeconds(
        self,
    ) -> bool:
        """
        Schedule the event to run every fifty seconds.

        Configure the event to execute at fifty-second intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            fifty-second execution.

        Notes
        -----
        Event triggers at 0 and 50 seconds of each minute within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFiftyFiveSeconds(
        self,
    ) -> bool:
        """
        Schedule the event to run every fifty-five seconds.

        Configure the event to execute at fifty-five-second intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            fifty-five-second execution.

        Notes
        -----
        Event triggers at 0 and 55 seconds of each minute within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyMinute(
        self,
        minutes: int,
    ) -> bool:
        """
        Schedule the event to run at fixed intervals measured in minutes.

        Configure the event to execute repeatedly at specified minute
        intervals. Optionally restrict execution to time window using
        start_date and end_date. Apply random delay if configured.

        Parameters
        ----------
        minutes : int
            Interval in minutes for execution. Must be positive integer.

        Returns
        -------
        bool
            True if interval scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If minutes is not a positive integer.

        Notes
        -----
        Event triggers every specified minutes, respecting configured
        start_date and end_date boundaries. Jitter applied if set.
        """

    @abstractmethod
    def everyMinuteAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule the event to run every minute at specific second.

        Configure the event to execute at specified second (0-59) of every
        minute. Previously configured random delay (jitter) is ignored for
        this schedule.

        Parameters
        ----------
        seconds : int
            Specific second (0-59) of each minute for execution.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If seconds is not an integer between 0 and 59 (inclusive).

        Notes
        -----
        Event triggers at specified second of every minute with no jitter
        applied.
        """

    @abstractmethod
    def everyMinutesAt(
        self,
        minutes: int,
        seconds: int,
    ) -> bool:
        """
        Schedule the event to run at specific second of minute intervals.

        Configure the event to execute at specified second (0-59) of every
        minutes interval. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Parameters
        ----------
        minutes : int
            Interval in minutes for execution. Must be positive integer.
        seconds : int
            Specific second (0-59) of each interval for execution.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If minutes is not positive integer or seconds not in range 0-59.

        Notes
        -----
        Event triggers at specified second of every minutes interval within
        optional scheduling window.
        """

    @abstractmethod
    def everyFiveMinutes(
        self,
    ) -> bool:
        """
        Schedule the event to run every five minutes.

        Configure the event to execute at five-minute intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            five-minute execution.

        Notes
        -----
        Event triggers at 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, and
        55 minutes of each hour within optional scheduling window. Jitter
        applied if set.
        """

    @abstractmethod
    def everyFiveMinutesAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule the event to run every five minutes at specific second.

        Configure the event to execute at specified second (0-59) of every
        five-minute interval. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Parameters
        ----------
        seconds : int
            Specific second (0-59) of each five-minute interval for execution.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If seconds is not an integer between 0 and 59 (inclusive).

        Notes
        -----
        Event triggers at specified second of every five-minute interval
        within optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyTenMinutes(
        self,
    ) -> bool:
        """
        Schedule the event to run every ten minutes.

        Configure the event to execute at ten-minute intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            ten-minute execution.

        Notes
        -----
        Event triggers at 0, 10, 20, 30, 40, and 50 minutes of each hour
        within optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyTenMinutesAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule the event to run every ten minutes at specific second.

        Configure the event to execute at specified second (0-59) of every
        ten-minute interval. Previously configured random delay (jitter) is
        ignored for this schedule. Optionally restrict scheduling window
        with start_date and end_date.

        Parameters
        ----------
        seconds : int
            Specific second (0-59) of each ten-minute interval for execution.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If seconds is not an integer between 0 and 59 (inclusive).

        Notes
        -----
        Event triggers at specified second of every ten-minute interval
        with no jitter applied. Schedule respects configured start_date
        and end_date.
        """

    @abstractmethod
    def everyFifteenMinutes(
        self,
    ) -> bool:
        """
        Schedule the event to run every fifteen minutes.

        Configure the event to execute at fifteen-minute intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            fifteen-minute execution.

        Notes
        -----
        Event triggers at 0, 15, 30, and 45 minutes of each hour within
        optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFifteenMinutesAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule the event to run every fifteen minutes at specific second.

        Configure the event to execute at specified second (0-59) of every
        fifteen-minute interval. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Parameters
        ----------
        seconds : int
            Specific second (0-59) of each fifteen-minute interval for
            execution.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If seconds is not an integer between 0 and 59 (inclusive).

        Notes
        -----
        Event triggers at specified second of every fifteen-minute interval
        within optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyTwentyMinutes(
        self,
    ) -> bool:
        """
        Schedule the event to run every twenty minutes.

        Configure the event to execute at twenty-minute intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            twenty-minute execution.

        Notes
        -----
        Event triggers at 0, 20, and 40 minutes of each hour within
        optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyTwentyMinutesAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule the event to run every twenty minutes at specific second.

        Configure the event to execute at specified second (0-59) of every
        twenty-minute interval. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Parameters
        ----------
        seconds : int
            Specific second (0-59) of each twenty-minute interval for
            execution.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If seconds is not an integer between 0 and 59 (inclusive).

        Notes
        -----
        Event triggers at specified second of every twenty-minute interval
        within optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyTwentyFiveMinutes(
        self,
    ) -> bool:
        """
        Schedule the event to run every twenty-five minutes.

        Configure the event to execute at twenty-five-minute intervals using
        an IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            twenty-five-minute execution.

        Notes
        -----
        Event triggers at 0, 25, and 50 minutes of each hour within
        optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyTwentyFiveMinutesAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule event to run every twenty-five minutes at a specific second.

        Set the event to execute at the given second (0-59) of each
        twenty-five-minute interval. Restrict the schedule with
        `start_date` and `end_date` if needed. Apply random delay if set.

        Parameters
        ----------
        seconds : int
            Specific second (0-59) of each twenty-five-minute interval.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises
            CLIOrionisValueError if seconds is not in range [0, 59].

        Raises
        ------
        CLIOrionisValueError
            Raised if seconds is not an integer between 0 and 59.

        Notes
        -----
        The event triggers at the specified second of every twenty-five-minute
        interval. Jitter is applied if set.
        """

    @abstractmethod
    def everyThirtyMinutes(
        self,
    ) -> bool:
        """
        Schedule the event to run every thirty minutes.

        Configure the event to execute at thirty-minute intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            thirty-minute execution.

        Notes
        -----
        Event triggers at 0 and 30 minutes of each hour within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyThirtyMinutesAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule the event to run every thirty minutes at specific second.

        Configure the event to execute at specified second (0-59) of every
        thirty-minute interval. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Parameters
        ----------
        seconds : int
            Specific second (0-59) of each thirty-minute interval for
            execution.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If seconds is not an integer between 0 and 59 (inclusive).

        Notes
        -----
        Event triggers at specified second of every thirty-minute interval
        within optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyThirtyFiveMinutes(
        self,
    ) -> bool:
        """
        Schedule the event to run every thirty-five minutes.

        Configure the event to execute at thirty-five-minute intervals using
        an IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            thirty-five-minute execution.

        Notes
        -----
        Event triggers at 0 and 35 minutes of each hour within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyThirtyFiveMinutesAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule the event to run every 35 minutes at specific second.

        Configure the event to execute at specified second (0-59) of every
        35-minute interval. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Parameters
        ----------
        seconds : int
            Specific second (0-59) of each 35-minute interval for execution.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If seconds is not an integer between 0 and 59 (inclusive).

        Notes
        -----
        Event triggers at specified second of every 35-minute interval
        within optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFortyMinutes(
        self,
    ) -> bool:
        """
        Schedule the event to run every forty minutes.

        Configure the event to execute at forty-minute intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            forty-minute execution.

        Notes
        -----
        Event triggers at 0 and 40 minutes of each hour within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFortyMinutesAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule the event to run every forty minutes at specific second.

        Configure the event to execute at specified second (0-59) of every
        forty-minute interval. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Parameters
        ----------
        seconds : int
            Specific second (0-59) of each forty-minute interval for
            execution.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If seconds is not an integer between 0 and 59 (inclusive).

        Notes
        -----
        Event triggers at specified second of every forty-minute interval
        within optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFortyFiveMinutes(
        self,
    ) -> bool:
        """
        Schedule the event to run every forty-five minutes.

        Configure the event to execute at forty-five-minute intervals using
        an IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            forty-five-minute execution.

        Notes
        -----
        Event triggers at 0 and 45 minutes of each hour within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFortyFiveMinutesAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule event to run every forty-five minutes at a specific second.

        Configure execution at the given second (0-59) of each forty-five-minute
        interval. Optionally restrict the schedule with start_date and end_date.
        Apply random delay if configured.

        Parameters
        ----------
        seconds : int
            Specific second (0-59) of each forty-five-minute interval.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if seconds is not in range [0, 59].

        Raises
        ------
        CLIOrionisValueError
            Raised if seconds is not an integer between 0 and 59.

        Notes
        -----
        The event triggers at the specified second of every forty-five-minute
        interval. Jitter is applied if set.
        """

    @abstractmethod
    def everyFiftyMinutes(
        self,
    ) -> bool:
        """
        Schedule the event to run every fifty minutes.

        Configure the event to execute at fifty-minute intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            fifty-minute execution.

        Notes
        -----
        Event triggers at 0 and 50 minutes of each hour within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFiftyMinutesAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule the event to run every fifty minutes at specific second.

        Configure the event to execute at specified second (0-59) of every
        fifty-minute interval. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Parameters
        ----------
        seconds : int
            Specific second (0-59) of each fifty-minute interval for
            execution.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If seconds is not an integer between 0 and 59 (inclusive).

        Notes
        -----
        Event triggers at specified second of every fifty-minute interval
        within optional scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFiftyFiveMinutes(
        self,
    ) -> bool:
        """
        Schedule the event to run every fifty-five minutes.

        Configure the event to execute at fifty-five-minute intervals using
        an IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for
            fifty-five-minute execution.

        Notes
        -----
        Event triggers at 0 and 55 minutes of each hour within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyFiftyFiveMinutesAt(
        self,
        seconds: int,
    ) -> bool:
        """
        Schedule the event to run every 55 minutes at specific second.

        Configure event execution at specified second of 55th minute. Used
        as wrapper around everyMinutesAt with minute parameter fixed at 55.

        Parameters
        ----------
        seconds : int
            Specific second of 55th minute for event trigger.

        Returns
        -------
        bool
            True if current time matches schedule (55 minutes past hour at
            specified second), False otherwise.

        Notes
        -----
        Wrapper around everyMinutesAt with minute parameter fixed at 55.
        """

    @abstractmethod
    def hourly(
        self,
    ) -> bool:
        """
        Schedule the event to run every hour.

        Configure the event to execute once every hour using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring hourly scheduling.

        Notes
        -----
        Event triggers at start of every hour within optional scheduling
        window. Jitter applied if set.
        """

    @abstractmethod
    def hourlyAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule the event to run every hour at specific minute and second.

        Configure the event to execute once every hour at specified minute
        and second. Optionally restrict scheduling window with start_date
        and end_date. Apply random delay if configured.

        Parameters
        ----------
        minute : int
            Minute of hour for event execution. Must be in range [0, 59].
        second : int, optional
            Second of minute for event execution. Must be in range [0, 59].
            Default is 0.

        Returns
        -------
        bool
            True if hourly scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If minute or second are not integers within valid ranges [0, 59].

        Notes
        -----
        Event triggers every hour at specified minute and second within
        optional scheduling window.
        """

    @abstractmethod
    def everyOddHours(
        self,
    ) -> bool:
        """
        Schedule the event to run at every odd hour of day.

        Configure the event to execute at every odd-numbered hour using a
        CronTrigger. Optionally restrict schedule with start_date and
        end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling.

        Notes
        -----
        Event triggers at hours 1, 3, 5, ..., 23 of each day (1 AM, 3 AM,
        5 AM, ..., 11 PM).
        """

    @abstractmethod
    def everyEvenHours(
        self,
    ) -> bool:
        """
        Schedule the event to run at every even hour of day.

        Configure the event to execute at every even-numbered hour using a
        CronTrigger. Optionally restrict schedule with start_date and
        end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling.

        Notes
        -----
        Event triggers at hours 0, 2, 4, ..., 22 of each day (12 AM, 2 AM,
        4 AM, ..., 10 PM).
        """

    @abstractmethod
    def everyHours(
        self,
        hours: int,
    ) -> bool:
        """
        Schedule the event to run at fixed intervals measured in hours.

        Configure the event to execute repeatedly at specified hour
        intervals. Optionally restrict execution to time window using
        start_date and end_date. Apply random delay if configured.

        Parameters
        ----------
        hours : int
            Interval in hours for execution. Must be positive integer.

        Returns
        -------
        bool
            True if interval scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If hours is not a positive integer.

        Notes
        -----
        Event triggers every specified hours, respecting configured
        start_date and end_date boundaries. Jitter applied if set.
        """

    @abstractmethod
    def everyHoursAt(
        self,
        hours: int,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule the event to run every hour at specific minute and second.

        Configure the event to execute once every hour at specified minute
        and second. Optionally restrict schedule with start_date and
        end_date. Jitter (random delay) is not applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of hour for event execution. Must be in range [0, 59].
        second : int, optional
            Second of minute for event execution. Must be in range [0, 59].
            Default is 0.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If minute or second are not integers within valid ranges [0, 59].

        Notes
        -----
        Event triggers every hour at specified minute and second within
        optional scheduling window.
        """

    @abstractmethod
    def everyTwoHours(
        self,
    ) -> bool:
        """
        Schedule the event to run every two hours.

        Configure the event to execute at two-hour intervals using the
        everyHours method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling by delegating to
            everyHours.
        """

    @abstractmethod
    def everyTwoHoursAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every two hours at a specific minute and second.

        Set the event to execute every two hours at the given minute and second.
        Restrict the schedule with start_date and end_date if needed. Jitter is
        not applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of the hour for execution. Must be in [0, 59].
        second : int, optional
            Second of the minute for execution. Must be in [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if minute or second are not integers within valid ranges.

        Notes
        -----
        The event triggers every two hours at the specified minute and second
        within the optional scheduling window.
        """

    @abstractmethod
    def everyThreeHours(
        self,
    ) -> bool:
        """
        Schedule the event to run every three hours.

        Configure the event to execute at three-hour intervals using the
        everyHours method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling by delegating to
            everyHours.
        """

    @abstractmethod
    def everyThreeHoursAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every three hours at a specific minute and second.

        Set the event to execute every three hours at the given minute and
        second. Restrict the schedule with start_date and end_date if needed.
        Jitter is not applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of the hour for execution. Must be in [0, 59].
        second : int, optional
            Second of the minute for execution. Must be in [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if minute or second are not integers within valid ranges.

        Notes
        -----
        The event triggers every three hours at the specified minute and second
        within the optional scheduling window.
        """

    @abstractmethod
    def everyFourHours(
        self,
    ) -> bool:
        """
        Schedule the event to run every four hours.

        Configure the event to execute at four-hour intervals using the
        everyHours method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling by delegating to
            everyHours.

        Notes
        -----
        Event triggers at 0:00, 4:00, 8:00, ..., 20:00 of each day.
        """

    @abstractmethod
    def everyFourHoursAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every four hours at a specific minute and second.

        Set the event to execute every four hours at the given minute and second.
        Restrict the schedule with start_date and end_date if needed. Jitter is
        not applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of the hour for execution. Must be in [0, 59].
        second : int, optional
            Second of the minute for execution. Must be in [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if minute or second are not integers within valid ranges.

        Notes
        -----
        The event triggers every four hours at the specified minute and second
        within the optional scheduling window.
        """

    @abstractmethod
    def everyFiveHours(
        self,
    ) -> bool:
        """
        Schedule the event to run every five hours.

        Configure the event to execute at five-hour intervals using the
        everyHours method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling by delegating to
            everyHours.

        Notes
        -----
        Event triggers at 0:00, 5:00, 10:00, 15:00, and 20:00 of each day.
        """

    @abstractmethod
    def everyFiveHoursAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every five hours at a specific minute and second.

        Set the event to execute every five hours at the given minute and
        second. Optionally restrict the schedule with start_date and end_date.
        Jitter (random delay) is not applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of the hour for execution. Must be in [0, 59].
        second : int, optional
            Second of the minute for execution. Must be in [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Notes
        -----
        The event triggers every five hours at the specified minute and second
        within the optional scheduling window.
        """

    @abstractmethod
    def everySixHours(
        self,
    ) -> bool:
        """
        Schedule the event to run every six hours.

        Configure the event to execute at six-hour intervals using the
        everyHours method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling by delegating to
            everyHours.

        Notes
        -----
        Event triggers at 0:00, 6:00, 12:00, and 18:00 of each day.
        """

    @abstractmethod
    def everySixHoursAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every six hours at a specific minute and second.

        Set the event to execute every six hours at the given minute and second.
        Restrict the schedule with start_date and end_date if needed. Jitter is
        not applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of the hour for execution. Must be in [0, 59].
        second : int, optional
            Second of the minute for execution. Must be in [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if minute or second are not integers within valid ranges.

        Notes
        -----
        The event triggers every six hours at the specified minute and second
        within the optional scheduling window.
        """

    @abstractmethod
    def everySevenHours(
        self,
    ) -> bool:
        """
        Schedule the event to run every seven hours.

        Configure the event to execute at seven-hour intervals using the
        everyHours method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling by delegating to
            everyHours.

        Notes
        -----
        Event triggers at 0:00, 7:00, 14:00, and 21:00 of each day.
        """

    @abstractmethod
    def everySevenHoursAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every seven hours at a specific minute and second.

        Set the event to execute every seven hours at the given minute and
        second. Optionally restrict the schedule with start_date and end_date.
        Jitter (random delay) is not applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of the hour for event execution. Must be in [0, 59].
        second : int, optional
            Second of the minute for event execution. Must be in [0, 59].
            Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if minute or second are not integers within valid ranges.

        Notes
        -----
        The event triggers every seven hours at the specified minute and second
        within the optional scheduling window.
        """

    @abstractmethod
    def everyEightHours(
        self,
    ) -> bool:
        """
        Schedule the event to run every eight hours.

        Configure the event to execute at eight-hour intervals using the
        everyHours method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling by delegating to
            everyHours.

        Notes
        -----
        Event triggers at 0:00, 8:00, 16:00 of each day.
        """

    @abstractmethod
    def everyEightHoursAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every eight hours at a specific minute and second.

        Set the event to execute every eight hours at the given minute and
        second. Optionally restrict the schedule with start_date and end_date.
        Jitter (random delay) is not applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of the hour for event execution. Must be in [0, 59].
        second : int, optional
            Second of the minute for event execution. Must be in [0, 59].
            Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if minute or second are not integers within valid ranges.

        Notes
        -----
        The event triggers every eight hours at the specified minute and second
        within the optional scheduling window.
        """

    @abstractmethod
    def everyNineHours(
        self,
    ) -> bool:
        """
        Schedule the event to run every nine hours.

        Configure the event to execute at nine-hour intervals using the
        everyHours method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling by delegating to
            everyHours.

        Notes
        -----
        Event triggers at 0:00, 9:00, and 18:00 of each day.
        """

    @abstractmethod
    def everyNineHoursAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every nine hours at a specific minute and second.

        Set the event to execute every nine hours at the given minute and second.
        Restrict the schedule with start_date and end_date if needed. Jitter is not
        applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of the hour for event execution. Must be in [0, 59].
        second : int, optional
            Second of the minute for event execution. Must be in [0, 59].
            Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if minute or second are not integers within valid ranges.

        Notes
        -----
        The event triggers every nine hours at the specified minute and second
        within the optional scheduling window.
        """

    @abstractmethod
    def everyTenHours(
        self,
    ) -> bool:
        """
        Schedule the event to run every ten hours.

        Configure the event to execute at ten-hour intervals using the
        everyHours method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling by delegating to
            everyHours.

        Notes
        -----
        Event triggers at 0:00, 10:00, and 20:00 of each day.
        """

    @abstractmethod
    def everyTenHoursAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every ten hours at a specific minute and second.

        Set the event to execute every ten hours at the given minute and second.
        Restrict the schedule with start_date and end_date if needed. Jitter is not
        applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of the hour for event execution. Must be in [0, 59].
        second : int, optional
            Second of the minute for event execution. Must be in [0, 59].
            Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if minute or second are not integers within valid ranges.

        Notes
        -----
        The event triggers every ten hours at the specified minute and second
        within the optional scheduling window.
        """

    @abstractmethod
    def everyElevenHours(
        self,
    ) -> bool:
        """
        Schedule the event to run every eleven hours.

        Configure the event to execute at eleven-hour intervals using the
        everyHours method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring scheduling by delegating to
            everyHours.

        Notes
        -----
        Event triggers at 0:00, 11:00, and 22:00 of each day.
        """

    @abstractmethod
    def everyElevenHoursAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every eleven hours at a specific minute and second.

        Set the event to execute every eleven hours at the given minute and
        second. Optionally restrict the schedule with start_date and end_date.
        Jitter is not applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of the hour for event execution. Must be in [0, 59].
        second : int, optional
            Second of the minute for event execution. Must be in [0, 59].
            Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if minute or second are not integers within valid ranges.

        Notes
        -----
        The event triggers every eleven hours at the specified minute and second
        within the optional scheduling window.
        """

    @abstractmethod
    def everyTwelveHours(
        self,
    ) -> bool:
        """
        Schedule the event to run every twelve hours.

        Configure the event to execute at twelve-hour intervals using the
        everyHours method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Notes
        -----
        Event triggers at 0:00 and 12:00 of each day.
        """

    @abstractmethod
    def everyTwelveHoursAt(
        self,
        minute: int,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every twelve hours at a specific minute and second.

        Set the event to execute every twelve hours at the given minute and second.
        Restrict the schedule with start_date and end_date if needed. Jitter is not
        applied for this schedule.

        Parameters
        ----------
        minute : int
            Minute of the hour for event execution. Must be in range [0, 59].
        second : int, optional
            Second of the minute for event execution. Must be in range [0, 59].
            Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if minute or second are not integers within valid ranges.

        Notes
        -----
        The event triggers every twelve hours at the specified minute and second
        within the optional scheduling window.
        """

    @abstractmethod
    def daily(
        self,
    ) -> bool:
        """
        Schedule the event to run once per day.

        Configure the event to execute at one-day intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True after successfully configuring interval trigger for daily
            execution.

        Notes
        -----
        Event triggers once every day within optional scheduling window.
        Jitter applied if set.
        """

    @abstractmethod
    def dailyAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run daily at specific hour, minute, and second.

        Configure the event to execute once daily at the specified hour,
        minute, and second. Optionally restrict schedule with start_date
        and end_date. Apply random delay if configured.

        Parameters
        ----------
        hour : int
            Hour of the day when event should run. Range [0, 23].
        minute : int, optional
            Minute of the hour when event should run. Range [0, 59].
            Default is 0.
        second : int, optional
            Second of the minute when event should run. Range [0, 59].
            Default is 0.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If hour, minute, or second are not integers within valid ranges.

        Notes
        -----
        Event triggers once per day at specified time within optional
        scheduling window. Jitter applied if set.
        """

    @abstractmethod
    def everyDays(
        self,
        days: int,
    ) -> bool:
        """
        Schedule the event at fixed intervals measured in days.

        Configure the event to execute repeatedly at specified day intervals.
        The interval must be positive. Optionally restrict execution to a
        time window using start_date and end_date. Apply random delay if
        configured.

        Parameters
        ----------
        days : int
            Interval in days for execution. Must be positive integer.

        Returns
        -------
        bool
            True if interval scheduling was successfully configured.

        Raises
        ------
        CLIOrionisValueError
            If days is not a positive integer.

        Notes
        -----
        Event triggers every specified days, respecting configured
        start_date and end_date boundaries. Jitter applied if set.
        """

    @abstractmethod
    def everyDaysAt(
        self,
        days: int,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every N days at a specific time.

        Parameters
        ----------
        days : int
            Number of days between executions. Must be positive.
        hour : int
            Hour of the day [0, 23].
        minute : int, optional
            Minute of the hour [0, 59]. Default is 0.
        second : int, optional
            Second of the minute [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Returns False if not set.
            Raises CLIOrionisValueError if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if `days`, `hour`, `minute`, or `second` are out of valid ranges.

        Notes
        -----
        The event is triggered every N days at the specified time. Jitter is applied
        if set. Scheduling window can be restricted by `start_date` and `end_date`.
        """

    @abstractmethod
    def everyTwoDays(
        self,
    ) -> bool:
        """
        Schedule the event to run every two days.

        Configure the event to execute at two-day intervals using an
        IntervalTrigger. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True if scheduling was successfully configured.
        """

    @abstractmethod
    def everyTwoDaysAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every two days at a specific time.

        Set the event to execute every two days at the given hour, minute,
        and second. Restrict the schedule with start_date and end_date if
        needed. Apply random delay if configured.

        Parameters
        ----------
        hour : int
            Hour of the day in range [0, 23].
        minute : int, optional
            Minute of the hour in range [0, 59]. Default is 0.
        second : int, optional
            Second of the minute in range [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Notes
        -----
        The event is triggered every two days at the specified time. Jitter is
        applied if set.
        """

    @abstractmethod
    def everyThreeDays(
        self,
    ) -> bool:
        """
        Schedule the event to run every three days.

        Configure the event to execute at three-day intervals using the
        everyDays method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Notes
        -----
        Event triggers every three days, respecting configured start_date
        and end_date boundaries. Jitter applied if set.
        """

    @abstractmethod
    def everyThreeDaysAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every three days at a specific time.

        Set the event to execute every three days at the given hour, minute,
        and second. Restrict the schedule with `start_date` and `end_date`
        if needed. Apply random delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day in range [0, 23].
        minute : int, optional
            Minute of the hour in range [0, 59]. Default is 0.
        second : int, optional
            Second of the minute in range [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Notes
        -----
        The event is triggered every three days at the specified time. Jitter is
        applied if set.
        """

    @abstractmethod
    def everyFourDays(
        self,
    ) -> bool:
        """
        Schedule the event to run every four days.

        Configure the event to execute at four-day intervals using the
        everyDays method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Notes
        -----
        Event triggers every four days, respecting configured start_date
        and end_date boundaries. Jitter applied if set.
        """

    @abstractmethod
    def everyFourDaysAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every four days at a specific time.

        Set the event to execute every four days at the specified hour,
        minute, and second. Restrict the schedule with start_date and
        end_date if needed. Apply random delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day in range [0, 23].
        minute : int, optional
            Minute of the hour in range [0, 59]. Default is 0.
        second : int, optional
            Second of the minute in range [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Notes
        -----
        The event is triggered every four days at the specified time. Jitter is
        applied if set.
        """

    @abstractmethod
    def everyFiveDays(
        self,
    ) -> bool:
        """
        Schedule the event to run every five days.

        Configure the event to execute at five-day intervals using the
        everyDays method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Notes
        -----
        Event triggers every five days, respecting configured start_date
        and end_date boundaries. Jitter applied if set.
        """

    @abstractmethod
    def everyFiveDaysAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every five days at a specific time.

        Set the event to execute every five days at the specified hour,
        minute, and second. Optionally restrict the schedule with
        start_date and end_date. Apply random delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day in range [0, 23].
        minute : int, optional
            Minute of the hour in range [0, 59]. Default is 0.
        second : int, optional
            Second of the minute in range [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if hour, minute, or second are out of valid ranges.

        Notes
        -----
        The event is triggered every five days at the specified time. Jitter is
        applied if set.
        """

    @abstractmethod
    def everySixDays(
        self,
    ) -> bool:
        """
        Schedule the event to run every six days.

        Configure the event to execute at six-day intervals using the
        everyDays method. Optionally restrict scheduling window with
        start_date and end_date. Apply random delay if configured.

        Returns
        -------
        bool
            True if scheduling was successfully configured.

        Notes
        -----
        Event triggers every six days, respecting configured start_date
        and end_date boundaries. Jitter applied if set.
        """

    @abstractmethod
    def everySixDaysAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every six days at a specific time.

        Set the event to execute every six days at the specified hour, minute,
        and second. Optionally restrict the schedule with start_date and end_date.
        Apply random delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day in range [0, 23].
        minute : int, optional
            Minute of the hour in range [0, 59]. Default is 0.
        second : int, optional
            Second of the minute in range [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError
            if parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if hour, minute, or second are out of valid ranges.

        Notes
        -----
        The event is triggered every six days at the specified time. Jitter is
        applied if set.
        """

    @abstractmethod
    def everySevenDays(
        self,
    ) -> bool:
        """
        Schedule event to run every seven days.

        Use the `everyDays` method to set a seven-day interval for event execution.
        Restrict the scheduling window with `start_date` and `end_date` if needed.
        Apply random delay (jitter) if configured.

        Returns
        -------
        bool
            Always returns True after delegating scheduling to `everyDays`.
        """

    @abstractmethod
    def everySevenDaysAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Configure event to run every seven days at a specific time.

        Set the event to execute every seven days at the given hour, minute, and
        second. Restrict the schedule with `start_date` and `end_date` if needed.
        Apply random delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day in range [0, 23].
        minute : int, optional
            Minute of the hour in range [0, 59]. Default is 0.
        second : int, optional
            Second of the minute in range [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError if
            parameters are invalid.
        """

    @abstractmethod
    def everyMondayAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every Monday at a specific hour, minute, and second.

        Restrict schedule using `start_date` and `end_date` if needed. Apply random
        delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day in range [0, 23].
        minute : int, optional
            Minute of the hour in range [0, 59]. Default is 0.
        second : int, optional
            Second of the minute in range [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError if
            parameters are invalid.
        """

    @abstractmethod
    def everyTuesdayAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every Tuesday at a specific hour, minute, and second.

        Restrict the schedule using `start_date` and `end_date` if needed. Apply
        random delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day in range [0, 23].
        minute : int, optional
            Minute of the hour in range [0, 59]. Default is 0.
        second : int, optional
            Second of the minute in range [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError if
            parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if `hour`, `minute`, or `second` are out of valid ranges.

        Notes
        -----
        The event is triggered every Tuesday at the specified time. Jitter is applied
        if set.
        """

    @abstractmethod
    def everyWednesdayAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every Wednesday at a specific hour, minute, and second.

        Restrict the schedule using `start_date` and `end_date` if needed. Apply
        random delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day in range [0, 23].
        minute : int, optional
            Minute of the hour in range [0, 59]. Default is 0.
        second : int, optional
            Second of the minute in range [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError if
            parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if `hour`, `minute`, or `second` are out of valid ranges.

        Notes
        -----
        The event is triggered every Wednesday at the specified time. Jitter is applied
        if set.
        """

    @abstractmethod
    def everyThursdayAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every Thursday at a specific hour, minute, and second.

        Restrict the schedule using `start_date` and `end_date` if needed. Apply
        random delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day in range [0, 23].
        minute : int, optional
            Minute of the hour in range [0, 59]. Default is 0.
        second : int, optional
            Second of the minute in range [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError if
            parameters are invalid.
        """

    @abstractmethod
    def everyFridayAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every Friday at a specific hour, minute, and second.

        Restrict the schedule with `start_date` and `end_date` if needed. Apply
        random delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day [0, 23].
        minute : int, optional
            Minute of the hour [0, 59]. Default is 0.
        second : int, optional
            Second of the minute [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError if
            parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if `hour`, `minute`, or `second` are out of valid ranges.

        Notes
        -----
        The event is triggered every Friday at the specified time. Jitter is applied
        if set.
        """

    @abstractmethod
    def everySaturdayAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every Saturday at a specific time.

        Set the event to execute weekly on Saturday at the given hour, minute,
        and second. Restrict the schedule with `start_date` and `end_date` if
        needed. Apply random delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day [0, 23].
        minute : int, optional
            Minute of the hour [0, 59]. Default is 0.
        second : int, optional
            Second of the minute [0, 59]. Default is 0.

        Returns
        -------
        bool
            Return True if scheduling is configured. Raise CLIOrionisValueError if
            parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if `hour`, `minute`, or `second` are out of valid ranges.

        Notes
        -----
        The event is triggered every Saturday at the specified time. Jitter is
        applied if set.
        """

    @abstractmethod
    def everySundayAt(
        self,
        hour: int,
        minute: int = 0,
        second: int = 0,
    ) -> bool:
        """
        Schedule event to run every Sunday at a specific time.

        Set the event to execute weekly on Sunday at the given hour, minute, and
        second. Restrict the schedule with `start_date` and `end_date` if needed.
        Apply random delay (jitter) if configured.

        Parameters
        ----------
        hour : int
            Hour of the day [0, 23].
        minute : int, optional
            Minute of the hour [0, 59]. Default is 0.
        second : int, optional
            Second of the minute [0, 59]. Default is 0.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError if
            parameters are invalid.

        Raises
        ------
        CLIOrionisValueError
            Raised if `hour`, `minute`, or `second` are out of valid ranges.

        Notes
        -----
        The event is triggered every Sunday at the specified time. Jitter is applied
        if set.
        """

    @abstractmethod
    def weekly(
        self,
    ) -> bool:
        """
        Schedule event to run every week.

        Set the event to execute at a fixed interval of one week using an
        IntervalTrigger. Optionally restrict the schedule with start_date and
        end_date. Jitter is applied if configured.

        Returns
        -------
        bool
            Returns True after configuring the interval trigger for weekly execution.
        """

    @abstractmethod
    def everyWeeks(
        self,
        weeks: int,
    ) -> bool:
        """
        Schedule event at fixed weekly intervals.

        Set the event to run every `weeks` weeks. The interval must be a positive
        integer. Optionally, restrict the schedule using `start_date` and `end_date`.
        Jitter is applied if configured.

        Parameters
        ----------
        weeks : int
            Interval in weeks. Must be a positive integer.

        Returns
        -------
        bool
            Returns True if scheduling is configured. Raises CLIOrionisValueError if
            `weeks` is not a positive integer.

        Raises
        ------
        CLIOrionisValueError
            Raised if `weeks` is not a positive integer.

        Notes
        -----
        The event is triggered every `weeks` weeks, using any configured start and end
        dates. Jitter is applied if set.
        """

    @abstractmethod
    def every(
        self,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ) -> bool:
        """
        Configure the event to run at fixed intervals.

        Set the schedule to execute at intervals defined by weeks, days, hours,
        minutes, and seconds. At least one parameter must be greater than zero.
        If all parameters are zero or any is negative, an exception is raised.

        Parameters
        ----------
        weeks : int, optional
            Interval in weeks. Must be non-negative. Default is 0.
        days : int, optional
            Interval in days. Must be non-negative. Default is 0.
        hours : int, optional
            Interval in hours. Must be non-negative. Default is 0.
        minutes : int, optional
            Interval in minutes. Must be non-negative. Default is 0.
        seconds : int, optional
            Interval in seconds. Must be non-negative. Default is 0.

        Returns
        -------
        bool
            Returns True if the interval scheduling is configured successfully.
            Returns False if the trigger is not set due to invalid input.

        Raises
        ------
        CLIOrionisValueError
            Raised if all parameters are zero or any parameter is negative.

        Notes
        -----
        The event will be triggered at the specified interval, using any
        configured start and end dates. Jitter is applied if set.
        """

    # ruff: noqa: PLR0913
    @abstractmethod
    def cron(
        self,
        year: str | None = None,
        month: str | None = None,
        day: str | None = None,
        week: str | None = None,
        day_of_week: str | None = None,
        hour: str | None = None,
        minute: str | None = None,
        second: str | None = None,
    ) -> bool:
        """
        Schedule the event using a CRON-like expression.

        This method configures the event to execute according to cron rules,
        allowing highly customizable schedules (e.g., every Monday at 8am).

        Parameters
        ----------
        year, month, day, week, day_of_week, hour, minute, second : str | None
            Cron-like expressions defining when the job should run.
            Examples: "*/5" (every 5 units), "1-5" (range), "0,15,30,45" (list).

        Returns
        -------
        bool
            True if the cron scheduling was successfully configured.
        """
