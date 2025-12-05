from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from orionis.support.entities.base import BaseEntity

if TYPE_CHECKING:
    from datetime import datetime
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.date import DateTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from orionis.console.contracts.schedule_event_listener import IScheduleEventListener

@dataclass(kw_only=True)
class Event(BaseEntity):
    """
    Represent a scheduled event with configuration for execution and timing.

    Parameters
    ----------
    signature : str
        Unique identifier for the event.
    args : list of str or None, default: []
        Arguments to be passed to the event.
    purpose : str or None, default: None
        Description of the event's purpose.
    random_delay : int or None, default: None
        Random delay in seconds before triggering.
    start_date : datetime or None, default: None
        Date and time when the event becomes active.
    end_date : datetime or None, default: None
        Date and time when the event becomes inactive.
    trigger : CronTrigger or DateTrigger or IntervalTrigger or None, default: None
        Trigger mechanism for event execution.
    details : str or None, default: None
        Additional metadata about the event.
    listener : IScheduleEventListener or None, default: None
        Listener for event-specific logic.
    max_instances : int, default: 1
        Maximum concurrent instances allowed.
    misfire_grace_time : int or None, default: None
        Grace period in seconds for misfired events.
    coalesce : bool, default: True
        Whether to coalesce missed runs into a single run.

    Returns
    -------
    Event
        Instance of Event with specified configuration.
    """

    # Unique identifier for the event
    signature: str

    # List of arguments for the event, defaults to empty list if not provided
    args: list[str] | None = field(default_factory=list)

    # Description of the event's purpose
    purpose: str | None = None

    # Optional random delay (in seconds) before the event is triggered
    random_delay: int | None = None

    # Start date and time for the event
    start_date: datetime | None = None

    # End date and time for the event
    end_date: datetime | None = None

    # Trigger mechanism for the event (cron, date, or interval)
    trigger: CronTrigger | DateTrigger | IntervalTrigger | None = None

    # Optional details about the event
    details: str | None = None

    # Optional listener that implements IScheduleEventListener
    listener: IScheduleEventListener | None = None

    # Maximum number of concurrent instances allowed for the event
    max_instances: int = 1

    # Grace time in seconds for misfired events
    misfire_grace_time: int | None = None

    # Whether to coalesce missed runs into a single run
    coalesce: bool = True
