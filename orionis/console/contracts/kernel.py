from __future__ import annotations
from abc import ABC, abstractmethod

class IKernelCLI(ABC):

    @abstractmethod
    def handle(self, args: list[str] | None = None) -> int:
        """
        Process and dispatch command line arguments to the appropriate handler.

        Parameters
        ----------
        args : list of str, optional
            List of command line arguments.

        Returns
        -------
        int
            The exit code from the command execution.
        """
