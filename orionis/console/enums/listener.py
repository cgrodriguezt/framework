from enum import Enum

class ListeningEvent(Enum):
    """
    Enumerate scheduler and job-related events.

    This enumeration defines events for monitoring and reacting to changes in
    the scheduler and job lifecycle.

    Attributes
    ----------
    SCHEDULER_STARTED : str
        Triggered when the scheduler starts.
    SCHEDULER_SHUTDOWN : str
        Triggered when the scheduler shuts down.
    SCHEDULER_PAUSED : str
        Triggered when the scheduler is paused.
    SCHEDULER_RESUMED : str
        Triggered when the scheduler is resumed.
    SCHEDULER_ERROR : str
        Triggered when the scheduler encounters an error.
    JOB_BEFORE : str
        Triggered before a job is executed.
    JOB_AFTER : str
        Triggered after a job is executed.
    JOB_ON_FAILURE : str
        Triggered when a job fails.
    JOB_ON_MISSED : str
        Triggered when a job is missed.
    JOB_ON_MAXINSTANCES : str
        Triggered when a job exceeds its allowed instances.
    JOB_ON_PAUSED : str
        Triggered when a job is paused.
    JOB_ON_RESUMED : str
        Triggered when a paused job is resumed.
    JOB_ON_REMOVED : str
        Triggered when a job is removed.

    Returns
    -------
    str
        The string value representing the event name.
    """

    # Indicates the scheduler has started.
    SCHEDULER_STARTED = "schedulerStarted"

    # Indicates the scheduler has shut down.
    SCHEDULER_SHUTDOWN = "schedulerShutdown"

    # Indicates the scheduler is paused.
    SCHEDULER_PAUSED = "schedulerPaused"

    # Indicates the scheduler has resumed.
    SCHEDULER_RESUMED = "schedulerResumed"

    # Indicates the scheduler encountered an error.
    SCHEDULER_ERROR = "schedulerError"

    # Job-related events

    # Indicates a job is about to execute.
    JOB_BEFORE = "before"

    # Indicates a job has finished execution.
    JOB_AFTER = "after"

    # Indicates a job failed during execution.
    JOB_ON_FAILURE = "onFailure"

    # Indicates a job was missed.
    JOB_ON_MISSED = "onMissed"

    # Indicates a job exceeded its maximum allowed instances.
    JOB_ON_MAXINSTANCES = "onMaxInstances"

    # Indicates a job is paused.
    JOB_ON_PAUSED = "onPaused"

    # Indicates a paused job has resumed.
    JOB_ON_RESUMED = "onResumed"

    # Indicates a job has been removed.
    JOB_ON_REMOVED = "onRemoved"
