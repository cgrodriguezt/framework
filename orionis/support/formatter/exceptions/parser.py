from __future__ import annotations
from linecache import getline
import traceback
from typing import Any
from orionis.support.formatter.exceptions.contracts.parser import IExceptionParser

class ExceptionParser(IExceptionParser):

    def __init__(
        self,
        exception: Exception,
    ) -> None:
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
        """
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
        }

    def __getSourceCode(
        self, filename: str | None, lineno: int | None,
    ) -> tuple[list[int], list[str]]:
        """
        Extract source code lines around a specific line number from a file.

        Parameters
        ----------
        filename : str | None
            Path to the source file to read from.
        lineno : int | None
            Line number to center the code extraction around.

        Returns
        -------
        tuple[list[int], list[str]]
            Tuple containing line numbers and corresponding source code lines.
        """
        # Return empty lists if filename or line number is invalid
        if not filename or not lineno:
            return [], []

        # Define range of lines to extract (1 before, 3 after current line)
        start = max(1, lineno - 1)
        end = lineno + 3
        lines = []
        source = []

        # Extract each line within the defined range
        for i in range(start, end + 1):
            code_line = getline(filename, i).rstrip()
            lines.append(i)
            source.append(code_line)

        # Return the list of line numbers and corresponding source code lines
        return lines, source

    def __parseStack(
        self,
        stack: traceback.StackSummary | list,
    ) -> list[dict[str, str | int | None]]:
        """
        Parse stack trace summary into frame dictionaries.

        Parameters
        ----------
        stack : traceback.StackSummary | list
            Stack trace summary or an empty list.

        Returns
        -------
        list[dict[str, str | int | None]]
            List of dictionaries containing frame details with keys:
            'id', 'filename', 'lineno', 'name', 'line_code', 'lines', 'source'.
        """
        if not stack:
            return []

        # Convert each frame to a dictionary with relevant details
        try:
            traceback_frames = []
            for iteration, frame in enumerate(stack, start=1):
                filename = getattr(frame, "filename", "<unknown>")
                lineno = getattr(frame, "lineno", 0)
                name = getattr(frame, "name", "<unknown>")
                line_code = getattr(frame, "line", None)

                # Extract source code context around the frame line
                lines, source = self.__getSourceCode(filename, lineno)

                frame_info = {
                    "id": iteration,
                    "filename": filename.replace("\\", "/"),
                    "lineno": lineno,
                    "name": name,
                    "line_code": line_code,
                    "code": source,
                    "lines": lines,
                    "code_with_lines": [
                        f"{ln}:{cd}"
                        for ln, cd in zip(lines, source, strict=False)
                    ],
                }
                traceback_frames.append(frame_info)

            # Reverse to show most recent frame first
            traceback_frames.reverse()
            return traceback_frames

        except (AttributeError, TypeError):
            return []
