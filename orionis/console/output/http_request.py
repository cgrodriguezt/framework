from __future__ import annotations
from typing import ClassVar
from rich.console import Console
from rich.text import Text
from orionis.console.output.contracts.http_request import IHTTPRequestPrinter
from orionis.support.strings.stringable import Stringable

class HTTPRequestPrinter(IHTTPRequestPrinter):

    # Predefined colors for HTTP methods (based on common conventions)
    HTTP_COLORS: ClassVar[dict] = {
        "GET": {"background": "green", "text": "black"},
        "POST": {"background": "blue", "text": "white"},
        "PUT": {"background": "yellow", "text": "black"},
        "PATCH": {"background": "magenta", "text": "white"},
        "DELETE": {"background": "red", "text": "white"},
        "OPTIONS": {"background": "cyan", "text": "black"},
        "HEAD": {"background": "white", "text": "black"},
        "TRACE": {"background": "grey70", "text": "black"},
        "CONNECT": {"background": "bright_black", "text": "white"},
        "default": {"background": "grey37", "text": "white"},
    }

    # Status code color mapping based on HTTP response codes
    STATUS_COLORS: ClassVar[dict] = {
        "1xx": {"background": "cyan", "text": "black"},
        "2xx": {"background": "green", "text": "white"},
        "3xx": {"background": "yellow", "text": "black"},
        "4xx": {"background": "magenta", "text": "white"},
        "5xx": {"background": "red", "text": "white"},
        "default": {"background": "grey50", "text": "white"},
    }

    def __init__(self) -> None:
        """
        Initialize the HTTPRequestPrinter instance.

        Sets up the console, determines the optimal output width, and precomputes
        reusable styles and text elements for efficient HTTP request printing.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Set up the console for output
        self.__console = Console()

        # Determine the total width for output, clamped between 60 and 120
        self._total_width = max(60, min(120, int(self.__console.size.width * 0.8)))

        # Precompute a single space Text object for reuse
        self.__space_text = Text(" ")

        # Precompute status texts for success and failure
        self.__status_texts = {
            True: Text("  OK  ", style="green", no_wrap=True),
            False: Text(" FAIL ", style="red", no_wrap=True),
        }

        # Store default styles for HTTP methods and status codes
        self.__style_method_default = self.HTTP_COLORS["default"]
        self.__style_status_default = self.STATUS_COLORS["default"]

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
        # Ensure method is uppercase and trimmed
        method = Stringable(method).upper().trim()

        # Get style for HTTP method
        style_method = self.HTTP_COLORS.get(
            method.value(), self.__style_method_default,
        )
        method_text = Text(
            method.padBoth(9).value(),
            style=f"bold {style_method['text']} on {style_method['background']}",
            no_wrap=True,
        )

        # Format duration string
        duration_str = (
            f"~ {duration * 1000:.0f}ms" if duration < 1.0 else f"~ {duration:.2f}s"
        )
        duration_text = Text(
            duration_str.rjust(8),
            style="cyan",
            no_wrap=True,
        )

        # Truncate and format path for display
        path_dots_space = self._total_width - 18
        max_path = max(1, path_dots_space - 3)
        path_display = (
            path[: max_path - 3] + "..." if len(path) > max_path else path
        )
        path_text = Text(
            path_display,
            style="white",
            no_wrap=True,
        )

        # Add filler dots to align output
        dots_count = path_dots_space - len(path_display)
        filler_text = Text(
            "." * dots_count,
            style="grey50",
            no_wrap=True,
        )

        # Status text based on request success
        status_text = self.__status_texts[success]

        # Determine style based on status code category
        code_str = str(code)
        status_category = f"{code_str[0]}xx"
        style_status = self.STATUS_COLORS.get(
            status_category,
            self.__style_status_default,
        )
        code_text = Text(
            code_str.center(5),
            style=f"bold {style_status['text']} on {style_status['background']}",
            no_wrap=True,
        )

        # Print the formatted HTTP request line to the console
        self.__console.print(
            method_text,
            self.__space_text,
            path_text,
            filler_text,
            duration_text,
            status_text,
            code_text,
            sep="",
            end="\n",
        )
