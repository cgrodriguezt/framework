from orionis.console.contracts.debug import IDebug

class DummyDebug(IDebug):
    """
    Dummy implementation of the IDebug interface for testing debug functionality.

    This class provides mock implementations of the `dd` and `dump` methods,
    allowing tests to verify that these methods are called and to inspect the
    arguments passed to them. It sets internal flags and stores arguments for
    later inspection by test cases.

    Returns
    -------
    None
        This class does not return a value upon instantiation.
    """
    def __init__(self):
        # Flags to indicate if dd or dump was called
        self.dd_called = False
        self.dump_called = False
        # Store arguments passed to dd and dump
        self.dd_args = None
        self.dump_args = None

    def dd(self, *args):
        """
        Simulates the 'dd' (dump and die) debug method.

        Sets a flag indicating the method was called and stores the arguments.
        Terminates the program by raising SystemExit.

        Parameters
        ----------
        *args : tuple
            Arguments to be dumped.

        Returns
        -------
        None
            This method does not return a value; it raises SystemExit.
        """
        self.dd_called = True  # Mark that dd was called
        self.dd_args = args    # Store the arguments
        raise SystemExit(0)    # Terminate execution

    def dump(self, *args):
        """
        Simulates the 'dump' debug method.

        Sets a flag indicating the method was called and stores the arguments.
        Does not terminate the program.

        Parameters
        ----------
        *args : tuple
            Arguments to be dumped.

        Returns
        -------
        None
            This method does not return a value.
        """
        self.dump_called = True  # Mark that dump was called
        self.dump_args = args    # Store the arguments