from abc import ABC, abstractmethod
from pendulum.datetime import DateTime as PendulumDateTime

class IDateTime(ABC):

    @abstractmethod
    def now(self) -> PendulumDateTime:
        """
        Get current date and time in configured timezone.

        Uses pendulum to obtain current datetime object based on
        instance's timezone.

        Returns
        -------
        datetime
            Current datetime in the specified timezone.
        """