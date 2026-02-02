from __future__ import annotations
import multiprocessing
import math
import psutil
from orionis.services.system.contracts.workers import IWorkers

class Workers(IWorkers):

    def __init__(self, ram_per_worker: float | None = 0.5) -> None:
        """
        Initialize the Workers system with resource constraints.

        Parameters
        ----------
        ram_per_worker : float | None, optional
            Amount of RAM (in GB) allocated per worker. Default is 0.5.

        Attributes
        ----------
        _cpu_count : int
            Number of CPU cores available on the system.
        _ram_total_gb : float
            Total system RAM in gigabytes.
        _ram_per_worker : float | None
            RAM allocated per worker in gigabytes.

        Returns
        -------
        None
            This constructor does not return a value.
        """
        # Get the number of CPU cores available
        self._cpu_count = multiprocessing.cpu_count()
        # Get the total system RAM in gigabytes
        self._ram_total_gb = psutil.virtual_memory().total / (1024 ** 3)
        # Set the RAM allocated per worker
        self._ram_per_worker = ram_per_worker

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
        # Update the RAM allocated per worker for future calculations
        self._ram_per_worker = ram_per_worker

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
        # Determine max workers by CPU core count
        max_workers_by_cpu: int = self._cpu_count

        # Determine max workers by available RAM
        max_workers_by_ram: int = math.floor(self._ram_total_gb / self._ram_per_worker)

        # Return the minimum to avoid overcommitting resources
        return min(max_workers_by_cpu, max_workers_by_ram)
