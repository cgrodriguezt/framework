from __future__ import annotations
import traceback
from typing import Any
from orionis.support.formatter.exceptions.contracts.parser import IExceptionParser

class ExceptionParser(IExceptionParser):

    def __init__(self, exception: Exception) -> None:
        """
        Initialize ExceptionParser with an exception instance.

        Parameters
        ----------
        exception : Exception
            Exception to be parsed and formatted.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Store the exception instance for later parsing.
        self.__exception = exception

    @property
    def rawException(self) -> Exception:
        """
        Return the raw exception instance.

        Returns
        -------
        Exception
            The original exception instance stored in the parser.
        """
        return self.__exception

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
        try:
            # Extract traceback information for the exception
            tb = traceback.TracebackException.from_exception(
                self.__exception, capture_locals=False,
            )

            error_type: str = "Unknown"
            if tb and tb.exc_type:
                error_type = tb.exc_type.__name__
            elif type(self.__exception).__name__:
                error_type = type(self.__exception).__name__

            error_message: str = str(tb).strip() if tb else str(self.__exception)

            return {
                "error_type": error_type,
                "error_message": error_message,
                "error_code": getattr(self.__exception, "code", None),
                "stack_trace": self.__parseStack(tb.stack if tb else []),
                "cause": self.__parseCause(
                    getattr(self.__exception, "__cause__", None),
                ),
            }
        except (AttributeError, TypeError, ValueError) as e:

            # Fallback in case traceback extraction fails
            error_msg: str = f"Failed to parse exception: {e!s}"
            return {
                "error_type": type(self.__exception).__name__,
                "error_message": str(self.__exception),
                "error_code": getattr(self.__exception, "code", None),
                "stack_trace": [],
                "cause": None,
                "_parse_error": error_msg,
            }

    def __parseStack(
        self, stack: traceback.StackSummary | list,
    ) -> list[dict[str, str | int | None]]:
        """
        Parse a stack trace summary into a list of frame dictionaries.

        Parameters
        ----------
        stack : traceback.StackSummary | list
            Stack trace summary or an empty list.

        Returns
        -------
        list of dict[str, str | int | None]
            Each dictionary contains:
            - 'filename': str, file where the frame is located.
            - 'lineno': int, line number in the file.
            - 'name': str, function or method name.
            - 'line': str | None, source line of code.
        """
        if not stack:
            return []
        # Convert each frame to a dictionary with relevant details.
        try:
            return [
                {
                    "filename": getattr(frame, "filename", "<unknown>"),
                    "lineno": getattr(frame, "lineno", 0),
                    "name": getattr(frame, "name", "<unknown>"),
                    "line": getattr(frame, "line", None),
                }
                for frame in stack
            ]
        except (AttributeError, TypeError):
            return []

    def __parseCause(
        self, cause: BaseException | None,
    ) -> dict[str, Any] | None:
        """
        Recursively parse the cause of an exception.

        Parameters
        ----------
        cause : BaseException | None
            The original cause of the exception.

        Returns
        -------
        dict[str, Any] | None
            Dictionary with the cause's error type, message, and stack trace,
            or None if no cause exists.
        """
        # Return None if the cause is not a valid exception
        if not isinstance(cause, BaseException):
            return None

        try:
            # Extract traceback information for the cause
            cause_tb = traceback.TracebackException.from_exception(cause)

            error_type = "Unknown"
            if cause_tb and cause_tb.exc_type:
                error_type = cause_tb.exc_type.__name__
            elif type(cause).__name__:
                error_type = type(cause).__name__

            error_message = str(cause_tb).strip() if cause_tb else str(cause)

            result = {
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": self.__parseStack(cause_tb.stack if cause_tb else []),
            }

            # Recursively parse nested causes, avoiding circular references
            nested_cause = getattr(cause, "__cause__", None)
            if nested_cause and nested_cause is not cause:
                result["cause"] = self.__parseCause(nested_cause)

            return result

        except (AttributeError, TypeError, ValueError) as parse_error:

            # Fallback for known parsing errors
            return {
                "error_type": type(cause).__name__,
                "error_message": str(cause),
                "stack_trace": [],
                "_parse_error": f"Failed to parse cause: {parse_error!s}",
            }
