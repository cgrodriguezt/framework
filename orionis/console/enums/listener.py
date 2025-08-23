from enum import Enum

class ListeningEvent(Enum):
    """
    Enum representing global listener events.

    Attributes
    ----------
    SCHEDULER_STARTED : str
        Event triggered when the scheduler starts.
    SCHEDULER_SHUTDOWN : str
        Event triggered when the scheduler shuts down.
    SCHEDULER_PAUSED : str
        Event triggered when the scheduler is paused.
    SCHEDULER_RESUMED : str
        Event triggered when the scheduler resumes.
    SCHEDULER_ERROR : str
        Event triggered when the scheduler encounters an error.
    SCHEDULER_STARTED : str
        Event triggered when the scheduler starts.
    SCHEDULER_SHUTDOWN : str
        Event triggered when the scheduler shuts down.
    SCHEDULER_PAUSED : str
        Event triggered when the scheduler is paused.
    SCHEDULER_RESUMED : str
        Event triggered when the scheduler resumes.
    EXECUTOR_ADDED : str
        Event triggered when an executor is added.
    EXECUTOR_REMOVED : str
        Event triggered when an executor is removed.
    JOBSTORE_ADDED : str
        Event triggered when a job store is added.
    JOBSTORE_REMOVED : str
        Event triggered when a job store is removed.
    ALL_JOBS_REMOVED : str
        Event triggered when all jobs are removed.
    JOB_ADDED : str
        Event triggered when a job is added.
    JOB_REMOVED : str
        Event triggered when a job is removed.
    JOB_MODIFIED : str
        Event triggered when a job is modified.
    JOB_EXECUTED : str
        Event triggered when a job is executed.
    JOB_ERROR : str
        Event triggered when a job encounters an error.
    JOB_MISSED : str
        Event triggered when a job is missed.
    JOB_SUBMITTED : str
        Event triggered when a job is submitted.
    JOB_MAX_INSTANCES : str
        Event triggered when a job exceeds max instances.
    ALL : str
        Event triggered for all events.
    """

    SCHEDULER_STARTED = "X-ORIONIS-EVENT-SCHEDULER-STARTED"
    SCHEDULER_SHUTDOWN = "X-ORIONIS-EVENT-SCHEDULER-SHUTDOWN"
    SCHEDULER_PAUSED = "X-ORIONIS-EVENT-SCHEDULER-PAUSED"
    SCHEDULER_RESUMED = "X-ORIONIS-EVENT-SCHEDULER-RESUMED"
    SCHEDULER_ERROR = "X-ORIONIS-SCHEDULER-ERROR"
    EXECUTOR_ADDED = "X-ORIONIS-EVENT-EXECUTOR-ADDED"
    EXECUTOR_REMOVED = "X-ORIONIS-EVENT-EXECUTOR-REMOVED"
    JOBSTORE_ADDED = "X-ORIONIS-EVENT-JOBSTORE-ADDED"
    JOBSTORE_REMOVED = "X-ORIONIS-EVENT-JOBSTORE-REMOVED"
    ALL_JOBS_REMOVED = "X-ORIONIS-EVENT-ALL-JOBS-REMOVED"
    JOB_ADDED = "X-ORIONIS-EVENT-JOB-ADDED"
    JOB_REMOVED = "X-ORIONIS-EVENT-JOB-REMOVED"
    JOB_MODIFIED = "X-ORIONIS-EVENT-JOB-MODIFIED"
    JOB_EXECUTED = "X-ORIONIS-EVENT-JOB-EXECUTED"
    JOB_ERROR = "X-ORIONIS-EVENT-JOB-ERROR"
    JOB_MISSED = "X-ORIONIS-EVENT-JOB-MISSED"
    JOB_SUBMITTED = "X-ORIONIS-EVENT-JOB-SUBMITTED"
    JOB_MAX_INSTANCES = "X-ORIONIS-EVENT-JOB-MAX-INSTANCES"
    ALL = "X-ORIONIS-EVENT-ALL"