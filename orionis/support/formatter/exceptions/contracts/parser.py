from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class IExceptionParser(ABC):

    @property
    @abstractmethod
    def rawException(self) -> Exception:
        """
        Return the raw exception instance.

        Returns
        -------
        Exception
            The original exception instance stored in the parser.
        """

    @abstractmethod
    def toDict(self) -> dict[str, Any]:
        """
        Serialize exception details into a dictionary.

        Parameters
        ----------
        self : ExceptionParser
            Instance of ExceptionParser.

        Returns
        -------
        dict[str, Any]
            Dictionary with keys:
            - 'error_type': str, type of the exception.
            - 'error_message': str, formatted traceback string.
            - 'error_code': Any, custom error code if present.
            - 'stack_trace': list[dict], frame details.
            - 'cause': dict or None, nested dictionary for the original cause.
            - '_parse_error': str, error message if parsing fails (optional).
        """
