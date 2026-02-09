from __future__ import annotations
import sys
from orionis.console.dynamic.contracts.progress_bar import IProgressBar

class ProgressBar(IProgressBar):

    def __init__(self, total: int = 100, width: int = 50) -> None:
        """
        Initialize a new progress bar instance.

        Parameters
        ----------
        total : int, optional
            Maximum value representing 100% progress. Default is 100.
        width : int, optional
            Width of the progress bar in characters. Default is 50.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Set the total value for 100% progress
        self.total = total

        # Set the width of the progress bar
        self.bar_width = width

        # Initialize progress to zero
        self.progress = 0

    def __updateBar(self) -> None:
        """
        Update the visual representation of the progress bar in the console.

        Calculates the percentage of completion and redraws the progress bar
        in place, overwriting the previous output.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Calculate the percentage of completion
        percent = self.progress / self.total

        # Determine the number of filled characters in the bar
        filled_length = int(self.bar_width * percent)

        # Build the filled and remaining parts of the bar
        advanced = "█" * filled_length

        remaining = "░" * (self.bar_width - filled_length)

        # Construct the complete bar string
        bar = f"[{advanced}{remaining}] {int(percent * 100)}%"

        # Move the cursor to the start of the line and overwrite it
        sys.stdout.write("\r" + bar)
        sys.stdout.flush()

    def start(self) -> None:
        """
        Reset and display the progress bar at the starting state.

        Sets the progress to zero and renders the initial progress bar.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Reset progress to zero
        self.progress = 0

        # Render the initial progress bar
        self.__updateBar()

    def advance(self, increment: int = 1) -> None:
        """
        Advance the progress bar by a specified increment.

        Parameters
        ----------
        increment : int, optional
            Value by which to increase the progress. Default is 1.

        Notes
        -----
        Progress will not exceed the total value.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Increase progress by the specified increment
        self.progress += increment

        # Ensure progress does not exceed the total value
        self.progress = min(self.progress, self.total)

        # Update the progress bar display
        self.__updateBar()

    def finish(self) -> None:
        """
        Complete the progress bar and move to a new line.

        Sets progress to the maximum value, updates the bar, and moves the
        cursor to a new line for cleaner output.

        Returns
        -------
        None
            This method does not return a value.
        """
        # Set progress to the maximum value
        self.progress = self.total

        # Update the progress bar to show completion
        self.__updateBar()

        # Move the cursor to a new line for cleaner output
        sys.stdout.write("\n")
        sys.stdout.flush()
