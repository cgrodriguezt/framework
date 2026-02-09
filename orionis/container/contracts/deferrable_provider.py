from __future__ import annotations
from abc import ABC, abstractmethod

class IDeferrableProvider(ABC):

    @abstractmethod
    def provides(self) -> list[type]:
        """Return the services provided by this provider.

        Returns
        -------
        list[type]
            A list of service types that this provider offers.

        Raises
        ------
        NotImplementedError
            When subclasses do not implement this method.
        """