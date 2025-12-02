from abc import ABC, abstractmethod

class IExecutor(ABC):

    @abstractmethod
    def running(self, program: str, time: str = "") -> None:
        """
        Log the execution of a program in the "RUNNING" state.

        Outputs a formatted console message to indicate a program is running.
        Uses ANSI color coding for the running state. Includes timestamp,
        program name, optional execution time, and colored state indicator.

        Parameters
        ----------
        program : str
            Name of the program or process currently being executed.
        time : str, optional
            Execution time duration (e.g., '30s', '2m 15s'). Defaults to ''.

        Returns
        -------
        None
            This method does not return any value.
        """

    @abstractmethod
    def done(self, program: str, time: str = "") -> None:
        """
        Log the execution of a program in the "DONE" state.

        Outputs a formatted console message to indicate a program has completed.
        Uses ANSI color coding for the done state. Includes timestamp, program
        name, optional execution time, and colored state indicator.

        Parameters
        ----------
        program : str
            Name of the program or process that has completed execution.
        time : str, optional
            Total execution time duration (e.g., '30s', '2m 15s'). Defaults to ''.

        Returns
        -------
        None
            This method does not return any value.
        """

    @abstractmethod
    def fail(self, program: str, time: str = "") -> None:
        """
        Log the execution of a program in the "FAIL" state.

        Outputs a formatted console message to indicate a program has failed.
        Uses ANSI color coding for the fail state. Includes timestamp, program
        name, optional execution time, and colored state indicator.

        Parameters
        ----------
        program : str
            Name of the program or process that has failed during execution.
        time : str, optional
            Execution time duration before failure (e.g., '30s', '2m 15s').
            Defaults to ''.

        Returns
        -------
        None
            This method does not return any value.
        """
