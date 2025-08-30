from orionis.console.contracts.progress_bar import IProgressBar

class DummyProgressBar(IProgressBar):
    """
    Dummy implementation of IProgressBar for testing purposes.

    This class provides a mock progress bar that can be used in unit tests or
    development environments where the actual progress bar functionality is not
    required. It tracks the state of the progress bar, including whether it has
    started, the current progress value, and whether it has finished.

    Attributes
    ----------
    started : bool
        Indicates whether the progress bar has been started.
    progress : int
        The current progress value.
    finished : bool
        Indicates whether the progress bar has been finished.

    Returns
    -------
    None
        This class does not return any value upon instantiation.
    """

    def __init__(self):
        # Initialize the progress bar state
        self.started = False
        self.progress = 0
        self.finished = False

    def start(self) -> None:
        """
        Mark the progress bar as started and reset progress.

        This method sets the `started` attribute to True and resets the
        `progress` attribute to 0.

        Returns
        -------
        None
            This method does not return any value.
        """
        self.started = True
        self.progress = 0

    def advance(self, increment: int) -> None:
        """
        Advance the progress bar by a specified increment.

        Increases the `progress` attribute by the given increment value.

        Parameters
        ----------
        increment : int
            The amount by which to advance the progress.

        Returns
        -------
        None
            This method does not return any value.
        """
        self.progress += increment

    def finish(self) -> None:
        """
        Mark the progress bar as finished.

        Sets the `finished` attribute to True to indicate that the progress
        bar has completed.

        Returns
        -------
        None
            This method does not return any value.
        """
        self.finished = True