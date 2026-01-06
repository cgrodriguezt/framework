from enum import Enum

class ExecutionMode(Enum):
    """
    Represent possible execution modes for running tests.

    Attributes
    ----------
    SEQUENTIAL : str
        Execute tests one after another in sequence.
    PARALLEL : str
        Execute tests concurrently in parallel.

    Returns
    -------
    ExecutionMode
        An enumeration member representing the execution mode.
    """

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
