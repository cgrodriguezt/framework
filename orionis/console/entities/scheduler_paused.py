from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from orionis.console.entities.scheduler_event_data import SchedulerEventData

if TYPE_CHECKING:
    from datetime import datetime

@dataclass(kw_only=True)
class SchedulerPaused(SchedulerEventData):
    """
    Represent an event when the scheduler is paused.

    This class extends SchedulerEventData and stores information about the
    scheduler pause event, including the time at which the pause occurred.

    Parameters
    ----------
    time : str or datetime or None, optional
        The time when the scheduler was paused. Can be a string, a datetime
        object, or None. Default is None.

    Returns
    -------
    SchedulerPaused
        Instance containing information about the pause event.
    """

    # The time when the scheduler was paused; can be a string, datetime, or None

    time: str | datetime | None = None
