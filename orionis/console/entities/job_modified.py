from dataclasses import dataclass
from orionis.console.entities.job_event_data import JobEventData

@dataclass(kw_only=True)
class JobModified(JobEventData):
    """
    Represents an event triggered when a job is modified in a job store.

    This class is a data structure that extends `JobEventData` to provide
    additional context or functionality specific to job modification events.

    Attributes
    ----------
    (Inherited from JobEventData)

    Returns
    -------
    None
        This class does not return a value; it is used as a data container.
    """

    # This class inherits from JobEventData and does not add additional fields or methods.
    # It serves as a specific type of event for job modifications.
