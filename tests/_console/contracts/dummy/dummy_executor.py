from orionis.console.contracts.executor import IExecutor

class DummyExecutor(IExecutor):
    """
    Dummy implementation of the IExecutor interface for testing purposes.

    This class simulates the behavior of an executor by recording method calls and their arguments
    into an internal log. It is intended to be used in unit tests where actual execution is not required.

    Methods
    -------
    running(program: str, time: str = '') -> None
        Records the start of a program execution.

    done(program: str, time: str = '') -> None
        Records the successful completion of a program execution.

    fail(program: str, time: str = '') -> None
        Records the failure of a program execution.

    Returns
    -------
    None
        This class and its methods do not return any value. All information is stored in the `logs` attribute.
    """
    def __init__(self):
        # Initialize an empty list to store log entries
        self.logs = []

    def running(self, program: str, time: str = '') -> None:
        # Log the start of a program execution
        self.logs.append(("RUNNING", program, time))

    def done(self, program: str, time: str = '') -> None:
        # Log the successful completion of a program execution
        self.logs.append(("DONE", program, time))

    def fail(self, program: str, time: str = '') -> None:
        # Log the failure of a program execution
        self.logs.append(("FAIL", program, time))
