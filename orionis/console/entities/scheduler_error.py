from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from orionis.console.entities.scheduler_event_data import SchedulerEventData

if TYPE_CHECKING:
    from datetime import datetime

@dataclass(kw_only=True)
class SchedulerError(SchedulerEventData):
    """
    Represent an error event triggered by the scheduler.

    Extend SchedulerEventData to encapsulate error details from scheduler operations.
    Store the exception, traceback, and time of occurrence.

    Parameters
    ----------
    time : str or datetime, optional
        Time when the error occurred.
    exception : BaseException, optional
        Exception instance that caused the error.
    traceback : str, optional
        Traceback string with error details.

    Returns
    -------
    SchedulerError
        Instance containing scheduler error event details.
    """

    # Store the time when the error occurred (string or datetime)
    time: str | datetime | None = None

    # Store the exception that caused the scheduler error, if present
    exception: BaseException | None = None

    # Store the traceback information related to the scheduler error, if available
    traceback: str | None = None
