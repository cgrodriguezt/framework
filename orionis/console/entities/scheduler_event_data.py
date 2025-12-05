from dataclasses import dataclass
from orionis.support.entities.base import BaseEntity

@dataclass(kw_only=True)
class SchedulerEventData(BaseEntity):
    """
    Define a base data structure for scheduler events.

    This class provides a numeric event code to identify event types. Subclasses
    may extend this class to include additional context.

    Parameters
    ----------
    code : int
        Numeric code identifying the event type.

    Returns
    -------
    SchedulerEventData
        Instance with the specified event code.
    """

    # Numeric code representing the type of event in the scheduler.
    code: int
