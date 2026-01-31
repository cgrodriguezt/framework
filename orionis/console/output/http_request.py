import shutil
from rich.console import Console
from rich.text import Text
from typing import ClassVar

class HTTPRequestPrinter:

    # Predefined colors for HTTP methods
    HTTP_COLORS: ClassVar[dict] = {
        "GET": {"background": "green", "text": "black"},
        "POST": {"background": "blue", "text": "white"},
        "PUT": {"background": "yellow", "text": "black"},
        "PATCH": {"background": "magenta", "text": "white"},
        "DELETE": {"background": "red", "text": "white"},
        "OPTIONS": {"background": "cyan", "text": "black"},
        "HEAD": {"background": "white", "text": "black"},
    }

    def __init__(self) -> None:
        """
        Initialize the HTTPRequestPrinter and precompute reusable values.

        This method sets up the console, determines the optimal width for output,
        and precomputes styles and text elements for efficient HTTP request
        printing.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Initialize the Rich console for output
        self.__console = Console()

        # Determine the console width, fallback to 80 if unavailable
        try:
            width = shutil.get_terminal_size().columns
        except OSError:
            width = 80

        # Clamp the width between 60 and 120, use 80% of terminal width
        self._total_width = max(60, min(120, int(width * 0.8)))

        # Precompute styles for each HTTP method
        self._method_styles = {}
        for method, cfg in self.HTTP_COLORS.items():
            self._method_styles[method.upper()] = (
                f"bold {cfg['text']} on {cfg['background']}"
            )
        self._default_method_style = "bold black on white"
        self._method_fmt = " {:^7} "
        self._circle_char = "●"

        # Precompute status text for success and failure
        self._status_texts = {
            True: Text(f" {self._circle_char} ", style="green", no_wrap=True),
            False: Text(f" {self._circle_char} ", style="red", no_wrap=True),
        }
        self._space_text = Text(" ")

    def printRequest(
        self,
        method: str,
        path: str,
        duration: float,
        *,
        success: bool = True,
    ) -> None:
        """
        Print a formatted HTTP request line with minimal logic.

        Parameters
        ----------
        method : str
            The HTTP method (e.g., 'GET', 'POST').
        path : str
            The request path.
        duration : float
            The duration of the request in seconds.
        success : bool, optional
            Indicates if the request was successful (default is True).

        Returns
        -------
        None
            This method does not return a value.
        """
        # Format the duration string based on its value
        duration_str = (
            f"{duration * 1000:.0f}ms" if duration < 1.0 else f"{duration:.2f}s"
        )

        # Select the style for the HTTP method
        m = method.upper()
        style_method = self._method_styles.get(m, self._default_method_style)
        method_fmt = self._method_fmt.format(m)
        method_text = Text(method_fmt, style=style_method)
        duration_text = Text(duration_str.rjust(8), style="green", no_wrap=True)

        # Calculate used width for formatting
        used = len(method_fmt) + 1 + 8
        path_dots_space = self._total_width - used
        max_path = max(1, path_dots_space - 3)

        # Truncate path if necessary
        path_display = path[:max_path - 3] + "..." if len(path) > max_path else path
        path_text = Text(path_display, style="white", no_wrap=True)
        dots_count = path_dots_space - len(path_display)
        filler_text = Text("." * dots_count, style="grey50", no_wrap=True)
        status_text = self._status_texts[success]

        # Print the formatted HTTP request line to the console
        self.__console.print(
            method_text,
            self._space_text,
            path_text,
            filler_text,
            duration_text,
            status_text,
            sep="",
            end="\n",
        )
