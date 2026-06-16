from __future__ import annotations
import os
import psutil
from orionis.services.system.contracts.workers import IWorkers

# Constants evaluated once at import time to cache system information.
_CPU_COUNT: int = os.cpu_count() or 1
_RAM_TOTAL_BYTES: int = psutil.virtual_memory().total

class Workers(IWorkers):

    # Using __slots__ to prevent instance attribute creation and reduce memory overhead
    __slots__ = ()

    # Class-level variable to store RAM allocation per worker, defaulting to 0.5 GB.
    _ram_per_worker: float = 0.5

    @classmethod
    def setRamPerWorker(cls, ram_per_worker: float) -> None:
        """
        Update the RAM allocation per worker.

        Parameters
        ----------
        ram_per_worker : float
            New amount of RAM in GB to allocate for each worker.

        Returns
        -------
        None
            This method updates the class-level RAM allocation and returns nothing.

        Notes
        -----
        Changing the RAM allocation per worker affects every subsequent call
        to calculate(). The update is reflected immediately.
        """
        cls._ram_per_worker = ram_per_worker

    @classmethod
    def calculate(cls) -> int:
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
            capacity. Always returns at least 1.

        Notes
        -----
        Uses module-level constants for CPU count and total RAM (evaluated
        once at import time) to avoid repeated OS calls on every invocation.

        Integer floor-division (//) on raw byte counts is used instead of
        math.floor() to eliminate the module attribute lookup, the float
        intermediate object, and the Python-level function call overhead.
        """
        # Convert RAM per worker from GB to bytes for the calculation.
        ram_per_worker_bytes: int = int(cls._ram_per_worker * (1 << 30))
        return min(_CPU_COUNT, _RAM_TOTAL_BYTES // ram_per_worker_bytes) or 1
