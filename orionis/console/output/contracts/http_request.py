from __future__ import annotations
from abc import ABC, abstractmethod

class IHTTPRequestPrinter(ABC):

    @abstractmethod
    def printRequest(
        self,
        method: str,
        path: str,
        duration: float,
        *,
        success: bool = True,
        code: int = 200,
    ) -> None:
        """
        Print a formatted HTTP request line.

        Parameters
        ----------
        method : str
            HTTP method (e.g., 'GET', 'POST').
        path : str
            Request path.
        duration : float
            Duration of the request in seconds.
        success : bool, optional
            Indicates if the request was successful (default is True).
        code : int, optional
            HTTP status code (default is 200).

        Returns
        -------
        None
            This method does not return a value.
        """
