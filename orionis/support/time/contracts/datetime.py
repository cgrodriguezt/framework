from abc import ABC, abstractmethod
import pendulum

class IDateTime(ABC):

    @abstractmethod
    def now(self) -> pendulum.DateTime:
        """
        Get current date and time in configured timezone.

        Uses pendulum to obtain current datetime object based on
        instance's timezone.

        Returns
        -------
        pendulum.DateTime
            Current datetime in the specified timezone.
        """