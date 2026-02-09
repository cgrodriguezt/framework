from __future__ import annotations
from abc import ABC, abstractmethod

class IWorkers(ABC):

    @abstractmethod
    def setRamPerWorker(self, ram_per_worker: float) -> None:
        """
        Update the RAM allocation per worker.

        Parameters
        ----------
        ram_per_worker : float
            New amount of RAM in GB to allocate for each worker.

        Returns
        -------
        None
            This method updates the internal RAM allocation setting and returns nothing.

        Notes
        -----
        Changing the RAM allocation per worker may affect the recommended number of
        workers calculated by the system. This method only updates the internal
        configuration and does not trigger any recalculation automatically.
        """

    @abstractmethod
    def calculate(self) -> int:
        """
        Calculate the recommended maximum number of worker processes.

        Parameters
        ----------
        None

        Returns
        -------
        int
            The maximum number of worker processes that can be safely run in
            parallel, determined by the lesser of available CPU cores and memory
            capacity.

        Notes
        -----
        The calculation considers both CPU core count and available RAM.
        Ensures resources are not overcommitted.
        """
