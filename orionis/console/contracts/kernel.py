from __future__ import annotations
from abc import ABC, abstractmethod

class IKernelCLI(ABC):

    @abstractmethod
    def handle(self, args: list[str] | None = None) -> None:
        """
        Process and dispatch command line arguments.

        Parameters
        ----------
        args : list of str or None, optional
            List of command line arguments to process.

        Returns
        -------
        None
            This method does not return a value. Raises NotImplementedError if
            not overridden.
        """
