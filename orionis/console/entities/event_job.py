from __future__ import annotations
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING
from orionis.support.entities.base import BaseEntity

if TYPE_CHECKING:
    from datetime import datetime
    from collections.abc import Callable

@dataclass(kw_only=True)
class EventJob(BaseEntity):
    """
    Represent the configuration and state of a scheduled job.

    Parameters
    ----------
    id : str
        Unique identifier for the job.
    code : int, optional
        Numeric code representing the job status or type. Defaults to 0.
    name : str or None, optional
        Human-readable name for the job. Defaults to None.
    func : Callable or None, optional
        Function or coroutine to be executed by the job. Defaults to None.
    args : tuple, optional
        Positional arguments for the function. Defaults to empty tuple.
    trigger : Any or None, optional
        Trigger that determines the job's schedule. Defaults to None.
    executor : str, optional
        Executor alias for running the job. Defaults to 'default'.
    jobstore : str, optional
        Job store alias. Defaults to 'default'.
    misfire_grace_time : int or None, optional
        Grace period in seconds for missed executions. Defaults to None.
    max_instances : int, optional
        Maximum concurrent job instances. Defaults to 1.
    coalesce : bool, optional
        Whether to merge pending executions. Defaults to False.
    next_run_time : datetime or None, optional
        Next scheduled execution time. Defaults to None.
    exception : BaseException or None, optional
        Exception from the last execution. Defaults to None.
    traceback : str or None, optional
        Traceback string if an exception occurred. Defaults to None.
    retval : Any or None, optional
        Return value from the last execution. Defaults to None.
    purpose : str or None, optional
        Description of the job's purpose. Defaults to None.
    start_date : datetime or None, optional
        Earliest possible run time. Defaults to None.
    end_date : datetime or None, optional
        Latest possible run time. Defaults to None.
    details : str or None, optional
        Additional job metadata. Defaults to None.

    Returns
    -------
    None
        This class is a data container and does not return a value upon instantiation.
    """

    # Unique identifier for the job
    id: str

    # Numeric code for job status or type
    code: int = 0

    # Human-readable job name
    name: str | None = None

    # Function or coroutine to execute
    func: Callable | None = None

    # Positional arguments for the function
    args: tuple = ()

    # Trigger for job scheduling
    trigger: Any | None = None

    # Executor alias
    executor: str = "default"

    # Job store alias
    jobstore: str = "default"

    # Grace period for missed executions
    misfire_grace_time: int | None = None

    # Maximum concurrent instances
    max_instances: int = 1

    # Whether to merge pending executions
    coalesce: bool = False

    # Next scheduled execution time
    next_run_time: datetime | None = None

    # Exception from last execution
    exception: BaseException | None = None

    # Traceback string if exception occurred
    traceback: str | None = None

    # Return value from last execution
    retval: Any | None = None

    # Description of job's purpose
    purpose: str | None = None

    # Earliest possible run time
    start_date: datetime | None = None

    # Latest possible run time
    end_date: datetime | None = None

    # Additional job metadata
    details: str | None = None
