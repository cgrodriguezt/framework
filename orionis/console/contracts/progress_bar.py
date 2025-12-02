from abc import ABC, abstractmethod

class IProgressBar(ABC):

    @abstractmethod
    def start(self) -> None:
        """
        Initialize the progress bar to its initial state and display starting progress.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """

    @abstractmethod
    def advance(self, increment: int) -> None:
        """
        Advance the progress bar by the specified increment.

        Parameters
        ----------
        increment : int
            Amount to increase the progress.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """

    @abstractmethod
    def finish(self) -> None:
        """
        Complete the progress bar and display its final state.

        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """
