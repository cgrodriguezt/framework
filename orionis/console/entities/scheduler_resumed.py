from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from orionis.console.entities.scheduler_event_data import SchedulerEventData

if TYPE_CHECKING:
    from datetime import datetime

@dataclass(kw_only=True)
class SchedulerResumed(SchedulerEventData):
    """
    Represent an event triggered when the scheduler resumes.

    This data class extends SchedulerEventData and holds information about the
    scheduler's resumption event.

    Parameters
    ----------
    time : str or datetime, optional
        The time when the scheduler was resumed. Can be a string or a datetime
        object.

    Returns
    -------
    SchedulerResumed
        An instance containing information about the resumed scheduler event.
    """

    # The time when the scheduler was resumed; can be a string or datetime object
    time: str | datetime | None = None
