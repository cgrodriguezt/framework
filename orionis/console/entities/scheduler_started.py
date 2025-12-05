from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from orionis.console.entities.scheduler_event_data import SchedulerEventData

if TYPE_CHECKING:
    from datetime import datetime

@dataclass(kw_only=True)
class SchedulerStarted(SchedulerEventData):
    """
    Represent scheduler start event data.

    Encapsulate information about the scheduler's start event, including the start
    time and the list of scheduled tasks.

    Parameters
    ----------
    time : str or datetime, optional
        The time when the scheduler started. Can be a string or a `datetime` object.
    tasks : list, optional
        The list of tasks scheduled at the scheduler start time.

    Returns
    -------
    SchedulerStarted
        Instance containing scheduler start event data.
    """

    # Store the time when the scheduler started; can be a string or datetime object
    time: str | datetime | None = None
